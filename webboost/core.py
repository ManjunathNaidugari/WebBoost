"""
Core WebBoost Analyzer class.

This is the main entry point for analyzing websites.
The class orchestrates data collection, scoring, and recommendation generation.
"""

import asyncio
import time
import os
from typing import Dict, Any, Optional
from datetime import datetime
from urllib.parse import urlparse
from bs4 import BeautifulSoup
try:
    from playwright.async_api import async_playwright  
    _PLAYWRIGHT_AVAILABLE = True
except Exception:
    _PLAYWRIGHT_AVAILABLE = False
import aiohttp

import re
from textstat import textstat
from webboost.constants import SCORING_WEIGHTS
from webboost.data_collection import (
    get_performance_metrics,
    get_free_performance_data,
    get_mobile_friendly_check,
    get_seo_data_free,
    get_ssl_security_info,
    get_social_metrics_free
)
from webboost.analysis import (
    analyze_citations,
    analyze_design_quality,
    analyze_content_freshness,
    analyze_keywords,
    analyze_internal_linking
)
from webboost.scoring import (
    score_readability,
    score_informativeness,
    score_engagement,
    score_uniqueness,
    score_discoverability,
    score_ad_experience,
    score_social_integration,
    score_layout_quality,
    score_seo_keywords
)
from webboost.recommendations import generate_recommendations


class WebBoostAnalyzer:
    """
    Main analyzer class for evaluating websites.
    
    This class provides a clean interface for analyzing websites across
    multiple criteria including readability, SEO, performance, and UX.
    
    Example:
        >>> analyzer = WebBoostAnalyzer("https://example.com")
        >>> results = await analyzer.analyze()
        >>> print(results['overall_score'])
    """
    
    def __init__(self, website_url: str):
        """
        Initialize the analyzer with a website URL.
        
        Args:
            website_url: The URL of the website to analyze
        """
        self.url = website_url
        self.domain = urlparse(website_url).netloc
        self.soup: Optional[BeautifulSoup] = None
        self.text: str = ""
        self.html: str = ""
        self.stylesheets = []
        self.performance_metrics: Optional[Dict] = None
        self.load_time: Optional[float] = None
    
    def _validate_scores(self, scores: Dict[str, float]) -> Dict[str, float]:
        """Validate and normalize all scores to 0-100 range"""
        validated = {}
        
        for criterion, score in scores.items():
            if not isinstance(score, (int, float)):
                print(f"❌ Invalid score type for {criterion}: {type(score)}")
                validated[criterion] = 0.0
            elif score < 0 or score > 100:
                print(f"⚠️  Score {criterion}={score:.2f} out of range, clamping to [0, 100]")
                validated[criterion] = max(0.0, min(100.0, float(score)))
            else:
                validated[criterion] = float(score)
        
        return validated
    
    def _print_score_report(self, results: Dict) -> None:
        """Print detailed score breakdown for debugging"""
        print("\n" + "="*60)
        print("WEBBOOST SCORE REPORT")
        print("="*60)
        
        for criterion, score in results['scores'].items():
            weight = SCORING_WEIGHTS.get(criterion, 0)
            contribution = score * weight
            bar = "█" * int(score / 5)  # Visual bar
            print(f"{criterion:20s}: {score:5.1f}/100 {bar:20s} (weight: {weight:.2f}, contrib: {contribution:.2f})")
        
        print("-"*60)
        print(f"{'OVERALL SCORE':20s}: {results['overall_score']:5.1f}/100")
        print("="*60 + "\n")
    
    async def load_with_playwright(self):
        """Load website using Playwright for dynamic content"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            try:
                page = await browser.new_page()
                await page.set_viewport_size({"width": 1280, "height": 720})

                start_time = time.perf_counter()
                await page.goto(self.url, timeout=30000, wait_until='networkidle')
                end_time = time.perf_counter()
                self.load_time = end_time - start_time

                # Attempt performance metrics collection
                try:
                    self.performance_metrics = await get_performance_metrics(page)
                    if self.performance_metrics and self.performance_metrics.get('load_time'):
                        self.load_time = self.performance_metrics.get('load_time')
                except Exception:
                    self.performance_metrics = None

                # Small delay to allow late network tasks
                await asyncio.sleep(1)

                self.html = await page.content()
                try:
                    self.text = await page.inner_text('body')
                except Exception:
                    self.text = ''
                self.soup = BeautifulSoup(self.html, 'html.parser')

                await self._extract_stylesheets(page)

            except Exception as e:
                raise Exception(f"Failed to fetch website via Playwright: {str(e)}")
            finally:
                await browser.close()

    async def load_with_requests(self):
        """Fallback loader using aiohttp (no JavaScript execution)."""
        try:
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                start_time = time.perf_counter()
                async with session.get(self.url, allow_redirects=True) as resp:
                    self.html = await resp.text()
                end_time = time.perf_counter()
                self.load_time = end_time - start_time
        except Exception as e:
            raise Exception(f"Basic fetch failed: {str(e)}")

        self.soup = BeautifulSoup(self.html, 'html.parser')
        self.text = self.soup.get_text(separator=' ', strip=True)
        self.performance_metrics = None  # Limited with basic fetch
    
    async def _extract_stylesheets(self, page):
        """Extract CSS styles for design analysis"""
        try:
            self.stylesheets = await page.evaluate("""() => {
                const styles = [];
                document.querySelectorAll('link[rel="stylesheet"]').forEach(link => {
                    styles.push(link.href);
                });
                return styles;
            }""")
        except:
            self.stylesheets = []
    
    async def analyze(self) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of the website.
        
        Returns:
            Dictionary containing:
            - overall_score: Weighted average of all criteria (0-100)
            - scores: Individual scores for each criterion
            - free_data_sources: Raw data collected during analysis
            - recommendations: List of actionable recommendations
        """
        if not self.soup:
            # Decide whether to use Playwright or fallback
            disable_pw = os.getenv("DISABLE_PLAYWRIGHT", "0") == "1"
            if not disable_pw and _PLAYWRIGHT_AVAILABLE:
                try:
                    await self.load_with_playwright()
                except Exception:
                    # Fallback silently
                    await self.load_with_requests()
            else:
                await self.load_with_requests()

        # Gather all free data concurrently
        performance_data, mobile_data, seo_data, security_data, social_data = await asyncio.gather(
            get_free_performance_data(self.url, self.performance_metrics, self.load_time),
            get_mobile_friendly_check(self.soup),
            get_seo_data_free(self.domain),
            get_ssl_security_info(self.url),
            get_social_metrics_free(self.html, self.soup),
            return_exceptions=True
        )

        # Convert exceptions to empty dicts
        performance_data = performance_data if isinstance(performance_data, dict) else {}
        mobile_data = mobile_data if isinstance(mobile_data, dict) else {}
        seo_data = seo_data if isinstance(seo_data, dict) else {}
        security_data = security_data if isinstance(security_data, dict) else {}
        social_data = social_data if isinstance(social_data, dict) else {}

        # Get additional metrics
        design_metrics = analyze_design_quality(self.soup, self.html)
        content_freshness = analyze_content_freshness(self.text)
        keyword_analysis = analyze_keywords(self.text)
        internal_linking = analyze_internal_linking(self.soup, self.domain)
        citation_analysis = analyze_citations(self.text, self.soup)
        # Additional lightweight detail exports for frontend breakdowns
        content_stats = {
            'word_count': len(self.text.split()) if self.text else 0,
            'header_count': len(self.soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])) if self.soup else 0,
            'image_count': len(self.soup.find_all('img')) if self.soup else 0,
            'link_count': len(self.soup.find_all('a')) if self.soup else 0
        }

        # Readability detailed metrics (best-effort with error handling)
        # Populate per-formula values so the template can display the actual
        # metrics used during scoring (do this whenever text exists).
        readability_details = {
            'flesch_reading_ease': 0.0,
            'flesch_kincaid_grade': 0.0,
            'gunning_fog': 0.0,
            'smog_index': 0.0,
            'automated_readability': 0.0,
            'coleman_liau': 0.0
        }

        if self.text:
            try:
                readability_details['flesch_reading_ease'] = float(textstat.flesch_reading_ease(self.text))
            except Exception:
                readability_details['flesch_reading_ease'] = 0.0

            try:
                readability_details['flesch_kincaid_grade'] = float(textstat.flesch_kincaid_grade(self.text))
            except Exception:
                readability_details['flesch_kincaid_grade'] = 0.0

            try:
                readability_details['gunning_fog'] = float(textstat.gunning_fog(self.text))
            except Exception:
                readability_details['gunning_fog'] = 0.0

            try:
                readability_details['smog_index'] = float(textstat.smog_index(self.text))
            except Exception:
                readability_details['smog_index'] = 0.0

            try:
                readability_details['automated_readability'] = float(textstat.automated_readability_index(self.text))
            except Exception:
                readability_details['automated_readability'] = 0.0

            try:
                readability_details['coleman_liau'] = float(textstat.coleman_liau_index(self.text))
            except Exception:
                readability_details['coleman_liau'] = 0.0



        # Engagement details
        positive_words = len(re.findall(r'\b(great|excellent|amazing|love|perfect|wonderful|good|nice|awesome)\b', self.text.lower())) if self.text else 0
        negative_words = len(re.findall(r'\b(bad|terrible|awful|hate|worst|horrible|poor|disappointing)\b', self.text.lower())) if self.text else 0
        engagement_details = {
            'positive_words': positive_words,
            'negative_words': negative_words,
            'questions': self.text.count('?') if self.text else 0,
            'exclamations': self.text.count('!') if self.text else 0,
            'cta_words': len(re.findall(r"\b(click|learn|discover|join|subscribe|download|sign up|get started)\b", self.text.lower())) if self.text else 0
        }

        # Uniqueness details
        try:
            words = re.findall(r"\b[a-zA-Z]{4,}\b", self.text.lower()) if self.text else []
            unique_ratio = (len(set(words)) / len(words)) if words else 0
        except Exception:
            unique_ratio = 0
        uniqueness_details = {
            'unique_ratio': unique_ratio,
            'research_words': len(re.findall(r'\b(research|study|survey|data|analysis|experiment|finding)\b', self.text.lower())) if self.text else 0,
            'first_person_count': len(re.findall(r"\b(I|we|our|us|my|mine|ours)\b", self.text)) if self.text else 0
        }

        # Ad experience details
        ad_indicators = [
            'googleads', 'doubleclick', 'adsbygoogle', 'advertisement',
            'banner-ad', 'popup', 'modal', 'overlay', 'ad-container',
            'ad-unit', 'ad-slot', 'ad-wrapper'
        ]
        ad_count = 0
        for indicator in ad_indicators:
            ad_count += self.html.lower().count(indicator) if self.html else 0
        ad_details = {'ad_count': ad_count}

        # Calculate all scores - SINGLE SOURCE OF TRUTH
        # Each scoring function now returns (score, breakdown)
        scores = {}
        breakdowns = {}
        
        score, breakdown = score_readability(self.text)
        scores['readability'] = score
        breakdowns['readability'] = breakdown
        
        score, breakdown = score_informativeness(self.text, self.soup, citation_analysis)
        scores['informativeness'] = score
        breakdowns['informativeness'] = breakdown
        
        score, breakdown = score_engagement(self.text, self.soup)
        scores['engagement'] = score
        breakdowns['engagement'] = breakdown
        
        score, breakdown = score_uniqueness(self.text)
        scores['uniqueness'] = score
        breakdowns['uniqueness'] = breakdown
        
        score, breakdown = score_discoverability(self.soup)
        scores['discoverability'] = score
        breakdowns['discoverability'] = breakdown
        
        score, breakdown = score_ad_experience(self.html, self.soup)
        scores['ad_experience'] = score
        breakdowns['ad_experience'] = breakdown
        
        score, breakdown = score_social_integration(social_data)
        scores['social_integration'] = score
        breakdowns['social_integration'] = breakdown
        
        score, breakdown = score_layout_quality(self.soup, mobile_data, security_data, design_metrics)
        scores['layout_quality'] = score
        breakdowns['layout_quality'] = breakdown
        
        score, breakdown = score_seo_keywords(self.soup, seo_data, keyword_analysis, internal_linking, content_freshness, self.url)
        scores['seo_keywords'] = score
        breakdowns['seo_keywords'] = breakdown

        # VALIDATE: Ensure all scores are 0-100
        scores = self._validate_scores(scores)

        results = {
            'url': self.url,
            'analyzed_at': datetime.now().isoformat(),
            'scores': scores,
            'score_breakdowns': breakdowns,  # NEW: Detailed sub-criteria breakdowns
            'free_data_sources': {
                'performance': performance_data,
                'mobile': mobile_data,
                'seo': seo_data,
                'security': security_data,
                'social': social_data,
                'design': design_metrics,
                'content_freshness': content_freshness,
                'keyword_analysis': keyword_analysis,
                'internal_linking': internal_linking,
                'citation_analysis': citation_analysis,
                'content_stats': content_stats,
                'readability_details': readability_details,
                'engagement_details': engagement_details,
                'uniqueness_details': uniqueness_details,
                'ad_details': ad_details
            },
            'recommendations': []
        }
        
        # Calculate overall score with transparency
        overall = 0
        score_breakdown = {}
        
        for key, weight in SCORING_WEIGHTS.items():
            if key in scores:
                contribution = scores[key] * weight
                overall += contribution
                score_breakdown[key] = {
                    'raw_score': scores[key],
                    'weight': weight,
                    'contribution': contribution
                }
            else:
                print(f"⚠️  Warning: Missing score for criterion '{key}'")
        
        results['overall_score'] = round(overall, 2)
        results['score_breakdown'] = score_breakdown
        results['recommendations'] = generate_recommendations(results['scores'], results['free_data_sources'])
        
        # Print debug report if enabled
        if os.getenv('WEBBOOST_DEBUG', '0') == '1':
            self._print_score_report(results)
        
        return results

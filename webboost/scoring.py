"""
Scoring module for WebBoost Analyzer.

This module contains all scoring functions that calculate
scores for each criterion (0-100 scale).
"""

import re
import warnings
from textstat import textstat
import nltk
from typing import Dict, Optional
from bs4 import BeautifulSoup
from webboost.analysis import (
    analyze_skimming_optimization,
    analyze_ad_placement,
    detect_autoplay_media,
    find_featured_content,
    analyze_category_organization,
    analyze_url_structure
)


def normalize_readability_scores(scores: Dict) -> float:
    """Normalize various readability scores to 0-100 scale"""
    total_score = 0
    weight_count = 0
    
    if 'flesch_reading_ease' in scores and scores['flesch_reading_ease'] > 0:
        fre = max(0, min(100, scores['flesch_reading_ease']))
        total_score += fre
        weight_count += 1
        
    if 'flesch_kincaid_grade' in scores and scores['flesch_kincaid_grade'] > 0:
        fk_grade = scores['flesch_kincaid_grade']
        fk_score = max(0, 100 - (fk_grade * 5))
        total_score += fk_score
        weight_count += 1
        
    if 'gunning_fog' in scores and scores['gunning_fog'] > 0:
        fog = scores['gunning_fog']
        fog_score = max(0, 100 - (fog * 5))
        total_score += fog_score
        weight_count += 1
        
    if 'smog_index' in scores and scores['smog_index'] > 0:
        smog = scores['smog_index']
        smog_score = max(0, 100 - (smog * 5))
        total_score += smog_score
        weight_count += 1
        
    # Add the missing scores that were being calculated but not used
    if 'automated_readability' in scores and scores['automated_readability'] > 0:
        ari = scores['automated_readability']
        ari_score = max(0, 100 - (ari * 5))
        total_score += ari_score
        weight_count += 1
        
    if 'coleman_liau' in scores and scores['coleman_liau'] > 0:
        cl = scores['coleman_liau']
        cl_score = max(0, 100 - (cl * 5))
        total_score += cl_score
        weight_count += 1
        
    return total_score / weight_count if weight_count > 0 else 50.0


def score_readability(text: str) -> float:
    """Enhanced readability scoring with all major formulas"""
    if not text or len(text.strip()) < 100:  # Minimum text length
        return 50.0  # Return neutral score instead of 0
        
    try:
        warnings.filterwarnings('ignore')
        
        try:
            nltk.data.find('corpora/cmudict')
        except LookupError:
            try:
                nltk.download('cmudict', quiet=True)
            except:
                pass
        
        scores = {}
        # Add individual error handling for each readability metric
        try:
            scores['flesch_reading_ease'] = textstat.flesch_reading_ease(text)
        except Exception:
            scores['flesch_reading_ease'] = 0
            
        try:
            scores['flesch_kincaid_grade'] = textstat.flesch_kincaid_grade(text)
        except Exception:
            scores['flesch_kincaid_grade'] = 0
            
        try:
            scores['gunning_fog'] = textstat.gunning_fog(text)
        except Exception:
            scores['gunning_fog'] = 0
            
        try:
            scores['smog_index'] = textstat.smog_index(text)
        except Exception:
            scores['smog_index'] = 0
            
        try:
            scores['automated_readability'] = textstat.automated_readability_index(text)
        except Exception:
            scores['automated_readability'] = 0
            
        try:
            scores['coleman_liau'] = textstat.coleman_liau_index(text)
        except Exception:
            scores['coleman_liau'] = 0
        
        readability_score = normalize_readability_scores(scores)
        return min(100.0, max(0, readability_score))  # Ensure within bounds
        
    except Exception:
        # Fallback calculation
        try:
            sentences = re.split(r'[.!?]+', text)
            words = text.split()
            
            if len(sentences) > 0 and len(words) > 0:
                avg_sentence_length = len(words) / len(sentences)
                if avg_sentence_length <= 15:
                    return 80.0
                elif avg_sentence_length <= 25:
                    return 60.0
                else:
                    return 40.0
        except Exception:
            pass
            
        return 50.0  # Default neutral score


def score_informativeness(text: str, soup: Optional[BeautifulSoup], citation_analysis: Dict) -> float:
    """Enhanced content quality scoring with citations"""
    if not text or not soup:
        return 0.0
        
    word_count = len(text.split())
    header_count = len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']))
    image_count = len(soup.find_all('img'))
    link_count = len(soup.find_all('a'))
    
    depth_score = min(30, (word_count / 100))
    structure_score = min(25, header_count * 2)
    media_score = min(20, (image_count + link_count) * 1.5)
    citation_score = min(25, citation_analysis.get('citation_score', 0))
    
    return min(100.0, depth_score + structure_score + media_score + citation_score)


def score_engagement(text: str, soup: Optional[BeautifulSoup]) -> float:
    """Enhanced engagement scoring with skimming analysis"""
    if not text:
        return 0.0
        
    positive_words = len(re.findall(r'\b(great|excellent|amazing|love|perfect|wonderful|good|nice|awesome)\b', text.lower()))
    negative_words = len(re.findall(r'\b(bad|terrible|awful|hate|worst|horrible|poor|disappointing)\b', text.lower()))
    
    questions = text.count('?')
    exclamations = text.count('!')
    cta_words = len(re.findall(r'\b(click|learn|discover|join|subscribe|download|sign up|get started)\b', text.lower()))
    
    skimming_score = analyze_skimming_optimization(soup)
    
    sentiment_score = 50 + ((positive_words - negative_words) * 3)
    sentiment_score = max(0, min(100, sentiment_score))
    
    interaction_score = min(30, (questions * 2) + (exclamations * 1.5) + (cta_words * 2))
    
    return min(100.0, sentiment_score + interaction_score + skimming_score)


def score_uniqueness(text: str) -> float:
    """Enhanced uniqueness scoring with plagiarism indicators"""
    if not text:
        return 0.0
        
    research_words = len(re.findall(r'\b(research|study|survey|data|analysis|experiment|finding)\b', text.lower()))
    first_person = len(re.findall(r'\b(I|we|our|us|my|mine|ours)\b', text.lower()))
    
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    unique_ratio = len(set(words)) / len(words) if words else 0
    
    primary_research = len(re.findall(r'\b(interview|surveyed|studied|analyzed|experimented|observed)\b', text.lower()))
    
    base_score = 40.0
    base_score += min(20, research_words * 3)
    base_score += min(15, first_person * 0.8)
    base_score += min(15, unique_ratio * 30)
    base_score += min(10, primary_research * 2)
    
    return min(100.0, base_score)


def score_discoverability(soup: Optional[BeautifulSoup]) -> float:
    """Enhanced discoverability scoring with user path simulation"""
    if not soup:
        return 0.0
        
    has_search = bool(soup.find('input', {'type': 'search'}))
    nav_count = len(soup.find_all('nav'))
    breadcrumbs = bool(soup.find(class_=re.compile('breadcrumb', re.IGNORECASE)))
    sitemap = bool(soup.find('a', href=re.compile('sitemap', re.IGNORECASE)))
    
    featured_posts = find_featured_content(soup)
    category_organization = analyze_category_organization(soup)
    
    score = 0
    score += 15 if has_search else 5
    score += min(20, nav_count * 5)
    score += 15 if breadcrumbs else 0
    score += 10 if sitemap else 0
    score += min(15, featured_posts * 3)
    score += min(25, category_organization)
    
    return min(100.0, score)


def score_ad_experience(html: str, soup: Optional[BeautifulSoup]) -> float:
    """Enhanced ad experience analysis"""
    if not html:
        return 0.0
        
    ad_indicators = [
        'googleads', 'doubleclick', 'adsbygoogle', 'advertisement',
        'banner-ad', 'popup', 'modal', 'overlay', 'ad-container',
        'ad-unit', 'ad-slot', 'ad-wrapper'
    ]
    
    ad_score = 0
    for indicator in ad_indicators:
        ad_score += html.lower().count(indicator)
        
    placement_score = analyze_ad_placement(soup)
    autoplay_score = detect_autoplay_media(soup)
    
    quality_score = max(0, 100 - (ad_score * 5) - placement_score - autoplay_score)
    return min(100.0, quality_score)


def score_social_integration(social_data: Dict) -> float:
    """Enhanced social integration scoring"""
    if not social_data:
        return 0.0
        
    platform_count = sum(1 for platform in [
        'facebook', 'twitter', 'instagram', 'linkedin', 'youtube', 'pinterest', 'tiktok'
    ] if social_data.get(platform, False))
    
    sharing_buttons = social_data.get('sharing_buttons', 0)
    social_proof = social_data.get('social_proof', {})
    
    share_counts = social_proof.get('share_counts', 0)
    follower_counts = social_proof.get('follower_counts', 0)
    testimonials = social_proof.get('testimonials', 0)
    
    score = (platform_count * 10) + (sharing_buttons * 3)
    score += min(share_counts * 2, 10)
    score += min(follower_counts * 2, 10)
    score += min(testimonials * 3, 15)
    
    return min(100.0, score)


def score_layout_quality(soup: Optional[BeautifulSoup], mobile_data: Dict, security_data: Dict, design_metrics: Dict) -> float:
    """Enhanced layout quality scoring with design analysis"""
    score = 40.0
    
    if mobile_data.get('has_viewport'):
        score += 10
    if mobile_data.get('handheld_friendly'):
        score += 5
    if mobile_data.get('touch_optimized'):
        score += 5
        
    if security_data.get('https'):
        score += 10
        
    if soup:
        h1_count = len(soup.find_all('h1'))
        if h1_count == 1:
            score += 5
            
    score += design_metrics.get('whitespace_score', 0)
    score += design_metrics.get('typography_score', 0)
    score += design_metrics.get('color_contrast_score', 0)
    
    return min(100.0, score)


def score_seo_keywords(soup: Optional[BeautifulSoup], seo_data: Dict, keyword_analysis: Dict, 
                      internal_linking: Dict, content_freshness: Dict, url: str) -> float:
    """Enhanced SEO scoring with comprehensive analysis"""
    if not soup:
        return 0.0
        
    score = 0
    
    title = soup.find('title')
    if title and title.string:
        title_len = len(title.string)
        if 30 <= title_len <= 60:
            score += 10
            
    meta_desc = soup.find('meta', {'name': 'description'})
    if meta_desc and meta_desc.get('content'):
        desc_len = len(meta_desc['content'])
        if 120 <= desc_len <= 160:
            score += 10
            
    h1_count = len(soup.find_all('h1'))
    if h1_count == 1:
        score += 5
        
    if seo_data.get('indexed'):
        score += 10
        
    score += keyword_analysis.get('keyword_score', 0)
    score += internal_linking.get('linking_score', 0)
    score += content_freshness.get('freshness_score', 0)
    
    schema_markup = len(soup.find_all('script', type='application/ld+json'))
    score += min(schema_markup * 3, 10)
    
    url_score = analyze_url_structure(url)
    score += url_score
    
    return min(100.0, score + 15)


"""
Scoring module for WebBoost Analyzer.

This module contains all scoring functions that calculate
scores for each criterion (0-100 scale).

Each scoring function now returns a tuple of (score, breakdown) where
breakdown is a dictionary showing how the score was calculated.
"""

import re
import warnings
from textstat import textstat
import nltk
from typing import Dict, Optional, Tuple
from bs4 import BeautifulSoup
from webboost.analysis import (
    analyze_skimming_optimization,
    analyze_ad_placement,
    detect_autoplay_media,
    find_featured_content,
    analyze_category_organization,
    analyze_url_structure
)


def normalize_grade(value, ideal_low, ideal_high, max_hard=20):
    if value <= ideal_low:
        return 100.0
    if value <= ideal_high:
        return 90.0
    if value >= max_hard:
        return 0.0
    
    # linear decline from ideal band to max_hard
    return 90.0 * (1 - (value - ideal_high) / (max_hard - ideal_high))


def normalize_readability_scores(scores: Dict) -> float:
    """Correct normalization: maps each readability metric to 0–100 based on real ideal ranges."""
    total = 0.0
    count = 0
    
    # 1. Flesch Reading Ease (already 0–100)
    if scores.get('flesch_reading_ease', 0) > 0:
        fre = max(0, min(100, scores['flesch_reading_ease']))
        total += fre
        count += 1
    
    # 2. Flesch-Kincaid Grade (ideal 6–8)
    if scores.get('flesch_kincaid_grade', 0) > 0:
        g = scores['flesch_kincaid_grade']
        total += normalize_grade(g, ideal_low=6, ideal_high=8)
        count += 1
    
    # 3. Gunning Fog (ideal < 12)
    if scores.get('gunning_fog', 0) > 0:
        g = scores['gunning_fog']
        total += normalize_grade(g, ideal_low=0, ideal_high=12)
        count += 1
    
    # 4. SMOG (ideal 8–10)
    if scores.get('smog_index', 0) > 0:
        g = scores['smog_index']
        total += normalize_grade(g, ideal_low=8, ideal_high=10)
        count += 1
    
    # 5. Automated Readability Index (ideal 6–8)
    if scores.get('automated_readability', 0) > 0:
        g = scores['automated_readability']
        total += normalize_grade(g, ideal_low=6, ideal_high=8)
        count += 1
    
    # 6. Coleman Liau (ideal 6–8)
    if scores.get('coleman_liau', 0) > 0:
        g = scores['coleman_liau']
        total += normalize_grade(g, ideal_low=6, ideal_high=8)
        count += 1
    
    return total / count if count else 50.0


def score_readability(text: str) -> Tuple[float, Dict]:
    """
    Enhanced readability scoring with all major formulas.
    
    Returns:
        Tuple of (score, breakdown) where breakdown shows individual metrics
    """
    breakdown = {
        'flesch_reading_ease': 0.0,
        'flesch_kincaid_grade': 0.0,
        'gunning_fog': 0.0,
        'smog_index': 0.0,
        'automated_readability': 0.0,
        'coleman_liau': 0.0,
        'metrics_used': 0,
        'final_score': 50.0
    }
    
    if not text or len(text.strip()) < 100:  # Minimum text length
        breakdown['note'] = 'Text too short (< 100 chars)'
        return 50.0, breakdown
        
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
            breakdown['flesch_reading_ease'] = scores['flesch_reading_ease']
        except Exception:
            scores['flesch_reading_ease'] = 0
            
        try:
            scores['flesch_kincaid_grade'] = textstat.flesch_kincaid_grade(text)
            breakdown['flesch_kincaid_grade'] = scores['flesch_kincaid_grade']
        except Exception:
            scores['flesch_kincaid_grade'] = 0
            
        try:
            scores['gunning_fog'] = textstat.gunning_fog(text)
            breakdown['gunning_fog'] = scores['gunning_fog']
        except Exception:
            scores['gunning_fog'] = 0
            
        try:
            scores['smog_index'] = textstat.smog_index(text)
            breakdown['smog_index'] = scores['smog_index']
        except Exception:
            scores['smog_index'] = 0
            
        try:
            scores['automated_readability'] = textstat.automated_readability_index(text)
            breakdown['automated_readability'] = scores['automated_readability']
        except Exception:
            scores['automated_readability'] = 0
            
        try:
            scores['coleman_liau'] = textstat.coleman_liau_index(text)
            breakdown['coleman_liau'] = scores['coleman_liau']
        except Exception:
            scores['coleman_liau'] = 0
        
        readability_score = normalize_readability_scores(scores)
        breakdown['metrics_used'] = sum(1 for v in scores.values() if v > 0)
        breakdown['final_score'] = min(100.0, max(0, readability_score))
        
        final = min(100.0, max(0, readability_score))
        return final, breakdown
        
    except Exception:
        # Fallback calculation
        try:
            sentences = re.split(r'[.!?]+', text)
            words = text.split()
            
            if len(sentences) > 0 and len(words) > 0:
                avg_sentence_length = len(words) / len(sentences)
                breakdown['avg_sentence_length'] = avg_sentence_length
                
                if avg_sentence_length <= 15:
                    final = 80.0
                elif avg_sentence_length <= 25:
                    final = 60.0
                else:
                    final = 40.0
                    
                breakdown['final_score'] = final
                breakdown['note'] = 'Fallback calculation based on sentence length'
                return final, breakdown
        except Exception:
            pass
            
        breakdown['final_score'] = 50.0
        breakdown['note'] = 'Error during calculation'
        return 50.0, breakdown


def score_informativeness(text: str, soup: Optional[BeautifulSoup], citation_analysis: Dict) -> Tuple[float, Dict]:
    """Enhanced content quality scoring with citations"""
    breakdown = {
        'word_count': 0,
        'header_count': 0,
        'image_count': 0,
        'link_count': 0,
        'depth_score': 0,
        'structure_score': 0,
        'media_score': 0,
        'citation_score': 0,
        'final_score': 0
    }
    
    if not text or not soup:
        return 0.0, breakdown
        
    word_count = len(text.split())
    header_count = len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']))
    image_count = len(soup.find_all('img'))
    link_count = len(soup.find_all('a'))
    
    depth_score = min(30, (word_count / 100))
    structure_score = min(25, header_count * 2)
    media_score = min(20, (image_count + link_count) * 1.5)
    citation_score = min(25, citation_analysis.get('citation_score', 0))
    
    breakdown['word_count'] = word_count
    breakdown['header_count'] = header_count
    breakdown['image_count'] = image_count
    breakdown['link_count'] = link_count
    breakdown['depth_score'] = int(round(depth_score, 2))
    breakdown['structure_score'] = round(structure_score, 2)
    breakdown['media_score'] = int(round(media_score, 2))
    breakdown['citation_score'] = round(citation_score, 2)
    
    total_score = depth_score + structure_score + media_score + citation_score
    final = max(0.0, min(100.0, total_score))
    breakdown['final_score'] = int(round(final, 2))
    
    return final, breakdown


def score_engagement(text: str, soup: Optional[BeautifulSoup]) -> Tuple[float, Dict]:
    """Enhanced engagement scoring with skimming analysis"""
    breakdown = {
        'positive_words': 0,
        'negative_words': 0,
        'questions': 0,
        'exclamations': 0,
        'cta_words': 0,
        'sentiment_score': 0,
        'interaction_score': 0,
        'skimming_score': 0,
        'final_score': 0
    }
    
    if not text:
        return 0.0, breakdown
        
    positive_words = len(re.findall(r'\b(great|excellent|amazing|love|perfect|wonderful|good|nice|awesome)\b', text.lower()))
    negative_words = len(re.findall(r'\b(bad|terrible|awful|hate|worst|horrible|poor|disappointing)\b', text.lower()))
    
    questions = text.count('?')
    exclamations = text.count('!')
    cta_words = len(re.findall(r'\b(click|learn|discover|join|subscribe|download|sign up|get started)\b', text.lower()))
    
    skimming_score = analyze_skimming_optimization(soup)
    
    sentiment_score = 50 + ((positive_words - negative_words) * 3)
    sentiment_score = max(0, min(100, sentiment_score))
    
    interaction_score = min(30, (questions * 2) + (exclamations * 1.5) + (cta_words * 2))
    
    breakdown['positive_words'] = positive_words
    breakdown['negative_words'] = negative_words
    breakdown['questions'] = questions
    breakdown['exclamations'] = exclamations
    breakdown['cta_words'] = cta_words
    breakdown['sentiment_score'] = round(sentiment_score, 2)
    breakdown['interaction_score'] = int(round(interaction_score, 2))
    breakdown['skimming_score'] = int(round(skimming_score, 2))
    
    total_score = sentiment_score + interaction_score + skimming_score
    final = max(0.0, min(100.0, total_score))
    breakdown['final_score'] = int(round(final, 2))
    
    return final, breakdown


def score_uniqueness(text: str) -> Tuple[float, Dict]:
    """Enhanced uniqueness scoring with plagiarism indicators"""
    breakdown = {
        'research_words': 0,
        'first_person_words': 0,
        'unique_word_ratio': 0,
        'primary_research_words': 0,
        'base_score': 40.0,
        'research_bonus': 0,
        'first_person_bonus': 0,
        'uniqueness_bonus': 0,
        'primary_research_bonus': 0,
        'final_score': 0
    }
    
    if not text:
        return 0.0, breakdown
        
    research_words = len(re.findall(r'\b(research|study|survey|data|analysis|experiment|finding)\b', text.lower()))
    first_person = len(re.findall(r'\b(I|we|our|us|my|mine|ours)\b', text.lower()))
    
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    unique_ratio = len(set(words)) / len(words) if words else 0
    
    primary_research = len(re.findall(r'\b(interview|surveyed|studied|analyzed|experimented|observed)\b', text.lower()))
    
    research_bonus = min(20, research_words * 3)
    first_person_bonus = min(15, first_person * 0.8)
    uniqueness_bonus = min(15, unique_ratio * 30)
    primary_research_bonus = min(10, primary_research * 2)
    
    breakdown['research_words'] = research_words
    breakdown['first_person_words'] = first_person
    breakdown['unique_word_ratio'] = round(unique_ratio, 3)
    breakdown['primary_research_words'] = primary_research
    breakdown['research_bonus'] = round(research_bonus, 2)
    breakdown['first_person_bonus'] = round(first_person_bonus, 2)
    breakdown['uniqueness_bonus'] = round(uniqueness_bonus, 2)
    breakdown['primary_research_bonus'] = round(primary_research_bonus, 2)
    
    base_score = 40.0
    total = base_score + research_bonus + first_person_bonus + uniqueness_bonus + primary_research_bonus
    final = min(100.0, total)
    breakdown['final_score'] = round(final, 2)
    
    return final, breakdown


def score_discoverability(soup: Optional[BeautifulSoup]) -> Tuple[float, Dict]:
    """Enhanced discoverability scoring with user path simulation"""
    breakdown = {
        'has_search': False,
        'nav_count': 0,
        'has_breadcrumbs': False,
        'has_sitemap': False,
        'featured_posts': 0,
        'category_score': 0,
        'search_score': 0,
        'navigation_score': 0,
        'breadcrumb_score': 0,
        'sitemap_score': 0,
        'featured_score': 0,
        'final_score': 0
    }
    
    if not soup:
        return 0.0, breakdown
        
    has_search = bool(soup.find('input', {'type': 'search'}))
    nav_count = len(soup.find_all('nav'))
    breadcrumbs = bool(soup.find(class_=re.compile('breadcrumb', re.IGNORECASE)))
    sitemap = bool(soup.find('a', href=re.compile('sitemap', re.IGNORECASE)))
    
    featured_posts = find_featured_content(soup)
    category_organization = analyze_category_organization(soup)
    
    search_score = 15 if has_search else 5
    navigation_score = min(20, nav_count * 5)
    breadcrumb_score = 15 if breadcrumbs else 0
    sitemap_score = 10 if sitemap else 0
    featured_score = min(15, featured_posts * 3)
    category_score = min(25, category_organization)
    
    breakdown['has_search'] = has_search
    breakdown['nav_count'] = nav_count
    breakdown['has_breadcrumbs'] = breadcrumbs
    breakdown['has_sitemap'] = sitemap
    breakdown['featured_posts'] = featured_posts
    breakdown['search_score'] = search_score
    breakdown['navigation_score'] = navigation_score
    breakdown['breadcrumb_score'] = breadcrumb_score
    breakdown['sitemap_score'] = sitemap_score
    breakdown['featured_score'] = featured_score
    breakdown['category_score'] = category_score
    
    total = search_score + navigation_score + breadcrumb_score + sitemap_score + featured_score + category_score
    final = max(0.0, min(100.0, total))
    breakdown['final_score'] = round(final, 2)
    
    return final, breakdown


# def score_ad_experience(html: str, soup: Optional[BeautifulSoup]) -> Tuple[float, Dict]:
    """Enhanced ad experience analysis with detailed ad type breakdown"""
    breakdown = {
        'ad_indicator_count': 0,
        'ad_types': {},
        'placement_penalty': 0,
        'autoplay_penalty': 0,
        'ad_density_penalty': 0,
        'final_score': 100.0
    }
    
    if not html:
        return 100.0, breakdown  # No ads detected = perfect score
        
    # Define ad indicators with categories
    ad_indicators = {
        'Google Ads': ['googleads', 'adsbygoogle', 'googlesyndication'],
        'DoubleClick': ['doubleclick'],
        'General Ads': ['advertisement', 'ad-banner', 'banner-ad'],
        'Popups/Modals': ['popup', 'modal', 'overlay'],
        'Ad Containers': ['ad-container', 'ad-unit', 'ad-slot', 'ad-wrapper'],
        'Video Ads': ['video-ad', 'preroll', 'midroll'],
        'Display Ads': ['display-ad', 'banner', 'leaderboard'],
        'Sponsored': ['sponsored', 'promoted']
    }
    
    total_ad_score = 0
    html_lower = html.lower()
    
    # Count each type of ad indicator
    for category, indicators in ad_indicators.items():
        category_count = 0
        for indicator in indicators:
            count = html_lower.count(indicator)
            category_count += count
            total_ad_score += count
        
        if category_count > 0:
            breakdown['ad_types'][category] = category_count
        
    placement_score = analyze_ad_placement(soup)
    autoplay_score = detect_autoplay_media(soup)
    
    breakdown['ad_indicator_count'] = total_ad_score
    breakdown['placement_penalty'] = placement_score
    breakdown['autoplay_penalty'] = autoplay_score
    breakdown['ad_density_penalty'] = total_ad_score * 5
    
    quality_score = max(0, 100 - (total_ad_score * 5) - placement_score - autoplay_score)
    final = max(0.0, min(100.0, quality_score))
    breakdown['final_score'] = round(final, 2)
    
    return final, breakdown


def score_ad_experience(html: str, soup: Optional[BeautifulSoup]) -> Tuple[float, Dict]:
    """Enhanced ad experience analysis using structural patterns instead of keywords"""
    breakdown = {
        'ad_indicator_count': 0,
        'ad_types': {},
        'placement_penalty': 0,
        'autoplay_penalty': 0,
        'ad_density_penalty': 0,
        'final_score': 100.0
    }
    
    if not html or not soup:
        return 100.0, breakdown
        
    total_ad_score = 0
    
    # 1. SCRIPT ANALYSIS - Check for ad network scripts
    ad_scripts = 0
    script_patterns = [
        'googlesyndication.com',
        'doubleclick.net',
        'googletagservices.com',
        'adngin.com',
        'mediavine.com',
        'ezoic.com',
        'taboola.com',
        'outbrain.com',
        'criteo.com',
        'pubmatic.com',
        'amazon-adsystem.com',
        'rubiconproject.com',
        'adsafeprotected.com',
        'moatads.com',
        'scorecardresearch.com'
    ]
    
    for script in soup.find_all('script', src=True):
        src = script.get('src', '').lower()
        if any(pattern in src for pattern in script_patterns):
            ad_scripts += 1
    
    if ad_scripts > 0:
        breakdown['ad_types']['Ad Scripts'] = ad_scripts
        total_ad_score += ad_scripts
    
    # 2. IFRAME ANALYSIS - Ad iframes
    ad_iframes = 0
    iframe_patterns = ['ad', 'doubleclick', 'google', 'banner', 'sponsor', 'promo']
    
    for iframe in soup.find_all('iframe'):
        src = iframe.get('src', '').lower()
        iframe_id = iframe.get('id', '').lower()
        iframe_class = ' '.join(iframe.get('class', [])).lower()
        
        if any(pattern in src or pattern in iframe_id or pattern in iframe_class 
               for pattern in iframe_patterns):
            ad_iframes += 1
    
    if ad_iframes > 0:
        breakdown['ad_types']['Ad iFrames'] = ad_iframes
        total_ad_score += ad_iframes
    
    # 3. DIV ANALYSIS - Ad containers by class/id
    ad_divs = 0
    div_patterns = ['ad-', 'ad_', 'ads-', 'ads_', 'advertisement', 'sponsor', 'promo']
    
    for div in soup.find_all('div'):
        div_id = div.get('id', '').lower()
        div_class = ' '.join(div.get('class', [])).lower()
        
        # Check if div looks like an ad container
        if any(pattern in div_id or pattern in div_class for pattern in div_patterns):
            # Additional check: does it have dimensions that suggest an ad?
            style = div.get('style', '').lower()
            if 'width' in style or 'height' in style:
                ad_divs += 1
    
    if ad_divs > 0:
        breakdown['ad_types']['Ad Containers'] = ad_divs
        total_ad_score += ad_divs
    
    # 4. INS ANALYSIS - Google AdSense uses <ins> tags
    ad_ins = 0
    for ins in soup.find_all('ins'):
        ins_class = ' '.join(ins.get('class', [])).lower()
        if 'adsby' in ins_class or 'ad' in ins_class:
            ad_ins += 1
    
    if ad_ins > 0:
        breakdown['ad_types']['AdSense Units'] = ad_ins
        total_ad_score += ad_ins
    
    # 5. DATA ATTRIBUTE ANALYSIS - Modern ads use data-* attributes
    data_ad_elements = 0
    for elem in soup.find_all(attrs={'data-ad-client': True}):
        data_ad_elements += 1
    for elem in soup.find_all(attrs={'data-ad-slot': True}):
        data_ad_elements += 1
    for elem in soup.find_all(attrs={'data-ad-unit': True}):
        data_ad_elements += 1
    
    if data_ad_elements > 0:
        breakdown['ad_types']['Data-Ad Elements'] = data_ad_elements
        total_ad_score += data_ad_elements
    
    # 6. LINK ANALYSIS - Affiliate/sponsored links
    affiliate_links = 0
    affiliate_patterns = [
        'amazon.com/dp/',
        'amazon.com/gp/',
        'amzn.to',
        'shareasale.com',
        'avantlink.com',
        'cj.com',
        'linksynergy.com',
        'impact.com',
        'affiliaxe.com',
        'awin1.com'
    ]
    
    for link in soup.find_all('a', href=True):
        href = link.get('href', '').lower()
        rel = ' '.join(link.get('rel', [])).lower()
        
        # Check for affiliate links or sponsored rel
        if any(pattern in href for pattern in affiliate_patterns) or 'sponsored' in rel:
            affiliate_links += 1
    
    if affiliate_links > 0:
        breakdown['ad_types']['Affiliate Links'] = affiliate_links
        # Affiliate links are less intrusive, so count them at 50% weight
        total_ad_score += (affiliate_links * 0.5)
    
    # 7. STYLE ANALYSIS - Check for fixed/sticky positioning (often used for sticky ads)
    sticky_elements = 0
    for elem in soup.find_all(style=True):
        style = elem.get('style', '').lower()
        if 'position:fixed' in style.replace(' ', '') or 'position:sticky' in style.replace(' ', ''):
            # Check if it looks ad-related
            elem_class = ' '.join(elem.get('class', [])).lower()
            elem_id = elem.get('id', '').lower()
            if any(pattern in elem_class or pattern in elem_id for pattern in div_patterns):
                sticky_elements += 1
    
    if sticky_elements > 0:
        breakdown['ad_types']['Sticky/Fixed Ads'] = sticky_elements
        total_ad_score += sticky_elements
    
    # Calculate penalties
    placement_score = analyze_ad_placement(soup)
    autoplay_score = detect_autoplay_media(soup)
    
    breakdown['ad_indicator_count'] = int(total_ad_score)
    breakdown['placement_penalty'] = placement_score
    breakdown['autoplay_penalty'] = autoplay_score
    breakdown['ad_density_penalty'] = int(total_ad_score * 5)
    
    # Scoring formula: Start at 100, subtract penalties
    # - Each ad element: -5 points
    # - Bad placement: up to -20 points
    # - Autoplay: up to -15 points
    quality_score = 100 - (total_ad_score * 5) - placement_score - autoplay_score
    final = max(0.0, min(100.0, quality_score))
    breakdown['final_score'] = round(final, 2)
    
    return final, breakdown


def score_social_integration(social_data: Dict) -> Tuple[float, Dict]:
    """Enhanced social integration scoring"""
    breakdown = {
        'platforms_found': [],
        'platform_count': 0,
        'sharing_buttons': 0,
        'share_counts': 0,
        'follower_counts': 0,
        'testimonials': 0,
        'platform_score': 0,
        'sharing_score': 0,
        'social_proof_score': 0,
        'final_score': 0
    }
    
    if not social_data:
        return 0.0, breakdown
    
    platforms = ['facebook', 'twitter', 'instagram', 'linkedin', 'youtube', 'pinterest', 'tiktok']
    platforms_found = [p for p in platforms if social_data.get(p, False)]
    platform_count = len(platforms_found)
    
    sharing_buttons = social_data.get('sharing_buttons', 0)
    social_proof = social_data.get('social_proof', {})
    
    share_counts = social_proof.get('share_counts', 0)
    follower_counts = social_proof.get('follower_counts', 0)
    testimonials = social_proof.get('testimonials', 0)
    
    platform_score = platform_count * 10
    sharing_score = sharing_buttons * 3
    share_proof_score = min(share_counts * 2, 10)
    follower_proof_score = min(follower_counts * 2, 10)
    testimonial_score = min(testimonials * 3, 15)
    
    breakdown['platforms_found'] = platforms_found
    breakdown['platform_count'] = platform_count
    breakdown['sharing_buttons'] = sharing_buttons
    breakdown['share_counts'] = share_counts
    breakdown['follower_counts'] = follower_counts
    breakdown['testimonials'] = testimonials
    breakdown['platform_score'] = platform_score
    breakdown['sharing_score'] = sharing_score
    breakdown['social_proof_score'] = share_proof_score + follower_proof_score + testimonial_score
    
    total = platform_score + sharing_score + share_proof_score + follower_proof_score + testimonial_score
    final = max(0.0, min(100.0, total))
    breakdown['final_score'] = round(final, 2)
    
    return final, breakdown


def score_layout_quality(soup: Optional[BeautifulSoup], mobile_data: Dict, security_data: Dict, design_metrics: Dict) -> Tuple[float, Dict]:
    """Enhanced layout quality scoring with design analysis"""
    breakdown = {
        'base_score': 40.0,
        'has_viewport': False,
        'handheld_friendly': False,
        'touch_optimized': False,
        'has_https': False,
        'h1_count': 0,
        'viewport_score': 0,
        'mobile_score': 0,
        'security_score': 0,
        'h1_score': 0,
        'whitespace_score': 0,
        'typography_score': 0,
        'color_contrast_score': 0,
        'final_score': 0
    }
    
    score = 40.0
    
    has_viewport = mobile_data.get('has_viewport', False)
    handheld_friendly = mobile_data.get('handheld_friendly', False)
    touch_optimized = mobile_data.get('touch_optimized', False)
    has_https = security_data.get('https', False)
    
    viewport_score = 10 if has_viewport else 0
    handheld_score = 5 if handheld_friendly else 0
    touch_score = 5 if touch_optimized else 0
    security_score = 10 if has_https else 0
    
    breakdown['has_viewport'] = has_viewport
    breakdown['handheld_friendly'] = handheld_friendly
    breakdown['touch_optimized'] = touch_optimized
    breakdown['has_https'] = has_https
    breakdown['viewport_score'] = viewport_score
    breakdown['mobile_score'] = handheld_score + touch_score
    breakdown['security_score'] = security_score
    
    score += viewport_score + handheld_score + touch_score + security_score
        
    if soup:
        h1_count = len(soup.find_all('h1'))
        breakdown['h1_count'] = h1_count
        if h1_count == 1:
            score += 5
            breakdown['h1_score'] = 5
            
    whitespace = design_metrics.get('whitespace_score', 0)
    typography = design_metrics.get('typography_score', 0)
    contrast = design_metrics.get('color_contrast_score', 0)
    
    breakdown['whitespace_score'] = whitespace
    breakdown['typography_score'] = typography
    breakdown['color_contrast_score'] = contrast
    
    score += whitespace + typography + contrast
    
    final = max(0.0, min(100.0, score))
    breakdown['final_score'] = round(final, 2)
    
    return final, breakdown


def score_seo_keywords(soup: Optional[BeautifulSoup], seo_data: Dict, keyword_analysis: Dict, 
                      internal_linking: Dict, content_freshness: Dict, url: str) -> Tuple[float, Dict]:
    """Enhanced SEO scoring with comprehensive analysis"""
    breakdown = {
        'has_title': False,
        'title_length': 0,
        'title_optimal': False,
        'has_meta_desc': False,
        'meta_desc_length': 0,
        'meta_desc_optimal': False,
        'h1_count': 0,
        'h1_optimal': False,
        'is_indexed': False,
        'schema_markup_count': 0,
        'title_score': 0,
        'meta_desc_score': 0,
        'h1_score': 0,
        'indexing_score': 0,
        'keyword_score': 0,
        'linking_score': 0,
        'freshness_score': 0,
        'schema_score': 0,
        'url_score': 0,
        'final_score': 0
    }
    
    if not soup:
        return 0.0, breakdown
        
    score = 0
    
    # Title tag
    title = soup.find('title')
    if title and title.string:
        title_len = len(title.string)
        breakdown['has_title'] = True
        breakdown['title_length'] = title_len
        if 30 <= title_len <= 60:
            score += 10
            breakdown['title_optimal'] = True
            breakdown['title_score'] = 10
            
    # Meta description
    meta_desc = soup.find('meta', {'name': 'description'})
    if meta_desc and meta_desc.get('content'):
        desc_len = len(meta_desc['content'])
        breakdown['has_meta_desc'] = True
        breakdown['meta_desc_length'] = desc_len
        if 120 <= desc_len <= 160:
            score += 10
            breakdown['meta_desc_optimal'] = True
            breakdown['meta_desc_score'] = 10
            
    # H1 tag
    h1_count = len(soup.find_all('h1'))
    breakdown['h1_count'] = h1_count
    if h1_count == 1:
        score += 5
        breakdown['h1_optimal'] = True
        breakdown['h1_score'] = 5
        
    # Indexing
    if seo_data.get('indexed'):
        score += 10
        breakdown['is_indexed'] = True
        breakdown['indexing_score'] = 10
        
    # Keywords, linking, freshness
    keyword_score = keyword_analysis.get('keyword_score', 0)
    linking_score = internal_linking.get('linking_score', 0)
    freshness_score = content_freshness.get('freshness_score', 0)
    
    breakdown['keyword_score'] = keyword_score
    breakdown['linking_score'] = linking_score
    breakdown['freshness_score'] = freshness_score
    
    score += keyword_score + linking_score + freshness_score
    
    # Schema markup
    schema_markup = len(soup.find_all('script', type='application/ld+json'))
    schema_score = min(schema_markup * 3, 10)
    breakdown['schema_markup_count'] = schema_markup
    breakdown['schema_score'] = schema_score
    score += schema_score
    
    # URL structure
    url_score = analyze_url_structure(url)
    breakdown['url_score'] = url_score
    score += url_score
    
    final = max(0.0, min(100.0, score + 15))
    breakdown['final_score'] = round(final, 2)
    
    return final, breakdown


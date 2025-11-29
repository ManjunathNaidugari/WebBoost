"""
Analysis helper functions for WebBoost Analyzer.

This module contains helper functions that analyze various aspects
of the website content and structure.
"""

import re
from typing import Dict, Optional
from collections import Counter
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from webboost.utils import find_featured_content, analyze_category_organization


def analyze_citations(text: str, soup: Optional[BeautifulSoup]) -> Dict:
    """Analyze citations and attributions in content"""
    citation_data = {
        'citation_count': 0,
        'source_count': 0,
        'citation_score': 0
    }
    
    if not text:
        return citation_data
        
    citation_patterns = [
        r'\([A-Za-z]+\s*et\s*al\.?\s*\d{4}\)',
        r'\[?\d+\]?',
        r'according to [A-Z][^.]{10,100}\.',
        r'source:',
        r'study (by|from)',
        r'research (by|from)',
    ]
    
    citation_count = 0
    for pattern in citation_patterns:
        citation_count += len(re.findall(pattern, text, re.IGNORECASE))
    
    if soup:
        reference_sections = len(soup.find_all(
            class_=re.compile('reference|citation|bibliography', re.IGNORECASE)
        ))
    else:
        reference_sections = 0
    
    citation_data['citation_count'] = citation_count
    citation_data['source_count'] = reference_sections
    citation_data['citation_score'] = min(25, citation_count * 2 + reference_sections * 5)
    
    return citation_data


def analyze_skimming_optimization(soup: Optional[BeautifulSoup]) -> float:
    """Analyze how optimized the content is for skimming"""
    if not soup:
        return 0.0
        
    skimming_elements = 0
    
    headers = len(soup.find_all(['h1', 'h2', 'h3', 'h4']))
    skimming_elements += min(headers * 2, 20)
    
    lists = len(soup.find_all(['ul', 'ol']))
    skimming_elements += min(lists * 3, 15)
    
    emphasis = len(soup.find_all(['b', 'strong', 'i', 'em']))
    skimming_elements += min(emphasis * 0.5, 10)
    
    blockquotes = len(soup.find_all('blockquote'))
    skimming_elements += min(blockquotes * 2, 10)
    
    images_with_alt = len(soup.find_all('img', alt=True))
    skimming_elements += min(images_with_alt, 5)
    
    return min(40.0, skimming_elements)


def analyze_ad_placement(soup: Optional[BeautifulSoup]) -> int:
    """Analyze ad placement intrusiveness"""
    placement_score = 0
    
    if not soup:
        return placement_score
        
    body_content = soup.find('body')
    if body_content:
        first_1000_chars = str(body_content)[:1000]
        ad_indicators = ['ad', 'banner', 'popup']
        for indicator in ad_indicators:
            if indicator in first_1000_chars.lower():
                placement_score += 10
                
    content_areas = soup.find_all(class_=re.compile('content|article|post', re.IGNORECASE))
    for area in content_areas:
        area_text = str(area).lower()
        if any(indicator in area_text for indicator in ['ad', 'banner']):
            placement_score += 5
            
    return min(placement_score, 30)


def detect_autoplay_media(soup: Optional[BeautifulSoup]) -> int:
    """Detect auto-playing media elements"""
    autoplay_score = 0
    
    if not soup:
        return autoplay_score
        
    autoplay_videos = len(soup.find_all('video', attrs={'autoplay': True}))
    autoplay_score += autoplay_videos * 15
    
    autoplay_audio = len(soup.find_all('audio', attrs={'autoplay': True}))
    autoplay_score += autoplay_audio * 15
    
    return min(autoplay_score, 30)


def analyze_design_quality(soup: Optional[BeautifulSoup], html: str) -> Dict:
    """Analyze design quality metrics"""
    design_metrics = {
        'whitespace_score': 0.0,
        'typography_score': 0.0,
        'color_contrast_score': 0.0,
        'visual_hierarchy_score': 0.0
    }
    
    if not soup:
        return design_metrics
        
    crowded_elements = len(soup.find_all(style=re.compile(
        r'margin:\s*0|padding:\s*0', re.IGNORECASE
    )))
    design_metrics['whitespace_score'] = max(0, 10 - crowded_elements)
    
    font_variety = len(set(re.findall(r'font-family:\s*([^;]+)', html)))
    design_metrics['typography_score'] = min(10, font_variety * 2)
    
    low_contrast = len(re.findall(r'color:\s*#([0-9a-f]{6})', html, re.IGNORECASE))
    design_metrics['color_contrast_score'] = max(0, 10 - (low_contrast * 0.1))
    
    heading_levels = len(set(tag.name for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])))
    design_metrics['visual_hierarchy_score'] = min(10, heading_levels * 2)
    
    return design_metrics


def analyze_keywords(text: str) -> Dict:
    """Analyze keyword optimization"""
    keyword_data = {
        'primary_keywords': [],
        'keyword_density': 0,
        'keyword_score': 0
    }
    
    if not text:
        return keyword_data
        
    words = re.findall(r'\b[a-zA-Z]{5,}\b', text.lower())
    word_freq = Counter(words)
    
    stop_words = {'the', 'and', 'for', 'with', 'that', 'this', 'from', 'have', 'were', 'been', 'their', 'what'}
    meaningful_words = {word: count for word, count in word_freq.items() if word not in stop_words}
    
    top_keywords = dict(sorted(meaningful_words.items(), key=lambda x: x[1], reverse=True)[:10])
    keyword_data['primary_keywords'] = list(top_keywords.keys())
    
    total_words = len(words)
    if total_words > 0:
        keyword_density = sum(top_keywords.values()) / total_words
        keyword_data['keyword_density'] = round(keyword_density * 100, 2)
        
        if 1 <= keyword_density <= 2:
            keyword_data['keyword_score'] = 15
        elif 0.5 <= keyword_density <= 3:
            keyword_data['keyword_score'] = 10
        else:
            keyword_data['keyword_score'] = 5
            
    return keyword_data


def analyze_internal_linking(soup: Optional[BeautifulSoup], domain: str) -> Dict:
    """Analyze internal linking structure"""
    linking_data = {
        'internal_links': 0,
        'external_links': 0,
        'linking_score': 0
    }
    
    if not soup:
        return linking_data
        
    all_links = soup.find_all('a', href=True)
    
    for link in all_links:
        href = link['href']
        if isinstance(href, list):
            href = href[0]
            
        if href.startswith('/') or domain in href:
            linking_data['internal_links'] += 1
        else:
            linking_data['external_links'] += 1
            
    total_links = linking_data['internal_links'] + linking_data['external_links']
    if total_links > 0:
        internal_ratio = linking_data['internal_links'] / total_links
        if internal_ratio >= 0.6:
            linking_data['linking_score'] = 15
        elif internal_ratio >= 0.4:
            linking_data['linking_score'] = 10
        else:
            linking_data['linking_score'] = 5
            
    return linking_data


def analyze_content_freshness(text: str) -> Dict:
    """Analyze content freshness"""
    freshness_data = {
        'last_updated': None,
        'update_frequency': 0,
        'freshness_score': 0
    }
    
    if not text:
        return freshness_data
        
    date_patterns = [
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b',
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b',
        r'\b\d{4}-\d{2}-\d{2}\b'
    ]
    
    dates_found = []
    for pattern in date_patterns:
        dates_found.extend(re.findall(pattern, text, re.IGNORECASE))
        
    if dates_found:
        freshness_data['update_frequency'] = len(dates_found)
        freshness_data['freshness_score'] = min(10, len(dates_found) * 2)
        
    return freshness_data


def analyze_url_structure(url: str) -> int:
    """Analyze URL structure quality"""
    url_score = 0
    parsed = urlparse(url)
    
    path_parts = [part for part in parsed.path.split('/') if part]
    if len(path_parts) <= 3:
        url_score += 5
        
    if '-' in parsed.path and '_' not in parsed.path:
        url_score += 5
        
    meaningful_parts = sum(1 for part in path_parts if len(part) > 2)
    if meaningful_parts >= 1:
        url_score += 5
        
    return url_score


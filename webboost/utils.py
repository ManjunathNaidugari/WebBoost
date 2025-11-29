"""
Utility functions and helpers for WebBoost Analyzer.
"""

import re
from typing import Dict, List, Optional
from bs4 import BeautifulSoup


def analyze_font_sizes(soup: Optional[BeautifulSoup]) -> int:
    """Analyze font sizes for mobile readability."""
    tiny_fonts = 0
    if soup:
        # Check inline styles
        elements = soup.find_all(style=re.compile('font-size:.*[0-9]px'))
        for element in elements:
            val = element.get('style', '')
            if isinstance(val, list):
                style = ' '.join(val)
            elif val is None:
                style = ''
            else:
                style = str(val)
            
            font_match = re.search(r'font-size:\s*(\d+)px', style)
            if font_match:
                size = int(font_match.group(1))
                if size < 14:  # Considered too small for mobile
                    tiny_fonts += 1
    return tiny_fonts


def find_social_buttons(soup: Optional[BeautifulSoup]) -> int:
    """Find social sharing buttons with enhanced detection."""
    if not soup:
        return 0
        
    social_patterns = [
        'share', 'social', 'like', 'follow', 'subscribe',
        'facebook', 'twitter', 'instagram', 'linkedin', 'youtube',
        'pinterest', 'tiktok'
    ]
    
    social_elements = 0
    for pattern in social_patterns:
        social_elements += len(soup.find_all(
            class_=re.compile(pattern, re.IGNORECASE)
        ))
        social_elements += len(soup.find_all(
            id=re.compile(pattern, re.IGNORECASE)
        ))
        
    return min(social_elements, 20)  # Cap at 20


def find_social_proof(soup: Optional[BeautifulSoup]) -> Dict:
    """Find social proof elements."""
    social_proof = {
        'share_counts': 0,
        'follower_counts': 0,
        'testimonials': 0
    }
    
    if not soup:
        return social_proof
        
    # Look for share counts
    share_indicators = ['shares', 'shares-count', 'share-count', 'social-count']
    for indicator in share_indicators:
        social_proof['share_counts'] += len(soup.find_all(
            class_=re.compile(indicator, re.IGNORECASE)
        ))
        
    # Look for follower counts
    follower_indicators = ['followers', 'follower-count', 'subscribers']
    for indicator in follower_indicators:
        social_proof['follower_counts'] += len(soup.find_all(
            class_=re.compile(indicator, re.IGNORECASE)
        ))
        
    # Look for testimonials
    testimonial_indicators = ['testimonial', 'review', 'rating']
    for indicator in testimonial_indicators:
        social_proof['testimonials'] += len(soup.find_all(
            class_=re.compile(indicator, re.IGNORECASE)
        ))
        
    return social_proof


def find_featured_content(soup: Optional[BeautifulSoup]) -> int:
    """Find featured/popular posts sections."""
    if not soup:
        return 0
        
    featured_indicators = [
        'featured', 'popular', 'trending', 'recommended', 'editor.pick',
        'most.read', 'top.posts', 'best.of'
    ]
    
    featured_count = 0
    for indicator in featured_indicators:
        featured_count += len(soup.find_all(
            class_=re.compile(indicator, re.IGNORECASE)
        ))
        
    return min(featured_count, 5)


def analyze_category_organization(soup: Optional[BeautifulSoup]) -> int:
    """Analyze category and tag organization."""
    if not soup:
        return 0
        
    organization_score = 0
    
    # Categories
    categories = len(soup.find_all(class_=re.compile('category', re.IGNORECASE)))
    organization_score += min(categories * 2, 10)
    
    # Tags
    tags = len(soup.find_all(class_=re.compile('tag', re.IGNORECASE)))
    organization_score += min(tags * 1, 5)
    
    # Filtering options
    filters = len(soup.find_all(class_=re.compile('filter|sort', re.IGNORECASE)))
    organization_score += min(filters * 3, 10)
    
    return organization_score


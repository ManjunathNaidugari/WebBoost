"""
Recommendations module for WebBoost Analyzer.

This module generates actionable recommendations based on
analysis scores and collected data.
"""

from typing import Dict, List, Tuple


def generate_recommendations(scores: Dict[str, float], free_data: Dict) -> List[str]:
    """
    Generate comprehensive recommendations based on scores and data.
    
    Priority levels:
    - 🔴 CRITICAL (< 50): Must fix immediately
    - 🟠 HIGH (50-69): Important improvements needed
    - 🟡 MEDIUM (70-84): Good but can be better
    - 🟢 LOW (85-94): Minor optimizations
    - ✅ EXCELLENT (95+): Maintain current quality
    """
    recommendations = []
    
    # Sort scores by value (lowest first) for prioritization
    sorted_scores = sorted(scores.items(), key=lambda x: x[1])
    
    # Generate criterion-specific recommendations
    for criterion, score in sorted_scores:
        recs = _get_criterion_recommendations(criterion, score, free_data)
        recommendations.extend(recs)
    
    # Add data-driven recommendations
    recommendations.extend(_get_data_driven_recommendations(free_data, scores))
    
    # Sort by priority (Critical → High → Medium → Low)
    priority_order = {'🔴 CRITICAL': 0, '🟠 HIGH': 1, '🟡 MEDIUM': 2, '🟢 LOW': 3, '✅ EXCELLENT': 4}
    recommendations.sort(key=lambda x: priority_order.get(x.split(':')[0], 5))
    
    return recommendations


def _get_priority_and_emoji(score: float) -> Tuple[str, str]:
    """Determine priority level based on score"""
    if score < 50:
        return "🔴 CRITICAL", "🔴"
    elif score < 70:
        return "🟠 HIGH", "🟠"
    elif score < 85:
        return "🟡 MEDIUM", "🟡"
    elif score < 95:
        return "🟢 LOW", "🟢"
    else:
        return "✅ EXCELLENT", "✅"


def _get_criterion_recommendations(criterion: str, score: float, free_data: Dict) -> List[str]:
    """Generate specific recommendations for each criterion"""
    priority, emoji = _get_priority_and_emoji(score)
    recs = []
    
    if criterion == 'readability':
        if score < 50:
            recs.append(f"{priority}: Readability is poor ({score:.1f}/100) - drastically simplify language, use 10-15 word sentences")
        elif score < 70:
            recs.append(f"{priority}: Improve readability ({score:.1f}/100) - use shorter sentences and simpler vocabulary")
        elif score < 85:
            recs.append(f"{priority}: Good readability ({score:.1f}/100) but can improve - aim for 8th grade reading level")
        elif score < 95:
            recs.append(f"{priority}: Readability is very good ({score:.1f}/100) - minor tweaks to complex sentences recommended")
        else:
            recs.append(f"{priority}: Excellent readability ({score:.1f}/100) - maintain current writing style")
            
    elif criterion == 'informativeness':
        if score < 50:
            recs.append(f"{priority}: Content lacks depth ({score:.1f}/100) - add 1000+ words, 10+ headers, citations, and media")
        elif score < 70:
            recs.append(f"{priority}: Add more depth to content ({score:.1f}/100) - include citations, images, and structured headers")
        elif score < 85:
            recs.append(f"{priority}: Content is informative ({score:.1f}/100) - consider adding more expert citations or case studies")
        elif score < 95:
            recs.append(f"{priority}: Very informative content ({score:.1f}/100) - could add 1-2 more visual aids")
        else:
            recs.append(f"{priority}: Exceptionally comprehensive content ({score:.1f}/100) - keep up the great work")
            
    elif criterion == 'engagement':
        if score < 50:
            recs.append(f"{priority}: Content is not engaging ({score:.1f}/100) - add questions, CTAs, bullet points, and emotional language")
        elif score < 70:
            recs.append(f"{priority}: Improve engagement ({score:.1f}/100) - add interactive elements, questions, and better formatting")
        elif score < 85:
            recs.append(f"{priority}: Good engagement ({score:.1f}/100) - add 2-3 more questions or CTAs for better interaction")
        elif score < 95:
            recs.append(f"{priority}: Very engaging content ({score:.1f}/100) - consider adding one more call-to-action")
        else:
            recs.append(f"{priority}: Highly engaging content ({score:.1f}/100) - excellent use of interactive elements")
            
    elif criterion == 'uniqueness':
        if score < 50:
            recs.append(f"{priority}: Content lacks originality ({score:.1f}/100) - add personal experiences, original research, or unique insights")
        elif score < 70:
            recs.append(f"{priority}: Improve uniqueness ({score:.1f}/100) - include more original research and personal perspectives")
        elif score < 85:
            recs.append(f"{priority}: Content is fairly unique ({score:.1f}/100) - consider adding original data or case studies")
        elif score < 95:
            recs.append(f"{priority}: Good originality ({score:.1f}/100) - well done with personal perspective")
        else:
            recs.append(f"{priority}: Highly original content ({score:.1f}/100) - excellent unique insights")
            
    elif criterion == 'discoverability':
        if score < 50:
            recs.append(f"{priority}: Poor navigation ({score:.1f}/100) - add search, breadcrumbs, sitemap, and category organization")
        elif score < 70:
            recs.append(f"{priority}: Improve navigation ({score:.1f}/100) - add search functionality and breadcrumbs")
        elif score < 85:
            recs.append(f"{priority}: Navigation is good ({score:.1f}/100) - consider adding a sitemap or featured posts section")
        elif score < 95:
            recs.append(f"{priority}: Very good navigation ({score:.1f}/100) - minor improvements to category organization possible")
        else:
            recs.append(f"{priority}: Excellent navigation structure ({score:.1f}/100) - easy to discover content")
            
    elif criterion == 'ad_experience':
        if score < 50:
            recs.append(f"{priority}: Too many intrusive ads ({score:.1f}/100) - remove 80%+ of ads, especially popups and modals")
        elif score < 70:
            recs.append(f"{priority}: Ad experience needs improvement ({score:.1f}/100) - reduce ad density and remove popups")
        elif score < 85:
            recs.append(f"{priority}: Ad placement acceptable ({score:.1f}/100) - remove 2-3 more ad units for better UX")
        elif score < 95:
            recs.append(f"{priority}: Good ad balance ({score:.1f}/100) - consider removing one more ad for optimal experience")
        else:
            recs.append(f"{priority}: Excellent ad experience ({score:.1f}/100) - non-intrusive advertising")
            
    elif criterion == 'social_integration':
        if score < 50:
            recs.append(f"{priority}: Poor social integration ({score:.1f}/100) - add sharing buttons for 5-7 platforms")
        elif score < 70:
            recs.append(f"{priority}: Improve social features ({score:.1f}/100) - add more social sharing options and platforms")
        elif score < 85:
            recs.append(f"{priority}: Good social presence ({score:.1f}/100) - add 1-2 more platforms or share counts")
        elif score < 95:
            recs.append(f"{priority}: Strong social integration ({score:.1f}/100) - consider displaying share counts")
        else:
            recs.append(f"{priority}: Excellent social integration ({score:.1f}/100) - comprehensive social features")
            
    elif criterion == 'layout_quality':
        if score < 50:
            recs.append(f"{priority}: Layout needs major work ({score:.1f}/100) - enable HTTPS, add viewport tag, optimize for mobile")
        elif score < 70:
            recs.append(f"{priority}: Improve layout and design ({score:.1f}/100) - focus on mobile responsiveness and typography")
        elif score < 85:
            recs.append(f"{priority}: Good layout ({score:.1f}/100) - improve whitespace or color contrast for better readability")
        elif score < 95:
            recs.append(f"{priority}: Very good layout ({score:.1f}/100) - minor design refinements recommended")
        else:
            recs.append(f"{priority}: Excellent layout and design ({score:.1f}/100) - professional appearance")
            
    elif criterion == 'seo_keywords':
        if score < 50:
            recs.append(f"{priority}: Poor SEO optimization ({score:.1f}/100) - fix title length, meta description, add schema markup")
        elif score < 70:
            recs.append(f"{priority}: SEO needs improvement ({score:.1f}/100) - optimize title, meta tags, and keyword strategy")
        elif score < 85:
            recs.append(f"{priority}: SEO is good ({score:.1f}/100) - fine-tune keyword density or add more internal links")
        elif score < 95:
            recs.append(f"{priority}: Very good SEO ({score:.1f}/100) - consider adding more schema markup")
        else:
            recs.append(f"{priority}: Excellent SEO optimization ({score:.1f}/100) - well-optimized content")
    
    return recs


def _get_data_driven_recommendations(free_data: Dict, scores: Dict[str, float]) -> List[str]:
    """Generate additional recommendations based on raw data analysis"""
    recs = []
    
    # Keyword density
    keyword_density = free_data.get('keyword_analysis', {}).get('keyword_density', 0)
    if keyword_density < 0.5:
        recs.append("🟠 HIGH: Keyword density too low (< 0.5%) - increase to 1-2% for better SEO")
    elif keyword_density < 1.0:
        recs.append("🟡 MEDIUM: Keyword density is low (< 1%) - aim for 1-2% for optimal SEO")
    elif keyword_density > 3.0:
        recs.append("🟡 MEDIUM: Keyword density too high (> 3%) - reduce to avoid keyword stuffing penalty")
    elif keyword_density > 2.5:
        recs.append("🟢 LOW: Keyword density is slightly high (> 2.5%) - consider reducing slightly")
    
    # Internal linking
    internal_links = free_data.get('internal_linking', {}).get('internal_links', 0)
    if internal_links < 3:
        recs.append("🔴 CRITICAL: Very few internal links (< 3) - add 10-15 internal links for better navigation and SEO")
    elif internal_links < 5:
        recs.append("🟠 HIGH: Low internal links (< 5) - add 5-10 more for better site structure")
    elif internal_links < 10:
        recs.append("🟡 MEDIUM: Could use more internal links (< 10) - add 3-5 more to related content")
    elif internal_links > 50:
        recs.append("🟢 LOW: Many internal links (> 50) - ensure they're all relevant and valuable")
    
    # External linking
    external_links = free_data.get('internal_linking', {}).get('external_links', 0)
    if external_links < 2:
        recs.append("🟡 MEDIUM: Add 3-5 external links to authoritative sources for credibility")
    elif external_links > 30:
        recs.append("🟢 LOW: Many external links (> 30) - ensure all are high-quality and relevant")
    
    # HTTPS
    if not free_data.get('security', {}).get('https', False):
        recs.append("🔴 CRITICAL: Site not using HTTPS - implement SSL certificate immediately for security and SEO")
    
    # Citations
    citation_count = free_data.get('citation_analysis', {}).get('citation_count', 0)
    if citation_count < 3:
        recs.append("🟠 HIGH: Few citations found (< 3) - add 5-10 references to improve credibility")
    elif citation_count < 5:
        recs.append("🟡 MEDIUM: Add 2-3 more citations for better authority")
    elif citation_count > 20:
        recs.append("🟢 LOW: Excellent use of citations (> 20) - well-researched content")
    
    # Word count
    word_count = free_data.get('content_stats', {}).get('word_count', 0)
    if word_count < 300:
        recs.append("🔴 CRITICAL: Content too short (< 300 words) - expand to at least 1000 words for blog posts")
    elif word_count < 600:
        recs.append("🟠 HIGH: Content is short (< 600 words) - aim for 1000-2500 words for better depth")
    elif word_count < 1000:
        recs.append("🟡 MEDIUM: Content could be longer (< 1000 words) - add 300-500 more words for comprehensive coverage")
    elif word_count > 3000:
        recs.append("🟢 LOW: Long-form content (> 3000 words) - ensure it's well-structured with headers and breaks")
    
    # Headers
    header_count = free_data.get('content_stats', {}).get('header_count', 0)
    if header_count < 3:
        recs.append("🟠 HIGH: Too few headers (< 3) - add 5-10 headers (H2, H3) for better structure")
    elif header_count < 5:
        recs.append("🟡 MEDIUM: Add 2-3 more headers for better content organization")
    elif header_count > 20:
        recs.append("🟢 LOW: Many headers (> 20) - ensure hierarchy is logical (H2 → H3 → H4)")
    
    # Images
    image_count = free_data.get('content_stats', {}).get('image_count', 0)
    if image_count < 1:
        recs.append("🟠 HIGH: No images found - add 3-5 relevant images for visual appeal")
    elif image_count < 3:
        recs.append("🟡 MEDIUM: Add 2-3 more images to enhance visual engagement")
    elif image_count > 20:
        recs.append("🟢 LOW: Many images (> 20) - ensure all have alt text and are optimized for web")
    
    # Mobile optimization
    mobile_data = free_data.get('mobile', {})
    if not mobile_data.get('has_viewport'):
        recs.append("🔴 CRITICAL: Missing viewport meta tag - add for mobile optimization")
    if not mobile_data.get('handheld_friendly'):
        recs.append("🟡 MEDIUM: Improve mobile-friendliness - test on mobile devices and fix issues")
    
    # Schema markup
    if 'seo' in free_data:
        schema_count = free_data.get('readability_details', {}).get('schema_markup_count', 0)
        if schema_count == 0:
            recs.append("🟡 MEDIUM: No schema markup found - add JSON-LD structured data for better rich snippets")
        elif schema_count == 1:
            recs.append("🟢 LOW: Good start with schema markup - consider adding more types (Article, BreadcrumbList, etc.)")
    
    # Load time (if available)
    if 'performance' in free_data and free_data['performance']:
        load_time = free_data['performance'].get('load_time', 0)
        if load_time > 5:
            recs.append("🔴 CRITICAL: Page load time is very slow (> 5s) - optimize images, minify CSS/JS, use CDN")
        elif load_time > 3:
            recs.append("🟠 HIGH: Page load time is slow (> 3s) - optimize images and enable caching")
        elif load_time > 2:
            recs.append("🟡 MEDIUM: Page load time could be faster (> 2s) - minor optimizations recommended")
        elif load_time < 1:
            recs.append("🟢 LOW: Excellent load time (< 1s) - great performance")
    
    return recs


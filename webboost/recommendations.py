"""
Recommendations module for WebBoost Analyzer.

This module generates actionable recommendations based on
analysis scores and collected data.
"""

from typing import Dict, List


def generate_recommendations(scores: Dict[str, float], free_data: Dict) -> List[str]:
    """Generate enhanced recommendations based on scores and data"""
    recommendations = []
    
    for criterion, score in scores.items():
        if score < 70:
            priority = "🔴 CRITICAL" if score < 50 else "🟠 HIGH"
            
            if criterion == 'readability':
                rec = f"{priority}: Improve readability (score: {score:.1f}) - use shorter sentences and simpler vocabulary"
            elif criterion == 'layout_quality':
                rec = f"{priority}: Improve mobile responsiveness and design (score: {score:.1f})"
            elif criterion == 'seo_keywords':
                rec = f"{priority}: Optimize SEO tags and keyword strategy (score: {score:.1f})"
            elif criterion == 'ad_experience':
                rec = f"{priority}: Reduce ad density and improve placement (score: {score:.1f})"
            elif criterion == 'informativeness':
                rec = f"{priority}: Add more citations and depth to content (score: {score:.1f})"
            elif criterion == 'engagement':
                rec = f"{priority}: Add more interactive elements and improve skimmability (score: {score:.1f})"
            elif criterion == 'uniqueness':
                rec = f"{priority}: Include more original research and unique perspectives (score: {score:.1f})"
            elif criterion == 'discoverability':
                rec = f"{priority}: Improve navigation and content organization (score: {score:.1f})"
            elif criterion == 'social_integration':
                rec = f"{priority}: Enhance social media integration and sharing options (score: {score:.1f})"
            else:
                rec = f"{priority}: Improve {criterion} (score: {score:.1f})"
                
            recommendations.append(rec)
            
    if free_data.get('keyword_analysis', {}).get('keyword_density', 0) < 0.5:
        recommendations.append("🟡 MEDIUM: Increase keyword density to 1-2% for better SEO")
        
    if free_data.get('internal_linking', {}).get('internal_links', 0) < 5:
        recommendations.append("🟡 MEDIUM: Add more internal links to improve navigation and SEO")
        
    if not free_data.get('security', {}).get('https', False):
        recommendations.append("🔴 CRITICAL: Implement HTTPS for security and SEO")
        
    if free_data.get('citation_analysis', {}).get('citation_count', 0) < 3:
        recommendations.append("🟡 MEDIUM: Add more citations to improve content credibility")
        
    return recommendations[:10]


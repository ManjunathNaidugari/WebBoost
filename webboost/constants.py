"""
Constants and configuration for WebBoost Analyzer.
"""

# Scoring weights for each criterion (must sum to 1.0)
SCORING_WEIGHTS = {
    'informativeness': 0.20,
    'readability': 0.15,
    'engagement': 0.15,
    'uniqueness': 0.15,
    'layout_quality': 0.10,
    'discoverability': 0.10,
    'seo_keywords': 0.05,
    'ad_experience': 0.05,
    'social_integration': 0.05
}

# Verify weights sum to 1.0
assert abs(sum(SCORING_WEIGHTS.values()) - 1.0) < 0.001, "Weights must sum to 1.0"


# WebBoost Quick Start Guide

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Run Web Interface
```bash
python3 app.py
```
Then open http://localhost:5001 in your browser.

### 3. Command Line Usage
```bash
python3 cli.py analyze https://yourblog.com/post
```

### 4. Test the System
```bash
python3 test_analyzer.py
```

---

## 🐛 Enable Debug Mode

See detailed score breakdown:

```bash
export WEBBOOST_DEBUG=1
python3 test_analyzer.py
```

This shows:
- Individual criterion scores
- Weights applied
- Contribution to overall score
- Visual bar chart
- Verification that math is correct

---

## 📊 Understanding Your Results

### Overall Score
- **90-100**: 🌟 Excellent - Minimal improvements needed
- **80-89**: ✅ Good - Minor optimizations recommended
- **70-79**: 🟡 Fair - Moderate improvements needed
- **60-69**: 🟠 Needs Work - Significant improvements needed
- **< 60**: 🔴 Poor - Major overhaul recommended

### Key Metrics for Blog Posts

**For Maximum Reach:**
1. **Informativeness (20%)**: Aim for 75+
   - Add citations and references
   - Include images and media
   - Use clear header structure

2. **Readability (15%)**: Aim for 70+
   - Use shorter sentences
   - Simplify vocabulary
   - Break up long paragraphs

3. **Engagement (15%)**: Aim for 70+
   - Add questions and CTAs
   - Use bullet points and lists
   - Include emotional language

4. **SEO Keywords (5%)**: Aim for 65+
   - Optimize title (30-60 chars)
   - Add meta description (120-160 chars)
   - Use meaningful URLs

---

## 🔍 How Scoring Works

### Single Source of Truth
```python
scores = {
    'readability': 72.0,
    'informativeness': 85.0,
    'engagement': 68.0,
    # ... etc
}
```

### Weighted Aggregation
```python
overall_score = (
    readability × 0.15 +
    informativeness × 0.20 +
    engagement × 0.15 +
    uniqueness × 0.15 +
    layout_quality × 0.10 +
    discoverability × 0.10 +
    seo_keywords × 0.05 +
    ad_experience × 0.05 +
    social_integration × 0.05
)
```

### Validation
Every score is validated to be in [0, 100] range:
```python
validated_score = max(0.0, min(100.0, raw_score))
```

---

## 📁 Project Structure

```
WebBoost-project/
├── app.py                  # Flask web interface
├── cli.py                  # Command-line interface
├── test_analyzer.py        # Test script
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore rules (includes __pycache__)
├── SCORING_WORKFLOW.md    # Detailed documentation
├── README.md              # Project overview
│
├── webboost/              # Main package
│   ├── __init__.py
│   ├── core.py           # Main analyzer (REFACTORED)
│   ├── scoring.py        # Scoring functions (REFACTORED)
│   ├── analysis.py       # Helper analysis functions
│   ├── data_collection.py # Data gathering
│   ├── recommendations.py # Recommendation generation
│   ├── constants.py      # Weights and config
│   └── utils.py          # Utility functions
│
├── templates/            # HTML templates
│   ├── landing.html      # Landing Page
│   ├── index.html        # Analyzing Page
│   └── results.html      # Results Page
│
└── static/              # CSS and JavaScript
    ├── css/style.css
    └── js/
        ├── main.js      # Frontend logic
        ├── paricles.js. # cursor trail animation logic
    
```

---

## 🎯 Workflow Example

```python
# 1. Create analyzer
from webboost import WebBoostAnalyzer
analyzer = WebBoostAnalyzer("https://yourblog.com/post")

# 2. Run analysis
results = await analyzer.analyze()

# 3. Check overall score
print(f"Overall: {results['overall_score']}/100")

# 4. Review individual scores
for criterion, score in results['scores'].items():
    print(f"{criterion}: {score}/100")

# 5. Get recommendations
for rec in results['recommendations']:
    print(rec)

# 6. Check score breakdown (for debugging)
for criterion, breakdown in results['score_breakdown'].items():
    print(f"{criterion}: {breakdown['raw_score']} × {breakdown['weight']} = {breakdown['contribution']}")
```

## 💡 Tips for Content Creators

1. **Run Before Publishing**: Always analyze drafts
2. **Target 70+ Overall**: Good baseline for quality content
3. **Fix Critical First**: Address 🔴 issues before 🟠
4. **Iterate**: Re-run after making changes
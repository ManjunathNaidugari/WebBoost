# WebBoost Analyzer

A comprehensive website analysis tool that evaluates websites across 9 key criteria without requiring any API keys.

## Features

- **9 Scoring Criteria**: Readability, Informativeness, Engagement, Uniqueness, Layout Quality, Discoverability, SEO Keywords, Ad Experience, Social Integration
- **Performance Metrics**: Load time, Core Web Vitals, Lighthouse scores
- **Free & Open Source**: Uses Google Lighthouse and Playwright - no paid APIs needed
- **Beautiful Web UI**: Modern, responsive interface
- **Detailed Recommendations**: Actionable insights to improve your website

## Installation

1. Install dependencies:
```bash
pip3 install -r requirements.txt
playwright install chromium
```

2. (Optional) Install NLTK data for enhanced readability:
```bash
python3 -c "import nltk; nltk.download('cmudict')"
```

## Usage

### Web Interface (Recommended)

Start the web server:
```bash
python3 app.py
```

Then open your browser to:
```
http://localhost:5000
```

Enter a website URL and click "Analyze Website"!

### Command Line

Run the CLI tool:
```bash
python3 cli.py https://example.com
```

Or use the analyzer programmatically:
```python
from webboost import WebBoostAnalyzer
import asyncio

async def main():
    analyzer = WebBoostAnalyzer("https://example.com")
    results = await analyzer.analyze()
    print(f"Score: {results['overall_score']}/100")

asyncio.run(main())
```

## Project Structure

```
weboost3/
├── app.py                          # Flask web application
├── cli.py                          # Command-line interface
├── config.py                       # API keys configuration (optional)
├── requirements.txt                # Python dependencies
├── webboost/                       # Main package
│   ├── __init__.py                 # Package exports
│   ├── constants.py                # Scoring weights and constants
│   ├── core.py                     # Main WebBoostAnalyzer class
│   ├── data_collection.py          # Data gathering functions
│   ├── scoring.py                  # Scoring functions
│   ├── analysis.py                 # Analysis helper functions
│   ├── recommendations.py           # Recommendation generation
│   └── utils.py                    # Utility functions
├── templates/
│   └── index.html                  # Web UI template
└── static/
    ├── css/
    │   └── style.css               # Styles
    └── js/
        └── main.js                 # Frontend logic
```

## Scoring Criteria

1. **Informativeness** (20%) - Content depth, citations, structure
2. **Readability** (15%) - Text complexity, readability formulas
3. **Engagement** (15%) - Sentiment, CTAs, skimmability
4. **Uniqueness** (15%) - Original content, research indicators
5. **Layout Quality** (10%) - Mobile-friendliness, design, security
6. **Discoverability** (10%) - Navigation, search, organization
7. **SEO Keywords** (5%) - Meta tags, keywords, indexing
8. **Ad Experience** (5%) - Ad density, placement, autoplay
9. **Social Integration** (5%) - Social links, sharing, proof

## Configuration

Edit `config.py` to add API keys (optional):
- WebPageTest API Key (if you want to use it)
- Google Search API Key (for enhanced SEO checking)

## Notes

- The analyzer works completely without API keys
- SSL certificate warnings are normal and don't affect functionality
- Analysis takes 30-60 seconds per website
- Results may vary slightly between runs due to dynamic content

## License

Free to use and modify!

# webboost

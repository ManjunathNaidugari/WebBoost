# WebBoost Analyzer - Architecture

## Code Organization

The codebase has been refactored into a modular structure for better maintainability and readability.

### Package Structure

```
webboost/
├── __init__.py          # Package initialization, exports main class
├── constants.py          # Scoring weights and configuration constants
├── core.py              # Main WebBoostAnalyzer class (orchestrator)
├── data_collection.py   # Data gathering (performance, mobile, SEO, social, security)
├── scoring.py           # All scoring functions (9 criteria)
├── analysis.py          # Analysis helper functions (citations, keywords, etc.)
├── recommendations.py   # Recommendation generation
└── utils.py             # Utility functions (font analysis, social detection, etc.)
```

### Module Responsibilities

#### `webboost/__init__.py`
- Package initialization
- Exports the main `WebBoostAnalyzer` class
- Version information

#### `webboost/constants.py`
- `SCORING_WEIGHTS`: Dictionary defining weights for each criterion
- Configuration constants
- Ensures weights sum to 1.0

#### `webboost/core.py`
- Main `WebBoostAnalyzer` class
- Provides clean public API
- Orchestrates analysis workflow
- Currently uses legacy code as bridge (gradual migration)

#### `webboost/utils.py`
- Helper functions for analysis
- Font size analysis
- Social button detection
- Content organization analysis

### Entry Points

#### Web Application (`app.py`)
- Flask web server
- RESTful API endpoint: `/analyze`
- Serves HTML interface

#### CLI Tool (`cli.py`)
- Command-line interface
- Usage: `python3 cli.py <url>`
- Displays formatted results

### Migration Status

**Current State:**
- ✅ Package structure created
- ✅ Clean public API (`from webboost import WebBoostAnalyzer`)
- ✅ Updated entry points (app.py, cli.py)
- ✅ All functions migrated to proper modules
- ✅ Legacy file removed
- ✅ Fully modular and maintainable

### Usage Examples

#### As a Package
```python
from webboost import WebBoostAnalyzer
import asyncio

async def analyze_site(url):
    analyzer = WebBoostAnalyzer(url)
    results = await analyzer.analyze()
    return results

results = asyncio.run(analyze_site("https://example.com"))
```

#### Command Line
```bash
python3 cli.py https://example.com
```

#### Web Interface
```bash
python3 app.py
# Then visit http://localhost:8080
```

### Benefits of New Structure

1. **Better Organization**: Related functions grouped together
2. **Easier Maintenance**: Clear separation of concerns
3. **Improved Readability**: Smaller, focused modules
4. **Professional Structure**: Standard Python package layout
5. **Gradual Migration**: Can migrate functions incrementally

### File Naming

- ✅ `cli.py` - Clear, descriptive name
- ✅ `app.py` - Standard Flask app name
- ✅ `webboost/` - Professional package name
- ⚠️ `analyzer need to resolve_issues.py` - Legacy file (to be removed after migration)


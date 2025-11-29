#!/usr/bin/env python3
"""
Simple test script to run the WebBoost Analyzer
Works without any API keys!
"""

import asyncio
import sys
import importlib.util
from typing import Optional

# Load the analyzer from the new package structure
try:
    from webboost import WebBoostAnalyzer
except ImportError:
    # Fallback to old structure if new package not available
    spec = importlib.util.spec_from_file_location(
        "analyzer", 
        "analyzer need to resolve_issues.py"
    )
    if spec and spec.loader:
        analyzer_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(analyzer_module)
        WebBoostAnalyzer = analyzer_module.WebBoostAnalyzer
    else:
        raise ImportError("Could not create module spec")

async def test_analyzer(url: Optional[str] = None):
    """Test the analyzer with a URL"""
    if url is None:
        # Default test URL from the main function
        url = "https://www.gimmesomeoven.com/life/blogs-im-reading-and-loving-lately"
    
    print(f"🔍 Analyzing: {url}")
    print("⏳ This may take 30-60 seconds...\n")
    
    try:
        analyzer = WebBoostAnalyzer(url)
        results = await analyzer.analyze()
        
        print(f"\n{'='*60}")
        print(f"📊 Overall Score: {results['overall_score']}/100")
        print(f"{'='*60}\n")
        
        print("📈 Detailed Scores:")
        for criterion, score in results['scores'].items():
            bar = "█" * int(score / 2)
            print(f"  {criterion:20s}: {score:5.1f}/100 {bar}")
        
        print("\n🔍 Additional Metrics:")
        metrics = results['free_data_sources']
        print(f"  Keyword Density: {metrics['keyword_analysis'].get('keyword_density', 0):.2f}%")
        print(f"  Internal Links: {metrics['internal_linking'].get('internal_links', 0)}")
        print(f"  External Links: {metrics['internal_linking'].get('external_links', 0)}")
        print(f"  Citations Found: {metrics['citation_analysis'].get('citation_count', 0)}")
        
        if 'performance' in metrics and metrics['performance']:
            perf = metrics['performance']
            if 'load_time' in perf:
                print(f"  Load Time: {perf['load_time']:.2f}s")
            if 'lcp' in perf:
                print(f"  LCP (Largest Contentful Paint): {perf['lcp']:.2f}ms")
            if 'lighthouse' in perf:
                lh = perf['lighthouse']
                print(f"  Lighthouse Performance Score: {lh.get('performance_score', 0):.1f}/100")
        
        print("\n💡 Top Recommendations:")
        for i, rec in enumerate(results['recommendations'][:5], 1):
            print(f"  {i}. {rec}")
        
        print(f"\n{'='*60}")
        print("✅ Analysis complete!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    # Get URL from command line or use default
    test_url = sys.argv[1] if len(sys.argv) > 1 else None
    
    print("🚀 WebBoost Analyzer - Test Run")
    print("=" * 60)
    print("ℹ️  No API keys required - using free tools only!")
    print("=" * 60)
    
    success = asyncio.run(test_analyzer(test_url))
    sys.exit(0 if success else 1)


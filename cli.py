#!/usr/bin/env python3
"""
Simple test script to run the WebBoost Analyzer
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
        
        # NEW: Show detailed breakdowns for each criterion
        if 'score_breakdowns' in results:
            print("\n" + "="*60)
            print("🔬 DETAILED SUB-CRITERIA BREAKDOWN")
            print("="*60)
            
            for criterion, breakdown in results['score_breakdowns'].items():
                print(f"\n📊 {criterion.upper().replace('_', ' ')} (Score: {results['scores'][criterion]:.1f}/100)")
                print("-" * 60)
                
                for key, value in breakdown.items():
                    if key == 'final_score':
                        continue  # Skip as we already show it above
                    
                    # Special handling for ad_types dictionary
                    if key == 'ad_types' and isinstance(value, dict):
                        if value:
                            print(f"  • Ad Types Found:")
                            for ad_type, count in sorted(value.items(), key=lambda x: x[1], reverse=True):
                                print(f"    - {ad_type:20s}: {count} occurrences")
                        else:
                            print(f"  • Ad Types Found: None")
                        continue
                    
                    # Format the output nicely
                    if isinstance(value, bool):
                        value_str = "✅ Yes" if value else "❌ No"
                    elif isinstance(value, (int, float)):
                        value_str = f"{value:.2f}" if isinstance(value, float) else str(value)
                    elif isinstance(value, list):
                        value_str = ", ".join(str(v) for v in value) if value else "None"
                    else:
                        value_str = str(value)
                    
                    # Make the key more readable
                    readable_key = key.replace('_', ' ').title()
                    print(f"  • {readable_key:30s}: {value_str}")
        
        print(f"\n{'='*60}")
        
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
        
        print("\n💡 Recommendations:")
        
        # Group recommendations by priority
        critical = [r for r in results['recommendations'] if r.startswith('🔴 CRITICAL')]
        high = [r for r in results['recommendations'] if r.startswith('🟠 HIGH')]
        medium = [r for r in results['recommendations'] if r.startswith('🟡 MEDIUM')]
        low = [r for r in results['recommendations'] if r.startswith('🟢 LOW')]
        excellent = [r for r in results['recommendations'] if r.startswith('✅ EXCELLENT')]
        
        if critical:
            print(f"\n  🔴 CRITICAL ({len(critical)}):")
            for i, rec in enumerate(critical, 1):
                print(f"    {i}. {rec.split(': ', 1)[1]}")
        
        if high:
            print(f"\n  🟠 HIGH PRIORITY ({len(high)}):")
            for i, rec in enumerate(high, 1):
                print(f"    {i}. {rec.split(': ', 1)[1]}")
        
        if medium:
            print(f"\n  🟡 MEDIUM PRIORITY ({len(medium)}):")
            for i, rec in enumerate(medium, 1):
                print(f"    {i}. {rec.split(': ', 1)[1]}")
        
        if low:
            print(f"\n  🟢 LOW PRIORITY ({len(low)}):")
            for i, rec in enumerate(low, 1):
                print(f"    {i}. {rec.split(': ', 1)[1]}")
        
        if excellent:
            print(f"\n  ✅ DOING GREAT ({len(excellent)}):")
            for i, rec in enumerate(excellent, 1):
                print(f"    {i}. {rec.split(': ', 1)[1]}")
        
        total_recs = len(results['recommendations'])
        print(f"\n  📊 Total Recommendations: {total_recs}")
        
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
    # Support both "python3 cli.py <URL>" and "python3 cli.py analyze <URL>"
    test_url = None
    
    if len(sys.argv) > 1:
        # Check if first argument is "analyze" (skip it)
        if sys.argv[1].lower() == "analyze":
            test_url = sys.argv[2] if len(sys.argv) > 2 else None
        else:
            test_url = sys.argv[1]
    
    if not test_url:
        print("❌ Error: Please provide a URL to analyze")
        print("\nUsage:")
        print("  python3 cli.py <URL>")
        print("  python3 cli.py analyze <URL>")
        print("\nExample:")
        print("  python3 cli.py https://example.com/blog-post")
        sys.exit(1)
    
    print("🚀 WebBoost Analyzer - Test Run")
    print("=" * 60)
    print("ℹ️  No API keys required - using free tools only!")
    print("=" * 60)
    
    success = asyncio.run(test_analyzer(test_url))
    sys.exit(0 if success else 1)


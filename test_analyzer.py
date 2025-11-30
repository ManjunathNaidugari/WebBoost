#!/usr/bin/env python3
"""
Test script for WebBoost Analyzer
Tests the refactored scoring system
"""

import asyncio
import os
from webboost import WebBoostAnalyzer

async def test_analyzer():
    """Test the analyzer with a sample URL"""
    
    # Enable debug mode to see score breakdown
    os.environ['WEBBOOST_DEBUG'] = '1'
    
    # Test with a popular blog
    test_url = "https://www.smashingmagazine.com/2024/01/web-design-done-well-delightful-details/"
    
    print(f"🧪 Testing WebBoost Analyzer with: {test_url}")
    print("="*60)
    
    try:
        analyzer = WebBoostAnalyzer(test_url)
        results = await analyzer.analyze()
        
        print(f"\n✅ Analysis completed successfully!")
        print(f"\n📊 Overall Score: {results['overall_score']:.1f}/100")
        
        print("\n📋 Individual Scores:")
        for criterion, score in results['scores'].items():
            status = "✅" if score >= 70 else "⚠️" if score >= 50 else "❌"
            print(f"  {status} {criterion:20s}: {score:5.1f}/100")
        
        print(f"\n💡 Top Recommendations ({len(results['recommendations'])} total):")
        for i, rec in enumerate(results['recommendations'][:5], 1):
            print(f"  {i}. {rec}")
        
        # Verify score breakdown
        if 'score_breakdown' in results:
            print("\n🔍 Score Breakdown Verification:")
            total_contribution = sum(
                breakdown['contribution'] 
                for breakdown in results['score_breakdown'].values()
            )
            print(f"  Sum of contributions: {total_contribution:.2f}")
            print(f"  Overall score: {results['overall_score']:.2f}")
            print(f"  Match: {'✅' if abs(total_contribution - results['overall_score']) < 0.1 else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_analyzer())
    exit(0 if success else 1)

"""
Data collection module for WebBoost Analyzer.

This module handles all data gathering functions including:
- Performance metrics (Playwright, Lighthouse)
- Mobile friendliness checks
- SEO data collection
- Security information
- Social metrics
"""

import re
import json
import subprocess
import aiohttp
from typing import Dict, Optional
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from webboost.utils import analyze_font_sizes, find_social_buttons, find_social_proof


async def get_performance_metrics(page) -> Optional[Dict]:
    """Get performance metrics using Playwright's CDP"""
    try:
        # Get performance timing
        performance_timing = await page.evaluate("""() => {
            const perf = window.performance.timing;
            return {
                navigationStart: perf.navigationStart,
                domContentLoaded: perf.domContentLoadedEventEnd - perf.navigationStart,
                loadComplete: perf.loadEventEnd - perf.navigationStart,
                domInteractive: perf.domInteractive - perf.navigationStart,
                firstPaint: perf.responseStart - perf.navigationStart,
            };
        }""")
        
        # Get Core Web Vitals if available
        web_vitals = await page.evaluate("""() => {
            return new Promise((resolve) => {
                const vitals = {};
                if (window.performance && window.performance.getEntriesByType) {
                    const paintEntries = window.performance.getEntriesByType('paint');
                    paintEntries.forEach(entry => {
                        if (entry.name === 'first-contentful-paint') {
                            vitals.fcp = entry.startTime;
                        }
                    });
                    
                    const lcpEntries = window.performance.getEntriesByType('largest-contentful-paint');
                    if (lcpEntries.length > 0) {
                        vitals.lcp = lcpEntries[lcpEntries.length - 1].startTime;
                    }
                }
                
                const resources = window.performance.getEntriesByType('resource');
                vitals.resource_count = resources.length;
                vitals.total_transfer_size = resources.reduce((sum, r) => sum + (r.transferSize || 0), 0);
                
                resolve(vitals);
            });
        }""")
        
        metrics = {
            'load_time': performance_timing.get('loadComplete', 0) / 1000,
            'dom_content_loaded': performance_timing.get('domContentLoaded', 0) / 1000,
            'dom_interactive': performance_timing.get('domInteractive', 0) / 1000,
            'first_paint': performance_timing.get('firstPaint', 0) / 1000,
            **web_vitals
        }
        
        return metrics
    except Exception as e:
        print(f"Performance metrics error: {e}")
        return None


async def get_free_performance_data(url: str, performance_metrics: Optional[Dict], load_time: Optional[float]) -> Dict:
    """Get performance data using Google Lighthouse metrics via Playwright"""
    performance_data = {}
    
    if performance_metrics:
        performance_data.update(performance_metrics)
        performance_data['source'] = 'playwright_cdp'
    elif load_time:
        performance_data['load_time'] = load_time
        performance_data['source'] = 'basic_timing'
    
    # Try to run Lighthouse CLI if available
    lighthouse_data = await run_lighthouse_cli(url)
    if lighthouse_data:
        performance_data['lighthouse'] = lighthouse_data
        performance_data['source'] = 'lighthouse_cli'
        
    return performance_data


async def run_lighthouse_cli(url: str) -> Optional[Dict]:
    """Run Google Lighthouse CLI for detailed performance analysis"""
    try:
        result = subprocess.run(
            ['which', 'lighthouse'],
            capture_output=True,
            text=True,
            timeout=2
        )
        
        if result.returncode != 0:
            return None
        
        cmd = [
            'lighthouse',
            url,
            '--chrome-flags=--headless',
            '--output=json',
            '--output-path=/dev/stdout',
            '--quiet',
            '--only-categories=performance'
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            lighthouse_json = json.loads(result.stdout)
            audits = lighthouse_json.get('audits', {})
            categories = lighthouse_json.get('categories', {})
            
            return {
                'performance_score': categories.get('performance', {}).get('score', 0) * 100,
                'first_contentful_paint': audits.get('first-contentful-paint', {}).get('numericValue', 0),
                'largest_contentful_paint': audits.get('largest-contentful-paint', {}).get('numericValue', 0),
                'total_blocking_time': audits.get('total-blocking-time', {}).get('numericValue', 0),
                'cumulative_layout_shift': audits.get('cumulative-layout-shift', {}).get('numericValue', 0),
                'speed_index': audits.get('speed-index', {}).get('numericValue', 0),
                'time_to_interactive': audits.get('interactive', {}).get('numericValue', 0),
            }
    except subprocess.TimeoutExpired:
        print("Lighthouse CLI timed out")
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"Lighthouse CLI error: {e}")
    
    return None


async def get_mobile_friendly_check(soup: Optional[BeautifulSoup]) -> Dict:
    """Enhanced mobile friendliness check"""
    mobile_data = {'mobile_friendly': True, 'issues': []}
    
    try:
        if soup:
            viewport = bool(soup.find('meta', {'name': 'viewport'}))
            mobile_data['has_viewport'] = viewport
            
            mobile_meta = soup.find('meta', {'name': 'HandheldFriendly'})
            mobile_data['handheld_friendly'] = bool(mobile_meta)
            
            tiny_fonts = analyze_font_sizes(soup)
            if tiny_fonts > 5:
                mobile_data['issues'].append('Potential small font sizes')
                
            touch_elements = len(soup.find_all(attrs={'ontouchstart': True}))
            mobile_data['touch_optimized'] = touch_elements > 0
            
    except Exception as e:
        print(f"Mobile check error: {e}")
        
    return mobile_data


async def get_seo_data_free(domain: str) -> Dict:
    """Enhanced SEO data collection"""
    seo_data = {}
    
    try:
        google_check_url = f"https://www.google.com/search?q=site:{domain}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(google_check_url, headers=headers) as response:
                content = await response.text()
                
                if 'did not match any documents' not in content:
                    seo_data['indexed'] = True
                    match = re.search(r'About ([0-9,]+) results', content)
                    if match:
                        seo_data['approx_results'] = int(match.group(1).replace(',', ''))
                else:
                    seo_data['indexed'] = False
                    
    except Exception as e:
        print(f"SEO data error: {e}")
        
    return seo_data


async def get_ssl_security_info(url: str) -> Dict:
    """Check SSL and security information"""
    security_data = {}
    
    try:
        parsed = urlparse(url)
        if parsed.scheme == 'https':
            security_data['https'] = True
            security_data['secure'] = True
        else:
            security_data['https'] = False
            security_data['secure'] = False
            
    except Exception as e:
        print(f"Security check error: {e}")
        
    return security_data


async def get_social_metrics_free(html: str, soup: Optional[BeautifulSoup]) -> Dict:
    """Enhanced social metrics collection"""
    social_data = {}
    
    platforms = ['facebook', 'twitter', 'instagram', 'linkedin', 'youtube', 'pinterest', 'tiktok']
    
    for platform in platforms:
        pattern = rf'{platform}\.com/[\w\.\-]+'
        social_data[platform] = bool(re.search(pattern, html, re.IGNORECASE))
        
    social_data['sharing_buttons'] = find_social_buttons(soup)
    social_data['social_proof'] = find_social_proof(soup)
    
    return social_data


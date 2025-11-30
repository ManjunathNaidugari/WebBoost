#!/usr/bin/env python3
"""
WebBoost Flask web application for analyzing blogs
"""

import asyncio
from flask import Flask, render_template, request
from webboost import WebBoostAnalyzer

app = Flask(__name__)

def run_async(coro):
    """Helper to run async functions in Flask"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

@app.route('/')
def landing():
    """Landing hero page"""
    try:
        return render_template('landing.html')
    except Exception as e:
        return f"Error loading template: {str(e)}", 500

@app.route('/analyzer')
def analyzer():
    """Analyzer input page"""
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Error loading template: {str(e)}", 500

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze a website"""
    try:
        if WebBoostAnalyzer is None:
            error_msg = 'Analyzer module not loaded. Please check server logs.'
            return render_template('index.html', error=error_msg)
        
        url = request.form.get('url', '').strip()
        
        if not url:
            error_msg = 'URL is required'
            return render_template('index.html', error=error_msg)
        
        # Add https:// if no protocol specified
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Run the analyzer
        analyzer = WebBoostAnalyzer(url)
        results = run_async(analyzer.analyze())
        
        return render_template('dashboard.html', results=results)
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Analysis error: {error_details}")
        return render_template('index.html', error=f"Analysis failed: {str(e)}")

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5001) 


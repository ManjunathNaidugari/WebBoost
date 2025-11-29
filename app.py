#!/usr/bin/env python3
"""
WebBoost Analyzer - Web Interface
Flask web application for analyzing websites
"""

from flask import Flask, render_template, request, jsonify
import asyncio
import importlib.util
import sys
import os

app = Flask(__name__)

# Load the analyzer from the new package structure
try:
    from webboost import WebBoostAnalyzer
except ImportError:
    # Fallback to old structure if new package not available
    try:
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
    except Exception as e:
        print(f"Warning: Could not load analyzer module: {e}")
        print("The web interface will still work, but analysis will fail.")
        WebBoostAnalyzer = None

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

@app.route('/test')
def test():
    """Test route to verify Flask is working"""
    return "<h1>Flask is working! ✅</h1><p>If you see this, the server is running correctly.</p>"

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze a website"""
    try:
        if WebBoostAnalyzer is None:
            error_msg = 'Analyzer module not loaded. Please check server logs.'
            if request.is_json:
                return jsonify({'success': False, 'error': error_msg}), 500
            return render_template('index.html', error=error_msg)
        
        # Get URL from JSON or Form data
        if request.is_json:
            data = request.get_json()
            url = data.get('url', '').strip()
        else:
            url = request.form.get('url', '').strip()
        
        if not url:
            error_msg = 'URL is required'
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            return render_template('index.html', error=error_msg)
        
        # Add https:// if no protocol specified
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Run the analyzer
        analyzer = WebBoostAnalyzer(url)
        results = run_async(analyzer.analyze())
        
        # Return JSON or Render Template
        if request.is_json:
            return jsonify({
                'success': True,
                'results': results
            })
        else:
            return render_template('results.html', results=results)
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Analysis error: {error_details}")
        
        if request.is_json:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
        else:
            return render_template('index.html', error=f"Analysis failed: {str(e)}")

if __name__ == '__main__':
    print("🚀 Starting WebBoost Analyzer Web Interface...")
    print("📊 Open http://localhost:5001 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5001)


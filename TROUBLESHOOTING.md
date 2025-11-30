# Troubleshooting - Blank Page Issue

## Quick Fixes

### 1. Check if server is running
```bash
# Start the server
python3 app.py

# You should see:
# 🚀 Starting WebBoost Analyzer Web Interface...
# 📊 Open http://localhost:5001 in your browser
# * Running on http://0.0.0.0:5001
```

### 2. Check the URL
Make sure you're visiting:
- `http://localhost:5001` (not https://)
- Or `http://127.0.0.1:5001`

### 3. Test the server
Visit: `http://localhost:5001/test`
- If you see "Flask is working! ✅" - server is fine
- If blank/error - server issue

### 4. Check browser console
1. Open browser Developer Tools (F12 or Cmd+Option+I)
2. Go to Console tab
3. Look for red error messages
4. Go to Network tab - check if CSS/JS files are loading (status 200)

### 5. Clear browser cache
- Hard refresh: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
- Or clear cache in browser settings

### 6. Check file structure
Make sure these files exist:
```
weboost3/
├── app.py
├── templates/
│   └── index.html
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

### 7. Common Issues

**Issue: "Template not found"**
- Make sure `templates/` folder exists
- Make sure `.html` files are inside `templates/`

**Issue: CSS/JS not loading**
- Check browser Network tab
- Verify static files exist
- Check Flask static folder path

**Issue: JavaScript errors**
- Open browser console (F12)
- Look for errors in red
- Check if `main.js` is loading

## Still not working?

1. Check terminal for error messages
2. Try accessing `http://localhost:5000/test` first
3. Check if port 5000 is already in use:
   ```bash
   lsof -i :5000
   ```
4. Try a different port:
   ```python
   app.run(debug=True, host='0.0.0.0', port=8080)
   ```


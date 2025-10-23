# Static Assets Directory

This directory contains the web UI files for the LLM Inference Server.

## Structure

```
static/
├── index.html          # Main HTML page
├── css/
│   └── style.css       # All styles
└── js/
    └── app.js          # Application logic
```

## Files

### `index.html`
- Main web interface
- Semantic HTML5 structure
- Links to external CSS and JS files

### `css/style.css`
- Complete stylesheet
- Responsive design
- Animation keyframes
- Component-based organization

### `js/app.js`
- All client-side logic
- API communication
- Event handlers
- State management (chat history)

## Usage

The static files are automatically served by FastAPI via:
```python
app.mount("/static", StaticFiles(directory="static"), name="static")
```

Access points:
- Web UI: `http://localhost:8000/ui`
- CSS: `http://localhost:8000/static/css/style.css`
- JS: `http://localhost:8000/static/js/app.js`

## Development

To modify the UI:
1. Edit the appropriate file (HTML/CSS/JS)
2. Restart the server: `sudo systemctl restart llm-server`
3. Hard refresh browser (Ctrl+Shift+R)

## Features

- **Tab Navigation**: Switch between Generate, Complete, Chat, and Batch
- **Real-time Stats**: Display tokens/sec, time, and token counts
- **API Key Support**: Optional authentication field
- **Responsive Design**: Works on desktop and tablet
- **Loading States**: Spinner animations during processing
- **Error Handling**: User-friendly error messages

## Browser Compatibility

- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- Modern browsers with ES6+ support required

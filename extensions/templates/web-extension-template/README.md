# Web Extension Template

A template for creating new uDOS web extensions.

## Overview

This template provides the basic structure and boilerplate for creating a web-based uDOS extension with HTML/CSS/JavaScript frontend and Python/Flask backend.

## Directory Structure

```
web-extension-template/
├── app.py              # Flask application
├── manifest.json       # Extension manifest
├── requirements.txt    # Python dependencies
├── static/            # Static assets
│   ├── css/          # Stylesheets
│   │   └── style.css
│   └── js/           # JavaScript
│       └── app.js
└── templates/         # HTML templates
    └── index.html
```

## Features

- 🌐 Web-based interface on configurable port
- 🎨 Modern CSS styling with uDOS theme integration
- ⚡ JavaScript functionality with uDOS API
- 🔌 Flask API endpoints
- 🔧 uDOS core integration

## Development

### Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the extension:
   ```bash
   python app.py
   ```

3. Open in browser:
   ```
   http://localhost:8999
   ```

### API Endpoints

- `GET /` - Main extension page
- `GET /api/status` - Extension status
- `GET /api/info` - Extension information

### File Structure

```
my-test-extension/
├── app.py              # Main Flask application
├── manifest.json       # Extension metadata
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── static/
│   ├── css/
│   │   └── style.css  # Extension styles
│   └── js/
│       └── app.js     # Extension JavaScript
└── templates/
    └── index.html     # Main HTML template
```

## Integration with uDOS

This extension can be managed using uDOS POKE commands:

```bash
# Start the extension
POKE START my-test-extension

# Check status
POKE STATUS my-test-extension

# Get information
POKE INFO my-test-extension

# Stop the extension
POKE STOP my-test-extension
```

## Customization

1. Edit `templates/index.html` for UI changes
2. Modify `static/css/style.css` for styling
3. Update `static/js/app.js` for functionality
4. Extend `app.py` for backend features

## Author

Created by: uDOS Developer
Generated: 2025-11-03 23:45:49

## License

This extension is part of the uDOS ecosystem.

# 🌐 uDOS Sorcerer Web Browser Module

Advanced web automation and scraping capabilities for the uDOS Sorcerer role.

## 🎯 Overview

This module provides SimpleBrowser.NET-inspired web automation tools for uDOS, enabling:
- **Web Scraping**: Extract data from websites using CSS selectors
- **API Integration**: Make REST API calls and handle JSON responses  
- **Link Extraction**: Find and filter links from web pages
- **Image Harvesting**: Extract image URLs and metadata
- **File Downloads**: Download files from web URLs
- **Metadata Extraction**: Get page titles, descriptions, and meta tags
- **Browser Testing**: Built-in test suite for validation

## 🚀 Quick Start

### Basic Web Scraping
```bash
# Test the system
python3 web_commands.py web.test

# Scrape elements from a webpage
python3 web_commands.py web.scrape "https://example.com" '{"title": "h1", "links": "a"}'

# Extract all links
python3 web_commands.py web.links "https://github.com"

# Get page metadata
python3 web_commands.py web.metadata "https://example.com"
```

### uDOS Interface Integration
Use the 🔮 Sorcerer emoji in the uDOS interface:
1. Click the 🔮 sorcerer icon
2. Type: `SORCERER web` to see web commands
3. Use commands like: `SORCERER web.test`

## 📁 Module Structure

```
sorcerer/web-browser/
├── simple_scraper.py      # Core scraping engine (no browser dependencies)
├── browser_automation.py  # Full browser automation (requires Selenium)
├── web_commands.py        # Command interface for uDOS
├── web_bridge.py          # uDOS UI integration bridge
├── requirements.txt       # Python dependencies
├── scraped_data/          # Downloaded files and scraped data
└── README.md             # This file
```

## 🛠️ Available Commands

### Web Scraping Commands
- `web.scrape <url> <selectors_json>` - Extract elements using CSS selectors
- `web.links <url> [filter_pattern]` - Extract all links, optionally filtered
- `web.images <url>` - Extract all image URLs and metadata
- `web.metadata <url>` - Get comprehensive page metadata
- `web.download <url> [filename]` - Download files from URLs
- `web.api <url> [method] [data_json]` - Make API requests
- `web.test` - Run comprehensive test suite
- `web.help` - Show detailed help

### Command Examples

#### Scrape Specific Elements
```bash
python3 web_commands.py web.scrape "https://news.ycombinator.com" '{
    "titles": ".titleline > a",
    "scores": ".score",
    "comments": ".subtext a[href*=item]"
}'
```

#### Extract Links with Filter
```bash
# Get all Python file links
python3 web_commands.py web.links "https://github.com/user/repo" ".*\\.py$"
```

#### API Integration
```bash
# GET request
python3 web_commands.py web.api "https://api.github.com/users/octocat"

# POST request with data
python3 web_commands.py web.api "https://httpbin.org/post" "POST" '{"key": "value"}'
```

## 🔌 uDOS Integration

### Sorcerer Commands
In the uDOS interface, use these commands:

```
SORCERER web                    # Show web automation help
SORCERER web.test              # Run test suite
SORCERER cast                  # Show advanced administration
```

### Emoji Controls
- 🔮 **Sorcerer Icon**: Click to access advanced system administration
- Combined with other emojis for complex operations

## 🧪 Testing

The module includes comprehensive testing:

```bash
# Run all tests
python3 web_commands.py web.test

# Test specific functionality
python3 simple_scraper.py  # CLI testing
python3 web_bridge.py web.test  # Bridge testing
```

Test coverage includes:
- ✅ Basic page scraping
- ✅ API requests and JSON handling
- ✅ Link extraction and filtering
- ✅ Error handling and edge cases

## 📦 Dependencies

### Required Python Packages
```bash
pip3 install requests beautifulsoup4 lxml
```

### Optional (for full browser automation)
```bash
pip3 install selenium webdriver-manager
```

## 🎭 SimpleBrowser.NET Inspiration

This module draws inspiration from SimpleBrowser.NET features:
- **Lightweight scraping** without full browser overhead
- **CSS selector support** for precise element targeting
- **Form handling** and data extraction
- **Session management** for complex workflows
- **Error handling** and retry mechanisms

## 🔒 Security & Best Practices

### Rate Limiting
- Built-in delays between requests
- Respectful of robots.txt (when configured)
- User-Agent identification as uDOS-Sorcerer

### Data Handling
- Scraped data stored in `scraped_data/` directory
- JSON export for structured data
- Automatic timestamping of scraping sessions

### Error Handling
- Comprehensive error catching and reporting
- Timeout protection for hanging requests
- Network error recovery

## 🌟 Advanced Features

### Smart Data Extraction
- Automatic content type detection
- Relative URL resolution
- Image metadata extraction
- Link categorization and filtering

### Performance Optimization
- Efficient request session management
- Minimal memory footprint
- Parallel processing capabilities (coming soon)

### Integration Points
- uDOS command system integration
- JSON-based data exchange
- Real-time progress reporting
- CLI and programmatic interfaces

## 🚀 Future Enhancements

- [ ] Full browser automation with Selenium
- [ ] JavaScript execution support
- [ ] Advanced form filling
- [ ] Screenshot capture
- [ ] Multi-threaded scraping
- [ ] Proxy support
- [ ] Cookie management
- [ ] Custom header injection

## 📊 Usage Statistics

Track your web automation with built-in analytics:
- Request counts and timing
- Success/failure rates
- Data volume metrics
- Popular target sites

---

**Part of uDOS Sorcerer Module - Level 80 Access**  
*Advanced Web Automation and System Administration*

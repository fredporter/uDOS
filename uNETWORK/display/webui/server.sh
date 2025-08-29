#!/bin/bash
# Simple HTTP Server for uDOS Web UI

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UI_PORT="${UI_PORT:-8080}"
UI_HOST="${UI_HOST:-localhost}"

# Check if Python is available
check_python() {
    if command -v python3 >/dev/null 2>&1; then
        echo "python3"
    elif command -v python >/dev/null 2>&1; then
        echo "python"
    else
        return 1
    fi
}

# Start HTTP server using Python
start_python_server() {
    local python_cmd="$1"
    
    echo "🌐 Starting uDOS Web UI Server"
    echo "================================"
    echo "Host: $UI_HOST"
    echo "Port: $UI_PORT"
    echo "Directory: $SCRIPT_DIR"
    echo "URL: http://$UI_HOST:$UI_PORT"
    echo ""
    echo "🚀 Server starting..."
    
    cd "$SCRIPT_DIR"
    
    if [ "$python_cmd" = "python3" ]; then
        python3 -m http.server "$UI_PORT" --bind "$UI_HOST"
    else
        python -m SimpleHTTPServer "$UI_PORT"
    fi
}

# Start server with Node.js (if available)
start_node_server() {
    cat > "$SCRIPT_DIR/server.js" << 'NODEJS_EOF'
const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

const PORT = process.env.UI_PORT || 8080;
const HOST = process.env.UI_HOST || 'localhost';

const mimeTypes = {
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'application/javascript',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.gif': 'image/gif',
    '.ico': 'image/x-icon'
};

const server = http.createServer((req, res) => {
    const parsedUrl = url.parse(req.url);
    let pathname = parsedUrl.pathname;
    
    // Default to index.html
    if (pathname === '/') {
        pathname = '/index.html';
    }
    
    // API routes
    if (pathname.startsWith('/api/')) {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end('{"message": "API endpoint simulation"}');
        return;
    }
    
    const filePath = path.join(__dirname, pathname);
    
    fs.readFile(filePath, (err, data) => {
        if (err) {
            res.writeHead(404, { 'Content-Type': 'text/plain' });
            res.end('404 Not Found');
            return;
        }
        
        const ext = path.extname(filePath);
        const mimeType = mimeTypes[ext] || 'text/plain';
        
        res.writeHead(200, { 'Content-Type': mimeType });
        res.end(data);
    });
});

server.listen(PORT, HOST, () => {
    console.log(`🌐 uDOS Web UI Server running at http://${HOST}:${PORT}/`);
});
NODEJS_EOF

    echo "🌐 Starting uDOS Web UI Server with Node.js"
    echo "============================================"
    echo "Host: $UI_HOST"
    echo "Port: $UI_PORT"
    echo "URL: http://$UI_HOST:$UI_PORT"
    echo ""
    
    cd "$SCRIPT_DIR"
    node server.js
}

# Main server startup
main() {
    case "${1:-auto}" in
        "python"|"python3")
            local python_cmd="$(check_python)"
            if [ $? -eq 0 ]; then
                start_python_server "$python_cmd"
            else
                echo "❌ Python not found"
                exit 1
            fi
            ;;
        "node")
            if command -v node >/dev/null 2>&1; then
                start_node_server
            else
                echo "❌ Node.js not found"
                exit 1
            fi
            ;;
        "auto")
            if command -v node >/dev/null 2>&1; then
                start_node_server
            else
                local python_cmd="$(check_python)"
                if [ $? -eq 0 ]; then
                    start_python_server "$python_cmd"
                else
                    echo "❌ No suitable web server found (Python or Node.js required)"
                    exit 1
                fi
            fi
            ;;
        "help"|*)
            echo "uDOS Web UI Server"
            echo "Usage: $0 {python|node|auto|help}"
            echo ""
            echo "Options:"
            echo "  python    - Use Python HTTP server"
            echo "  node      - Use Node.js HTTP server"
            echo "  auto      - Auto-detect available server"
            echo "  help      - Show this help"
            ;;
    esac
}

# Execute if called directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi

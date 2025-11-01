#!/bin/bash

# uDOS Extension Installer: cmd.js Web Terminal
# Downloads and configures mrchimp/cmd terminal emulator for uDOS

set -e  # Exit on error

EXTENSION_NAME="cmd"
EXTENSION_DIR="extensions/clone/web/cmd"
REPO_URL="https://github.com/mrchimp/cmd.git"
MIN_NODE_VERSION="14"

echo "======================================================================"
echo "🖥️  cmd.js Web Terminal Installer for uDOS"
echo "======================================================================"
echo ""
echo "This script will install mrchimp/cmd - an HTML5 command line terminal"
echo "for browser-based terminal emulation with uDOS integration."
echo ""

# Check if already installed
if [ -d "$EXTENSION_DIR" ]; then
    echo "⚠️  cmd.js is already installed at $EXTENSION_DIR"
    read -p "Reinstall? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Installation cancelled."
        exit 0
    fi
    echo "🗑️  Removing existing installation..."
    rm -rf "$EXTENSION_DIR"
fi

# Ensure clone/web directory exists
mkdir -p "extensions/clone/web"

# Check for internet connectivity
echo "🌐 Checking internet connectivity..."
if ! ping -c 1 github.com &> /dev/null; then
    echo "❌ ERROR: No internet connection detected."
    echo "   Please connect to the internet and try again."
    exit 1
fi

# Check for Node.js
echo "🔍 Checking for Node.js..."
if ! command -v node &> /dev/null; then
    echo "❌ ERROR: Node.js not found."
    echo ""
    echo "   cmd.js requires Node.js $MIN_NODE_VERSION or higher."
    echo ""
    echo "   Install Node.js from:"
    echo "   - macOS: brew install node"
    echo "   - Linux: https://nodejs.org/ or use your package manager"
    echo "   - Windows: https://nodejs.org/"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt "$MIN_NODE_VERSION" ]; then
    echo "❌ ERROR: Node.js version $MIN_NODE_VERSION or higher required."
    echo "   Current version: $(node --version)"
    echo "   Please upgrade Node.js."
    exit 1
fi

echo "✅ Node.js $(node --version) found"

# Check for npm
if ! command -v npm &> /dev/null; then
    echo "❌ ERROR: npm not found."
    echo "   npm should be installed with Node.js."
    exit 1
fi

echo "✅ npm $(npm --version) found"

# Check for git
if ! command -v git &> /dev/null; then
    echo "❌ ERROR: git not found."
    echo "   Please install git first."
    exit 1
fi

# Check for Grunt CLI (optional, for building)
if ! command -v grunt &> /dev/null; then
    echo "⚠️  Grunt CLI not found globally. Will install as dev dependency."
    NEED_GRUNT_CLI=true
else
    echo "✅ Grunt CLI found"
    NEED_GRUNT_CLI=false
fi

# Create web directory if it doesn't exist
echo ""
echo "📁 Creating directory structure..."
mkdir -p extensions/web

# Clone repository
echo ""
echo "📦 Cloning cmd repository from $REPO_URL..."
cd extensions/web
if ! git clone "$REPO_URL" cmd 2>&1 | tee /tmp/cmd_clone.log; then
    echo "❌ ERROR: Failed to clone repository."
    echo "   Check /tmp/cmd_clone.log for details."
    exit 1
fi

cd cmd

# Install dependencies
echo ""
echo "📦 Installing Node.js dependencies..."
echo "   This may take a few minutes..."
if ! npm install 2>&1 | tee /tmp/cmd_install.log; then
    echo "❌ ERROR: npm install failed."
    echo "   Check /tmp/cmd_install.log for details."
    exit 1
fi

# Install Grunt CLI locally if needed
if [ "$NEED_GRUNT_CLI" = true ]; then
    echo ""
    echo "📦 Installing Grunt CLI as dev dependency..."
    npm install --save-dev grunt-cli
fi

# Build distribution files
echo ""
echo "🔨 Building cmd.js distribution files..."
if ! npm run build 2>&1 | tee /tmp/cmd_build.log; then
    # Try using grunt directly
    if command -v grunt &> /dev/null; then
        echo "⚠️  npm run build failed, trying grunt directly..."
        if ! grunt 2>&1 | tee /tmp/cmd_grunt.log; then
            echo "❌ ERROR: Build failed."
            echo "   Check /tmp/cmd_build.log and /tmp/cmd_grunt.log for details."
            exit 1
        fi
    else
        echo "❌ ERROR: Build failed and grunt not available."
        echo "   Check /tmp/cmd_build.log for details."
        exit 1
    fi
fi

# Verify installation
echo ""
echo "✅ Verifying installation..."

REQUIRED_FILES=(
    "dist/js/cmd.min.js"
    "dist/css/cmd.min.css"
    "example.html"
)

MISSING_FILES=()
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
    echo "❌ ERROR: Installation incomplete. Missing files:"
    for file in "${MISSING_FILES[@]}"; do
        echo "   - $file"
    done
    exit 1
fi

# Count installed files
JS_FILES=$(find dist/js -name "*.js" 2>/dev/null | wc -l | tr -d ' ')
CSS_FILES=$(find dist/css -name "*.css" 2>/dev/null | wc -l | tr -d ' ')

echo "✅ cmd.js installed successfully!"
echo ""
echo "   📊 Installation Summary:"
echo "   ├─ JavaScript files: $JS_FILES"
echo "   ├─ CSS files: $CSS_FILES"
echo "   ├─ Node modules: $(ls -1 node_modules 2>/dev/null | wc -l | tr -d ' ')"
echo "   └─ Location: $(pwd)"
echo ""

# Return to uDOS root
cd ../../..

# Create uDOS integration file
echo "🔧 Creating uDOS integration..."
cat > "$EXTENSION_DIR/udos_cmd_bridge.html" << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>uDOS Web Terminal</title>
    <link rel="stylesheet" href="dist/css/cmd.min.css">
    <style>
        body {
            margin: 0;
            padding: 0;
            background-color: #101010;
            font-family: var(--udos-font), Menlo, Consolas, Monaco, monospace;
        }
        #terminal {
            width: 100vw;
            height: 100vh;
            padding: 20px;
            box-sizing: border-box;
        }

        /* Monaspace Font Family - All 5 Variants */
        @font-face {
            font-family: 'Monaspace Neon';
            src: url('../../clone/fonts/monaspace/MonaspaceNeon-Regular.woff2') format('woff2');
            font-weight: 400;
            font-style: normal;
            font-display: swap;
        }
        @font-face {
            font-family: 'Monaspace Neon';
            src: url('../../clone/fonts/monaspace/MonaspaceNeon-Bold.woff2') format('woff2');
            font-weight: 700;
            font-style: normal;
            font-display: swap;
        }
        @font-face {
            font-family: 'Monaspace Neon';
            src: url('../../clone/fonts/monaspace/MonaspaceNeon-Italic.woff2') format('woff2');
            font-weight: 400;
            font-style: italic;
            font-display: swap;
        }

        @font-face {
            font-family: 'Monaspace Argon';
            src: url('../../clone/fonts/monaspace/MonaspaceArgon-Regular.woff2') format('woff2');
            font-weight: 400;
            font-style: normal;
            font-display: swap;
        }
        @font-face {
            font-family: 'Monaspace Argon';
            src: url('../../clone/fonts/monaspace/MonaspaceArgon-Bold.woff2') format('woff2');
            font-weight: 700;
            font-style: normal;
            font-display: swap;
        }
        @font-face {
            font-family: 'Monaspace Argon';
            src: url('../../clone/fonts/monaspace/MonaspaceArgon-Italic.woff2') format('woff2');
            font-weight: 400;
            font-style: italic;
            font-display: swap;
        }

        @font-face {
            font-family: 'Monaspace Xenon';
            src: url('../../clone/fonts/monaspace/MonaspaceXenon-Regular.woff2') format('woff2');
            font-weight: 400;
            font-style: normal;
            font-display: swap;
        }
        @font-face {
            font-family: 'Monaspace Xenon';
            src: url('../../clone/fonts/monaspace/MonaspaceXenon-Bold.woff2') format('woff2');
            font-weight: 700;
            font-style: normal;
            font-display: swap;
        }
        @font-face {
            font-family: 'Monaspace Xenon';
            src: url('../../clone/fonts/monaspace/MonaspaceXenon-Italic.woff2') format('woff2');
            font-weight: 400;
            font-style: italic;
            font-display: swap;
        }

        @font-face {
            font-family: 'Monaspace Radon';
            src: url('../../clone/fonts/monaspace/MonaspaceRadon-Regular.woff2') format('woff2');
            font-weight: 400;
            font-style: normal;
            font-display: swap;
        }
        @font-face {
            font-family: 'Monaspace Radon';
            src: url('../../clone/fonts/monaspace/MonaspaceRadon-Bold.woff2') format('woff2');
            font-weight: 700;
            font-style: normal;
            font-display: swap;
        }
        @font-face {
            font-family: 'Monaspace Radon';
            src: url('../../clone/fonts/monaspace/MonaspaceRadon-Italic.woff2') format('woff2');
            font-weight: 400;
            font-style: italic;
            font-display: swap;
        }

        @font-face {
            font-family: 'Monaspace Krypton';
            src: url('../../clone/fonts/monaspace/MonaspaceKrypton-Regular.woff2') format('woff2');
            font-weight: 400;
            font-style: normal;
            font-display: swap;
        }
        @font-face {
            font-family: 'Monaspace Krypton';
            src: url('../../clone/fonts/monaspace/MonaspaceKrypton-Bold.woff2') format('woff2');
            font-weight: 700;
            font-style: normal;
            font-display: swap;
        }
        @font-face {
            font-family: 'Monaspace Krypton';
            src: url('../../clone/fonts/monaspace/MonaspaceKrypton-Italic.woff2') format('woff2');
            font-weight: 400;
            font-style: italic;
            font-display: swap;
        }

        /* Default font - Neon (can be changed via localStorage) */
        :root {
            --udos-font: 'Monaspace Neon', monospace;
            --udos-font-size: 14px;
            --udos-line-height: 1.5;
        }

        /* Apply font settings to terminal */
        #terminal, .cmd, .cmd-output, .cmd-prompt {
            font-family: var(--udos-font) !important;
            font-size: var(--udos-font-size) !important;
            line-height: var(--udos-line-height) !important;
            font-feature-settings: "liga" 1, "calt" 1;
        }

        /* uDOS status bar */
        #udos-status {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: #1a1a1a;
            color: #00ff00;
            padding: 5px 20px;
            font-size: 12px;
            font-family: var(--udos-font);
            border-top: 1px solid #333;
            display: flex;
            justify-content: space-between;
        }
    </style>
</head>
<body>
    <div id="terminal"></div>
    <div id="udos-status">
        <span id="font-info">Font: Monaspace Neon</span>
        <span id="backend-status">Backend: Disconnected</span>
    </div>

    <script src="//code.jquery.com/jquery-1.11.0.min.js"></script>
    <script src="dist/js/cmd.min.js"></script>
    <script>
        // uDOS Configuration
        const uDOS = {
            // Font management
            fonts: ['Monaspace Neon', 'Monaspace Argon', 'Monaspace Xenon', 'Monaspace Radon', 'Monaspace Krypton'],
            currentFont: localStorage.getItem('udos_font') || 'Monaspace Neon',

            // Backend API endpoint (to be implemented)
            backendURL: 'http://localhost:5000/api/command',
            backendConnected: false,

            setFont: function(fontName) {
                if (this.fonts.includes(fontName)) {
                    this.currentFont = fontName;
                    document.documentElement.style.setProperty('--udos-font', fontName);
                    localStorage.setItem('udos_font', fontName);
                    document.getElementById('font-info').textContent = 'Font: ' + fontName;
                    return true;
                }
                return false;
            },

            // Execute command on backend (placeholder for future Flask/FastAPI integration)
            executeCommand: function(command) {
                // TODO: Implement actual HTTP request to uDOS backend
                // For now, simulate offline mode
                return null;
            }
        };

        // Initialize font from localStorage
        document.documentElement.style.setProperty('--udos-font', uDOS.currentFont);
        document.getElementById('font-info').textContent = 'Font: ' + uDOS.currentFont;

        // uDOS Terminal Integration
        var udos_terminal = new Cmd({
            selector: '#terminal',
            history_id: 'udos_cmd_history',
            external_processor: function(input, cmd) {
                const trimmed = input.trim().toLowerCase();
                const parts = input.trim().split(/\s+/);
                const command = parts[0].toUpperCase();

                // Built-in web terminal commands
                if (trimmed === 'help') {
                    return {
                        cmd_out: '<strong>🔮 uDOS Web Terminal</strong><br><br>' +
                                '<strong>Web Commands:</strong><br>' +
                                '  help           - Show this help<br>' +
                                '  clear          - Clear screen<br>' +
                                '  invert         - Toggle dark/light theme<br>' +
                                '  font [variant] - Show or set font<br>' +
                                '  fonts          - List available fonts<br><br>' +
                                '<strong>Font Variants:</strong><br>' +
                                '  neon    - Neo-grotesque sans (default)<br>' +
                                '  argon   - Humanist sans<br>' +
                                '  xenon   - Slab serif<br>' +
                                '  radon   - Handwriting style<br>' +
                                '  krypton - Mechanical sans<br><br>' +
                                '<em>Note: Backend integration coming soon...</em>'
                    };
                }

                if (trimmed === 'fonts') {
                    return {
                        cmd_out: '<strong>Available Monaspace Fonts:</strong><br>' +
                                uDOS.fonts.map((f, i) =>
                                    (f === uDOS.currentFont ? '→ ' : '  ') +
                                    f +
                                    (f === uDOS.currentFont ? ' (current)' : '')
                                ).join('<br>') +
                                '<br><br>Use: <em>font &lt;variant&gt;</em> to change'
                    };
                }

                if (command === 'FONT') {
                    if (parts.length === 1) {
                        return {
                            cmd_out: 'Current font: <strong>' + uDOS.currentFont + '</strong><br>' +
                                    'Use: <em>font &lt;variant&gt;</em> to change<br>' +
                                    'Available: neon, argon, xenon, radon, krypton'
                        };
                    } else {
                        const variant = parts[1].toLowerCase();
                        const fontMap = {
                            'neon': 'Monaspace Neon',
                            'argon': 'Monaspace Argon',
                            'xenon': 'Monaspace Xenon',
                            'radon': 'Monaspace Radon',
                            'krypton': 'Monaspace Krypton'
                        };

                        if (fontMap[variant]) {
                            const success = uDOS.setFont(fontMap[variant]);
                            if (success) {
                                return {
                                    cmd_out: '✅ Font changed to: <strong>' + fontMap[variant] + '</strong>'
                                };
                            }
                        }
                        return {
                            cmd_out: '❌ Unknown font variant: ' + variant + '<br>' +
                                    'Available: neon, argon, xenon, radon, krypton'
                        };
                    }
                }

                if (trimmed === 'status') {
                    return {
                        cmd_out: '<strong>uDOS Web Terminal Status:</strong><br>' +
                                'Font: ' + uDOS.currentFont + '<br>' +
                                'Backend: ' + (uDOS.backendConnected ? 'Connected ✅' : 'Disconnected ⚠️') + '<br>' +
                                'History: ' + (localStorage.getItem('udos_cmd_history') ? 'Enabled' : 'Disabled')
                    };
                }

                // Try to forward to backend (not yet implemented)
                // const backendResponse = uDOS.executeCommand(input);
                // if (backendResponse) {
                //     return { cmd_out: backendResponse };
                // }

                // Unknown command
                return {
                    cmd_out: '❌ Unknown command: <em>' + command + '</em><br>' +
                            'Type <strong>help</strong> for available commands.'
                };
            }
        });

        // Set uDOS-style prompt
        udos_terminal.setPrompt('🔮 > ');

        console.log('🔮 uDOS Web Terminal initialized');
        console.log('Font:', uDOS.currentFont);
    </script>
</body>
</html>
EOF

echo "✅ Created uDOS integration bridge: $EXTENSION_DIR/udos_cmd_bridge.html"
echo ""

echo "======================================================================"
echo "✅ Installation Complete!"
echo "======================================================================"
echo ""
echo "📖 Next Steps:"
echo ""
echo "1. Start the cmd terminal server:"
echo "   SERVER START cmd"
echo ""
echo "2. View the terminal in your browser:"
echo "   Open: http://localhost:3000"
echo ""
echo "3. Manage the server:"
echo "   SERVER STATUS cmd     # Check status"
echo "   SERVER STOP cmd       # Stop server"
echo ""
echo "4. Install Monaspace fonts (if not already installed):"
echo "   bash extensions/setup_monaspace.sh"
echo ""
echo "5. Customize fonts via uDOS:"
echo "   FONT LIST             # View available fonts"
echo "   FONT SET ARGON        # Change font variant"
echo ""
echo "📚 Documentation:"
echo "   - cmd.js: $(pwd)/$EXTENSION_DIR/README.md"
echo "   - Upstream: https://github.com/mrchimp/cmd"
echo "   - Example: $(pwd)/$EXTENSION_DIR/example.html"
echo ""
echo "🎨 Features:"
echo "   ✓ Command history (localStorage)"
echo "   ✓ Tab completion"
echo "   ✓ Light/dark themes"
echo "   ✓ Monaspace font support"
echo "   ✓ JSON API for command processing"
echo ""
echo "Happy terminal emulation! 🚀"
echo ""

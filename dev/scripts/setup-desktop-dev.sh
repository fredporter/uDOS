#!/bin/bash
# uDOS Desktop App Development Environment Setup
# Installs Node.js, Rust, and Tauri for native desktop application development

set -euo pipefail

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🏗️ Setting up uDOS Desktop App Development Environment...${NC}"
echo ""

# Get script directory and uDOS root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo -e "${BLUE}📂 uDOS Root: $UDOS_ROOT${NC}"

# Check if running as wizard
if [[ ! -d "$UDOS_ROOT/wizard" ]]; then
    echo -e "${RED}❌ Desktop development requires wizard role${NC}"
    exit 1
fi

# Function to install Node.js via NodeSource
install_nodejs() {
    echo -e "${BLUE}📦 Installing Node.js 20 LTS...${NC}"
    
    if command -v node >/dev/null 2>&1; then
        local node_version=$(node --version | sed 's/v//')
        echo -e "${GREEN}✅ Node.js $node_version already installed${NC}"
        return 0
    fi
    
    case "$(uname -s)" in
        Linux)
            # Install Node.js via NodeSource
            curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
            sudo apt-get install -y nodejs
            ;;
        Darwin)
            # Install Node.js via Homebrew
            if command -v brew >/dev/null 2>&1; then
                brew install node
            else
                echo -e "${YELLOW}⚠️ Please install Homebrew first or download Node.js from nodejs.org${NC}"
                exit 1
            fi
            ;;
        *)
            echo -e "${YELLOW}⚠️ Please install Node.js 20+ manually from nodejs.org${NC}"
            exit 1
            ;;
    esac
    
    echo -e "${GREEN}✅ Node.js installed: $(node --version)${NC}"
}

# Function to install Rust
install_rust() {
    echo -e "${BLUE}🦀 Installing Rust...${NC}"
    
    if command -v rustc >/dev/null 2>&1; then
        local rust_version=$(rustc --version | cut -d' ' -f2)
        echo -e "${GREEN}✅ Rust $rust_version already installed${NC}"
        return 0
    fi
    
    # Install Rust via rustup
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source "$HOME/.cargo/env"
    
    echo -e "${GREEN}✅ Rust installed: $(rustc --version)${NC}"
}

# Function to install Tauri CLI
install_tauri_cli() {
    echo -e "${BLUE}⚡ Installing Tauri CLI...${NC}"
    
    if command -v cargo >/dev/null 2>&1 && cargo tauri --version >/dev/null 2>&1; then
        local tauri_version=$(cargo tauri --version | cut -d' ' -f2)
        echo -e "${GREEN}✅ Tauri CLI $tauri_version already installed${NC}"
        return 0
    fi
    
    # Install Tauri CLI
    cargo install tauri-cli
    
    echo -e "${GREEN}✅ Tauri CLI installed: $(cargo tauri --version)${NC}"
}

# Function to setup desktop app project structure
setup_desktop_project() {
    echo -e "${BLUE}📁 Setting up desktop app project structure...${NC}"
    
    local desktop_dir="$UDOS_ROOT/uNETWORK/desktop"
    mkdir -p "$desktop_dir"
    
    # Create package.json for Tauri frontend dependencies
    cat > "$desktop_dir/package.json" << 'EOF'
{
  "name": "udos-desktop",
  "version": "1.0.4.1",
  "description": "uDOS Native Desktop Application",
  "main": "src/main.js",
  "scripts": {
    "dev": "cargo tauri dev",
    "build": "cargo tauri build",
    "setup": "npm install && cargo tauri info"
  },
  "dependencies": {
    "@tauri-apps/api": "^1.5.0"
  },
  "devDependencies": {
    "@tauri-apps/cli": "^1.5.0"
  }
}
EOF
    
    # Create basic Tauri configuration that connects to existing Flask backend
    mkdir -p "$desktop_dir/src-tauri"
    cat > "$desktop_dir/src-tauri/tauri.conf.json" << 'EOF'
{
  "build": {
    "beforeDevCommand": "echo 'Starting uDOS backend...' && cd ../../.. && ./uNETWORK/display/udos-display.sh export dashboard > /dev/null 2>&1 &",
    "beforeBuildCommand": "",
    "devPath": "http://localhost:8080",
    "distDir": "../dist"
  },
  "package": {
    "productName": "uDOS",
    "version": "1.0.4.1"
  },
  "tauri": {
    "allowlist": {
      "all": false,
      "shell": {
        "all": false,
        "open": true
      },
      "window": {
        "all": false,
        "close": true,
        "hide": true,
        "show": true,
        "maximize": true,
        "minimize": true,
        "unmaximize": true,
        "unminimize": true,
        "startDragging": true
      },
      "http": {
        "all": true,
        "request": true
      }
    },
    "bundle": {
      "active": true,
      "category": "DeveloperTool",
      "copyright": "",
      "deb": {
        "depends": []
      },
      "externalBin": [],
      "icon": [
        "icons/32x32.png",
        "icons/128x128.png",
        "icons/128x128@2x.png",
        "icons/icon.icns",
        "icons/icon.ico"
      ],
      "identifier": "dev.udos.desktop",
      "longDescription": "Universal Device Operating System - Native Desktop Application",
      "macOS": {
        "entitlements": null,
        "exceptionDomain": "",
        "frameworks": [],
        "providerShortName": null,
        "signingIdentity": null
      },
      "resources": [],
      "shortDescription": "uDOS Desktop",
      "targets": "all",
      "windows": {
        "certificateThumbprint": null,
        "digestAlgorithm": "sha256",
        "timestampUrl": ""
      }
    },
    "security": {
      "csp": null
    },
    "updater": {
      "active": false
    },
    "windows": [
      {
        "fullscreen": false,
        "height": 800,
        "resizable": true,
        "title": "uDOS - Universal Device Operating System",
        "width": 1200,
        "minWidth": 800,
        "minHeight": 600,
        "url": "http://localhost:8080"
      }
    ]
  }
}
EOF
    
    # Create Cargo.toml with HTTP dependencies for backend communication
    cat > "$desktop_dir/src-tauri/Cargo.toml" << 'EOF'
[package]
name = "udos-desktop"
version = "1.0.4.1"
description = "uDOS Native Desktop Application"
authors = ["uDOS Team"]
license = "MIT"
repository = "https://github.com/fredporter/uDOS"
edition = "2021"

[build-dependencies]
tauri-build = { version = "1.5", features = [] }

[dependencies]
tauri = { version = "1.5", features = ["shell-open", "window-close", "window-hide", "window-show", "window-maximize", "window-minimize", "window-unmaximize", "window-unminimize", "window-start-dragging"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
reqwest = { version = "0.11", features = ["json"] }
tokio = { version = "1.0", features = ["full"] }

[features]
default = ["custom-protocol"]
custom-protocol = ["tauri/custom-protocol"]
EOF
    
    # Create main Rust file that manages Python backend
    mkdir -p "$desktop_dir/src-tauri/src"
    cat > "$desktop_dir/src-tauri/src/main.rs" << 'EOF'
// uDOS Desktop Application - Native Tauri Implementation
// Integrates with existing Python Flask backend via uSCRIPT environment
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::Manager;
use std::process::{Command, Stdio};
use std::thread;
use std::time::Duration;

#[tauri::command]
fn get_udos_status() -> String {
    "uDOS Desktop v1.0.4.1 - Connected to Python Backend".to_string()
}

#[tauri::command]
async fn start_backend() -> Result<String, String> {
    // Start the Python Flask backend using existing uSCRIPT environment
    let output = Command::new("bash")
        .arg("-c")
        .arg("cd ../../../ && ./uNETWORK/display/udos-display.sh export dashboard")
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn();
    
    match output {
        Ok(_) => {
            // Give the server time to start
            thread::sleep(Duration::from_secs(2));
            Ok("Python backend started".to_string())
        },
        Err(e) => Err(format!("Failed to start backend: {}", e))
    }
}

#[tauri::command]
async fn check_backend_health() -> Result<String, String> {
    // Check if the Flask server is responding
    match reqwest::get("http://localhost:8080/api/status").await {
        Ok(response) => {
            if response.status().is_success() {
                Ok("Backend healthy".to_string())
            } else {
                Err("Backend not responding".to_string())
            }
        },
        Err(_) => Err("Backend unreachable".to_string())
    }
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            get_udos_status,
            start_backend,
            check_backend_health
        ])
        .setup(|app| {
            let window = app.get_window("main").unwrap();
            
            // Auto-start the Python backend in development
            #[cfg(debug_assertions)]
            {
                tauri::async_runtime::spawn(async {
                    thread::sleep(Duration::from_secs(1));
                    let _ = start_backend().await;
                });
                window.open_devtools();
            }
            
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
EOF
    
    echo -e "${GREEN}✅ Desktop app project structure created${NC}"
    echo -e "${BLUE}ℹ️  Desktop app will connect to existing Flask backend at http://localhost:8080${NC}"
}

# Function to create desktop development scripts
create_dev_scripts() {
    echo -e "${BLUE}📜 Creating development scripts...${NC}"
    
    local scripts_dir="$UDOS_ROOT/uNETWORK/desktop"
    
    # Create development launcher that integrates with uSCRIPT
    cat > "$scripts_dir/dev-desktop.sh" << 'EOF'
#!/bin/bash
# uDOS Desktop Development Launcher
echo "🏗️ Starting uDOS Desktop Development..."
echo "📡 This will start the Python backend and desktop app"

cd "$(dirname "$0")"

# Ensure Python backend dependencies are available
echo "🐍 Checking Python environment..."
if [ -d "../../uSCRIPT/venv" ]; then
    echo "✅ uSCRIPT virtual environment found"
else
    echo "⚠️  Setting up uSCRIPT environment first..."
    cd ../../uSCRIPT && ./setup-environment.sh && cd ../uNETWORK/desktop
fi

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
npm install

# Start development with integrated backend
echo "🚀 Starting Tauri development with Python backend..."
cargo tauri dev
EOF
    chmod +x "$scripts_dir/dev-desktop.sh"
    
    # Create build script
    cat > "$scripts_dir/build-desktop.sh" << 'EOF'
#!/bin/bash
# uDOS Desktop Build Script
echo "🔨 Building uDOS Desktop Application..."
cd "$(dirname "$0")"

# Ensure dependencies
npm install

# Build the desktop application
echo "🏗️ Building native desktop app..."
cargo tauri build

echo "✅ Desktop app built successfully!"
echo "📦 Binary location: src-tauri/target/release/"
echo ""
echo "🚀 To run the built app:"
case "$(uname -s)" in
    Darwin)
        echo "   open src-tauri/target/release/bundle/macos/uDOS.app"
        ;;
    Linux)
        echo "   ./src-tauri/target/release/udos-desktop"
        ;;
    *)
        echo "   Check src-tauri/target/release/ for executable"
        ;;
esac
EOF
    chmod +x "$scripts_dir/build-desktop.sh"
    
    echo -e "${GREEN}✅ Development scripts created${NC}"
}

# Main installation process
main() {
    echo -e "${YELLOW}This will install Node.js, Rust, and Tauri CLI for desktop development.${NC}"
    echo -e "${YELLOW}Continue? [y/N]:${NC} "
    read -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 0
    fi
    
    install_nodejs
    install_rust
    
    # Source Rust environment
    if [ -f "$HOME/.cargo/env" ]; then
        source "$HOME/.cargo/env"
    fi
    
    install_tauri_cli
    setup_desktop_project
    create_dev_scripts
    
    echo ""
    echo -e "${GREEN}🎉 Desktop development environment setup complete!${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "  1. Test installation: cd uNETWORK/desktop && ./dev-desktop.sh"
    echo "  2. Build desktop app: cd uNETWORK/desktop && ./build-desktop.sh"
    echo "  3. VS Code integration: Open uDOS workspace and use tasks"
    echo ""
    echo -e "${BLUE}Development commands:${NC}"
    echo "  • cargo tauri dev  - Start development server"
    echo "  • cargo tauri build - Build production app"
    echo "  • cargo tauri info  - Show environment info"
    echo ""
}

# Run main function
main "$@"

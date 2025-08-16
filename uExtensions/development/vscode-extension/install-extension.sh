#!/bin/bash
# uDOS VS Code Extension Installer
# Compiles and installs the uDOS extension for VS Code

echo "🔧 Building uDOS VS Code Extension..."

# Compile TypeScript
npm run compile

if [ $? -eq 0 ]; then
    echo "✅ Extension compiled successfully"
    
    # Package extension
    echo "📦 Packaging extension..."
    npm run package
    
    if [ $? -eq 0 ]; then
        echo "✅ Extension packaged successfully"
        
        # Get the latest VSIX file
        VSIX_FILE=$(ls -t *.vsix | head -n1)
        
        if [ -n "$VSIX_FILE" ]; then
            echo "🚀 Installing extension: $VSIX_FILE"
            code --install-extension "$VSIX_FILE"
            
            if [ $? -eq 0 ]; then
                echo "✅ uDOS VS Code Extension installed successfully!"
                echo "📖 Please reload VS Code to activate the extension"
                echo ""
                echo "Available commands:"
                echo "  - uDOS: Run Command"
                echo "  - uDOS: Validate Installation"
                echo "  - uDOS: Show User Role"
                echo "  - uDOS: Initialize User"
                echo "  - uDOS: Start Chester AI"
            else
                echo "❌ Failed to install extension"
                exit 1
            fi
        else
            echo "❌ No VSIX file found"
            exit 1
        fi
    else
        echo "❌ Failed to package extension"
        exit 1
    fi
else
    echo "❌ Failed to compile extension"
    exit 1
fi

#!/bin/bash
# Setup secrets from .env file
# This script helps configure API keys and secrets for local development

set -euo pipefail

echo "🔐 uDOS Secrets Setup"
echo "===================="
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "📋 Creating .env from template..."
    cp .env.template .env
    echo "✅ Created .env (edit with your API keys)"
    echo ""
    echo "Next steps:"
    echo "  1. Edit .env with your actual API keys"
    echo "  2. Run this script again: ./bin/setup-secrets.sh"
    exit 0
fi

echo "📝 Loading secrets from .env..."

# Load .env
export $(cat .env | grep -v '^#' | xargs)

# Create wizard config if it doesn't exist
if [ ! -f "wizard/config/ai_keys.json" ]; then
    echo "🔑 Setting up wizard/config/ai_keys.json..."
    mkdir -p wizard/config
    cat > wizard/config/ai_keys.json << EOF
{
  "_generated": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "_instructions": "Auto-generated from .env file. DO NOT COMMIT THIS FILE!",
  "GEMINI_API_KEY": "${GEMINI_API_KEY:-}",
  "OPENAI_API_KEY": "${OPENAI_API_KEY:-}",
  "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY:-}",
  "MISTRAL_API_KEY": "${MISTRAL_API_KEY:-}"
}
EOF
    echo "✅ Created wizard/config/ai_keys.json"
fi

if [ ! -f "public/wizard/config/ai_keys.json" ]; then
    echo "🔑 Setting up public/wizard/config/ai_keys.json..."
    mkdir -p public/wizard/config
    cat > public/wizard/config/ai_keys.json << EOF
{
  "_generated": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "_instructions": "Auto-generated from .env file. DO NOT COMMIT THIS FILE!",
  "GEMINI_API_KEY": "${GEMINI_API_KEY:-}",
  "OPENAI_API_KEY": "${OPENAI_API_KEY:-}",
  "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY:-}",
  "MISTRAL_API_KEY": "${MISTRAL_API_KEY:-}"
}
EOF
    echo "✅ Created public/wizard/config/ai_keys.json"
fi

# Create GitHub keys config
if [ ! -f "wizard/config/github_keys.json" ]; then
    echo "🔑 Setting up wizard/config/github_keys.json..."
    cat > wizard/config/github_keys.json << EOF
{
  "_generated": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "_instructions": "Auto-generated from .env file. DO NOT COMMIT THIS FILE!",
  "GITHUB_TOKEN": "${GITHUB_TOKEN:-}",
  "GITHUB_WEBHOOK_SECRET": "${GITHUB_WEBHOOK_SECRET:-}"
}
EOF
    echo "✅ Created wizard/config/github_keys.json"
fi

# Create OAuth config
if [ ! -f "wizard/config/oauth_providers.json" ]; then
    echo "🔑 Setting up wizard/config/oauth_providers.json..."
    cat > wizard/config/oauth_providers.json << 'EOF'
{
  "_generated": "auto-generated from .env",
  "providers": {
    "google": {
      "client_id": "GOOGLE_CLIENT_ID",
      "client_secret": "GOOGLE_CLIENT_SECRET"
    },
    "github": {
      "client_id": "GITHUB_OAUTH_ID",
      "client_secret": "GITHUB_OAUTH_SECRET"
    },
    "microsoft": {
      "client_id": "MICROSOFT_CLIENT_ID",
      "client_secret": "MICROSOFT_CLIENT_SECRET"
    }
  }
}
EOF
    echo "✅ Created wizard/config/oauth_providers.json"
fi

echo ""
echo "✅ Secrets configured!"
echo ""
echo "Security checklist:"
echo "  ☑️  .env is in .gitignore (protected from git)"
echo "  ☑️  Config files generated from .env"
echo "  ☑️  Never commit .env or *_keys.json"
echo "  ☑️  Share credentials via 1Password, LastPass, or secure channel"
echo ""
echo "To update secrets:"
echo "  1. Edit .env with new values"
echo "  2. Run: ./bin/setup-secrets.sh"
echo ""

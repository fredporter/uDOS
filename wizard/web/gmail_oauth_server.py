#!/usr/bin/env python3
"""
Gmail OAuth - Standalone Test Server

Minimal FastAPI server with just Gmail OAuth routes for testing.
Doesn't import full wizard/web/app.py to avoid dependencies.
"""

import sys
import os
from pathlib import Path

# Allow insecure HTTP for local OAuth testing
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import uvicorn

# Import Gmail OAuth routes
from wizard.web.gmail_fastapi_routes import gmail_router

# Create minimal app
app = FastAPI(title="uDOS Gmail OAuth Test")

# Session middleware (required for OAuth)
app.add_middleware(SessionMiddleware, secret_key="test-secret-key-change-in-production")

# Register Gmail OAuth routes
app.include_router(gmail_router)


# Root redirect
@app.get("/")
async def root():
    from fastapi.responses import RedirectResponse

    return RedirectResponse(url="/gmail/")


# Health check
@app.get("/health")
async def health():
    return {"status": "ok", "service": "gmail-oauth-test"}


if __name__ == "__main__":
    print("=" * 60)
    print("Gmail OAuth Test Server")
    print("=" * 60)
    print()
    print("📍 Gmail OAuth: http://127.0.0.1:8080/gmail/")
    print("🔐 Click 'Sign in with Google' button")
    print()
    print("Prerequisites:")
    print("  1. Download gmail_credentials.json from Google Cloud Console")
    print("  2. Save to: memory/bank/user/gmail_credentials.json")
    print("  3. Follow: wiki/Google-Cloud-Console-Setup.md")
    print()
    print("=" * 60)
    print()

    uvicorn.run(app, host="127.0.0.1", port=8080, log_level="info")

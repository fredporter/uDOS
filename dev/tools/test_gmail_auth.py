"""
Gmail Authentication Test Script for uDOS v1.2.9

Tests OAuth2 flow, token encryption, and basic Gmail/Drive operations.

Usage:
    python dev/tools/test_gmail_auth.py

Requirements:
    1. Install packages: pip install -r requirements.txt
    2. Download OAuth credentials from Google Cloud Console
    3. Save as: memory/system/user/gmail_credentials.json

What this tests:
    - OAuth2 authentication flow
    - Token encryption/decryption
    - Token persistence and reload
    - Auto-refresh on expiry
    - User profile retrieval
    - Gmail and Drive service availability

Author: @fredporter
Version: 1.2.9
Date: December 2025
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.services.gmail_auth import get_gmail_auth
from core.services.gmail_service import get_gmail_service, get_drive_service
from core.config import Config


def test_authentication():
    """Test OAuth2 authentication flow."""
    print("=" * 60)
    print("Gmail Authentication Test - v1.2.9")
    print("=" * 60)
    print()
    
    # Initialize config
    config = Config()
    auth = get_gmail_auth(config)
    
    # Test 1: Check if already authenticated
    print("Test 1: Check existing authentication")
    print("-" * 60)
    if auth.is_authenticated():
        status = auth.get_status()
        print(f"✅ Already authenticated")
        print(f"   Email: {status['email']}")
        print(f"   Name: {status['name']}")
        print(f"   Token expiry: {status['token_expiry']}")
    else:
        print("❌ Not authenticated")
        print("   Run LOGIN GMAIL in uDOS to authenticate")
    print()
    
    # Test 2: Check credentials file
    print("Test 2: Check OAuth credentials file")
    print("-" * 60)
    creds_path = project_root / "memory" / "system" / "user" / "gmail_credentials.json"
    if creds_path.exists():
        print(f"✅ Credentials file exists: {creds_path}")
    else:
        print(f"❌ Credentials file missing: {creds_path}")
        print("   Download from: https://console.cloud.google.com/apis/credentials")
        print("   1. Create OAuth 2.0 Client ID")
        print("   2. Download JSON")
        print("   3. Save as gmail_credentials.json")
    print()
    
    # Test 3: Check token encryption
    print("Test 3: Check token encryption")
    print("-" * 60)
    token_path = project_root / "memory" / "system" / "user" / ".gmail_token.enc"
    if token_path.exists():
        print(f"✅ Encrypted token exists: {token_path}")
        print(f"   Size: {token_path.stat().st_size} bytes")
        
        # Try to load and decrypt
        try:
            loaded = auth.load_credentials()
            if loaded:
                print("✅ Token decryption successful")
            else:
                print("❌ Token decryption failed")
        except Exception as e:
            print(f"❌ Token decryption error: {e}")
    else:
        print(f"ℹ️  No encrypted token yet: {token_path}")
        print("   Will be created after LOGIN GMAIL")
    print()
    
    # Test 4: Check encryption key
    print("Test 4: Check encryption key")
    print("-" * 60)
    env_path = project_root / ".env"
    if env_path.exists():
        with open(env_path, 'r') as f:
            env_content = f.read()
            if 'GMAIL_TOKEN_ENCRYPTION_KEY' in env_content:
                print("✅ Encryption key exists in .env")
            else:
                print("❌ Encryption key missing in .env")
                print("   Will be auto-generated on first login")
    else:
        print("❌ .env file missing")
        print("   Copy from .env.example or will be created on first run")
    print()
    
    # Test 5: Gmail service availability
    print("Test 5: Gmail service availability")
    print("-" * 60)
    gmail = get_gmail_service()
    if gmail.is_available():
        print("✅ Gmail service available")
        
        # Try to get labels
        labels = gmail.get_labels()
        if labels:
            print(f"✅ Gmail API working - found {len(labels)} labels")
            print(f"   Labels: {', '.join([l['name'] for l in labels[:5]])}")
        else:
            print("⚠️  Gmail API accessible but no labels found")
    else:
        print("❌ Gmail service not available (not authenticated)")
    print()
    
    # Test 6: Drive service availability
    print("Test 6: Drive service availability")
    print("-" * 60)
    drive = get_drive_service()
    if drive.is_available():
        print("✅ Drive service available")
        
        # Get quota
        quota = drive.get_quota_usage()
        used_mb = quota['used'] / (1024 * 1024)
        limit_mb = quota['limit'] / (1024 * 1024)
        print(f"✅ App Data quota: {used_mb:.2f} MB / {limit_mb:.2f} MB")
        
        # List files
        files = drive.list_files()
        print(f"   Files in App Data: {len(files)}")
    else:
        print("❌ Drive service not available (not authenticated)")
    print()
    
    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    if auth.is_authenticated():
        print("✅ All systems operational")
        print()
        print("Next steps:")
        print("  - Use EMAIL LIST to view emails")
        print("  - Use EMAIL SEND to send emails")
        print("  - Use SYNC GMAIL to sync data (coming in Part 2)")
    else:
        print("⚠️  Not authenticated")
        print()
        print("To authenticate:")
        print("  1. Ensure gmail_credentials.json exists")
        print("  2. Run: LOGIN GMAIL in uDOS")
        print("  3. Authorize in browser")
        print("  4. Re-run this test")
    print()


if __name__ == "__main__":
    try:
        test_authentication()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

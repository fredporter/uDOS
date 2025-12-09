"""
Gmail OAuth2 Authentication Service for uDOS v1.2.9

This module handles Gmail/Google authentication using OAuth2 flow.
Provides secure token management, auto-refresh, and user profile access.

OAuth Scopes Used:
- https://www.googleapis.com/auth/drive.appdata - App folder access only
- https://www.googleapis.com/auth/gmail.readonly - Read emails
- https://www.googleapis.com/auth/gmail.send - Send emails
- https://www.googleapis.com/auth/userinfo.email - User profile

Security:
- Tokens stored encrypted in .env
- Browser-based consent flow (user approval required)
- Auto-refresh on expiry
- Revocation support

Author: @fredporter
Version: 1.2.9
Date: December 2025
"""

import os
import json
import pickle
import base64
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from cryptography.fernet import Fernet

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GmailAuthService:
    """
    Gmail OAuth2 authentication and token management.

    Handles:
    - OAuth2 consent flow
    - Token storage and encryption
    - Auto-refresh on expiry
    - User profile retrieval
    - Token revocation
    """

    # OAuth scopes required for uDOS functionality
    SCOPES = [
        'https://www.googleapis.com/auth/drive.appdata',     # App folder only
        'https://www.googleapis.com/auth/gmail.readonly',    # Read emails
        'https://www.googleapis.com/auth/gmail.send',        # Send emails
        'https://www.googleapis.com/auth/userinfo.email'     # User info
    ]

    def __init__(self, config_manager=None):
        """
        Initialize Gmail authentication service.

        Args:
            config_manager: Optional uDOS Config instance for settings
        """
        self.config = config_manager
        self.credentials: Optional[Credentials] = None
        self.user_info: Optional[Dict[str, Any]] = None

        # Paths
        self.project_root = Path(__file__).parent.parent.parent
        self.token_path = self.project_root / "memory" / "system" / "user" / ".gmail_token.enc"
        self.credentials_path = self.project_root / "memory" / "system" / "user" / "gmail_credentials.json"

        # Ensure directories exist
        self.token_path.parent.mkdir(parents=True, exist_ok=True)

        # Encryption key (stored in .env or generated)
        self.encryption_key = self._get_or_create_encryption_key()

    def _get_or_create_encryption_key(self) -> bytes:
        """
        Get encryption key from .env or generate new one.

        Returns:
            Fernet encryption key (bytes)
        """
        env_path = self.project_root / ".env"
        key_name = "GMAIL_TOKEN_ENCRYPTION_KEY"

        # Try to load from .env
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith(key_name):
                        key_value = line.split('=', 1)[1].strip()
                        return key_value.encode()

        # Generate new key
        key = Fernet.generate_key()

        # Save to .env
        with open(env_path, 'a') as f:
            f.write(f"\n# Gmail token encryption key (auto-generated)\n")
            f.write(f"{key_name}={key.decode()}\n")

        return key

    def _encrypt_token(self, token_data: dict) -> bytes:
        """
        Encrypt token data using Fernet.

        Args:
            token_data: Dictionary containing token information

        Returns:
            Encrypted bytes
        """
        fernet = Fernet(self.encryption_key)
        token_json = json.dumps(token_data)
        return fernet.encrypt(token_json.encode())

    def _decrypt_token(self, encrypted_data: bytes) -> dict:
        """
        Decrypt token data.

        Args:
            encrypted_data: Encrypted token bytes

        Returns:
            Decrypted token dictionary
        """
        fernet = Fernet(self.encryption_key)
        decrypted = fernet.decrypt(encrypted_data)
        return json.loads(decrypted.decode())

    def is_authenticated(self) -> bool:
        """
        Check if user is currently authenticated.

        Returns:
            True if valid credentials exist, False otherwise
        """
        if self.credentials and self.credentials.valid:
            return True

        # Try to load and refresh
        if self.load_credentials():
            if self.credentials.valid:
                return True
            elif self.credentials.expired and self.credentials.refresh_token:
                try:
                    self.credentials.refresh(Request())
                    self.save_credentials()
                    return True
                except Exception:
                    return False

        return False

    def login(self, auth_port: int = 8080) -> Dict[str, Any]:
        """
        Start OAuth2 login flow.

        Opens browser for user consent, retrieves tokens,
        saves encrypted credentials.

        Returns:
            Dictionary with status and user info:
            {
                'success': True/False,
                'email': 'user@gmail.com',
                'name': 'User Name',
                'message': 'Login successful'
            }
        """
        try:
            # Check if already authenticated
            if self.is_authenticated():
                self._load_user_info()
                return {
                    'success': True,
                    'email': self.user_info.get('email', 'Unknown'),
                    'name': self.user_info.get('name', 'Unknown'),
                    'message': 'Already authenticated'
                }

            # Check for credentials file
            if not self.credentials_path.exists():
                return {
                    'success': False,
                    'message': f'Credentials file not found: {self.credentials_path}\n'
                              f'Please download OAuth credentials from Google Cloud Console.'
                }

            # Start OAuth flow
            flow = InstalledAppFlow.from_client_secrets_file(
                str(self.credentials_path),
                self.SCOPES
            )

            # Run local server for callback (opens browser)
            self.credentials = flow.run_local_server(
                port=auth_port,
                prompt='consent',
                success_message='Authentication successful! You can close this window.'
            )

            # Save encrypted credentials
            self.save_credentials()

            # Load user info
            self._load_user_info()

            return {
                'success': True,
                'email': self.user_info.get('email', 'Unknown'),
                'name': self.user_info.get('name', 'Unknown'),
                'message': 'Login successful'
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Login failed: {str(e)}'
            }

    def logout(self) -> Dict[str, str]:
        """
        Revoke tokens and clear credentials.

        Returns:
            Dictionary with status message
        """
        try:
            # Revoke token with Google
            if self.credentials and self.credentials.valid:
                try:
                    self.credentials.revoke(Request())
                except Exception:
                    pass  # Continue even if revoke fails

            # Delete encrypted token file
            if self.token_path.exists():
                self.token_path.unlink()

            # Clear in-memory credentials
            self.credentials = None
            self.user_info = None

            return {
                'success': True,
                'message': 'Logged out successfully'
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Logout failed: {str(e)}'
            }

    def save_credentials(self) -> bool:
        """
        Save credentials to encrypted file.

        Returns:
            True if saved successfully, False otherwise
        """
        if not self.credentials:
            return False

        try:
            # Convert credentials to dict
            creds_dict = {
                'token': self.credentials.token,
                'refresh_token': self.credentials.refresh_token,
                'token_uri': self.credentials.token_uri,
                'client_id': self.credentials.client_id,
                'client_secret': self.credentials.client_secret,
                'scopes': self.credentials.scopes,
                'expiry': self.credentials.expiry.isoformat() if self.credentials.expiry else None
            }

            # Encrypt and save
            encrypted = self._encrypt_token(creds_dict)
            self.token_path.write_bytes(encrypted)

            return True

        except Exception as e:
            print(f"Error saving credentials: {e}")
            return False

    def load_credentials(self) -> bool:
        """
        Load credentials from encrypted file.

        Returns:
            True if loaded successfully, False otherwise
        """
        if not self.token_path.exists():
            return False

        try:
            # Read and decrypt
            encrypted = self.token_path.read_bytes()
            creds_dict = self._decrypt_token(encrypted)

            # Convert dict to Credentials object
            self.credentials = Credentials(
                token=creds_dict.get('token'),
                refresh_token=creds_dict.get('refresh_token'),
                token_uri=creds_dict.get('token_uri'),
                client_id=creds_dict.get('client_id'),
                client_secret=creds_dict.get('client_secret'),
                scopes=creds_dict.get('scopes')
            )

            # Set expiry if present
            if creds_dict.get('expiry'):
                self.credentials.expiry = datetime.fromisoformat(creds_dict['expiry'])

            return True

        except Exception as e:
            print(f"Error loading credentials: {e}")
            return False

    def _load_user_info(self) -> None:
        """
        Load user profile information from Google.

        Updates self.user_info with email, name, etc.
        """
        if not self.credentials or not self.credentials.valid:
            return

        try:
            # Build People API service
            service = build('people', 'v1', credentials=self.credentials)

            # Get user profile
            profile = service.people().get(
                resourceName='people/me',
                personFields='names,emailAddresses'
            ).execute()

            # Extract info
            self.user_info = {
                'email': profile.get('emailAddresses', [{}])[0].get('value', 'Unknown'),
                'name': profile.get('names', [{}])[0].get('displayName', 'Unknown'),
                'id': profile.get('resourceName', '').replace('people/', '')
            }

        except Exception as e:
            print(f"Error loading user info: {e}")
            self.user_info = {
                'email': 'Unknown',
                'name': 'Unknown',
                'id': 'Unknown'
            }

    def get_status(self) -> Dict[str, Any]:
        """
        Get current authentication status.

        Returns:
            Dictionary with auth status, user info, token expiry
        """
        status = {
            'authenticated': False,
            'email': None,
            'name': None,
            'token_expiry': None,
            'scopes': self.SCOPES
        }

        if self.is_authenticated():
            if not self.user_info:
                self._load_user_info()

            status.update({
                'authenticated': True,
                'email': self.user_info.get('email', 'Unknown'),
                'name': self.user_info.get('name', 'Unknown'),
                'token_expiry': self.credentials.expiry.isoformat() if self.credentials.expiry else None
            })

        return status

    def get_credentials(self) -> Optional[Credentials]:
        """
        Get current credentials for API calls.

        Auto-refreshes if expired.

        Returns:
            Google Credentials object or None
        """
        if not self.is_authenticated():
            return None

        # Auto-refresh if needed
        if self.credentials.expired and self.credentials.refresh_token:
            try:
                self.credentials.refresh(Request())
                self.save_credentials()
            except Exception:
                return None

        return self.credentials


# Singleton instance
_gmail_auth_instance = None

def get_gmail_auth(config_manager=None) -> GmailAuthService:
    """
    Get singleton Gmail auth service instance.

    Args:
        config_manager: Optional Config instance

    Returns:
        GmailAuthService instance
    """
    global _gmail_auth_instance
    if _gmail_auth_instance is None:
        _gmail_auth_instance = GmailAuthService(config_manager)
    return _gmail_auth_instance

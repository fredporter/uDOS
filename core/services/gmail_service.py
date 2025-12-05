"""
Gmail API Service for uDOS v1.2.9

Provides Gmail and Google Drive API integration for:
- Reading emails and converting to tasks/notes
- Sending emails from uDOS
- Syncing data to Google Drive App Data folder
- Email search and filtering

Requires authentication via gmail_auth.py.

Author: @fredporter
Version: 1.2.9
Date: December 2025
"""

import os
import json
import base64
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io

from core.services.gmail_auth import get_gmail_auth


class GmailService:
    """
    Gmail API wrapper for uDOS.

    Handles:
    - Email retrieval and search
    - Email sending
    - Label management
    - Attachment handling
    """

    def __init__(self):
        """Initialize Gmail service."""
        self.auth = get_gmail_auth()
        self._service = None

    @property
    def service(self):
        """
        Lazy-load Gmail API service.

        Returns:
            Gmail API service or None if not authenticated
        """
        if self._service is None:
            creds = self.auth.get_credentials()
            if creds:
                self._service = build('gmail', 'v1', credentials=creds)
        return self._service

    def is_available(self) -> bool:
        """Check if Gmail service is available (authenticated)."""
        return self.service is not None

    def get_messages(self, query: str = "", max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search and retrieve emails.

        Args:
            query: Gmail search query (e.g., "is:unread from:boss@company.com")
            max_results: Maximum number of messages to return

        Returns:
            List of message dictionaries with id, subject, from, date, body
        """
        if not self.is_available():
            return []

        try:
            # Search for messages
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()

            messages = results.get('messages', [])

            # Get full message details
            full_messages = []
            for msg in messages:
                msg_id = msg['id']
                message = self.service.users().messages().get(
                    userId='me',
                    id=msg_id,
                    format='full'
                ).execute()

                parsed = self._parse_message(message)
                full_messages.append(parsed)

            return full_messages

        except HttpError as e:
            print(f"Error retrieving messages: {e}")
            return []

    def _parse_message(self, message: dict) -> Dict[str, Any]:
        """
        Parse Gmail message into simplified format.

        Args:
            message: Raw Gmail API message object

        Returns:
            Dictionary with id, subject, from, to, date, body, labels
        """
        headers = message.get('payload', {}).get('headers', [])

        # Extract headers
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        from_addr = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
        to_addr = next((h['value'] for h in headers if h['name'] == 'To'), 'Unknown')
        date_str = next((h['value'] for h in headers if h['name'] == 'Date'), '')

        # Extract body
        body = self._extract_body(message.get('payload', {}))

        # Labels
        labels = message.get('labelIds', [])

        return {
            'id': message['id'],
            'thread_id': message.get('threadId'),
            'subject': subject,
            'from': from_addr,
            'to': to_addr,
            'date': date_str,
            'body': body,
            'labels': labels,
            'snippet': message.get('snippet', '')
        }

    def _extract_body(self, payload: dict) -> str:
        """
        Extract email body from message payload.

        Args:
            payload: Message payload from Gmail API

        Returns:
            Decoded email body text
        """
        body = ""

        if 'parts' in payload:
            # Multipart message
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part.get('body', {}).get('data', '')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
                        break
        else:
            # Simple message
            data = payload.get('body', {}).get('data', '')
            if data:
                body = base64.urlsafe_b64decode(data).decode('utf-8')

        return body

    def send_message(self, to: str, subject: str, body: str,
                     cc: Optional[str] = None,
                     bcc: Optional[str] = None) -> Dict[str, Any]:
        """
        Send an email.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            cc: Optional CC address
            bcc: Optional BCC address

        Returns:
            Dictionary with success status and message ID
        """
        if not self.is_available():
            return {'success': False, 'error': 'Not authenticated'}

        try:
            # Create message
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject

            if cc:
                message['cc'] = cc
            if bcc:
                message['bcc'] = bcc

            # Encode message
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

            # Send
            result = self.service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()

            return {
                'success': True,
                'message_id': result['id'],
                'thread_id': result.get('threadId')
            }

        except HttpError as e:
            return {
                'success': False,
                'error': str(e)
            }

    def mark_as_read(self, message_id: str) -> bool:
        """
        Mark a message as read.

        Args:
            message_id: Gmail message ID

        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            return False

        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
        except HttpError:
            return False

    def get_labels(self) -> List[Dict[str, str]]:
        """
        Get all Gmail labels.

        Returns:
            List of label dictionaries with id and name
        """
        if not self.is_available():
            return []

        try:
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            return [{'id': l['id'], 'name': l['name']} for l in labels]
        except HttpError:
            return []


class DriveService:
    """
    Google Drive API wrapper for uDOS.

    Handles:
    - App Data folder access (15MB quota)
    - File upload/download
    - Sync operations
    - Conflict resolution
    """

    # App Data folder (not visible to user, 15MB quota)
    APP_DATA_SPACE = 'appDataFolder'

    def __init__(self):
        """Initialize Drive service."""
        self.auth = get_gmail_auth()
        self._service = None

    @property
    def service(self):
        """
        Lazy-load Drive API service.

        Returns:
            Drive API service or None if not authenticated
        """
        if self._service is None:
            creds = self.auth.get_credentials()
            if creds:
                self._service = build('drive', 'v3', credentials=creds)
        return self._service

    def is_available(self) -> bool:
        """Check if Drive service is available (authenticated)."""
        return self.service is not None

    def upload_file(self, file_path: Path, cloud_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Upload file to App Data folder.

        Args:
            file_path: Local file path
            cloud_name: Optional name for cloud file (defaults to basename)

        Returns:
            Dictionary with success status, file_id, and metadata
        """
        if not self.is_available():
            return {'success': False, 'error': 'Not authenticated'}

        if not file_path.exists():
            return {'success': False, 'error': 'File not found'}

        try:
            # File metadata
            file_metadata = {
                'name': cloud_name or file_path.name,
                'parents': [self.APP_DATA_SPACE]
            }

            # Media upload
            media = MediaFileUpload(str(file_path), resumable=True)

            # Upload
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,size,modifiedTime'
            ).execute()

            return {
                'success': True,
                'file_id': file['id'],
                'name': file['name'],
                'size': file.get('size', 0),
                'modified': file.get('modifiedTime')
            }

        except HttpError as e:
            return {'success': False, 'error': str(e)}

    def download_file(self, file_id: str, local_path: Path) -> bool:
        """
        Download file from App Data folder.

        Args:
            file_id: Google Drive file ID
            local_path: Local destination path

        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            return False

        try:
            # Request file download
            request = self.service.files().get_media(fileId=file_id)

            # Download to local file
            fh = io.FileIO(str(local_path), 'wb')
            downloader = MediaIoBaseDownload(fh, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()

            fh.close()
            return True

        except HttpError:
            return False

    def list_files(self, name_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List files in App Data folder.

        Args:
            name_filter: Optional name filter (substring match)

        Returns:
            List of file dictionaries with id, name, size, modified
        """
        if not self.is_available():
            return []

        try:
            # Query for files in appDataFolder
            query = f"'{self.APP_DATA_SPACE}' in parents"
            if name_filter:
                query += f" and name contains '{name_filter}'"

            results = self.service.files().list(
                spaces=self.APP_DATA_SPACE,
                q=query,
                fields='files(id, name, size, modifiedTime, md5Checksum)'
            ).execute()

            files = results.get('files', [])
            return files

        except HttpError:
            return []

    def delete_file(self, file_id: str) -> bool:
        """
        Delete file from App Data folder.

        Args:
            file_id: Google Drive file ID

        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            return False

        try:
            self.service.files().delete(fileId=file_id).execute()
            return True
        except HttpError:
            return False

    def get_quota_usage(self) -> Dict[str, Any]:
        """
        Get App Data folder quota usage.

        Returns:
            Dictionary with used, limit, available (in bytes)
        """
        if not self.is_available():
            return {'used': 0, 'limit': 15 * 1024 * 1024, 'available': 15 * 1024 * 1024}

        try:
            about = self.service.about().get(fields='storageQuota').execute()
            quota = about.get('storageQuota', {})

            # App Data has separate 15MB limit
            app_data_limit = 15 * 1024 * 1024  # 15MB in bytes

            return {
                'used': int(quota.get('usageInDrive', 0)),
                'limit': app_data_limit,
                'available': app_data_limit - int(quota.get('usageInDrive', 0))
            }

        except HttpError:
            return {'used': 0, 'limit': 15 * 1024 * 1024, 'available': 15 * 1024 * 1024}


# Singleton instances
_gmail_service_instance = None
_drive_service_instance = None

def get_gmail_service() -> GmailService:
    """Get singleton Gmail service instance."""
    global _gmail_service_instance
    if _gmail_service_instance is None:
        _gmail_service_instance = GmailService()
    return _gmail_service_instance

def get_drive_service() -> DriveService:
    """Get singleton Drive service instance."""
    global _drive_service_instance
    if _drive_service_instance is None:
        _drive_service_instance = DriveService()
    return _drive_service_instance

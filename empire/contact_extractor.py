"""
Contact Extractor - Extract business/person contacts from emails

Parses Gmail messages to identify:
- Sender information (name, email, domain)
- Email signatures (company, title, phone)
- Business entities from domain names
- Person entities from senders

Filters out system/automated emails (noreply@, notifications, etc.)
Generates biz-*/prs-*/msg-* IDs and stores in contacts.db
"""

import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from .marketing_db import MarketingDB
from .entity_resolver import EntityResolver
from .id_generator import generate_message_id


class ContactExtractor:
    """Extract contacts from Gmail messages."""
    
    # System email patterns to filter out
    SYSTEM_EMAIL_PATTERNS = [
        r'^noreply@',
        r'^no-reply@',
        r'^donotreply@',
        r'^do-not-reply@',
        r'^notification',
        r'^notifications@',
        r'^automated@',
        r'^system@',
        r'^mailer-daemon@',
        r'^postmaster@',
        r'^bounce',
        r'^unsubscribe@',
        r'^support@.*\.(zendesk|freshdesk|intercom)',
        r'^.*@mail\.(google|yahoo|outlook|microsoft)\.com$',
    ]
    
    # Common signature markers
    SIGNATURE_MARKERS = [
        '---',
        '___',
        'Sent from',
        'Get Outlook',
        'Sent via',
        'Best regards',
        'Kind regards',
        'Sincerely',
        'Thanks',
        'Cheers',
        'Regards',
    ]
    
    def __init__(self, db: MarketingDB):
        """Initialize contact extractor.
        
        Args:
            db: MarketingDB instance
        """
        self.db = db
        self.resolver = EntityResolver(db)
    
    def is_system_email(self, email: str) -> bool:
        """Check if email is from system/automated sender.
        
        Args:
            email: Email address
        
        Returns:
            bool: True if system email, False otherwise
        """
        email_lower = email.lower()
        
        for pattern in self.SYSTEM_EMAIL_PATTERNS:
            if re.search(pattern, email_lower):
                return True
        
        return False
    
    def extract_from_email(self, gmail_message: Dict) -> Optional[str]:
        """Extract contacts from Gmail message.
        
        Args:
            gmail_message: Gmail message dict with:
                - id: Gmail message ID
                - threadId: Thread ID
                - payload: Message payload
                - internalDate: Timestamp (milliseconds)
        
        Returns:
            message_id if processed, None if filtered
        """
        # Extract headers
        headers = self._extract_headers(gmail_message)
        
        sender_email = headers.get('from_email', '')
        sender_name = headers.get('from_name', '')
        subject = headers.get('subject', '')
        
        # Filter system emails
        if self.is_system_email(sender_email):
            return None
        
        # Extract message body
        body = self._extract_body(gmail_message)
        snippet = gmail_message.get('snippet', '')
        
        # Parse signature
        signature_data = self._parse_signature(body)
        
        # Extract sender domain
        email_domain = self._extract_domain(sender_email)
        
        # Resolve or create person
        person_data = {
            'full_name': sender_name or sender_email.split('@')[0],
            'primary_email': sender_email,
            'source': 'gmail'
        }
        
        # Add signature data if found
        if signature_data.get('title'):
            person_data['job_title'] = signature_data['title']
        if signature_data.get('phone'):
            person_data['phone'] = signature_data['phone']
        if signature_data.get('company'):
            person_data['company_name'] = signature_data['company']
        
        person_id = self.resolver.resolve_or_create_person(**person_data)
        
        # Resolve or create business (aggressive - from email domain)
        business_id = None
        if email_domain and not self._is_generic_domain(email_domain):
            business_data = {
                'name': signature_data.get('company') or self._domain_to_business_name(email_domain),
                'website_domain': email_domain,
                'source': 'gmail_domain'
            }
            
            # Add signature contact info
            if signature_data.get('phone'):
                business_data['phone'] = signature_data['phone']
            if signature_data.get('website'):
                business_data['website'] = signature_data['website']
            
            business_id = self.resolver.resolve_or_create_business(**business_data)
        
        # Create message record
        message_id = generate_message_id()
        sent_at = self._parse_timestamp(gmail_message.get('internalDate'))
        
        self.db.create_message(
            message_id=message_id,
            gmail_message_id=gmail_message['id'],
            thread_id=gmail_message['threadId'],
            sender_email=sender_email,
            sender_name=sender_name,
            subject=subject,
            snippet=snippet[:500],  # Truncate to 500 chars
            sent_at=sent_at,
            person_id=person_id,
            business_id=business_id
        )
        
        return message_id
    
    def _extract_headers(self, gmail_message: Dict) -> Dict[str, str]:
        """Extract key headers from Gmail message.
        
        Args:
            gmail_message: Gmail message dict
        
        Returns:
            Dict with from_email, from_name, subject
        """
        headers = {}
        payload = gmail_message.get('payload', {})
        
        for header in payload.get('headers', []):
            name = header['name'].lower()
            value = header['value']
            
            if name == 'from':
                # Parse "Name <email@domain.com>" format
                match = re.match(r'^(.+?)\s*<(.+?)>$', value)
                if match:
                    headers['from_name'] = match.group(1).strip('"')
                    headers['from_email'] = match.group(2).strip()
                else:
                    headers['from_email'] = value.strip()
                    headers['from_name'] = ''
            
            elif name == 'subject':
                headers['subject'] = value
        
        return headers
    
    def _extract_body(self, gmail_message: Dict) -> str:
        """Extract message body text.
        
        Args:
            gmail_message: Gmail message dict
        
        Returns:
            Body text (plain text preferred)
        """
        import base64
        
        payload = gmail_message.get('payload', {})
        
        # Try to get plain text part
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data', '')
                    if data:
                        return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        
        # Fallback to body data
        if 'body' in payload and 'data' in payload['body']:
            data = payload['body']['data']
            return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        
        return ''
    
    def _parse_signature(self, body: str) -> Dict[str, str]:
        """Parse email signature for contact details.
        
        Args:
            body: Email body text
        
        Returns:
            Dict with company, title, phone, website
        """
        signature_data = {}
        
        # Find signature start
        signature_start = -1
        for marker in self.SIGNATURE_MARKERS:
            idx = body.find(marker)
            if idx != -1 and (signature_start == -1 or idx < signature_start):
                signature_start = idx
        
        if signature_start == -1:
            # Take last 500 chars as potential signature
            signature = body[-500:]
        else:
            signature = body[signature_start:]
        
        # Extract phone number
        phone_pattern = r'\b(?:\+?1[-.\s]?)?\(?([2-9][0-9]{2})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b'
        phone_match = re.search(phone_pattern, signature)
        if phone_match:
            signature_data['phone'] = ''.join(phone_match.groups())
        
        # Extract website
        url_pattern = r'https?://(?:www\.)?([a-zA-Z0-9-]+\.[a-zA-Z]{2,})'
        url_match = re.search(url_pattern, signature)
        if url_match:
            signature_data['website'] = url_match.group(0)
        
        # Extract job title (common patterns)
        title_patterns = [
            r'\b(CEO|CTO|CFO|COO|President|Director|Manager|Coordinator|Specialist|Engineer|Developer|Designer)\b',
            r'\b(Senior|Junior|Lead|Principal|Chief)\s+\w+',
        ]
        for pattern in title_patterns:
            title_match = re.search(pattern, signature, re.IGNORECASE)
            if title_match:
                signature_data['title'] = title_match.group(0)
                break
        
        # Extract company name (line before phone/website, or after title)
        lines = [line.strip() for line in signature.split('\n') if line.strip()]
        for i, line in enumerate(lines):
            if len(line) < 50 and any(char.isupper() for char in line):
                # Likely company name (capitalized, short line)
                if not any(marker in line for marker in self.SIGNATURE_MARKERS):
                    signature_data['company'] = line
                    break
        
        return signature_data
    
    def _extract_domain(self, email: str) -> str:
        """Extract domain from email address.
        
        Args:
            email: Email address
        
        Returns:
            Domain (lowercase)
        """
        if '@' in email:
            return email.split('@')[1].lower()
        return ''
    
    def _is_generic_domain(self, domain: str) -> bool:
        """Check if domain is generic (Gmail, Yahoo, etc.).
        
        Args:
            domain: Domain name
        
        Returns:
            bool: True if generic, False otherwise
        """
        generic_domains = [
            'gmail.com', 'googlemail.com', 'yahoo.com', 'yahoo.co.uk',
            'hotmail.com', 'outlook.com', 'live.com', 'msn.com',
            'aol.com', 'icloud.com', 'me.com', 'mac.com',
            'protonmail.com', 'proton.me', 'mail.com'
        ]
        return domain in generic_domains
    
    def _domain_to_business_name(self, domain: str) -> str:
        """Convert domain to business name.
        
        Args:
            domain: Domain name (e.g., 'acmecorp.com')
        
        Returns:
            Business name (e.g., 'Acme Corp')
        """
        # Remove TLD
        name = domain.split('.')[0]
        
        # Split on hyphens/underscores
        parts = re.split(r'[-_]', name)
        
        # Capitalize each part
        return ' '.join(part.capitalize() for part in parts)
    
    def _parse_timestamp(self, internal_date: str) -> str:
        """Parse Gmail internal date to ISO timestamp.
        
        Args:
            internal_date: Milliseconds since epoch (string)
        
        Returns:
            ISO timestamp
        """
        if not internal_date:
            return datetime.utcnow().isoformat()
        
        timestamp_ms = int(internal_date)
        timestamp_s = timestamp_ms / 1000.0
        dt = datetime.utcfromtimestamp(timestamp_s)
        return dt.isoformat()

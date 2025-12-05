"""
Email Parser for uDOS v1.2.9

Parses Gmail emails into structured data for conversion to tasks, notes, and missions.
Handles HTML and plain text emails, extracts metadata, and identifies actionable items.

Features:
- HTML email parsing (BeautifulSoup)
- Plain text email parsing
- Metadata extraction (from, to, date, subject)
- Task/action item detection
- URL extraction
- Attachment metadata
- Thread/conversation tracking

Author: @fredporter
Version: 1.2.9
Date: December 2025
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser


class EmailParser:
    """
    Parse and extract structured data from Gmail emails.

    Handles:
    - HTML and plain text emails
    - Metadata extraction
    - Task/action item detection
    - Content cleaning and normalization
    """

    # Task indicator patterns
    TASK_PATTERNS = [
        r'(?i)^[-*•]\s+(.+)$',  # Bullet points
        r'(?i)^(\d+[\.)]\s+.+)$',  # Numbered lists
        r'(?i)^(TODO|TASK|ACTION|DO):\s*(.+)$',  # Explicit task markers
        r'(?i)(please|could you|can you|need to|should|must)\s+(.+)',  # Action verbs
        r'(?i)^☐\s+(.+)$',  # Checkbox
    ]

    # Date patterns for deadlines
    DATE_PATTERNS = [
        r'(?i)by\s+(\w+\s+\d+)',  # "by Friday", "by Dec 15"
        r'(?i)due\s+(\w+\s+\d+)',  # "due Monday"
        r'(?i)deadline[:\s]+(\w+\s+\d+)',  # "deadline: tomorrow"
        r'(?i)before\s+(\w+\s+\d+)',  # "before next week"
    ]

    # Priority indicators
    PRIORITY_PATTERNS = [
        (r'(?i)(urgent|critical|asap|emergency|!!+)', 'high'),
        (r'(?i)(important|priority|high)', 'high'),
        (r'(?i)(low priority|when you can|eventually)', 'low'),
    ]

    def __init__(self):
        """Initialize email parser."""
        pass

    def parse_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse email data into structured format.

        Args:
            email_data: Raw email data from GmailService

        Returns:
            Parsed email dictionary with structured content
        """
        # Extract metadata
        metadata = self._extract_metadata(email_data)

        # Parse body content
        body_html = email_data.get('body_html', '')
        body_plain = email_data.get('body', '')

        if body_html:
            content = self._parse_html_body(body_html)
        else:
            content = self._parse_plain_body(body_plain)

        # Extract tasks and action items
        tasks = self._extract_tasks(content)

        # Extract URLs
        urls = self._extract_urls(content)

        # Detect priority
        priority = self._detect_priority(email_data.get('subject', '') + ' ' + content)

        # Extract deadline
        deadline = self._extract_deadline(content)

        return {
            'metadata': metadata,
            'content': content,
            'tasks': tasks,
            'urls': urls,
            'priority': priority,
            'deadline': deadline,
            'raw': email_data
        }

    def _extract_metadata(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract email metadata.

        Args:
            email_data: Raw email data

        Returns:
            Metadata dictionary
        """
        # Parse date
        date_str = email_data.get('date', '')
        try:
            date_parsed = parsedate_to_datetime(date_str)
        except Exception:
            date_parsed = None

        return {
            'message_id': email_data.get('id'),
            'thread_id': email_data.get('thread_id'),
            'subject': email_data.get('subject', 'No Subject'),
            'from': self._parse_email_address(email_data.get('from', '')),
            'to': self._parse_email_address(email_data.get('to', '')),
            'date': date_parsed.isoformat() if date_parsed else date_str,
            'labels': email_data.get('labels', []),
            'snippet': email_data.get('snippet', '')
        }

    def _parse_email_address(self, addr: str) -> Dict[str, str]:
        """
        Parse email address into name and email.

        Args:
            addr: Email address string (e.g., "John Doe <john@example.com>")

        Returns:
            Dictionary with name and email
        """
        # Match "Name <email>" format
        match = re.match(r'^(.*?)\s*<(.+?)>$', addr)
        if match:
            return {
                'name': match.group(1).strip().strip('"'),
                'email': match.group(2).strip()
            }

        # Just an email
        return {
            'name': '',
            'email': addr.strip()
        }

    def _parse_html_body(self, html: str) -> str:
        """
        Parse HTML email body to plain text.

        Args:
            html: HTML email body

        Returns:
            Plain text content
        """
        # Simple HTML to text conversion
        # Remove script and style elements
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)

        # Convert line breaks
        html = re.sub(r'<br\s*/?>', '\n', html, flags=re.IGNORECASE)
        html = re.sub(r'</p>', '\n\n', html, flags=re.IGNORECASE)
        html = re.sub(r'</div>', '\n', html, flags=re.IGNORECASE)
        html = re.sub(r'</li>', '\n', html, flags=re.IGNORECASE)

        # Remove remaining HTML tags
        text = re.sub(r'<[^>]+>', '', html)

        # Clean up whitespace
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        text = text.strip()

        return text

    def _parse_plain_body(self, text: str) -> str:
        """
        Parse plain text email body.

        Args:
            text: Plain text email body

        Returns:
            Cleaned plain text content
        """
        # Remove quoted text (lines starting with >)
        lines = text.split('\n')
        cleaned_lines = []

        in_quote = False
        for line in lines:
            stripped = line.strip()

            # Detect quote block
            if stripped.startswith('>'):
                in_quote = True
                continue

            # Detect forwarded message headers
            if re.match(r'^(On .+ wrote:|From:|Sent:|To:|Subject:)', stripped):
                in_quote = True
                continue

            # Reset quote if we hit a blank line
            if not stripped:
                in_quote = False

            if not in_quote:
                cleaned_lines.append(line)

        text = '\n'.join(cleaned_lines)

        # Clean up excessive whitespace
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        text = text.strip()

        return text

    def _extract_tasks(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract task/action items from email content.

        Args:
            content: Email body text

        Returns:
            List of task dictionaries
        """
        tasks = []
        lines = content.split('\n')

        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if not line_stripped:
                continue

            # Check each task pattern
            for pattern in self.TASK_PATTERNS:
                match = re.search(pattern, line_stripped)
                if match:
                    # Extract task text (use last group)
                    task_text = match.group(match.lastindex) if match.lastindex else match.group(0)
                    task_text = task_text.strip()

                    # Skip if too short or looks like noise
                    if len(task_text) < 5:
                        continue

                    # Extract deadline from task or next line
                    deadline = self._extract_deadline(task_text)
                    if not deadline and i + 1 < len(lines):
                        deadline = self._extract_deadline(lines[i + 1])

                    tasks.append({
                        'text': task_text,
                        'deadline': deadline,
                        'line_number': i + 1,
                        'completed': False
                    })
                    break

        return tasks

    def _extract_urls(self, content: str) -> List[str]:
        """
        Extract URLs from email content.

        Args:
            content: Email body text

        Returns:
            List of URLs
        """
        url_pattern = r'https?://[^\s<>"\')]+[^\s<>"\'.,;!?)]'
        urls = re.findall(url_pattern, content)

        # Remove duplicates while preserving order
        seen = set()
        unique_urls = []
        for url in urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)

        return unique_urls

    def _detect_priority(self, text: str) -> str:
        """
        Detect email priority from text.

        Args:
            text: Email subject + body

        Returns:
            Priority level: 'high', 'medium', 'low'
        """
        text_lower = text.lower()

        for pattern, priority in self.PRIORITY_PATTERNS:
            if re.search(pattern, text_lower):
                return priority

        return 'medium'

    def _extract_deadline(self, text: str) -> Optional[str]:
        """
        Extract deadline from text.

        Args:
            text: Text to search for deadlines

        Returns:
            Deadline string or None
        """
        for pattern in self.DATE_PATTERNS:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()

        return None

    def extract_thread_context(self, emails: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract context from email thread.

        Args:
            emails: List of emails in thread (oldest first)

        Returns:
            Thread context dictionary
        """
        if not emails:
            return {}

        # Get thread metadata
        thread_id = emails[0].get('thread_id')
        participants = set()

        for email in emails:
            from_addr = email.get('from', '')
            to_addr = email.get('to', '')

            if from_addr:
                participants.add(from_addr)
            if to_addr:
                participants.add(to_addr)

        # Parse all emails
        parsed = [self.parse_email(e) for e in emails]

        # Aggregate tasks
        all_tasks = []
        for p in parsed:
            all_tasks.extend(p.get('tasks', []))

        # Get latest subject
        subject = emails[-1].get('subject', 'No Subject')

        return {
            'thread_id': thread_id,
            'subject': subject,
            'participants': list(participants),
            'message_count': len(emails),
            'all_tasks': all_tasks,
            'emails': parsed
        }


# Singleton instance
_email_parser_instance = None

def get_email_parser() -> EmailParser:
    """Get singleton email parser instance."""
    global _email_parser_instance
    if _email_parser_instance is None:
        _email_parser_instance = EmailParser()
    return _email_parser_instance

"""
Message Pruner - Thread compression and message archiving

Keeps 4 most recent messages per thread, compresses to [Name:] format.
Archives old messages to .archive/ directory with metadata preservation.
Removes quoted replies, signatures, and extra whitespace.
"""

import re
import json
from typing import List, Dict
from datetime import datetime
from pathlib import Path
from .marketing_db import MarketingDB


class MessagePruner:
    """Manage message retention and thread compression."""
    
    def __init__(self, db: MarketingDB):
        """Initialize message pruner.
        
        Args:
            db: MarketingDB instance
        """
        self.db = db
        self.messages_per_thread = 4
        
        # Setup archive directory
        project_root = Path(__file__).parent.parent.parent.parent
        self.archive_dir = project_root / "memory" / "bank" / "user" / ".archive" / "messages"
        self.archive_dir.mkdir(parents=True, exist_ok=True)
    
    def prune_thread(self, thread_id: str) -> Dict[str, int]:
        """Prune messages in a thread, keeping 4 most recent.
        
        Args:
            thread_id: Gmail thread ID
        
        Returns:
            Dict with stats: {kept: int, archived: int, compressed: int}
        """
        # Get all messages in thread (non-archived only)
        messages = self.db.get_messages_by_thread(thread_id, include_archived=False)
        
        if len(messages) <= self.messages_per_thread:
            # Compress all messages
            compressed = 0
            for msg in messages:
                if self._compress_message(msg['message_id']):
                    compressed += 1
            
            return {'kept': len(messages), 'archived': 0, 'compressed': compressed}
        
        # Sort by sent_at (most recent last)
        messages.sort(key=lambda m: m['sent_at'])
        
        # Keep last N messages
        to_keep = messages[-self.messages_per_thread:]
        to_archive = messages[:-self.messages_per_thread]
        
        # Archive old messages
        archived = 0
        for msg in to_archive:
            if self._archive_message(msg):
                archived += 1
        
        # Compress kept messages
        compressed = 0
        for msg in to_keep:
            if self._compress_message(msg['message_id']):
                compressed += 1
        
        return {
            'kept': len(to_keep),
            'archived': archived,
            'compressed': compressed
        }
    
    def prune_all_threads(self) -> Dict[str, int]:
        """Prune all threads in database.
        
        Returns:
            Dict with stats: {threads: int, kept: int, archived: int, compressed: int}
        """
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT DISTINCT thread_id FROM messages WHERE is_archived = 0")
        thread_ids = [row[0] for row in cursor.fetchall()]
        
        total_stats = {
            'threads': len(thread_ids),
            'kept': 0,
            'archived': 0,
            'compressed': 0
        }
        
        for thread_id in thread_ids:
            stats = self.prune_thread(thread_id)
            total_stats['kept'] += stats['kept']
            total_stats['archived'] += stats['archived']
            total_stats['compressed'] += stats['compressed']
        
        return total_stats
    
    def _compress_message(self, message_id: str) -> bool:
        """Compress message content to [Name:] format.
        
        Args:
            message_id: Message ID to compress
        
        Returns:
            bool: True if compressed, False if already compressed or failed
        """
        msg = self.db.get_message(message_id)
        if not msg:
            return False
        
        # Skip if already compressed
        if msg.get('compressed_content'):
            return False
        
        # Get full message content from snippet
        content = msg.get('snippet', '')
        
        if not content:
            return False
        
        # Compress thread content
        compressed = self._compress_thread_content(
            content,
            sender_name=msg.get('sender_name') or msg.get('sender_email', '').split('@')[0]
        )
        
        # Update message
        cursor = self.db.conn.cursor()
        cursor.execute(
            "UPDATE messages SET compressed_content = ? WHERE message_id = ?",
            (compressed, message_id)
        )
        self.db.conn.commit()
        
        return True
    
    def _compress_thread_content(self, content: str, sender_name: str) -> str:
        """Compress content to [Name:] format with quoted text removed.
        
        Args:
            content: Original message content
            sender_name: Sender's name for prefix
        
        Returns:
            Compressed content
        """
        # Remove quoted text (lines starting with > or |)
        lines = content.split('\n')
        filtered_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            # Skip quoted lines
            if stripped.startswith('>') or stripped.startswith('|'):
                continue
            
            # Skip signature markers
            if any(marker in line for marker in [
                '---', '___', 'Sent from', 'Get Outlook',
                'Sent via', 'Best regards', 'Kind regards',
                'Sincerely', 'Thanks', 'Cheers', 'Regards'
            ]):
                break
            
            # Skip empty lines
            if not stripped:
                continue
            
            filtered_lines.append(stripped)
        
        # Join with single spaces
        text = ' '.join(filtered_lines)
        
        # Truncate to 500 chars
        if len(text) > 500:
            text = text[:497] + '...'
        
        # Format as [Name:] content
        return f"[{sender_name}:] {text}"
    
    def _archive_message(self, message: Dict) -> bool:
        """Archive message to .archive/ directory.
        
        Args:
            message: Message dict to archive
        
        Returns:
            bool: True if archived successfully
        """
        # Mark as archived in database
        self.db.archive_message(message['message_id'])
        
        # Save to archive file
        archive_file = self.archive_dir / f"{message['thread_id']}.jsonl"
        
        # Prepare archive record
        archive_record = {
            'message_id': message['message_id'],
            'gmail_message_id': message['gmail_message_id'],
            'sender_email': message['sender_email'],
            'sender_name': message['sender_name'],
            'subject': message['subject'],
            'snippet': message['snippet'],
            'sent_at': message['sent_at'],
            'archived_at': datetime.utcnow().isoformat(),
            'business_id': message.get('business_id'),
            'person_id': message.get('person_id')
        }
        
        # Append to JSONL file
        with open(archive_file, 'a') as f:
            f.write(json.dumps(archive_record) + '\n')
        
        return True
    
    def recover_archived_messages(self, thread_id: str) -> List[Dict]:
        """Recover archived messages for a thread.
        
        Args:
            thread_id: Gmail thread ID
        
        Returns:
            List of archived message dicts
        """
        archive_file = self.archive_dir / f"{thread_id}.jsonl"
        
        if not archive_file.exists():
            return []
        
        messages = []
        with open(archive_file, 'r') as f:
            for line in f:
                if line.strip():
                    messages.append(json.loads(line))
        
        return messages
    
    def get_archive_stats(self) -> Dict[str, int]:
        """Get archive statistics.
        
        Returns:
            Dict with: {threads: int, messages: int, size_mb: float}
        """
        archive_files = list(self.archive_dir.glob('*.jsonl'))
        
        total_messages = 0
        total_size = 0
        
        for file in archive_files:
            with open(file, 'r') as f:
                total_messages += sum(1 for line in f if line.strip())
            total_size += file.stat().st_size
        
        return {
            'threads': len(archive_files),
            'messages': total_messages,
            'size_mb': round(total_size / (1024 * 1024), 2)
        }

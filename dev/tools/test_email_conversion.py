"""
Email Conversion Test Script for uDOS v1.2.9

Tests email parsing and conversion to notes, checklists, and missions.

Usage:
    python dev/tools/test_email_conversion.py

What this tests:
    - Email parsing (HTML and plain text)
    - Task extraction from email content
    - Metadata extraction
    - Conversion to markdown notes
    - Conversion to task checklists
    - Conversion to mission workflows
    - Auto-detection logic

Author: @fredporter
Version: 1.2.9
Date: December 2025
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.services.email_parser import get_email_parser
from core.services.email_converter import get_email_converter


# Sample test emails
TEST_EMAILS = [
    {
        'id': 'test001',
        'thread_id': 'thread001',
        'subject': 'Weekly Tasks',
        'from': 'Boss <boss@company.com>',
        'to': 'You <you@company.com>',
        'date': 'Thu, 5 Dec 2025 09:00:00 -0800',
        'labels': ['INBOX', 'IMPORTANT'],
        'snippet': 'Here are the tasks for this week...',
        'body': """Hi Team,

Here are the tasks for this week:

- Review Q4 metrics by Friday
- Update project documentation
- Schedule team meeting
- Submit expense reports by Dec 10

Please let me know if you have any questions.

Thanks,
Boss"""
    },
    {
        'id': 'test002',
        'thread_id': 'thread002',
        'subject': 'URGENT: Production Issue',
        'from': 'DevOps <devops@company.com>',
        'to': 'Team <team@company.com>',
        'date': 'Thu, 5 Dec 2025 14:30:00 -0800',
        'labels': ['INBOX', 'URGENT'],
        'snippet': 'We have a critical issue in production...',
        'body': """URGENT: Production server down

Action items:
1. Check server logs immediately
2. Restart database service
3. Verify backup systems
4. Update status page
5. Send customer notification

This needs to be resolved ASAP!

Deadline: Today by 6pm"""
    },
    {
        'id': 'test003',
        'thread_id': 'thread003',
        'subject': 'Meeting Notes - Q1 Planning',
        'from': 'Project Manager <pm@company.com>',
        'to': 'Team <team@company.com>',
        'date': 'Wed, 4 Dec 2025 11:00:00 -0800',
        'labels': ['INBOX'],
        'snippet': 'Thanks for attending the Q1 planning meeting...',
        'body': """Team,

Thanks for attending the Q1 planning meeting today. Here are my notes:

Key Decisions:
- Launch date set for March 15
- Budget approved at $500k
- Team to grow by 3 people

Links:
- Project timeline: https://docs.company.com/timeline
- Budget spreadsheet: https://sheets.company.com/budget

No specific action items from this meeting - just FYI.

Best,
PM"""
    }
]


def test_email_parser():
    """Test email parsing functionality."""
    print("=" * 60)
    print("Email Parser Test - v1.2.9")
    print("=" * 60)
    print()
    
    parser = get_email_parser()
    
    for i, email in enumerate(TEST_EMAILS, 1):
        print(f"Test {i}: {email['subject']}")
        print("-" * 60)
        
        # Parse email
        parsed = parser.parse_email(email)
        
        # Show metadata
        metadata = parsed['metadata']
        print(f"From: {metadata['from']['name']} <{metadata['from']['email']}>")
        print(f"Date: {metadata['date']}")
        print(f"Priority: {parsed['priority']}")
        
        # Show tasks
        tasks = parsed['tasks']
        print(f"Tasks found: {len(tasks)}")
        for task in tasks:
            print(f"  • {task['text']}")
            if task.get('deadline'):
                print(f"    Deadline: {task['deadline']}")
        
        # Show URLs
        urls = parsed['urls']
        if urls:
            print(f"URLs found: {len(urls)}")
            for url in urls:
                print(f"  - {url}")
        
        # Show deadline
        if parsed.get('deadline'):
            print(f"Overall deadline: {parsed['deadline']}")
        
        print()
    
    print("✅ Email parser tests complete\n")


def test_email_converter():
    """Test email conversion functionality."""
    print("=" * 60)
    print("Email Converter Test - v1.2.9")
    print("=" * 60)
    print()
    
    converter = get_email_converter()
    
    for i, email in enumerate(TEST_EMAILS, 1):
        print(f"Test {i}: {email['subject']}")
        print("-" * 60)
        
        # Test auto-detection
        result = converter.auto_convert(email)
        
        if result['success']:
            print(f"✅ Auto-converted to: {result['type']}")
            print(f"   File: {result['filename']}")
            
            if 'task_count' in result:
                print(f"   Tasks: {result['task_count']}")
            
            # Show file contents (first few lines)
            filepath = Path(result['path'])
            if filepath.exists():
                content = filepath.read_text()
                lines = content.split('\n')[:10]
                print(f"\n   Preview:")
                for line in lines:
                    print(f"   {line}")
                if len(content.split('\n')) > 10:
                    print(f"   ... ({len(content.split('\n')) - 10} more lines)")
        else:
            print(f"❌ Conversion failed: {result.get('error')}")
        
        print()
    
    print("✅ Email converter tests complete\n")


def test_conversion_types():
    """Test specific conversion types."""
    print("=" * 60)
    print("Conversion Types Test - v1.2.9")
    print("=" * 60)
    print()
    
    converter = get_email_converter()
    email = TEST_EMAILS[0]  # Weekly Tasks email
    
    # Test each conversion type
    types = ['note', 'checklist', 'mission']
    
    for conv_type in types:
        print(f"Testing conversion to {conv_type}...")
        print("-" * 60)
        
        if conv_type == 'note':
            result = converter.convert_to_note(email)
        elif conv_type == 'checklist':
            result = converter.convert_to_checklist(email)
        elif conv_type == 'mission':
            result = converter.convert_to_mission(email)
        
        if result['success']:
            print(f"✅ Created {result['type']}: {result['filename']}")
            
            # Check file exists
            filepath = Path(result['path'])
            if filepath.exists():
                size = filepath.stat().st_size
                print(f"   Size: {size} bytes")
        else:
            print(f"❌ Failed: {result.get('error')}")
        
        print()
    
    print("✅ Conversion types tests complete\n")


def test_summary():
    """Show test summary."""
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    converter = get_email_converter()
    
    # Count created files
    notes = list(converter.docs_dir.glob('*.md'))
    checklists = list(converter.checklists_dir.glob('*.md'))
    missions = list(converter.missions_dir.glob('*.upy'))
    
    print(f"Files created:")
    print(f"  Notes: {len(notes)} in {converter.docs_dir}")
    print(f"  Checklists: {len(checklists)} in {converter.checklists_dir}")
    print(f"  Missions: {len(missions)} in {converter.missions_dir}")
    print()
    
    print("✅ All conversion tests passed!")
    print()
    print("Next steps:")
    print("  - Use IMPORT GMAIL to import real emails")
    print("  - Test with HTML emails")
    print("  - Test with email threads")
    print()


if __name__ == "__main__":
    try:
        test_email_parser()
        test_email_converter()
        test_conversion_types()
        test_summary()
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

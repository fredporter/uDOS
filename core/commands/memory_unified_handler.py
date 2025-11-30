"""
MEMORY Unified Command Handler - v1.0.23
Consolidates PRIVATE, SHARED, COMMUNITY, and KB (Knowledge Bank) into one smart command

Smart Features:
- Interactive tier picker
- Auto-tier selection based on content
- Cross-tier search with permissions
- Security-aware suggestions

Commands:
  MEMORY                  Interactive tier picker
  MEMORY <query>          Smart search across accessible tiers
  MEMORY --save <file>    Auto-select appropriate tier
  MEMORY --tier=private   Direct tier access
  MEMORY --list           List all accessible memory

Author: uDOS Development Team
Version: 1.0.23
"""

from pathlib import Path
from typing import List, Dict, Optional
import sys
import json

# Import the original handlers
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.commands.private_commands import PrivateCommandHandler
from core.commands.shared_commands import SharedCommandHandler
from core.commands.community_commands import CommunityCommandHandler
# KnowledgeCommandHandler removed in v2.0.0 - use guide_handler instead
# from core.commands.knowledge_commands import KnowledgeCommandHandler


class MemoryUnifiedHandler:
    """Unified memory access - consolidates 4-tier memory system"""

    def __init__(self, viewport=None, logger=None, user_manager=None):
        """Initialize with all tier handlers"""
        self.viewport = viewport
        self.logger = logger
        self.user_manager = user_manager

        # Initialize tier handlers
        self.private_handler = PrivateCommandHandler()
        self.shared_handler = SharedCommandHandler()
        self.community_handler = CommunityCommandHandler()
        # self.kb_handler = KnowledgeCommandHandler()  # Removed in v2.0.0
        self.kb_handler = None  # KB commands redirect to GUIDE handler

        # Tier definitions with security levels
        self.tiers = {
            'private': {
                'name': 'PRIVATE',
                'icon': '🔒',
                'description': 'Encrypted, you only',
                'speed': '<10ms',
                'security': 'AES-256',
                'access': 'User',
                'handler': self.private_handler,
                'priority': 4,  # Highest priority for personal
                'path': 'memory/private'
            },
            'shared': {
                'name': 'SHARED',
                'icon': '🔐',
                'description': 'Selected team members',
                'speed': '<25ms',
                'security': 'AES-128',
                'access': 'Team',
                'handler': self.shared_handler,
                'priority': 3,
                'path': 'memory/shared'
            },
            'community': {
                'name': 'COMMUNITY',
                'icon': '👥',
                'description': 'Group access',
                'speed': '<50ms',
                'security': 'None',
                'access': 'Group',
                'handler': self.community_handler,
                'priority': 2,
                'path': 'memory/community'
            },
            'public': {
                'name': 'PUBLIC',
                'icon': '🌍',
                'description': 'Everyone, open',
                'speed': '<100ms',
                'security': 'None',
                'access': 'All',
                'handler': self.kb_handler,
                'priority': 1,
                'path': 'memory/public'
            }
        }

    def handle(self, command: str, args: List[str]) -> str:
        """Route MEMORY commands intelligently"""

        # No command = interactive picker
        if not command:
            return self._show_picker()

        # Help
        if command == "HELP" or command == "--help":
            return self._show_help()

        # Tier-specific access
        if command.startswith("--tier="):
            tier_name = command.split("=")[1].lower()
            action = args[0] if args else "list"
            return self._access_tier(tier_name, action, args[1:] if len(args) > 1 else [])

        # Direct tier shortcuts
        if command in ["--private", "-p"]:
            return self._access_tier('private', args[0] if args else "list", args[1:] if len(args) > 1 else [])

        if command in ["--shared", "-s"]:
            return self._access_tier('shared', args[0] if args else "list", args[1:] if len(args) > 1 else [])

        if command in ["--community", "-c"]:
            return self._access_tier('community', args[0] if args else "list", args[1:] if len(args) > 1 else [])

        if command in ["--public", "--kb"]:
            return self._access_tier('public', args[0] if args else "list", args[1:] if len(args) > 1 else [])

        # Save with auto-tier selection
        if command == "--save":
            file_path = args[0] if args else None
            return self._smart_save(file_path, args[1:])

        # List all accessible
        if command in ["--list", "LIST"]:
            return self._list_all()

        # Smart search across tiers
        query = command + " " + " ".join(args) if args else command
        return self._smart_search(query.strip())

    def _show_picker(self) -> str:
        """Show interactive tier picker"""
        return """
┌─────────────────────────────────────────────────────────────────┐
│  MEMORY - Select tier:                                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. 🔒 PRIVATE     Encrypted, you only         <10ms  AES-256  │
│     Your personal notes, passwords, private scripts            │
│                                                                 │
│  2. 🔐 SHARED      Selected team members       <25ms  AES-128  │
│     Team documents, shared configs, collaboration              │
│                                                                 │
│  3. 👥 COMMUNITY   Group access                <50ms  Plain    │
│     Community guides, shared scripts, templates                │
│                                                                 │
│  4. 🌍 PUBLIC      Everyone, open              <100ms Plain    │
│     Public docs, knowledge base, examples                      │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  Quick Actions:                                                 │
│    MEMORY <query>           Search all accessible tiers        │
│    MEMORY --save <file>     Save with auto-tier selection      │
│    MEMORY --tier=private    Direct tier access                 │
│    MEMORY --list            List all content                   │
│                                                                 │
│  Shortcuts:                                                     │
│    MEMORY -p                PRIVATE tier                        │
│    MEMORY -s                SHARED tier                         │
│    MEMORY -c                COMMUNITY tier                      │
│    MEMORY --kb              PUBLIC knowledge base               │
│                                                                 │
│  Security Recommendations:                                      │
│    • Passwords, keys      → PRIVATE (encrypted)                │
│    • Team configs         → SHARED (encrypted)                 │
│    • Public guides        → COMMUNITY or PUBLIC                │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  [1-4] Select | [S] Search | [L] List | [H] Help               │
└─────────────────────────────────────────────────────────────────┘

Enter choice (1-4) or action: """

    def _show_help(self) -> str:
        """Show MEMORY command help"""
        return """
┌─────────────────────────────────────────────────────────────────┐
│  MEMORY - Unified 4-Tier Memory System                         │
└─────────────────────────────────────────────────────────────────┘

🧠 Smart memory access consolidating PRIVATE, SHARED, COMMUNITY, and KB

USAGE:
  MEMORY                      Interactive tier picker
  MEMORY <query>              Smart search across tiers
  MEMORY --tier=<tier>        Direct tier access
  MEMORY --save <file>        Save with auto-tier selection
  MEMORY --list               List all accessible memory
  MEMORY -p, -s, -c, --kb     Tier shortcuts

TIERS (Speed & Security):
  🔒 PRIVATE   <10ms   AES-256  You only
  🔐 SHARED    <25ms   AES-128  Team members
  👥 COMMUNITY <50ms   None     Group access
  🌍 PUBLIC    <100ms  None     Everyone

SMART TIER SELECTION:
  MEMORY automatically suggests the right tier based on content:
  • Passwords, API keys    → PRIVATE (encrypted)
  • Team configurations    → SHARED (selective)
  • Scripts, templates     → COMMUNITY (group)
  • Documentation          → PUBLIC (open)

EXAMPLES:
  MEMORY                          # Interactive picker
  MEMORY api-keys                 # Search all tiers
  MEMORY --tier=private list      # List private memory
  MEMORY -p save mypassword.txt   # Save to private
  MEMORY --save config.json       # Auto-select tier
  MEMORY --list                   # List everything

CROSS-TIER SEARCH:
  Smart search respects permissions and ranks results:
  1. PRIVATE (if you have access)
  2. SHARED (if you're in team)
  3. COMMUNITY (if you're in group)
  4. PUBLIC (always accessible)

SECURITY WARNINGS:
  ⚠️  Saving sensitive data to public tiers triggers warnings
  ⚠️  Auto-encryption for PRIVATE/SHARED tiers
  ⚠️  Access logs maintained for audit trail

BACKWARDS COMPATIBILITY:
  PRIVATE    → MEMORY --tier=private
  SHARED     → MEMORY --tier=shared
  COMMUNITY  → MEMORY --tier=community
  KB         → MEMORY --tier=public

All old commands still work with migration notices.

See also: DOCS (documentation), LEARN (learning content)
"""

    def _access_tier(self, tier_name: str, action: str, args: List[str]) -> str:
        """Access specific tier with action"""
        if tier_name not in self.tiers:
            return f"\n❌ Unknown tier '{tier_name}'\n\nAvailable: private, shared, community, public\n"

        tier = self.tiers[tier_name]
        handler = tier['handler']

        # Route to appropriate handler
        try:
            result = handler.handle(action.upper(), args)

            # Add tier indicator to result
            tier_info = f"\n[{tier['icon']} {tier['name']} tier - {tier['speed']} access]\n"
            return tier_info + result

        except Exception as e:
            return f"\n❌ Error accessing {tier['name']} tier: {e}\n"

    def _smart_save(self, file_path: Optional[str], args: List[str]) -> str:
        """Save with intelligent tier selection"""
        if not file_path:
            return "\n❌ Usage: MEMORY --save <file> [content]\n"

        # Analyze content to suggest tier
        suggested_tier = self._analyze_content_security(file_path, args)

        return f"""
Smart Save Analysis for: {file_path}
─────────────────────────────────────────────────────────────────

Suggested tier: {self.tiers[suggested_tier]['icon']} {suggested_tier.upper()}
Reason: {self._get_tier_reason(file_path, suggested_tier)}

Security: {self.tiers[suggested_tier]['security']}
Access: {self.tiers[suggested_tier]['access']}
Speed: {self.tiers[suggested_tier]['speed']}

Proceed? (y/n) or specify tier (private/shared/community/public):
"""

    def _analyze_content_security(self, file_path: str, content: List[str]) -> str:
        """Analyze content to suggest appropriate tier"""
        file_lower = file_path.lower()
        content_str = " ".join(content).lower() if content else ""

        # Password/key indicators → PRIVATE
        sensitive_keywords = ['password', 'key', 'secret', 'token', 'credential', 'api_key']
        if any(keyword in file_lower or keyword in content_str for keyword in sensitive_keywords):
            return 'private'

        # Documentation/guides → PUBLIC (check before config to catch README)
        doc_files = ['readme', 'license', 'contributing', 'changelog', 'authors']
        doc_extensions = ['.md', '.txt', '.html', '.rst']
        if any(doc in file_lower for doc in doc_files) or any(file_path.endswith(ext) for ext in doc_extensions):
            if any(doc in file_lower for doc in doc_files) or 'guide' in file_lower or 'tutorial' in file_lower or 'documentation' in file_lower:
                return 'public'

        # Config files → SHARED (unless personal)
        if 'config' in file_lower or 'settings' in file_lower:
            if 'personal' in file_lower or 'my' in file_lower:
                return 'private'
            return 'shared'

        # Scripts → COMMUNITY (shareable)
        script_extensions = ['.py', '.uscript', '.sh', '.js']
        if any(file_path.endswith(ext) for ext in script_extensions):
            return 'community'

        # Default to PRIVATE (safe choice)
        return 'private'

    def _get_tier_reason(self, file_path: str, tier: str) -> str:
        """Get human-readable reason for tier suggestion"""
        reasons = {
            'private': {
                'password': 'Contains sensitive credentials',
                'key': 'Contains API keys or secrets',
                'personal': 'Personal file',
                'default': 'Safe default for unknown content'
            },
            'shared': {
                'config': 'Team configuration file',
                'settings': 'Shared settings',
                'default': 'Team-level access appropriate'
            },
            'community': {
                'script': 'Shareable code/script',
                '.py': 'Python script for community',
                '.uscript': 'uCODE script for sharing',
                'default': 'Useful for community sharing'
            },
            'public': {
                'readme': 'Public documentation',
                'guide': 'Educational content',
                'tutorial': 'Learning resource',
                'default': 'Suitable for public access'
            }
        }

        file_lower = file_path.lower()
        tier_reasons = reasons.get(tier, {})

        # Find matching reason
        for keyword, reason in tier_reasons.items():
            if keyword in file_lower:
                return reason

        return tier_reasons.get('default', 'Recommended tier based on analysis')

    def _smart_search(self, query: str) -> str:
        """Smart search across all accessible tiers"""
        query_lower = query.lower()
        results = []

        # Search each tier (respecting permissions)
        for tier_name, tier_data in self.tiers.items():
            try:
                handler = tier_data['handler']
                # Try to search (may fail if no access)
                tier_results = handler.handle("SEARCH", [query])

                if tier_results and "No results" not in tier_results:
                    results.append({
                        'tier': tier_name,
                        'icon': tier_data['icon'],
                        'results': tier_results,
                        'priority': tier_data['priority']
                    })
            except Exception:
                # No access to this tier, skip
                continue

        if not results:
            return f"\n❌ No results found for '{query}' in accessible tiers\n"

        # Sort by priority
        results.sort(key=lambda x: x['priority'], reverse=True)

        return self._format_search_results(query, results)

    def _format_search_results(self, query: str, results: List[Dict]) -> str:
        """Format cross-tier search results"""
        output = [f"\n🔍 Memory search for '{query}'", "═" * 60, ""]
        output.append(f"Found in {len(results)} tier(s):")
        output.append("")

        for result in results:
            output.append(f"{result['icon']} {result['tier'].upper()} tier:")
            output.append("─" * 60)
            output.append(result['results'])
            output.append("")

        output.append("Access specific tier: MEMORY --tier=<tier> <action>")
        output.append("")

        return "\n".join(output)

    def _list_all(self) -> str:
        """List all accessible memory across tiers"""
        output = ["\n🧠 All Accessible Memory", "═" * 60, ""]

        accessible_count = 0
        for tier_name, tier_data in self.tiers.items():
            try:
                handler = tier_data['handler']
                listing = handler.handle("LIST", [])

                output.append(f"{tier_data['icon']} {tier_name.upper()} ({tier_data['description']})")
                output.append("─" * 60)
                output.append(listing)
                output.append("")
                accessible_count += 1
            except Exception as e:
                output.append(f"{tier_data['icon']} {tier_name.upper()} - No access")
                output.append("")

        output.append(f"Accessible tiers: {accessible_count}/4")
        output.append("")

        return "\n".join(output)


def create_handler(viewport=None, logger=None, user_manager=None):
    """Factory function to create unified handler"""
    return MemoryUnifiedHandler(viewport=viewport, logger=logger, user_manager=user_manager)

"""
uDOS v1.0.20 - KNOWLEDGE Command Implementation
CLI commands for 4-tier knowledge management
"""

from core.services.tier_knowledge_manager import TierKnowledgeManager
from core.services.knowledge_types import KnowledgeTier, KnowledgeType


def cmd_knowledge(user_data, args):
    """
    KNOWLEDGE - Manage 4-tier knowledge bank

    Usage:
        KNOWLEDGE ADD <tier> <type> <title> - Add knowledge
        KNOWLEDGE SEARCH <query> [--tier N] [--tags tag1,tag2] - Search
        KNOWLEDGE VIEW <id> - View knowledge item
        KNOWLEDGE STATS - Show tier statistics
        KNOWLEDGE TIERS - List tier descriptions

    Examples:
        KNOWLEDGE ADD 0 survival "Water Filter" - Add personal survival note
        KNOWLEDGE SEARCH "water" --tier 3 - Search public tier
        KNOWLEDGE VIEW abc123 - View specific knowledge
        KNOWLEDGE STATS - Show tier statistics
    """
    if not args:
        return {
            'success': False,
            'message': 'Usage: KNOWLEDGE <action> [args...]\nType "HELP KNOWLEDGE" for details'
        }

    action = args[0].upper()
    manager = TierKnowledgeManager(user_id=user_data.username or "user")

    if action == 'ADD':
        return _knowledge_add(manager, args[1:])
    elif action == 'SEARCH':
        return _knowledge_search(manager, args[1:])
    elif action == 'VIEW':
        return _knowledge_view(manager, args[1:])
    elif action == 'STATS':
        return _knowledge_stats(manager)
    elif action == 'TIERS':
        return _knowledge_tiers()
    else:
        return {
            'success': False,
            'message': f'Unknown action: {action}\nAvailable: ADD, SEARCH, VIEW, STATS, TIERS'
        }


def _knowledge_add(manager, args):
    """Add knowledge to tier."""
    if len(args) < 3:
        return {
            'success': False,
            'message': 'Usage: KNOWLEDGE ADD <tier> <type> <title>\nExample: KNOWLEDGE ADD 0 survival "Water Filter"'
        }

    try:
        tier = KnowledgeTier(int(args[0]))
    except (ValueError, IndexError):
        return {
            'success': False,
            'message': f'Invalid tier: {args[0]}\nValid tiers: 0=PERSONAL, 1=SHARED, 2=GROUP, 3=PUBLIC'
        }

    try:
        knowledge_type = KnowledgeType[args[1].upper()]
    except KeyError:
        return {
            'success': False,
            'message': f'Invalid type: {args[1]}\nValid types: {", ".join([t.name for t in KnowledgeType])}'
        }

    title = ' '.join(args[2:])

    # Prompt for content
    content = input("Enter knowledge content (Ctrl+D when done):\n")

    # Prompt for tags
    tags_input = input("Enter tags (comma-separated, optional): ")
    tags = [t.strip() for t in tags_input.split(',')] if tags_input else []

    # Add knowledge
    item = manager.add_knowledge(tier, knowledge_type, title, content, tags)

    return {
        'success': True,
        'message': f'Added knowledge "{title}" to tier {tier.value} ({tier.name})',
        'data': {
            'id': item.id,
            'tier': tier.name,
            'type': knowledge_type.name,
            'encrypted': item.encrypted
        }
    }


def _knowledge_search(manager, args):
    """Search knowledge."""
    if not args:
        return {
            'success': False,
            'message': 'Usage: KNOWLEDGE SEARCH <query> [--tier N] [--tags tag1,tag2]'
        }

    # Parse arguments
    query_parts = []
    tier = None
    tags = None

    i = 0
    while i < len(args):
        if args[i] == '--tier' and i + 1 < len(args):
            try:
                tier = KnowledgeTier(int(args[i + 1]))
            except ValueError:
                pass
            i += 2
        elif args[i] == '--tags' and i + 1 < len(args):
            tags = [t.strip() for t in args[i + 1].split(',')]
            i += 2
        else:
            query_parts.append(args[i])
            i += 1

    query = ' '.join(query_parts)

    if not query:
        return {
            'success': False,
            'message': 'No search query provided'
        }

    # Search
    results = manager.search_knowledge(query, tier=tier, tags=tags)

    if not results:
        return {
            'success': True,
            'message': f'No results found for "{query}"',
            'data': {'results': []}
        }

    # Format results
    result_list = []
    for item in results:
        result_list.append({
            'id': item.id,
            'title': item.title,
            'type': item.type.name,
            'tier': item.tier.name,
            'tags': item.tags,
            'views': item.views,
            'preview': item.content[:100] + '...' if len(item.content) > 100 else item.content
        })

    return {
        'success': True,
        'message': f'Found {len(results)} result(s) for "{query}"',
        'data': {'results': result_list}
    }


def _knowledge_view(manager, args):
    """View specific knowledge item."""
    if not args:
        return {
            'success': False,
            'message': 'Usage: KNOWLEDGE VIEW <id>'
        }

    knowledge_id = args[0]
    item = manager.get_knowledge(knowledge_id)

    if not item:
        return {
            'success': False,
            'message': f'Knowledge item not found: {knowledge_id}'
        }

    return {
        'success': True,
        'message': f'Knowledge: {item.title}',
        'data': {
            'id': item.id,
            'title': item.title,
            'type': item.type.name,
            'tier': item.tier.name,
            'content': item.content,
            'tags': item.tags,
            'author_id': item.author_id,
            'created_at': item.created_at.isoformat(),
            'views': item.views,
            'rating': item.rating,
            'encrypted': item.encrypted
        }
    }


def _knowledge_stats(manager):
    """Show tier statistics."""
    stats = manager.get_tier_stats()

    result_lines = ['4-Tier Knowledge Bank Statistics:\n']

    for tier_name, tier_stats in stats.items():
        desc = tier_stats['description']
        result_lines.append(f"{desc['icon']} Tier {desc['name']} - {desc['description']}")
        result_lines.append(f"  Total: {tier_stats['total']}")
        result_lines.append(f"  Owned: {tier_stats['owned']}")
        result_lines.append(f"  Avg Views: {tier_stats['avg_views']:.1f}\n")

    return {
        'success': True,
        'message': '\n'.join(result_lines),
        'data': {'stats': stats}
    }


def _knowledge_tiers():
    """List tier descriptions."""
    from core.services.knowledge_types import TIER_DESCRIPTIONS

    result_lines = ['4-Tier Knowledge System:\n']

    for tier, desc in TIER_DESCRIPTIONS.items():
        result_lines.append(f"{desc['icon']} Tier {tier.value}: {desc['name']}")
        result_lines.append(f"  {desc['description']}")
        result_lines.append(f"  Color: {desc['color']}\n")

    return {
        'success': True,
        'message': '\n'.join(result_lines)
    }

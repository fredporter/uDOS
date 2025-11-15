"""
Knowledge Command Handler for uDOS v1.0.18
Handles knowledge management, reading, and contribution commands.
"""

import os
from datetime import datetime
from typing import Dict, Any, Optional
from core.services.knowledge_service import KnowledgeService
from core.services.xp_service import XPService, SkillTree


class KnowledgeCommandHandler:
    """Handles knowledge-related commands."""

    def __init__(self, xp_service: XPService, knowledge_service: KnowledgeService):
        """
        Initialize handler.

        Args:
            xp_service: XP service instance
            knowledge_service: Knowledge service instance
        """
        self.xp_service = xp_service
        self.knowledge_service = knowledge_service

    def handle_command(self, command: str, args: list) -> Dict[str, Any]:
        """
        Handle knowledge command.

        Args:
            command: Command name (e.g., "INDEX", "SEARCH", "READ")
            args: Command arguments

        Returns:
            Result dictionary with success status and data
        """
        command = command.upper()

        handlers = {
            'INDEX': self._handle_index,
            'SEARCH': self._handle_search,
            'LIST': self._handle_list,
            'READ': self._handle_read,
            'CONTRIBUTE': self._handle_contribute,
            'STATS': self._handle_stats,
            'INFO': self._handle_info,
        }

        handler = handlers.get(command)
        if not handler:
            return {
                'success': False,
                'error': f"Unknown knowledge command: {command}",
                'available_commands': list(handlers.keys())
            }

        return handler(args)

    def _handle_index(self, args: list) -> Dict[str, Any]:
        """
        Index knowledge base.

        Usage: KNOWLEDGE INDEX
        """
        try:
            result = self.knowledge_service.index_knowledge_base()

            if 'error' in result:
                return {
                    'success': False,
                    'error': result['error']
                }

            return {
                'success': True,
                'indexed': result['indexed'],
                'failed': len(result.get('errors', [])) if result.get('errors') else 0,
                'total': result['total_items'],
                'message': f"Indexed {result['indexed']} knowledge items"
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"Indexing failed: {str(e)}"
            }

    def _handle_search(self, args: list) -> Dict[str, Any]:
        """
        Search knowledge items.

        Usage: KNOWLEDGE SEARCH <query> [skill_tree]
        """
        if not args:
            return {
                'success': False,
                'error': "Usage: KNOWLEDGE SEARCH <query> [skill_tree]"
            }

        query = args[0]
        skill_tree = args[1] if len(args) > 1 else None

        # Validate skill tree if provided
        if skill_tree:
            try:
                skill_tree = SkillTree[skill_tree.upper()]
            except KeyError:
                return {
                    'success': False,
                    'error': f"Invalid skill tree: {skill_tree}",
                    'valid_trees': [tree.name for tree in SkillTree]
                }

        results = self.knowledge_service.search_knowledge(
            query=query,
            skill_tree=skill_tree,
            xp_service=self.xp_service
        )

        return {
            'success': True,
            'query': query,
            'skill_tree': skill_tree.name if skill_tree else None,
            'results': results,
            'count': len(results)
        }

    def _handle_list(self, args: list) -> Dict[str, Any]:
        """
        List knowledge items.

        Usage: KNOWLEDGE LIST [skill_tree]
        """
        skill_tree = None

        if args:
            try:
                skill_tree = SkillTree[args[0].upper()]
            except KeyError:
                return {
                    'success': False,
                    'error': f"Invalid skill tree: {args[0]}",
                    'valid_trees': [tree.name for tree in SkillTree]
                }

        if skill_tree:
            items = self.knowledge_service.get_knowledge_by_skill(skill_tree)
        else:
            # Get all knowledge items
            items = self.knowledge_service.search_knowledge(
                query="",
                xp_service=self.xp_service
            )

        return {
            'success': True,
            'skill_tree': skill_tree.name if skill_tree else 'ALL',
            'items': items,
            'count': len(items)
        }

    def _handle_read(self, args: list) -> Dict[str, Any]:
        """
        Read knowledge item.

        Usage: KNOWLEDGE READ <id> [time_seconds]
        """
        if not args:
            return {
                'success': False,
                'error': "Usage: KNOWLEDGE READ <id> [time_seconds]"
            }

        try:
            knowledge_id = int(args[0])
        except ValueError:
            return {
                'success': False,
                'error': f"Invalid knowledge ID: {args[0]}"
            }

        time_spent = 60  # Default 1 minute
        if len(args) > 1:
            try:
                time_spent = int(args[1])
            except ValueError:
                return {
                    'success': False,
                    'error': f"Invalid time value: {args[1]}"
                }

        result = self.knowledge_service.read_knowledge(
            knowledge_id=knowledge_id,
            xp_service=self.xp_service,
            time_spent_seconds=time_spent
        )

        if 'error' in result:
            return {
                'success': False,
                'error': result['error']
            }

        return {
            'success': True,
            'knowledge_id': knowledge_id,
            'xp_awarded': result['xp_awarded'],
            'skill_tree': result.get('skill_tree'),
            'message': f"Read knowledge #{knowledge_id}, earned {result['xp_awarded']} XP in {result.get('skill_tree', 'INFORMATION')}"
        }

    def _handle_contribute(self, args: list) -> Dict[str, Any]:
        """
        Contribute to knowledge.

        Usage: KNOWLEDGE CONTRIBUTE <id> <type> <description>

        Types: correction, addition, example, resource, translation
        """
        if len(args) < 3:
            return {
                'success': False,
                'error': "Usage: KNOWLEDGE CONTRIBUTE <id> <type> <description>",
                'valid_types': ['correction', 'addition', 'example', 'resource', 'translation']
            }

        try:
            knowledge_id = int(args[0])
        except ValueError:
            return {
                'success': False,
                'error': f"Invalid knowledge ID: {args[0]}"
            }

        contribution_type = args[1].lower()
        valid_types = ['correction', 'addition', 'example', 'resource', 'translation']

        if contribution_type not in valid_types:
            return {
                'success': False,
                'error': f"Invalid contribution type: {contribution_type}",
                'valid_types': valid_types
            }

        description = ' '.join(args[2:])

        result = self.knowledge_service.contribute_knowledge(
            knowledge_id=knowledge_id,
            contribution_type=contribution_type,
            description=description,
            xp_service=self.xp_service
        )

        if 'error' in result:
            return {
                'success': False,
                'error': result['error']
            }

        return {
            'success': True,
            'knowledge_id': knowledge_id,
            'contribution_type': contribution_type,
            'xp_awarded': result['xp_awarded'],
            'message': f"Contribution recorded, earned {result['xp_awarded']} XP"
        }

    def _handle_stats(self, args: list) -> Dict[str, Any]:
        """
        Show reading statistics.

        Usage: KNOWLEDGE STATS
        """
        stats = self.knowledge_service.get_reading_stats()

        return {
            'success': True,
            'total_reads': stats['total_reads'],
            'total_xp': stats['total_xp'],
            'total_time_hours': stats['total_time_hours'],
            'average_completion': stats.get('avg_completion', 0),
            'message': f"Read {stats['total_reads']} items, earned {stats['total_xp']} XP, spent {stats['total_time_hours']} hours"
        }

    def _handle_info(self, args: list) -> Dict[str, Any]:
        """
        Show knowledge item details.

        Usage: KNOWLEDGE INFO <id>
        """
        if not args:
            return {
                'success': False,
                'error': "Usage: KNOWLEDGE INFO <id>"
            }

        try:
            knowledge_id = int(args[0])
        except ValueError:
            return {
                'success': False,
                'error': f"Invalid knowledge ID: {args[0]}"
            }

        # Get knowledge item via search
        results = self.knowledge_service.search_knowledge(
            query="",
            xp_service=self.xp_service
        )

        item = None
        for result in results:
            if result['id'] == knowledge_id:
                item = result
                break

        if not item:
            return {
                'success': False,
                'error': f"Knowledge item not found: {knowledge_id}"
            }

        return {
            'success': True,
            'item': item
        }

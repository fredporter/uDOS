"""
uDOS v1.0.20 - 4-Tier Knowledge Bank Architecture
Defines the data structures and privacy model for the knowledge tier system
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime


class KnowledgeTier(Enum):
    """
    Four-tier knowledge privacy system.

    Tier 0 (PERSONAL): Private, encrypted, never shared
    Tier 1 (SHARED): Explicitly shared with specific users
    Tier 2 (GROUP): Community/group knowledge, anonymous
    Tier 3 (PUBLIC): Global knowledge bank, read-only
    """
    PERSONAL = 0  # Private, encrypted, local-only
    SHARED = 1    # Shared with specific users, trackable
    GROUP = 2     # Community knowledge, anonymous
    PUBLIC = 3    # Global read-only knowledge bank


class KnowledgeType(Enum):
    """Types of knowledge that can be stored."""
    SURVIVAL = "survival"
    SKILL = "skill"
    RECIPE = "recipe"
    GUIDE = "guide"
    REFERENCE = "reference"
    NOTE = "note"
    LINK = "link"
    EXPERIENCE = "experience"
    TIP = "tip"
    WARNING = "warning"


@dataclass
class KnowledgeItem:
    """
    A single piece of knowledge in the knowledge bank.

    Attributes:
        id: Unique identifier (UUID)
        tier: Privacy tier (0-3)
        type: Type of knowledge
        title: Short descriptive title
        content: Full content (markdown supported)
        tags: List of categorization tags
        author_id: User ID (anonymized for tier 2+)
        created_at: Creation timestamp
        updated_at: Last update timestamp
        shared_with: List of user IDs (tier 1 only)
        group_id: Group identifier (tier 2 only)
        views: Number of times viewed
        rating: Community rating (tier 2-3)
        encrypted: Whether content is encrypted
        checksum: Content integrity hash
    """
    id: str
    tier: KnowledgeTier
    type: KnowledgeType
    title: str
    content: str
    tags: List[str]
    author_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    shared_with: Optional[List[str]] = None
    group_id: Optional[str] = None
    views: int = 0
    rating: float = 0.0
    encrypted: bool = False
    checksum: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'id': self.id,
            'tier': self.tier.value,
            'type': self.type.value,
            'title': self.title,
            'content': self.content,
            'tags': ','.join(self.tags),
            'author_id': self.author_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'shared_with': ','.join(self.shared_with) if self.shared_with else None,
            'group_id': self.group_id,
            'views': self.views,
            'rating': self.rating,
            'encrypted': 1 if self.encrypted else 0,
            'checksum': self.checksum
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeItem':
        """Create from dictionary."""
        return cls(
            id=data['id'],
            tier=KnowledgeTier(data['tier']),
            type=KnowledgeType(data['type']),
            title=data['title'],
            content=data['content'],
            tags=data['tags'].split(',') if data['tags'] else [],
            author_id=data.get('author_id'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None,
            shared_with=data['shared_with'].split(',') if data.get('shared_with') else None,
            group_id=data.get('group_id'),
            views=data.get('views', 0),
            rating=data.get('rating', 0.0),
            encrypted=bool(data.get('encrypted', 0)),
            checksum=data.get('checksum')
        )


@dataclass
class PrivacySettings:
    """
    Privacy settings for knowledge tiers.

    Attributes:
        allow_tier_0_backup: Allow encrypted backups of personal knowledge
        allow_tier_1_sharing: Enable sharing to tier 1 (shared)
        allow_tier_2_contribution: Enable anonymous contribution to groups
        allow_tier_3_contribution: Enable contribution to public knowledge
        encrypt_tier_0: Encrypt all tier 0 (personal) content
        encrypt_tier_1: Encrypt tier 1 (shared) content
        anonymize_tier_2: Anonymize identity for tier 2 (group)
        anonymize_tier_3: Anonymize identity for tier 3 (public)
        auto_backup: Automatically backup knowledge
        backup_interval: Backup interval in days
    """
    allow_tier_0_backup: bool = True
    allow_tier_1_sharing: bool = True
    allow_tier_2_contribution: bool = True
    allow_tier_3_contribution: bool = False  # Requires review
    encrypt_tier_0: bool = True
    encrypt_tier_1: bool = False
    anonymize_tier_2: bool = True
    anonymize_tier_3: bool = True
    auto_backup: bool = True
    backup_interval: int = 7  # days


@dataclass
class KnowledgeTransaction:
    """
    Record of a knowledge barter transaction.

    Attributes:
        id: Transaction ID
        from_user: User offering knowledge
        to_user: User receiving knowledge
        offered_knowledge_id: ID of knowledge being offered
        requested_knowledge_id: ID of knowledge being requested
        status: Transaction status (pending, accepted, rejected, completed)
        created_at: Transaction creation time
        completed_at: Transaction completion time
        notes: Additional transaction notes
    """
    id: str
    from_user: str
    to_user: str
    offered_knowledge_id: str
    requested_knowledge_id: Optional[str] = None
    status: str = "pending"  # pending, accepted, rejected, completed
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None


# Privacy tier descriptions for user display
TIER_DESCRIPTIONS = {
    KnowledgeTier.PERSONAL: {
        "name": "Personal",
        "description": "Private knowledge, encrypted, never shared automatically",
        "icon": "🔒",
        "color": "red"
    },
    KnowledgeTier.SHARED: {
        "name": "Shared",
        "description": "Explicitly shared with specific users you trust",
        "icon": "🤝",
        "color": "yellow"
    },
    KnowledgeTier.GROUP: {
        "name": "Group",
        "description": "Community knowledge, your identity is anonymized",
        "icon": "👥",
        "color": "green"
    },
    KnowledgeTier.PUBLIC: {
        "name": "Public",
        "description": "Global knowledge bank, read-only, curated content",
        "icon": "🌍",
        "color": "blue"
    }
}


# Default tags for knowledge categorization
DEFAULT_TAGS = {
    "survival": ["water", "shelter", "fire", "food", "signaling", "first-aid"],
    "skills": ["cooking", "building", "repair", "navigation", "communication"],
    "reference": ["math", "science", "history", "geography", "language"],
    "guides": ["how-to", "tutorial", "step-by-step", "beginner", "advanced"],
    "warnings": ["danger", "caution", "toxic", "avoid", "emergency"]
}

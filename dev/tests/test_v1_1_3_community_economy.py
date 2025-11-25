#!/usr/bin/env python3
"""
v1.1.3.6-8 - Community, Matching Engine, and Analytics Dashboard Test Suite

Tests the complete community-integrated economy system:

v1.1.3.6 - Community Integration (Tier 3):
1. Community Creation & Management
2. Location-Aware Discovery (LOCATE/TIZO integration)
3. Knowledge & Resource Sharing
4. RBAC & Privacy Rules
5. Community Health Metrics

v1.1.3.7 - What I Have vs What I Need Engine:
1. Skill/Resource Inventory Analysis
2. Mission/Project Needs Matching
3. Barter Partner Suggestions
4. Learning Path Recommendations
5. Gemini-Enhanced Matching

v1.1.3.8 - Economy Analytics Dashboard:
1. Trade Volume Tracking
2. Resource Scarcity Monitoring
3. Reputation Distribution Analysis
4. Fairness Metrics Visualization
5. Wizard Role Access Controls

Author: uDOS Development Team
Created: 2025-11-24
Version: 1.1.3.6-8
"""

import unittest
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple
import json


# ============================================================================
# v1.1.3.6 - COMMUNITY INTEGRATION (TIER 3)
# ============================================================================

class CommunityRole(Enum):
    """Community member roles"""
    OWNER = "owner"
    MODERATOR = "moderator"
    MEMBER = "member"
    GUEST = "guest"


class PrivacyLevel(Enum):
    """Content privacy levels"""
    PRIVATE = "private"      # Tier 1: User only
    SHARED = "shared"        # Tier 2: Trusted users
    COMMUNITY = "community"  # Tier 3: Community members
    PUBLIC = "public"        # Tier 4: Anyone


@dataclass
class Community:
    """Community/group structure"""
    community_id: str
    name: str
    description: str
    location: Optional[str] = None  # TIZO/city location
    owner_id: str = ""
    members: Dict[str, CommunityRole] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)
    privacy: PrivacyLevel = PrivacyLevel.COMMUNITY
    max_members: int = 100

    def add_member(self, user_id: str, role: CommunityRole = CommunityRole.MEMBER) -> bool:
        """Add a member to the community"""
        if len(self.members) >= self.max_members:
            return False
        self.members[user_id] = role
        return True

    def remove_member(self, user_id: str, remover_id: str) -> bool:
        """Remove a member (only owner/moderators can remove)"""
        if remover_id not in self.members:
            return False

        remover_role = self.members[remover_id]
        if remover_role not in [CommunityRole.OWNER, CommunityRole.MODERATOR]:
            return False

        if user_id == self.owner_id:
            return False  # Can't remove owner

        if user_id in self.members:
            del self.members[user_id]
            return True
        return False

    def get_member_role(self, user_id: str) -> Optional[CommunityRole]:
        """Get a member's role"""
        return self.members.get(user_id)

    def is_member(self, user_id: str) -> bool:
        """Check if user is a member"""
        return user_id in self.members


@dataclass
class SharedResource:
    """Resource shared within community"""
    resource_id: str
    community_id: str
    owner_id: str
    title: str
    description: str
    resource_type: str  # "knowledge", "tool", "skill", "guide"
    content: str
    privacy: PrivacyLevel
    created_at: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)

    def can_access(self, user_id: str, community: Community) -> bool:
        """Check if user can access this resource"""
        if self.privacy == PrivacyLevel.PUBLIC:
            return True
        if self.privacy == PrivacyLevel.PRIVATE:
            return user_id == self.owner_id
        if self.privacy == PrivacyLevel.COMMUNITY:
            return community.is_member(user_id)
        if self.privacy == PrivacyLevel.SHARED:
            # For Tier 2, would check trusted users list
            return user_id == self.owner_id or community.is_member(user_id)
        return False


class CommunityManager:
    """Manage communities and discovery"""

    def __init__(self):
        self.communities: Dict[str, Community] = {}
        self.resources: Dict[str, SharedResource] = {}
        self.community_counter = 0
        self.resource_counter = 0

    def create_community(
        self,
        name: str,
        description: str,
        owner_id: str,
        location: Optional[str] = None,
        tags: List[str] = None
    ) -> Community:
        """Create a new community"""
        self.community_counter += 1
        community_id = f"comm_{self.community_counter:06d}"

        community = Community(
            community_id=community_id,
            name=name,
            description=description,
            owner_id=owner_id,
            location=location,
            tags=tags or []
        )
        community.add_member(owner_id, CommunityRole.OWNER)

        self.communities[community_id] = community
        return community

    def join_community(self, community_id: str, user_id: str) -> bool:
        """Join a community"""
        community = self.communities.get(community_id)
        if not community:
            return False
        return community.add_member(user_id)

    def discover_by_location(self, location: str) -> List[Community]:
        """Find communities by location (TIZO/LOCATE integration)"""
        return [
            c for c in self.communities.values()
            if c.location and c.location.lower() == location.lower()
        ]

    def discover_by_tags(self, tags: List[str]) -> List[Community]:
        """Find communities by tags"""
        matching = []
        for community in self.communities.values():
            if any(tag in community.tags for tag in tags):
                matching.append(community)
        return matching

    def share_resource(
        self,
        community_id: str,
        owner_id: str,
        title: str,
        description: str,
        resource_type: str,
        content: str,
        privacy: PrivacyLevel = PrivacyLevel.COMMUNITY,
        tags: List[str] = None
    ) -> Optional[SharedResource]:
        """Share a resource with community"""
        community = self.communities.get(community_id)
        if not community or not community.is_member(owner_id):
            return None

        self.resource_counter += 1
        resource_id = f"res_{self.resource_counter:06d}"

        resource = SharedResource(
            resource_id=resource_id,
            community_id=community_id,
            owner_id=owner_id,
            title=title,
            description=description,
            resource_type=resource_type,
            content=content,
            privacy=privacy,
            tags=tags or []
        )

        self.resources[resource_id] = resource
        return resource

    def get_community_resources(
        self,
        community_id: str,
        user_id: str
    ) -> List[SharedResource]:
        """Get resources accessible to user in community"""
        community = self.communities.get(community_id)
        if not community:
            return []

        accessible = []
        for resource in self.resources.values():
            if resource.community_id == community_id:
                if resource.can_access(user_id, community):
                    accessible.append(resource)

        return accessible


# ============================================================================
# v1.1.3.7 - WHAT I HAVE VS WHAT I NEED ENGINE
# ============================================================================

@dataclass
class UserInventory:
    """User's skills, resources, and capabilities"""
    user_id: str
    skills: List[str] = field(default_factory=list)
    resources: Dict[str, int] = field(default_factory=dict)  # item -> quantity
    knowledge: List[str] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)

    def has_skill(self, skill: str) -> bool:
        """Check if user has a skill"""
        return skill.lower() in [s.lower() for s in self.skills]

    def has_resource(self, resource: str, quantity: int = 1) -> bool:
        """Check if user has enough of a resource"""
        return self.resources.get(resource, 0) >= quantity


@dataclass
class ProjectNeeds:
    """Requirements for a project or mission"""
    project_id: str
    name: str
    required_skills: List[str] = field(default_factory=list)
    required_resources: Dict[str, int] = field(default_factory=dict)
    required_knowledge: List[str] = field(default_factory=list)
    optional_skills: List[str] = field(default_factory=list)

    def calculate_readiness(self, inventory: UserInventory) -> float:
        """Calculate how ready user is for this project (0.0 to 1.0)"""
        total_requirements = 0
        met_requirements = 0

        # Check skills
        for skill in self.required_skills:
            total_requirements += 1
            if inventory.has_skill(skill):
                met_requirements += 1

        # Check resources
        for resource, qty in self.required_resources.items():
            total_requirements += 1
            if inventory.has_resource(resource, qty):
                met_requirements += 1

        # Check knowledge
        for knowledge in self.required_knowledge:
            total_requirements += 1
            if knowledge in inventory.knowledge:
                met_requirements += 1

        if total_requirements == 0:
            return 1.0

        return met_requirements / total_requirements


@dataclass
class MatchSuggestion:
    """Suggestion for barter partner or learning path"""
    suggestion_type: str  # "barter_partner", "learning_path", "resource_trade"
    priority: int  # 1 (highest) to 5 (lowest)
    description: str
    action: str
    target_user_id: Optional[str] = None
    required_items: List[str] = field(default_factory=list)
    confidence: float = 0.5  # 0.0 to 1.0


class MatchingEngine:
    """Intelligent 'What I Have vs What I Need' matching"""

    def __init__(self):
        self.inventories: Dict[str, UserInventory] = {}
        self.projects: Dict[str, ProjectNeeds] = {}

    def register_inventory(self, inventory: UserInventory):
        """Register a user's inventory"""
        self.inventories[inventory.user_id] = inventory

    def register_project(self, project: ProjectNeeds):
        """Register a project's needs"""
        self.projects[project.project_id] = project

    def analyze_gaps(self, user_id: str, project_id: str) -> Dict[str, List[str]]:
        """Analyze what user is missing for a project"""
        inventory = self.inventories.get(user_id)
        project = self.projects.get(project_id)

        if not inventory or not project:
            return {}

        gaps = {
            "skills": [],
            "resources": [],
            "knowledge": []
        }

        # Find missing skills
        for skill in project.required_skills:
            if not inventory.has_skill(skill):
                gaps["skills"].append(skill)

        # Find missing resources
        for resource, qty in project.required_resources.items():
            if not inventory.has_resource(resource, qty):
                needed = qty - inventory.resources.get(resource, 0)
                gaps["resources"].append(f"{resource} (need {needed})")

        # Find missing knowledge
        for knowledge in project.required_knowledge:
            if knowledge not in inventory.knowledge:
                gaps["knowledge"].append(knowledge)

        return gaps

    def suggest_barter_partners(
        self,
        user_id: str,
        needed_items: List[str]
    ) -> List[MatchSuggestion]:
        """Suggest users who might trade for needed items"""
        suggestions = []
        user_inventory = self.inventories.get(user_id)

        if not user_inventory:
            return suggestions

        for other_id, other_inventory in self.inventories.items():
            if other_id == user_id:
                continue

            # Check if other user has what we need
            has_needed = any(
                item in other_inventory.resources or
                item.lower() in [s.lower() for s in other_inventory.skills]
                for item in needed_items
            )

            if has_needed:
                # Calculate what we can offer
                can_offer = list(user_inventory.resources.keys()) + user_inventory.skills

                suggestion = MatchSuggestion(
                    suggestion_type="barter_partner",
                    priority=2,
                    description=f"User {other_id} has items you need",
                    action=f"Initiate trade with {other_id}",
                    target_user_id=other_id,
                    required_items=can_offer[:3],  # Show first 3 items
                    confidence=0.7
                )
                suggestions.append(suggestion)

        return suggestions

    def suggest_learning_paths(
        self,
        user_id: str,
        project_id: str
    ) -> List[MatchSuggestion]:
        """Suggest skills to learn for project readiness"""
        gaps = self.analyze_gaps(user_id, project_id)
        suggestions = []

        # Prioritize skills
        for i, skill in enumerate(gaps.get("skills", [])[:3]):
            suggestion = MatchSuggestion(
                suggestion_type="learning_path",
                priority=1,
                description=f"Learn {skill} to increase project readiness",
                action=f"Search knowledge base for {skill} tutorials",
                required_items=[skill],
                confidence=0.8
            )
            suggestions.append(suggestion)

        # Add knowledge gaps
        for knowledge in gaps.get("knowledge", [])[:2]:
            suggestion = MatchSuggestion(
                suggestion_type="learning_path",
                priority=2,
                description=f"Acquire knowledge: {knowledge}",
                action=f"Find community members teaching {knowledge}",
                required_items=[knowledge],
                confidence=0.6
            )
            suggestions.append(suggestion)

        return suggestions

    def suggest_resource_trades(
        self,
        user_id: str,
        project_id: str
    ) -> List[MatchSuggestion]:
        """Suggest resource trades needed for project"""
        gaps = self.analyze_gaps(user_id, project_id)
        suggestions = []

        for resource_info in gaps.get("resources", [])[:3]:
            suggestion = MatchSuggestion(
                suggestion_type="resource_trade",
                priority=3,
                description=f"Acquire {resource_info}",
                action=f"Search barter system for {resource_info}",
                required_items=[resource_info],
                confidence=0.5
            )
            suggestions.append(suggestion)

        return suggestions

    def get_readiness_score(self, user_id: str, project_id: str) -> float:
        """Get overall project readiness score"""
        inventory = self.inventories.get(user_id)
        project = self.projects.get(project_id)

        if not inventory or not project:
            return 0.0

        return project.calculate_readiness(inventory)


# ============================================================================
# v1.1.3.8 - ECONOMY ANALYTICS DASHBOARD
# ============================================================================

@dataclass
class TradeVolumeMetric:
    """Trade volume over time"""
    period: str  # "hour", "day", "week", "month"
    timestamp: datetime
    trade_count: int
    total_value: float = 0.0  # Estimated value
    unique_traders: int = 0


@dataclass
class ResourceScarcityMetric:
    """Resource scarcity tracking"""
    resource_name: str
    supply: int
    demand: int
    scarcity_score: float  # 0.0 (abundant) to 1.0 (scarce)
    trend: str  # "increasing", "stable", "decreasing"
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class ReputationDistribution:
    """Reputation distribution across users"""
    tier_0_25: int = 0   # Low reputation
    tier_26_50: int = 0  # Neutral
    tier_51_75: int = 0  # Good
    tier_76_100: int = 0 # Trusted
    average: float = 50.0
    median: float = 50.0


class EconomyDashboard:
    """Analytics dashboard for economy monitoring"""

    def __init__(self):
        self.trade_volumes: List[TradeVolumeMetric] = []
        self.scarcity_metrics: Dict[str, ResourceScarcityMetric] = {}
        self.reputation_snapshots: List[ReputationDistribution] = []
        self.alert_threshold_monopoly = 0.6
        self.alert_threshold_scarcity = 0.8

    def record_trade_volume(
        self,
        period: str,
        timestamp: datetime,
        trade_count: int,
        unique_traders: int
    ):
        """Record trade volume for a period"""
        metric = TradeVolumeMetric(
            period=period,
            timestamp=timestamp,
            trade_count=trade_count,
            unique_traders=unique_traders
        )
        self.trade_volumes.append(metric)

    def update_scarcity(
        self,
        resource_name: str,
        supply: int,
        demand: int
    ):
        """Update resource scarcity metrics"""
        if demand == 0:
            scarcity_score = 0.0
            trend = "stable"
        elif supply >= demand * 1.2:  # Abundant (20%+ surplus)
            scarcity_score = 0.0
            trend = "decreasing"
        elif supply >= demand:  # Adequate supply
            scarcity_score = 0.0
            trend = "stable"
        else:
            scarcity_score = 1.0 - (supply / demand)
            trend = "increasing" if scarcity_score > 0.5 else "stable"

        metric = ResourceScarcityMetric(
            resource_name=resource_name,
            supply=supply,
            demand=demand,
            scarcity_score=scarcity_score,
            trend=trend
        )
        self.scarcity_metrics[resource_name] = metric

    def record_reputation_snapshot(
        self,
        user_reputations: List[float]
    ):
        """Record reputation distribution snapshot"""
        dist = ReputationDistribution()

        for rep in user_reputations:
            if rep <= 25:
                dist.tier_0_25 += 1
            elif rep <= 50:
                dist.tier_26_50 += 1
            elif rep <= 75:
                dist.tier_51_75 += 1
            else:
                dist.tier_76_100 += 1

        if user_reputations:
            dist.average = sum(user_reputations) / len(user_reputations)
            sorted_reps = sorted(user_reputations)
            mid = len(sorted_reps) // 2
            dist.median = sorted_reps[mid]

        self.reputation_snapshots.append(dist)

    def get_trade_velocity(self, hours: int = 24) -> float:
        """Calculate recent trade velocity (trades per hour)"""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_trades = [
            tv for tv in self.trade_volumes
            if tv.timestamp >= cutoff
        ]

        if not recent_trades:
            return 0.0

        total_trades = sum(tv.trade_count for tv in recent_trades)
        return total_trades / hours

    def get_scarce_resources(self, threshold: float = 0.7) -> List[ResourceScarcityMetric]:
        """Get resources above scarcity threshold"""
        return [
            metric for metric in self.scarcity_metrics.values()
            if metric.scarcity_score >= threshold
        ]

    def get_health_score(self) -> Dict[str, any]:
        """Calculate overall economy health score"""
        score = 100.0
        issues = []

        # Check trade velocity (should be > 0)
        velocity = self.get_trade_velocity(24)
        if velocity < 1.0:
            score -= 20
            issues.append("Low trade activity")

        # Check scarcity issues
        scarce = self.get_scarce_resources(0.8)
        if len(scarce) > 3:
            score -= 15
            issues.append(f"{len(scarce)} resources critically scarce")

        # Check reputation distribution (should be balanced)
        if self.reputation_snapshots:
            latest = self.reputation_snapshots[-1]
            if latest.tier_0_25 > latest.tier_76_100 * 2:
                score -= 10
                issues.append("Too many low-reputation users")

        return {
            "score": max(0, score),
            "rating": "Healthy" if score >= 80 else "Fair" if score >= 60 else "Poor",
            "issues": issues,
            "velocity": velocity,
            "scarce_resources": len(self.get_scarce_resources(0.7))
        }

    def generate_alerts(self) -> List[Dict[str, str]]:
        """Generate alerts for Wizard role"""
        alerts = []

        # Scarcity alerts
        for metric in self.scarcity_metrics.values():
            if metric.scarcity_score >= self.alert_threshold_scarcity:
                alerts.append({
                    "type": "scarcity",
                    "severity": "high",
                    "message": f"Critical scarcity: {metric.resource_name} "
                              f"(supply: {metric.supply}, demand: {metric.demand})"
                })

        # Low activity alert
        velocity = self.get_trade_velocity(24)
        if velocity < 0.5:
            alerts.append({
                "type": "activity",
                "severity": "medium",
                "message": f"Low trade activity: {velocity:.2f} trades/hour"
            })

        # Reputation imbalance
        if self.reputation_snapshots:
            latest = self.reputation_snapshots[-1]
            if latest.tier_0_25 > 10:
                alerts.append({
                    "type": "reputation",
                    "severity": "medium",
                    "message": f"{latest.tier_0_25} users with low reputation"
                })

        return alerts


# ============================================================================
# TEST SUITE
# ============================================================================

class TestCommunityIntegration(unittest.TestCase):
    """Test v1.1.3.6 - Community Integration"""

    def test_create_community(self):
        """Test creating a community"""
        manager = CommunityManager()

        community = manager.create_community(
            name="Portland Preppers",
            description="Urban survival community",
            owner_id="user_alice",
            location="Portland, OR",
            tags=["survival", "urban", "prepping"]
        )

        self.assertIsNotNone(community)
        self.assertEqual(community.name, "Portland Preppers")
        self.assertTrue(community.is_member("user_alice"))
        self.assertEqual(community.get_member_role("user_alice"), CommunityRole.OWNER)

    def test_join_community(self):
        """Test joining a community"""
        manager = CommunityManager()

        community = manager.create_community(
            name="Tech Collective",
            description="Technology sharing",
            owner_id="user_bob"
        )

        success = manager.join_community(community.community_id, "user_charlie")
        self.assertTrue(success)
        self.assertTrue(community.is_member("user_charlie"))
        self.assertEqual(community.get_member_role("user_charlie"), CommunityRole.MEMBER)

    def test_location_discovery(self):
        """Test discovering communities by location"""
        manager = CommunityManager()

        manager.create_community(
            "Seattle Tech", "Tech community", "user_1",
            location="Seattle, WA"
        )
        manager.create_community(
            "Seattle Makers", "Maker space", "user_2",
            location="Seattle, WA"
        )
        manager.create_community(
            "Portland Group", "Portland based", "user_3",
            location="Portland, OR"
        )

        seattle_communities = manager.discover_by_location("Seattle, WA")
        self.assertEqual(len(seattle_communities), 2)

    def test_tag_discovery(self):
        """Test discovering communities by tags"""
        manager = CommunityManager()

        manager.create_community(
            "Survival Group", "Survival skills", "user_1",
            tags=["survival", "wilderness"]
        )
        manager.create_community(
            "Urban Survival", "City survival", "user_2",
            tags=["survival", "urban"]
        )
        manager.create_community(
            "Cooking Club", "Food prep", "user_3",
            tags=["cooking", "food"]
        )

        survival_communities = manager.discover_by_tags(["survival"])
        self.assertEqual(len(survival_communities), 2)

    def test_share_resource(self):
        """Test sharing a resource with community"""
        manager = CommunityManager()

        community = manager.create_community(
            "Knowledge Sharers", "Share knowledge", "user_alice"
        )
        manager.join_community(community.community_id, "user_bob")

        resource = manager.share_resource(
            community_id=community.community_id,
            owner_id="user_alice",
            title="Water Purification Guide",
            description="How to purify water",
            resource_type="knowledge",
            content="Step 1: Boil water...",
            privacy=PrivacyLevel.COMMUNITY,
            tags=["water", "survival"]
        )

        self.assertIsNotNone(resource)
        self.assertEqual(resource.title, "Water Purification Guide")

    def test_resource_access_control(self):
        """Test resource access based on privacy level"""
        manager = CommunityManager()

        community = manager.create_community(
            "Private Group", "Test group", "user_alice"
        )
        manager.join_community(community.community_id, "user_bob")

        # Community-level resource
        community_resource = manager.share_resource(
            community_id=community.community_id,
            owner_id="user_alice",
            title="Community Resource",
            description="For members",
            resource_type="knowledge",
            content="Content",
            privacy=PrivacyLevel.COMMUNITY
        )

        # Member can access
        self.assertTrue(community_resource.can_access("user_bob", community))

        # Non-member cannot access
        self.assertFalse(community_resource.can_access("user_outsider", community))

        # Private resource
        private_resource = manager.share_resource(
            community_id=community.community_id,
            owner_id="user_alice",
            title="Private Resource",
            description="Owner only",
            resource_type="knowledge",
            content="Secret",
            privacy=PrivacyLevel.PRIVATE
        )

        # Only owner can access
        self.assertTrue(private_resource.can_access("user_alice", community))
        self.assertFalse(private_resource.can_access("user_bob", community))

    def test_get_community_resources(self):
        """Test retrieving accessible community resources"""
        manager = CommunityManager()

        community = manager.create_community(
            "Resource Hub", "Share everything", "user_alice"
        )
        manager.join_community(community.community_id, "user_bob")

        # Add multiple resources with different privacy levels
        manager.share_resource(
            community.community_id, "user_alice", "Public Guide", "Public",
            "knowledge", "Content1", PrivacyLevel.PUBLIC
        )
        manager.share_resource(
            community.community_id, "user_alice", "Community Guide", "Members only",
            "knowledge", "Content2", PrivacyLevel.COMMUNITY
        )
        manager.share_resource(
            community.community_id, "user_alice", "Private Notes", "Owner only",
            "knowledge", "Content3", PrivacyLevel.PRIVATE
        )

        # Bob should see public + community resources (2)
        bob_resources = manager.get_community_resources(community.community_id, "user_bob")
        self.assertEqual(len(bob_resources), 2)

        # Alice should see all 3
        alice_resources = manager.get_community_resources(community.community_id, "user_alice")
        self.assertEqual(len(alice_resources), 3)

    def test_remove_member(self):
        """Test removing a community member"""
        manager = CommunityManager()

        community = manager.create_community(
            "Test Community", "Test", "user_owner"
        )
        community.add_member("user_mod", CommunityRole.MODERATOR)
        community.add_member("user_member", CommunityRole.MEMBER)

        # Moderator can remove member
        success = community.remove_member("user_member", "user_mod")
        self.assertTrue(success)
        self.assertFalse(community.is_member("user_member"))

        # Cannot remove owner
        success = community.remove_member("user_owner", "user_mod")
        self.assertFalse(success)

    def test_max_members_limit(self):
        """Test community member limit"""
        manager = CommunityManager()

        community = manager.create_community(
            "Small Group", "Limited size", "user_alice"
        )
        community.max_members = 3

        # Owner + 2 more should work
        self.assertTrue(community.add_member("user_1"))
        self.assertTrue(community.add_member("user_2"))

        # 4th member should fail (owner + 3)
        self.assertFalse(community.add_member("user_3"))


class TestMatchingEngine(unittest.TestCase):
    """Test v1.1.3.7 - What I Have vs What I Need Engine"""

    def test_inventory_creation(self):
        """Test creating user inventory"""
        inventory = UserInventory(
            user_id="user_alice",
            skills=["programming", "gardening"],
            resources={"wood": 20, "nails": 100},
            knowledge=["Python tutorial", "Gardening basics"]
        )

        self.assertTrue(inventory.has_skill("programming"))
        self.assertTrue(inventory.has_resource("wood", 10))
        self.assertFalse(inventory.has_resource("wood", 30))

    def test_project_readiness(self):
        """Test calculating project readiness"""
        inventory = UserInventory(
            user_id="user_bob",
            skills=["carpentry", "welding"],
            resources={"wood": 50, "metal": 20},
            knowledge=["Workshop safety"]
        )

        project = ProjectNeeds(
            project_id="proj_001",
            name="Build shed",
            required_skills=["carpentry"],
            required_resources={"wood": 30, "nails": 200},
            required_knowledge=["Workshop safety"]
        )

        readiness = project.calculate_readiness(inventory)
        # Has carpentry (1/1), has wood (1/1), missing nails (0/1), has knowledge (1/1)
        # = 3/4 = 0.75
        self.assertAlmostEqual(readiness, 0.75, places=2)

    def test_analyze_gaps(self):
        """Test analyzing what's missing for a project"""
        engine = MatchingEngine()

        inventory = UserInventory(
            user_id="user_charlie",
            skills=["programming"],
            resources={"laptop": 1},
            knowledge=[]
        )
        engine.register_inventory(inventory)

        project = ProjectNeeds(
            project_id="proj_web",
            name="Build website",
            required_skills=["programming", "design"],
            required_resources={"laptop": 1, "hosting": 1},
            required_knowledge=["HTML basics", "CSS basics"]
        )
        engine.register_project(project)

        gaps = engine.analyze_gaps("user_charlie", "proj_web")

        self.assertIn("design", gaps["skills"])
        self.assertIn("hosting (need 1)", gaps["resources"])
        self.assertEqual(len(gaps["knowledge"]), 2)

    def test_suggest_learning_paths(self):
        """Test suggesting skills to learn"""
        engine = MatchingEngine()

        inventory = UserInventory(
            user_id="user_dave",
            skills=[],
            resources={},
            knowledge=[]
        )
        engine.register_inventory(inventory)

        project = ProjectNeeds(
            project_id="proj_garden",
            name="Start garden",
            required_skills=["gardening", "composting"],
            required_knowledge=["Soil preparation"]
        )
        engine.register_project(project)

        suggestions = engine.suggest_learning_paths("user_dave", "proj_garden")

        self.assertGreater(len(suggestions), 0)
        self.assertTrue(any(s.suggestion_type == "learning_path" for s in suggestions))

    def test_suggest_barter_partners(self):
        """Test suggesting users to trade with"""
        engine = MatchingEngine()

        # User needs nails
        inventory1 = UserInventory(
            user_id="user_eve",
            skills=[],
            resources={"wood": 100}
        )
        engine.register_inventory(inventory1)

        # User has nails
        inventory2 = UserInventory(
            user_id="user_frank",
            skills=[],
            resources={"nails": 500}
        )
        engine.register_inventory(inventory2)

        suggestions = engine.suggest_barter_partners("user_eve", ["nails"])

        self.assertEqual(len(suggestions), 1)
        self.assertEqual(suggestions[0].target_user_id, "user_frank")
        self.assertEqual(suggestions[0].suggestion_type, "barter_partner")

    def test_suggest_resource_trades(self):
        """Test suggesting resource trades"""
        engine = MatchingEngine()

        inventory = UserInventory(
            user_id="user_grace",
            skills=["welding"],
            resources={}
        )
        engine.register_inventory(inventory)

        project = ProjectNeeds(
            project_id="proj_fence",
            name="Build fence",
            required_resources={"metal_posts": 10, "wire": 100}
        )
        engine.register_project(project)

        suggestions = engine.suggest_resource_trades("user_grace", "proj_fence")

        self.assertGreater(len(suggestions), 0)
        self.assertTrue(all(s.suggestion_type == "resource_trade" for s in suggestions))

    def test_get_readiness_score(self):
        """Test getting overall readiness score"""
        engine = MatchingEngine()

        inventory = UserInventory(
            user_id="user_henry",
            skills=["coding"],
            resources={"computer": 1},
            knowledge=["Git basics"]
        )
        engine.register_inventory(inventory)

        project = ProjectNeeds(
            project_id="proj_app",
            name="Build app",
            required_skills=["coding"],
            required_resources={"computer": 1},
            required_knowledge=["Git basics"]
        )
        engine.register_project(project)

        score = engine.get_readiness_score("user_henry", "proj_app")
        self.assertEqual(score, 1.0)  # Fully ready


class TestEconomyDashboard(unittest.TestCase):
    """Test v1.1.3.8 - Economy Analytics Dashboard"""

    def test_record_trade_volume(self):
        """Test recording trade volume"""
        dashboard = EconomyDashboard()

        dashboard.record_trade_volume(
            period="hour",
            timestamp=datetime.now(),
            trade_count=15,
            unique_traders=8
        )

        self.assertEqual(len(dashboard.trade_volumes), 1)
        self.assertEqual(dashboard.trade_volumes[0].trade_count, 15)

    def test_update_scarcity(self):
        """Test updating resource scarcity"""
        dashboard = EconomyDashboard()

        # Abundant resource
        dashboard.update_scarcity("water", supply=100, demand=50)
        self.assertEqual(dashboard.scarcity_metrics["water"].scarcity_score, 0.0)

        # Scarce resource
        dashboard.update_scarcity("medicine", supply=10, demand=50)
        self.assertGreater(dashboard.scarcity_metrics["medicine"].scarcity_score, 0.5)

    def test_reputation_snapshot(self):
        """Test recording reputation distribution"""
        dashboard = EconomyDashboard()

        reputations = [20, 45, 60, 75, 80, 90, 95]
        dashboard.record_reputation_snapshot(reputations)

        snapshot = dashboard.reputation_snapshots[0]
        self.assertEqual(snapshot.tier_0_25, 1)  # 20
        self.assertEqual(snapshot.tier_26_50, 1)  # 45
        self.assertEqual(snapshot.tier_51_75, 2)  # 60, 75
        self.assertEqual(snapshot.tier_76_100, 3)  # 80, 90, 95

    def test_get_trade_velocity(self):
        """Test calculating trade velocity"""
        dashboard = EconomyDashboard()

        now = datetime.now()
        # Record 20 trades over last 10 hours
        for i in range(10):
            dashboard.record_trade_volume(
                period="hour",
                timestamp=now - timedelta(hours=i),
                trade_count=2,
                unique_traders=2
            )

        velocity = dashboard.get_trade_velocity(hours=24)
        # 20 trades / 24 hours = 0.833...
        self.assertAlmostEqual(velocity, 20/24, places=2)

    def test_get_scarce_resources(self):
        """Test finding scarce resources"""
        dashboard = EconomyDashboard()

        dashboard.update_scarcity("common_item", 1000, 500)
        dashboard.update_scarcity("rare_item", 5, 50)
        dashboard.update_scarcity("critical_item", 1, 100)

        scarce = dashboard.get_scarce_resources(threshold=0.7)

        # Should find rare_item and critical_item
        self.assertEqual(len(scarce), 2)

    def test_health_score_healthy(self):
        """Test health score for healthy economy"""
        dashboard = EconomyDashboard()

        # Good trade activity
        now = datetime.now()
        for i in range(10):
            dashboard.record_trade_volume(
                "hour", now - timedelta(hours=i), 5, 5
            )

        # Balanced reputation
        dashboard.record_reputation_snapshot([60, 65, 70, 75, 80] * 4)

        # No critical scarcity
        dashboard.update_scarcity("item1", 100, 50)
        dashboard.update_scarcity("item2", 80, 60)

        health = dashboard.get_health_score()

        self.assertGreaterEqual(health["score"], 80)
        self.assertEqual(health["rating"], "Healthy")

    def test_health_score_poor(self):
        """Test health score for struggling economy"""
        dashboard = EconomyDashboard()

        # Low trade activity
        dashboard.record_trade_volume(
            "hour", datetime.now(), 0, 0
        )

        # Many low-reputation users
        dashboard.record_reputation_snapshot([10, 15, 20] * 10)

        # Critical scarcity
        for i in range(5):
            dashboard.update_scarcity(f"item{i}", 1, 100)

        health = dashboard.get_health_score()

        self.assertLess(health["score"], 60)
        self.assertEqual(health["rating"], "Poor")

    def test_generate_alerts(self):
        """Test generating alerts for Wizard role"""
        dashboard = EconomyDashboard()

        # Create scarcity alert
        dashboard.update_scarcity("medicine", 2, 100)

        # Create low activity
        dashboard.record_trade_volume("hour", datetime.now(), 0, 0)

        # Create reputation issue
        dashboard.record_reputation_snapshot([10, 15, 20] * 5)

        alerts = dashboard.generate_alerts()

        self.assertGreater(len(alerts), 0)
        self.assertTrue(any(a["type"] == "scarcity" for a in alerts))
        self.assertTrue(any(a["type"] == "activity" for a in alerts))
        self.assertTrue(any(a["type"] == "reputation" for a in alerts))

    def test_scarcity_trend_detection(self):
        """Test detecting scarcity trends"""
        dashboard = EconomyDashboard()

        # Increasing scarcity
        dashboard.update_scarcity("trending_item", 10, 50)
        self.assertEqual(dashboard.scarcity_metrics["trending_item"].trend, "increasing")

        # Stable (low scarcity)
        dashboard.update_scarcity("stable_item", 100, 100)
        self.assertEqual(dashboard.scarcity_metrics["stable_item"].trend, "stable")

        # Decreasing (abundance)
        dashboard.update_scarcity("abundant_item", 200, 50)
        self.assertEqual(dashboard.scarcity_metrics["abundant_item"].trend, "decreasing")


class TestIntegration(unittest.TestCase):
    """Test complete community-economy integration"""

    def test_community_based_matching(self):
        """Test finding barter partners within community"""
        comm_manager = CommunityManager()
        engine = MatchingEngine()

        # Create community
        community = comm_manager.create_community(
            "Tool Share", "Share tools and skills", "user_alice",
            location="Seattle, WA"
        )
        comm_manager.join_community(community.community_id, "user_bob")
        comm_manager.join_community(community.community_id, "user_charlie")

        # Set up inventories
        alice_inv = UserInventory(
            user_id="user_alice",
            skills=["carpentry"],
            resources={"saw": 1, "hammer": 2}
        )
        bob_inv = UserInventory(
            user_id="user_bob",
            skills=["plumbing"],
            resources={"wrench": 3, "pipes": 10}
        )
        charlie_inv = UserInventory(
            user_id="user_charlie",
            skills=["welding"],
            resources={"torch": 1, "metal": 50}
        )

        engine.register_inventory(alice_inv)
        engine.register_inventory(bob_inv)
        engine.register_inventory(charlie_inv)

        # Alice needs welding equipment
        suggestions = engine.suggest_barter_partners("user_alice", ["torch", "metal"])

        # Should suggest Charlie (community member)
        self.assertEqual(len(suggestions), 1)
        self.assertEqual(suggestions[0].target_user_id, "user_charlie")

    def test_dashboard_monitoring_community_economy(self):
        """Test dashboard monitoring community trading activity"""
        dashboard = EconomyDashboard()

        # Simulate trading activity over time
        now = datetime.now()
        for hour in range(24):
            timestamp = now - timedelta(hours=hour)
            trade_count = 3 if hour < 12 else 1  # Activity declining
            dashboard.record_trade_volume("hour", timestamp, trade_count, trade_count)

        # Update scarcity based on community trading
        dashboard.update_scarcity("tools", 50, 20)   # Abundant
        dashboard.update_scarcity("food", 30, 40)    # Slightly scarce
        dashboard.update_scarcity("medicine", 5, 50) # Very scarce

        # Record reputation distribution
        dashboard.record_reputation_snapshot([45, 55, 60, 70, 75, 80, 85, 90])

        # Get health assessment
        health = dashboard.get_health_score()

        self.assertIn("rating", health)
        self.assertGreater(health["velocity"], 0)

        # Check for alerts
        alerts = dashboard.generate_alerts()
        self.assertTrue(any(a["type"] == "scarcity" for a in alerts if "medicine" in a["message"]))


if __name__ == "__main__":
    unittest.main()

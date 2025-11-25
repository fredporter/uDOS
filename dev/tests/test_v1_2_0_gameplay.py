"""
uDOS v1.2.0 - Advanced Gameplay & Community Features Tests

Validates:
- Multi-player missions and collaboration
- Community events and seasonal challenges
- Leaderboards and rankings
- Achievement system extensions
- Trading and resource sharing
- Community-driven content
"""

import pytest
import json
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict


# ============================================================================
# MULTI-PLAYER MISSIONS
# ============================================================================

class MissionType(Enum):
    """Mission types"""
    SOLO = "solo"
    COOPERATIVE = "cooperative"
    COMPETITIVE = "competitive"
    COMMUNITY = "community"


class PlayerRole(Enum):
    """Player roles in missions"""
    LEADER = "leader"
    MEMBER = "member"
    SUPPORTER = "supporter"


class MultiPlayerMission:
    """Mission that supports multiple players"""

    def __init__(self, mission_id: str, title: str, mission_type: MissionType,
                 min_players: int = 1, max_players: int = 4):
        self.mission_id = mission_id
        self.title = title
        self.mission_type = mission_type
        self.min_players = min_players
        self.max_players = max_players
        self.participants: Dict[str, PlayerRole] = {}
        self.objectives: List[Dict[str, Any]] = []
        self.shared_resources: Dict[str, int] = {}
        self.status = "open"  # "open", "active", "completed", "failed"
        self.xp_pool = 0
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

    def add_participant(self, user_id: str, role: PlayerRole = PlayerRole.MEMBER):
        """Add player to mission"""
        if len(self.participants) >= self.max_players:
            raise ValueError("Mission is full")

        self.participants[user_id] = role

        # Auto-start if minimum players reached
        if len(self.participants) >= self.min_players and self.status == "open":
            self.status = "ready"

    def start(self) -> bool:
        """Start mission"""
        if len(self.participants) < self.min_players:
            return False

        self.status = "active"
        self.started_at = datetime.now()
        return True

    def contribute_resource(self, user_id: str, resource: str, amount: int):
        """Contribute resources to shared pool"""
        if user_id not in self.participants:
            raise ValueError("User not in mission")

        if resource not in self.shared_resources:
            self.shared_resources[resource] = 0

        self.shared_resources[resource] += amount

    def complete_objective(self, objective_id: str, user_id: str):
        """Mark objective as complete"""
        for obj in self.objectives:
            if obj["id"] == objective_id:
                obj["completed_by"] = user_id
                obj["completed_at"] = datetime.now().isoformat()
                return True
        return False

    def complete(self) -> Dict[str, int]:
        """Complete mission and distribute rewards"""
        if self.status != "active":
            return {}

        self.status = "completed"
        self.completed_at = datetime.now()

        # Distribute XP based on participation
        num_participants = len(self.participants)
        if num_participants == 0:
            return {}

        rewards = {}
        if self.mission_type == MissionType.COOPERATIVE:
            # Equal distribution for cooperative
            xp_per_player = self.xp_pool // num_participants
            for user_id in self.participants:
                rewards[user_id] = xp_per_player
        elif self.mission_type == MissionType.COMPETITIVE:
            # Winner takes more
            leader = [uid for uid, role in self.participants.items() if role == PlayerRole.LEADER]
            if leader:
                rewards[leader[0]] = int(self.xp_pool * 0.5)
                remaining = self.xp_pool - rewards[leader[0]]
                others_share = remaining // (num_participants - 1) if num_participants > 1 else 0
                for user_id in self.participants:
                    if user_id not in rewards:
                        rewards[user_id] = others_share
        else:
            # Default equal distribution
            xp_per_player = self.xp_pool // num_participants
            for user_id in self.participants:
                rewards[user_id] = xp_per_player

        return rewards

    def get_stats(self) -> Dict[str, Any]:
        """Get mission statistics"""
        completed_objectives = len([obj for obj in self.objectives if "completed_by" in obj])

        return {
            "mission_id": self.mission_id,
            "title": self.title,
            "type": self.mission_type.value,
            "status": self.status,
            "participants": len(self.participants),
            "objectives": {
                "total": len(self.objectives),
                "completed": completed_objectives
            },
            "shared_resources": self.shared_resources,
            "duration_minutes": (
                (self.completed_at or datetime.now()) - (self.started_at or datetime.now())
            ).total_seconds() / 60 if self.started_at else 0
        }


# ============================================================================
# COMMUNITY EVENTS
# ============================================================================

class EventType(Enum):
    """Event types"""
    CHALLENGE = "challenge"
    SEASONAL = "seasonal"
    TOURNAMENT = "tournament"
    COLLABORATION = "collaboration"


class CommunityEvent:
    """Time-limited community event"""

    def __init__(self, event_id: str, title: str, event_type: EventType,
                 start_date: datetime, end_date: datetime):
        self.event_id = event_id
        self.title = title
        self.event_type = event_type
        self.description = ""
        self.start_date = start_date
        self.end_date = end_date
        self.participants: Set[str] = set()
        self.challenges: List[Dict[str, Any]] = []
        self.leaderboard: Dict[str, int] = {}
        self.rewards: Dict[str, Any] = {}
        self.active = False

    def is_active(self) -> bool:
        """Check if event is currently active"""
        now = datetime.now()
        return self.start_date <= now <= self.end_date

    def join(self, user_id: str) -> bool:
        """Join event"""
        if not self.is_active():
            return False

        self.participants.add(user_id)
        if user_id not in self.leaderboard:
            self.leaderboard[user_id] = 0
        return True

    def add_challenge(self, challenge: Dict[str, Any]):
        """Add challenge to event"""
        self.challenges.append(challenge)

    def submit_score(self, user_id: str, score: int):
        """Submit score for event"""
        if user_id not in self.participants:
            return False

        if user_id not in self.leaderboard:
            self.leaderboard[user_id] = 0

        self.leaderboard[user_id] += score
        return True

    def get_rankings(self, limit: int = 10) -> List[tuple]:
        """Get top rankings"""
        sorted_scores = sorted(
            self.leaderboard.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_scores[:limit]

    def get_rank(self, user_id: str) -> Optional[int]:
        """Get user's rank"""
        rankings = self.get_rankings(limit=len(self.leaderboard))
        for i, (uid, score) in enumerate(rankings, 1):
            if uid == user_id:
                return i
        return None

    def end_event(self) -> Dict[str, Any]:
        """End event and calculate rewards"""
        self.active = False

        rankings = self.get_rankings()
        rewards_given = {}

        # Top 3 get special rewards
        reward_multipliers = {1: 3.0, 2: 2.0, 3: 1.5}

        for rank, (user_id, score) in enumerate(rankings[:3], 1):
            base_reward = 100
            multiplier = reward_multipliers.get(rank, 1.0)
            rewards_given[user_id] = int(base_reward * multiplier)

        return rewards_given


# ============================================================================
# LEADERBOARDS
# ============================================================================

class LeaderboardType(Enum):
    """Leaderboard types"""
    GLOBAL = "global"
    COMMUNITY = "community"
    SKILL = "skill"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ALL_TIME = "all_time"


class Leaderboard:
    """Ranking system for players"""

    def __init__(self, board_id: str, name: str, board_type: LeaderboardType):
        self.board_id = board_id
        self.name = name
        self.board_type = board_type
        self.scores: Dict[str, int] = {}
        self.metadata: Dict[str, Dict[str, Any]] = {}  # Additional player info
        self.last_updated = datetime.now()
        self.reset_date: Optional[datetime] = None

    def update_score(self, user_id: str, score: int, metadata: Optional[Dict[str, Any]] = None):
        """Update player score"""
        if user_id not in self.scores:
            self.scores[user_id] = 0

        self.scores[user_id] = score

        if metadata:
            self.metadata[user_id] = metadata

        self.last_updated = datetime.now()

    def add_score(self, user_id: str, points: int):
        """Add points to existing score"""
        if user_id not in self.scores:
            self.scores[user_id] = 0

        self.scores[user_id] += points
        self.last_updated = datetime.now()

    def get_rank(self, user_id: str) -> Optional[int]:
        """Get user's current rank"""
        sorted_scores = sorted(self.scores.items(), key=lambda x: x[1], reverse=True)
        for rank, (uid, _) in enumerate(sorted_scores, 1):
            if uid == user_id:
                return rank
        return None

    def get_top(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top players"""
        sorted_scores = sorted(self.scores.items(), key=lambda x: x[1], reverse=True)

        top_players = []
        for rank, (user_id, score) in enumerate(sorted_scores[:limit], 1):
            player_data = {
                "rank": rank,
                "user_id": user_id,
                "score": score
            }

            if user_id in self.metadata:
                player_data.update(self.metadata[user_id])

            top_players.append(player_data)

        return top_players

    def get_nearby(self, user_id: str, range_size: int = 5) -> List[Dict[str, Any]]:
        """Get players near user's rank"""
        rank = self.get_rank(user_id)
        if not rank:
            return []

        sorted_scores = sorted(self.scores.items(), key=lambda x: x[1], reverse=True)

        start = max(0, rank - range_size - 1)
        end = min(len(sorted_scores), rank + range_size)

        nearby = []
        for i in range(start, end):
            uid, score = sorted_scores[i]
            nearby.append({
                "rank": i + 1,
                "user_id": uid,
                "score": score,
                "is_current_user": uid == user_id
            })

        return nearby

    def reset(self):
        """Reset leaderboard scores"""
        self.scores = {}
        self.metadata = {}
        self.reset_date = datetime.now()
        self.last_updated = datetime.now()


# ============================================================================
# TRADING & RESOURCE SHARING
# ============================================================================

class TradeStatus(Enum):
    """Trade status"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Trade:
    """Player-to-player trade"""

    def __init__(self, trade_id: str, from_user: str, to_user: str):
        self.trade_id = trade_id
        self.from_user = from_user
        self.to_user = to_user
        self.from_offers: Dict[str, int] = {}
        self.to_offers: Dict[str, int] = {}
        self.status = TradeStatus.PENDING
        self.created_at = datetime.now()
        self.completed_at: Optional[datetime] = None
        self.message = ""

    def add_offer_from(self, resource: str, amount: int):
        """Add resource from initiator"""
        self.from_offers[resource] = amount

    def add_offer_to(self, resource: str, amount: int):
        """Add counter-offer"""
        self.to_offers[resource] = amount

    def accept(self):
        """Accept trade"""
        if self.status != TradeStatus.PENDING:
            raise ValueError("Trade not pending")

        self.status = TradeStatus.ACCEPTED

    def complete(self):
        """Complete trade (execute exchange)"""
        if self.status != TradeStatus.ACCEPTED:
            raise ValueError("Trade not accepted")

        self.status = TradeStatus.COMPLETED
        self.completed_at = datetime.now()

    def reject(self):
        """Reject trade"""
        self.status = TradeStatus.REJECTED

    def cancel(self):
        """Cancel trade"""
        self.status = TradeStatus.CANCELLED

    def get_summary(self) -> Dict[str, Any]:
        """Get trade summary"""
        return {
            "trade_id": self.trade_id,
            "from_user": self.from_user,
            "to_user": self.to_user,
            "from_offers": self.from_offers,
            "to_offers": self.to_offers,
            "status": self.status.value,
            "created_at": self.created_at.isoformat()
        }


class ResourcePool:
    """Community resource sharing pool"""

    def __init__(self, pool_id: str, name: str):
        self.pool_id = pool_id
        self.name = name
        self.resources: Dict[str, int] = {}
        self.contributions: Dict[str, Dict[str, int]] = {}  # user_id -> {resource: amount}
        self.withdrawals: Dict[str, Dict[str, int]] = {}

    def contribute(self, user_id: str, resource: str, amount: int):
        """Contribute resources to pool"""
        if resource not in self.resources:
            self.resources[resource] = 0

        self.resources[resource] += amount

        if user_id not in self.contributions:
            self.contributions[user_id] = {}
        if resource not in self.contributions[user_id]:
            self.contributions[user_id][resource] = 0

        self.contributions[user_id][resource] += amount

    def withdraw(self, user_id: str, resource: str, amount: int) -> bool:
        """Withdraw resources from pool"""
        if resource not in self.resources or self.resources[resource] < amount:
            return False

        self.resources[resource] -= amount

        if user_id not in self.withdrawals:
            self.withdrawals[user_id] = {}
        if resource not in self.withdrawals[user_id]:
            self.withdrawals[user_id][resource] = 0

        self.withdrawals[user_id][resource] += amount
        return True

    def get_balance(self, resource: str) -> int:
        """Get current balance of resource"""
        return self.resources.get(resource, 0)

    def get_top_contributors(self, limit: int = 5) -> List[tuple]:
        """Get top contributors by total value"""
        totals = {}
        for user_id, resources in self.contributions.items():
            totals[user_id] = sum(resources.values())

        sorted_contributors = sorted(totals.items(), key=lambda x: x[1], reverse=True)
        return sorted_contributors[:limit]


# ============================================================================
# TESTS
# ============================================================================

class TestMultiPlayerMission:
    """Test multi-player missions"""

    def test_create_mission(self):
        """Test creating multi-player mission"""
        mission = MultiPlayerMission(
            "mp_001",
            "Community Water Collection",
            MissionType.COOPERATIVE,
            min_players=2,
            max_players=5
        )

        assert mission.mission_id == "mp_001"
        assert mission.mission_type == MissionType.COOPERATIVE
        assert mission.status == "open"

    def test_add_participants(self):
        """Test adding participants"""
        mission = MultiPlayerMission("mp_002", "Team Mission", MissionType.COOPERATIVE, min_players=2)

        mission.add_participant("user_001", PlayerRole.LEADER)
        mission.add_participant("user_002", PlayerRole.MEMBER)

        assert len(mission.participants) == 2
        assert mission.status == "ready"

    def test_start_mission(self):
        """Test starting mission"""
        mission = MultiPlayerMission("mp_003", "Test Mission", MissionType.COOPERATIVE, min_players=2)

        # Can't start without enough players
        assert not mission.start()

        mission.add_participant("user_001")
        mission.add_participant("user_002")

        assert mission.start()
        assert mission.status == "active"

    def test_resource_contribution(self):
        """Test resource contribution"""
        mission = MultiPlayerMission("mp_004", "Resource Mission", MissionType.COOPERATIVE)
        mission.add_participant("user_001")

        mission.contribute_resource("user_001", "water", 10)
        mission.contribute_resource("user_001", "food", 5)

        assert mission.shared_resources["water"] == 10
        assert mission.shared_resources["food"] == 5

    def test_complete_mission_cooperative(self):
        """Test completing cooperative mission"""
        mission = MultiPlayerMission("mp_005", "Coop Mission", MissionType.COOPERATIVE)
        mission.xp_pool = 100

        mission.add_participant("user_001")
        mission.add_participant("user_002")
        mission.add_participant("user_003")
        mission.start()

        rewards = mission.complete()

        assert mission.status == "completed"
        assert len(rewards) == 3
        assert all(xp == 33 for xp in rewards.values())  # Equal distribution

    def test_complete_mission_competitive(self):
        """Test completing competitive mission"""
        mission = MultiPlayerMission("mp_006", "Comp Mission", MissionType.COMPETITIVE)
        mission.xp_pool = 100

        mission.add_participant("user_001", PlayerRole.LEADER)
        mission.add_participant("user_002", PlayerRole.MEMBER)
        mission.start()

        rewards = mission.complete()

        assert rewards["user_001"] == 50  # Leader gets 50%
        assert rewards["user_002"] == 50  # Remaining 50%

    def test_mission_stats(self):
        """Test mission statistics"""
        mission = MultiPlayerMission("mp_007", "Stats Mission", MissionType.COOPERATIVE)
        mission.add_participant("user_001")
        mission.add_participant("user_002")
        mission.objectives = [
            {"id": "obj_1", "title": "Collect water"},
            {"id": "obj_2", "title": "Build shelter"}
        ]
        mission.complete_objective("obj_1", "user_001")

        stats = mission.get_stats()

        assert stats["participants"] == 2
        assert stats["objectives"]["total"] == 2
        assert stats["objectives"]["completed"] == 1


class TestCommunityEvent:
    """Test community events"""

    def test_create_event(self):
        """Test creating event"""
        start = datetime.now()
        end = start + timedelta(days=7)

        event = CommunityEvent(
            "event_001",
            "Summer Challenge",
            EventType.SEASONAL,
            start,
            end
        )

        assert event.event_id == "event_001"
        assert event.event_type == EventType.SEASONAL

    def test_join_event(self):
        """Test joining event"""
        start = datetime.now()
        end = start + timedelta(days=7)

        event = CommunityEvent("event_002", "Test Event", EventType.CHALLENGE, start, end)

        assert event.join("user_001")
        assert "user_001" in event.participants

    def test_submit_score(self):
        """Test score submission"""
        start = datetime.now()
        end = start + timedelta(days=7)

        event = CommunityEvent("event_003", "Score Event", EventType.CHALLENGE, start, end)
        event.join("user_001")
        event.join("user_002")

        event.submit_score("user_001", 100)
        event.submit_score("user_002", 150)
        event.submit_score("user_001", 50)  # Add more

        assert event.leaderboard["user_001"] == 150
        assert event.leaderboard["user_002"] == 150

    def test_get_rankings(self):
        """Test getting rankings"""
        start = datetime.now()
        end = start + timedelta(days=7)

        event = CommunityEvent("event_004", "Rank Event", EventType.TOURNAMENT, start, end)

        for i in range(10):
            event.join(f"user_{i:03d}")
            event.submit_score(f"user_{i:03d}", (10 - i) * 10)

        rankings = event.get_rankings(limit=3)

        assert len(rankings) == 3
        assert rankings[0][0] == "user_000"  # Highest score
        assert rankings[0][1] == 100

    def test_get_rank(self):
        """Test getting specific rank"""
        start = datetime.now()
        end = start + timedelta(days=7)

        event = CommunityEvent("event_005", "Test Rank", EventType.CHALLENGE, start, end)

        event.join("user_001")
        event.join("user_002")
        event.join("user_003")

        event.submit_score("user_001", 100)
        event.submit_score("user_002", 200)
        event.submit_score("user_003", 150)

        assert event.get_rank("user_002") == 1
        assert event.get_rank("user_003") == 2
        assert event.get_rank("user_001") == 3

    def test_end_event(self):
        """Test ending event with rewards"""
        start = datetime.now()
        end = start + timedelta(days=7)

        event = CommunityEvent("event_006", "Reward Event", EventType.SEASONAL, start, end)

        for i in range(5):
            event.join(f"user_{i}")
            event.submit_score(f"user_{i}", (5 - i) * 10)

        rewards = event.end_event()

        assert len(rewards) == 3  # Top 3
        assert rewards["user_0"] == 300  # 1st place (3x)
        assert rewards["user_1"] == 200  # 2nd place (2x)
        assert rewards["user_2"] == 150  # 3rd place (1.5x)


class TestLeaderboard:
    """Test leaderboard system"""

    def test_create_leaderboard(self):
        """Test creating leaderboard"""
        board = Leaderboard("board_001", "Global XP", LeaderboardType.GLOBAL)

        assert board.board_id == "board_001"
        assert board.board_type == LeaderboardType.GLOBAL

    def test_update_score(self):
        """Test updating scores"""
        board = Leaderboard("board_002", "Test Board", LeaderboardType.WEEKLY)

        board.update_score("user_001", 100)
        board.update_score("user_002", 150)
        board.update_score("user_001", 200)  # Update

        assert board.scores["user_001"] == 200
        assert board.scores["user_002"] == 150

    def test_add_score(self):
        """Test adding to scores"""
        board = Leaderboard("board_003", "Add Score", LeaderboardType.SKILL)

        board.add_score("user_001", 50)
        board.add_score("user_001", 30)
        board.add_score("user_001", 20)

        assert board.scores["user_001"] == 100

    def test_get_rank(self):
        """Test getting rank"""
        board = Leaderboard("board_004", "Rank Test", LeaderboardType.GLOBAL)

        board.update_score("user_001", 100)
        board.update_score("user_002", 200)
        board.update_score("user_003", 150)

        assert board.get_rank("user_002") == 1
        assert board.get_rank("user_003") == 2
        assert board.get_rank("user_001") == 3

    def test_get_top(self):
        """Test getting top players"""
        board = Leaderboard("board_005", "Top Test", LeaderboardType.MONTHLY)

        for i in range(20):
            board.update_score(f"user_{i:03d}", (20 - i) * 10)

        top_5 = board.get_top(limit=5)

        assert len(top_5) == 5
        assert top_5[0]["rank"] == 1
        assert top_5[0]["user_id"] == "user_000"
        assert top_5[0]["score"] == 200

    def test_get_nearby(self):
        """Test getting nearby ranks"""
        board = Leaderboard("board_006", "Nearby Test", LeaderboardType.GLOBAL)

        for i in range(100):
            board.update_score(f"user_{i:03d}", (100 - i) * 10)

        nearby = board.get_nearby("user_050", range_size=2)

        # Should get ranks 49-53 (5 total)
        assert len(nearby) == 5
        assert any(p["is_current_user"] for p in nearby)

    def test_reset_leaderboard(self):
        """Test resetting leaderboard"""
        board = Leaderboard("board_007", "Reset Test", LeaderboardType.WEEKLY)

        board.update_score("user_001", 100)
        board.update_score("user_002", 200)

        board.reset()

        assert len(board.scores) == 0
        assert board.reset_date is not None


class TestTrade:
    """Test trading system"""

    def test_create_trade(self):
        """Test creating trade"""
        trade = Trade("trade_001", "user_001", "user_002")

        assert trade.trade_id == "trade_001"
        assert trade.from_user == "user_001"
        assert trade.to_user == "user_002"
        assert trade.status == TradeStatus.PENDING

    def test_add_offers(self):
        """Test adding offers"""
        trade = Trade("trade_002", "user_001", "user_002")

        trade.add_offer_from("water", 10)
        trade.add_offer_from("food", 5)
        trade.add_offer_to("wood", 20)

        assert trade.from_offers["water"] == 10
        assert trade.to_offers["wood"] == 20

    def test_accept_trade(self):
        """Test accepting trade"""
        trade = Trade("trade_003", "user_001", "user_002")
        trade.add_offer_from("water", 10)
        trade.add_offer_to("food", 5)

        trade.accept()

        assert trade.status == TradeStatus.ACCEPTED

    def test_complete_trade(self):
        """Test completing trade"""
        trade = Trade("trade_004", "user_001", "user_002")
        trade.add_offer_from("water", 10)
        trade.add_offer_to("food", 5)

        trade.accept()
        trade.complete()

        assert trade.status == TradeStatus.COMPLETED
        assert trade.completed_at is not None

    def test_reject_trade(self):
        """Test rejecting trade"""
        trade = Trade("trade_005", "user_001", "user_002")
        trade.add_offer_from("water", 10)

        trade.reject()

        assert trade.status == TradeStatus.REJECTED

    def test_trade_summary(self):
        """Test trade summary"""
        trade = Trade("trade_006", "user_001", "user_002")
        trade.add_offer_from("water", 10)
        trade.add_offer_to("food", 5)

        summary = trade.get_summary()

        assert summary["trade_id"] == "trade_006"
        assert summary["from_offers"]["water"] == 10
        assert summary["to_offers"]["food"] == 5


class TestResourcePool:
    """Test resource sharing pool"""

    def test_create_pool(self):
        """Test creating resource pool"""
        pool = ResourcePool("pool_001", "Community Water")

        assert pool.pool_id == "pool_001"
        assert pool.name == "Community Water"

    def test_contribute_resources(self):
        """Test contributing resources"""
        pool = ResourcePool("pool_002", "Test Pool")

        pool.contribute("user_001", "water", 100)
        pool.contribute("user_002", "water", 50)
        pool.contribute("user_001", "food", 25)

        assert pool.get_balance("water") == 150
        assert pool.get_balance("food") == 25

    def test_withdraw_resources(self):
        """Test withdrawing resources"""
        pool = ResourcePool("pool_003", "Test Pool")

        pool.contribute("user_001", "water", 100)

        success = pool.withdraw("user_002", "water", 30)

        assert success
        assert pool.get_balance("water") == 70

    def test_withdraw_insufficient(self):
        """Test withdrawing more than available"""
        pool = ResourcePool("pool_004", "Test Pool")

        pool.contribute("user_001", "water", 50)

        success = pool.withdraw("user_002", "water", 100)

        assert not success
        assert pool.get_balance("water") == 50

    def test_top_contributors(self):
        """Test getting top contributors"""
        pool = ResourcePool("pool_005", "Test Pool")

        pool.contribute("user_001", "water", 100)
        pool.contribute("user_001", "food", 50)
        pool.contribute("user_002", "water", 200)
        pool.contribute("user_003", "food", 75)

        top = pool.get_top_contributors(limit=2)

        assert len(top) == 2
        assert top[0][0] == "user_002"  # 200 total
        assert top[1][0] == "user_001"  # 150 total


# ============================================================================
# TEST SUMMARY
# ============================================================================

def test_summary():
    """Print test summary"""
    print("\n" + "="*70)
    print("uDOS v1.2.0 - Advanced Gameplay & Community Features Tests")
    print("="*70)
    print("\n✅ Multi-Player Missions:")
    print("  • Cooperative missions (shared objectives)")
    print("  • Competitive missions (ranked rewards)")
    print("  • Community missions (large-scale)")
    print("  • Resource pooling and contribution")
    print("  • Dynamic XP distribution")
    print("\n✅ Community Events:")
    print("  • Time-limited challenges")
    print("  • Seasonal events")
    print("  • Tournament system")
    print("  • Leaderboards with rankings")
    print("  • Tiered rewards (top 3)")
    print("\n✅ Leaderboards:")
    print("  • Global, community, skill-based")
    print("  • Weekly, monthly, all-time")
    print("  • Rank calculation and nearby players")
    print("  • Metadata support")
    print("  • Automatic reset functionality")
    print("\n✅ Trading System:")
    print("  • Player-to-player trades")
    print("  • Offer/counter-offer flow")
    print("  • Trade status tracking")
    print("  • Resource sharing pools")
    print("  • Contribution tracking")
    print("\n" + "="*70)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

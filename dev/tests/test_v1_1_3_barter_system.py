#!/usr/bin/env python3
"""
v1.1.3.5 - Barter System Test Suite

Tests the zero-currency barter economy system:
1. Offer/Request Management - Creating and managing trade offers
2. Trade Matching - "What I Have vs What I Need" engine
3. Reputation System - Trust scoring and trade history
4. Trade Workflow - Negotiation, counter-offers, completion
5. Economy Analytics - Pattern detection and health metrics
6. Integration - Complete barter ecosystem scenarios

Building on v1.0.33 foundation with enhanced matching and analytics.

Author: uDOS Development Team
Created: 2025-11-24
Version: 1.1.3.5
"""

import unittest
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple
import json


# ============================================================================
# CORE DATA STRUCTURES
# ============================================================================

class OfferType(Enum):
    """Types of barter offers"""
    GOODS = "goods"           # Physical items
    SERVICES = "services"     # Skills/labor
    KNOWLEDGE = "knowledge"   # Information/teaching
    SKILLS = "skills"         # Skill training
    RESOURCES = "resources"   # Raw materials


class TradeStatus(Enum):
    """Trade negotiation status"""
    PENDING = "pending"
    NEGOTIATING = "negotiating"
    ACCEPTED = "accepted"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"


@dataclass
class BarterOffer:
    """Individual barter offer"""
    offer_id: str
    user_id: str
    offer_type: OfferType
    title: str
    description: str
    tags: List[str]
    quantity: int = 1
    location: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    active: bool = True

    def is_expired(self) -> bool:
        """Check if offer has expired"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

    def matches_tags(self, search_tags: List[str]) -> bool:
        """Check if offer matches search tags"""
        return any(tag in self.tags for tag in search_tags)


@dataclass
class BarterRequest:
    """Request for goods/services"""
    request_id: str
    user_id: str
    request_type: OfferType
    title: str
    description: str
    tags: List[str]
    quantity: int = 1
    location: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    active: bool = True

    def matches_offer(self, offer: BarterOffer) -> bool:
        """Check if this request matches an offer"""
        if offer.offer_type != self.request_type:
            return False
        if not offer.active or offer.is_expired():
            return False
        return any(tag in offer.tags for tag in self.tags)


@dataclass
class Trade:
    """Trade negotiation between two parties"""
    trade_id: str
    offer_id: str
    request_id: str
    offerer_id: str
    requester_id: str
    status: TradeStatus
    offer_items: List[Dict]
    request_items: List[Dict]
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    notes: str = ""

    def is_complete(self) -> bool:
        """Check if trade is completed"""
        return self.status == TradeStatus.COMPLETED


# ============================================================================
# TRADE MATCHING ENGINE
# ============================================================================

class MatchScore:
    """Trade match quality score"""
    def __init__(self, offer: BarterOffer, request: BarterRequest):
        self.offer = offer
        self.request = request
        self.score = self._calculate_score()

    def _calculate_score(self) -> float:
        """Calculate match quality (0.0 to 1.0)"""
        score = 0.0

        # Type match (required)
        if self.offer.offer_type != self.request.request_type:
            return 0.0

        # Tag overlap
        common_tags = set(self.offer.tags) & set(self.request.tags)
        if self.offer.tags and self.request.tags:
            tag_score = len(common_tags) / max(len(self.offer.tags), len(self.request.tags))
            score += tag_score * 0.5

        # Location proximity (if both specified)
        if self.offer.location and self.request.location:
            if self.offer.location == self.request.location:
                score += 0.3
        else:
            score += 0.1  # Partial credit for no location conflict

        # Quantity match
        if self.offer.quantity >= self.request.quantity:
            score += 0.2

        return min(1.0, score)


class TradeMatchingEngine:
    """Match offers with requests using 'What I Have vs What I Need' logic"""

    def __init__(self):
        self.offers: Dict[str, BarterOffer] = {}
        self.requests: Dict[str, BarterRequest] = {}
        self.matches: List[Tuple[BarterOffer, BarterRequest, float]] = []

    def add_offer(self, offer: BarterOffer):
        """Register a new offer"""
        self.offers[offer.offer_id] = offer
        self._update_matches()

    def add_request(self, request: BarterRequest):
        """Register a new request"""
        self.requests[request.request_id] = request
        self._update_matches()

    def _update_matches(self):
        """Recalculate all matches"""
        self.matches.clear()

        for offer in self.offers.values():
            if not offer.active or offer.is_expired():
                continue

            for request in self.requests.values():
                if not request.active:
                    continue

                if request.user_id == offer.user_id:
                    continue  # Can't trade with yourself

                match_score = MatchScore(offer, request)
                if match_score.score > 0:
                    self.matches.append((offer, request, match_score.score))

        # Sort by score descending
        self.matches.sort(key=lambda x: x[2], reverse=True)

    def find_matches(self, user_id: str, min_score: float = 0.3) -> List[Tuple[BarterOffer, BarterRequest, float]]:
        """Find matches for a specific user"""
        user_matches = []

        for offer, request, score in self.matches:
            if score < min_score:
                continue

            if request.user_id == user_id or offer.user_id == user_id:
                user_matches.append((offer, request, score))

        return user_matches

    def find_best_match(self, request_id: str) -> Optional[Tuple[BarterOffer, float]]:
        """Find best offer for a specific request"""
        request = self.requests.get(request_id)
        if not request:
            return None

        best_offer = None
        best_score = 0.0

        for offer, req, score in self.matches:
            if req.request_id == request_id and score > best_score:
                best_offer = offer
                best_score = score

        return (best_offer, best_score) if best_offer else None

    def get_statistics(self) -> Dict:
        """Get matching statistics"""
        active_offers = sum(1 for o in self.offers.values() if o.active and not o.is_expired())
        active_requests = sum(1 for r in self.requests.values() if r.active)

        return {
            "total_offers": len(self.offers),
            "active_offers": active_offers,
            "total_requests": len(self.requests),
            "active_requests": active_requests,
            "total_matches": len(self.matches),
            "high_quality_matches": sum(1 for _, _, score in self.matches if score > 0.7)
        }


# ============================================================================
# REPUTATION SYSTEM
# ============================================================================

@dataclass
class TradeReview:
    """Review of a completed trade"""
    trade_id: str
    reviewer_id: str
    reviewed_id: str
    rating: int  # 1-5 stars
    comment: str
    created_at: datetime = field(default_factory=datetime.now)


class ReputationManager:
    """Track user reputation based on trade history"""

    def __init__(self):
        self.trade_history: Dict[str, List[Trade]] = {}  # user_id -> trades
        self.reviews: Dict[str, List[TradeReview]] = {}  # user_id -> reviews received
        self.reputation_scores: Dict[str, float] = {}    # user_id -> score (0-100)

    def record_trade(self, trade: Trade):
        """Record a completed trade"""
        if trade.status != TradeStatus.COMPLETED:
            return

        # Add to offerer's history
        if trade.offerer_id not in self.trade_history:
            self.trade_history[trade.offerer_id] = []
        self.trade_history[trade.offerer_id].append(trade)

        # Add to requester's history
        if trade.requester_id not in self.trade_history:
            self.trade_history[trade.requester_id] = []
        self.trade_history[trade.requester_id].append(trade)

        # Update reputation scores
        self._update_reputation(trade.offerer_id)
        self._update_reputation(trade.requester_id)

    def add_review(self, review: TradeReview):
        """Add a trade review"""
        if review.reviewed_id not in self.reviews:
            self.reviews[review.reviewed_id] = []
        self.reviews[review.reviewed_id].append(review)

        # Update reputation
        self._update_reputation(review.reviewed_id)

    def _update_reputation(self, user_id: str):
        """Calculate reputation score for a user"""
        score = 50.0  # Start at neutral

        # Trade completion bonus
        trades = self.trade_history.get(user_id, [])
        completed_trades = len(trades)
        score += min(20, completed_trades * 2)  # Up to +20 for trade history

        # Review ratings
        reviews = self.reviews.get(user_id, [])
        if reviews:
            avg_rating = sum(r.rating for r in reviews) / len(reviews)
            # Convert 1-5 rating to -20 to +20 bonus
            score += (avg_rating - 3) * 10

        # Recent activity bonus (trades in last 30 days)
        recent_trades = [
            t for t in trades
            if t.completed_at and (datetime.now() - t.completed_at).days <= 30
        ]
        score += min(10, len(recent_trades) * 2)

        self.reputation_scores[user_id] = max(0, min(100, score))

    def get_reputation(self, user_id: str) -> float:
        """Get user's reputation score (0-100)"""
        return self.reputation_scores.get(user_id, 50.0)

    def get_trade_count(self, user_id: str) -> int:
        """Get number of completed trades"""
        return len(self.trade_history.get(user_id, []))

    def get_average_rating(self, user_id: str) -> Optional[float]:
        """Get average review rating"""
        reviews = self.reviews.get(user_id, [])
        if not reviews:
            return None
        return sum(r.rating for r in reviews) / len(reviews)

    def is_trusted(self, user_id: str, threshold: float = 70.0) -> bool:
        """Check if user meets trusted threshold"""
        return self.get_reputation(user_id) >= threshold


# ============================================================================
# TRADE WORKFLOW
# ============================================================================

class TradeNegotiator:
    """Handle trade negotiation workflow"""

    def __init__(self, reputation_manager: ReputationManager):
        self.reputation_manager = reputation_manager
        self.active_trades: Dict[str, Trade] = {}
        self.trade_counter = 0

    def initiate_trade(
        self,
        offer_id: str,
        request_id: str,
        offerer_id: str,
        requester_id: str,
        offer_items: List[Dict],
        request_items: List[Dict]
    ) -> Trade:
        """Start a new trade negotiation"""
        self.trade_counter += 1
        trade_id = f"trade_{self.trade_counter:06d}"

        trade = Trade(
            trade_id=trade_id,
            offer_id=offer_id,
            request_id=request_id,
            offerer_id=offerer_id,
            requester_id=requester_id,
            status=TradeStatus.PENDING,
            offer_items=offer_items,
            request_items=request_items
        )

        self.active_trades[trade_id] = trade
        return trade

    def propose_counter_offer(
        self,
        trade_id: str,
        user_id: str,
        new_items: List[Dict]
    ) -> bool:
        """Propose a counter-offer"""
        trade = self.active_trades.get(trade_id)
        if not trade:
            return False

        if trade.status not in [TradeStatus.PENDING, TradeStatus.NEGOTIATING]:
            return False

        # Update items based on who's countering
        if user_id == trade.offerer_id:
            trade.offer_items = new_items
        elif user_id == trade.requester_id:
            trade.request_items = new_items
        else:
            return False

        trade.status = TradeStatus.NEGOTIATING
        trade.updated_at = datetime.now()
        return True

    def accept_trade(self, trade_id: str, user_id: str) -> bool:
        """Accept a trade proposal"""
        trade = self.active_trades.get(trade_id)
        if not trade:
            return False

        if trade.status not in [TradeStatus.PENDING, TradeStatus.NEGOTIATING]:
            return False

        # Both parties must be involved
        if user_id not in [trade.offerer_id, trade.requester_id]:
            return False

        trade.status = TradeStatus.ACCEPTED
        trade.updated_at = datetime.now()
        return True

    def complete_trade(self, trade_id: str) -> bool:
        """Mark trade as completed"""
        trade = self.active_trades.get(trade_id)
        if not trade:
            return False

        if trade.status != TradeStatus.ACCEPTED:
            return False

        trade.status = TradeStatus.COMPLETED
        trade.completed_at = datetime.now()
        trade.updated_at = datetime.now()

        # Record in reputation system
        self.reputation_manager.record_trade(trade)

        return True

    def reject_trade(self, trade_id: str, user_id: str, reason: str = "") -> bool:
        """Reject a trade"""
        trade = self.active_trades.get(trade_id)
        if not trade:
            return False

        if user_id not in [trade.offerer_id, trade.requester_id]:
            return False

        trade.status = TradeStatus.REJECTED
        trade.notes = reason
        trade.updated_at = datetime.now()
        return True

    def cancel_trade(self, trade_id: str, user_id: str) -> bool:
        """Cancel an active trade"""
        trade = self.active_trades.get(trade_id)
        if not trade:
            return False

        if user_id not in [trade.offerer_id, trade.requester_id]:
            return False

        trade.status = TradeStatus.CANCELLED
        trade.updated_at = datetime.now()
        return True

    def get_trade_status(self, trade_id: str) -> Optional[TradeStatus]:
        """Get current trade status"""
        trade = self.active_trades.get(trade_id)
        return trade.status if trade else None


# ============================================================================
# ECONOMY ANALYTICS
# ============================================================================

@dataclass
class EconomyMetrics:
    """Economy health metrics"""
    total_trades: int
    active_offers: int
    active_requests: int
    average_completion_time: float  # hours
    trade_velocity: float  # trades per day
    resource_distribution: Dict[str, int]  # type -> count
    user_participation: int  # unique users
    reputation_distribution: Dict[str, int]  # score range -> count


class EconomyAnalyzer:
    """Analyze barter economy health and detect patterns"""

    def __init__(self):
        self.trade_log: List[Trade] = []
        self.offer_log: List[BarterOffer] = []
        self.request_log: List[BarterRequest] = []

    def log_trade(self, trade: Trade):
        """Log a completed trade"""
        self.trade_log.append(trade)

    def log_offer(self, offer: BarterOffer):
        """Log a new offer"""
        self.offer_log.append(offer)

    def log_request(self, request: BarterRequest):
        """Log a new request"""
        self.request_log.append(request)

    def detect_hoarding(self, user_id: str, threshold: int = 10) -> bool:
        """Detect if a user is hoarding resources"""
        user_offers = [o for o in self.offer_log if o.user_id == user_id and o.active]
        total_quantity = sum(o.quantity for o in user_offers)
        return total_quantity > threshold

    def detect_monopoly(self, offer_type: OfferType, threshold: float = 0.5) -> Optional[str]:
        """Detect if one user controls too much of a resource type"""
        type_offers = [o for o in self.offer_log if o.offer_type == offer_type and o.active]
        if not type_offers:
            return None

        # Count by user
        user_counts: Dict[str, int] = {}
        for offer in type_offers:
            user_counts[offer.user_id] = user_counts.get(offer.user_id, 0) + offer.quantity

        total = sum(user_counts.values())
        for user_id, count in user_counts.items():
            if count / total > threshold:
                return user_id

        return None

    def calculate_scarcity(self, tags: List[str]) -> float:
        """Calculate resource scarcity (0.0 = abundant, 1.0 = scarce)"""
        matching_offers = [
            o for o in self.offer_log
            if o.active and any(tag in o.tags for tag in tags)
        ]
        matching_requests = [
            r for r in self.request_log
            if r.active and any(tag in r.tags for tag in tags)
        ]

        if not matching_requests:
            return 0.0  # No demand = not scarce

        if not matching_offers:
            return 1.0  # Demand but no supply = very scarce

        supply = sum(o.quantity for o in matching_offers)
        demand = sum(r.quantity for r in matching_requests)

        if supply >= demand:
            return 0.0

        return 1.0 - (supply / demand)

    def get_metrics(self, reputation_manager: ReputationManager) -> EconomyMetrics:
        """Calculate comprehensive economy metrics"""
        completed_trades = [t for t in self.trade_log if t.status == TradeStatus.COMPLETED]

        # Average completion time
        avg_time = 0.0
        if completed_trades:
            completion_times = [
                (t.completed_at - t.created_at).total_seconds() / 3600
                for t in completed_trades if t.completed_at
            ]
            avg_time = sum(completion_times) / len(completion_times) if completion_times else 0.0

        # Trade velocity (trades per day)
        if completed_trades:
            earliest = min(t.created_at for t in completed_trades)
            latest = max(t.completed_at for t in completed_trades if t.completed_at)
            days = max(1, (latest - earliest).days)
            velocity = len(completed_trades) / days
        else:
            velocity = 0.0

        # Resource distribution
        resource_dist: Dict[str, int] = {}
        for offer in self.offer_log:
            if offer.active:
                key = offer.offer_type.value
                resource_dist[key] = resource_dist.get(key, 0) + offer.quantity

        # Unique users
        all_users = set()
        for offer in self.offer_log:
            all_users.add(offer.user_id)
        for request in self.request_log:
            all_users.add(request.user_id)

        # Reputation distribution
        rep_dist = {"0-25": 0, "26-50": 0, "51-75": 0, "76-100": 0}
        for user_id in all_users:
            score = reputation_manager.get_reputation(user_id)
            if score <= 25:
                rep_dist["0-25"] += 1
            elif score <= 50:
                rep_dist["26-50"] += 1
            elif score <= 75:
                rep_dist["51-75"] += 1
            else:
                rep_dist["76-100"] += 1

        return EconomyMetrics(
            total_trades=len(completed_trades),
            active_offers=sum(1 for o in self.offer_log if o.active and not o.is_expired()),
            active_requests=sum(1 for r in self.request_log if r.active),
            average_completion_time=avg_time,
            trade_velocity=velocity,
            resource_distribution=resource_dist,
            user_participation=len(all_users),
            reputation_distribution=rep_dist
        )

    def get_fairness_score(self, reputation_manager: ReputationManager) -> float:
        """Calculate economy fairness (0.0 = very unfair, 1.0 = perfectly fair)"""
        completed_trades = [t for t in self.trade_log if t.status == TradeStatus.COMPLETED]
        if not completed_trades:
            return 1.0

        # Check reputation variance (lower variance = more fair)
        all_users = set()
        for trade in completed_trades:
            all_users.add(trade.offerer_id)
            all_users.add(trade.requester_id)

        if len(all_users) < 2:
            return 1.0

        reputations = [reputation_manager.get_reputation(uid) for uid in all_users]
        avg_rep = sum(reputations) / len(reputations)
        variance = sum((r - avg_rep) ** 2 for r in reputations) / len(reputations)

        # Normalize variance to 0-1 (lower variance = higher fairness)
        # Max variance is 2500 (all at 0, all at 100)
        fairness = 1.0 - min(1.0, variance / 2500)

        return fairness


# ============================================================================
# TEST SUITE
# ============================================================================

class TestOfferManagement(unittest.TestCase):
    """Test offer creation and management"""

    def test_create_offer(self):
        """Test creating a barter offer"""
        offer = BarterOffer(
            offer_id="offer_001",
            user_id="user_alice",
            offer_type=OfferType.GOODS,
            title="Fresh vegetables",
            description="Tomatoes and cucumbers from garden",
            tags=["food", "vegetables", "organic"],
            quantity=5
        )

        self.assertEqual(offer.offer_id, "offer_001")
        self.assertEqual(offer.offer_type, OfferType.GOODS)
        self.assertEqual(offer.quantity, 5)
        self.assertTrue(offer.active)

    def test_offer_expiration(self):
        """Test offer expiration checking"""
        # Expired offer
        expired_offer = BarterOffer(
            offer_id="offer_002",
            user_id="user_bob",
            offer_type=OfferType.SERVICES,
            title="Carpentry work",
            description="Build shelves",
            tags=["carpentry", "building"],
            expires_at=datetime.now() - timedelta(hours=1)
        )

        self.assertTrue(expired_offer.is_expired())

        # Active offer
        active_offer = BarterOffer(
            offer_id="offer_003",
            user_id="user_charlie",
            offer_type=OfferType.KNOWLEDGE,
            title="Python tutorial",
            description="Learn Python basics",
            tags=["programming", "python"],
            expires_at=datetime.now() + timedelta(days=7)
        )

        self.assertFalse(active_offer.is_expired())

    def test_offer_tag_matching(self):
        """Test offer tag matching"""
        offer = BarterOffer(
            offer_id="offer_004",
            user_id="user_dave",
            offer_type=OfferType.SKILLS,
            title="Guitar lessons",
            description="Beginner to intermediate",
            tags=["music", "guitar", "teaching"]
        )

        self.assertTrue(offer.matches_tags(["music"]))
        self.assertTrue(offer.matches_tags(["guitar", "drums"]))
        self.assertFalse(offer.matches_tags(["piano", "drums"]))

    def test_offer_with_location(self):
        """Test offer with location specification"""
        offer = BarterOffer(
            offer_id="offer_005",
            user_id="user_eve",
            offer_type=OfferType.RESOURCES,
            title="Firewood",
            description="Seasoned oak firewood",
            tags=["wood", "fuel", "heating"],
            quantity=20,
            location="Portland, OR"
        )

        self.assertEqual(offer.location, "Portland, OR")


class TestRequestManagement(unittest.TestCase):
    """Test request creation and matching"""

    def test_create_request(self):
        """Test creating a barter request"""
        request = BarterRequest(
            request_id="req_001",
            user_id="user_frank",
            request_type=OfferType.GOODS,
            title="Need fresh produce",
            description="Looking for vegetables",
            tags=["food", "vegetables"],
            quantity=3
        )

        self.assertEqual(request.request_id, "req_001")
        self.assertEqual(request.request_type, OfferType.GOODS)
        self.assertTrue(request.active)

    def test_request_offer_matching(self):
        """Test request matching with offers"""
        request = BarterRequest(
            request_id="req_002",
            user_id="user_grace",
            request_type=OfferType.SERVICES,
            title="Need plumbing help",
            description="Fix leaky faucet",
            tags=["plumbing", "repair"]
        )

        # Matching offer
        matching_offer = BarterOffer(
            offer_id="offer_006",
            user_id="user_henry",
            offer_type=OfferType.SERVICES,
            title="Plumbing services",
            description="Professional plumber",
            tags=["plumbing", "repair", "maintenance"]
        )

        self.assertTrue(request.matches_offer(matching_offer))

        # Non-matching offer (wrong type)
        wrong_type = BarterOffer(
            offer_id="offer_007",
            user_id="user_ian",
            offer_type=OfferType.GOODS,
            title="Plumbing supplies",
            description="Pipes and fittings",
            tags=["plumbing", "supplies"]
        )

        self.assertFalse(request.matches_offer(wrong_type))

    def test_request_inactive_offer_matching(self):
        """Test request doesn't match inactive offers"""
        request = BarterRequest(
            request_id="req_003",
            user_id="user_judy",
            request_type=OfferType.KNOWLEDGE,
            title="Learn gardening",
            description="Need gardening advice",
            tags=["gardening", "growing"]
        )

        inactive_offer = BarterOffer(
            offer_id="offer_008",
            user_id="user_karl",
            offer_type=OfferType.KNOWLEDGE,
            title="Gardening workshop",
            description="Teach gardening basics",
            tags=["gardening", "teaching"],
            active=False
        )

        self.assertFalse(request.matches_offer(inactive_offer))


class TestTradeMatching(unittest.TestCase):
    """Test trade matching engine"""

    def test_add_offer_and_request(self):
        """Test adding offers and requests to matching engine"""
        engine = TradeMatchingEngine()

        offer = BarterOffer(
            offer_id="offer_009",
            user_id="user_leo",
            offer_type=OfferType.GOODS,
            title="Honey",
            description="Local honey",
            tags=["food", "honey", "sweet"]
        )

        request = BarterRequest(
            request_id="req_004",
            user_id="user_mary",
            request_type=OfferType.GOODS,
            title="Need honey",
            description="Looking for local honey",
            tags=["food", "honey"]
        )

        engine.add_offer(offer)
        engine.add_request(request)

        self.assertEqual(len(engine.offers), 1)
        self.assertEqual(len(engine.requests), 1)
        self.assertGreater(len(engine.matches), 0)

    def test_match_scoring(self):
        """Test match quality scoring"""
        offer = BarterOffer(
            offer_id="offer_010",
            user_id="user_nancy",
            offer_type=OfferType.SKILLS,
            title="Web development",
            description="Build websites",
            tags=["programming", "web", "html", "css"],
            location="Seattle, WA"
        )

        request = BarterRequest(
            request_id="req_005",
            user_id="user_oscar",
            request_type=OfferType.SKILLS,
            title="Need website built",
            description="Small business site",
            tags=["web", "programming"],
            location="Seattle, WA"
        )

        score = MatchScore(offer, request)
        self.assertGreater(score.score, 0.5)  # Good match

    def test_no_self_matching(self):
        """Test users can't match with themselves"""
        engine = TradeMatchingEngine()

        offer = BarterOffer(
            offer_id="offer_011",
            user_id="user_paul",
            offer_type=OfferType.RESOURCES,
            title="Scrap metal",
            description="Various metal scraps",
            tags=["metal", "materials"]
        )

        request = BarterRequest(
            request_id="req_006",
            user_id="user_paul",  # Same user
            request_type=OfferType.RESOURCES,
            title="Need metal",
            description="Looking for metal",
            tags=["metal"]
        )

        engine.add_offer(offer)
        engine.add_request(request)

        self.assertEqual(len(engine.matches), 0)  # No self-match

    def test_find_user_matches(self):
        """Test finding matches for a specific user"""
        engine = TradeMatchingEngine()

        # User Quinn's request
        request = BarterRequest(
            request_id="req_007",
            user_id="user_quinn",
            request_type=OfferType.GOODS,
            title="Need eggs",
            description="Fresh eggs",
            tags=["food", "eggs", "protein"]
        )

        # Rachel's matching offer
        offer = BarterOffer(
            offer_id="offer_012",
            user_id="user_rachel",
            offer_type=OfferType.GOODS,
            title="Fresh eggs",
            description="Farm fresh eggs",
            tags=["food", "eggs", "organic"]
        )

        engine.add_request(request)
        engine.add_offer(offer)

        matches = engine.find_matches("user_quinn")
        self.assertEqual(len(matches), 1)

    def test_find_best_match(self):
        """Test finding best offer for a request"""
        engine = TradeMatchingEngine()

        request = BarterRequest(
            request_id="req_008",
            user_id="user_sam",
            request_type=OfferType.SERVICES,
            title="Need roof repair",
            description="Leaking roof",
            tags=["repair", "roofing", "construction"]
        )

        # Good match
        good_offer = BarterOffer(
            offer_id="offer_013",
            user_id="user_tina",
            offer_type=OfferType.SERVICES,
            title="Roofing specialist",
            description="Professional roofer",
            tags=["roofing", "repair", "construction"]
        )

        # Weaker match
        weak_offer = BarterOffer(
            offer_id="offer_014",
            user_id="user_uma",
            offer_type=OfferType.SERVICES,
            title="General repairs",
            description="Handyman services",
            tags=["repair", "maintenance"]
        )

        engine.add_request(request)
        engine.add_offer(good_offer)
        engine.add_offer(weak_offer)

        best_match = engine.find_best_match("req_008")
        self.assertIsNotNone(best_match)
        self.assertEqual(best_match[0].offer_id, "offer_013")

    def test_matching_statistics(self):
        """Test matching engine statistics"""
        engine = TradeMatchingEngine()

        for i in range(5):
            offer = BarterOffer(
                offer_id=f"offer_{i}",
                user_id=f"user_{i}",
                offer_type=OfferType.GOODS,
                title=f"Item {i}",
                description="Description",
                tags=["test"]
            )
            engine.add_offer(offer)

        stats = engine.get_statistics()
        self.assertEqual(stats["total_offers"], 5)
        self.assertEqual(stats["active_offers"], 5)


class TestReputationSystem(unittest.TestCase):
    """Test reputation tracking and scoring"""

    def test_initial_reputation(self):
        """Test new users start with neutral reputation"""
        manager = ReputationManager()
        rep = manager.get_reputation("user_new")

        self.assertEqual(rep, 50.0)  # Neutral starting point

    def test_trade_completion_bonus(self):
        """Test reputation increases with completed trades"""
        manager = ReputationManager()

        # Complete several trades
        for i in range(5):
            trade = Trade(
                trade_id=f"trade_{i}",
                offer_id=f"offer_{i}",
                request_id=f"req_{i}",
                offerer_id="user_victor",
                requester_id=f"user_{i}",
                status=TradeStatus.COMPLETED,
                offer_items=[{"item": "test"}],
                request_items=[{"item": "test"}],
                completed_at=datetime.now()
            )
            manager.record_trade(trade)

        rep = manager.get_reputation("user_victor")
        self.assertGreater(rep, 50.0)  # Reputation increased

    def test_review_impact_on_reputation(self):
        """Test reviews affect reputation score"""
        manager = ReputationManager()

        # Add positive reviews
        for i in range(3):
            review = TradeReview(
                trade_id=f"trade_{i}",
                reviewer_id=f"user_{i}",
                reviewed_id="user_wendy",
                rating=5,  # Excellent
                comment="Great trader!"
            )
            manager.add_review(review)

        rep = manager.get_reputation("user_wendy")
        self.assertGreater(rep, 50.0)

        # Add negative review
        bad_review = TradeReview(
            trade_id="trade_bad",
            reviewer_id="user_xyz",
            reviewed_id="user_wendy",
            rating=1,  # Poor
            comment="Did not deliver"
        )
        manager.add_review(bad_review)

        new_rep = manager.get_reputation("user_wendy")
        self.assertLess(new_rep, rep)  # Reputation decreased

    def test_get_trade_count(self):
        """Test trade count tracking"""
        manager = ReputationManager()

        for i in range(7):
            trade = Trade(
                trade_id=f"trade_{i}",
                offer_id=f"offer_{i}",
                request_id=f"req_{i}",
                offerer_id="user_xavier",
                requester_id=f"user_{i}",
                status=TradeStatus.COMPLETED,
                offer_items=[{"item": "test"}],
                request_items=[{"item": "test"}],
                completed_at=datetime.now()
            )
            manager.record_trade(trade)

        count = manager.get_trade_count("user_xavier")
        self.assertEqual(count, 7)

    def test_average_rating_calculation(self):
        """Test average rating calculation"""
        manager = ReputationManager()

        ratings = [5, 4, 5, 3, 4]
        for i, rating in enumerate(ratings):
            review = TradeReview(
                trade_id=f"trade_{i}",
                reviewer_id=f"user_{i}",
                reviewed_id="user_yara",
                rating=rating,
                comment="Review"
            )
            manager.add_review(review)

        avg = manager.get_average_rating("user_yara")
        expected = sum(ratings) / len(ratings)
        self.assertAlmostEqual(avg, expected, places=2)

    def test_trusted_user_threshold(self):
        """Test trusted user identification"""
        manager = ReputationManager()

        # Build up reputation
        for i in range(10):
            trade = Trade(
                trade_id=f"trade_{i}",
                offer_id=f"offer_{i}",
                request_id=f"req_{i}",
                offerer_id="user_zara",
                requester_id=f"user_{i}",
                status=TradeStatus.COMPLETED,
                offer_items=[{"item": "test"}],
                request_items=[{"item": "test"}],
                completed_at=datetime.now()
            )
            manager.record_trade(trade)

            review = TradeReview(
                trade_id=f"trade_{i}",
                reviewer_id=f"user_{i}",
                reviewed_id="user_zara",
                rating=5,
                comment="Excellent!"
            )
            manager.add_review(review)

        self.assertTrue(manager.is_trusted("user_zara"))

    def test_recent_activity_bonus(self):
        """Test recent activity affects reputation"""
        manager = ReputationManager()

        # Recent trade
        recent_trade = Trade(
            trade_id="trade_recent",
            offer_id="offer_recent",
            request_id="req_recent",
            offerer_id="user_active",
            requester_id="user_other",
            status=TradeStatus.COMPLETED,
            offer_items=[{"item": "test"}],
            request_items=[{"item": "test"}],
            completed_at=datetime.now()
        )
        manager.record_trade(recent_trade)

        rep_with_recent = manager.get_reputation("user_active")

        # Old trade (31 days ago)
        old_trade = Trade(
            trade_id="trade_old",
            offer_id="offer_old",
            request_id="req_old",
            offerer_id="user_inactive",
            requester_id="user_other2",
            status=TradeStatus.COMPLETED,
            offer_items=[{"item": "test"}],
            request_items=[{"item": "test"}],
            completed_at=datetime.now() - timedelta(days=31)
        )
        manager.record_trade(old_trade)

        rep_without_recent = manager.get_reputation("user_inactive")

        # Recent activity should give bonus
        self.assertGreater(rep_with_recent, rep_without_recent)


class TestTradeWorkflow(unittest.TestCase):
    """Test trade negotiation workflow"""

    def setUp(self):
        """Set up test fixtures"""
        self.rep_manager = ReputationManager()
        self.negotiator = TradeNegotiator(self.rep_manager)

    def test_initiate_trade(self):
        """Test starting a new trade"""
        trade = self.negotiator.initiate_trade(
            offer_id="offer_100",
            request_id="req_100",
            offerer_id="user_alice",
            requester_id="user_bob",
            offer_items=[{"item": "bread", "qty": 2}],
            request_items=[{"item": "butter", "qty": 1}]
        )

        self.assertIsNotNone(trade)
        self.assertEqual(trade.status, TradeStatus.PENDING)
        self.assertEqual(trade.offerer_id, "user_alice")
        self.assertEqual(trade.requester_id, "user_bob")

    def test_counter_offer(self):
        """Test proposing a counter-offer"""
        trade = self.negotiator.initiate_trade(
            offer_id="offer_101",
            request_id="req_101",
            offerer_id="user_charlie",
            requester_id="user_dave",
            offer_items=[{"item": "apples", "qty": 5}],
            request_items=[{"item": "carrots", "qty": 10}]
        )

        # Requester proposes counter
        success = self.negotiator.propose_counter_offer(
            trade.trade_id,
            "user_dave",
            [{"item": "carrots", "qty": 8}]  # Lower quantity
        )

        self.assertTrue(success)
        self.assertEqual(trade.status, TradeStatus.NEGOTIATING)

    def test_accept_trade(self):
        """Test accepting a trade"""
        trade = self.negotiator.initiate_trade(
            offer_id="offer_102",
            request_id="req_102",
            offerer_id="user_eve",
            requester_id="user_frank",
            offer_items=[{"item": "tools", "qty": 1}],
            request_items=[{"item": "wood", "qty": 20}]
        )

        success = self.negotiator.accept_trade(trade.trade_id, "user_frank")

        self.assertTrue(success)
        self.assertEqual(trade.status, TradeStatus.ACCEPTED)

    def test_complete_trade(self):
        """Test completing a trade"""
        trade = self.negotiator.initiate_trade(
            offer_id="offer_103",
            request_id="req_103",
            offerer_id="user_grace",
            requester_id="user_henry",
            offer_items=[{"item": "seeds", "qty": 100}],
            request_items=[{"item": "fertilizer", "qty": 5}]
        )

        # Accept then complete
        self.negotiator.accept_trade(trade.trade_id, "user_grace")
        success = self.negotiator.complete_trade(trade.trade_id)

        self.assertTrue(success)
        self.assertEqual(trade.status, TradeStatus.COMPLETED)
        self.assertIsNotNone(trade.completed_at)

        # Check reputation updated
        self.assertEqual(self.rep_manager.get_trade_count("user_grace"), 1)

    def test_reject_trade(self):
        """Test rejecting a trade"""
        trade = self.negotiator.initiate_trade(
            offer_id="offer_104",
            request_id="req_104",
            offerer_id="user_ian",
            requester_id="user_judy",
            offer_items=[{"item": "pottery", "qty": 3}],
            request_items=[{"item": "clay", "qty": 50}]
        )

        success = self.negotiator.reject_trade(
            trade.trade_id,
            "user_judy",
            reason="Price too high"
        )

        self.assertTrue(success)
        self.assertEqual(trade.status, TradeStatus.REJECTED)
        self.assertIn("too high", trade.notes)

    def test_cancel_trade(self):
        """Test cancelling a trade"""
        trade = self.negotiator.initiate_trade(
            offer_id="offer_105",
            request_id="req_105",
            offerer_id="user_karl",
            requester_id="user_leo",
            offer_items=[{"item": "fabric", "qty": 10}],
            request_items=[{"item": "thread", "qty": 5}]
        )

        success = self.negotiator.cancel_trade(trade.trade_id, "user_karl")

        self.assertTrue(success)
        self.assertEqual(trade.status, TradeStatus.CANCELLED)

    def test_get_trade_status(self):
        """Test getting trade status"""
        trade = self.negotiator.initiate_trade(
            offer_id="offer_106",
            request_id="req_106",
            offerer_id="user_mary",
            requester_id="user_nancy",
            offer_items=[{"item": "books", "qty": 5}],
            request_items=[{"item": "paper", "qty": 100}]
        )

        status = self.negotiator.get_trade_status(trade.trade_id)
        self.assertEqual(status, TradeStatus.PENDING)

    def test_unauthorized_user_cannot_modify(self):
        """Test unauthorized users can't modify trades"""
        trade = self.negotiator.initiate_trade(
            offer_id="offer_107",
            request_id="req_107",
            offerer_id="user_oscar",
            requester_id="user_paul",
            offer_items=[{"item": "honey", "qty": 2}],
            request_items=[{"item": "wax", "qty": 1}]
        )

        # Outsider tries to accept
        success = self.negotiator.accept_trade(trade.trade_id, "user_outsider")
        self.assertFalse(success)


class TestEconomyAnalytics(unittest.TestCase):
    """Test economy analytics and pattern detection"""

    def test_detect_hoarding(self):
        """Test detection of resource hoarding"""
        analyzer = EconomyAnalyzer()

        # User has many active offers
        for i in range(15):
            offer = BarterOffer(
                offer_id=f"offer_{i}",
                user_id="user_hoarder",
                offer_type=OfferType.RESOURCES,
                title=f"Resource {i}",
                description="Resource",
                tags=["resource"],
                quantity=2
            )
            analyzer.log_offer(offer)

        is_hoarding = analyzer.detect_hoarding("user_hoarder", threshold=10)
        self.assertTrue(is_hoarding)

    def test_detect_monopoly(self):
        """Test detection of resource monopoly"""
        analyzer = EconomyAnalyzer()

        # One user controls most of a resource type
        for i in range(10):
            offer = BarterOffer(
                offer_id=f"offer_mono_{i}",
                user_id="user_monopolist",
                offer_type=OfferType.GOODS,
                title="Food",
                description="Food item",
                tags=["food"],
                quantity=10
            )
            analyzer.log_offer(offer)

        # Others have small amounts
        for i in range(3):
            offer = BarterOffer(
                offer_id=f"offer_other_{i}",
                user_id=f"user_{i}",
                offer_type=OfferType.GOODS,
                title="Food",
                description="Food item",
                tags=["food"],
                quantity=1
            )
            analyzer.log_offer(offer)

        monopolist = analyzer.detect_monopoly(OfferType.GOODS, threshold=0.5)
        self.assertEqual(monopolist, "user_monopolist")

    def test_calculate_scarcity(self):
        """Test resource scarcity calculation"""
        analyzer = EconomyAnalyzer()

        # High demand, low supply = high scarcity
        for i in range(10):
            request = BarterRequest(
                request_id=f"req_{i}",
                user_id=f"user_{i}",
                request_type=OfferType.RESOURCES,
                title="Need metal",
                description="Metal needed",
                tags=["metal"],
                quantity=5
            )
            analyzer.log_request(request)

        # Only 1 offer
        offer = BarterOffer(
            offer_id="offer_scarce",
            user_id="user_supplier",
            offer_type=OfferType.RESOURCES,
            title="Metal",
            description="Some metal",
            tags=["metal"],
            quantity=10
        )
        analyzer.log_offer(offer)

        scarcity = analyzer.calculate_scarcity(["metal"])
        self.assertGreater(scarcity, 0.5)  # High scarcity

    def test_get_economy_metrics(self):
        """Test comprehensive economy metrics"""
        rep_manager = ReputationManager()
        analyzer = EconomyAnalyzer()

        # Add some trades
        for i in range(5):
            trade = Trade(
                trade_id=f"trade_{i}",
                offer_id=f"offer_{i}",
                request_id=f"req_{i}",
                offerer_id=f"user_{i}",
                requester_id=f"user_{i+10}",
                status=TradeStatus.COMPLETED,
                offer_items=[{"item": "test"}],
                request_items=[{"item": "test"}],
                created_at=datetime.now() - timedelta(hours=24-i),
                completed_at=datetime.now() - timedelta(hours=20-i)
            )
            analyzer.log_trade(trade)
            rep_manager.record_trade(trade)

        # Add offers and requests
        for i in range(10):
            offer = BarterOffer(
                offer_id=f"offer_active_{i}",
                user_id=f"user_{i}",
                offer_type=OfferType.GOODS,
                title="Item",
                description="Description",
                tags=["test"]
            )
            analyzer.log_offer(offer)

        metrics = analyzer.get_metrics(rep_manager)

        self.assertEqual(metrics.total_trades, 5)
        self.assertGreater(metrics.active_offers, 0)
        self.assertGreater(metrics.user_participation, 0)

    def test_fairness_score(self):
        """Test economy fairness calculation"""
        rep_manager = ReputationManager()
        analyzer = EconomyAnalyzer()

        # Create trades between users
        for i in range(5):
            trade = Trade(
                trade_id=f"trade_fair_{i}",
                offer_id=f"offer_{i}",
                request_id=f"req_{i}",
                offerer_id=f"user_{i}",
                requester_id=f"user_{i+5}",
                status=TradeStatus.COMPLETED,
                offer_items=[{"item": "test"}],
                request_items=[{"item": "test"}],
                completed_at=datetime.now()
            )
            analyzer.log_trade(trade)
            rep_manager.record_trade(trade)

            # Equal reviews
            review1 = TradeReview(
                trade_id=trade.trade_id,
                reviewer_id=trade.requester_id,
                reviewed_id=trade.offerer_id,
                rating=4,
                comment="Good"
            )
            review2 = TradeReview(
                trade_id=trade.trade_id,
                reviewer_id=trade.offerer_id,
                reviewed_id=trade.requester_id,
                rating=4,
                comment="Good"
            )
            rep_manager.add_review(review1)
            rep_manager.add_review(review2)

        fairness = analyzer.get_fairness_score(rep_manager)
        self.assertGreater(fairness, 0.5)  # Relatively fair


class TestIntegration(unittest.TestCase):
    """Test complete barter system integration"""

    def test_complete_barter_flow(self):
        """Test end-to-end barter workflow"""
        # Initialize systems
        engine = TradeMatchingEngine()
        rep_manager = ReputationManager()
        negotiator = TradeNegotiator(rep_manager)
        analyzer = EconomyAnalyzer()

        # User Alice offers vegetables
        alice_offer = BarterOffer(
            offer_id="offer_alice_veg",
            user_id="user_alice",
            offer_type=OfferType.GOODS,
            title="Fresh vegetables",
            description="Tomatoes and lettuce",
            tags=["food", "vegetables", "organic"],
            quantity=10,
            location="Portland, OR"
        )
        engine.add_offer(alice_offer)
        analyzer.log_offer(alice_offer)

        # User Bob requests vegetables
        bob_request = BarterRequest(
            request_id="req_bob_veg",
            user_id="user_bob",
            request_type=OfferType.GOODS,
            title="Need fresh produce",
            description="Looking for vegetables",
            tags=["food", "vegetables"],
            quantity=5,
            location="Portland, OR"
        )
        engine.add_request(bob_request)
        analyzer.log_request(bob_request)

        # Find match
        matches = engine.find_matches("user_bob")
        self.assertEqual(len(matches), 1)

        # Initiate trade
        trade = negotiator.initiate_trade(
            offer_id=alice_offer.offer_id,
            request_id=bob_request.request_id,
            offerer_id="user_alice",
            requester_id="user_bob",
            offer_items=[{"item": "vegetables", "qty": 5}],
            request_items=[{"item": "bread", "qty": 2}]
        )

        # Accept and complete
        negotiator.accept_trade(trade.trade_id, "user_bob")
        negotiator.complete_trade(trade.trade_id)
        analyzer.log_trade(trade)

        # Add reviews
        alice_review = TradeReview(
            trade_id=trade.trade_id,
            reviewer_id="user_alice",
            reviewed_id="user_bob",
            rating=5,
            comment="Great trade!"
        )
        bob_review = TradeReview(
            trade_id=trade.trade_id,
            reviewer_id="user_bob",
            reviewed_id="user_alice",
            rating=5,
            comment="Excellent produce!"
        )
        rep_manager.add_review(alice_review)
        rep_manager.add_review(bob_review)

        # Verify reputation increased
        self.assertGreater(rep_manager.get_reputation("user_alice"), 50.0)
        self.assertGreater(rep_manager.get_reputation("user_bob"), 50.0)

        # Check economy metrics
        metrics = analyzer.get_metrics(rep_manager)
        self.assertEqual(metrics.total_trades, 1)
        self.assertEqual(metrics.user_participation, 2)

    def test_multi_party_marketplace(self):
        """Test marketplace with multiple users and trades"""
        engine = TradeMatchingEngine()
        rep_manager = ReputationManager()

        # Multiple users post offers
        users = ["alice", "bob", "charlie", "dave", "eve"]
        offer_types = [OfferType.GOODS, OfferType.SERVICES, OfferType.SKILLS,
                      OfferType.RESOURCES, OfferType.KNOWLEDGE]

        for i, user in enumerate(users):
            offer = BarterOffer(
                offer_id=f"offer_{user}",
                user_id=f"user_{user}",
                offer_type=offer_types[i],
                title=f"{user}'s offer",
                description="Something useful",
                tags=[offer_types[i].value, "trade"],
                quantity=5
            )
            engine.add_offer(offer)

        # Multiple requests
        for i, user in enumerate(users):
            # Request something different from what they offer
            request_type = offer_types[(i + 1) % len(offer_types)]
            request = BarterRequest(
                request_id=f"req_{user}",
                user_id=f"user_{user}",
                request_type=request_type,
                title=f"{user}'s request",
                description="Something needed",
                tags=[request_type.value, "trade"],
                quantity=3
            )
            engine.add_request(request)

        # Check that matches were found
        stats = engine.get_statistics()
        self.assertEqual(stats["total_offers"], 5)
        self.assertEqual(stats["total_requests"], 5)
        self.assertGreater(stats["total_matches"], 0)


if __name__ == "__main__":
    unittest.main()

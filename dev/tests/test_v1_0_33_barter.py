"""
uDOS v1.0.33 - Barter Economy System Tests

Comprehensive test coverage for zero-currency economy:
- Command routing
- OFFER operations
- REQUEST operations
- TRADE execution
- Matching engine
- Reputation tracking
- Error handling
- Integration scenarios

Target: 60+ tests

Author: uDOS Development Team
Version: 1.0.33
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from core.services.barter_service import (
    BarterService, OfferType, TradeStatus, Offer, Request, Trade
)
from core.commands.barter_commands import BarterCommandHandler


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_barter_dir():
    """Create temporary directory for barter data"""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def barter_service(temp_barter_dir):
    """Create BarterService with temp directory"""
    return BarterService(base_path=temp_barter_dir)


@pytest.fixture
def barter_handler():
    """Create BarterCommandHandler"""
    return BarterCommandHandler()


@pytest.fixture
def sample_offer(barter_service):
    """Create sample offer"""
    return barter_service.create_offer(
        user="alice@localhost",
        offer_type=OfferType.SKILL,
        title="Python tutoring",
        description="Can teach Python basics and advanced concepts",
        tags=["python", "programming", "tutoring", "basics", "advanced", "concepts"]
    )


@pytest.fixture
def sample_request(barter_service):
    """Create sample request"""
    return barter_service.create_request(
        user="bob@localhost",
        request_type=OfferType.SKILL,
        title="Learn Python",
        description="Want to learn Python programming",
        tags=["learn", "python", "programming"]
    )


# ============================================================================
# TEST COMMAND ROUTING (5 tests)
# ============================================================================

class TestCommandRouting:
    """Test barter command routing"""

    def test_help_command(self, barter_handler):
        """Test BARTER HELP command"""
        result = barter_handler.handle("HELP", [])
        assert "BARTER - Zero-Currency Economy" in result
        assert "OFFER" in result
        assert "REQUEST" in result
        assert "TRADE" in result
        assert "REPUTATION" in result

    def test_offer_routing(self, barter_handler):
        """Test OFFER command routes to _offer"""
        result = barter_handler.handle("OFFER", [])
        assert "Missing subcommand" in result or "Usage" in result

    def test_request_routing(self, barter_handler):
        """Test REQUEST command routes to _request"""
        result = barter_handler.handle("REQUEST", [])
        assert "Missing subcommand" in result or "Usage" in result

    def test_trade_routing(self, barter_handler):
        """Test TRADE command routes to _trade"""
        result = barter_handler.handle("TRADE", [])
        assert "Missing subcommand" in result or "Usage" in result

    def test_invalid_command(self, barter_handler):
        """Test invalid command returns error"""
        result = barter_handler.handle("INVALID", [])
        assert "Unknown BARTER command" in result


# ============================================================================
# TEST OFFER OPERATIONS (8 tests)
# ============================================================================

class TestOfferOperations:
    """Test OFFER creation, listing, and deletion"""

    def test_create_offer(self, barter_service):
        """Test creating a new offer"""
        offer = barter_service.create_offer(
            user="test@localhost",
            offer_type=OfferType.SKILL,
            title="Web development",
            description="Build websites",
            tags=["web", "development", "websites"]
        )

        assert offer.id.startswith("OFR_")
        assert offer.user == "test@localhost"
        assert offer.type == OfferType.SKILL
        assert offer.title == "Web development"
        assert offer.active is True

    def test_list_all_offers(self, barter_service, sample_offer):
        """Test listing all offers"""
        offers = barter_service.list_offers()
        assert len(offers) >= 1
        assert any(o.id == sample_offer.id for o in offers)

    def test_list_offers_by_user(self, barter_service, sample_offer):
        """Test filtering offers by user"""
        offers = barter_service.list_offers(user="alice@localhost")
        assert all(o.user == "alice@localhost" for o in offers)

    def test_list_offers_by_type(self, barter_service, sample_offer):
        """Test filtering offers by type"""
        offers = barter_service.list_offers(offer_type=OfferType.SKILL)
        assert all(o.type == OfferType.SKILL for o in offers)

    def test_get_specific_offer(self, barter_service, sample_offer):
        """Test retrieving specific offer"""
        offer = barter_service.get_offer(sample_offer.id)
        assert offer is not None
        assert offer.id == sample_offer.id

    def test_delete_own_offer(self, barter_service, sample_offer):
        """Test deleting own offer"""
        success = barter_service.delete_offer(sample_offer.id, "alice@localhost")
        assert success is True

        # Verify it's marked inactive
        offer = barter_service.get_offer(sample_offer.id)
        assert offer.active is False

    def test_cannot_delete_others_offer(self, barter_service, sample_offer):
        """Test cannot delete another user's offer"""
        success = barter_service.delete_offer(sample_offer.id, "eve@localhost")
        assert success is False

    def test_offer_persistence(self, temp_barter_dir, sample_offer):
        """Test offers persist across service instances"""
        service1 = BarterService(base_path=temp_barter_dir)
        offer1 = service1.create_offer(
            user="test@localhost",
            offer_type=OfferType.TOOL,
            title="Hammer",
            description="For rent",
            tags=["hammer", "tool", "rent"]
        )

        # Create new service instance
        service2 = BarterService(base_path=temp_barter_dir)
        offer2 = service2.get_offer(offer1.id)

        assert offer2 is not None
        assert offer2.title == "Hammer"


# ============================================================================
# TEST REQUEST OPERATIONS (8 tests)
# ============================================================================

class TestRequestOperations:
    """Test REQUEST creation, listing, and deletion"""

    def test_create_request(self, barter_service):
        """Test creating a new request"""
        request = barter_service.create_request(
            user="test@localhost",
            request_type=OfferType.RESOURCE,
            title="Need firewood",
            description="For winter heating",
            tags=["firewood", "winter", "heating"],
            urgency="high"
        )

        assert request.id.startswith("REQ_")
        assert request.user == "test@localhost"
        assert request.type == OfferType.RESOURCE
        assert request.urgency == "high"

    def test_list_all_requests(self, barter_service, sample_request):
        """Test listing all requests"""
        requests = barter_service.list_requests()
        assert len(requests) >= 1
        assert any(r.id == sample_request.id for r in requests)

    def test_list_requests_by_user(self, barter_service, sample_request):
        """Test filtering requests by user"""
        requests = barter_service.list_requests(user="bob@localhost")
        assert all(r.user == "bob@localhost" for r in requests)

    def test_list_requests_by_type(self, barter_service, sample_request):
        """Test filtering requests by type"""
        requests = barter_service.list_requests(request_type=OfferType.SKILL)
        assert all(r.type == OfferType.SKILL for r in requests)

    def test_get_specific_request(self, barter_service, sample_request):
        """Test retrieving specific request"""
        request = barter_service.get_request(sample_request.id)
        assert request is not None
        assert request.id == sample_request.id

    def test_delete_own_request(self, barter_service, sample_request):
        """Test deleting own request"""
        success = barter_service.delete_request(sample_request.id, "bob@localhost")
        assert success is True

        # Verify it's marked inactive
        request = barter_service.get_request(sample_request.id)
        assert request.active is False

    def test_cannot_delete_others_request(self, barter_service, sample_request):
        """Test cannot delete another user's request"""
        success = barter_service.delete_request(sample_request.id, "eve@localhost")
        assert success is False

    def test_request_urgency_levels(self, barter_service):
        """Test different urgency levels"""
        for urgency in ["low", "normal", "high", "critical"]:
            request = barter_service.create_request(
                user="test@localhost",
                request_type=OfferType.SERVICE,
                title=f"Test {urgency}",
                description="Test",
                tags=["test"],
                urgency=urgency
            )
            assert request.urgency == urgency


# ============================================================================
# TEST TRADE EXECUTION (10 tests)
# ============================================================================

class TestTradeExecution:
    """Test TRADE proposal, acceptance, completion, cancellation"""

    def test_propose_trade(self, barter_service, sample_offer, sample_request):
        """Test proposing a trade"""
        trade = barter_service.propose_trade(
            offer_id=sample_offer.id,
            request_id=sample_request.id,
            user="alice@localhost"  # Offerer proposes
        )

        assert trade is not None
        assert trade.id.startswith("TRD_")
        assert trade.offer_id == sample_offer.id
        assert trade.request_id == sample_request.id
        assert trade.status == TradeStatus.PROPOSED

    def test_propose_trade_as_requester(self, barter_service, sample_offer, sample_request):
        """Test requester can also propose trade"""
        trade = barter_service.propose_trade(
            offer_id=sample_offer.id,
            request_id=sample_request.id,
            user="bob@localhost"  # Requester proposes
        )

        assert trade is not None
        assert trade.offerer == "alice@localhost"
        assert trade.requester == "bob@localhost"

    def test_accept_trade(self, barter_service, sample_offer, sample_request):
        """Test accepting a proposed trade"""
        trade = barter_service.propose_trade(
            offer_id=sample_offer.id,
            request_id=sample_request.id,
            user="alice@localhost"
        )

        # Bob accepts
        success = barter_service.accept_trade(trade.id, "bob@localhost")
        assert success is True

        # Verify status changed
        trades = barter_service.list_trades()
        accepted_trade = next(t for t in trades if t.id == trade.id)
        assert accepted_trade.status == TradeStatus.ACCEPTED

    def test_cannot_accept_own_trade(self, barter_service, sample_offer, sample_request):
        """Test cannot accept own trade proposal"""
        trade = barter_service.propose_trade(
            offer_id=sample_offer.id,
            request_id=sample_request.id,
            user="alice@localhost"
        )

        # Alice tries to accept her own proposal
        success = barter_service.accept_trade(trade.id, "alice@localhost")
        assert success is False

    def test_complete_trade_both_parties(self, barter_service, sample_offer, sample_request):
        """Test completing trade requires both parties to rate"""
        trade = barter_service.propose_trade(
            offer_id=sample_offer.id,
            request_id=sample_request.id,
            user="alice@localhost"
        )
        barter_service.accept_trade(trade.id, "bob@localhost")

        # Alice rates first
        barter_service.complete_trade(trade.id, "alice@localhost", 5)
        trades = barter_service.list_trades()
        trade1 = next(t for t in trades if t.id == trade.id)
        assert trade1.status == TradeStatus.ACCEPTED  # Not yet complete

        # Bob rates second
        barter_service.complete_trade(trade.id, "bob@localhost", 4)
        trades = barter_service.list_trades()
        trade2 = next(t for t in trades if t.id == trade.id)
        assert trade2.status == TradeStatus.COMPLETED  # Now complete

    def test_complete_trade_updates_reputation(self, barter_service, sample_offer, sample_request):
        """Test completing trade updates both users' reputation"""
        trade = barter_service.propose_trade(
            offer_id=sample_offer.id,
            request_id=sample_request.id,
            user="alice@localhost"
        )
        barter_service.accept_trade(trade.id, "bob@localhost")

        # Complete trade
        barter_service.complete_trade(trade.id, "alice@localhost", 5)
        barter_service.complete_trade(trade.id, "bob@localhost", 4)

        # Check reputation updated
        alice_rep = barter_service.get_reputation("alice@localhost")
        bob_rep = barter_service.get_reputation("bob@localhost")

        assert alice_rep['total_trades'] == 1
        assert bob_rep['total_trades'] == 1
        assert alice_rep['avg_rating'] == 4.0  # Bob rated Alice 4
        assert bob_rep['avg_rating'] == 5.0   # Alice rated Bob 5

    def test_cancel_trade(self, barter_service, sample_offer, sample_request):
        """Test canceling a trade"""
        trade = barter_service.propose_trade(
            offer_id=sample_offer.id,
            request_id=sample_request.id,
            user="alice@localhost"
        )

        success = barter_service.cancel_trade(trade.id, "alice@localhost", "Changed my mind")
        assert success is True

        trades = barter_service.list_trades()
        cancelled_trade = next(t for t in trades if t.id == trade.id)
        assert cancelled_trade.status == TradeStatus.CANCELLED

    def test_list_trades_by_user(self, barter_service, sample_offer, sample_request):
        """Test filtering trades by user"""
        trade = barter_service.propose_trade(
            offer_id=sample_offer.id,
            request_id=sample_request.id,
            user="alice@localhost"
        )

        alice_trades = barter_service.list_trades(user="alice@localhost")
        assert len(alice_trades) >= 1
        assert any(t.id == trade.id for t in alice_trades)

    def test_list_trades_by_status(self, barter_service, sample_offer, sample_request):
        """Test filtering trades by status"""
        trade = barter_service.propose_trade(
            offer_id=sample_offer.id,
            request_id=sample_request.id,
            user="alice@localhost"
        )

        proposed_trades = barter_service.list_trades(status=TradeStatus.PROPOSED)
        assert any(t.id == trade.id for t in proposed_trades)

    def test_trade_persistence(self, temp_barter_dir):
        """Test trades persist across service instances"""
        service1 = BarterService(base_path=temp_barter_dir)
        offer = service1.create_offer(
            user="alice@localhost",
            offer_type=OfferType.SKILL,
            title="Test",
            description="Test",
            tags=["test"]
        )
        request = service1.create_request(
            user="bob@localhost",
            request_type=OfferType.SKILL,
            title="Test",
            description="Test",
            tags=["test"]
        )
        trade1 = service1.propose_trade(offer.id, request.id, "alice@localhost")

        # New service instance
        service2 = BarterService(base_path=temp_barter_dir)
        trades = service2.list_trades()
        assert any(t.id == trade1.id for t in trades)


# ============================================================================
# TEST MATCHING ENGINE (10 tests)
# ============================================================================

class TestMatchingEngine:
    """Test 'What I Have' vs 'What I Need' matching algorithm"""

    def test_find_matches_basic(self, barter_service):
        """Test basic matching between offers and requests"""
        # Alice offers Python tutoring
        barter_service.create_offer(
            user="alice@localhost",
            offer_type=OfferType.SKILL,
            title="Python tutoring",
            description="Teach Python programming",
            tags=["python", "tutoring", "programming"]
        )

        # Bob requests Python help
        barter_service.create_request(
            user="bob@localhost",
            request_type=OfferType.SKILL,
            title="Learn Python",
            description="Want to learn Python",
            tags=["python", "programming", "learn"]
        )

        matches = barter_service.find_matches(user="alice@localhost")
        assert len(matches) >= 1

        # Check match has correct structure
        offer, request, score = matches[0]
        assert offer.user == "alice@localhost"
        assert request.user == "bob@localhost"
        assert 0 <= score <= 1.0

    def test_match_score_calculation(self, barter_service):
        """Test match score based on tag overlap"""
        service = barter_service

        # Test high overlap
        score1 = service._calculate_match_score(
            ["python", "programming", "tutoring"],
            ["python", "programming", "learn"],
            None, None, "normal"
        )
        assert score1 > 0.5  # High tag overlap

        # Test low overlap
        score2 = service._calculate_match_score(
            ["python", "programming"],
            ["woodworking", "crafts"],
            None, None, "normal"
        )
        assert score2 < 0.3  # Low tag overlap

    def test_location_matching_bonus(self, barter_service):
        """Test location matching increases score"""
        service = barter_service

        # Same location
        score_same = service._calculate_match_score(
            ["test"],
            ["test"],
            "Melbourne", "Melbourne",
            "normal"
        )

        # Different location
        score_diff = service._calculate_match_score(
            ["test"],
            ["test"],
            "Melbourne", "Sydney",
            "normal"
        )

        assert score_same > score_diff

    def test_urgency_affects_score(self, barter_service):
        """Test urgency level affects match score"""
        service = barter_service

        score_low = service._calculate_match_score(
            ["test"], ["test"], None, None, "low"
        )
        score_critical = service._calculate_match_score(
            ["test"], ["test"], None, None, "critical"
        )

        assert score_critical > score_low

    def test_type_mismatch_no_match(self, barter_service):
        """Test different types don't match"""
        # Alice offers skill
        barter_service.create_offer(
            user="alice@localhost",
            offer_type=OfferType.SKILL,
            title="Python tutoring",
            description="Teach Python",
            tags=["python"]
        )

        # Bob requests resource (not skill)
        barter_service.create_request(
            user="bob@localhost",
            request_type=OfferType.RESOURCE,
            title="Computer",
            description="Need a computer",
            tags=["computer"]
        )

        matches = barter_service.find_matches(user="alice@localhost")
        # Should have no matches or very low score
        assert len(matches) == 0 or all(score < 0.3 for _, _, score in matches)

    def test_match_limit(self, barter_service):
        """Test match result limit"""
        # Create many offers and requests
        for i in range(20):
            barter_service.create_offer(
                user=f"user{i}@localhost",
                offer_type=OfferType.SKILL,
                title=f"Skill {i}",
                description="Test",
                tags=["test", "skill"]
            )

        barter_service.create_request(
            user="alice@localhost",
            request_type=OfferType.SKILL,
            title="Need skills",
            description="Test",
            tags=["test", "skill"]
        )

        matches = barter_service.find_matches(user="alice@localhost", limit=5)
        assert len(matches) <= 5

    def test_bidirectional_matching(self, barter_service):
        """Test matching works in both directions"""
        # Alice offers and requests
        alice_offer = barter_service.create_offer(
            user="alice@localhost",
            offer_type=OfferType.SKILL,
            title="Python tutoring",
            description="Teach Python",
            tags=["python", "tutoring"]
        )
        alice_request = barter_service.create_request(
            user="alice@localhost",
            request_type=OfferType.TOOL,
            title="Need hammer",
            description="For building",
            tags=["hammer", "tool", "building"]
        )

        # Bob offers and requests (opposite)
        bob_offer = barter_service.create_offer(
            user="bob@localhost",
            offer_type=OfferType.TOOL,
            title="Hammer for loan",
            description="Can lend hammer",
            tags=["hammer", "tool", "loan"]
        )
        bob_request = barter_service.create_request(
            user="bob@localhost",
            request_type=OfferType.SKILL,
            title="Learn Python",
            description="Want to learn Python",
            tags=["python", "learn"]
        )

        # Both should find matches
        alice_matches = barter_service.find_matches(user="alice@localhost")
        bob_matches = barter_service.find_matches(user="bob@localhost")

        assert len(alice_matches) >= 2  # Hammer and Python
        assert len(bob_matches) >= 2    # Python and Hammer

    def test_no_self_matching(self, barter_service):
        """Test user doesn't match with own offers/requests"""
        barter_service.create_offer(
            user="alice@localhost",
            offer_type=OfferType.SKILL,
            title="Python",
            description="Test",
            tags=["python"]
        )
        barter_service.create_request(
            user="alice@localhost",
            request_type=OfferType.SKILL,
            title="Python",
            description="Test",
            tags=["python"]
        )

        matches = barter_service.find_matches(user="alice@localhost")
        # Should have no self-matches
        for offer, request, _ in matches:
            assert not (offer.user == "alice@localhost" and request.user == "alice@localhost")

    def test_match_score_ordering(self, barter_service):
        """Test matches are ordered by score (best first)"""
        # Create high-match request
        barter_service.create_request(
            user="bob@localhost",
            request_type=OfferType.SKILL,
            title="Python expert needed",
            description="Need advanced Python help",
            tags=["python", "expert", "advanced", "help"]
        )

        # Create low-match request
        barter_service.create_request(
            user="charlie@localhost",
            request_type=OfferType.SKILL,
            title="Basic coding",
            description="Learn basics",
            tags=["coding", "basics"]
        )

        # Alice offers Python expertise
        barter_service.create_offer(
            user="alice@localhost",
            offer_type=OfferType.SKILL,
            title="Python expert",
            description="Advanced Python tutoring",
            tags=["python", "expert", "advanced", "tutoring"]
        )

        matches = barter_service.find_matches(user="alice@localhost")
        if len(matches) >= 2:
            # Scores should be descending
            for i in range(len(matches) - 1):
                assert matches[i][2] >= matches[i+1][2]

    def test_inactive_not_matched(self, barter_service):
        """Test inactive offers/requests are not matched"""
        offer = barter_service.create_offer(
            user="alice@localhost",
            offer_type=OfferType.SKILL,
            title="Python",
            description="Test",
            tags=["python"]
        )

        # Deactivate offer
        barter_service.delete_offer(offer.id, "alice@localhost")

        # Create matching request
        barter_service.create_request(
            user="bob@localhost",
            request_type=OfferType.SKILL,
            title="Python",
            description="Test",
            tags=["python"]
        )

        matches = barter_service.find_matches(user="bob@localhost")
        # Should not match inactive offer
        assert all(o.id != offer.id for o, _, _ in matches)


# ============================================================================
# TEST REPUTATION SYSTEM (6 tests)
# ============================================================================

class TestReputationSystem:
    """Test reputation tracking and leaderboard"""

    def test_initial_reputation(self, barter_service):
        """Test new user has zero reputation"""
        rep = barter_service.get_reputation("newuser@localhost")
        assert rep['total_trades'] == 0
        assert rep['total_rating'] == 0
        assert rep['avg_rating'] == 0.0

    def test_reputation_after_trade(self, barter_service):
        """Test reputation updates after completed trade"""
        # Create and complete a trade
        offer = barter_service.create_offer(
            user="alice@localhost",
            offer_type=OfferType.SKILL,
            title="Test",
            description="Test",
            tags=["test"]
        )
        request = barter_service.create_request(
            user="bob@localhost",
            request_type=OfferType.SKILL,
            title="Test",
            description="Test",
            tags=["test"]
        )
        trade = barter_service.propose_trade(offer.id, request.id, "alice@localhost")
        barter_service.accept_trade(trade.id, "bob@localhost")
        barter_service.complete_trade(trade.id, "alice@localhost", 5)
        barter_service.complete_trade(trade.id, "bob@localhost", 4)

        alice_rep = barter_service.get_reputation("alice@localhost")
        bob_rep = barter_service.get_reputation("bob@localhost")

        assert alice_rep['total_trades'] == 1
        assert alice_rep['avg_rating'] == 4.0
        assert bob_rep['total_trades'] == 1
        assert bob_rep['avg_rating'] == 5.0

    def test_reputation_average_calculation(self, barter_service):
        """Test average rating calculated correctly over multiple trades"""
        # Simulate multiple completed trades for Alice
        ratings = [5, 4, 5, 3, 4]

        for rating in ratings:
            barter_service._update_reputation("alice@localhost", rating)

        rep = barter_service.get_reputation("alice@localhost")
        expected_avg = sum(ratings) / len(ratings)

        assert rep['total_trades'] == len(ratings)
        assert abs(rep['avg_rating'] - expected_avg) < 0.01

    def test_reputation_history(self, barter_service):
        """Test reputation includes rating history"""
        barter_service._update_reputation("alice@localhost", 5)
        barter_service._update_reputation("alice@localhost", 4)

        rep = barter_service.get_reputation("alice@localhost")
        assert len(rep['ratings']) == 2
        assert rep['ratings'][0]['rating'] == 5
        assert rep['ratings'][1]['rating'] == 4

    def test_leaderboard_minimum_trades(self, barter_service):
        """Test leaderboard requires 3+ trades"""
        # User with 2 trades (below threshold)
        barter_service._update_reputation("alice@localhost", 5)
        barter_service._update_reputation("alice@localhost", 5)

        # User with 3 trades (at threshold)
        for _ in range(3):
            barter_service._update_reputation("bob@localhost", 5)

        leaderboard = barter_service.get_leaderboard()

        # Alice should not be in leaderboard
        assert not any(t['user'] == "alice@localhost" for t in leaderboard)
        # Bob should be in leaderboard
        assert any(t['user'] == "bob@localhost" for t in leaderboard)

    def test_leaderboard_ordering(self, barter_service):
        """Test leaderboard ordered by average rating"""
        # Create users with different ratings
        for _ in range(3):
            barter_service._update_reputation("alice@localhost", 5)  # 5.0 avg
        for _ in range(3):
            barter_service._update_reputation("bob@localhost", 4)    # 4.0 avg
        for _ in range(3):
            barter_service._update_reputation("charlie@localhost", 3)  # 3.0 avg

        leaderboard = barter_service.get_leaderboard()

        assert len(leaderboard) >= 3
        # Check descending order
        for i in range(len(leaderboard) - 1):
            assert leaderboard[i]['avg_rating'] >= leaderboard[i+1]['avg_rating']


# ============================================================================
# TEST ERROR HANDLING (5 tests)
# ============================================================================

class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_invalid_offer_type(self, barter_handler):
        """Test creating offer with invalid type"""
        result = barter_handler._offer_create(["invalidtype", "Test title"])
        assert "Invalid type" in result

    def test_missing_offer_arguments(self, barter_handler):
        """Test creating offer without required arguments"""
        result = barter_handler._offer_create(["skill"])
        assert "Usage" in result or "❌" in result

    def test_delete_nonexistent_offer(self, barter_handler, barter_service):
        """Test deleting non-existent offer"""
        barter_handler.barter_service = barter_service
        result = barter_handler._offer_delete(["NONEXISTENT_ID"])
        assert "Could not delete" in result or "not found" in result

    def test_propose_trade_invalid_ids(self, barter_service):
        """Test proposing trade with invalid IDs"""
        trade = barter_service.propose_trade(
            offer_id="INVALID_OFFER",
            request_id="INVALID_REQUEST",
            user="test@localhost"
        )
        assert trade is None

    def test_complete_trade_invalid_rating(self, barter_handler):
        """Test completing trade with invalid rating"""
        result = barter_handler._trade_complete(["TRD_123", "10"])  # Rating out of range
        assert "Rating must be 1-5" in result


# ============================================================================
# TEST INTEGRATION SCENARIOS (8 tests)
# ============================================================================

class TestIntegrationScenarios:
    """Test complete workflows and integration scenarios"""

    def test_full_barter_workflow(self, barter_service):
        """Test complete barter workflow from offer to completion"""
        # 1. Alice creates offer
        offer = barter_service.create_offer(
            user="alice@localhost",
            offer_type=OfferType.SKILL,
            title="Python tutoring",
            description="Teach Python basics",
            tags=["python", "tutoring", "basics"]
        )
        assert offer.active is True

        # 2. Bob creates request
        request = barter_service.create_request(
            user="bob@localhost",
            request_type=OfferType.SKILL,
            title="Learn Python",
            description="Want to learn programming",
            tags=["python", "programming", "learn"]
        )
        assert request.active is True

        # 3. Find matches
        matches = barter_service.find_matches(user="alice@localhost")
        assert len(matches) >= 1

        # 4. Propose trade
        trade = barter_service.propose_trade(offer.id, request.id, "alice@localhost")
        assert trade.status == TradeStatus.PROPOSED

        # 5. Accept trade
        success = barter_service.accept_trade(trade.id, "bob@localhost")
        assert success is True

        # 6. Complete trade
        barter_service.complete_trade(trade.id, "alice@localhost", 5)
        barter_service.complete_trade(trade.id, "bob@localhost", 5)

        # 7. Verify completion
        trades = barter_service.list_trades(user="alice@localhost")
        completed_trade = next(t for t in trades if t.id == trade.id)
        assert completed_trade.status == TradeStatus.COMPLETED

        # 8. Check reputation
        alice_rep = barter_service.get_reputation("alice@localhost")
        bob_rep = barter_service.get_reputation("bob@localhost")
        assert alice_rep['total_trades'] == 1
        assert bob_rep['total_trades'] == 1

    def test_multi_user_marketplace(self, barter_service):
        """Test marketplace with multiple users and trades"""
        users = ["alice@localhost", "bob@localhost", "charlie@localhost"]

        # Each user creates offers and requests
        for i, user in enumerate(users):
            barter_service.create_offer(
                user=user,
                offer_type=OfferType.SKILL,
                title=f"Skill {i}",
                description="Test skill",
                tags=["skill", f"type{i}"]
            )
            barter_service.create_request(
                user=user,
                request_type=OfferType.SKILL,
                title=f"Need skill {(i+1)%3}",
                description="Test request",
                tags=["skill", f"type{(i+1)%3}"]
            )

        # Everyone should find matches
        for user in users:
            matches = barter_service.find_matches(user=user)
            assert len(matches) > 0

    def test_concurrent_trades(self, barter_service):
        """Test user can have multiple active trades"""
        # Alice creates multiple offers
        offer1 = barter_service.create_offer(
            user="alice@localhost",
            offer_type=OfferType.SKILL,
            title="Python",
            description="Test",
            tags=["python"]
        )
        offer2 = barter_service.create_offer(
            user="alice@localhost",
            offer_type=OfferType.TOOL,
            title="Hammer",
            description="Test",
            tags=["hammer"]
        )

        # Different users request
        request1 = barter_service.create_request(
            user="bob@localhost",
            request_type=OfferType.SKILL,
            title="Python",
            description="Test",
            tags=["python"]
        )
        request2 = barter_service.create_request(
            user="charlie@localhost",
            request_type=OfferType.TOOL,
            title="Hammer",
            description="Test",
            tags=["hammer"]
        )

        # Create multiple trades
        trade1 = barter_service.propose_trade(offer1.id, request1.id, "alice@localhost")
        trade2 = barter_service.propose_trade(offer2.id, request2.id, "alice@localhost")

        # Alice should have 2 active trades
        alice_trades = barter_service.list_trades(user="alice@localhost")
        assert len(alice_trades) == 2

    def test_trade_cancellation_workflow(self, barter_service):
        """Test trade cancellation at different stages"""
        offer = barter_service.create_offer(
            user="alice@localhost",
            offer_type=OfferType.SKILL,
            title="Test",
            description="Test",
            tags=["test"]
        )
        request = barter_service.create_request(
            user="bob@localhost",
            request_type=OfferType.SKILL,
            title="Test",
            description="Test",
            tags=["test"]
        )

        # Cancel at PROPOSED stage
        trade1 = barter_service.propose_trade(offer.id, request.id, "alice@localhost")
        success = barter_service.cancel_trade(trade1.id, "alice@localhost", "Test cancel")
        assert success is True

        # Cancel at ACCEPTED stage
        trade2 = barter_service.propose_trade(offer.id, request.id, "alice@localhost")
        barter_service.accept_trade(trade2.id, "bob@localhost")
        success = barter_service.cancel_trade(trade2.id, "bob@localhost", "Changed mind")
        assert success is True

    def test_reputation_across_multiple_trades(self, barter_service):
        """Test reputation builds correctly across multiple trades"""
        # Simulate Alice completing 5 trades with different ratings
        ratings_for_alice = [5, 4, 5, 3, 4]

        for i, rating in enumerate(ratings_for_alice):
            offer = barter_service.create_offer(
                user="alice@localhost",
                offer_type=OfferType.SKILL,
                title=f"Offer {i}",
                description="Test",
                tags=["test"]
            )
            request = barter_service.create_request(
                user=f"user{i}@localhost",
                request_type=OfferType.SKILL,
                title=f"Request {i}",
                description="Test",
                tags=["test"]
            )
            trade = barter_service.propose_trade(offer.id, request.id, "alice@localhost")
            barter_service.accept_trade(trade.id, f"user{i}@localhost")
            barter_service.complete_trade(trade.id, f"user{i}@localhost", rating)
            barter_service.complete_trade(trade.id, "alice@localhost", 5)

        alice_rep = barter_service.get_reputation("alice@localhost")
        expected_avg = sum(ratings_for_alice) / len(ratings_for_alice)

        assert alice_rep['total_trades'] == 5
        assert abs(alice_rep['avg_rating'] - expected_avg) < 0.01

    def test_data_persistence_full_cycle(self, temp_barter_dir):
        """Test all data persists correctly across service restarts"""
        # Create initial data
        service1 = BarterService(base_path=temp_barter_dir)
        offer = service1.create_offer(
            user="alice@localhost",
            offer_type=OfferType.SKILL,
            title="Python",
            description="Test",
            tags=["python"]
        )
        request = service1.create_request(
            user="bob@localhost",
            request_type=OfferType.SKILL,
            title="Python",
            description="Test",
            tags=["python"]
        )
        trade = service1.propose_trade(offer.id, request.id, "alice@localhost")

        # Restart service
        service2 = BarterService(base_path=temp_barter_dir)

        # Verify all data persisted
        assert service2.get_offer(offer.id) is not None
        assert service2.get_request(request.id) is not None
        trades = service2.list_trades()
        assert any(t.id == trade.id for t in trades)

    def test_edge_case_empty_marketplace(self, barter_service):
        """Test operations on empty marketplace"""
        # List operations should return empty
        assert len(barter_service.list_offers()) == 0
        assert len(barter_service.list_requests()) == 0
        assert len(barter_service.list_trades()) == 0

        # Find matches should return empty
        matches = barter_service.find_matches(user="test@localhost")
        assert len(matches) == 0

        # Get non-existent should return None
        assert barter_service.get_offer("NONEXISTENT") is None
        assert barter_service.get_request("NONEXISTENT") is None

    def test_special_characters_in_content(self, barter_service):
        """Test handling special characters in titles/descriptions"""
        offer = barter_service.create_offer(
            user="alice@localhost",
            offer_type=OfferType.SKILL,
            title="Test with émojis 🚀 and spëcial çhars!",
            description="Description with \"quotes\" and 'apostrophes'",
            tags=["test", "special"]
        )

        retrieved = barter_service.get_offer(offer.id)
        assert retrieved.title == "Test with émojis 🚀 and spëcial çhars!"
        assert "quotes" in retrieved.description


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

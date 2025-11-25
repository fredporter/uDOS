"""
uDOS v1.0.33 - Barter Service

Zero-currency economy system for exchanging knowledge, skills, and resources.

Features:
- OFFER: Post what you have to trade
- REQUEST: Post what you need
- Matching engine: "What I Have" vs "What I Need"
- Reputation tracking: Community-driven trust
- Offline-first: All data local, P2P sync later
- No currency: Direct barter only

Philosophy: Real community resilience through skill/resource sharing, not wealth exchange.

Version: 1.0.33
Author: uDOS Development Team
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum


class OfferType(Enum):
    """Types of things that can be offered"""
    SKILL = "skill"           # Teaching/doing a skill
    KNOWLEDGE = "knowledge"   # Information/documentation
    RESOURCE = "resource"     # Physical items
    SERVICE = "service"       # Time/labor
    TOOL = "tool"            # Equipment/devices


class TradeStatus(Enum):
    """Status of a trade transaction"""
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"


@dataclass
class Offer:
    """An offer to provide something"""
    id: str
    user: str
    type: OfferType
    title: str
    description: str
    tags: List[str]
    location: Optional[str] = None
    created: str = ""
    expires: Optional[str] = None
    active: bool = True

    def to_dict(self) -> Dict:
        data = asdict(self)
        data['type'] = self.type.value
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'Offer':
        data['type'] = OfferType(data['type'])
        return cls(**data)


@dataclass
class Request:
    """A request for something needed"""
    id: str
    user: str
    type: OfferType
    title: str
    description: str
    tags: List[str]
    location: Optional[str] = None
    created: str = ""
    expires: Optional[str] = None
    active: bool = True
    urgency: str = "normal"  # low, normal, high, critical

    def to_dict(self) -> Dict:
        data = asdict(self)
        data['type'] = self.type.value
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'Request':
        data['type'] = OfferType(data['type'])
        return cls(**data)


@dataclass
class Trade:
    """A barter transaction between two parties"""
    id: str
    offer_id: str
    request_id: str
    offerer: str
    requester: str
    status: TradeStatus
    created: str
    proposed_by: Optional[str] = None  # Who proposed the trade
    completed: Optional[str] = None
    rating_offerer: Optional[int] = None  # 1-5 stars
    rating_requester: Optional[int] = None
    notes: str = ""

    def to_dict(self) -> Dict:
        data = asdict(self)
        data['status'] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'Trade':
        data['status'] = TradeStatus(data['status'])
        return cls(**data)


class BarterService:
    """Service for managing the barter economy"""

    def __init__(self, base_path: Optional[Path] = None):
        """Initialize barter service (v1.5.0: Uses new ConfigManager)"""
        if base_path is None:
            try:
                from core.uDOS_main import get_config
                config = get_config()
                project_root = config.get('UDOS_INSTALL_PATH', str(Path.cwd()))
                base_path = Path(project_root) / "memory" / "barter"
            except Exception:
                # Fallback to current working directory
                base_path = Path.cwd() / "memory" / "barter"

        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

        self.offers_file = self.base_path / "offers.json"
        self.requests_file = self.base_path / "requests.json"
        self.trades_file = self.base_path / "trades.json"
        self.reputation_file = self.base_path / "reputation.json"

        # Initialize files if they don't exist
        self._init_storage()

    def _init_storage(self):
        """Initialize storage files"""
        for file in [self.offers_file, self.requests_file,
                     self.trades_file, self.reputation_file]:
            if not file.exists():
                file.write_text(json.dumps([], indent=2))

    def _load_json(self, file: Path) -> List[Dict]:
        """Load JSON data from file"""
        try:
            return json.loads(file.read_text())
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_json(self, file: Path, data: List[Dict]):
        """Save JSON data to file, converting enums to values"""
        # Convert any remaining enums to their values
        def convert_enums(obj):
            if isinstance(obj, dict):
                return {k: convert_enums(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_enums(item) for item in obj]
            elif isinstance(obj, (OfferType, TradeStatus)):
                return obj.value
            else:
                return obj

        cleaned_data = convert_enums(data)
        file.write_text(json.dumps(cleaned_data, indent=2))

    def _generate_id(self, prefix: str) -> str:
        """Generate unique ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        return f"{prefix}_{timestamp}"

    # ========================================================================
    # OFFER OPERATIONS
    # ========================================================================

    def create_offer(self, user: str, offer_type: OfferType, title: str,
                    description: str, tags: List[str],
                    location: Optional[str] = None,
                    expires: Optional[str] = None) -> Offer:
        """Create a new offer"""
        offer = Offer(
            id=self._generate_id("OFR"),
            user=user,
            type=offer_type,
            title=title,
            description=description,
            tags=tags,
            location=location,
            created=datetime.now().isoformat(),
            expires=expires,
            active=True
        )

        offers = self._load_json(self.offers_file)
        offers.append(offer.to_dict())
        self._save_json(self.offers_file, offers)

        return offer

    def list_offers(self, user: Optional[str] = None,
                   offer_type: Optional[OfferType] = None,
                   active_only: bool = True) -> List[Offer]:
        """List offers with optional filters"""
        offers_data = self._load_json(self.offers_file)
        offers = [Offer.from_dict(o) for o in offers_data]

        # Apply filters
        if user:
            offers = [o for o in offers if o.user == user]
        if offer_type:
            offers = [o for o in offers if o.type == offer_type]
        if active_only:
            offers = [o for o in offers if o.active]

        return offers

    def get_offer(self, offer_id: str) -> Optional[Offer]:
        """Get a specific offer by ID"""
        offers_data = self._load_json(self.offers_file)
        for o in offers_data:
            if o['id'] == offer_id:
                return Offer.from_dict(o)
        return None

    def delete_offer(self, offer_id: str, user: str) -> bool:
        """Delete/deactivate an offer (only by owner)"""
        offers_data = self._load_json(self.offers_file)
        for i, o in enumerate(offers_data):
            if o['id'] == offer_id and o['user'] == user:
                offers_data[i]['active'] = False
                self._save_json(self.offers_file, offers_data)
                return True
        return False

    # ========================================================================
    # REQUEST OPERATIONS
    # ========================================================================

    def create_request(self, user: str, request_type: OfferType, title: str,
                      description: str, tags: List[str],
                      location: Optional[str] = None,
                      urgency: str = "normal",
                      expires: Optional[str] = None) -> Request:
        """Create a new request"""
        request = Request(
            id=self._generate_id("REQ"),
            user=user,
            type=request_type,
            title=title,
            description=description,
            tags=tags,
            location=location,
            created=datetime.now().isoformat(),
            urgency=urgency,
            expires=expires,
            active=True
        )

        requests = self._load_json(self.requests_file)
        requests.append(request.to_dict())
        self._save_json(self.requests_file, requests)

        return request

    def list_requests(self, user: Optional[str] = None,
                     request_type: Optional[OfferType] = None,
                     active_only: bool = True) -> List[Request]:
        """List requests with optional filters"""
        requests_data = self._load_json(self.requests_file)
        requests = [Request.from_dict(r) for r in requests_data]

        # Apply filters
        if user:
            requests = [r for r in requests if r.user == user]
        if request_type:
            requests = [r for r in requests if r.type == request_type]
        if active_only:
            requests = [r for r in requests if r.active]

        return requests

    def get_request(self, request_id: str) -> Optional[Request]:
        """Get a specific request by ID"""
        requests_data = self._load_json(self.requests_file)
        for r in requests_data:
            if r['id'] == request_id:
                return Request.from_dict(r)
        return None

    def delete_request(self, request_id: str, user: str) -> bool:
        """Delete/deactivate a request (only by owner)"""
        requests_data = self._load_json(self.requests_file)
        for i, r in enumerate(requests_data):
            if r['id'] == request_id and r['user'] == user:
                requests_data[i]['active'] = False
                self._save_json(self.requests_file, requests_data)
                return True
        return False

    # ========================================================================
    # MATCHING ENGINE - "What I Have" vs "What I Need"
    # ========================================================================

    def find_matches(self, user: str, limit: int = 10) -> List[Tuple[Offer, Request, float]]:
        """
        Find matching trades for a user.
        Returns list of (offer, request, match_score) tuples.

        Algorithm:
        1. User's offers matched against others' requests
        2. User's requests matched against others' offers
        3. Score based on: tag overlap, location proximity, urgency
        """
        my_offers = self.list_offers(user=user)
        my_requests = self.list_requests(user=user)

        all_offers = [o for o in self.list_offers() if o.user != user]
        all_requests = [r for r in self.list_requests() if r.user != user]

        matches = []

        # My offers <-> Their requests
        for my_offer in my_offers:
            for their_request in all_requests:
                if my_offer.type == their_request.type:
                    score = self._calculate_match_score(
                        my_offer.tags, their_request.tags,
                        my_offer.location, their_request.location,
                        their_request.urgency
                    )
                    if score > 0.3:  # Threshold for relevance
                        matches.append((my_offer, their_request, score))

        # Their offers <-> My requests
        for their_offer in all_offers:
            for my_request in my_requests:
                if their_offer.type == my_request.type:
                    score = self._calculate_match_score(
                        their_offer.tags, my_request.tags,
                        their_offer.location, my_request.location,
                        my_request.urgency
                    )
                    if score > 0.3:
                        matches.append((their_offer, my_request, score))

        # Sort by score (descending)
        matches.sort(key=lambda x: x[2], reverse=True)

        return matches[:limit]

    def _calculate_match_score(self, tags1: List[str], tags2: List[str],
                               loc1: Optional[str], loc2: Optional[str],
                               urgency: str = "normal") -> float:
        """Calculate match score between offer and request"""
        score = 0.0

        # Tag overlap (0-1)
        if tags1 and tags2:
            common_tags = set(tags1) & set(tags2)
            tag_score = len(common_tags) / max(len(tags1), len(tags2))
            score += tag_score * 0.7  # 70% weight

        # Location match (0-1)
        if loc1 and loc2:
            if loc1.lower() == loc2.lower():
                score += 0.2  # 20% weight

        # Urgency boost (0-1)
        urgency_multiplier = {
            'low': 0.05,
            'normal': 0.1,
            'high': 0.15,
            'critical': 0.2
        }
        score += urgency_multiplier.get(urgency, 0.1)  # 10% weight

        return min(score, 1.0)

    # ========================================================================
    # TRADE OPERATIONS
    # ========================================================================

    def propose_trade(self, offer_id: str, request_id: str,
                     user: str) -> Optional[Trade]:
        """Propose a trade between an offer and request"""
        offer = self.get_offer(offer_id)
        request = self.get_request(request_id)

        if not offer or not request:
            return None

        # Determine who is offerer/requester
        if offer.user == user:
            offerer = offer.user
            requester = request.user
        elif request.user == user:
            offerer = offer.user
            requester = request.user
        else:
            return None  # User not involved in this trade

        trade = Trade(
            id=self._generate_id("TRD"),
            offer_id=offer_id,
            request_id=request_id,
            offerer=offerer,
            requester=requester,
            status=TradeStatus.PROPOSED,
            created=datetime.now().isoformat(),
            proposed_by=user  # Track who proposed
        )

        trades = self._load_json(self.trades_file)
        trades.append(trade.to_dict())
        self._save_json(self.trades_file, trades)

        return trade

    def accept_trade(self, trade_id: str, user: str) -> bool:
        """Accept a proposed trade - only the non-proposer can accept"""
        trades_data = self._load_json(self.trades_file)
        for i, t in enumerate(trades_data):
            if t['id'] == trade_id:
                trade = Trade.from_dict(t)
                # Only allow non-proposer to accept
                if (trade.status == TradeStatus.PROPOSED and
                    user in [trade.offerer, trade.requester] and
                    user != trade.proposed_by):
                    trades_data[i]['status'] = TradeStatus.ACCEPTED.value
                    self._save_json(self.trades_file, trades_data)
                    return True
        return False

    def complete_trade(self, trade_id: str, user: str,
                      rating: int, notes: str = "") -> bool:
        """Mark trade as completed and rate the other party"""
        trades_data = self._load_json(self.trades_file)
        for i, t in enumerate(trades_data):
            if t['id'] == trade_id:
                trade = Trade.from_dict(t)
                if trade.status == TradeStatus.ACCEPTED:
                    if trade.offerer == user:
                        trades_data[i]['rating_requester'] = rating
                    elif trade.requester == user:
                        trades_data[i]['rating_offerer'] = rating

                    # Both rated? Mark complete
                    if (trades_data[i].get('rating_offerer') and
                        trades_data[i].get('rating_requester')):
                        trades_data[i]['status'] = TradeStatus.COMPLETED.value
                        trades_data[i]['completed'] = datetime.now().isoformat()

                        # Update reputation
                        self._update_reputation(trade.offerer,
                                              trades_data[i]['rating_offerer'])
                        self._update_reputation(trade.requester,
                                              trades_data[i]['rating_requester'])

                    trades_data[i]['notes'] = notes
                    self._save_json(self.trades_file, trades_data)
                    return True
        return False

    def cancel_trade(self, trade_id: str, user: str, reason: str = "") -> bool:
        """Cancel a trade"""
        trades_data = self._load_json(self.trades_file)
        for i, t in enumerate(trades_data):
            if t['id'] == trade_id:
                trade = Trade.from_dict(t)
                if trade.offerer == user or trade.requester == user:
                    trades_data[i]['status'] = TradeStatus.CANCELLED.value
                    trades_data[i]['notes'] = reason
                    self._save_json(self.trades_file, trades_data)
                    return True
        return False

    def list_trades(self, user: Optional[str] = None,
                   status: Optional[TradeStatus] = None) -> List[Trade]:
        """List trades with optional filters"""
        trades_data = self._load_json(self.trades_file)
        trades = [Trade.from_dict(t) for t in trades_data]

        if user:
            trades = [t for t in trades
                     if t.offerer == user or t.requester == user]
        if status:
            trades = [t for t in trades if t.status == status]

        return trades

    # ========================================================================
    # REPUTATION SYSTEM
    # ========================================================================

    def _update_reputation(self, user: str, rating: int):
        """Update user reputation based on trade rating"""
        reputation_data = self._load_json(self.reputation_file)

        # Find or create user reputation
        user_rep = None
        for rep in reputation_data:
            if rep['user'] == user:
                user_rep = rep
                break

        if user_rep is None:
            user_rep = {
                'user': user,
                'total_trades': 0,
                'total_rating': 0,
                'avg_rating': 0.0,
                'ratings': []
            }
            reputation_data.append(user_rep)

        # Update stats
        user_rep['total_trades'] += 1
        user_rep['total_rating'] += rating
        user_rep['avg_rating'] = user_rep['total_rating'] / user_rep['total_trades']
        user_rep['ratings'].append({
            'rating': rating,
            'timestamp': datetime.now().isoformat()
        })

        self._save_json(self.reputation_file, reputation_data)

    def get_reputation(self, user: str) -> Dict:
        """Get user reputation"""
        reputation_data = self._load_json(self.reputation_file)
        for rep in reputation_data:
            if rep['user'] == user:
                return rep

        return {
            'user': user,
            'total_trades': 0,
            'total_rating': 0,
            'avg_rating': 0.0,
            'ratings': []
        }

    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get top-rated traders"""
        reputation_data = self._load_json(self.reputation_file)
        # Filter to users with at least 3 trades
        active_traders = [r for r in reputation_data if r['total_trades'] >= 3]
        # Sort by average rating
        active_traders.sort(key=lambda x: x['avg_rating'], reverse=True)
        return active_traders[:limit]

"""
uDOS v1.0.33 - Barter Command Handler

Commands for zero-currency economy:
- OFFER: Post what you have to trade
- REQUEST: Post what you need
- TRADE: Execute barter transactions
- REPUTATION: View trader history
- MATCH: Find compatible trades

Author: uDOS Development Team
Version: 1.0.33
"""

from typing import List
from core.services.barter_service import (
    BarterService, OfferType, TradeStatus, Offer, Request, Trade
)


class BarterCommandHandler:
    """Handler for BARTER economy commands"""

    def __init__(self):
        """Initialize BarterCommandHandler"""
        self.barter_service = BarterService()
        self.current_user = "owner@localhost"  # TODO: Get from session/auth

    def handle(self, command: str, args: List[str]) -> str:
        """
        Route BARTER commands to appropriate handlers

        Args:
            command: Subcommand (OFFER, REQUEST, TRADE, etc.)
            args: Command arguments

        Returns:
            Formatted response string
        """
        if not command or command.upper() == "HELP":
            return self._help()

        command = command.upper()

        handlers = {
            'OFFER': self._offer,
            'REQUEST': self._request,
            'TRADE': self._trade,
            'REPUTATION': self._reputation,
            'REP': self._reputation,     # Alias
            'MATCH': self._match,
            'FIND': self._match,          # Alias
        }

        handler = handlers.get(command)
        if handler:
            return handler(args)
        else:
            return f"❌ Unknown BARTER command: {command}\n\nType 'BARTER HELP' for usage."

    def _help(self) -> str:
        """Display BARTER command help"""
        return """
💰 BARTER - Zero-Currency Economy System

PHILOSOPHY:
  • No money - Direct exchange only
  • Skill & knowledge sharing
  • Community-driven trust (reputation)
  • Offline-first - Local data
  • What I Have ↔ What I Need matching

COMMANDS:
  OFFER CREATE <type> <title> [desc]    Create offer
  OFFER LIST [type]                     List all offers
  OFFER MY                              List my offers
  OFFER DELETE <id>                     Delete my offer

  REQUEST CREATE <type> <title> [desc]  Create request
  REQUEST LIST [type]                   List all requests
  REQUEST MY                            List my requests
  REQUEST DELETE <id>                   Delete my request

  TRADE PROPOSE <offer_id> <request_id> Propose trade
  TRADE ACCEPT <trade_id>               Accept trade
  TRADE COMPLETE <trade_id> <rating>    Complete & rate (1-5)
  TRADE CANCEL <trade_id> [reason]      Cancel trade
  TRADE LIST [status]                   List trades

  MATCH                                 Find compatible trades
  REPUTATION [user]                     View reputation
  REPUTATION TOP                        View leaderboard

OFFER/REQUEST TYPES:
  skill      - Teaching/doing a skill
  knowledge  - Information/documentation
  resource   - Physical items
  service    - Time/labor
  tool       - Equipment/devices

EXAMPLES:
  OFFER CREATE skill "Python tutoring" "Can teach Python basics"
  REQUEST CREATE tool "Raspberry Pi" "Need for IoT project"
  MATCH
  TRADE PROPOSE OFR_20251124_120000 REQ_20251124_115500
  TRADE ACCEPT TRD_20251124_120530
  TRADE COMPLETE TRD_20251124_120530 5

📖 See wiki/Barter-System.md for detailed guide
"""

    # ========================================================================
    # OFFER COMMANDS
    # ========================================================================

    def _offer(self, args: List[str]) -> str:
        """Handle OFFER subcommands"""
        if not args:
            return "❌ Missing subcommand. Use: OFFER CREATE|LIST|MY|DELETE"

        subcommand = args[0].upper()

        if subcommand == "CREATE":
            return self._offer_create(args[1:])
        elif subcommand == "LIST":
            return self._offer_list(args[1:])
        elif subcommand == "MY":
            return self._offer_my()
        elif subcommand == "DELETE":
            return self._offer_delete(args[1:])
        else:
            return f"❌ Unknown OFFER subcommand: {args[0]}"

    def _offer_create(self, args: List[str]) -> str:
        """Create new offer"""
        if len(args) < 2:
            return ("❌ Usage: OFFER CREATE <type> <title> [description]\n"
                   "Types: skill, knowledge, resource, service, tool")

        try:
            offer_type = OfferType(args[0].lower())
        except ValueError:
            return f"❌ Invalid type: {args[0]}. Use: skill, knowledge, resource, service, tool"

        title = args[1]
        description = ' '.join(args[2:]) if len(args) > 2 else ""

        # Extract tags from title and description
        tags = self._extract_tags(title + " " + description)

        offer = self.barter_service.create_offer(
            user=self.current_user,
            offer_type=offer_type,
            title=title,
            description=description,
            tags=tags
        )

        return f"""✅ Offer created!

ID: {offer.id}
Type: {offer.type.value}
Title: {offer.title}
Description: {offer.description}
Tags: {', '.join(offer.tags)}

💡 Use MATCH to find compatible requests
"""

    def _offer_list(self, args: List[str]) -> str:
        """List all offers"""
        offer_type = None
        if args:
            try:
                offer_type = OfferType(args[0].lower())
            except ValueError:
                return f"❌ Invalid type: {args[0]}"

        offers = self.barter_service.list_offers(offer_type=offer_type)

        if not offers:
            return "📭 No active offers found."

        output = [f"📦 Active Offers ({len(offers)})"]
        output.append("=" * 60)

        for offer in offers:
            output.append(f"\nID: {offer.id}")
            output.append(f"Type: {offer.type.value}")
            output.append(f"Title: {offer.title}")
            output.append(f"User: {offer.user}")
            output.append(f"Tags: {', '.join(offer.tags)}")
            if offer.description:
                output.append(f"Description: {offer.description}")
            output.append("-" * 60)

        return '\n'.join(output)

    def _offer_my(self) -> str:
        """List user's offers"""
        offers = self.barter_service.list_offers(user=self.current_user)

        if not offers:
            return "📭 You have no active offers."

        output = [f"📦 My Offers ({len(offers)})"]
        output.append("=" * 60)

        for offer in offers:
            output.append(f"\nID: {offer.id}")
            output.append(f"Type: {offer.type.value}")
            output.append(f"Title: {offer.title}")
            output.append(f"Tags: {', '.join(offer.tags)}")
            output.append(f"Created: {offer.created[:10]}")
            output.append("-" * 60)

        return '\n'.join(output)

    def _offer_delete(self, args: List[str]) -> str:
        """Delete user's offer"""
        if not args:
            return "❌ Usage: OFFER DELETE <offer_id>"

        offer_id = args[0]
        if self.barter_service.delete_offer(offer_id, self.current_user):
            return f"✅ Offer {offer_id} deleted"
        else:
            return f"❌ Could not delete offer {offer_id} (not found or not yours)"

    # ========================================================================
    # REQUEST COMMANDS
    # ========================================================================

    def _request(self, args: List[str]) -> str:
        """Handle REQUEST subcommands"""
        if not args:
            return "❌ Missing subcommand. Use: REQUEST CREATE|LIST|MY|DELETE"

        subcommand = args[0].upper()

        if subcommand == "CREATE":
            return self._request_create(args[1:])
        elif subcommand == "LIST":
            return self._request_list(args[1:])
        elif subcommand == "MY":
            return self._request_my()
        elif subcommand == "DELETE":
            return self._request_delete(args[1:])
        else:
            return f"❌ Unknown REQUEST subcommand: {args[0]}"

    def _request_create(self, args: List[str]) -> str:
        """Create new request"""
        if len(args) < 2:
            return ("❌ Usage: REQUEST CREATE <type> <title> [description]\n"
                   "Types: skill, knowledge, resource, service, tool")

        try:
            request_type = OfferType(args[0].lower())
        except ValueError:
            return f"❌ Invalid type: {args[0]}. Use: skill, knowledge, resource, service, tool"

        title = args[1]
        description = ' '.join(args[2:]) if len(args) > 2 else ""

        # Extract tags from title and description
        tags = self._extract_tags(title + " " + description)

        request = self.barter_service.create_request(
            user=self.current_user,
            request_type=request_type,
            title=title,
            description=description,
            tags=tags
        )

        return f"""✅ Request created!

ID: {request.id}
Type: {request.type.value}
Title: {request.title}
Description: {request.description}
Tags: {', '.join(request.tags)}

💡 Use MATCH to find compatible offers
"""

    def _request_list(self, args: List[str]) -> str:
        """List all requests"""
        request_type = None
        if args:
            try:
                request_type = OfferType(args[0].lower())
            except ValueError:
                return f"❌ Invalid type: {args[0]}"

        requests = self.barter_service.list_requests(request_type=request_type)

        if not requests:
            return "📭 No active requests found."

        output = [f"🔍 Active Requests ({len(requests)})"]
        output.append("=" * 60)

        for request in requests:
            output.append(f"\nID: {request.id}")
            output.append(f"Type: {request.type.value}")
            output.append(f"Title: {request.title}")
            output.append(f"User: {request.user}")
            output.append(f"Urgency: {request.urgency}")
            output.append(f"Tags: {', '.join(request.tags)}")
            if request.description:
                output.append(f"Description: {request.description}")
            output.append("-" * 60)

        return '\n'.join(output)

    def _request_my(self) -> str:
        """List user's requests"""
        requests = self.barter_service.list_requests(user=self.current_user)

        if not requests:
            return "📭 You have no active requests."

        output = [f"🔍 My Requests ({len(requests)})"]
        output.append("=" * 60)

        for request in requests:
            output.append(f"\nID: {request.id}")
            output.append(f"Type: {request.type.value}")
            output.append(f"Title: {request.title}")
            output.append(f"Urgency: {request.urgency}")
            output.append(f"Tags: {', '.join(request.tags)}")
            output.append(f"Created: {request.created[:10]}")
            output.append("-" * 60)

        return '\n'.join(output)

    def _request_delete(self, args: List[str]) -> str:
        """Delete user's request"""
        if not args:
            return "❌ Usage: REQUEST DELETE <request_id>"

        request_id = args[0]
        if self.barter_service.delete_request(request_id, self.current_user):
            return f"✅ Request {request_id} deleted"
        else:
            return f"❌ Could not delete request {request_id} (not found or not yours)"

    # ========================================================================
    # TRADE COMMANDS
    # ========================================================================

    def _trade(self, args: List[str]) -> str:
        """Handle TRADE subcommands"""
        if not args:
            return "❌ Missing subcommand. Use: TRADE PROPOSE|ACCEPT|COMPLETE|CANCEL|LIST"

        subcommand = args[0].upper()

        if subcommand == "PROPOSE":
            return self._trade_propose(args[1:])
        elif subcommand == "ACCEPT":
            return self._trade_accept(args[1:])
        elif subcommand == "COMPLETE":
            return self._trade_complete(args[1:])
        elif subcommand == "CANCEL":
            return self._trade_cancel(args[1:])
        elif subcommand == "LIST":
            return self._trade_list(args[1:])
        else:
            return f"❌ Unknown TRADE subcommand: {args[0]}"

    def _trade_propose(self, args: List[str]) -> str:
        """Propose a trade"""
        if len(args) < 2:
            return "❌ Usage: TRADE PROPOSE <offer_id> <request_id>"

        offer_id = args[0]
        request_id = args[1]

        trade = self.barter_service.propose_trade(
            offer_id=offer_id,
            request_id=request_id,
            user=self.current_user
        )

        if trade:
            return f"""✅ Trade proposed!

Trade ID: {trade.id}
Offer: {offer_id}
Request: {request_id}
Status: {trade.status.value}

⏳ Waiting for other party to accept
"""
        else:
            return "❌ Could not create trade. Check offer/request IDs and permissions."

    def _trade_accept(self, args: List[str]) -> str:
        """Accept a trade"""
        if not args:
            return "❌ Usage: TRADE ACCEPT <trade_id>"

        trade_id = args[0]

        if self.barter_service.accept_trade(trade_id, self.current_user):
            return f"""✅ Trade accepted!

Trade ID: {trade_id}
Status: accepted

💡 Both parties should now complete the exchange, then:
   TRADE COMPLETE {trade_id} <rating 1-5>
"""
        else:
            return "❌ Could not accept trade. Check trade ID and permissions."

    def _trade_complete(self, args: List[str]) -> str:
        """Complete a trade and rate"""
        if len(args) < 2:
            return "❌ Usage: TRADE COMPLETE <trade_id> <rating 1-5>"

        trade_id = args[0]
        try:
            rating = int(args[1])
            if not 1 <= rating <= 5:
                return "❌ Rating must be 1-5"
        except ValueError:
            return "❌ Rating must be a number (1-5)"

        notes = ' '.join(args[2:]) if len(args) > 2 else ""

        if self.barter_service.complete_trade(trade_id, self.current_user, rating, notes):
            return f"""✅ Trade completed!

Trade ID: {trade_id}
Your Rating: {rating}/5 ⭐
Notes: {notes}

💰 Reputation updated for both parties
"""
        else:
            return "❌ Could not complete trade. Check trade ID and status."

    def _trade_cancel(self, args: List[str]) -> str:
        """Cancel a trade"""
        if not args:
            return "❌ Usage: TRADE CANCEL <trade_id> [reason]"

        trade_id = args[0]
        reason = ' '.join(args[1:]) if len(args) > 1 else ""

        if self.barter_service.cancel_trade(trade_id, self.current_user, reason):
            return f"✅ Trade {trade_id} cancelled"
        else:
            return "❌ Could not cancel trade. Check trade ID and permissions."

    def _trade_list(self, args: List[str]) -> str:
        """List trades"""
        status = None
        if args:
            try:
                status = TradeStatus(args[0].lower())
            except ValueError:
                return f"❌ Invalid status: {args[0]}"

        trades = self.barter_service.list_trades(user=self.current_user, status=status)

        if not trades:
            return "📭 No trades found."

        output = [f"🤝 Trades ({len(trades)})"]
        output.append("=" * 60)

        for trade in trades:
            output.append(f"\nTrade ID: {trade.id}")
            output.append(f"Offer: {trade.offer_id}")
            output.append(f"Request: {trade.request_id}")
            output.append(f"Offerer: {trade.offerer}")
            output.append(f"Requester: {trade.requester}")
            output.append(f"Status: {trade.status.value}")
            output.append(f"Created: {trade.created[:10]}")
            if trade.completed:
                output.append(f"Completed: {trade.completed[:10]}")
            if trade.rating_offerer:
                output.append(f"Rating (offerer): {trade.rating_offerer}/5 ⭐")
            if trade.rating_requester:
                output.append(f"Rating (requester): {trade.rating_requester}/5 ⭐")
            output.append("-" * 60)

        return '\n'.join(output)

    # ========================================================================
    # MATCH COMMAND
    # ========================================================================

    def _match(self, args: List[str]) -> str:
        """Find compatible trades"""
        matches = self.barter_service.find_matches(user=self.current_user)

        if not matches:
            return """📭 No matches found.

💡 Tips to increase matches:
   • Create more offers (OFFER CREATE)
   • Create more requests (REQUEST CREATE)
   • Use descriptive tags in titles
   • Specify your location
"""

        output = [f"🎯 Trade Matches ({len(matches)})"]
        output.append("=" * 60)

        for i, (offer, request, score) in enumerate(matches, 1):
            output.append(f"\n{i}. Match Score: {score:.0%}")
            output.append(f"   Offer: {offer.id} - {offer.title}")
            output.append(f"   By: {offer.user}")
            output.append(f"   Request: {request.id} - {request.title}")
            output.append(f"   By: {request.user}")
            output.append(f"   Tags: {', '.join(set(offer.tags) & set(request.tags))}")
            output.append(f"\n   💡 Propose: TRADE PROPOSE {offer.id} {request.id}")
            output.append("-" * 60)

        return '\n'.join(output)

    # ========================================================================
    # REPUTATION COMMAND
    # ========================================================================

    def _reputation(self, args: List[str]) -> str:
        """View reputation"""
        if args and args[0].upper() == "TOP":
            return self._reputation_top()

        user = args[0] if args else self.current_user
        rep = self.barter_service.get_reputation(user)

        if rep['total_trades'] == 0:
            return f"📊 No trading history for {user}"

        output = [f"📊 Reputation: {user}"]
        output.append("=" * 60)
        output.append(f"Total Trades: {rep['total_trades']}")
        output.append(f"Average Rating: {rep['avg_rating']:.2f}/5.00 ⭐")
        output.append(f"Total Rating Points: {rep['total_rating']}")

        if rep['ratings']:
            output.append(f"\nRecent Ratings:")
            for rating_entry in rep['ratings'][-5:]:
                output.append(f"  {rating_entry['rating']}/5 ⭐ - {rating_entry['timestamp'][:10]}")

        return '\n'.join(output)

    def _reputation_top(self) -> str:
        """View reputation leaderboard"""
        leaderboard = self.barter_service.get_leaderboard()

        if not leaderboard:
            return "📊 No traders with 3+ completed trades yet"

        output = ["📊 Top Traders (3+ trades)"]
        output.append("=" * 60)

        for i, trader in enumerate(leaderboard, 1):
            stars = "⭐" * int(trader['avg_rating'])
            output.append(f"{i}. {trader['user']}")
            output.append(f"   {trader['avg_rating']:.2f}/5.00 {stars}")
            output.append(f"   {trader['total_trades']} trades completed")
            output.append("")

        return '\n'.join(output)

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def _extract_tags(self, text: str) -> List[str]:
        """Extract simple tags from text"""
        # Simple word extraction (lowercase, remove punctuation, min 3 chars)
        import re
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        # Remove common words
        stopwords = {'the', 'and', 'for', 'with', 'can', 'will', 'need', 'want'}
        tags = [w for w in words if w not in stopwords]
        # Return unique tags (max 10)
        return list(dict.fromkeys(tags))[:10]

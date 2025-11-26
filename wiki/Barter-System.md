# Barter System

## Overview

The uDOS Barter Economy enables zero-currency exchange of skills, knowledge, resources, and services between community members. Built on trust and mutual aid principles, the system facilitates peer-to-peer trading without requiring money.

**Version**: v1.0.33
**Status**: COMPLETE (2025-11-24)
**Implementation**: `core/services/barter_service.py`, `core/commands/barter_commands.py`
**Tests**: 60/60 passing (100% coverage)

---

## Philosophy

> "What I Have vs What I Need"

The barter system creates a resilient economy where:
- Skills and knowledge have equal value to physical resources
- Reputation is earned through reliable trading
- Location-aware matching connects nearby traders
- Urgency levels prioritize critical needs
- Every transaction strengthens community bonds

---

## Quick Start

### 1. Post an Offer

```
OFFER CREATE skill "Python tutoring" "Can teach Python basics and advanced concepts"
```

System automatically extracts tags: `python, tutoring, basics, advanced, concepts`

### 2. Request What You Need

```
REQUEST CREATE skill "Learn woodworking" "Want to learn furniture making" --urgency high
```

Tags extracted: `learn, woodworking, furniture, making`

### 3. Find Matches

```
MATCH
```

System shows best matches based on:
- Tag overlap (shared keywords)
- Location proximity (if set)
- Urgency levels
- Active offers/requests only

### 4. Propose a Trade

```
TRADE PROPOSE <offer_id> <request_id>
```

### 5. Accept the Trade

```
TRADE ACCEPT <trade_id>
```

Only the non-proposer can accept.

### 6. Complete & Rate

```
TRADE COMPLETE <trade_id> 5
```

Both parties must rate (1-5 stars) to complete the trade.

---

## Command Reference

### OFFER Commands

| Command | Description | Example |
|---------|-------------|---------|
| `OFFER CREATE <type> <title> <description>` | Post a new offer | `OFFER CREATE service "Car repair" "Basic maintenance and diagnostics"` |
| `OFFER LIST [type]` | List all offers (optional filter) | `OFFER LIST skill` |
| `OFFER MY` | List your active offers | `OFFER MY` |
| `OFFER DELETE <id>` | Remove your offer | `OFFER DELETE OFR_20251124_143022_123456` |

**Offer Types**:
- `skill` - Skills you can teach or perform
- `knowledge` - Information you can share
- `service` - Services you can provide
- `tool` - Tools/equipment for loan
- `resource` - Physical resources available

### REQUEST Commands

| Command | Description | Example |
|---------|-------------|---------|
| `REQUEST CREATE <type> <title> <description>` | Post a new request | `REQUEST CREATE resource "Firewood" "Need for winter heating"` |
| `REQUEST LIST [type]` | List all requests | `REQUEST LIST tool` |
| `REQUEST MY` | List your active requests | `REQUEST MY` |
| `REQUEST DELETE <id>` | Remove your request | `REQUEST DELETE REQ_20251124_143530_789012` |

**Urgency Levels** (use `--urgency <level>`):
- `low` - No time pressure
- `normal` - Standard request (default)
- `high` - Needed soon
- `critical` - Urgent need

### TRADE Commands

| Command | Description | Example |
|---------|-------------|---------|
| `TRADE PROPOSE <offer_id> <request_id>` | Propose a trade | `TRADE PROPOSE OFR_123 REQ_456` |
| `TRADE ACCEPT <trade_id>` | Accept a proposal | `TRADE ACCEPT TRD_20251124_144500_345678` |
| `TRADE COMPLETE <trade_id> <rating>` | Complete and rate (1-5) | `TRADE COMPLETE TRD_123 5` |
| `TRADE CANCEL <trade_id> [reason]` | Cancel a trade | `TRADE CANCEL TRD_123 "Changed plans"` |
| `TRADE LIST [status]` | List trades | `TRADE LIST proposed` |

**Trade Statuses**:
- `proposed` - Awaiting acceptance
- `accepted` - Both parties agreed
- `completed` - Finished and rated
- `cancelled` - Trade cancelled

### MATCH Command

```
MATCH
```

Finds best matches between your offers and others' requests, and vice versa.

### REPUTATION Command

| Command | Description |
|---------|-------------|
| `REPUTATION` | View your reputation |
| `REPUTATION <user>` | View another user's reputation |
| `REPUTATION LEADERBOARD` | Top-rated traders (minimum 3 trades) |

---

## Matching Algorithm

### How It Works

The matching engine scores every offer/request pair using:

1. **Tag Overlap** (0.0-1.0)
   - Shared keywords between offers and requests
   - Example: `["python", "tutoring"]` vs `["python", "learn"]` = 50% overlap

2. **Location Proximity** (+0.2 bonus)
   - Same location gets bonus points
   - Requires `LOCATE SET` to be active

3. **Urgency Multiplier** (1.0-2.0x)
   - `critical`: 2.0x boost
   - `high`: 1.5x boost
   - `normal`: 1.0x (no change)
   - `low`: 0.8x reduction

4. **Type Matching** (required)
   - Offer type must match request type
   - `skill` offers only match `skill` requests

### Match Score Formula

```
base_score = (shared_tags / total_unique_tags)
location_bonus = 0.2 if same_location else 0.0
urgency_multiplier = {low: 0.8, normal: 1.0, high: 1.5, critical: 2.0}

final_score = (base_score + location_bonus) * urgency_multiplier
```

### Match Results

Matches are:
- Sorted by score (best first)
- Limited to top 10 by default
- Exclude inactive offers/requests
- Exclude self-matches

---

## Reputation System

### How Reputation Works

1. **Complete Trades**: Both parties must rate each other (1-5 stars)
2. **Average Rating**: Your average across all completed trades
3. **Total Trades**: Number of successfully completed transactions
4. **Leaderboard**: Top traders with 3+ completed trades

### Rating Guidelines

| Rating | Meaning |
|--------|---------|
| ⭐⭐⭐⭐⭐ (5) | Excellent - Exceeded expectations |
| ⭐⭐⭐⭐ (4) | Good - Met expectations |
| ⭐⭐⭐ (3) | Fair - Some issues but acceptable |
| ⭐⭐ (2) | Poor - Did not meet expectations |
| ⭐ (1) | Very Poor - Unreliable or problematic |

### Viewing Reputation

```bash
# Your reputation
REPUTATION

# Output:
Total Trades: 12
Average Rating: 4.7 ⭐
Recent Ratings: [5, 5, 4, 5, 4]

# Leaderboard
REPUTATION LEADERBOARD

# Output:
🏆 Top Community Traders
1. alice@localhost - 4.9 ⭐ (15 trades)
2. bob@localhost - 4.7 ⭐ (12 trades)
3. charlie@localhost - 4.5 ⭐ (8 trades)
```

---

## Usage Examples

### Example 1: Trading Skills

**Alice has**: Python programming knowledge
**Bob needs**: Learn Python

```bash
# Alice creates offer
alice> OFFER CREATE skill "Python tutoring" "Can teach basics to advanced"

# Bob creates request
bob> REQUEST CREATE skill "Learn Python" "Want to learn programming"

# Alice checks for matches
alice> MATCH
Found 1 match:
- Bob's "Learn Python" request (Score: 0.85)

# Alice proposes trade
alice> TRADE PROPOSE OFR_20251124_001 REQ_20251124_002

# Bob accepts
bob> TRADE ACCEPT TRD_20251124_003

# After tutoring sessions, both rate
alice> TRADE COMPLETE TRD_20251124_003 5
bob> TRADE COMPLETE TRD_20251124_003 5

✅ Trade completed! Reputation updated.
```

### Example 2: Resource Exchange

**Charlie needs**: Firewood (critical urgency)
**Diana has**: Extra firewood

```bash
# Charlie creates urgent request
charlie> REQUEST CREATE resource "Firewood" "Need for winter heating" --urgency critical

# Diana creates offer
diana> OFFER CREATE resource "Firewood" "Have extra cords available"

# Diana checks matches (Charlie's request shows high due to urgency)
diana> MATCH
Found 1 match:
- Charlie's "Firewood" request (Score: 1.8) 🔥 CRITICAL

# Diana proposes
diana> TRADE PROPOSE OFR_20251124_010 REQ_20251124_011

# Charlie accepts immediately
charlie> TRADE ACCEPT TRD_20251124_012

# After exchange
charlie> TRADE COMPLETE TRD_20251124_012 5 "Lifesaver, thank you!"
diana> TRADE COMPLETE TRD_20251124_012 5 "Glad to help!"
```

### Example 3: Tool Lending

**Eve needs**: Hammer temporarily
**Frank has**: Hammer available for loan

```bash
# Eve creates request
eve> REQUEST CREATE tool "Hammer" "Need for weekend project"

# Frank creates offer
frank> OFFER CREATE tool "Hammer for loan" "Available weekends"

# Frank sees match
frank> MATCH
Found 1 match:
- Eve's "Hammer" request (Score: 0.92)

# Frank proposes
frank> TRADE PROPOSE OFR_20251124_020 REQ_20251124_021

# Eve accepts
eve> TRADE ACCEPT TRD_20251124_022

# After weekend project
eve> TRADE COMPLETE TRD_20251124_022 4 "Tool worked great, thanks!"
frank> TRADE COMPLETE TRD_20251124_022 5 "Returned in perfect condition"
```

---

## Data Persistence

### Storage Location

All barter data is stored locally in JSON format:

```
memory/barter/
├── offers.json       # All offers
├── requests.json     # All requests
├── trades.json       # Trade history
└── reputation.json   # User reputation data
```

### Offline Operation

The barter system operates **100% offline**:
- No internet required
- All data stored locally
- Works on any planet/location
- Syncs via COMMUNITY commands (if enabled)

### Data Structure

**Offer**:
```json
{
  "id": "OFR_20251124_143022_123456",
  "user": "alice@localhost",
  "type": "skill",
  "title": "Python tutoring",
  "description": "Can teach basics to advanced",
  "tags": ["python", "tutoring", "basics", "advanced"],
  "location": "Melbourne",
  "created": "2025-11-24T14:30:22",
  "active": true
}
```

**Trade**:
```json
{
  "id": "TRD_20251124_144500_345678",
  "offer_id": "OFR_20251124_143022_123456",
  "request_id": "REQ_20251124_143530_789012",
  "offerer": "alice@localhost",
  "requester": "bob@localhost",
  "proposed_by": "alice@localhost",
  "status": "completed",
  "created": "2025-11-24T14:45:00",
  "completed": "2025-11-24T15:30:00",
  "rating_offerer": 5,
  "rating_requester": 5,
  "notes": "Great trade!"
}
```

---

## Troubleshooting

### Common Issues

**Q: "No matches found"**
A: Try:
- Adding more descriptive tags to your offers/requests
- Broadening your search (different types)
- Checking if location filtering is too strict
- Creating more diverse offers

**Q: "Cannot accept own trade"**
A: Only the non-proposer can accept a trade. If you proposed it, wait for the other party.

**Q: "Trade not completing"**
A: Both parties must rate the trade. Check:
```bash
TRADE LIST accepted
```
Then both users run:
```bash
TRADE COMPLETE <trade_id> <rating>
```

**Q: "Low match scores"**
A: Improve by:
- Using more specific keywords in titles/descriptions
- Setting your location with `LOCATE SET <city>`
- Adjusting urgency levels appropriately

**Q: "Can't delete offer"**
A: You can only delete your own offers. Check:
```bash
OFFER MY
```

---

## Integration

### With Community System

Barter integrates with Community features (v1.0.33):
- Community reputation affects barter trust
- Group members can prioritize trading with each other
- Community knowledge includes barter best practices

### With Location System

Barter uses MAP/LOCATE data (v1.0.32):
- `LOCATE SET <city>` enables location-aware matching
- Same-location traders get +0.2 score bonus
- Planet-specific barter economies (future)

### Future Enhancements

Planned improvements:
- [ ] Barter analytics dashboard
- [ ] Trade history visualization
- [ ] Multi-party trades (3+ participants)
- [ ] Recurring trade agreements
- [ ] Escrow/mediation system
- [ ] Trade templates
- [ ] Seasonal/event-based markets

---

## Developer Notes

### Architecture

**Service Layer** (`barter_service.py`):
- Business logic and data persistence
- Matching algorithm implementation
- Reputation calculations
- JSON file operations

**Command Layer** (`barter_commands.py`):
- CLI parsing and routing
- User input validation
- Output formatting
- Help documentation

**Integration** (`uDOS_commands.py`):
- Command routing: BARTER, OFFER, REQUEST, TRADE
- Handler initialization
- Error propagation

### Testing

Run test suite:
```bash
pytest memory/tests/test_v1_0_33_barter.py -v
```

Test coverage:
- 60 tests (100% pass rate)
- 8 test classes covering:
  - Command routing (5 tests)
  - Offer operations (8 tests)
  - Request operations (8 tests)
  - Trade execution (10 tests)
  - Matching engine (10 tests)
  - Reputation system (6 tests)
  - Error handling (5 tests)
  - Integration scenarios (8 tests)

### Extension Points

**Custom Matching**:
Modify `_calculate_match_score()` in `barter_service.py` to add:
- Skill level matching
- Time availability overlap
- Equipment compatibility checks

**New Offer Types**:
Add to `OfferType` enum:
```python
class OfferType(Enum):
    SKILL = "skill"
    # ... existing types ...
    DIGITAL = "digital"  # New type
```

**Trade Workflow**:
Extend `TradeStatus` enum for custom workflows:
```python
class TradeStatus(Enum):
    # ... existing statuses ...
    IN_PROGRESS = "in-progress"
    DISPUTED = "disputed"
```

---

## Related Documentation

- [Community Features](./Community-Features.md) - Group knowledge sharing
- [Location System](./Mapping-System.md) - MAP and LOCATE commands
- [Planet System](./Planet-System.md) - Multi-planet support
- [Command Reference](./Command-Reference.md) - Full command listing

---

## Support

**Implementation**: v1.0.33 (COMPLETE)
**Maintainer**: uDOS Development Team
**Last Updated**: 2025-11-24
**License**: See LICENSE.txt

For bugs or feature requests, see [CONTRIBUTING.md](../CONTRIBUTING.md)

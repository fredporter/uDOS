# GENERATE Command Consolidation - Architecture Design

**Date:** December 3, 2025  
**Version:** v1.2.0 (Architecture Redesign)  
**Status:** 🚧 PLANNING

---

## Executive Summary

Consolidate ASSISTANT and GENERATE commands into a unified **GENERATE** system with **offline-first AI** using knowledge bank, FAQs, and user memory. Gemini becomes an optional extension, Banana is explicitly called for images only. Add smart throttling, API monitoring, and workflow variable integration.

**Key Principles:**
1. **Offline First** - No API calls unless explicitly needed
2. **Knowledge Bank Primary** - Local content is the source of truth
3. **Gemini = Extension** - Optional, not core dependency
4. **Smart Resource Management** - Rate limiting, cost tracking, priority workflows
5. **Workflow Integration** - System/user prompts, variables, FAQ injection

---

## Current State Analysis

### Existing Commands (BEFORE)

**ASSISTANT Handler** (`core/commands/assistant_handler.py`)
- ASK - Question answering (offline-first for users, Gemini for wizards)
- READ - Panel content reading
- EXPLAIN - Command explanation
- GENERATE - Script generation (deprecated)
- DEBUG - Error debugging
- CLEAR - Conversation history
- DEV - Development mode (wizard only)

**GENERATE Handler** (`core/commands/generate_handler.py`)
- GENERATE SVG - Vector diagrams via Nano Banana
- GENERATE DIAGRAM - Alias for SVG
- GENERATE ASCII - ASCII art diagrams
- GENERATE TELETEXT - BBC teletext graphics

**Offline Engine** (`core/interpreters/offline.py`)
- FAQ search and pattern matching
- Intent analysis
- Local knowledge fallback

### Problems with Current Design

1. **Split Responsibility** - AI features scattered across assistant_handler, generate_handler, offline.py
2. **Gemini in Core** - Hard dependency on API key, not truly offline-first
3. **No Unified Interface** - Inconsistent command structure (ASK vs GENERATE)
4. **No Resource Management** - No rate limiting, cost tracking, or priority workflows
5. **Limited Offline Intelligence** - Offline engine is basic pattern matching
6. **No Workflow Integration** - Prompts and variables not accessible in workflows

---

## Proposed Architecture (AFTER)

### Command Structure

```
GENERATE <subcommand> [options] <input>

Subcommands:
  DO <query>              - Default generation (text, guides, answers)
  REDO <id>               - Retry previous generation
  GUIDE <topic>           - Generate knowledge bank guide
  SVG <description>       - Generate SVG diagram (requires Banana)
  DIAGRAM <description>   - Alias for SVG
  ASCII <description>     - Generate ASCII art
  TELETEXT <description>  - Generate teletext graphics
  HELP                    - Show command reference
  
Options:
  --offline               - Force offline mode (no API calls)
  --online                - Allow API calls (if available)
  --priority <level>      - critical | high | normal | low
  --style <name>          - Style preset (for diagrams)
  --save <file>           - Save output to file
  --stats                 - Show live generation stats
```

### 3-Tier Intelligence System

```
┌─────────────────────────────────────────────────────────────┐
│                    USER REQUEST                              │
│                "GENERATE DO water purification methods"      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  TIER 1: OFFLINE AI ENGINE (Primary)                         │
│  ─────────────────────────────────────────────────────────  │
│  • Search Knowledge Bank (166+ guides)                       │
│  • Query FAQ System (core/data/faq.json)                     │
│  • Access User Memory (memory/user/)                         │
│  • Template System (prompts, workflows)                      │
│  • Pattern Matching & Intent Analysis                        │
│  ─────────────────────────────────────────────────────────  │
│  ✅ 90% of queries answered here (instant, free, offline)   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ If insufficient local data...
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  TIER 2: GEMINI EXTENSION (Optional)                         │
│  ─────────────────────────────────────────────────────────  │
│  • Located in: extensions/assistant/                         │
│  • Requires: GEMINI_API_KEY in .env                          │
│  • Rate Limiting: 2 req/sec (configurable)                   │
│  • Cost Tracking: $1 per 1M tokens estimate                  │
│  • Priority Queue: critical > high > normal > low            │
│  ─────────────────────────────────────────────────────────  │
│  ⚠️  Used only when local knowledge insufficient            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ For image generation only...
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  TIER 3: BANANA EXTENSION (Explicit Only)                    │
│  ─────────────────────────────────────────────────────────  │
│  • Located in: extensions/assistant/banana.py                │
│  • Commands: GENERATE SVG, GENERATE DIAGRAM                  │
│  • Pipeline: Style Guide → Gemini 2.5 Flash → PNG → SVG     │
│  • Rate Limiting: 1 req/6sec (strict)                        │
│  • Cost: ~$0.01-0.05 per image                               │
│  ─────────────────────────────────────────────────────────  │
│  🎨 Explicit image generation only                           │
└─────────────────────────────────────────────────────────────┘
```

### File Structure

```
core/
├── commands/
│   ├── generate_handler.py (NEW - unified handler)
│   ├── assistant_handler.py (DEPRECATED → remove in v1.3)
│   └── ...
├── interpreters/
│   ├── offline.py (ENHANCED - primary AI engine)
│   └── ...
├── services/
│   ├── api_monitor.py (NEW - rate limiting, cost tracking)
│   ├── priority_queue.py (NEW - workflow prioritization)
│   └── ...
└── data/
    ├── faq.json (ENHANCED - expanded coverage)
    ├── prompts.json (NEW - system/user prompt templates)
    └── ...

extensions/
├── assistant/ (NEW - extracted from core)
│   ├── extension.json
│   ├── handler.py (Gemini integration)
│   ├── banana.py (Nano Banana pipeline)
│   ├── config.py
│   └── README.md
└── ...

memory/
├── user/
│   ├── prompts/ (NEW - user-defined prompts)
│   ├── context.json (NEW - conversation history)
│   └── preferences.json (NEW - generation preferences)
└── ...
```

---

## Component Details

### 1. Unified GENERATE Handler

**File:** `core/commands/generate_handler.py` (complete rewrite)

```python
class GenerateHandler:
    """Unified generation system with offline-first AI."""
    
    def __init__(self, components):
        self.offline_engine = OfflineEngine()  # Primary AI
        self.gemini_ext = None  # Lazy load if available
        self.banana_ext = None  # Lazy load if available
        self.api_monitor = APIMonitor()
        self.priority_queue = PriorityQueue()
        
    def handle_command(self, params):
        """Route GENERATE subcommands."""
        if not params:
            return self._show_help()
            
        subcommand = params[0].upper()
        
        if subcommand == "DO":
            return self._generate_default(params[1:])
        elif subcommand == "REDO":
            return self._generate_redo(params[1:])
        elif subcommand == "GUIDE":
            return self._generate_guide(params[1:])
        elif subcommand in ["SVG", "DIAGRAM"]:
            return self._generate_svg(params[1:])
        # ... etc
    
    def _generate_default(self, params):
        """Default generation using 3-tier system."""
        query = " ".join(params)
        
        # Tier 1: Try offline engine first
        offline_result = self.offline_engine.generate(query)
        if offline_result.confidence > 0.85:
            return offline_result.content
        
        # Tier 2: Fall back to Gemini if available
        if self._has_gemini_extension():
            # Check rate limits and cost budget
            if self.api_monitor.can_make_request():
                gemini_result = self.gemini_ext.generate(query)
                self.api_monitor.log_request()
                return gemini_result
        
        # Return best offline result with disclaimer
        return f"{offline_result.content}\n\n⚠️  Limited local data. Install Gemini extension for enhanced results."
```

### 2. Enhanced Offline Engine

**File:** `core/interpreters/offline.py` (major enhancement)

```python
class OfflineEngine:
    """Enhanced offline AI using knowledge bank, FAQ, and templates."""
    
    def __init__(self):
        self.knowledge_manager = get_knowledge_manager()
        self.faq_system = FAQSystem()
        self.user_memory = UserMemory()
        self.prompt_templates = load_json("core/data/prompts.json")
        
    def generate(self, query: str, context: dict = None):
        """Generate response using local resources only."""
        
        # Step 1: Analyze intent
        intent = self._analyze_intent(query)
        
        # Step 2: Search knowledge bank
        kb_results = self.knowledge_manager.search(query, limit=5)
        
        # Step 3: Search FAQ
        faq_results = self.faq_system.search(query)
        
        # Step 4: Check user memory
        user_context = self.user_memory.get_relevant_context(query)
        
        # Step 5: Apply templates
        template = self._select_template(intent)
        
        # Step 6: Synthesize response
        response = self._synthesize_response(
            query=query,
            intent=intent,
            kb_results=kb_results,
            faq_results=faq_results,
            user_context=user_context,
            template=template
        )
        
        return OfflineResponse(
            content=response,
            confidence=self._calculate_confidence(kb_results, faq_results),
            sources=self._extract_sources(kb_results, faq_results)
        )
    
    def _synthesize_response(self, **kwargs):
        """Intelligent response synthesis from local data."""
        # Combine knowledge bank excerpts
        # Format FAQ answers
        # Apply user context
        # Fill template with synthesized content
        # Return cohesive response
```

### 3. Gemini Extension

**File:** `extensions/assistant/handler.py` (extracted from core)

```python
class GeminiExtension:
    """Gemini API integration as optional extension."""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ExtensionNotAvailableError("GEMINI_API_KEY required")
        
        self.client = genai.Client(api_key=self.api_key)
        
    def generate(self, query: str, context: dict = None):
        """Generate using Gemini with rate limiting."""
        # Apply rate limiting
        # Inject system/user prompts
        # Make API call
        # Track usage
        # Return result
```

**File:** `extensions/assistant/extension.json`

```json
{
  "id": "gemini-assistant",
  "name": "Gemini AI Assistant",
  "version": "1.0.0",
  "description": "Optional Gemini API integration for enhanced generation",
  "type": "assistant",
  "requires": ["GEMINI_API_KEY"],
  "optional": true,
  "commands": [],
  "config": {
    "rate_limit": 2,
    "cost_budget": 1.00,
    "priority_levels": ["critical", "high", "normal", "low"]
  }
}
```

### 4. API Monitoring Service

**File:** `core/services/api_monitor.py` (NEW)

```python
class APIMonitor:
    """Monitor API usage, enforce rate limits, track costs."""
    
    def __init__(self):
        self.requests_log = []
        self.cost_tracker = CostTracker()
        self.rate_limiter = RateLimiter()
        
    def can_make_request(self, priority="normal"):
        """Check if request is allowed based on limits and budget."""
        # Check rate limit
        if not self.rate_limiter.is_allowed():
            return False
        
        # Check cost budget
        if not self.cost_tracker.within_budget():
            return False
        
        # Check priority queue
        if not self.priority_queue.should_process(priority):
            return False
        
        return True
    
    def log_request(self, tokens, cost, duration_ms):
        """Log API request for analytics."""
        self.requests_log.append({
            "timestamp": datetime.now().isoformat(),
            "tokens": tokens,
            "cost": cost,
            "duration_ms": duration_ms
        })
        self.cost_tracker.add_cost(cost)
    
    def get_stats(self):
        """Get live usage statistics."""
        return {
            "total_requests": len(self.requests_log),
            "total_tokens": sum(r["tokens"] for r in self.requests_log),
            "total_cost": self.cost_tracker.total_cost,
            "avg_duration_ms": statistics.mean(r["duration_ms"] for r in self.requests_log),
            "budget_remaining": self.cost_tracker.budget_remaining
        }
```

### 5. Workflow Variable Integration

**File:** `core/utils/variables.py` (ENHANCED)

Add new variable namespaces:

```python
# Prompt variables
$PROMPT.SYSTEM          # System prompt template
$PROMPT.USER            # User prompt template
$PROMPT.CONTEXT         # Injected context

# Generation variables
$GENERATE.MODE          # offline | online | hybrid
$GENERATE.PRIORITY      # critical | high | normal | low
$GENERATE.STYLE         # Style preset name
$GENERATE.LAST_RESULT   # Previous generation result
$GENERATE.LAST_COST     # Previous generation cost

# API variables
$API.REQUESTS_TODAY     # Request count today
$API.COST_TODAY         # Cost today
$API.BUDGET_REMAINING   # Remaining budget
$API.RATE_LIMIT         # Current rate limit
```

**Usage in Workflows:**

```ucode
# knowledge-expansion.upy

# Set system prompt for guide generation
SET PROMPT.SYSTEM = "You are a survival expert. Generate comprehensive, safety-first guides."
SET PROMPT.USER = "Create a detailed guide on: $TOPIC"

# Generate with priority
SET GENERATE.PRIORITY = "high"
GENERATE GUIDE $TOPIC --priority $GENERATE.PRIORITY

# Monitor API usage
IF $API.COST_TODAY > 5.00
  PRINT "⚠️  Daily API budget exceeded ($5.00)"
  SET GENERATE.MODE = "offline"
END
```

---

## Migration Plan

### Phase 1: Preparation (Day 1)
- [x] Create design document
- [ ] Audit current assistant_handler.py and generate_handler.py
- [ ] Identify all Gemini dependencies
- [ ] Create backup branch

### Phase 2: Core Restructure (Days 2-3)
- [ ] Enhance offline.py with knowledge bank synthesis
- [ ] Create new generate_handler.py (unified)
- [ ] Create api_monitor.py service
- [ ] Create priority_queue.py service
- [ ] Add prompt templates system

### Phase 3: Extension Creation (Days 4-5)
- [ ] Create extensions/assistant/ directory
- [ ] Move Gemini code to extension
- [ ] Create extension.json manifest
- [ ] Test extension loading/unloading
- [ ] Document extension API

### Phase 4: Workflow Integration (Day 6)
- [ ] Add $PROMPT.* variables
- [ ] Add $GENERATE.* variables
- [ ] Add $API.* variables
- [ ] Update knowledge-expansion.upy workflow
- [ ] Test variable injection

### Phase 5: Testing & Documentation (Days 7-8)
- [ ] Test offline-only mode (no API key)
- [ ] Test offline→online fallback
- [ ] Test rate limiting and cost tracking
- [ ] Test priority workflows
- [ ] Update wiki documentation
- [ ] Update command reference
- [ ] Create migration guide

### Phase 6: Deprecation (Day 9)
- [ ] Mark assistant_handler.py as deprecated
- [ ] Add migration notices
- [ ] Update all examples
- [ ] Plan removal for v1.3.0

---

## Backwards Compatibility

### Deprecated Commands (still work, redirect)
```
ASK <query>           → GENERATE DO <query>
ASSIST <query>        → GENERATE DO <query>
OK ASK <query>        → GENERATE DO <query>
GENERATE SVG <desc>   → GENERATE SVG <desc> (no change)
```

### Config Migration
```json
// OLD (.env)
GEMINI_API_KEY=xxx

// NEW (.env + config.json)
GEMINI_API_KEY=xxx  (still works)

// config.json
{
  "generation": {
    "default_mode": "offline",  // offline | online | hybrid
    "api_budget_daily": 5.00,
    "rate_limit_rps": 2,
    "priority_default": "normal"
  }
}
```

---

## Benefits

### For Users
1. **Faster Responses** - Most queries answered instantly from local knowledge
2. **Lower Costs** - Reduced API usage = lower bills
3. **Offline Capable** - Full functionality without internet
4. **Transparent Costs** - Live API usage tracking
5. **Better Quality** - Local knowledge is curated and accurate

### For Developers
1. **Cleaner Architecture** - Single unified GENERATE system
2. **Easier Extension** - Gemini as plugin, not core dependency
3. **Better Testing** - Offline mode fully testable
4. **Resource Control** - Fine-grained API limits and budgets
5. **Workflow Integration** - Prompts and context as variables

### For System
1. **Reduced Dependencies** - Gemini optional, not required
2. **Better Performance** - Local knowledge = no network latency
3. **Scalability** - Priority queue handles load
4. **Observability** - Detailed API usage analytics
5. **Maintainability** - Smaller core, modular extensions

---

## Success Criteria

- [ ] 90%+ queries answered offline (measured over 1 week)
- [ ] API costs reduced by 70%+ vs current system
- [ ] Response time <100ms for offline queries
- [ ] Zero errors when GEMINI_API_KEY not set
- [ ] All existing workflows still function
- [ ] Documentation complete for new system
- [ ] Migration guide available

---

## Open Questions

1. **FAQ Coverage** - How many FAQ entries needed for 90% offline coverage?
2. **Template Variety** - How many prompt templates required?
3. **Synthesis Quality** - Can offline synthesis match Gemini quality?
4. **Rate Limiting** - What are sensible defaults for different priority levels?
5. **Cost Budgets** - Should budgets be daily, weekly, or monthly?
6. **Extension Discovery** - How do users know Gemini extension is available?

---

## Next Steps

1. **Start Phase 2** - Enhance offline.py with synthesis capability
2. **Create Prompts System** - Design prompt template structure
3. **Build API Monitor** - Implement rate limiting and cost tracking
4. **Test Offline Synthesis** - Validate quality vs Gemini

---

**Document Status:** Living document, updated as design evolves  
**Last Updated:** December 3, 2025  
**Next Review:** After Phase 2 completion

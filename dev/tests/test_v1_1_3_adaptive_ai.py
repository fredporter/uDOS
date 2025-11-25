#!/usr/bin/env python3
"""
v1.1.3.4 - Adaptive Difficulty & AI Storytelling Test Suite

Tests the adaptive difficulty system and Gemini-powered AI storytelling features:
1. Difficulty Scaling - Dynamic adjustment based on player performance
2. Gemini API Integration - AI-powered content generation (with mocks)
3. Narrative Generation - Dynamic story events and mission descriptions
4. Session Analysis - Player behavior pattern extraction
5. Content Validation - Quality checks for generated content
6. Integration - End-to-end adaptive gameplay scenarios

Author: uDOS Development Team
Created: 2025-11-24
Version: 1.1.3.4
"""

import unittest
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple
import json
import re


# ============================================================================
# DIFFICULTY SCALING SYSTEM
# ============================================================================

class DifficultyLevel(Enum):
    """Difficulty levels for adaptive scaling"""
    TUTORIAL = 1
    EASY = 2
    NORMAL = 3
    HARD = 4
    EXPERT = 5
    NIGHTMARE = 6


class PlayerMetrics:
    """Track player performance metrics for difficulty assessment"""
    def __init__(self):
        self.missions_completed: int = 0
        self.missions_failed: int = 0
        self.average_completion_time: float = 0.0  # minutes
        self.deaths: int = 0
        self.resources_collected: int = 0
        self.skills_mastered: int = 0
        self.xp_total: int = 0
        self.playtime_hours: float = 0.0
        self.combat_wins: int = 0
        self.combat_losses: int = 0

    def success_rate(self) -> float:
        """Calculate mission success rate"""
        total = self.missions_completed + self.missions_failed
        return self.missions_completed / total if total > 0 else 0.0

    def combat_effectiveness(self) -> float:
        """Calculate combat win rate"""
        total = self.combat_wins + self.combat_losses
        return self.combat_wins / total if total > 0 else 0.5


class DifficultyScaler:
    """Adaptive difficulty scaling based on player performance"""

    def __init__(self):
        self.current_level = DifficultyLevel.NORMAL
        self.adjustment_cooldown = 3  # missions before next adjustment
        self.missions_since_adjustment = 0

    def assess_difficulty(self, metrics: PlayerMetrics) -> DifficultyLevel:
        """Assess appropriate difficulty level based on player metrics"""
        score = 0

        # Success rate scoring
        success_rate = metrics.success_rate()
        if success_rate > 0.9:
            score += 2
        elif success_rate > 0.7:
            score += 1
        elif success_rate < 0.3:
            score -= 2
        elif success_rate < 0.5:
            score -= 1

        # Combat effectiveness
        combat_rate = metrics.combat_effectiveness()
        if combat_rate > 0.8:
            score += 1
        elif combat_rate < 0.3:
            score -= 1

        # Death frequency
        if metrics.missions_completed > 0:
            death_ratio = metrics.deaths / metrics.missions_completed
            if death_ratio > 0.5:
                score -= 2
            elif death_ratio < 0.1:
                score += 1

        # Skills progression
        if metrics.skills_mastered > 10:
            score += 1

        # XP accumulation rate
        if metrics.playtime_hours > 0:
            xp_rate = metrics.xp_total / metrics.playtime_hours
            if xp_rate > 100:
                score += 1
            elif xp_rate < 20:
                score -= 1

        # Calculate new difficulty level
        current_value = self.current_level.value
        new_value = max(1, min(6, current_value + score))

        return DifficultyLevel(new_value)

    def adjust_difficulty(self, metrics: PlayerMetrics) -> bool:
        """Adjust difficulty if cooldown expired, returns True if adjusted"""
        if self.missions_since_adjustment < self.adjustment_cooldown:
            self.missions_since_adjustment += 1
            return False

        new_level = self.assess_difficulty(metrics)
        if new_level != self.current_level:
            self.current_level = new_level
            self.missions_since_adjustment = 0
            return True

        return False

    def scale_mission_parameters(self, base_params: Dict) -> Dict:
        """Scale mission parameters based on current difficulty"""
        multipliers = {
            DifficultyLevel.TUTORIAL: {"enemy_hp": 0.5, "time_limit": 2.0, "resources": 2.0},
            DifficultyLevel.EASY: {"enemy_hp": 0.75, "time_limit": 1.5, "resources": 1.5},
            DifficultyLevel.NORMAL: {"enemy_hp": 1.0, "time_limit": 1.0, "resources": 1.0},
            DifficultyLevel.HARD: {"enemy_hp": 1.5, "time_limit": 0.75, "resources": 0.75},
            DifficultyLevel.EXPERT: {"enemy_hp": 2.0, "time_limit": 0.5, "resources": 0.5},
            DifficultyLevel.NIGHTMARE: {"enemy_hp": 3.0, "time_limit": 0.4, "resources": 0.3},
        }

        mult = multipliers[self.current_level]
        scaled = base_params.copy()

        if "enemy_hp" in scaled:
            scaled["enemy_hp"] = int(base_params["enemy_hp"] * mult["enemy_hp"])
        if "time_limit" in scaled:
            scaled["time_limit"] = int(base_params["time_limit"] * mult["time_limit"])
        if "resources_available" in scaled:
            scaled["resources_available"] = int(base_params["resources_available"] * mult["resources"])

        return scaled


# ============================================================================
# GEMINI API INTEGRATION (MOCK)
# ============================================================================

class GeminiResponse:
    """Gemini API response wrapper"""
    def __init__(self, text: str, model: str = "gemini-pro"):
        self.text = text
        self.model = model
        self.timestamp = datetime.now()


class GeminiClient:
    """Mock Gemini API client for content generation"""

    def __init__(self, api_key: Optional[str] = None, mock_mode: bool = True):
        self.api_key = api_key
        self.mock_mode = mock_mode
        self.request_count = 0
        self.rate_limit = 60  # requests per minute
        self.last_request_time = datetime.now()

    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits"""
        now = datetime.now()
        # In mock mode, allow all requests (real mode would enforce limits)
        if not self.mock_mode:
            if (now - self.last_request_time).seconds < 1:
                return False
        self.last_request_time = now
        return True

    def generate_content(self, prompt: str, temperature: float = 0.7) -> GeminiResponse:
        """Generate content using Gemini API (mocked)"""
        if not self._check_rate_limit():
            raise Exception("Rate limit exceeded")

        self.request_count += 1

        if self.mock_mode:
            # Mock responses based on prompt keywords
            if "mission" in prompt.lower():
                return GeminiResponse(
                    "Scavenge the abandoned warehouse district for medical supplies. "
                    "Avoid or eliminate raider patrols. Time limit: 2 hours."
                )
            elif "narrative" in prompt.lower() or "story" in prompt.lower():
                return GeminiResponse(
                    "As you approach the ruins, a distant howl echoes through the streets. "
                    "The wind carries the scent of smoke and decay."
                )
            elif "dialogue" in prompt.lower():
                return GeminiResponse(
                    "Stranger: 'You look like you know how to handle yourself. "
                    "I might have work for someone with your skills.'"
                )
            else:
                return GeminiResponse("Generated content based on prompt.")
        else:
            # Real API call would go here
            raise NotImplementedError("Real Gemini API integration not implemented")


# ============================================================================
# NARRATIVE GENERATION
# ============================================================================

class NarrativeEvent:
    """Dynamic narrative event"""
    def __init__(self, text: str, category: str, triggers: List[str]):
        self.text = text
        self.category = category  # "environmental", "dialogue", "discovery", "combat"
        self.triggers = triggers
        self.timestamp = datetime.now()


class NarrativeGenerator:
    """AI-powered narrative generation system"""

    def __init__(self, gemini_client: GeminiClient):
        self.client = gemini_client
        self.event_history: List[NarrativeEvent] = []

    def generate_mission_description(
        self,
        mission_type: str,
        difficulty: DifficultyLevel,
        player_context: Dict
    ) -> str:
        """Generate dynamic mission description"""
        prompt = f"""Generate a post-apocalyptic survival mission description.
Mission Type: {mission_type}
Difficulty: {difficulty.name}
Player Skills: {player_context.get('skills', [])}
Player Location: {player_context.get('location', 'unknown')}

Create a concise, engaging mission brief (2-3 sentences) that fits the difficulty level."""

        response = self.client.generate_content(prompt)
        return response.text

    def generate_narrative_event(
        self,
        context: Dict,
        event_type: str = "environmental"
    ) -> NarrativeEvent:
        """Generate dynamic narrative event based on context"""
        prompt = f"""Generate a brief narrative event for a post-apocalyptic survival game.
Event Type: {event_type}
Context: {json.dumps(context)}

Create an atmospheric description (1-2 sentences) that enhances immersion."""

        response = self.client.generate_content(prompt, temperature=0.8)

        event = NarrativeEvent(
            text=response.text,
            category=event_type,
            triggers=context.get("triggers", [])
        )
        self.event_history.append(event)

        return event

    def generate_dialogue(
        self,
        npc_type: str,
        player_reputation: int,
        context: str
    ) -> str:
        """Generate NPC dialogue"""
        prompt = f"""Generate NPC dialogue for a post-apocalyptic survival game.
NPC Type: {npc_type}
Player Reputation: {player_reputation}/100
Context: {context}

Create realistic dialogue (1-2 lines) that reflects the harsh world and NPC's personality."""

        response = self.client.generate_content(prompt, temperature=0.9)
        return response.text


# ============================================================================
# SESSION ANALYSIS
# ============================================================================

@dataclass
class SessionPattern:
    """Detected player behavior pattern"""
    pattern_type: str  # "combat_focused", "stealth_preferred", "resource_hoarder", etc.
    confidence: float  # 0.0 to 1.0
    evidence: List[str]


class SessionAnalyzer:
    """Analyze player session logs to extract behavior patterns"""

    def __init__(self):
        self.sessions: List[Dict] = []

    def add_session(self, session_data: Dict):
        """Add session data for analysis"""
        self.sessions.append({
            **session_data,
            "timestamp": datetime.now()
        })

    def extract_patterns(self) -> List[SessionPattern]:
        """Extract behavior patterns from session history"""
        patterns = []

        if not self.sessions:
            return patterns

        # Analyze combat preference
        total_combats = sum(s.get("combats", 0) for s in self.sessions)
        total_stealth = sum(s.get("stealth_actions", 0) for s in self.sessions)

        if total_combats + total_stealth > 0:
            combat_ratio = total_combats / (total_combats + total_stealth)
            if combat_ratio > 0.7:
                patterns.append(SessionPattern(
                    pattern_type="combat_focused",
                    confidence=combat_ratio,
                    evidence=[f"Combat actions: {total_combats}, Stealth: {total_stealth}"]
                ))
            elif combat_ratio < 0.3:
                patterns.append(SessionPattern(
                    pattern_type="stealth_preferred",
                    confidence=1.0 - combat_ratio,
                    evidence=[f"Stealth actions: {total_stealth}, Combat: {total_combats}"]
                ))

        # Analyze resource management
        total_resources = sum(s.get("resources_collected", 0) for s in self.sessions)
        total_used = sum(s.get("resources_used", 0) for s in self.sessions)

        if total_resources > 0:
            usage_ratio = total_used / total_resources
            if usage_ratio < 0.3:
                patterns.append(SessionPattern(
                    pattern_type="resource_hoarder",
                    confidence=1.0 - usage_ratio,
                    evidence=[f"Collected: {total_resources}, Used: {total_used}"]
                ))
            elif usage_ratio > 0.8:
                patterns.append(SessionPattern(
                    pattern_type="resource_spender",
                    confidence=usage_ratio,
                    evidence=[f"High usage ratio: {usage_ratio:.2f}"]
                ))

        # Analyze skill preferences
        skill_usage = {}
        for session in self.sessions:
            for skill, count in session.get("skills_used", {}).items():
                skill_usage[skill] = skill_usage.get(skill, 0) + count

        if skill_usage:
            dominant_skill = max(skill_usage.items(), key=lambda x: x[1])
            total_skill_uses = sum(skill_usage.values())
            dominance = dominant_skill[1] / total_skill_uses

            if dominance > 0.5:
                patterns.append(SessionPattern(
                    pattern_type=f"specialist_{dominant_skill[0]}",
                    confidence=dominance,
                    evidence=[f"{dominant_skill[0]} used {dominant_skill[1]} times"]
                ))

        return patterns

    def generate_insights(self) -> Dict[str, any]:
        """Generate insights for AI content personalization"""
        patterns = self.extract_patterns()

        return {
            "patterns": [
                {"type": p.pattern_type, "confidence": p.confidence}
                for p in patterns
            ],
            "total_sessions": len(self.sessions),
            "preferred_playstyle": patterns[0].pattern_type if patterns else "balanced",
            "session_count": len(self.sessions)
        }


# ============================================================================
# CONTENT LOGGING
# ============================================================================

@dataclass
class GeneratedContent:
    """Logged AI-generated content"""
    content_type: str  # "mission", "narrative", "dialogue"
    prompt: str
    response: str
    difficulty: Optional[DifficultyLevel] = None
    player_context: Dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    quality_score: Optional[float] = None


class GeneratedContentLogger:
    """Log and track AI-generated content for quality review"""

    def __init__(self, log_directory: str = "memory/logs/generated_content"):
        self.log_directory = log_directory
        self.entries: List[GeneratedContent] = []

    def log_content(
        self,
        content_type: str,
        prompt: str,
        response: str,
        **kwargs
    ) -> GeneratedContent:
        """Log generated content"""
        entry = GeneratedContent(
            content_type=content_type,
            prompt=prompt,
            response=response,
            **kwargs
        )
        self.entries.append(entry)
        return entry

    def rate_content(self, entry: GeneratedContent, score: float):
        """Add quality rating to content (0.0 to 1.0)"""
        entry.quality_score = max(0.0, min(1.0, score))

    def get_statistics(self) -> Dict:
        """Get logging statistics"""
        if not self.entries:
            return {
                "total_entries": 0,
                "average_quality": 0.0,
                "by_type": {}
            }

        by_type = {}
        rated_entries = [e for e in self.entries if e.quality_score is not None]

        for entry in self.entries:
            by_type[entry.content_type] = by_type.get(entry.content_type, 0) + 1

        avg_quality = (
            sum(e.quality_score for e in rated_entries) / len(rated_entries)
            if rated_entries else 0.0
        )

        return {
            "total_entries": len(self.entries),
            "average_quality": avg_quality,
            "rated_count": len(rated_entries),
            "by_type": by_type
        }

    def export_to_json(self) -> str:
        """Export logs to JSON format"""
        data = []
        for entry in self.entries:
            data.append({
                "type": entry.content_type,
                "prompt": entry.prompt,
                "response": entry.response,
                "difficulty": entry.difficulty.name if entry.difficulty else None,
                "quality_score": entry.quality_score,
                "timestamp": entry.timestamp.isoformat()
            })
        return json.dumps(data, indent=2)


# ============================================================================
# TEST SUITE
# ============================================================================

class TestDifficultyScaling(unittest.TestCase):
    """Test adaptive difficulty scaling system"""

    def test_initial_difficulty(self):
        """Test starting difficulty level"""
        scaler = DifficultyScaler()
        self.assertEqual(scaler.current_level, DifficultyLevel.NORMAL)

    def test_assess_high_performer(self):
        """Test difficulty assessment for high-performing player"""
        scaler = DifficultyScaler()
        metrics = PlayerMetrics()
        metrics.missions_completed = 20
        metrics.missions_failed = 1
        metrics.combat_wins = 15
        metrics.combat_losses = 2
        metrics.deaths = 1
        metrics.skills_mastered = 12
        metrics.xp_total = 500
        metrics.playtime_hours = 4.0

        difficulty = scaler.assess_difficulty(metrics)
        self.assertGreater(difficulty.value, DifficultyLevel.NORMAL.value)

    def test_assess_struggling_player(self):
        """Test difficulty assessment for struggling player"""
        scaler = DifficultyScaler()
        metrics = PlayerMetrics()
        metrics.missions_completed = 5
        metrics.missions_failed = 10
        metrics.combat_wins = 2
        metrics.combat_losses = 8
        metrics.deaths = 12
        metrics.xp_total = 50
        metrics.playtime_hours = 5.0

        difficulty = scaler.assess_difficulty(metrics)
        self.assertLess(difficulty.value, DifficultyLevel.NORMAL.value)

    def test_adjustment_cooldown(self):
        """Test difficulty adjustment cooldown mechanism"""
        scaler = DifficultyScaler()
        scaler.adjustment_cooldown = 3
        metrics = PlayerMetrics()
        metrics.missions_completed = 20
        metrics.missions_failed = 1
        metrics.combat_wins = 15
        metrics.combat_losses = 2
        metrics.xp_total = 500
        metrics.playtime_hours = 4.0

        # First few missions shouldn't adjust (cooldown not reached)
        self.assertFalse(scaler.adjust_difficulty(metrics))
        self.assertFalse(scaler.adjust_difficulty(metrics))
        self.assertFalse(scaler.adjust_difficulty(metrics))

        # After cooldown, should adjust (metrics show higher difficulty needed)
        adjusted = scaler.adjust_difficulty(metrics)
        self.assertTrue(adjusted)

    def test_scale_mission_parameters_easy(self):
        """Test mission parameter scaling for easy difficulty"""
        scaler = DifficultyScaler()
        scaler.current_level = DifficultyLevel.EASY

        base = {
            "enemy_hp": 100,
            "time_limit": 60,
            "resources_available": 10
        }

        scaled = scaler.scale_mission_parameters(base)

        self.assertEqual(scaled["enemy_hp"], 75)
        self.assertEqual(scaled["time_limit"], 90)
        self.assertEqual(scaled["resources_available"], 15)

    def test_scale_mission_parameters_nightmare(self):
        """Test mission parameter scaling for nightmare difficulty"""
        scaler = DifficultyScaler()
        scaler.current_level = DifficultyLevel.NIGHTMARE

        base = {
            "enemy_hp": 100,
            "time_limit": 60,
            "resources_available": 10
        }

        scaled = scaler.scale_mission_parameters(base)

        self.assertEqual(scaled["enemy_hp"], 300)
        self.assertEqual(scaled["time_limit"], 24)
        self.assertEqual(scaled["resources_available"], 3)

    def test_difficulty_never_exceeds_bounds(self):
        """Test difficulty stays within valid range"""
        scaler = DifficultyScaler()
        scaler.current_level = DifficultyLevel.NIGHTMARE

        # Even with impossible stats, shouldn't go above max
        metrics = PlayerMetrics()
        metrics.missions_completed = 1000
        metrics.combat_wins = 1000
        metrics.skills_mastered = 100

        difficulty = scaler.assess_difficulty(metrics)
        self.assertLessEqual(difficulty.value, DifficultyLevel.NIGHTMARE.value)

    def test_success_rate_calculation(self):
        """Test player success rate calculation"""
        metrics = PlayerMetrics()
        metrics.missions_completed = 7
        metrics.missions_failed = 3

        self.assertEqual(metrics.success_rate(), 0.7)

    def test_combat_effectiveness(self):
        """Test combat effectiveness calculation"""
        metrics = PlayerMetrics()
        metrics.combat_wins = 8
        metrics.combat_losses = 2

        self.assertEqual(metrics.combat_effectiveness(), 0.8)


class TestGeminiIntegration(unittest.TestCase):
    """Test Gemini API integration (mocked)"""

    def test_client_initialization(self):
        """Test Gemini client initialization"""
        client = GeminiClient(api_key="test_key", mock_mode=True)
        self.assertTrue(client.mock_mode)
        self.assertEqual(client.request_count, 0)

    def test_generate_mission_content(self):
        """Test mission content generation"""
        client = GeminiClient(mock_mode=True)
        response = client.generate_content("Generate a mission description")

        self.assertIsInstance(response, GeminiResponse)
        self.assertIn("scavenge", response.text.lower())

    def test_generate_narrative_content(self):
        """Test narrative content generation"""
        client = GeminiClient(mock_mode=True)
        response = client.generate_content("Generate a narrative event")

        self.assertIsInstance(response, GeminiResponse)
        self.assertTrue(len(response.text) > 0)

    def test_rate_limiting(self):
        """Test API rate limiting"""
        client = GeminiClient(mock_mode=True)

        # First request should succeed
        response1 = client.generate_content("test")
        self.assertIsNotNone(response1)

        # Second immediate request might fail (rate limit)
        # In mock mode, we check the limit is tracked
        self.assertGreater(client.request_count, 0)

    def test_request_counting(self):
        """Test request counting"""
        client = GeminiClient(mock_mode=True)

        client.generate_content("test 1")
        client.generate_content("test 2")
        client.generate_content("test 3")

        self.assertEqual(client.request_count, 3)

    def test_response_timestamp(self):
        """Test response includes timestamp"""
        client = GeminiClient(mock_mode=True)
        response = client.generate_content("test")

        self.assertIsInstance(response.timestamp, datetime)


class TestNarrativeGeneration(unittest.TestCase):
    """Test AI narrative generation system"""

    def test_generate_mission_description(self):
        """Test mission description generation"""
        client = GeminiClient(mock_mode=True)
        generator = NarrativeGenerator(client)

        description = generator.generate_mission_description(
            mission_type="scavenge",
            difficulty=DifficultyLevel.NORMAL,
            player_context={"skills": ["lockpicking"], "location": "city"}
        )

        self.assertTrue(len(description) > 0)

    def test_generate_narrative_event(self):
        """Test narrative event generation"""
        client = GeminiClient(mock_mode=True)
        generator = NarrativeGenerator(client)

        event = generator.generate_narrative_event(
            context={"location": "ruins", "weather": "stormy"},
            event_type="environmental"
        )

        self.assertIsInstance(event, NarrativeEvent)
        self.assertEqual(event.category, "environmental")

    def test_generate_dialogue(self):
        """Test NPC dialogue generation"""
        client = GeminiClient(mock_mode=True)
        generator = NarrativeGenerator(client)

        dialogue = generator.generate_dialogue(
            npc_type="trader",
            player_reputation=50,
            context="first meeting"
        )

        self.assertTrue(len(dialogue) > 0)

    def test_event_history_tracking(self):
        """Test narrative event history is tracked"""
        client = GeminiClient(mock_mode=True)
        generator = NarrativeGenerator(client)

        generator.generate_narrative_event({"location": "ruins"})
        generator.generate_narrative_event({"location": "bunker"})

        self.assertEqual(len(generator.event_history), 2)

    def test_narrative_event_structure(self):
        """Test narrative event has required fields"""
        event = NarrativeEvent(
            text="Test event",
            category="discovery",
            triggers=["entered_zone", "high_perception"]
        )

        self.assertEqual(event.text, "Test event")
        self.assertEqual(event.category, "discovery")
        self.assertEqual(len(event.triggers), 2)
        self.assertIsInstance(event.timestamp, datetime)


class TestSessionAnalysis(unittest.TestCase):
    """Test session history analysis"""

    def test_add_session(self):
        """Test adding session data"""
        analyzer = SessionAnalyzer()
        analyzer.add_session({
            "combats": 5,
            "stealth_actions": 2,
            "resources_collected": 100
        })

        self.assertEqual(len(analyzer.sessions), 1)

    def test_detect_combat_focus(self):
        """Test detection of combat-focused playstyle"""
        analyzer = SessionAnalyzer()
        analyzer.add_session({
            "combats": 15,
            "stealth_actions": 2,
            "resources_collected": 50,
            "resources_used": 40
        })

        patterns = analyzer.extract_patterns()
        combat_patterns = [p for p in patterns if "combat" in p.pattern_type]

        self.assertTrue(len(combat_patterns) > 0)
        self.assertGreater(combat_patterns[0].confidence, 0.7)

    def test_detect_stealth_preference(self):
        """Test detection of stealth-preferred playstyle"""
        analyzer = SessionAnalyzer()
        analyzer.add_session({
            "combats": 2,
            "stealth_actions": 18,
            "resources_collected": 50,
            "resources_used": 25
        })

        patterns = analyzer.extract_patterns()
        stealth_patterns = [p for p in patterns if "stealth" in p.pattern_type]

        self.assertTrue(len(stealth_patterns) > 0)

    def test_detect_resource_hoarding(self):
        """Test detection of resource hoarding behavior"""
        analyzer = SessionAnalyzer()
        analyzer.add_session({
            "combats": 5,
            "stealth_actions": 5,
            "resources_collected": 100,
            "resources_used": 20
        })

        patterns = analyzer.extract_patterns()
        hoarder_patterns = [p for p in patterns if "hoarder" in p.pattern_type]

        self.assertTrue(len(hoarder_patterns) > 0)

    def test_detect_skill_specialization(self):
        """Test detection of skill specialization"""
        analyzer = SessionAnalyzer()
        analyzer.add_session({
            "combats": 5,
            "stealth_actions": 5,
            "resources_collected": 50,
            "resources_used": 25,
            "skills_used": {
                "lockpicking": 25,
                "combat": 5,
                "crafting": 3
            }
        })

        patterns = analyzer.extract_patterns()
        specialist_patterns = [p for p in patterns if "specialist" in p.pattern_type]

        self.assertTrue(len(specialist_patterns) > 0)
        self.assertIn("lockpicking", specialist_patterns[0].pattern_type)

    def test_generate_insights(self):
        """Test insight generation for AI personalization"""
        analyzer = SessionAnalyzer()
        analyzer.add_session({
            "combats": 10,
            "stealth_actions": 2,
            "resources_collected": 50,
            "resources_used": 40
        })

        insights = analyzer.generate_insights()

        self.assertIn("patterns", insights)
        self.assertIn("total_sessions", insights)
        self.assertIn("preferred_playstyle", insights)

    def test_empty_session_handling(self):
        """Test handling of empty session history"""
        analyzer = SessionAnalyzer()
        patterns = analyzer.extract_patterns()

        self.assertEqual(len(patterns), 0)

    def test_multi_session_analysis(self):
        """Test analysis across multiple sessions"""
        analyzer = SessionAnalyzer()

        for _ in range(5):
            analyzer.add_session({
                "combats": 8,
                "stealth_actions": 2,
                "resources_collected": 40,
                "resources_used": 35
            })

        patterns = analyzer.extract_patterns()
        self.assertTrue(len(patterns) > 0)


class TestContentLogging(unittest.TestCase):
    """Test generated content logging system"""

    def test_log_content(self):
        """Test logging generated content"""
        logger = GeneratedContentLogger()

        entry = logger.log_content(
            content_type="mission",
            prompt="Generate a scavenge mission",
            response="Find supplies in the ruins"
        )

        self.assertIsInstance(entry, GeneratedContent)
        self.assertEqual(len(logger.entries), 1)

    def test_rate_content(self):
        """Test rating logged content"""
        logger = GeneratedContentLogger()

        entry = logger.log_content(
            content_type="narrative",
            prompt="Generate event",
            response="Event text"
        )

        logger.rate_content(entry, 0.85)
        self.assertEqual(entry.quality_score, 0.85)

    def test_quality_score_bounds(self):
        """Test quality scores are bounded 0-1"""
        logger = GeneratedContentLogger()

        entry = logger.log_content(
            content_type="test",
            prompt="test",
            response="test"
        )

        logger.rate_content(entry, 1.5)  # Should clamp to 1.0
        self.assertEqual(entry.quality_score, 1.0)

        logger.rate_content(entry, -0.5)  # Should clamp to 0.0
        self.assertEqual(entry.quality_score, 0.0)

    def test_get_statistics(self):
        """Test statistics generation"""
        logger = GeneratedContentLogger()

        logger.log_content("mission", "p1", "r1")
        logger.log_content("narrative", "p2", "r2")
        logger.log_content("mission", "p3", "r3")

        stats = logger.get_statistics()

        self.assertEqual(stats["total_entries"], 3)
        self.assertEqual(stats["by_type"]["mission"], 2)
        self.assertEqual(stats["by_type"]["narrative"], 1)

    def test_average_quality_calculation(self):
        """Test average quality score calculation"""
        logger = GeneratedContentLogger()

        entry1 = logger.log_content("test", "p1", "r1")
        entry2 = logger.log_content("test", "p2", "r2")
        entry3 = logger.log_content("test", "p3", "r3")

        logger.rate_content(entry1, 0.8)
        logger.rate_content(entry2, 0.6)
        logger.rate_content(entry3, 1.0)

        stats = logger.get_statistics()
        self.assertAlmostEqual(stats["average_quality"], 0.8, places=2)

    def test_export_to_json(self):
        """Test JSON export functionality"""
        logger = GeneratedContentLogger()

        logger.log_content(
            content_type="mission",
            prompt="test prompt",
            response="test response",
            difficulty=DifficultyLevel.HARD
        )

        json_str = logger.export_to_json()
        data = json.loads(json_str)

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["type"], "mission")
        self.assertEqual(data[0]["difficulty"], "HARD")

    def test_content_with_context(self):
        """Test logging content with player context"""
        logger = GeneratedContentLogger()

        entry = logger.log_content(
            content_type="mission",
            prompt="generate mission",
            response="mission text",
            difficulty=DifficultyLevel.EXPERT,
            player_context={"level": 15, "location": "wasteland"}
        )

        self.assertEqual(entry.difficulty, DifficultyLevel.EXPERT)
        self.assertEqual(entry.player_context["level"], 15)


class TestIntegration(unittest.TestCase):
    """Test end-to-end adaptive gameplay scenarios"""

    def test_adaptive_mission_generation(self):
        """Test complete adaptive mission generation pipeline"""
        # Setup systems
        scaler = DifficultyScaler()
        client = GeminiClient(mock_mode=True)
        generator = NarrativeGenerator(client)
        logger = GeneratedContentLogger()

        # Simulate player metrics
        metrics = PlayerMetrics()
        metrics.missions_completed = 10
        metrics.missions_failed = 2
        metrics.combat_wins = 8
        metrics.combat_losses = 2

        # Adjust difficulty
        scaler.adjust_difficulty(metrics)

        # Generate mission with scaled difficulty
        base_params = {
            "enemy_hp": 100,
            "time_limit": 60,
            "resources_available": 10
        }
        scaled_params = scaler.scale_mission_parameters(base_params)

        # Generate mission description
        description = generator.generate_mission_description(
            mission_type="combat",
            difficulty=scaler.current_level,
            player_context={"skills": ["combat"]}
        )

        # Log generated content
        entry = logger.log_content(
            content_type="mission",
            prompt="adaptive mission",
            response=description,
            difficulty=scaler.current_level
        )

        # Validate complete pipeline
        self.assertIsNotNone(scaled_params)
        self.assertIsNotNone(description)
        self.assertEqual(entry.difficulty, scaler.current_level)

    def test_personalized_narrative_flow(self):
        """Test personalized narrative generation based on session analysis"""
        # Setup systems
        analyzer = SessionAnalyzer()
        client = GeminiClient(mock_mode=True)
        generator = NarrativeGenerator(client)

        # Add session showing combat preference
        analyzer.add_session({
            "combats": 15,
            "stealth_actions": 3,
            "resources_collected": 50,
            "resources_used": 45,
            "skills_used": {"combat": 20, "survival": 5}
        })

        # Extract patterns
        insights = analyzer.generate_insights()

        # Generate personalized narrative
        event = generator.generate_narrative_event(
            context={
                "playstyle": insights["preferred_playstyle"],
                "location": "combat_zone"
            },
            event_type="combat"
        )

        # Validate personalization
        self.assertIn("combat", insights["preferred_playstyle"])
        self.assertIsNotNone(event)

    def test_difficulty_progression_over_time(self):
        """Test difficulty scaling over multiple missions"""
        scaler = DifficultyScaler()
        scaler.adjustment_cooldown = 2
        metrics = PlayerMetrics()

        # Simulate successful mission progression
        difficulty_history = []

        for i in range(10):
            metrics.missions_completed += 1
            metrics.combat_wins += 1
            metrics.xp_total += 50
            metrics.playtime_hours += 0.5

            scaler.adjust_difficulty(metrics)
            difficulty_history.append(scaler.current_level.value)

        # Difficulty should increase over time for successful player
        self.assertGreater(difficulty_history[-1], difficulty_history[0])

    def test_quality_tracking_pipeline(self):
        """Test content quality tracking across generation pipeline"""
        client = GeminiClient(mock_mode=True)
        generator = NarrativeGenerator(client)
        logger = GeneratedContentLogger()

        # Generate multiple pieces of content
        for i in range(5):
            description = generator.generate_mission_description(
                mission_type="scavenge",
                difficulty=DifficultyLevel.NORMAL,
                player_context={"skills": []}
            )

            entry = logger.log_content(
                content_type="mission",
                prompt=f"mission {i}",
                response=description
            )

            # Simulate quality rating (in real system, from player feedback)
            logger.rate_content(entry, 0.7 + (i * 0.05))

        stats = logger.get_statistics()

        self.assertEqual(stats["total_entries"], 5)
        self.assertGreater(stats["average_quality"], 0.7)

    def test_full_adaptive_gameplay_loop(self):
        """Test complete adaptive gameplay loop with all systems"""
        # Initialize all systems
        scaler = DifficultyScaler()
        analyzer = SessionAnalyzer()
        client = GeminiClient(mock_mode=True)
        generator = NarrativeGenerator(client)
        logger = GeneratedContentLogger()

        # Player session 1 - learning phase
        session1_metrics = PlayerMetrics()
        session1_metrics.missions_completed = 3
        session1_metrics.missions_failed = 2
        session1_metrics.combat_wins = 2
        session1_metrics.combat_losses = 3

        analyzer.add_session({
            "combats": 5,
            "stealth_actions": 1,
            "resources_collected": 30,
            "resources_used": 28
        })

        scaler.adjust_difficulty(session1_metrics)
        initial_difficulty = scaler.current_level

        # Player session 2 - improved performance
        session2_metrics = PlayerMetrics()
        session2_metrics.missions_completed = 10
        session2_metrics.missions_failed = 2
        session2_metrics.combat_wins = 9
        session2_metrics.combat_losses = 3
        session2_metrics.skills_mastered = 5
        session2_metrics.xp_total = 300
        session2_metrics.playtime_hours = 3.0

        analyzer.add_session({
            "combats": 12,
            "stealth_actions": 2,
            "resources_collected": 60,
            "resources_used": 55,
            "skills_used": {"combat": 15, "survival": 8}
        })

        scaler.adjust_difficulty(session2_metrics)
        improved_difficulty = scaler.current_level

        # Generate adaptive content
        insights = analyzer.generate_insights()

        mission_desc = generator.generate_mission_description(
            mission_type="combat",
            difficulty=scaler.current_level,
            player_context={"playstyle": insights["preferred_playstyle"]}
        )

        logger.log_content(
            content_type="mission",
            prompt="adaptive mission",
            response=mission_desc,
            difficulty=scaler.current_level,
            player_context=insights
        )

        # Validate complete loop
        self.assertEqual(len(analyzer.sessions), 2)
        self.assertGreaterEqual(improved_difficulty.value, initial_difficulty.value)
        self.assertIsNotNone(mission_desc)
        self.assertEqual(len(logger.entries), 1)


if __name__ == "__main__":
    unittest.main()

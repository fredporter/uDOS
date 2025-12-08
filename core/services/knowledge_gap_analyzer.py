"""
Knowledge Gap Analyzer
Identifies missing guides in the knowledge matrix and prioritizes creation.

Part of v1.2.11 - Knowledge Quality & Automation
"""

import json
from pathlib import Path
from typing import Dict, List, Set
from dataclasses import dataclass, asdict


@dataclass
class KnowledgeGap:
    """Represents a missing guide in the knowledge bank."""
    category: str
    topic: str
    tier: int
    priority: str  # critical, high, medium, low
    reason: str
    expected_path: str
    related_topics: List[str]


class GapAnalyzer:
    """Analyzer for detecting gaps in knowledge coverage."""

    def __init__(self, knowledge_path: str = "knowledge"):
        self.knowledge_path = Path(knowledge_path)
        from core.utils.paths import PATHS
        self.gaps_report_path = PATHS.KNOWLEDGE_GAPS_REPORT

        # Define expected knowledge matrix
        self.expected_coverage = {
            'water': {
                'core': [
                    'purification-methods', 'boiling-water', 'chemical-treatment',
                    'filtration-systems', 'collection-techniques', 'storage-methods',
                    'water-sources', 'testing-water', 'conservation', 'emergency-collection'
                ],
                'advanced': [
                    'solar-still-construction', 'desalination', 'rainwater-harvesting',
                    'groundwater-location', 'water-recycling', 'long-term-storage'
                ]
            },
            'fire': {
                'core': [
                    'fire-starting-methods', 'tinder-materials', 'kindling-prep',
                    'maintaining-fire', 'fire-safety', 'fire-types', 'fire-locations',
                    'wet-weather-fires', 'signaling-fires', 'cooking-fires'
                ],
                'advanced': [
                    'friction-fire-methods', 'primitive-fire', 'fire-tools',
                    'smokeless-fires', 'underground-fires', 'fire-management'
                ]
            },
            'shelter': {
                'core': [
                    'shelter-location', 'natural-shelters', 'debris-shelters',
                    'lean-to-construction', 'insulation-materials', 'waterproofing',
                    'ventilation', 'heat-retention', 'emergency-shelters', 'wind-protection'
                ],
                'advanced': [
                    'long-term-shelters', 'underground-shelters', 'snow-shelters',
                    'tropical-shelters', 'desert-shelters', 'multi-person-shelters'
                ]
            },
            'food': {
                'core': [
                    'edible-plants', 'plant-identification', 'foraging-safety',
                    'hunting-basics', 'trapping-methods', 'fishing-techniques',
                    'food-preservation', 'cooking-methods', 'food-storage', 'nutrition'
                ],
                'advanced': [
                    'advanced-trapping', 'fishing-gear', 'smoking-meat',
                    'fermentation', 'drying-foods', 'underground-storage'
                ]
            },
            'navigation': {
                'core': [
                    'map-reading', 'compass-use', 'direction-finding',
                    'star-navigation', 'natural-landmarks', 'terrain-reading',
                    'gps-basics', 'route-planning', 'distance-estimation', 'backtracking'
                ],
                'advanced': [
                    'dead-reckoning', 'celestial-navigation', 'terrain-association',
                    'pace-counting', 'altimeter-use', 'magnetic-declination'
                ]
            },
            'medical': {
                'core': [
                    'first-aid-basics', 'wound-treatment', 'bleeding-control',
                    'fracture-care', 'burn-treatment', 'hypothermia', 'heat-illness',
                    'dehydration', 'hygiene', 'disease-prevention'
                ],
                'advanced': [
                    'advanced-wound-care', 'improvised-splints', 'medication-basics',
                    'dental-emergencies', 'emergency-procedures', 'mental-health'
                ]
            }
        }

        # Priority weights
        self.priority_weights = {
            'core': 100,
            'safety': 90,
            'commonly_needed': 80,
            'advanced': 60,
            'specialized': 40
        }

    def analyze_gaps(self) -> List[KnowledgeGap]:
        """
        Analyze knowledge bank and identify missing guides.

        Returns:
            List of KnowledgeGap objects prioritized by importance
        """
        print("🔍 Analyzing knowledge gaps...")

        gaps = []

        for category, topics in self.expected_coverage.items():
            existing_guides = self._get_existing_guides(category)

            # Check core topics
            for topic in topics.get('core', []):
                if not self._topic_exists(topic, existing_guides):
                    gap = KnowledgeGap(
                        category=category,
                        topic=topic,
                        tier=2,  # Core topics are tier 2
                        priority=self._calculate_priority(category, topic, 'core'),
                        reason=f"Core {category} knowledge - essential survival skill",
                        expected_path=f"knowledge/{category}/{topic}.md",
                        related_topics=self._find_related_topics(category, topic)
                    )
                    gaps.append(gap)

            # Check advanced topics
            for topic in topics.get('advanced', []):
                if not self._topic_exists(topic, existing_guides):
                    gap = KnowledgeGap(
                        category=category,
                        topic=topic,
                        tier=3,  # Advanced topics are tier 3
                        priority=self._calculate_priority(category, topic, 'advanced'),
                        reason=f"Advanced {category} technique",
                        expected_path=f"knowledge/{category}/{topic}.md",
                        related_topics=self._find_related_topics(category, topic)
                    )
                    gaps.append(gap)

        # Sort by priority
        gaps.sort(key=lambda x: self._priority_score(x), reverse=True)

        # Save report
        self._save_gaps_report(gaps)

        return gaps

    def _get_existing_guides(self, category: str) -> Set[str]:
        """Get list of existing guide topics in a category."""
        category_path = self.knowledge_path / category

        if not category_path.exists():
            return set()

        guides = category_path.glob("*.md")
        return {g.stem for g in guides}

    def _topic_exists(self, topic: str, existing: Set[str]) -> bool:
        """Check if a topic exists (fuzzy match for variations)."""
        # Exact match
        if topic in existing:
            return True

        # Fuzzy match (handles different naming conventions)
        topic_words = set(topic.lower().replace('-', ' ').split())

        for existing_topic in existing:
            existing_words = set(existing_topic.lower().replace('-', ' ').split())
            # If 2+ words match, consider it exists
            if len(topic_words & existing_words) >= 2:
                return True

        return False

    def _calculate_priority(self, category: str, topic: str, level: str) -> str:
        """Calculate priority level for a gap."""
        # Safety-critical topics
        safety_keywords = ['safety', 'treatment', 'emergency', 'first-aid', 'purification']
        if any(kw in topic for kw in safety_keywords):
            return 'critical'

        # Core topics are high priority
        if level == 'core':
            return 'high'

        # Commonly needed skills
        common_keywords = ['starting', 'basic', 'collection', 'construction', 'use']
        if any(kw in topic for kw in common_keywords):
            return 'high'

        # Advanced topics
        if level == 'advanced':
            return 'medium'

        return 'low'

    def _priority_score(self, gap: KnowledgeGap) -> int:
        """Calculate numeric priority score for sorting."""
        base_scores = {
            'critical': 100,
            'high': 75,
            'medium': 50,
            'low': 25
        }

        score = base_scores.get(gap.priority, 0)

        # Boost score for categories with fewer guides
        category_count = len(self._get_existing_guides(gap.category))
        if category_count < 15:
            score += 10

        # Boost tier 2 (core) over tier 3
        if gap.tier == 2:
            score += 5

        return score

    def _find_related_topics(self, category: str, topic: str) -> List[str]:
        """Find related topics for cross-referencing."""
        related = []

        # Topics in same category
        all_topics = (self.expected_coverage.get(category, {}).get('core', []) +
                     self.expected_coverage.get(category, {}).get('advanced', []))

        # Find topics with shared keywords
        topic_words = set(topic.lower().replace('-', ' ').split())

        for other_topic in all_topics:
            if other_topic == topic:
                continue

            other_words = set(other_topic.lower().replace('-', ' ').split())
            if topic_words & other_words:
                related.append(other_topic)

        return related[:3]  # Top 3 related

    def _save_gaps_report(self, gaps: List[KnowledgeGap]):
        """Save gaps analysis to JSON report."""
        self.gaps_report_path.parent.mkdir(parents=True, exist_ok=True)

        report = {
            'analysis_date': Path().cwd().joinpath('.').stat().st_mtime,
            'total_gaps': len(gaps),
            'by_priority': {
                'critical': len([g for g in gaps if g.priority == 'critical']),
                'high': len([g for g in gaps if g.priority == 'high']),
                'medium': len([g for g in gaps if g.priority == 'medium']),
                'low': len([g for g in gaps if g.priority == 'low'])
            },
            'by_category': {
                cat: len([g for g in gaps if g.category == cat])
                for cat in self.expected_coverage.keys()
            },
            'gaps': [asdict(g) for g in gaps]
        }

        self.gaps_report_path.write_text(json.dumps(report, indent=2))

    def generate_creation_workflow(self, gaps: List[KnowledgeGap],
                                   max_guides: int = 10) -> str:
        """Generate .upy workflow to create missing guides."""
        workflow_path = PATHS.MEMORY_WORKFLOWS / "fill-knowledge-gaps.upy"

        # Take top N highest priority gaps
        top_gaps = gaps[:max_guides]

        workflow = f"""#!/usr/bin/env udos
# Fill Knowledge Gaps Workflow
# Auto-generated from gap analysis
# Total gaps identified: {len(gaps)}
# Creating top {len(top_gaps)} highest priority

MISSION CREATE "Fill Knowledge Gaps"
SET $objective "Create {len(top_gaps)} missing high-priority guides"

"""

        for i, gap in enumerate(top_gaps, 1):
            workflow += f"""
# Gap {i}/{len(top_gaps)}: {gap.topic} ({gap.priority} priority)
ECHO "[{i}/{len(top_gaps)}] Creating: {gap.topic}"
GENERATE GUIDE "{gap.topic.replace('-', ' ').title()}" --category {gap.category} --save
CHECKPOINT SAVE "gap-filled-{gap.topic}"

"""

        workflow += """
# Verify gaps were filled
WORKFLOW START knowledge-gap-analysis --verify

MISSION COMPLETE
"""

        workflow_path.write_text(workflow)
        return str(workflow_path)


# CLI interface
if __name__ == "__main__":
    import sys

    analyzer = GapAnalyzer()

    if '--analyze' in sys.argv:
        gaps = analyzer.analyze_gaps()

        print(f"\n📊 Knowledge Gap Analysis:")
        print(f"   Total gaps: {len(gaps)}")
        print(f"\n🎯 By Priority:")
        for priority in ['critical', 'high', 'medium', 'low']:
            count = len([g for g in gaps if g.priority == priority])
            print(f"   {priority.title()}: {count}")

        print(f"\n📂 By Category:")
        for category in analyzer.expected_coverage.keys():
            count = len([g for g in gaps if g.category == category])
            print(f"   {category.title()}: {count}")

        print(f"\n💾 Gap report saved to: {analyzer.gaps_report_path}")

        if '--generate-workflow' in sys.argv:
            workflow_path = analyzer.generate_creation_workflow(gaps)
            print(f"📝 Creation workflow generated: {workflow_path}")

    else:
        print("Usage: python knowledge_gap_analyzer.py --analyze [--generate-workflow]")

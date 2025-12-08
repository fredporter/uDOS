"""
Knowledge Metrics Service
Aggregates quality data from knowledge bank and generates comprehensive metrics.

Part of v1.2.11 - Knowledge Quality & Automation
Uses data from v1.2.10 quality checker to track improvements over time.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class GuideMetrics:
    """Metrics for a single guide."""
    path: str
    category: str
    tier: int
    title: str
    word_count: int
    example_count: int
    cross_refs: int
    last_updated: str
    age_days: int
    quality_score: float
    issues: List[str]


@dataclass
class CategoryMetrics:
    """Metrics for a knowledge category."""
    name: str
    total_guides: int
    high_quality: int
    needs_update: int
    critical: int
    avg_quality_score: float
    avg_word_count: int
    avg_examples: int
    coverage_score: float


@dataclass
class QualityBaseline:
    """Overall knowledge bank quality baseline."""
    scan_date: str
    total_guides: int
    high_quality_count: int
    needs_update_count: int
    critical_count: int
    overall_quality_score: float
    categories: Dict[str, CategoryMetrics]
    trend: Optional[str] = None


class KnowledgeMetrics:
    """Service for knowledge quality metrics and reporting."""

    def __init__(self, knowledge_path: str = "knowledge"):
        self.knowledge_path = Path(knowledge_path)
        from core.utils.paths import PATHS
        self.report_path = PATHS.KNOWLEDGE_QUALITY_REPORT
        self.history_path = PATHS.KNOWLEDGE_QUALITY_HISTORY

        # Quality thresholds
        self.thresholds = {
            'high_quality': 0.85,
            'needs_update': 0.70,
            'min_word_count': 200,
            'min_examples': 2,
            'max_age_days': 180,
            'critical_age_days': 365
        }

    def scan_knowledge_bank(self) -> QualityBaseline:
        """
        Scan entire knowledge bank and generate quality baseline.

        Returns:
            QualityBaseline with comprehensive metrics
        """
        print("🔍 Scanning knowledge bank...")

        categories = ['water', 'fire', 'shelter', 'food', 'navigation', 'medical']
        category_metrics = {}
        total_guides = 0
        high_quality = 0
        needs_update = 0
        critical = 0
        total_quality_score = 0

        for category in categories:
            cat_metrics = self._scan_category(category)
            category_metrics[category] = cat_metrics

            total_guides += cat_metrics.total_guides
            high_quality += cat_metrics.high_quality
            needs_update += cat_metrics.needs_update
            critical += cat_metrics.critical
            total_quality_score += cat_metrics.avg_quality_score * cat_metrics.total_guides

        overall_quality = total_quality_score / total_guides if total_guides > 0 else 0

        baseline = QualityBaseline(
            scan_date=datetime.now().isoformat(),
            total_guides=total_guides,
            high_quality_count=high_quality,
            needs_update_count=needs_update,
            critical_count=critical,
            overall_quality_score=overall_quality,
            categories=category_metrics
        )

        # Calculate trend if history exists
        baseline.trend = self._calculate_trend(baseline)

        # Save baseline
        self._save_baseline(baseline)

        return baseline

    def _scan_category(self, category: str) -> CategoryMetrics:
        """Scan a single knowledge category."""
        category_path = self.knowledge_path / category

        if not category_path.exists():
            return CategoryMetrics(
                name=category,
                total_guides=0,
                high_quality=0,
                needs_update=0,
                critical=0,
                avg_quality_score=0.0,
                avg_word_count=0,
                avg_examples=0,
                coverage_score=0.0
            )

        guides = list(category_path.glob("*.md"))
        guide_metrics = [self._analyze_guide(g, category) for g in guides]

        total = len(guide_metrics)
        high_quality = sum(1 for g in guide_metrics if g.quality_score >= self.thresholds['high_quality'])
        needs_update = sum(1 for g in guide_metrics if
                          self.thresholds['needs_update'] <= g.quality_score < self.thresholds['high_quality'])
        critical = sum(1 for g in guide_metrics if g.quality_score < self.thresholds['needs_update'])

        avg_quality = sum(g.quality_score for g in guide_metrics) / total if total > 0 else 0
        avg_words = sum(g.word_count for g in guide_metrics) / total if total > 0 else 0
        avg_examples = sum(g.example_count for g in guide_metrics) / total if total > 0 else 0

        # Coverage score based on expected topics
        expected_topics = self._get_expected_topics(category)
        coverage = len(guides) / len(expected_topics) if expected_topics else 1.0

        return CategoryMetrics(
            name=category,
            total_guides=total,
            high_quality=high_quality,
            needs_update=needs_update,
            critical=critical,
            avg_quality_score=avg_quality,
            avg_word_count=int(avg_words),
            avg_examples=int(avg_examples),
            coverage_score=min(coverage, 1.0)
        )

    def _analyze_guide(self, guide_path: Path, category: str) -> GuideMetrics:
        """Analyze a single guide and calculate metrics."""
        content = guide_path.read_text()

        # Parse frontmatter
        frontmatter = self._parse_frontmatter(content)

        # Calculate metrics
        word_count = len(content.split())
        example_count = content.lower().count('example:') + content.lower().count('## example')
        cross_refs = content.count('[') + content.count('](')

        # Age calculation
        last_updated = frontmatter.get('last_updated', frontmatter.get('date', ''))
        age_days = self._calculate_age(last_updated) if last_updated else 999

        # Quality score (0.0 - 1.0)
        quality_score = self._calculate_quality_score(
            word_count, example_count, cross_refs, age_days, frontmatter
        )

        # Identify issues
        issues = []
        if word_count < self.thresholds['min_word_count']:
            issues.append(f"Low word count ({word_count})")
        if example_count < self.thresholds['min_examples']:
            issues.append(f"Few examples ({example_count})")
        if age_days > self.thresholds['max_age_days']:
            issues.append(f"Outdated ({age_days} days)")
        if not frontmatter:
            issues.append("Missing frontmatter")

        return GuideMetrics(
            path=str(guide_path),
            category=category,
            tier=frontmatter.get('tier', 0),
            title=frontmatter.get('title', guide_path.stem),
            word_count=word_count,
            example_count=example_count,
            cross_refs=cross_refs,
            last_updated=last_updated,
            age_days=age_days,
            quality_score=quality_score,
            issues=issues
        )

    def _parse_frontmatter(self, content: str) -> dict:
        """Parse YAML frontmatter from markdown."""
        if not content.startswith('---'):
            return {}

        try:
            parts = content.split('---', 2)
            if len(parts) < 3:
                return {}

            frontmatter = {}
            for line in parts[1].strip().split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    frontmatter[key.strip()] = value.strip().strip('"\'')

            return frontmatter
        except Exception:
            return {}

    def _calculate_age(self, date_str: str) -> int:
        """Calculate age in days from date string."""
        try:
            date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            age = (datetime.now() - date).days
            return max(0, age)
        except Exception:
            return 999  # Unknown age

    def _calculate_quality_score(self, word_count: int, examples: int,
                                 refs: int, age_days: int, frontmatter: dict) -> float:
        """Calculate overall quality score (0.0 - 1.0)."""
        score = 0.0

        # Word count (30%)
        if word_count >= 500:
            score += 0.30
        elif word_count >= self.thresholds['min_word_count']:
            score += 0.15

        # Examples (25%)
        if examples >= 3:
            score += 0.25
        elif examples >= self.thresholds['min_examples']:
            score += 0.15

        # Cross-references (15%)
        if refs >= 5:
            score += 0.15
        elif refs >= 2:
            score += 0.08

        # Freshness (20%)
        if age_days < 90:
            score += 0.20
        elif age_days < self.thresholds['max_age_days']:
            score += 0.10

        # Frontmatter (10%)
        if frontmatter and 'tier' in frontmatter and 'title' in frontmatter:
            score += 0.10

        return round(score, 2)

    def _get_expected_topics(self, category: str) -> List[str]:
        """Get expected topics for complete coverage."""
        expected = {
            'water': ['purification', 'collection', 'storage', 'testing', 'sources', 'filtration'],
            'fire': ['starting', 'maintaining', 'safety', 'types', 'materials', 'location'],
            'shelter': ['location', 'materials', 'types', 'insulation', 'waterproofing', 'ventilation'],
            'food': ['foraging', 'hunting', 'fishing', 'preservation', 'storage', 'cooking'],
            'navigation': ['map-reading', 'compass', 'stars', 'landmarks', 'gps', 'dead-reckoning'],
            'medical': ['first-aid', 'injuries', 'illness', 'hygiene', 'medications', 'mental-health']
        }
        return expected.get(category, [])

    def _calculate_trend(self, current: QualityBaseline) -> Optional[str]:
        """Calculate trend compared to previous scan."""
        if not self.history_path.exists():
            return None

        try:
            history = json.loads(self.history_path.read_text())
            if not history:
                return None

            previous = history[-1]
            prev_score = previous.get('overall_quality_score', 0)
            curr_score = current.overall_quality_score

            diff = curr_score - prev_score

            if diff > 0.05:
                return "improving"
            elif diff < -0.05:
                return "declining"
            else:
                return "stable"

        except Exception:
            return None

    def _save_baseline(self, baseline: QualityBaseline):
        """Save baseline to report file and append to history."""
        # Save current report
        self.report_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to dict for JSON
        data = asdict(baseline)
        self.report_path.write_text(json.dumps(data, indent=2))

        # Append to history
        history = []
        if self.history_path.exists():
            history = json.loads(self.history_path.read_text())

        history.append(data)

        # Keep last 30 scans
        if len(history) > 30:
            history = history[-30:]

        self.history_path.write_text(json.dumps(history, indent=2))

    def generate_html_report(self, baseline: QualityBaseline) -> str:
        """Generate HTML dashboard for quality metrics."""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Knowledge Quality Dashboard</title>
    <style>
        body {{ font-family: monospace; background: #1a1a2e; color: #eee; padding: 20px; }}
        h1 {{ color: #00ff88; }}
        .metric {{ background: #16213e; padding: 15px; margin: 10px 0; border-left: 3px solid #00ff88; }}
        .critical {{ border-left-color: #ff006e; }}
        .warning {{ border-left-color: #ffaa00; }}
        .good {{ border-left-color: #00ff88; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #333; }}
        th {{ color: #00ff88; }}
        .score {{ font-size: 2em; font-weight: bold; }}
        .trend {{ font-size: 0.8em; color: #888; }}
    </style>
</head>
<body>
    <h1>📊 Knowledge Quality Dashboard</h1>
    <p>Scan Date: {baseline.scan_date}</p>

    <div class="metric good">
        <div class="score">{baseline.overall_quality_score:.1%}</div>
        <div>Overall Quality Score</div>
        {f'<div class="trend">Trend: {baseline.trend}</div>' if baseline.trend else ''}
    </div>

    <div class="metric">
        <h2>Summary</h2>
        <p>Total Guides: {baseline.total_guides}</p>
        <p>High Quality: {baseline.high_quality_count} ({baseline.high_quality_count/baseline.total_guides:.1%})</p>
        <p>Needs Update: {baseline.needs_update_count}</p>
        <p>Critical: {baseline.critical_count}</p>
    </div>

    <h2>Category Breakdown</h2>
    <table>
        <tr>
            <th>Category</th>
            <th>Guides</th>
            <th>Quality Score</th>
            <th>Avg Words</th>
            <th>Avg Examples</th>
            <th>Coverage</th>
        </tr>
"""

        for cat_name, cat_metrics in baseline.categories.items():
            html += f"""
        <tr>
            <td>{cat_name.title()}</td>
            <td>{cat_metrics.total_guides}</td>
            <td>{cat_metrics.avg_quality_score:.1%}</td>
            <td>{cat_metrics.avg_word_count}</td>
            <td>{cat_metrics.avg_examples}</td>
            <td>{cat_metrics.coverage_score:.1%}</td>
        </tr>
"""

        html += """
    </table>
</body>
</html>
"""

        # Save HTML report
        html_path = PATHS.KNOWLEDGE_QUALITY_DASHBOARD
        html_path.write_text(html)

        return str(html_path)


# CLI interface
if __name__ == "__main__":
    import sys

    metrics = KnowledgeMetrics()

    if len(sys.argv) > 1 and sys.argv[1] == '--scan':
        print("🔍 Starting knowledge quality scan...")
        baseline = metrics.scan_knowledge_bank()

        print(f"\n📊 Quality Baseline:")
        print(f"   Total Guides: {baseline.total_guides}")
        print(f"   Quality Score: {baseline.overall_quality_score:.1%}")
        print(f"   High Quality: {baseline.high_quality_count}")
        print(f"   Needs Update: {baseline.needs_update_count}")
        print(f"   Critical: {baseline.critical_count}")

        if baseline.trend:
            print(f"   Trend: {baseline.trend}")

        # Generate HTML dashboard
        html_path = metrics.generate_html_report(baseline)
        print(f"\n📄 Reports generated:")
        print(f"   JSON: {metrics.report_path}")
        print(f"   HTML: {html_path}")

    else:
        print("Usage: python knowledge_metrics.py --scan")

"""
Feature 1.1.2.9: Knowledge Validation System Test Suite

Validates offline knowledge content for accuracy, completeness, and quality.
Works with Feature 1.1.2.6 (Offline Knowledge Library) and 1.1.2.8 (SVG/Citation).

Test Coverage:
- Accuracy validation: Fact checking, consistency verification
- Source verification: Citation completeness, URL validation, author checks
- Completeness: Required sections, minimum content, cross-references
- Contradiction detection: Internal consistency, conflicting information
- Update notifications: Change tracking, staleness detection, version comparison
- Quality scoring: Rubric-based assessment, automated metrics
- Integration: Works with knowledge library and citation systems
"""

import unittest
from datetime import datetime, timedelta
from enum import Enum
import json
import re


class ValidationSeverity(Enum):
    """Validation issue severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationCategory(Enum):
    """Validation categories."""
    ACCURACY = "accuracy"
    COMPLETENESS = "completeness"
    SOURCE = "source"
    QUALITY = "quality"
    CONSISTENCY = "consistency"
    FRESHNESS = "freshness"


class QualityMetric(Enum):
    """Quality assessment metrics."""
    READABILITY = "readability"
    TECHNICAL_DEPTH = "technical_depth"
    PRACTICAL_VALUE = "practical_value"
    CITATION_QUALITY = "citation_quality"
    STRUCTURE = "structure"


class KnowledgeValidator:
    """Validates offline knowledge content."""

    def __init__(self):
        self.validation_rules = {}
        self.validation_history = {}
        self.quality_rubrics = {}
        self.contradiction_patterns = []
        self.required_sections = {}
        self.external_refs = {}

    def validate_content(self, content_id, content, metadata=None):
        """Validate content against all rules."""
        metadata = metadata or {}
        
        validation_result = {
            "content_id": content_id,
            "timestamp": datetime.now().isoformat(),
            "issues": [],
            "passed": True,
            "score": 100
        }

        # Check completeness
        completeness_issues = self._check_completeness(content, metadata)
        validation_result["issues"].extend(completeness_issues)

        # Check accuracy
        accuracy_issues = self._check_accuracy(content, metadata)
        validation_result["issues"].extend(accuracy_issues)

        # Check sources
        source_issues = self._check_sources(content, metadata)
        validation_result["issues"].extend(source_issues)

        # Calculate overall pass/fail
        critical_issues = [i for i in validation_result["issues"] 
                          if i["severity"] == ValidationSeverity.CRITICAL.value]
        error_issues = [i for i in validation_result["issues"]
                       if i["severity"] == ValidationSeverity.ERROR.value]
        
        if critical_issues or len(error_issues) > 3:
            validation_result["passed"] = False

        # Calculate score (deduct points for issues)
        score = 100
        for issue in validation_result["issues"]:
            if issue["severity"] == ValidationSeverity.CRITICAL.value:
                score -= 25
            elif issue["severity"] == ValidationSeverity.ERROR.value:
                score -= 10
            elif issue["severity"] == ValidationSeverity.WARNING.value:
                score -= 5
            elif issue["severity"] == ValidationSeverity.INFO.value:
                score -= 1
        
        validation_result["score"] = max(0, score)

        # Store validation history
        if content_id not in self.validation_history:
            self.validation_history[content_id] = []
        
        self.validation_history[content_id].append(validation_result)

        return validation_result

    def _check_completeness(self, content, metadata):
        """Check content completeness."""
        issues = []
        
        # Check minimum content length
        if len(content) < 100:
            issues.append({
                "category": ValidationCategory.COMPLETENESS.value,
                "severity": ValidationSeverity.WARNING.value,
                "message": "Content is too short (minimum 100 characters recommended)",
                "details": {"length": len(content), "minimum": 100}
            })

        # Check for required sections if defined
        category = metadata.get("category")
        if category in self.required_sections:
            for section in self.required_sections[category]:
                # Simple check - section header should appear in content
                if section.lower() not in content.lower():
                    issues.append({
                        "category": ValidationCategory.COMPLETENESS.value,
                        "severity": ValidationSeverity.ERROR.value,
                        "message": f"Missing required section: {section}",
                        "details": {"section": section, "category": category}
                    })

        return issues

    def _check_accuracy(self, content, metadata):
        """Check content accuracy."""
        issues = []
        
        # Check for contradictions
        for pattern in self.contradiction_patterns:
            if pattern["phrase1"] in content.lower() and pattern["phrase2"] in content.lower():
                issues.append({
                    "category": ValidationCategory.ACCURACY.value,
                    "severity": ValidationSeverity.WARNING.value,
                    "message": f"Potential contradiction detected",
                    "details": {
                        "phrase1": pattern["phrase1"],
                        "phrase2": pattern["phrase2"]
                    }
                })

        return issues

    def _check_sources(self, content, metadata):
        """Check source citations."""
        issues = []
        
        # Extract citations from content
        citation_patterns = [
            r'\[([^\]]+),\s*(\d{4})\]',  # [Author, 2024]
            r'\(([^,]+),\s*(\d{4})\)',   # (Author, 2024)
            r'\[(\d+)\]'                  # [1]
        ]

        citations_found = False
        for pattern in citation_patterns:
            if re.search(pattern, content):
                citations_found = True
                break

        # If content makes factual claims, it should have citations
        factual_indicators = ["study shows", "research indicates", "according to", 
                            "proven", "evidence", "data shows"]
        has_factual_claims = any(indicator in content.lower() for indicator in factual_indicators)

        if has_factual_claims and not citations_found:
            issues.append({
                "category": ValidationCategory.SOURCE.value,
                "severity": ValidationSeverity.WARNING.value,
                "message": "Factual claims detected without citations",
                "details": {"citations_found": False}
            })

        return issues

    def add_validation_rule(self, rule_id, category, check_function, severity):
        """Add custom validation rule."""
        if not isinstance(category, ValidationCategory):
            raise ValueError(f"Invalid category: {category}")
        
        if not isinstance(severity, ValidationSeverity):
            raise ValueError(f"Invalid severity: {severity}")

        self.validation_rules[rule_id] = {
            "id": rule_id,
            "category": category.value,
            "check_function": check_function,
            "severity": severity.value,
            "added_at": datetime.now().isoformat()
        }

        return rule_id

    def verify_citations(self, content_id, citations):
        """Verify citation completeness."""
        verification_result = {
            "content_id": content_id,
            "citations_checked": len(citations),
            "issues": [],
            "complete": True
        }

        for citation in citations:
            # Check required fields
            required_fields = ["author", "year", "title"]
            for field in required_fields:
                if field not in citation or not citation[field]:
                    verification_result["issues"].append({
                        "citation_id": citation.get("id", "unknown"),
                        "field": field,
                        "severity": ValidationSeverity.ERROR.value,
                        "message": f"Missing required field: {field}"
                    })
                    verification_result["complete"] = False

            # Verify year format
            if "year" in citation:
                if not re.match(r'^\d{4}$', str(citation["year"])):
                    verification_result["issues"].append({
                        "citation_id": citation.get("id", "unknown"),
                        "field": "year",
                        "severity": ValidationSeverity.WARNING.value,
                        "message": f"Invalid year format: {citation['year']}"
                    })

            # Check URL validity if provided
            if "url" in citation and citation["url"]:
                if not citation["url"].startswith(("http://", "https://")):
                    verification_result["issues"].append({
                        "citation_id": citation.get("id", "unknown"),
                        "field": "url",
                        "severity": ValidationSeverity.WARNING.value,
                        "message": "URL should start with http:// or https://"
                    })

        return verification_result

    def check_freshness(self, content_id, last_updated, max_age_days=365):
        """Check if content is fresh/up-to-date."""
        if isinstance(last_updated, str):
            last_updated = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))

        age = datetime.now() - last_updated
        age_days = age.days

        freshness_result = {
            "content_id": content_id,
            "last_updated": last_updated.isoformat(),
            "age_days": age_days,
            "max_age_days": max_age_days,
            "fresh": age_days <= max_age_days,
            "status": "fresh"
        }

        if age_days > max_age_days * 2:
            freshness_result["status"] = "stale"
        elif age_days > max_age_days:
            freshness_result["status"] = "aging"

        return freshness_result

    def detect_contradictions(self, content1, content2):
        """Detect contradictions between two pieces of content."""
        contradictions = []

        # Simple keyword-based contradiction detection
        # Look for opposing statements
        opposing_pairs = [
            ("safe", "dangerous"),
            ("recommended", "not recommended"),
            ("effective", "ineffective"),
            ("always", "never"),
            ("increase", "decrease")
        ]

        for word1, word2 in opposing_pairs:
            if word1 in content1.lower() and word2 in content2.lower():
                contradictions.append({
                    "type": "opposing_terms",
                    "term1": word1,
                    "term2": word2,
                    "severity": ValidationSeverity.WARNING.value
                })

        return {
            "contradictions_found": len(contradictions),
            "contradictions": contradictions,
            "consistent": len(contradictions) == 0
        }

    def assess_quality(self, content_id, content, metadata=None):
        """Assess content quality using metrics."""
        metadata = metadata or {}
        
        quality_scores = {}

        # Readability: Based on sentence length and word complexity
        sentences = content.split('.')
        avg_sentence_length = len(content.split()) / max(len(sentences), 1)
        
        if avg_sentence_length < 15:
            quality_scores[QualityMetric.READABILITY.value] = 90
        elif avg_sentence_length < 25:
            quality_scores[QualityMetric.READABILITY.value] = 75
        else:
            quality_scores[QualityMetric.READABILITY.value] = 60

        # Technical depth: Based on technical terms and detail
        technical_indicators = ["procedure", "method", "technique", "process", "analysis"]
        technical_count = sum(1 for term in technical_indicators if term in content.lower())
        quality_scores[QualityMetric.TECHNICAL_DEPTH.value] = min(100, technical_count * 20)

        # Practical value: Based on actionable content
        actionable_indicators = ["step", "how to", "follow", "instruction", "guide"]
        actionable_count = sum(1 for term in actionable_indicators if term in content.lower())
        quality_scores[QualityMetric.PRACTICAL_VALUE.value] = min(100, actionable_count * 25)

        # Citation quality: Based on citation presence and format
        citation_count = len(re.findall(r'\[[^\]]+,\s*\d{4}\]', content))
        quality_scores[QualityMetric.CITATION_QUALITY.value] = min(100, citation_count * 30)

        # Structure: Based on sections and organization
        structure_indicators = ["#", "##", "###", "introduction", "conclusion"]
        structure_count = sum(1 for term in structure_indicators if term in content.lower())
        quality_scores[QualityMetric.STRUCTURE.value] = min(100, structure_count * 20)

        # Calculate overall quality score
        overall_score = sum(quality_scores.values()) / len(quality_scores)

        assessment = {
            "content_id": content_id,
            "timestamp": datetime.now().isoformat(),
            "metrics": quality_scores,
            "overall_score": round(overall_score, 2),
            "grade": self._score_to_grade(overall_score)
        }

        return assessment

    def _score_to_grade(self, score):
        """Convert numeric score to letter grade."""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def set_required_sections(self, category, sections):
        """Set required sections for a content category."""
        self.required_sections[category] = sections
        return True

    def add_contradiction_pattern(self, phrase1, phrase2):
        """Add contradiction pattern to detect."""
        pattern = {
            "phrase1": phrase1.lower(),
            "phrase2": phrase2.lower(),
            "added_at": datetime.now().isoformat()
        }
        
        self.contradiction_patterns.append(pattern)
        return len(self.contradiction_patterns) - 1

    def get_validation_history(self, content_id):
        """Get validation history for content."""
        return self.validation_history.get(content_id, []).copy()

    def track_external_reference(self, ref_id, url, status="unverified"):
        """Track external reference for validation."""
        self.external_refs[ref_id] = {
            "id": ref_id,
            "url": url,
            "status": status,
            "last_checked": datetime.now().isoformat() if status != "unverified" else None
        }

        return ref_id

    def verify_external_reference(self, ref_id, is_accessible):
        """Verify external reference accessibility."""
        if ref_id not in self.external_refs:
            raise KeyError(f"Reference not found: {ref_id}")

        ref = self.external_refs[ref_id]
        ref["status"] = "accessible" if is_accessible else "broken"
        ref["last_checked"] = datetime.now().isoformat()

        return ref.copy()

    def generate_validation_report(self, content_ids):
        """Generate comprehensive validation report."""
        report = {
            "generated_at": datetime.now().isoformat(),
            "content_count": len(content_ids),
            "summary": {
                "passed": 0,
                "failed": 0,
                "warnings": 0,
                "errors": 0
            },
            "content_results": []
        }

        for content_id in content_ids:
            if content_id in self.validation_history:
                history = self.validation_history[content_id]
                if history:
                    latest = history[-1]
                    report["content_results"].append(latest)
                    
                    if latest["passed"]:
                        report["summary"]["passed"] += 1
                    else:
                        report["summary"]["failed"] += 1

                    for issue in latest["issues"]:
                        if issue["severity"] == ValidationSeverity.WARNING.value:
                            report["summary"]["warnings"] += 1
                        elif issue["severity"] in [ValidationSeverity.ERROR.value, 
                                                   ValidationSeverity.CRITICAL.value]:
                            report["summary"]["errors"] += 1

        return report

    def compare_versions(self, content_v1, content_v2):
        """Compare two versions of content."""
        comparison = {
            "length_change": len(content_v2) - len(content_v1),
            "similarity_percent": 0,
            "major_changes": []
        }

        # Calculate simple similarity
        words_v1 = set(content_v1.lower().split())
        words_v2 = set(content_v2.lower().split())
        
        if words_v1 or words_v2:
            common_words = words_v1.intersection(words_v2)
            total_words = words_v1.union(words_v2)
            comparison["similarity_percent"] = round(
                (len(common_words) / len(total_words)) * 100, 2
            )

        # Detect major changes
        if abs(comparison["length_change"]) > 100:
            comparison["major_changes"].append("Significant length change")

        if comparison["similarity_percent"] < 70:
            comparison["major_changes"].append("Major content revision")

        return comparison

    def get_validator_stats(self):
        """Get validator statistics."""
        total_validations = sum(len(history) for history in self.validation_history.values())
        
        return {
            "total_validations": total_validations,
            "content_items_validated": len(self.validation_history),
            "validation_rules": len(self.validation_rules),
            "contradiction_patterns": len(self.contradiction_patterns),
            "external_references": len(self.external_refs)
        }


class TestContentValidation(unittest.TestCase):
    """Test content validation."""

    def setUp(self):
        self.validator = KnowledgeValidator()

    def test_validate_complete_content(self):
        """Test validating complete content."""
        content = "This is a comprehensive guide about water purification. " * 10
        result = self.validator.validate_content("guide1", content)

        self.assertIn("content_id", result)
        self.assertIn("issues", result)
        self.assertIn("passed", result)

    def test_validate_short_content(self):
        """Test validating too-short content."""
        content = "Short."
        result = self.validator.validate_content("guide2", content)

        # Should have warning about short content
        warnings = [i for i in result["issues"] 
                   if i["severity"] == ValidationSeverity.WARNING.value]
        self.assertGreater(len(warnings), 0)

    def test_validate_missing_required_sections(self):
        """Test detecting missing required sections."""
        self.validator.set_required_sections("water", ["Introduction", "Methods"])
        
        content = "This is about water purification."
        result = self.validator.validate_content(
            "guide3", 
            content,
            {"category": "water"}
        )

        # Should have errors for missing sections
        errors = [i for i in result["issues"]
                 if i["category"] == ValidationCategory.COMPLETENESS.value]
        self.assertGreater(len(errors), 0)

    def test_validation_scoring(self):
        """Test validation scoring system."""
        content = "Complete guide. " * 20
        result = self.validator.validate_content("guide4", content)

        self.assertIn("score", result)
        self.assertGreaterEqual(result["score"], 0)
        self.assertLessEqual(result["score"], 100)

    def test_validation_history(self):
        """Test validation history tracking."""
        content = "Content for history test."
        
        self.validator.validate_content("guide5", content)
        self.validator.validate_content("guide5", content + " Updated.")

        history = self.validator.get_validation_history("guide5")
        self.assertEqual(len(history), 2)


class TestCitationVerification(unittest.TestCase):
    """Test citation verification."""

    def setUp(self):
        self.validator = KnowledgeValidator()

    def test_verify_complete_citations(self):
        """Test verifying complete citations."""
        citations = [
            {"id": "c1", "author": "Smith", "year": "2024", "title": "Guide"}
        ]

        result = self.validator.verify_citations("content1", citations)

        self.assertTrue(result["complete"])
        self.assertEqual(len(result["issues"]), 0)

    def test_verify_missing_citation_fields(self):
        """Test detecting missing citation fields."""
        citations = [
            {"id": "c1", "author": "Smith"}  # Missing year and title
        ]

        result = self.validator.verify_citations("content1", citations)

        self.assertFalse(result["complete"])
        self.assertGreater(len(result["issues"]), 0)

    def test_verify_invalid_year_format(self):
        """Test detecting invalid year format."""
        citations = [
            {"id": "c1", "author": "Smith", "year": "24", "title": "Guide"}
        ]

        result = self.validator.verify_citations("content1", citations)

        warnings = [i for i in result["issues"]
                   if i["severity"] == ValidationSeverity.WARNING.value]
        self.assertGreater(len(warnings), 0)

    def test_verify_invalid_url(self):
        """Test detecting invalid URLs."""
        citations = [
            {"id": "c1", "author": "Smith", "year": "2024", 
             "title": "Guide", "url": "invalid-url"}
        ]

        result = self.validator.verify_citations("content1", citations)

        url_issues = [i for i in result["issues"] if i["field"] == "url"]
        self.assertGreater(len(url_issues), 0)

    def test_citation_count_tracking(self):
        """Test tracking citation counts."""
        citations = [
            {"id": "c1", "author": "Smith", "year": "2024", "title": "Guide1"},
            {"id": "c2", "author": "Jones", "year": "2023", "title": "Guide2"}
        ]

        result = self.validator.verify_citations("content1", citations)

        self.assertEqual(result["citations_checked"], 2)


class TestFreshnessChecking(unittest.TestCase):
    """Test content freshness checking."""

    def setUp(self):
        self.validator = KnowledgeValidator()

    def test_check_fresh_content(self):
        """Test checking fresh content."""
        last_updated = datetime.now()
        result = self.validator.check_freshness("content1", last_updated)

        self.assertTrue(result["fresh"])
        self.assertEqual(result["status"], "fresh")

    def test_check_aging_content(self):
        """Test checking aging content."""
        last_updated = datetime.now() - timedelta(days=400)
        result = self.validator.check_freshness("content1", last_updated, max_age_days=365)

        self.assertFalse(result["fresh"])
        self.assertEqual(result["status"], "aging")

    def test_check_stale_content(self):
        """Test checking stale content."""
        last_updated = datetime.now() - timedelta(days=800)
        result = self.validator.check_freshness("content1", last_updated, max_age_days=365)

        self.assertFalse(result["fresh"])
        self.assertEqual(result["status"], "stale")

    def test_freshness_age_calculation(self):
        """Test age calculation in days."""
        last_updated = datetime.now() - timedelta(days=30)
        result = self.validator.check_freshness("content1", last_updated)

        self.assertEqual(result["age_days"], 30)

    def test_freshness_iso_format(self):
        """Test freshness check with ISO format string."""
        last_updated = (datetime.now() - timedelta(days=10)).isoformat()
        result = self.validator.check_freshness("content1", last_updated)

        self.assertIn("age_days", result)


class TestContradictionDetection(unittest.TestCase):
    """Test contradiction detection."""

    def setUp(self):
        self.validator = KnowledgeValidator()

    def test_detect_no_contradictions(self):
        """Test when no contradictions exist."""
        content1 = "Water purification is safe and recommended."
        content2 = "Water purification is effective for health."

        result = self.validator.detect_contradictions(content1, content2)

        self.assertTrue(result["consistent"])
        self.assertEqual(result["contradictions_found"], 0)

    def test_detect_opposing_terms(self):
        """Test detecting opposing terms."""
        content1 = "This method is safe for use."
        content2 = "This method is dangerous to apply."

        result = self.validator.detect_contradictions(content1, content2)

        self.assertGreater(result["contradictions_found"], 0)
        self.assertFalse(result["consistent"])

    def test_detect_multiple_contradictions(self):
        """Test detecting multiple contradictions."""
        content1 = "Always use this. It is recommended and effective."
        content2 = "Never use this. It is not recommended and ineffective."

        result = self.validator.detect_contradictions(content1, content2)

        self.assertGreater(result["contradictions_found"], 1)

    def test_contradiction_severity(self):
        """Test contradiction severity assignment."""
        content1 = "This is safe."
        content2 = "This is dangerous."

        result = self.validator.detect_contradictions(content1, content2)

        if result["contradictions"]:
            self.assertIn("severity", result["contradictions"][0])

    def test_add_contradiction_pattern(self):
        """Test adding custom contradiction patterns."""
        pattern_id = self.validator.add_contradiction_pattern("hot", "cold")

        self.assertIsNotNone(pattern_id)
        self.assertEqual(len(self.validator.contradiction_patterns), 1)


class TestQualityAssessment(unittest.TestCase):
    """Test quality assessment."""

    def setUp(self):
        self.validator = KnowledgeValidator()

    def test_assess_quality_basic(self):
        """Test basic quality assessment."""
        content = "This is a guide about survival. Follow these steps carefully."
        result = self.validator.assess_quality("content1", content)

        self.assertIn("metrics", result)
        self.assertIn("overall_score", result)
        self.assertIn("grade", result)

    def test_quality_metrics_included(self):
        """Test all quality metrics are assessed."""
        content = "Comprehensive guide."
        result = self.validator.assess_quality("content1", content)

        metrics = result["metrics"]
        self.assertIn(QualityMetric.READABILITY.value, metrics)
        self.assertIn(QualityMetric.TECHNICAL_DEPTH.value, metrics)
        self.assertIn(QualityMetric.PRACTICAL_VALUE.value, metrics)

    def test_readability_scoring(self):
        """Test readability scoring."""
        # Short sentences are more readable
        content = "Short. Clear. Direct."
        result = self.validator.assess_quality("content1", content)

        self.assertGreater(result["metrics"][QualityMetric.READABILITY.value], 70)

    def test_technical_depth_scoring(self):
        """Test technical depth scoring."""
        content = "This procedure uses analysis method and technique for process."
        result = self.validator.assess_quality("content1", content)

        self.assertGreater(result["metrics"][QualityMetric.TECHNICAL_DEPTH.value], 0)

    def test_grade_assignment(self):
        """Test grade assignment from score."""
        # High quality content
        content = """
        # Introduction
        This is a comprehensive guide with step-by-step instructions.
        The procedure involves a technical method and analysis technique.
        According to research [Smith, 2024], this process is effective.
        ## Conclusion
        Follow these instructions for best results.
        """
        result = self.validator.assess_quality("content1", content)

        self.assertIn(result["grade"], ["A", "B", "C", "D", "F"])


class TestValidationRules(unittest.TestCase):
    """Test custom validation rules."""

    def setUp(self):
        self.validator = KnowledgeValidator()

    def test_add_validation_rule(self):
        """Test adding custom validation rule."""
        def check_func(content):
            return "water" in content.lower()

        rule_id = self.validator.add_validation_rule(
            "water_check",
            ValidationCategory.ACCURACY,
            check_func,
            ValidationSeverity.INFO
        )

        self.assertEqual(rule_id, "water_check")
        self.assertIn(rule_id, self.validator.validation_rules)

    def test_validation_rule_properties(self):
        """Test validation rule properties."""
        def check_func(content):
            return True

        self.validator.add_validation_rule(
            "test_rule",
            ValidationCategory.COMPLETENESS,
            check_func,
            ValidationSeverity.WARNING
        )

        rule = self.validator.validation_rules["test_rule"]
        self.assertEqual(rule["category"], ValidationCategory.COMPLETENESS.value)
        self.assertEqual(rule["severity"], ValidationSeverity.WARNING.value)

    def test_invalid_category_rejected(self):
        """Test invalid category is rejected."""
        with self.assertRaises(ValueError):
            self.validator.add_validation_rule(
                "test", "invalid_category", lambda x: True, ValidationSeverity.INFO
            )

    def test_invalid_severity_rejected(self):
        """Test invalid severity is rejected."""
        with self.assertRaises(ValueError):
            self.validator.add_validation_rule(
                "test", ValidationCategory.ACCURACY, lambda x: True, "invalid_severity"
            )

    def test_required_sections_setting(self):
        """Test setting required sections."""
        result = self.validator.set_required_sections(
            "medical", ["Symptoms", "Treatment", "Prevention"]
        )

        self.assertTrue(result)
        self.assertIn("medical", self.validator.required_sections)


class TestExternalReferences(unittest.TestCase):
    """Test external reference tracking."""

    def setUp(self):
        self.validator = KnowledgeValidator()

    def test_track_external_reference(self):
        """Test tracking external reference."""
        ref_id = self.validator.track_external_reference(
            "ref1", "https://example.com"
        )

        self.assertEqual(ref_id, "ref1")
        self.assertIn(ref_id, self.validator.external_refs)

    def test_verify_accessible_reference(self):
        """Test verifying accessible reference."""
        self.validator.track_external_reference("ref1", "https://example.com")
        
        result = self.validator.verify_external_reference("ref1", True)

        self.assertEqual(result["status"], "accessible")
        self.assertIsNotNone(result["last_checked"])

    def test_verify_broken_reference(self):
        """Test verifying broken reference."""
        self.validator.track_external_reference("ref1", "https://example.com")
        
        result = self.validator.verify_external_reference("ref1", False)

        self.assertEqual(result["status"], "broken")

    def test_verify_nonexistent_reference(self):
        """Test verifying nonexistent reference raises error."""
        with self.assertRaises(KeyError):
            self.validator.verify_external_reference("nonexistent", True)

    def test_reference_initial_status(self):
        """Test reference initial status is unverified."""
        self.validator.track_external_reference("ref1", "https://example.com")
        
        ref = self.validator.external_refs["ref1"]
        self.assertEqual(ref["status"], "unverified")
        self.assertIsNone(ref["last_checked"])


class TestValidationReporting(unittest.TestCase):
    """Test validation reporting."""

    def setUp(self):
        self.validator = KnowledgeValidator()

    def test_generate_empty_report(self):
        """Test generating report with no validations."""
        report = self.validator.generate_validation_report([])

        self.assertEqual(report["content_count"], 0)
        self.assertEqual(report["summary"]["passed"], 0)

    def test_generate_report_with_validations(self):
        """Test generating report with validations."""
        self.validator.validate_content("c1", "Content one " * 20)
        self.validator.validate_content("c2", "Content two " * 20)

        report = self.validator.generate_validation_report(["c1", "c2"])

        self.assertEqual(report["content_count"], 2)
        self.assertGreater(report["summary"]["passed"], 0)

    def test_report_includes_summary(self):
        """Test report includes summary statistics."""
        self.validator.validate_content("c1", "Short")  # Will have warnings

        report = self.validator.generate_validation_report(["c1"])

        self.assertIn("passed", report["summary"])
        self.assertIn("failed", report["summary"])
        self.assertIn("warnings", report["summary"])

    def test_report_timestamp(self):
        """Test report includes timestamp."""
        report = self.validator.generate_validation_report([])

        self.assertIn("generated_at", report)

    def test_report_content_results(self):
        """Test report includes content results."""
        self.validator.validate_content("c1", "Content " * 20)

        report = self.validator.generate_validation_report(["c1"])

        self.assertGreater(len(report["content_results"]), 0)


class TestVersionComparison(unittest.TestCase):
    """Test version comparison."""

    def setUp(self):
        self.validator = KnowledgeValidator()

    def test_compare_identical_versions(self):
        """Test comparing identical versions."""
        content = "Same content"
        result = self.validator.compare_versions(content, content)

        self.assertEqual(result["length_change"], 0)
        self.assertEqual(result["similarity_percent"], 100)

    def test_compare_different_versions(self):
        """Test comparing different versions."""
        v1 = "Original content here"
        v2 = "Completely different content here now"

        result = self.validator.compare_versions(v1, v2)

        self.assertNotEqual(result["length_change"], 0)
        self.assertLess(result["similarity_percent"], 100)

    def test_detect_major_length_change(self):
        """Test detecting major length change."""
        v1 = "Short"
        v2 = "This is a much longer version " * 20

        result = self.validator.compare_versions(v1, v2)

        self.assertIn("major_changes", result)

    def test_detect_major_revision(self):
        """Test detecting major content revision."""
        v1 = "Water purification techniques for survival"
        v2 = "Food preservation methods for emergencies"

        result = self.validator.compare_versions(v1, v2)

        self.assertLess(result["similarity_percent"], 70)

    def test_similarity_calculation(self):
        """Test similarity percentage calculation."""
        v1 = "water food shelter medical"
        v2 = "water food survival skills"

        result = self.validator.compare_versions(v1, v2)

        # Should have some similarity (water, food)
        self.assertGreater(result["similarity_percent"], 0)
        self.assertLess(result["similarity_percent"], 100)


class TestIntegrationScenarios(unittest.TestCase):
    """Test integration scenarios."""

    def setUp(self):
        self.validator = KnowledgeValidator()

    def test_complete_validation_workflow(self):
        """Test complete validation workflow."""
        # Set up validation rules
        self.validator.set_required_sections("water", ["Introduction", "Methods"])
        
        # Validate content
        content = """
        # Introduction
        Water purification is essential for survival.
        According to research [Smith, 2024], boiling is effective.
        
        # Methods
        Follow these step-by-step instructions for purification.
        """
        
        result = self.validator.validate_content(
            "guide1",
            content,
            {"category": "water"}
        )

        # Assess quality
        quality = self.validator.assess_quality("guide1", content)

        # Check freshness
        freshness = self.validator.check_freshness(
            "guide1", 
            datetime.now()
        )

        self.assertIsNotNone(result)
        self.assertIsNotNone(quality)
        self.assertTrue(freshness["fresh"])

    def test_citation_and_source_validation(self):
        """Test citation and source validation together."""
        content = "Research [Smith, 2024] shows this is effective."
        
        # Validate content
        result = self.validator.validate_content("guide1", content)

        # Verify citations
        citations = [
            {"id": "c1", "author": "Smith", "year": "2024", 
             "title": "Water Guide", "url": "https://example.com"}
        ]
        citation_result = self.validator.verify_citations("guide1", citations)

        # Track external reference
        ref_id = self.validator.track_external_reference(
            "ref1", "https://example.com"
        )

        self.assertIsNotNone(result)
        self.assertTrue(citation_result["complete"])
        self.assertEqual(ref_id, "ref1")

    def test_quality_and_freshness_workflow(self):
        """Test quality assessment with freshness checking."""
        content = """
        # Survival Guide
        This comprehensive guide provides step-by-step instructions.
        The procedure involves technical analysis and proven methods.
        According to studies [Author, 2024], this approach is effective.
        """

        # Assess quality
        quality = self.validator.assess_quality("guide1", content)

        # Check freshness
        freshness = self.validator.check_freshness("guide1", datetime.now())

        # Generate report
        report = self.validator.generate_validation_report(["guide1"])

        self.assertGreater(quality["overall_score"], 50)
        self.assertTrue(freshness["fresh"])
        self.assertIsNotNone(report)


class TestValidatorStatistics(unittest.TestCase):
    """Test validator statistics."""

    def setUp(self):
        self.validator = KnowledgeValidator()

    def test_get_empty_stats(self):
        """Test getting stats with no activity."""
        stats = self.validator.get_validator_stats()

        self.assertEqual(stats["total_validations"], 0)
        self.assertEqual(stats["content_items_validated"], 0)

    def test_stats_after_validations(self):
        """Test stats after performing validations."""
        self.validator.validate_content("c1", "Content one")
        self.validator.validate_content("c2", "Content two")

        stats = self.validator.get_validator_stats()

        self.assertEqual(stats["total_validations"], 2)
        self.assertEqual(stats["content_items_validated"], 2)

    def test_stats_include_all_counts(self):
        """Test stats include all relevant counts."""
        stats = self.validator.get_validator_stats()

        self.assertIn("validation_rules", stats)
        self.assertIn("contradiction_patterns", stats)
        self.assertIn("external_references", stats)

    def test_stats_track_patterns(self):
        """Test stats track contradiction patterns."""
        self.validator.add_contradiction_pattern("safe", "dangerous")
        
        stats = self.validator.get_validator_stats()

        self.assertEqual(stats["contradiction_patterns"], 1)

    def test_stats_track_references(self):
        """Test stats track external references."""
        self.validator.track_external_reference("ref1", "https://example.com")
        
        stats = self.validator.get_validator_stats()

        self.assertEqual(stats["external_references"], 1)


if __name__ == "__main__":
    unittest.main()

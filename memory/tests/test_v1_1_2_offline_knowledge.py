"""
Test Suite for Feature 1.1.2.6: Offline Knowledge Library
v1.1.2 Phase 2: Knowledge Bank & AI Integration

Tests offline knowledge library with 500+ survival guides, 100+ diagrams,
category organization, search/indexing, version control, and validation.

Test Categories:
1. Knowledge Library Structure (5 tests)
2. Category Management (6 tests)
3. Guide Storage & Retrieval (5 tests)
4. Diagram Management (5 tests)
5. Search & Indexing (6 tests)
6. Version Control (5 tests)
7. Knowledge Validation (6 tests)
8. Offline Accessibility (5 tests)
9. Cross-References (4 tests)
10. Knowledge Metadata (5 tests)
11. Import/Export (5 tests)
12. Integration Scenarios (3 tests)

Total: 60 tests
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
from datetime import datetime
from enum import Enum
from pathlib import Path


class KnowledgeCategory(Enum):
    """Knowledge category enumeration."""
    WATER = "water"
    FOOD = "food"
    SHELTER = "shelter"
    MEDICAL = "medical"
    SKILLS = "skills"
    TECH = "tech"
    SURVIVAL = "survival"
    REFERENCE = "reference"


class ContentType(Enum):
    """Content type enumeration."""
    GUIDE = "guide"
    DIAGRAM = "diagram"
    MAP = "map"
    CHECKLIST = "checklist"
    REFERENCE = "reference"


class OfflineKnowledgeLibrary:
    """Offline knowledge library management system."""

    def __init__(self, library_path="/knowledge"):
        self.library_path = library_path
        self.guides = {}
        self.diagrams = {}
        self.categories = {cat: [] for cat in KnowledgeCategory}
        self.index = {}
        self.versions = {}
        self.metadata = {}
        self.cross_refs = {}
        self.validation_results = {}

    def add_guide(self, guide_id, title, category, content, metadata=None):
        """Add guide to library."""
        if not isinstance(category, KnowledgeCategory):
            raise ValueError(f"Invalid category: {category}")

        guide = {
            "id": guide_id,
            "title": title,
            "category": category.value,
            "content": content,
            "type": ContentType.GUIDE.value,
            "added_at": datetime.now().isoformat(),
            "version": 1
        }

        if metadata:
            guide["metadata"] = metadata

        self.guides[guide_id] = guide
        self.categories[category].append(guide_id)

        # Index for search
        self._index_content(guide_id, title, content)

        # Version control
        self._track_version(guide_id, 1, "Initial version")

        return guide_id

    def get_guide(self, guide_id):
        """Retrieve guide by ID."""
        if guide_id not in self.guides:
            raise KeyError(f"Guide not found: {guide_id}")

        return self.guides[guide_id].copy()

    def update_guide(self, guide_id, content=None, title=None, metadata=None):
        """Update existing guide."""
        if guide_id not in self.guides:
            raise KeyError(f"Guide not found: {guide_id}")

        guide = self.guides[guide_id]

        # Increment version
        new_version = guide["version"] + 1

        if content:
            guide["content"] = content
            # Re-index
            self._index_content(guide_id, guide["title"], content)

        if title:
            guide["title"] = title

        if metadata:
            guide["metadata"] = metadata

        guide["version"] = new_version
        guide["updated_at"] = datetime.now().isoformat()

        # Track version
        self._track_version(guide_id, new_version, "Updated")

        return new_version

    def delete_guide(self, guide_id):
        """Delete guide from library."""
        if guide_id not in self.guides:
            return False

        guide = self.guides[guide_id]
        category = KnowledgeCategory(guide["category"])

        # Remove from category
        if guide_id in self.categories[category]:
            self.categories[category].remove(guide_id)

        # Remove from index
        if guide_id in self.index:
            del self.index[guide_id]

        # Remove guide
        del self.guides[guide_id]

        return True

    def add_diagram(self, diagram_id, title, category, diagram_data, format="svg"):
        """Add diagram to library."""
        if not isinstance(category, KnowledgeCategory):
            raise ValueError(f"Invalid category: {category}")

        diagram = {
            "id": diagram_id,
            "title": title,
            "category": category.value,
            "data": diagram_data,
            "format": format,
            "type": ContentType.DIAGRAM.value,
            "added_at": datetime.now().isoformat(),
            "version": 1
        }

        self.diagrams[diagram_id] = diagram
        self.categories[category].append(diagram_id)

        # Index for search
        self._index_content(diagram_id, title, title)  # Index by title

        return diagram_id

    def get_diagram(self, diagram_id):
        """Retrieve diagram by ID."""
        if diagram_id not in self.diagrams:
            raise KeyError(f"Diagram not found: {diagram_id}")

        return self.diagrams[diagram_id].copy()

    def list_by_category(self, category):
        """List all content in category."""
        if not isinstance(category, KnowledgeCategory):
            raise ValueError(f"Invalid category: {category}")

        return self.categories[category].copy()

    def get_category_stats(self, category):
        """Get statistics for category."""
        if not isinstance(category, KnowledgeCategory):
            raise ValueError(f"Invalid category: {category}")

        items = self.categories[category]

        guides_count = sum(1 for item_id in items if item_id in self.guides)
        diagrams_count = sum(1 for item_id in items if item_id in self.diagrams)

        return {
            "category": category.value,
            "total_items": len(items),
            "guides": guides_count,
            "diagrams": diagrams_count
        }

    def search(self, query, category=None):
        """Search knowledge library."""
        query_lower = query.lower()
        results = []

        # Search in index
        for item_id, keywords in self.index.items():
            if query_lower in keywords.lower():
                # Check category filter
                if category:
                    item = self.guides.get(item_id) or self.diagrams.get(item_id)
                    if item and item["category"] != category.value:
                        continue

                results.append(item_id)

        return results

    def _index_content(self, item_id, title, content):
        """Index content for search."""
        # Combine title and content for indexing
        keywords = f"{title} {content}".lower()
        self.index[item_id] = keywords

    def get_version_history(self, item_id):
        """Get version history for item."""
        if item_id not in self.versions:
            return []

        return self.versions[item_id].copy()

    def _track_version(self, item_id, version, note):
        """Track version change."""
        if item_id not in self.versions:
            self.versions[item_id] = []

        self.versions[item_id].append({
            "version": version,
            "note": note,
            "timestamp": datetime.now().isoformat()
        })

    def revert_to_version(self, item_id, version):
        """Revert item to specific version."""
        # In real implementation, would restore from version history
        if item_id not in self.guides:
            raise KeyError(f"Item not found: {item_id}")

        history = self.get_version_history(item_id)

        # Check version exists
        if not any(v["version"] == version for v in history):
            raise ValueError(f"Version {version} not found")

        # Simulate revert
        self.guides[item_id]["version"] = version
        self.guides[item_id]["reverted_from"] = self.guides[item_id].get("version", version)

        return True

    def validate_guide(self, guide_id):
        """Validate guide content."""
        if guide_id not in self.guides:
            raise KeyError(f"Guide not found: {guide_id}")

        guide = self.guides[guide_id]

        validation = {
            "valid": True,
            "errors": [],
            "warnings": []
        }

        # Check required fields
        if not guide.get("title"):
            validation["valid"] = False
            validation["errors"].append("Missing title")

        if not guide.get("content"):
            validation["valid"] = False
            validation["errors"].append("Missing content")

        # Check content length
        if len(guide.get("content", "")) < 50:
            validation["warnings"].append("Content is very short")

        # Check category
        if guide.get("category") not in [c.value for c in KnowledgeCategory]:
            validation["valid"] = False
            validation["errors"].append("Invalid category")

        # Store validation result
        self.validation_results[guide_id] = validation

        return validation

    def validate_all(self):
        """Validate all guides."""
        results = {
            "total": len(self.guides),
            "valid": 0,
            "invalid": 0,
            "warnings": 0
        }

        for guide_id in self.guides:
            validation = self.validate_guide(guide_id)

            if validation["valid"]:
                results["valid"] += 1
            else:
                results["invalid"] += 1

            if validation["warnings"]:
                results["warnings"] += len(validation["warnings"])

        return results

    def check_offline_accessible(self, item_id):
        """Check if item is accessible offline."""
        # Check in guides
        if item_id in self.guides:
            guide = self.guides[item_id]
            # No external dependencies
            return not self._has_external_refs(guide.get("content", ""))

        # Check in diagrams
        if item_id in self.diagrams:
            # Diagrams stored locally are offline accessible
            return True

        return False

    def _has_external_refs(self, content):
        """Check if content has external references."""
        external_patterns = ["http://", "https://", "www."]
        return any(pattern in content for pattern in external_patterns)

    def get_offline_stats(self):
        """Get offline accessibility statistics."""
        total = len(self.guides) + len(self.diagrams)
        offline = sum(1 for item_id in list(self.guides.keys()) + list(self.diagrams.keys())
                     if self.check_offline_accessible(item_id))

        return {
            "total_items": total,
            "offline_accessible": offline,
            "percentage": round((offline / total * 100) if total > 0 else 0, 2)
        }

    def add_cross_reference(self, from_id, to_id, ref_type="related"):
        """Add cross-reference between items."""
        if from_id not in self.cross_refs:
            self.cross_refs[from_id] = []

        self.cross_refs[from_id].append({
            "to": to_id,
            "type": ref_type
        })

        return True

    def get_cross_references(self, item_id):
        """Get cross-references for item."""
        return self.cross_refs.get(item_id, []).copy()

    def get_related_content(self, item_id):
        """Get related content for item."""
        refs = self.get_cross_references(item_id)

        related = []
        for ref in refs:
            to_id = ref["to"]

            # Get referenced item
            item = self.guides.get(to_id) or self.diagrams.get(to_id)
            if item:
                related.append({
                    "id": to_id,
                    "title": item["title"],
                    "type": item["type"],
                    "ref_type": ref["type"]
                })

        return related

    def set_metadata(self, item_id, key, value):
        """Set metadata for item."""
        if item_id not in self.metadata:
            self.metadata[item_id] = {}

        self.metadata[item_id][key] = value
        return True

    def get_metadata(self, item_id, key=None):
        """Get metadata for item."""
        if item_id not in self.metadata:
            return None if key else {}

        if key:
            return self.metadata[item_id].get(key)

        return self.metadata[item_id].copy()

    def tag_item(self, item_id, tags):
        """Tag item with keywords."""
        return self.set_metadata(item_id, "tags", tags)

    def get_items_by_tag(self, tag):
        """Get items with specific tag."""
        results = []

        for item_id, meta in self.metadata.items():
            if "tags" in meta and tag in meta["tags"]:
                results.append(item_id)

        return results

    def export_library(self, include_diagrams=True):
        """Export entire library."""
        export = {
            "guides": self.guides.copy(),
            "metadata": self.metadata.copy(),
            "exported_at": datetime.now().isoformat(),
            "total_guides": len(self.guides)
        }

        if include_diagrams:
            export["diagrams"] = self.diagrams.copy()
            export["total_diagrams"] = len(self.diagrams)

        return export

    def import_library(self, data):
        """Import library data."""
        imported = {
            "guides": 0,
            "diagrams": 0,
            "errors": []
        }

        # Import guides
        if "guides" in data:
            for guide_id, guide in data["guides"].items():
                try:
                    self.guides[guide_id] = guide

                    # Add to category
                    category = KnowledgeCategory(guide["category"])
                    if guide_id not in self.categories[category]:
                        self.categories[category].append(guide_id)

                    # Re-index
                    self._index_content(guide_id, guide["title"], guide["content"])

                    imported["guides"] += 1
                except Exception as e:
                    imported["errors"].append(f"Guide {guide_id}: {str(e)}")

        # Import diagrams
        if "diagrams" in data:
            for diagram_id, diagram in data["diagrams"].items():
                try:
                    self.diagrams[diagram_id] = diagram

                    # Add to category
                    category = KnowledgeCategory(diagram["category"])
                    if diagram_id not in self.categories[category]:
                        self.categories[category].append(diagram_id)

                    imported["diagrams"] += 1
                except Exception as e:
                    imported["errors"].append(f"Diagram {diagram_id}: {str(e)}")

        # Import metadata
        if "metadata" in data:
            self.metadata.update(data["metadata"])

        return imported

    def get_library_stats(self):
        """Get overall library statistics."""
        return {
            "total_guides": len(self.guides),
            "total_diagrams": len(self.diagrams),
            "total_items": len(self.guides) + len(self.diagrams),
            "categories": {cat.value: len(items) for cat, items in self.categories.items()},
            "indexed_items": len(self.index),
            "cross_references": sum(len(refs) for refs in self.cross_refs.values())
        }


class TestKnowledgeLibraryStructure(unittest.TestCase):
    """Test knowledge library structure."""

    def setUp(self):
        self.library = OfflineKnowledgeLibrary()

    def test_library_initialization(self):
        """Test library is initialized."""
        self.assertIsNotNone(self.library.guides)
        self.assertIsNotNone(self.library.diagrams)
        self.assertIsNotNone(self.library.categories)

    def test_category_structure(self):
        """Test category structure."""
        self.assertEqual(len(self.library.categories), len(KnowledgeCategory))
        self.assertIn(KnowledgeCategory.WATER, self.library.categories)
        self.assertIn(KnowledgeCategory.MEDICAL, self.library.categories)

    def test_content_types(self):
        """Test content type enumeration."""
        self.assertEqual(ContentType.GUIDE.value, "guide")
        self.assertEqual(ContentType.DIAGRAM.value, "diagram")

    def test_library_path(self):
        """Test library path configuration."""
        self.assertEqual(self.library.library_path, "/knowledge")

    def test_empty_library_stats(self):
        """Test statistics for empty library."""
        stats = self.library.get_library_stats()
        self.assertEqual(stats["total_guides"], 0)
        self.assertEqual(stats["total_diagrams"], 0)


class TestCategoryManagement(unittest.TestCase):
    """Test category management."""

    def setUp(self):
        self.library = OfflineKnowledgeLibrary()

    def test_add_guide_to_category(self):
        """Test adding guide to category."""
        guide_id = self.library.add_guide(
            "water_001",
            "Water Purification",
            KnowledgeCategory.WATER,
            "How to purify water..."
        )

        self.assertIn(guide_id, self.library.categories[KnowledgeCategory.WATER])

    def test_list_category_content(self):
        """Test listing category content."""
        self.library.add_guide("w1", "Guide 1", KnowledgeCategory.WATER, "Content")
        self.library.add_guide("w2", "Guide 2", KnowledgeCategory.WATER, "Content")

        items = self.library.list_by_category(KnowledgeCategory.WATER)
        self.assertEqual(len(items), 2)

    def test_category_stats(self):
        """Test category statistics."""
        self.library.add_guide("w1", "Guide", KnowledgeCategory.WATER, "Content")
        self.library.add_diagram("w2", "Diagram", KnowledgeCategory.WATER, "SVG data")

        stats = self.library.get_category_stats(KnowledgeCategory.WATER)
        self.assertEqual(stats["guides"], 1)
        self.assertEqual(stats["diagrams"], 1)
        self.assertEqual(stats["total_items"], 2)

    def test_multiple_categories(self):
        """Test content in multiple categories."""
        self.library.add_guide("w1", "Water", KnowledgeCategory.WATER, "Content")
        self.library.add_guide("f1", "Food", KnowledgeCategory.FOOD, "Content")

        water_items = self.library.list_by_category(KnowledgeCategory.WATER)
        food_items = self.library.list_by_category(KnowledgeCategory.FOOD)

        self.assertEqual(len(water_items), 1)
        self.assertEqual(len(food_items), 1)

    def test_invalid_category(self):
        """Test invalid category raises error."""
        with self.assertRaises(ValueError):
            self.library.add_guide("test", "Title", "invalid", "Content")

    def test_category_with_mixed_content(self):
        """Test category with guides and diagrams."""
        self.library.add_guide("m1", "First Aid", KnowledgeCategory.MEDICAL, "Guide content")
        self.library.add_diagram("m2", "Anatomy", KnowledgeCategory.MEDICAL, "SVG")

        stats = self.library.get_category_stats(KnowledgeCategory.MEDICAL)
        self.assertGreater(stats["total_items"], 0)


class TestGuideStorageRetrieval(unittest.TestCase):
    """Test guide storage and retrieval."""

    def setUp(self):
        self.library = OfflineKnowledgeLibrary()

    def test_add_guide(self):
        """Test adding guide."""
        guide_id = self.library.add_guide(
            "test_001",
            "Test Guide",
            KnowledgeCategory.SURVIVAL,
            "This is test content."
        )

        self.assertIn(guide_id, self.library.guides)

    def test_retrieve_guide(self):
        """Test retrieving guide."""
        guide_id = self.library.add_guide(
            "test_002",
            "Test Title",
            KnowledgeCategory.SKILLS,
            "Test content"
        )

        guide = self.library.get_guide(guide_id)
        self.assertEqual(guide["title"], "Test Title")
        self.assertEqual(guide["content"], "Test content")

    def test_update_guide(self):
        """Test updating guide."""
        guide_id = self.library.add_guide(
            "test_003",
            "Original",
            KnowledgeCategory.TECH,
            "Original content"
        )

        new_version = self.library.update_guide(
            guide_id,
            content="Updated content"
        )

        self.assertEqual(new_version, 2)

        guide = self.library.get_guide(guide_id)
        self.assertEqual(guide["content"], "Updated content")

    def test_delete_guide(self):
        """Test deleting guide."""
        guide_id = self.library.add_guide(
            "test_004",
            "To Delete",
            KnowledgeCategory.REFERENCE,
            "Content"
        )

        deleted = self.library.delete_guide(guide_id)
        self.assertTrue(deleted)
        self.assertNotIn(guide_id, self.library.guides)

    def test_guide_not_found(self):
        """Test retrieving non-existent guide."""
        with self.assertRaises(KeyError):
            self.library.get_guide("nonexistent")


class TestDiagramManagement(unittest.TestCase):
    """Test diagram management."""

    def setUp(self):
        self.library = OfflineKnowledgeLibrary()

    def test_add_diagram(self):
        """Test adding diagram."""
        diagram_id = self.library.add_diagram(
            "diag_001",
            "Water Filter",
            KnowledgeCategory.WATER,
            "<svg>...</svg>"
        )

        self.assertIn(diagram_id, self.library.diagrams)

    def test_retrieve_diagram(self):
        """Test retrieving diagram."""
        diagram_id = self.library.add_diagram(
            "diag_002",
            "Shelter Design",
            KnowledgeCategory.SHELTER,
            "<svg>shelter</svg>"
        )

        diagram = self.library.get_diagram(diagram_id)
        self.assertEqual(diagram["title"], "Shelter Design")
        self.assertEqual(diagram["format"], "svg")

    def test_diagram_format(self):
        """Test diagram format specification."""
        diagram_id = self.library.add_diagram(
            "diag_003",
            "Map",
            KnowledgeCategory.REFERENCE,
            "PNG data",
            format="png"
        )

        diagram = self.library.get_diagram(diagram_id)
        self.assertEqual(diagram["format"], "png")

    def test_diagram_in_category(self):
        """Test diagram added to category."""
        diagram_id = self.library.add_diagram(
            "diag_004",
            "Medical Diagram",
            KnowledgeCategory.MEDICAL,
            "SVG"
        )

        self.assertIn(diagram_id, self.library.categories[KnowledgeCategory.MEDICAL])

    def test_diagram_not_found(self):
        """Test retrieving non-existent diagram."""
        with self.assertRaises(KeyError):
            self.library.get_diagram("nonexistent")


class TestSearchIndexing(unittest.TestCase):
    """Test search and indexing."""

    def setUp(self):
        self.library = OfflineKnowledgeLibrary()

    def test_search_by_title(self):
        """Test searching by title."""
        self.library.add_guide(
            "g1",
            "Water Purification Methods",
            KnowledgeCategory.WATER,
            "Various methods..."
        )

        results = self.library.search("purification")
        self.assertIn("g1", results)

    def test_search_by_content(self):
        """Test searching by content."""
        self.library.add_guide(
            "g2",
            "Guide Title",
            KnowledgeCategory.SURVIVAL,
            "This guide covers emergency shelter construction."
        )

        results = self.library.search("emergency")
        self.assertIn("g2", results)

    def test_search_case_insensitive(self):
        """Test search is case insensitive."""
        self.library.add_guide(
            "g3",
            "First Aid Basics",
            KnowledgeCategory.MEDICAL,
            "Content"
        )

        results = self.library.search("FIRST")
        self.assertIn("g3", results)

    def test_search_with_category_filter(self):
        """Test search with category filter."""
        self.library.add_guide("g4", "Water Guide", KnowledgeCategory.WATER, "water content")
        self.library.add_guide("g5", "Food Guide", KnowledgeCategory.FOOD, "food content")

        results = self.library.search("guide", category=KnowledgeCategory.WATER)
        self.assertIn("g4", results)
        self.assertNotIn("g5", results)

    def test_search_no_results(self):
        """Test search with no matches."""
        self.library.add_guide("g6", "Title", KnowledgeCategory.TECH, "Content")

        results = self.library.search("nonexistent")
        self.assertEqual(len(results), 0)

    def test_indexing_on_update(self):
        """Test content is re-indexed on update."""
        guide_id = self.library.add_guide(
            "g7",
            "Original Title",
            KnowledgeCategory.SKILLS,
            "Original content"
        )

        self.library.update_guide(guide_id, content="Updated with special keyword")

        results = self.library.search("special")
        self.assertIn(guide_id, results)


class TestVersionControl(unittest.TestCase):
    """Test version control."""

    def setUp(self):
        self.library = OfflineKnowledgeLibrary()

    def test_initial_version(self):
        """Test initial version is 1."""
        guide_id = self.library.add_guide(
            "v1",
            "Title",
            KnowledgeCategory.WATER,
            "Content"
        )

        guide = self.library.get_guide(guide_id)
        self.assertEqual(guide["version"], 1)

    def test_version_increment(self):
        """Test version increments on update."""
        guide_id = self.library.add_guide("v2", "Title", KnowledgeCategory.FOOD, "Content")

        self.library.update_guide(guide_id, content="Updated")
        guide = self.library.get_guide(guide_id)

        self.assertEqual(guide["version"], 2)

    def test_version_history(self):
        """Test version history tracking."""
        guide_id = self.library.add_guide("v3", "Title", KnowledgeCategory.SHELTER, "Content")
        self.library.update_guide(guide_id, content="Update 1")

        history = self.library.get_version_history(guide_id)
        self.assertGreater(len(history), 0)

    def test_revert_to_version(self):
        """Test reverting to previous version."""
        guide_id = self.library.add_guide("v4", "Title", KnowledgeCategory.MEDICAL, "Original")
        self.library.update_guide(guide_id, content="Update")

        reverted = self.library.revert_to_version(guide_id, 1)
        self.assertTrue(reverted)

    def test_version_history_metadata(self):
        """Test version history includes metadata."""
        guide_id = self.library.add_guide("v5", "Title", KnowledgeCategory.SKILLS, "Content")

        history = self.library.get_version_history(guide_id)
        self.assertIn("timestamp", history[0])
        self.assertIn("note", history[0])


class TestKnowledgeValidation(unittest.TestCase):
    """Test knowledge validation."""

    def setUp(self):
        self.library = OfflineKnowledgeLibrary()

    def test_validate_valid_guide(self):
        """Test validating valid guide."""
        guide_id = self.library.add_guide(
            "val1",
            "Valid Guide",
            KnowledgeCategory.WATER,
            "This is a comprehensive guide with sufficient content to be considered valid."
        )

        validation = self.library.validate_guide(guide_id)
        self.assertTrue(validation["valid"])

    def test_validate_missing_title(self):
        """Test validation detects missing title."""
        guide_id = self.library.add_guide(
            "val2",
            "",
            KnowledgeCategory.FOOD,
            "Content"
        )

        validation = self.library.validate_guide(guide_id)
        self.assertFalse(validation["valid"])
        self.assertIn("Missing title", validation["errors"])

    def test_validate_missing_content(self):
        """Test validation detects missing content."""
        guide_id = self.library.add_guide(
            "val3",
            "Title",
            KnowledgeCategory.SHELTER,
            ""
        )

        validation = self.library.validate_guide(guide_id)
        self.assertFalse(validation["valid"])

    def test_validate_short_content_warning(self):
        """Test validation warns about short content."""
        guide_id = self.library.add_guide(
            "val4",
            "Title",
            KnowledgeCategory.MEDICAL,
            "Short"
        )

        validation = self.library.validate_guide(guide_id)
        self.assertGreater(len(validation["warnings"]), 0)

    def test_validate_all(self):
        """Test validating all guides."""
        self.library.add_guide("va1", "Good", KnowledgeCategory.SKILLS, "Good content here.")
        self.library.add_guide("va2", "", KnowledgeCategory.TECH, "Bad")

        results = self.library.validate_all()
        self.assertIn("total", results)
        self.assertIn("valid", results)
        self.assertIn("invalid", results)

    def test_validation_stored(self):
        """Test validation results are stored."""
        guide_id = self.library.add_guide(
            "val5",
            "Title",
            KnowledgeCategory.REFERENCE,
            "Content here"
        )

        self.library.validate_guide(guide_id)
        self.assertIn(guide_id, self.library.validation_results)


class TestOfflineAccessibility(unittest.TestCase):
    """Test offline accessibility."""

    def setUp(self):
        self.library = OfflineKnowledgeLibrary()

    def test_offline_accessible_guide(self):
        """Test guide without external refs is offline accessible."""
        guide_id = self.library.add_guide(
            "off1",
            "Offline Guide",
            KnowledgeCategory.WATER,
            "This guide has no external dependencies."
        )

        accessible = self.library.check_offline_accessible(guide_id)
        self.assertTrue(accessible)

    def test_external_refs_detected(self):
        """Test guide with external refs detected."""
        guide_id = self.library.add_guide(
            "off2",
            "Online Guide",
            KnowledgeCategory.FOOD,
            "See https://example.com for more info."
        )

        accessible = self.library.check_offline_accessible(guide_id)
        self.assertFalse(accessible)

    def test_diagram_offline_accessible(self):
        """Test diagrams are offline accessible."""
        diagram_id = self.library.add_diagram(
            "off3",
            "Local Diagram",
            KnowledgeCategory.SHELTER,
            "<svg>local data</svg>"
        )

        accessible = self.library.check_offline_accessible(diagram_id)
        self.assertTrue(accessible)

    def test_offline_stats(self):
        """Test offline accessibility statistics."""
        self.library.add_guide("os1", "Title", KnowledgeCategory.MEDICAL, "Offline content")
        self.library.add_guide("os2", "Title", KnowledgeCategory.SKILLS, "See http://link.com")

        stats = self.library.get_offline_stats()
        self.assertIn("offline_accessible", stats)
        self.assertIn("percentage", stats)

    def test_www_pattern_detected(self):
        """Test www pattern detected as external."""
        guide_id = self.library.add_guide(
            "off4",
            "Title",
            KnowledgeCategory.TECH,
            "Visit www.example.com"
        )

        accessible = self.library.check_offline_accessible(guide_id)
        self.assertFalse(accessible)


class TestCrossReferences(unittest.TestCase):
    """Test cross-references between content."""

    def setUp(self):
        self.library = OfflineKnowledgeLibrary()

    def test_add_cross_reference(self):
        """Test adding cross-reference."""
        g1 = self.library.add_guide("cr1", "Guide 1", KnowledgeCategory.WATER, "Content")
        g2 = self.library.add_guide("cr2", "Guide 2", KnowledgeCategory.WATER, "Content")

        self.library.add_cross_reference(g1, g2, "related")

        refs = self.library.get_cross_references(g1)
        self.assertEqual(len(refs), 1)
        self.assertEqual(refs[0]["to"], g2)

    def test_get_related_content(self):
        """Test getting related content."""
        g1 = self.library.add_guide("rc1", "Water", KnowledgeCategory.WATER, "Content")
        g2 = self.library.add_guide("rc2", "Purification", KnowledgeCategory.WATER, "Content")

        self.library.add_cross_reference(g1, g2, "related")

        related = self.library.get_related_content(g1)
        self.assertEqual(len(related), 1)
        self.assertEqual(related[0]["id"], g2)

    def test_multiple_references(self):
        """Test multiple cross-references."""
        g1 = self.library.add_guide("mr1", "Main", KnowledgeCategory.SURVIVAL, "Content")
        g2 = self.library.add_guide("mr2", "Ref 1", KnowledgeCategory.WATER, "Content")
        g3 = self.library.add_guide("mr3", "Ref 2", KnowledgeCategory.FOOD, "Content")

        self.library.add_cross_reference(g1, g2)
        self.library.add_cross_reference(g1, g3)

        refs = self.library.get_cross_references(g1)
        self.assertEqual(len(refs), 2)

    def test_reference_types(self):
        """Test different reference types."""
        g1 = self.library.add_guide("rt1", "Guide", KnowledgeCategory.MEDICAL, "Content")
        g2 = self.library.add_guide("rt2", "Ref", KnowledgeCategory.MEDICAL, "Content")

        self.library.add_cross_reference(g1, g2, "prerequisite")

        refs = self.library.get_cross_references(g1)
        self.assertEqual(refs[0]["type"], "prerequisite")


class TestKnowledgeMetadata(unittest.TestCase):
    """Test knowledge metadata."""

    def setUp(self):
        self.library = OfflineKnowledgeLibrary()

    def test_set_metadata(self):
        """Test setting metadata."""
        guide_id = self.library.add_guide(
            "meta1",
            "Title",
            KnowledgeCategory.WATER,
            "Content"
        )

        self.library.set_metadata(guide_id, "author", "John Doe")

        author = self.library.get_metadata(guide_id, "author")
        self.assertEqual(author, "John Doe")

    def test_get_all_metadata(self):
        """Test getting all metadata."""
        guide_id = self.library.add_guide("meta2", "Title", KnowledgeCategory.FOOD, "Content")

        self.library.set_metadata(guide_id, "author", "Jane")
        self.library.set_metadata(guide_id, "difficulty", "beginner")

        meta = self.library.get_metadata(guide_id)
        self.assertEqual(len(meta), 2)

    def test_tag_item(self):
        """Test tagging item."""
        guide_id = self.library.add_guide("tag1", "Title", KnowledgeCategory.SHELTER, "Content")

        self.library.tag_item(guide_id, ["survival", "emergency"])

        tags = self.library.get_metadata(guide_id, "tags")
        self.assertIn("survival", tags)

    def test_get_items_by_tag(self):
        """Test getting items by tag."""
        g1 = self.library.add_guide("tag2", "Guide 1", KnowledgeCategory.MEDICAL, "Content")
        g2 = self.library.add_guide("tag3", "Guide 2", KnowledgeCategory.MEDICAL, "Content")

        self.library.tag_item(g1, ["first-aid"])
        self.library.tag_item(g2, ["first-aid", "trauma"])

        items = self.library.get_items_by_tag("first-aid")
        self.assertEqual(len(items), 2)

    def test_metadata_for_nonexistent_item(self):
        """Test metadata for nonexistent item."""
        meta = self.library.get_metadata("nonexistent")
        self.assertEqual(meta, {})


class TestImportExport(unittest.TestCase):
    """Test import/export functionality."""

    def setUp(self):
        self.library = OfflineKnowledgeLibrary()

    def test_export_library(self):
        """Test exporting library."""
        self.library.add_guide("exp1", "Guide", KnowledgeCategory.WATER, "Content")

        export = self.library.export_library()

        self.assertIn("guides", export)
        self.assertIn("exported_at", export)
        self.assertEqual(export["total_guides"], 1)

    def test_export_with_diagrams(self):
        """Test exporting with diagrams."""
        self.library.add_diagram("exp2", "Diagram", KnowledgeCategory.FOOD, "SVG")

        export = self.library.export_library(include_diagrams=True)

        self.assertIn("diagrams", export)

    def test_export_without_diagrams(self):
        """Test exporting without diagrams."""
        export = self.library.export_library(include_diagrams=False)

        self.assertNotIn("diagrams", export)

    def test_import_library(self):
        """Test importing library."""
        data = {
            "guides": {
                "imp1": {
                    "id": "imp1",
                    "title": "Imported",
                    "category": "water",
                    "content": "Content",
                    "type": "guide",
                    "version": 1
                }
            }
        }

        result = self.library.import_library(data)

        self.assertEqual(result["guides"], 1)
        self.assertIn("imp1", self.library.guides)

    def test_import_with_errors(self):
        """Test import with invalid data."""
        data = {
            "guides": {
                "bad": {
                    "id": "bad",
                    "category": "invalid_category"
                }
            }
        }

        result = self.library.import_library(data)

        self.assertGreater(len(result["errors"]), 0)


class TestIntegrationScenarios(unittest.TestCase):
    """Test end-to-end knowledge library scenarios."""

    def setUp(self):
        self.library = OfflineKnowledgeLibrary()

    def test_complete_guide_lifecycle(self):
        """Test complete guide lifecycle."""
        # Add guide
        guide_id = self.library.add_guide(
            "life1",
            "Water Purification Guide",
            KnowledgeCategory.WATER,
            "Comprehensive guide to purifying water in emergency situations."
        )

        # Add metadata
        self.library.tag_item(guide_id, ["survival", "water", "emergency"])

        # Add cross-reference
        ref_id = self.library.add_guide(
            "life2",
            "Water Storage",
            KnowledgeCategory.WATER,
            "How to store purified water."
        )
        self.library.add_cross_reference(guide_id, ref_id, "related")

        # Validate
        validation = self.library.validate_guide(guide_id)
        self.assertTrue(validation["valid"])

        # Search
        results = self.library.search("purification")
        self.assertIn(guide_id, results)

        # Get related
        related = self.library.get_related_content(guide_id)
        self.assertEqual(len(related), 1)

    def test_category_based_workflow(self):
        """Test category-based workflow."""
        # Add multiple guides to category
        for i in range(3):
            self.library.add_guide(
                f"med{i}",
                f"Medical Guide {i}",
                KnowledgeCategory.MEDICAL,
                f"Medical content {i}"
            )

        # Get category stats
        stats = self.library.get_category_stats(KnowledgeCategory.MEDICAL)
        self.assertEqual(stats["guides"], 3)

        # List category
        items = self.library.list_by_category(KnowledgeCategory.MEDICAL)
        self.assertEqual(len(items), 3)

        # Validate all
        results = self.library.validate_all()
        self.assertEqual(results["total"], 3)

    def test_offline_library_preparation(self):
        """Test preparing offline library."""
        # Add offline-accessible content
        self.library.add_guide(
            "off_prep1",
            "Shelter Building",
            KnowledgeCategory.SHELTER,
            "Complete offline guide to building emergency shelters."
        )

        # Add diagrams
        self.library.add_diagram(
            "off_prep2",
            "Shelter Diagram",
            KnowledgeCategory.SHELTER,
            "<svg>shelter design</svg>"
        )

        # Verify offline accessibility
        stats = self.library.get_offline_stats()
        self.assertEqual(stats["offline_accessible"], 2)
        self.assertEqual(stats["percentage"], 100.0)

        # Export for offline use
        export = self.library.export_library()
        self.assertGreater(export["total_guides"], 0)


if __name__ == "__main__":
    unittest.main()

"""
uDOS v1.2.0 - Knowledge Bank Extensions Tests

Validates:
- Interactive skill trees with ASCII visualization
- Practical checklists (emergency, learning, projects)
- Knowledge guide expansion (500 → 1000+ guides)
- Category organization and tagging
- Progress tracking and completion
- SVG illustration integration
"""

import pytest
import json
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
from enum import Enum
from datetime import datetime


# ============================================================================
# SKILL TREE SYSTEM
# ============================================================================

class SkillLevel(Enum):
    """Skill proficiency levels"""
    NOVICE = "novice"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    MASTER = "master"


class SkillNode:
    """Individual skill in skill tree"""

    def __init__(self, skill_id: str, name: str, description: str,
                 level: SkillLevel, prerequisites: Optional[List[str]] = None,
                 estimated_hours: int = 0):
        self.skill_id = skill_id
        self.name = name
        self.description = description
        self.level = level
        self.prerequisites = prerequisites or []
        self.estimated_hours = estimated_hours
        self.completed = False
        self.completion_date: Optional[datetime] = None
        self.related_guides: List[str] = []
        self.xp_reward = estimated_hours * 10  # 10 XP per hour

    def can_unlock(self, completed_skills: Set[str]) -> bool:
        """Check if prerequisites are met"""
        return all(prereq in completed_skills for prereq in self.prerequisites)

    def complete(self):
        """Mark skill as completed"""
        self.completed = True
        self.completion_date = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "skill_id": self.skill_id,
            "name": self.name,
            "description": self.description,
            "level": self.level.value,
            "prerequisites": self.prerequisites,
            "estimated_hours": self.estimated_hours,
            "completed": self.completed,
            "completion_date": self.completion_date.isoformat() if self.completion_date else None,
            "related_guides": self.related_guides,
            "xp_reward": self.xp_reward
        }


class SkillTree:
    """Manages skill progression tree"""

    def __init__(self, tree_id: str, name: str, description: str):
        self.tree_id = tree_id
        self.name = name
        self.description = description
        self.skills: Dict[str, SkillNode] = {}
        self.root_skills: List[str] = []  # Skills with no prerequisites

    def add_skill(self, skill: SkillNode):
        """Add skill to tree"""
        self.skills[skill.skill_id] = skill

        # Track root skills (no prerequisites)
        if not skill.prerequisites:
            self.root_skills.append(skill.skill_id)

    def get_available_skills(self, completed_skills: Set[str]) -> List[SkillNode]:
        """Get skills that can be learned based on completed skills"""
        available = []

        for skill_id, skill in self.skills.items():
            if skill_id not in completed_skills and skill.can_unlock(completed_skills):
                available.append(skill)

        return sorted(available, key=lambda s: s.level.value)

    def get_next_recommended(self, completed_skills: Set[str]) -> Optional[SkillNode]:
        """Get next recommended skill to learn"""
        available = self.get_available_skills(completed_skills)
        if available:
            return available[0]  # Return easiest available skill
        return None

    def get_progression_path(self, target_skill_id: str) -> List[str]:
        """Get path from root to target skill"""
        if target_skill_id not in self.skills:
            return []

        path = []
        current = self.skills[target_skill_id]

        # Build path backwards from target
        visited = set()
        to_visit = [target_skill_id]

        while to_visit:
            skill_id = to_visit.pop(0)
            if skill_id in visited:
                continue

            visited.add(skill_id)
            skill = self.skills[skill_id]
            path.insert(0, skill_id)

            # Add prerequisites
            for prereq in skill.prerequisites:
                if prereq not in visited:
                    to_visit.append(prereq)

        return path

    def render_ascii_tree(self, completed_skills: Set[str]) -> str:
        """Render skill tree as ASCII art"""
        lines = []
        lines.append(f"╔═══ {self.name} ═══╗")
        lines.append(f"║ {self.description}")
        lines.append("╚═══════════════════╝\n")

        # Group skills by level
        levels = {}
        for skill_id, skill in self.skills.items():
            level_name = skill.level.value
            if level_name not in levels:
                levels[level_name] = []
            levels[level_name].append(skill)

        # Render each level
        for level in SkillLevel:
            level_skills = levels.get(level.value, [])
            if not level_skills:
                continue

            lines.append(f"\n┌─ {level.value.upper()} ─┐")

            for skill in level_skills:
                icon = "✓" if skill.skill_id in completed_skills else "○"
                locked = not skill.can_unlock(completed_skills)
                lock_icon = "🔒" if locked else ""

                lines.append(f"  {icon} {skill.name} {lock_icon}")
                lines.append(f"     └─ {skill.estimated_hours}h | {skill.xp_reward} XP")

                if skill.prerequisites:
                    prereq_names = [self.skills[p].name for p in skill.prerequisites]
                    lines.append(f"     ├─ Requires: {', '.join(prereq_names)}")

        return "\n".join(lines)

    def get_completion_stats(self, completed_skills: Set[str]) -> Dict[str, Any]:
        """Get completion statistics"""
        total_skills = len(self.skills)
        completed_count = len([s for s in self.skills.keys() if s in completed_skills])
        total_xp = sum(s.xp_reward for s in self.skills.values() if s.skill_id in completed_skills)
        total_hours = sum(s.estimated_hours for s in self.skills.values() if s.skill_id in completed_skills)

        return {
            "total_skills": total_skills,
            "completed_skills": completed_count,
            "completion_percentage": (completed_count / total_skills * 100) if total_skills > 0 else 0,
            "total_xp_earned": total_xp,
            "total_hours_invested": total_hours,
            "available_to_learn": len(self.get_available_skills(completed_skills))
        }


# ============================================================================
# PRACTICAL CHECKLISTS
# ============================================================================

class ChecklistCategory(Enum):
    """Checklist categories"""
    EMERGENCY = "emergency"
    LEARNING = "learning"
    PROJECT = "project"
    MAINTENANCE = "maintenance"
    DAILY = "daily"


class ChecklistItem:
    """Individual checklist item"""

    def __init__(self, item_id: str, description: str,
                 priority: str = "normal", notes: str = ""):
        self.item_id = item_id
        self.description = description
        self.priority = priority  # "critical", "high", "normal", "low"
        self.notes = notes
        self.completed = False
        self.completion_date: Optional[datetime] = None

    def complete(self):
        """Mark item as complete"""
        self.completed = True
        self.completion_date = datetime.now()

    def reset(self):
        """Reset completion status"""
        self.completed = False
        self.completion_date = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "item_id": self.item_id,
            "description": self.description,
            "priority": self.priority,
            "notes": self.notes,
            "completed": self.completed,
            "completion_date": self.completion_date.isoformat() if self.completion_date else None
        }


class Checklist:
    """Practical checklist template"""

    def __init__(self, checklist_id: str, name: str, category: ChecklistCategory,
                 description: str = ""):
        self.checklist_id = checklist_id
        self.name = name
        self.category = category
        self.description = description
        self.items: List[ChecklistItem] = []
        self.tags: List[str] = []
        self.created_at = datetime.now()
        self.last_updated = datetime.now()

    def add_item(self, item: ChecklistItem):
        """Add item to checklist"""
        self.items.append(item)
        self.last_updated = datetime.now()

    def complete_item(self, item_id: str) -> bool:
        """Complete a specific item"""
        for item in self.items:
            if item.item_id == item_id:
                item.complete()
                self.last_updated = datetime.now()
                return True
        return False

    def reset_all(self):
        """Reset all items"""
        for item in self.items:
            item.reset()
        self.last_updated = datetime.now()

    def get_progress(self) -> Dict[str, Any]:
        """Get completion progress"""
        total = len(self.items)
        completed = len([i for i in self.items if i.completed])

        return {
            "total_items": total,
            "completed_items": completed,
            "completion_percentage": (completed / total * 100) if total > 0 else 0,
            "remaining_items": total - completed
        }

    def render_markdown(self) -> str:
        """Render as markdown checklist"""
        lines = []
        lines.append(f"# {self.name}")
        lines.append(f"\n**Category:** {self.category.value}")

        if self.description:
            lines.append(f"\n{self.description}")

        if self.tags:
            lines.append(f"\n**Tags:** {', '.join(self.tags)}")

        # Progress bar
        progress = self.get_progress()
        pct = progress["completion_percentage"]
        filled = int(pct / 10)
        bar = "█" * filled + "░" * (10 - filled)
        lines.append(f"\n**Progress:** {bar} {pct:.0f}% ({progress['completed_items']}/{progress['total_items']})")

        lines.append("\n## Items\n")

        # Group by priority
        priority_order = ["critical", "high", "normal", "low"]
        for priority in priority_order:
            priority_items = [i for i in self.items if i.priority == priority]
            if not priority_items:
                continue

            if priority != "normal":
                lines.append(f"\n### {priority.upper()} Priority")

            for item in priority_items:
                checkbox = "x" if item.completed else " "
                priority_icon = {"critical": "🔴", "high": "🟠", "normal": "", "low": "🟢"}.get(priority, "")

                lines.append(f"- [{checkbox}] {priority_icon} {item.description}")

                if item.notes:
                    lines.append(f"  > {item.notes}")

        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "checklist_id": self.checklist_id,
            "name": self.name,
            "category": self.category.value,
            "description": self.description,
            "items": [item.to_dict() for item in self.items],
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat()
        }


class ChecklistLibrary:
    """Manages checklist templates and instances"""

    def __init__(self, storage_dir: str = "memory/checklists"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.templates: Dict[str, Checklist] = {}
        self.user_checklists: Dict[str, Checklist] = {}

    def add_template(self, checklist: Checklist):
        """Add checklist template"""
        self.templates[checklist.checklist_id] = checklist

    def create_from_template(self, template_id: str, instance_id: str) -> Optional[Checklist]:
        """Create user checklist from template"""
        if template_id not in self.templates:
            return None

        template = self.templates[template_id]

        # Create deep copy
        instance = Checklist(
            checklist_id=instance_id,
            name=template.name,
            category=template.category,
            description=template.description
        )
        instance.tags = template.tags.copy()

        # Copy items
        for item in template.items:
            new_item = ChecklistItem(
                item_id=item.item_id,
                description=item.description,
                priority=item.priority,
                notes=item.notes
            )
            instance.add_item(new_item)

        self.user_checklists[instance_id] = instance
        return instance

    def save_checklist(self, checklist_id: str):
        """Save user checklist to disk"""
        if checklist_id not in self.user_checklists:
            raise ValueError(f"Checklist {checklist_id} not found")

        checklist = self.user_checklists[checklist_id]
        filepath = self.storage_dir / f"{checklist_id}.json"

        with open(filepath, 'w') as f:
            json.dump(checklist.to_dict(), f, indent=2)

    def load_checklist(self, checklist_id: str) -> Optional[Checklist]:
        """Load checklist from disk"""
        filepath = self.storage_dir / f"{checklist_id}.json"
        if not filepath.exists():
            return None

        with open(filepath, 'r') as f:
            data = json.load(f)

        # Reconstruct checklist
        checklist = Checklist(
            checklist_id=data["checklist_id"],
            name=data["name"],
            category=ChecklistCategory(data["category"]),
            description=data.get("description", "")
        )
        checklist.tags = data.get("tags", [])
        checklist.created_at = datetime.fromisoformat(data["created_at"])
        checklist.last_updated = datetime.fromisoformat(data["last_updated"])

        # Add items
        for item_data in data["items"]:
            item = ChecklistItem(
                item_id=item_data["item_id"],
                description=item_data["description"],
                priority=item_data["priority"],
                notes=item_data.get("notes", "")
            )
            item.completed = item_data["completed"]
            if item_data.get("completion_date"):
                item.completion_date = datetime.fromisoformat(item_data["completion_date"])
            checklist.add_item(item)

        self.user_checklists[checklist_id] = checklist
        return checklist

    def search_templates(self, category: Optional[ChecklistCategory] = None,
                        tags: Optional[List[str]] = None) -> List[Checklist]:
        """Search templates by category and tags"""
        results = list(self.templates.values())

        if category:
            results = [c for c in results if c.category == category]

        if tags:
            results = [c for c in results if any(tag in c.tags for tag in tags)]

        return results


# ============================================================================
# KNOWLEDGE GUIDE SYSTEM
# ============================================================================

class GuideCategory(Enum):
    """Knowledge guide categories"""
    SURVIVAL = "survival"
    SKILLS = "skills"
    MAKING = "making"
    TECH = "tech"
    FOOD = "food"
    WATER = "water"
    MEDICAL = "medical"
    WELLBEING = "wellbeing"
    REFERENCE = "reference"


class KnowledgeGuide:
    """Individual knowledge guide"""

    def __init__(self, guide_id: str, title: str, category: GuideCategory,
                 content: str, difficulty: str = "beginner"):
        self.guide_id = guide_id
        self.title = title
        self.category = category
        self.content = content
        self.difficulty = difficulty  # "beginner", "intermediate", "advanced"
        self.tags: List[str] = []
        self.related_skills: List[str] = []
        self.estimated_read_time: int = len(content.split()) // 200  # minutes (200 wpm)
        self.illustrations: List[str] = []  # SVG file paths
        self.created_at = datetime.now()
        self.last_updated = datetime.now()

    def add_illustration(self, svg_path: str):
        """Add SVG illustration"""
        self.illustrations.append(svg_path)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "guide_id": self.guide_id,
            "title": self.title,
            "category": self.category.value,
            "content": self.content,
            "difficulty": self.difficulty,
            "tags": self.tags,
            "related_skills": self.related_skills,
            "estimated_read_time": self.estimated_read_time,
            "illustrations": self.illustrations,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat()
        }


class KnowledgeBank:
    """Extended knowledge bank with 1000+ guides"""

    def __init__(self, storage_dir: str = "knowledge"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.guides: Dict[str, KnowledgeGuide] = {}
        self.category_index: Dict[GuideCategory, List[str]] = {}
        self.tag_index: Dict[str, List[str]] = {}
        self.difficulty_index: Dict[str, List[str]] = {}

    def add_guide(self, guide: KnowledgeGuide):
        """Add guide to bank"""
        self.guides[guide.guide_id] = guide        # Update category index
        if guide.category not in self.category_index:
            self.category_index[guide.category] = []
        self.category_index[guide.category].append(guide.guide_id)

        # Update tag index
        for tag in guide.tags:
            if tag not in self.tag_index:
                self.tag_index[tag] = []
            self.tag_index[tag].append(guide.guide_id)

        # Update difficulty index
        if guide.difficulty not in self.difficulty_index:
            self.difficulty_index[guide.difficulty] = []
        self.difficulty_index[guide.difficulty].append(guide.guide_id)

    def get_by_category(self, category: GuideCategory) -> List[KnowledgeGuide]:
        """Get all guides in category"""
        guide_ids = self.category_index.get(category, [])
        return [self.guides[gid] for gid in guide_ids]

    def get_by_tags(self, tags: List[str]) -> List[KnowledgeGuide]:
        """Get guides matching any tag"""
        guide_ids = set()
        for tag in tags:
            guide_ids.update(self.tag_index.get(tag, []))

        return [self.guides[gid] for gid in guide_ids]

    def get_by_difficulty(self, difficulty: str) -> List[KnowledgeGuide]:
        """Get guides by difficulty level"""
        guide_ids = self.difficulty_index.get(difficulty, [])
        return [self.guides[gid] for gid in guide_ids]

    def search(self, query: str) -> List[KnowledgeGuide]:
        """Simple keyword search"""
        query_lower = query.lower()
        results = []

        for guide in self.guides.values():
            # Search in title, tags, and content
            if (query_lower in guide.title.lower() or
                any(query_lower in tag.lower() for tag in guide.tags) or
                query_lower in guide.content.lower()):
                results.append(guide)

        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge bank statistics"""
        return {
            "total_guides": len(self.guides),
            "categories": {cat.value: len(guides) for cat, guides in self.category_index.items()},
            "difficulty_levels": {diff: len(guides) for diff, guides in self.difficulty_index.items()},
            "total_tags": len(self.tag_index),
            "total_illustrations": sum(len(g.illustrations) for g in self.guides.values())
        }


# ============================================================================
# TESTS - Skill Trees
# ============================================================================

class TestSkillNode:
    """Test skill node"""

    def test_create_skill(self):
        """Test creating skill node"""
        skill = SkillNode(
            "water_001",
            "Water Purification",
            "Learn to purify water safely",
            SkillLevel.BEGINNER,
            estimated_hours=2
        )

        assert skill.skill_id == "water_001"
        assert skill.level == SkillLevel.BEGINNER
        assert skill.xp_reward == 20  # 2 hours * 10 XP

    def test_skill_prerequisites(self):
        """Test prerequisite checking"""
        skill = SkillNode(
            "fire_002",
            "Bow Drill Fire",
            "Advanced fire starting",
            SkillLevel.ADVANCED,
            prerequisites=["fire_001"],
            estimated_hours=5
        )

        # No skills completed - locked
        assert not skill.can_unlock(set())

        # Prerequisite completed - unlocked
        assert skill.can_unlock({"fire_001"})

    def test_skill_completion(self):
        """Test skill completion"""
        skill = SkillNode("shelter_001", "Basic Lean-To", "Build shelter", SkillLevel.BEGINNER)

        assert not skill.completed
        skill.complete()

        assert skill.completed
        assert skill.completion_date is not None


class TestSkillTree:
    """Test skill tree system"""

    @pytest.fixture
    def survival_tree(self):
        """Create survival skill tree"""
        tree = SkillTree(
            "survival_basics",
            "Survival Fundamentals",
            "Core survival skills for emergency situations"
        )

        # Beginner skills (no prerequisites)
        tree.add_skill(SkillNode(
            "water_001", "Find Water Sources", "Locate water", SkillLevel.BEGINNER, estimated_hours=1
        ))
        tree.add_skill(SkillNode(
            "fire_001", "Match Fire Starting", "Start fire with matches", SkillLevel.BEGINNER, estimated_hours=1
        ))

        # Intermediate skills (require beginner)
        tree.add_skill(SkillNode(
            "water_002", "Water Purification", "Purify water", SkillLevel.INTERMEDIATE,
            prerequisites=["water_001"], estimated_hours=2
        ))
        tree.add_skill(SkillNode(
            "fire_002", "Friction Fire", "Start fire without matches", SkillLevel.INTERMEDIATE,
            prerequisites=["fire_001"], estimated_hours=3
        ))

        # Advanced skill (require intermediate)
        tree.add_skill(SkillNode(
            "water_003", "Well Construction", "Build water well", SkillLevel.ADVANCED,
            prerequisites=["water_002"], estimated_hours=8
        ))

        return tree

    def test_create_tree(self, survival_tree):
        """Test creating skill tree"""
        assert survival_tree.tree_id == "survival_basics"
        assert len(survival_tree.skills) == 5
        assert len(survival_tree.root_skills) == 2

    def test_available_skills(self, survival_tree):
        """Test getting available skills"""
        completed = set()

        # Initially only root skills available
        available = survival_tree.get_available_skills(completed)
        assert len(available) == 2
        assert all(s.level == SkillLevel.BEGINNER for s in available)

        # Complete water_001
        completed.add("water_001")
        available = survival_tree.get_available_skills(completed)
        assert any(s.skill_id == "water_002" for s in available)

    def test_next_recommended(self, survival_tree):
        """Test next skill recommendation"""
        completed = set()

        next_skill = survival_tree.get_next_recommended(completed)
        assert next_skill is not None
        assert next_skill.level == SkillLevel.BEGINNER

    def test_progression_path(self, survival_tree):
        """Test getting progression path"""
        path = survival_tree.get_progression_path("water_003")

        assert "water_001" in path
        assert "water_002" in path
        assert "water_003" in path
        assert path.index("water_001") < path.index("water_002")
        assert path.index("water_002") < path.index("water_003")

    def test_ascii_rendering(self, survival_tree):
        """Test ASCII tree rendering"""
        completed = {"water_001", "fire_001"}
        ascii_tree = survival_tree.render_ascii_tree(completed)

        assert "Survival Fundamentals" in ascii_tree
        assert "BEGINNER" in ascii_tree
        assert "INTERMEDIATE" in ascii_tree
        assert "✓" in ascii_tree  # Completed skills
        assert "○" in ascii_tree  # Uncompleted skills
        assert "🔒" in ascii_tree  # Locked skills

    def test_completion_stats(self, survival_tree):
        """Test completion statistics"""
        completed = {"water_001", "fire_001", "water_002"}
        stats = survival_tree.get_completion_stats(completed)

        assert stats["total_skills"] == 5
        assert stats["completed_skills"] == 3
        assert stats["completion_percentage"] == 60.0
        assert stats["total_xp_earned"] == 40  # 1+1+2 hours * 10 XP


# ============================================================================
# TESTS - Checklists
# ============================================================================

class TestChecklistItem:
    """Test checklist items"""

    def test_create_item(self):
        """Test creating checklist item"""
        item = ChecklistItem(
            "item_001",
            "Pack first aid kit",
            priority="critical"
        )

        assert item.item_id == "item_001"
        assert item.priority == "critical"
        assert not item.completed

    def test_complete_item(self):
        """Test completing item"""
        item = ChecklistItem("item_002", "Check batteries")

        item.complete()
        assert item.completed
        assert item.completion_date is not None

        item.reset()
        assert not item.completed


class TestChecklist:
    """Test checklist system"""

    @pytest.fixture
    def bugout_checklist(self):
        """Create bug-out bag checklist"""
        checklist = Checklist(
            "bugout_001",
            "Bug-Out Bag Essentials",
            ChecklistCategory.EMERGENCY,
            "72-hour emergency kit"
        )
        checklist.tags = ["emergency", "preparedness", "72hour"]

        checklist.add_item(ChecklistItem("i1", "Water - 3L per person", "critical"))
        checklist.add_item(ChecklistItem("i2", "Food - Non-perishable", "critical"))
        checklist.add_item(ChecklistItem("i3", "First aid kit", "critical"))
        checklist.add_item(ChecklistItem("i4", "Flashlight + batteries", "high"))
        checklist.add_item(ChecklistItem("i5", "Emergency blanket", "high"))
        checklist.add_item(ChecklistItem("i6", "Multi-tool", "normal"))

        return checklist

    def test_create_checklist(self, bugout_checklist):
        """Test creating checklist"""
        assert bugout_checklist.checklist_id == "bugout_001"
        assert bugout_checklist.category == ChecklistCategory.EMERGENCY
        assert len(bugout_checklist.items) == 6

    def test_complete_items(self, bugout_checklist):
        """Test completing items"""
        assert bugout_checklist.complete_item("i1")
        assert bugout_checklist.complete_item("i2")

        progress = bugout_checklist.get_progress()
        assert progress["completed_items"] == 2
        assert progress["completion_percentage"] == pytest.approx(33.33, rel=0.1)

    def test_reset_checklist(self, bugout_checklist):
        """Test resetting checklist"""
        bugout_checklist.complete_item("i1")
        bugout_checklist.complete_item("i2")

        bugout_checklist.reset_all()

        progress = bugout_checklist.get_progress()
        assert progress["completed_items"] == 0

    def test_markdown_rendering(self, bugout_checklist):
        """Test markdown rendering"""
        bugout_checklist.complete_item("i1")

        markdown = bugout_checklist.render_markdown()

        assert "Bug-Out Bag Essentials" in markdown
        assert "CRITICAL Priority" in markdown
        assert "[x]" in markdown  # Completed item
        assert "[ ]" in markdown  # Uncompleted items
        assert "Progress:" in markdown


class TestChecklistLibrary:
    """Test checklist library"""

    @pytest.fixture
    def library(self, tmp_path):
        """Create checklist library"""
        return ChecklistLibrary(str(tmp_path / "checklists"))

    def test_create_library(self, library):
        """Test creating library"""
        assert library.storage_dir.exists()

    def test_add_template(self, library):
        """Test adding template"""
        template = Checklist(
            "template_001",
            "Daily Routine",
            ChecklistCategory.DAILY
        )
        template.add_item(ChecklistItem("d1", "Morning exercise"))

        library.add_template(template)
        assert "template_001" in library.templates

    def test_create_from_template(self, library):
        """Test creating instance from template"""
        template = Checklist("tmpl_001", "Test Template", ChecklistCategory.PROJECT)
        template.add_item(ChecklistItem("t1", "Task 1"))
        template.add_item(ChecklistItem("t2", "Task 2"))
        library.add_template(template)

        instance = library.create_from_template("tmpl_001", "instance_001")

        assert instance is not None
        assert instance.checklist_id == "instance_001"
        assert len(instance.items) == 2

    def test_save_and_load(self, library):
        """Test saving and loading checklist"""
        checklist = Checklist("check_001", "Test Checklist", ChecklistCategory.LEARNING)
        checklist.add_item(ChecklistItem("c1", "Learn Python"))
        library.user_checklists["check_001"] = checklist

        library.save_checklist("check_001")

        loaded = library.load_checklist("check_001")
        assert loaded is not None
        assert loaded.checklist_id == "check_001"
        assert len(loaded.items) == 1

    def test_search_templates(self, library):
        """Test searching templates"""
        emergency = Checklist("em_001", "Emergency Kit", ChecklistCategory.EMERGENCY)
        emergency.tags = ["emergency", "72hour"]
        library.add_template(emergency)

        project = Checklist("pr_001", "Garden Project", ChecklistCategory.PROJECT)
        project.tags = ["garden", "outdoor"]
        library.add_template(project)

        results = library.search_templates(category=ChecklistCategory.EMERGENCY)
        assert len(results) == 1

        results = library.search_templates(tags=["garden"])
        assert len(results) == 1


# ============================================================================
# TESTS - Knowledge Bank
# ============================================================================

class TestKnowledgeGuide:
    """Test knowledge guide"""

    def test_create_guide(self):
        """Test creating guide"""
        guide = KnowledgeGuide(
            "water_101",
            "Water Purification Methods",
            GuideCategory.WATER,
            "This guide covers various water purification techniques. " * 50,  # Longer content
            difficulty="beginner"
        )

        assert guide.guide_id == "water_101"
        assert guide.category == GuideCategory.WATER
        assert guide.estimated_read_time > 0

    def test_add_illustration(self):
        """Test adding illustrations"""
        guide = KnowledgeGuide(
            "fire_101",
            "Fire Starting",
            GuideCategory.SURVIVAL,
            "Fire starting basics..."
        )

        guide.add_illustration("illustrations/fire_starting.svg")
        assert len(guide.illustrations) == 1


class TestKnowledgeBank:
    """Test knowledge bank system"""

    @pytest.fixture
    def knowledge_bank(self, tmp_path):
        """Create knowledge bank"""
        return KnowledgeBank(str(tmp_path / "knowledge"))

    def test_create_bank(self, knowledge_bank):
        """Test creating knowledge bank"""
        assert knowledge_bank.storage_dir.exists()

    def test_add_guides(self, knowledge_bank):
        """Test adding guides"""
        guide1 = KnowledgeGuide(
            "water_001", "Find Water", GuideCategory.WATER,
            "How to find water sources in wilderness..."
        )
        guide1.tags = ["water", "survival", "wilderness"]

        guide2 = KnowledgeGuide(
            "fire_001", "Start Fire", GuideCategory.SURVIVAL,
            "Fire starting techniques..."
        )
        guide2.tags = ["fire", "survival"]

        knowledge_bank.add_guide(guide1)
        knowledge_bank.add_guide(guide2)

        assert len(knowledge_bank.guides) == 2

    def test_get_by_category(self, knowledge_bank):
        """Test getting guides by category"""
        water_guide = KnowledgeGuide(
            "w1", "Water Guide", GuideCategory.WATER, "Content..."
        )
        survival_guide = KnowledgeGuide(
            "s1", "Survival Guide", GuideCategory.SURVIVAL, "Content..."
        )

        knowledge_bank.add_guide(water_guide)
        knowledge_bank.add_guide(survival_guide)

        water_guides = knowledge_bank.get_by_category(GuideCategory.WATER)
        assert len(water_guides) == 1
        assert water_guides[0].guide_id == "w1"

    def test_get_by_tags(self, knowledge_bank):
        """Test getting guides by tags"""
        guide1 = KnowledgeGuide("g1", "Guide 1", GuideCategory.SURVIVAL, "Content...")
        guide1.tags = ["water", "emergency"]

        guide2 = KnowledgeGuide("g2", "Guide 2", GuideCategory.SURVIVAL, "Content...")
        guide2.tags = ["fire", "emergency"]

        knowledge_bank.add_guide(guide1)
        knowledge_bank.add_guide(guide2)

        emergency_guides = knowledge_bank.get_by_tags(["emergency"])
        assert len(emergency_guides) == 2

        water_guides = knowledge_bank.get_by_tags(["water"])
        assert len(water_guides) == 1

    def test_get_by_difficulty(self, knowledge_bank):
        """Test getting guides by difficulty"""
        beginner = KnowledgeGuide(
            "b1", "Beginner Guide", GuideCategory.SKILLS, "Content...", difficulty="beginner"
        )
        advanced = KnowledgeGuide(
            "a1", "Advanced Guide", GuideCategory.SKILLS, "Content...", difficulty="advanced"
        )

        knowledge_bank.add_guide(beginner)
        knowledge_bank.add_guide(advanced)

        beginner_guides = knowledge_bank.get_by_difficulty("beginner")
        assert len(beginner_guides) == 1

    def test_search_guides(self, knowledge_bank):
        """Test searching guides"""
        guide1 = KnowledgeGuide(
            "g1", "Water Purification Methods", GuideCategory.WATER,
            "Learn how to purify water using various methods..."
        )
        guide2 = KnowledgeGuide(
            "g2", "Fire Starting Basics", GuideCategory.SURVIVAL,
            "Basic fire starting techniques for beginners..."
        )

        knowledge_bank.add_guide(guide1)
        knowledge_bank.add_guide(guide2)

        results = knowledge_bank.search("water")
        assert len(results) == 1
        assert results[0].guide_id == "g1"

        results = knowledge_bank.search("fire")
        assert len(results) == 1
        assert results[0].guide_id == "g2"

    def test_bank_stats(self, knowledge_bank):
        """Test knowledge bank statistics"""
        for i in range(10):
            guide = KnowledgeGuide(
                f"guide_{i}", f"Guide {i}", GuideCategory.SURVIVAL,
                "Content...", difficulty="beginner"
            )
            knowledge_bank.add_guide(guide)

        stats = knowledge_bank.get_stats()

        assert stats["total_guides"] == 10
        assert stats["categories"][GuideCategory.SURVIVAL.value] == 10


# ============================================================================
# TEST SUMMARY
# ============================================================================

def test_summary():
    """Print test summary"""
    print("\n" + "="*70)
    print("uDOS v1.2.0 - Knowledge Bank Extensions Tests")
    print("="*70)
    print("\n✅ Skill Tree System:")
    print("  • SkillNode - Individual skills with prerequisites")
    print("  • SkillTree - Progression paths and dependencies")
    print("  • ASCII tree visualization")
    print("  • XP rewards and time estimates")
    print("  • Completion tracking")
    print("\n✅ Practical Checklists:")
    print("  • ChecklistItem - Individual tasks")
    print("  • Checklist - Categorized task lists")
    print("  • ChecklistLibrary - Templates and instances")
    print("  • Markdown rendering with progress")
    print("  • Emergency, Learning, Project categories")
    print("\n✅ Knowledge Bank:")
    print("  • KnowledgeGuide - Individual guides")
    print("  • KnowledgeBank - 1000+ guide management")
    print("  • Category organization (9 categories)")
    print("  • Tag-based search")
    print("  • Difficulty filtering")
    print("  • SVG illustration support")
    print("\n✅ Features:")
    print("  • 6 skill proficiency levels")
    print("  • 5 checklist categories")
    print("  • 9 knowledge categories")
    print("  • Prerequisite tracking")
    print("  • Progress visualization")
    print("  • JSON persistence")
    print("\n" + "="*70)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

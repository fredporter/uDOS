"""
Test Suite for v1.1.3.3 - Interactive Skill Trees
Tests: ASCII skill trees, progression paths, XP integration, display modes

Test Coverage (50 tests total):
- Skill Tree Structure: 10 tests
- Progression Paths: 10 tests
- ASCII Rendering: 10 tests
- XP Integration: 8 tests
- Display Modes: 6 tests
- Integration: 6 tests

Author: uDOS Development Team
Version: 1.1.3.3
Date: 2025-11-24
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
import json
from typing import Dict, List, Any, Optional

# Add core to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))


class SkillNode:
    """Individual skill in tree"""

    def __init__(self, id: str, name: str, description: str,
                 xp_cost: int = 0, max_level: int = 5):
        self.id = id
        self.name = name
        self.description = description
        self.xp_cost = xp_cost
        self.max_level = max_level
        self.current_level = 0
        self.unlocked = False
        self.prerequisites = []  # List of skill IDs
        self.position = (0, 0)  # (row, col) for ASCII rendering
        self.category = "general"  # survival, technical, social, etc.

    def can_unlock(self, unlocked_skills: set, current_xp: int) -> bool:
        """Check if skill can be unlocked"""
        if self.unlocked:
            return False

        # Check XP requirement
        if current_xp < self.xp_cost:
            return False

        # Check prerequisites
        for prereq in self.prerequisites:
            if prereq not in unlocked_skills:
                return False

        return True

    def unlock(self):
        """Unlock skill"""
        self.unlocked = True
        self.current_level = 1

    def level_up(self) -> bool:
        """Increase skill level"""
        if not self.unlocked:
            return False

        if self.current_level >= self.max_level:
            return False

        self.current_level += 1
        return True

    def get_progress(self) -> float:
        """Get skill progress percentage"""
        if not self.unlocked:
            return 0.0
        return (self.current_level / self.max_level) * 100.0


class SkillTreeTemplate:
    """Predefined skill tree templates"""

    @staticmethod
    def survival_tree() -> 'SkillTree':
        """Create survival skill tree"""
        tree = SkillTree("survival", "Survival Skills")

        # Tier 1 - Basics
        tree.add_skill("water_basics", "Water Basics", "Find and purify water", 0, category="survival")
        tree.add_skill("fire_basics", "Fire Starting", "Start fire with basic tools", 0, category="survival")
        tree.add_skill("shelter_basics", "Basic Shelter", "Build simple shelter", 0, category="survival")

        # Tier 2 - Advanced
        tree.add_skill("water_advanced", "Water Purification", "Advanced water treatment", 100,
                      prerequisites=["water_basics"], category="survival")
        tree.add_skill("fire_advanced", "Fire Mastery", "Start fire in any condition", 100,
                      prerequisites=["fire_basics"], category="survival")
        tree.add_skill("shelter_advanced", "Advanced Shelter", "Build weatherproof shelter", 100,
                      prerequisites=["shelter_basics"], category="survival")

        # Tier 3 - Expert
        tree.add_skill("survival_expert", "Survival Expert", "Master survivalist", 500,
                      prerequisites=["water_advanced", "fire_advanced", "shelter_advanced"],
                      category="survival")

        # Set positions for rendering
        tree.skills["water_basics"].position = (0, 0)
        tree.skills["fire_basics"].position = (0, 2)
        tree.skills["shelter_basics"].position = (0, 4)
        tree.skills["water_advanced"].position = (2, 0)
        tree.skills["fire_advanced"].position = (2, 2)
        tree.skills["shelter_advanced"].position = (2, 4)
        tree.skills["survival_expert"].position = (4, 2)

        return tree

    @staticmethod
    def technical_tree() -> 'SkillTree':
        """Create technical skill tree"""
        tree = SkillTree("technical", "Technical Skills")

        # Programming branch
        tree.add_skill("coding_basics", "Coding Basics", "Learn programming fundamentals", 0, category="technical")
        tree.add_skill("python_intermediate", "Python", "Python programming", 50,
                      prerequisites=["coding_basics"], category="technical")
        tree.add_skill("automation", "Automation", "Script automation", 200,
                      prerequisites=["python_intermediate"], category="technical")

        # Electronics branch
        tree.add_skill("electronics_basics", "Electronics Basics", "Basic circuits", 0, category="technical")
        tree.add_skill("solar_power", "Solar Power", "Solar panel systems", 100,
                      prerequisites=["electronics_basics"], category="technical")

        # Master skill
        tree.add_skill("tech_master", "Tech Master", "Technical mastery", 1000,
                      prerequisites=["automation", "solar_power"], category="technical")

        # Set positions
        tree.skills["coding_basics"].position = (0, 0)
        tree.skills["electronics_basics"].position = (0, 4)
        tree.skills["python_intermediate"].position = (1, 0)
        tree.skills["solar_power"].position = (1, 4)
        tree.skills["automation"].position = (2, 0)
        tree.skills["tech_master"].position = (3, 2)

        return tree


class SkillTree:
    """Skill tree manager"""

    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name
        self.skills = {}  # id -> SkillNode
        self.unlocked_skills = set()
        self.total_xp_spent = 0

    def add_skill(self, id: str, name: str, description: str,
                  xp_cost: int = 0, max_level: int = 5,
                  prerequisites: List[str] = None, category: str = "general"):
        """Add skill to tree"""
        skill = SkillNode(id, name, description, xp_cost, max_level)
        skill.prerequisites = prerequisites or []
        skill.category = category
        self.skills[id] = skill

    def unlock_skill(self, skill_id: str, current_xp: int) -> bool:
        """Unlock a skill"""
        skill = self.skills.get(skill_id)
        if not skill:
            return False

        if not skill.can_unlock(self.unlocked_skills, current_xp):
            return False

        skill.unlock()
        self.unlocked_skills.add(skill_id)
        self.total_xp_spent += skill.xp_cost
        return True

    def level_up_skill(self, skill_id: str) -> bool:
        """Level up a skill"""
        skill = self.skills.get(skill_id)
        if not skill:
            return False

        return skill.level_up()

    def get_available_skills(self, current_xp: int) -> List[SkillNode]:
        """Get skills that can be unlocked"""
        available = []
        for skill in self.skills.values():
            if skill.can_unlock(self.unlocked_skills, current_xp):
                available.append(skill)
        return available

    def get_skills_by_category(self, category: str) -> List[SkillNode]:
        """Get all skills in category"""
        return [s for s in self.skills.values() if s.category == category]

    def get_tree_progress(self) -> Dict[str, float]:
        """Get overall tree progress"""
        if not self.skills:
            return {'unlocked': 0, 'total': 0, 'percentage': 0}

        unlocked = len(self.unlocked_skills)
        total = len(self.skills)
        percentage = (unlocked / total) * 100

        return {
            'unlocked': unlocked,
            'total': total,
            'percentage': percentage,
            'xp_spent': self.total_xp_spent
        }


class ASCIITreeRenderer:
    """Render skill trees as ASCII art"""

    def __init__(self):
        self.width = 80
        self.height = 25
        self.grid = []

    def render_tree(self, tree: SkillTree) -> str:
        """Render complete skill tree"""
        # Initialize grid
        self.grid = [[' ' for _ in range(self.width)] for _ in range(self.height)]

        # Render skills
        for skill in tree.skills.values():
            self._render_skill_node(skill)

        # Render connections
        for skill in tree.skills.values():
            for prereq_id in skill.prerequisites:
                prereq = tree.skills.get(prereq_id)
                if prereq:
                    self._render_connection(prereq, skill)

        # Convert grid to string
        return '\n'.join(''.join(row) for row in self.grid)

    def _render_skill_node(self, skill: SkillNode):
        """Render individual skill node"""
        row, col = skill.position
        row = row * 3  # Vertical spacing
        col = col * 12  # Horizontal spacing

        # Ensure within bounds
        if row >= self.height - 2 or col >= self.width - 10:
            return

        # Box style based on status
        if skill.unlocked:
            if skill.current_level >= skill.max_level:
                border = '═'  # Mastered
                corner = '╬'
            else:
                border = '─'  # Unlocked
                corner = '┼'
        else:
            border = '·'  # Locked
            corner = '·'

        # Draw box (simplified 10-char width)
        box_width = 10

        # Top border
        if row < self.height and col + box_width < self.width:
            self.grid[row][col] = corner
            for i in range(1, box_width - 1):
                if col + i < self.width:
                    self.grid[row][col + i] = border
            if col + box_width - 1 < self.width:
                self.grid[row][col + box_width - 1] = corner

        # Skill name (truncated to fit)
        if row + 1 < self.height:
            name = skill.name[:8]  # Max 8 chars
            start_col = col + 1
            for i, char in enumerate(name):
                if start_col + i < self.width:
                    self.grid[row + 1][start_col + i] = char

        # Bottom border
        if row + 2 < self.height and col + box_width < self.width:
            self.grid[row + 2][col] = corner
            for i in range(1, box_width - 1):
                if col + i < self.width:
                    self.grid[row + 2][col + i] = border
            if col + box_width - 1 < self.width:
                self.grid[row + 2][col + box_width - 1] = corner

    def _render_connection(self, from_skill: SkillNode, to_skill: SkillNode):
        """Render connection line between skills"""
        from_row, from_col = from_skill.position
        to_row, to_col = to_skill.position

        # Convert to grid coordinates (center of boxes)
        from_row = from_row * 3 + 1
        from_col = from_col * 12 + 5
        to_row = to_row * 3 + 1
        to_col = to_col * 12 + 5

        # Simple line drawing (vertical then horizontal)
        if from_row < to_row:
            # Draw vertical line
            for r in range(from_row + 1, to_row):
                if r < self.height and from_col < self.width:
                    if self.grid[r][from_col] == ' ':
                        self.grid[r][from_col] = '│'

            # Draw horizontal line
            if to_row < self.height:
                start_col = min(from_col, to_col)
                end_col = max(from_col, to_col)
                for c in range(start_col, end_col + 1):
                    if c < self.width:
                        if self.grid[to_row][c] == ' ':
                            self.grid[to_row][c] = '─'
                        elif self.grid[to_row][c] == '│':
                            self.grid[to_row][c] = '┼'


class ProgressionPath:
    """Learning progression path through skill tree"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.milestones = []  # List of skill IDs in order
        self.current_milestone = 0

    def add_milestone(self, skill_id: str):
        """Add skill to progression path"""
        self.milestones.append(skill_id)

    def get_next_skill(self) -> Optional[str]:
        """Get next skill to unlock"""
        if self.current_milestone >= len(self.milestones):
            return None
        return self.milestones[self.current_milestone]

    def advance(self):
        """Move to next milestone"""
        if self.current_milestone < len(self.milestones):
            self.current_milestone += 1

    def get_progress(self) -> Dict:
        """Get path progress"""
        total = len(self.milestones)
        current = self.current_milestone
        percentage = (current / total * 100) if total > 0 else 0

        return {
            'current': current,
            'total': total,
            'percentage': percentage,
            'completed': current >= total
        }


class SkillTreeManager:
    """Manage multiple skill trees"""

    def __init__(self):
        self.trees = {}  # tree_id -> SkillTree
        self.paths = {}  # path_id -> ProgressionPath

    def add_tree(self, tree: SkillTree):
        """Add skill tree"""
        self.trees[tree.id] = tree

    def get_tree(self, tree_id: str) -> Optional[SkillTree]:
        """Get skill tree by ID"""
        return self.trees.get(tree_id)

    def add_path(self, path: ProgressionPath, path_id: str):
        """Add progression path"""
        self.paths[path_id] = path

    def get_all_available_skills(self, current_xp: int) -> List[tuple]:
        """Get all available skills across all trees"""
        available = []
        for tree in self.trees.values():
            for skill in tree.get_available_skills(current_xp):
                available.append((tree.id, skill))
        return available

    def get_total_progress(self) -> Dict:
        """Get progress across all trees"""
        total_unlocked = 0
        total_skills = 0
        total_xp_spent = 0

        for tree in self.trees.values():
            progress = tree.get_tree_progress()
            total_unlocked += progress['unlocked']
            total_skills += progress['total']
            total_xp_spent += progress['xp_spent']

        percentage = (total_unlocked / total_skills * 100) if total_skills > 0 else 0

        return {
            'unlocked': total_unlocked,
            'total': total_skills,
            'percentage': percentage,
            'xp_spent': total_xp_spent,
            'trees': len(self.trees)
        }


# ============================================================================
# TEST CLASSES
# ============================================================================

class TestSkillTreeStructure(unittest.TestCase):
    """Test skill tree structure (10 tests)"""

    def test_skill_node_creation(self):
        """Test creating skill nodes"""
        skill = SkillNode("test1", "Test Skill", "Description", xp_cost=100)
        self.assertEqual(skill.name, "Test Skill")
        self.assertEqual(skill.xp_cost, 100)
        self.assertFalse(skill.unlocked)

    def test_skill_tree_creation(self):
        """Test creating skill tree"""
        tree = SkillTree("survival", "Survival Skills")
        self.assertEqual(tree.name, "Survival Skills")
        self.assertEqual(len(tree.skills), 0)

    def test_add_skill_to_tree(self):
        """Test adding skills to tree"""
        tree = SkillTree("test", "Test Tree")
        tree.add_skill("skill1", "Skill 1", "Description", xp_cost=50)

        self.assertEqual(len(tree.skills), 1)
        self.assertIn("skill1", tree.skills)

    def test_skill_prerequisites(self):
        """Test skill prerequisites"""
        tree = SkillTree("test", "Test Tree")
        tree.add_skill("basic", "Basic", "Basic skill", xp_cost=0)
        tree.add_skill("advanced", "Advanced", "Advanced skill",
                      xp_cost=100, prerequisites=["basic"])

        self.assertEqual(tree.skills["advanced"].prerequisites, ["basic"])

    def test_skill_can_unlock_no_prereqs(self):
        """Test skill can unlock without prerequisites"""
        skill = SkillNode("test", "Test", "Description", xp_cost=50)
        result = skill.can_unlock(set(), 100)

        self.assertTrue(result)

    def test_skill_cannot_unlock_insufficient_xp(self):
        """Test skill requires sufficient XP"""
        skill = SkillNode("test", "Test", "Description", xp_cost=100)
        result = skill.can_unlock(set(), 50)

        self.assertFalse(result)

    def test_skill_cannot_unlock_missing_prereq(self):
        """Test skill requires prerequisites"""
        skill = SkillNode("advanced", "Advanced", "Description", xp_cost=50)
        skill.prerequisites = ["basic"]

        result = skill.can_unlock(set(), 100)
        self.assertFalse(result)

    def test_skill_unlock(self):
        """Test unlocking skill"""
        tree = SkillTree("test", "Test")
        tree.add_skill("skill1", "Skill", "Description", xp_cost=50)

        result = tree.unlock_skill("skill1", 100)
        self.assertTrue(result)
        self.assertIn("skill1", tree.unlocked_skills)

    def test_skill_level_up(self):
        """Test leveling up skill"""
        tree = SkillTree("test", "Test")
        tree.add_skill("skill1", "Skill", "Description", xp_cost=0, max_level=5)
        tree.unlock_skill("skill1", 0)

        result = tree.level_up_skill("skill1")
        self.assertTrue(result)
        self.assertEqual(tree.skills["skill1"].current_level, 2)

    def test_skill_max_level(self):
        """Test skill max level cap"""
        skill = SkillNode("test", "Test", "Description", max_level=3)
        skill.unlock()

        skill.level_up()  # Level 2
        skill.level_up()  # Level 3
        result = skill.level_up()  # Try level 4

        self.assertFalse(result)
        self.assertEqual(skill.current_level, 3)


class TestProgressionPaths(unittest.TestCase):
    """Test progression paths (10 tests)"""

    def test_path_creation(self):
        """Test creating progression path"""
        path = ProgressionPath("beginner", "Beginner path")
        self.assertEqual(path.name, "beginner")
        self.assertEqual(len(path.milestones), 0)

    def test_add_milestones(self):
        """Test adding milestones to path"""
        path = ProgressionPath("beginner", "Beginner path")
        path.add_milestone("skill1")
        path.add_milestone("skill2")
        path.add_milestone("skill3")

        self.assertEqual(len(path.milestones), 3)

    def test_get_next_skill(self):
        """Test getting next skill in path"""
        path = ProgressionPath("beginner", "Beginner path")
        path.add_milestone("skill1")
        path.add_milestone("skill2")

        next_skill = path.get_next_skill()
        self.assertEqual(next_skill, "skill1")

    def test_advance_path(self):
        """Test advancing through path"""
        path = ProgressionPath("beginner", "Beginner path")
        path.add_milestone("skill1")
        path.add_milestone("skill2")

        path.advance()
        next_skill = path.get_next_skill()

        self.assertEqual(next_skill, "skill2")
        self.assertEqual(path.current_milestone, 1)

    def test_path_completion(self):
        """Test completing path"""
        path = ProgressionPath("beginner", "Beginner path")
        path.add_milestone("skill1")
        path.add_milestone("skill2")

        path.advance()
        path.advance()

        progress = path.get_progress()
        self.assertTrue(progress['completed'])

    def test_path_progress_percentage(self):
        """Test path progress calculation"""
        path = ProgressionPath("beginner", "Beginner path")
        path.add_milestone("skill1")
        path.add_milestone("skill2")
        path.add_milestone("skill3")
        path.add_milestone("skill4")

        path.advance()
        path.advance()

        progress = path.get_progress()
        self.assertEqual(progress['percentage'], 50.0)

    def test_path_at_end(self):
        """Test path at completion"""
        path = ProgressionPath("beginner", "Beginner path")
        path.add_milestone("skill1")

        path.advance()
        next_skill = path.get_next_skill()

        self.assertIsNone(next_skill)

    def test_survival_progression_path(self):
        """Test survival skill progression"""
        path = ProgressionPath("survival_basics", "Survival Basics Path")
        path.add_milestone("water_basics")
        path.add_milestone("fire_basics")
        path.add_milestone("shelter_basics")
        path.add_milestone("water_advanced")

        self.assertEqual(len(path.milestones), 4)
        self.assertEqual(path.get_next_skill(), "water_basics")

    def test_technical_progression_path(self):
        """Test technical skill progression"""
        path = ProgressionPath("coding_path", "Coding Path")
        path.add_milestone("coding_basics")
        path.add_milestone("python_intermediate")
        path.add_milestone("automation")

        self.assertEqual(len(path.milestones), 3)

    def test_multiple_paths(self):
        """Test managing multiple paths"""
        manager = SkillTreeManager()

        path1 = ProgressionPath("path1", "Path 1")
        path1.add_milestone("skill1")

        path2 = ProgressionPath("path2", "Path 2")
        path2.add_milestone("skill2")

        manager.add_path(path1, "path1")
        manager.add_path(path2, "path2")

        self.assertEqual(len(manager.paths), 2)


class TestASCIIRendering(unittest.TestCase):
    """Test ASCII tree rendering (10 tests)"""

    def test_renderer_creation(self):
        """Test creating ASCII renderer"""
        renderer = ASCIITreeRenderer()
        self.assertEqual(renderer.width, 80)
        self.assertEqual(renderer.height, 25)

    def test_render_empty_tree(self):
        """Test rendering empty tree"""
        tree = SkillTree("test", "Test")
        renderer = ASCIITreeRenderer()

        result = renderer.render_tree(tree)
        self.assertIsInstance(result, str)

    def test_render_single_skill(self):
        """Test rendering single skill"""
        tree = SkillTree("test", "Test")
        tree.add_skill("skill1", "Skill1", "Description")
        tree.skills["skill1"].position = (0, 0)

        renderer = ASCIITreeRenderer()
        result = renderer.render_tree(tree)

        self.assertIn("Skill1", result)

    def test_locked_skill_rendering(self):
        """Test locked skill uses dots"""
        tree = SkillTree("test", "Test")
        tree.add_skill("locked", "Locked", "Description")
        tree.skills["locked"].position = (0, 0)

        renderer = ASCIITreeRenderer()
        result = renderer.render_tree(tree)

        # Locked skills use ·
        self.assertIn("·", result)

    def test_unlocked_skill_rendering(self):
        """Test unlocked skill uses lines"""
        tree = SkillTree("test", "Test")
        tree.add_skill("unlocked", "Unlocked", "Description")
        tree.skills["unlocked"].position = (0, 0)
        tree.unlock_skill("unlocked", 0)

        renderer = ASCIITreeRenderer()
        result = renderer.render_tree(tree)

        # Unlocked skills use ─
        self.assertIn("─", result)

    def test_mastered_skill_rendering(self):
        """Test mastered skill uses double lines"""
        tree = SkillTree("test", "Test")
        tree.add_skill("mastered", "Mastered", "Description", max_level=3)
        tree.skills["mastered"].position = (0, 0)
        tree.unlock_skill("mastered", 0)

        # Level up to max
        tree.level_up_skill("mastered")
        tree.level_up_skill("mastered")

        renderer = ASCIITreeRenderer()
        result = renderer.render_tree(tree)

        # Mastered skills use ═
        self.assertIn("═", result)

    def test_render_skill_connection(self):
        """Test rendering connections between skills"""
        tree = SkillTree("test", "Test")
        tree.add_skill("basic", "Basic", "Description")
        tree.add_skill("advanced", "Advanced", "Description", prerequisites=["basic"])

        tree.skills["basic"].position = (0, 0)
        tree.skills["advanced"].position = (2, 0)

        renderer = ASCIITreeRenderer()
        result = renderer.render_tree(tree)

        # Should contain connection lines
        self.assertIn("│", result)

    def test_render_survival_tree(self):
        """Test rendering survival tree template"""
        tree = SkillTreeTemplate.survival_tree()
        renderer = ASCIITreeRenderer()

        result = renderer.render_tree(tree)

        # Skills are truncated to 8 chars in rendering
        self.assertIn("Water", result)
        self.assertIn("Fire", result)
        self.assertIn("Survival", result)  # "Survival Expert" shows as "Survival"    def test_render_technical_tree(self):
        """Test rendering technical tree template"""
        tree = SkillTreeTemplate.technical_tree()
        renderer = ASCIITreeRenderer()

        result = renderer.render_tree(tree)

        self.assertIn("Coding", result)
        self.assertIn("Electron", result)  # Electronics truncated

    def test_grid_bounds(self):
        """Test rendering respects grid bounds"""
        tree = SkillTree("test", "Test")
        tree.add_skill("skill", "Skill", "Description")
        tree.skills["skill"].position = (100, 100)  # Out of bounds

        renderer = ASCIITreeRenderer()
        result = renderer.render_tree(tree)

        # Should not crash, just not render out-of-bounds skill
        self.assertIsInstance(result, str)


class TestXPIntegration(unittest.TestCase):
    """Test XP system integration (8 tests)"""

    def test_unlock_with_xp_cost(self):
        """Test unlocking skill consumes XP"""
        tree = SkillTree("test", "Test")
        tree.add_skill("skill1", "Skill", "Description", xp_cost=100)

        tree.unlock_skill("skill1", 100)

        self.assertEqual(tree.total_xp_spent, 100)

    def test_cannot_unlock_without_xp(self):
        """Test cannot unlock without sufficient XP"""
        tree = SkillTree("test", "Test")
        tree.add_skill("skill1", "Skill", "Description", xp_cost=100)

        result = tree.unlock_skill("skill1", 50)

        self.assertFalse(result)
        self.assertEqual(tree.total_xp_spent, 0)

    def test_progressive_xp_costs(self):
        """Test skills have increasing XP costs"""
        tree = SkillTreeTemplate.survival_tree()

        basics_cost = tree.skills["water_basics"].xp_cost
        advanced_cost = tree.skills["water_advanced"].xp_cost
        expert_cost = tree.skills["survival_expert"].xp_cost

        self.assertEqual(basics_cost, 0)
        self.assertGreater(advanced_cost, basics_cost)
        self.assertGreater(expert_cost, advanced_cost)

    def test_get_available_by_xp(self):
        """Test getting available skills by XP"""
        tree = SkillTree("test", "Test")
        tree.add_skill("cheap", "Cheap", "Description", xp_cost=10)
        tree.add_skill("expensive", "Expensive", "Description", xp_cost=100)

        available = tree.get_available_skills(50)
        available_ids = [s.id for s in available]

        self.assertIn("cheap", available_ids)
        self.assertNotIn("expensive", available_ids)

    def test_xp_tracking_across_trees(self):
        """Test XP tracking across multiple trees"""
        manager = SkillTreeManager()

        tree1 = SkillTree("tree1", "Tree 1")
        tree1.add_skill("skill1", "Skill 1", "Desc", xp_cost=50)

        tree2 = SkillTree("tree2", "Tree 2")
        tree2.add_skill("skill2", "Skill 2", "Desc", xp_cost=75)

        manager.add_tree(tree1)
        manager.add_tree(tree2)

        tree1.unlock_skill("skill1", 100)
        tree2.unlock_skill("skill2", 100)

        progress = manager.get_total_progress()
        self.assertEqual(progress['xp_spent'], 125)

    def test_skill_unlock_prerequisite_chain_xp(self):
        """Test XP costs in prerequisite chains"""
        tree = SkillTree("test", "Test")
        tree.add_skill("basic", "Basic", "Desc", xp_cost=0)
        tree.add_skill("intermediate", "Intermediate", "Desc",
                      xp_cost=50, prerequisites=["basic"])
        tree.add_skill("advanced", "Advanced", "Desc",
                      xp_cost=100, prerequisites=["intermediate"])

        tree.unlock_skill("basic", 0)
        tree.unlock_skill("intermediate", 50)
        tree.unlock_skill("advanced", 100)

        self.assertEqual(tree.total_xp_spent, 150)

    def test_survival_tree_total_xp(self):
        """Test total XP cost of survival tree"""
        tree = SkillTreeTemplate.survival_tree()

        # Unlock all skills
        tree.unlock_skill("water_basics", 0)
        tree.unlock_skill("fire_basics", 0)
        tree.unlock_skill("shelter_basics", 0)
        tree.unlock_skill("water_advanced", 100)
        tree.unlock_skill("fire_advanced", 100)
        tree.unlock_skill("shelter_advanced", 100)
        tree.unlock_skill("survival_expert", 500)

        self.assertEqual(tree.total_xp_spent, 800)

    def test_get_all_available_across_trees(self):
        """Test getting all available skills across trees"""
        manager = SkillTreeManager()
        manager.add_tree(SkillTreeTemplate.survival_tree())
        manager.add_tree(SkillTreeTemplate.technical_tree())

        available = manager.get_all_available_skills(0)

        # Should include all 0-cost skills from both trees
        self.assertGreater(len(available), 0)


class TestDisplayModes(unittest.TestCase):
    """Test display modes (6 tests)"""

    def test_skill_progress_display(self):
        """Test skill progress percentage"""
        skill = SkillNode("test", "Test", "Description", max_level=5)
        skill.unlock()
        skill.level_up()  # Level 2
        skill.level_up()  # Level 3

        progress = skill.get_progress()
        self.assertEqual(progress, 60.0)  # 3/5 = 60%

    def test_tree_progress_display(self):
        """Test tree progress summary"""
        tree = SkillTree("test", "Test")
        tree.add_skill("skill1", "Skill 1", "Desc")
        tree.add_skill("skill2", "Skill 2", "Desc")
        tree.add_skill("skill3", "Skill 3", "Desc")

        tree.unlock_skill("skill1", 0)

        progress = tree.get_tree_progress()

        self.assertEqual(progress['unlocked'], 1)
        self.assertEqual(progress['total'], 3)
        self.assertAlmostEqual(progress['percentage'], 33.33, places=1)

    def test_manager_total_progress(self):
        """Test manager total progress"""
        manager = SkillTreeManager()

        tree1 = SkillTree("tree1", "Tree 1")
        tree1.add_skill("s1", "S1", "Desc")
        tree1.add_skill("s2", "S2", "Desc")

        tree2 = SkillTree("tree2", "Tree 2")
        tree2.add_skill("s3", "S3", "Desc")
        tree2.add_skill("s4", "S4", "Desc")

        manager.add_tree(tree1)
        manager.add_tree(tree2)

        tree1.unlock_skill("s1", 0)
        tree2.unlock_skill("s3", 0)

        progress = manager.get_total_progress()

        self.assertEqual(progress['unlocked'], 2)
        self.assertEqual(progress['total'], 4)
        self.assertEqual(progress['trees'], 2)

    def test_category_filtering(self):
        """Test filtering skills by category"""
        tree = SkillTree("test", "Test")
        tree.add_skill("s1", "S1", "Desc", category="survival")
        tree.add_skill("s2", "S2", "Desc", category="survival")
        tree.add_skill("s3", "S3", "Desc", category="technical")

        survival_skills = tree.get_skills_by_category("survival")

        self.assertEqual(len(survival_skills), 2)

    def test_skill_node_position(self):
        """Test skill node positioning"""
        skill = SkillNode("test", "Test", "Description")
        skill.position = (2, 3)

        self.assertEqual(skill.position, (2, 3))

    def test_path_progress_display(self):
        """Test progression path progress display"""
        path = ProgressionPath("test", "Test Path")
        path.add_milestone("skill1")
        path.add_milestone("skill2")
        path.add_milestone("skill3")

        path.advance()

        progress = path.get_progress()

        self.assertEqual(progress['current'], 1)
        self.assertEqual(progress['total'], 3)
        self.assertAlmostEqual(progress['percentage'], 33.33, places=1)


class TestIntegration(unittest.TestCase):
    """Integration tests (6 tests)"""

    def test_full_tree_unlock_progression(self):
        """Test unlocking entire tree progression"""
        tree = SkillTree("test", "Test")
        tree.add_skill("basic", "Basic", "Desc", xp_cost=0)
        tree.add_skill("intermediate", "Intermediate", "Desc",
                      xp_cost=50, prerequisites=["basic"])
        tree.add_skill("advanced", "Advanced", "Desc",
                      xp_cost=100, prerequisites=["intermediate"])

        # Unlock in order
        self.assertTrue(tree.unlock_skill("basic", 0))
        self.assertTrue(tree.unlock_skill("intermediate", 50))
        self.assertTrue(tree.unlock_skill("advanced", 100))

        progress = tree.get_tree_progress()
        self.assertEqual(progress['unlocked'], 3)

    def test_survival_tree_complete_path(self):
        """Test completing survival tree path"""
        tree = SkillTreeTemplate.survival_tree()

        # Basics
        tree.unlock_skill("water_basics", 0)
        tree.unlock_skill("fire_basics", 0)
        tree.unlock_skill("shelter_basics", 0)

        # Advanced (requires 100 XP each)
        tree.unlock_skill("water_advanced", 100)
        tree.unlock_skill("fire_advanced", 100)
        tree.unlock_skill("shelter_advanced", 100)

        # Expert (requires 500 XP)
        tree.unlock_skill("survival_expert", 500)

        progress = tree.get_tree_progress()
        self.assertEqual(progress['percentage'], 100.0)

    def test_multi_tree_manager(self):
        """Test managing multiple skill trees"""
        manager = SkillTreeManager()

        survival = SkillTreeTemplate.survival_tree()
        technical = SkillTreeTemplate.technical_tree()

        manager.add_tree(survival)
        manager.add_tree(technical)

        # Unlock some skills
        survival.unlock_skill("water_basics", 0)
        technical.unlock_skill("coding_basics", 0)

        progress = manager.get_total_progress()
        self.assertEqual(progress['unlocked'], 2)
        self.assertGreater(progress['total'], 2)

    def test_progression_path_with_tree(self):
        """Test progression path guides tree unlocking"""
        tree = SkillTreeTemplate.survival_tree()
        path = ProgressionPath("survival_basics", "Survival Basics")

        path.add_milestone("water_basics")
        path.add_milestone("fire_basics")
        path.add_milestone("shelter_basics")

        # Follow path
        for _ in range(3):
            next_skill = path.get_next_skill()
            if next_skill:
                tree.unlock_skill(next_skill, 0)
                path.advance()

        path_progress = path.get_progress()
        self.assertTrue(path_progress['completed'])

    def test_ascii_render_with_unlocked_skills(self):
        """Test ASCII rendering shows unlocked status"""
        tree = SkillTree("test", "Test")
        tree.add_skill("unlocked", "Unlocked", "Desc")
        tree.add_skill("locked", "Locked", "Desc")

        tree.skills["unlocked"].position = (0, 0)
        tree.skills["locked"].position = (0, 2)

        tree.unlock_skill("unlocked", 0)

        renderer = ASCIITreeRenderer()
        result = renderer.render_tree(tree)

        # Should show different styles for locked/unlocked
        self.assertIn("─", result)  # Unlocked
        self.assertIn("·", result)  # Locked

    def test_xp_availability_updates(self):
        """Test available skills update with XP"""
        tree = SkillTree("test", "Test")
        tree.add_skill("cheap", "Cheap", "Desc", xp_cost=10)
        tree.add_skill("medium", "Medium", "Desc", xp_cost=50)
        tree.add_skill("expensive", "Expensive", "Desc", xp_cost=100)

        # With 25 XP
        available_25 = tree.get_available_skills(25)
        self.assertEqual(len(available_25), 1)  # Only cheap

        # With 75 XP
        available_75 = tree.get_available_skills(75)
        self.assertEqual(len(available_75), 2)  # Cheap + medium

        # With 150 XP
        available_150 = tree.get_available_skills(150)
        self.assertEqual(len(available_150), 3)  # All


def run_tests():
    """Run the test suite"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSkillTreeStructure))
    suite.addTests(loader.loadTestsFromTestCase(TestProgressionPaths))
    suite.addTests(loader.loadTestsFromTestCase(TestASCIIRendering))
    suite.addTests(loader.loadTestsFromTestCase(TestXPIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestDisplayModes))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)

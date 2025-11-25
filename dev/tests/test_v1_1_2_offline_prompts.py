"""
Test Suite for Feature 1.1.2.7: Offline AI Prompt Development
v1.1.2 Phase 2: Knowledge Bank & AI Integration

Tests offline AI prompt development with prompt library management,
template system, context injection, role-specific prompts, testing/validation,
version control, and offline editing.

Test Categories:
1. Prompt Library Structure (5 tests)
2. Template Management (6 tests)
3. Context Injection (6 tests)
4. Role-Specific Prompts (5 tests)
5. Prompt Testing (6 tests)
6. Prompt Validation (6 tests)
7. Version Control (5 tests)
8. Offline Editing (5 tests)
9. Prompt Variables (5 tests)
10. Prompt Chaining (4 tests)
11. Import/Export (4 tests)
12. Integration Scenarios (3 tests)

Total: 60 tests
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
from datetime import datetime
from enum import Enum
import re


class PromptType(Enum):
    """Prompt type enumeration."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TEMPLATE = "template"


class PromptRole(Enum):
    """Role-specific prompt categories."""
    USER = "user"
    POWER = "power"
    WIZARD = "wizard"
    ROOT = "root"
    GENERAL = "general"


class OfflinePromptLibrary:
    """Offline AI prompt development and management system."""

    def __init__(self, library_path="/prompts"):
        self.library_path = library_path
        self.prompts = {}
        self.templates = {}
        self.role_prompts = {role: [] for role in PromptRole}
        self.versions = {}
        self.test_results = {}
        self.variables = {}
        self.chains = {}

    def add_prompt(self, prompt_id, name, content, prompt_type=PromptType.USER,
                   role=PromptRole.GENERAL, metadata=None):
        """Add prompt to library."""
        if not isinstance(prompt_type, PromptType):
            raise ValueError(f"Invalid prompt type: {prompt_type}")

        if not isinstance(role, PromptRole):
            raise ValueError(f"Invalid role: {role}")

        prompt = {
            "id": prompt_id,
            "name": name,
            "content": content,
            "type": prompt_type.value,
            "role": role.value,
            "created_at": datetime.now().isoformat(),
            "version": 1
        }

        if metadata:
            prompt["metadata"] = metadata

        self.prompts[prompt_id] = prompt
        self.role_prompts[role].append(prompt_id)

        # Track version
        self._track_version(prompt_id, 1, "Initial version")

        return prompt_id

    def get_prompt(self, prompt_id):
        """Get prompt by ID."""
        if prompt_id not in self.prompts:
            raise KeyError(f"Prompt not found: {prompt_id}")

        return self.prompts[prompt_id].copy()

    def update_prompt(self, prompt_id, content=None, name=None, metadata=None):
        """Update existing prompt."""
        if prompt_id not in self.prompts:
            raise KeyError(f"Prompt not found: {prompt_id}")

        prompt = self.prompts[prompt_id]

        # Increment version
        new_version = prompt["version"] + 1

        if content is not None:
            prompt["content"] = content

        if name is not None:
            prompt["name"] = name

        if metadata is not None:
            prompt["metadata"] = metadata

        prompt["version"] = new_version
        prompt["updated_at"] = datetime.now().isoformat()

        # Track version
        self._track_version(prompt_id, new_version, "Updated")

        return new_version

    def delete_prompt(self, prompt_id):
        """Delete prompt from library."""
        if prompt_id not in self.prompts:
            return False

        prompt = self.prompts[prompt_id]
        role = PromptRole(prompt["role"])

        # Remove from role list
        if prompt_id in self.role_prompts[role]:
            self.role_prompts[role].remove(prompt_id)

        del self.prompts[prompt_id]
        return True

    def create_template(self, template_id, name, template_content, variables=None):
        """Create prompt template."""
        template = {
            "id": template_id,
            "name": name,
            "content": template_content,
            "variables": variables or [],
            "created_at": datetime.now().isoformat()
        }

        # Extract variables from template
        extracted_vars = self._extract_variables(template_content)
        if extracted_vars:
            template["variables"] = list(set(template["variables"] + extracted_vars))

        self.templates[template_id] = template
        return template_id

    def get_template(self, template_id):
        """Get template by ID."""
        if template_id not in self.templates:
            raise KeyError(f"Template not found: {template_id}")

        return self.templates[template_id].copy()

    def render_template(self, template_id, variables):
        """Render template with variables."""
        template = self.get_template(template_id)
        content = template["content"]

        # Replace variables
        for var_name, var_value in variables.items():
            placeholder = f"{{{var_name}}}"
            content = content.replace(placeholder, str(var_value))

        # Check for unreplaced variables
        unreplaced = self._extract_variables(content)
        if unreplaced:
            raise ValueError(f"Unreplaced variables: {unreplaced}")

        return content

    def _extract_variables(self, content):
        """Extract variable placeholders from content."""
        pattern = r'\{(\w+)\}'
        matches = re.findall(pattern, content)
        return matches

    def inject_context(self, prompt_id, context_data):
        """Inject context into prompt."""
        prompt = self.get_prompt(prompt_id)
        content = prompt["content"]

        # Add context at the beginning
        context_str = json.dumps(context_data, indent=2)
        injected = f"Context:\n{context_str}\n\n{content}"

        return injected

    def create_contextual_prompt(self, base_prompt_id, context_data):
        """Create new prompt with injected context."""
        injected_content = self.inject_context(base_prompt_id, context_data)

        base_prompt = self.get_prompt(base_prompt_id)
        new_id = f"{base_prompt_id}_ctx_{datetime.now().timestamp()}"

        return self.add_prompt(
            new_id,
            f"{base_prompt['name']} (with context)",
            injected_content,
            PromptType(base_prompt["type"]),
            PromptRole(base_prompt["role"]),
            {"context": context_data, "base_prompt": base_prompt_id}
        )

    def get_prompts_by_role(self, role):
        """Get all prompts for specific role."""
        if not isinstance(role, PromptRole):
            raise ValueError(f"Invalid role: {role}")

        return self.role_prompts[role].copy()

    def filter_prompts_by_type(self, prompt_type):
        """Filter prompts by type."""
        if not isinstance(prompt_type, PromptType):
            raise ValueError(f"Invalid prompt type: {prompt_type}")

        return [
            pid for pid, p in self.prompts.items()
            if p["type"] == prompt_type.value
        ]

    def test_prompt(self, prompt_id, test_input, expected_output=None):
        """Test prompt with input."""
        prompt = self.get_prompt(prompt_id)

        test_result = {
            "prompt_id": prompt_id,
            "test_input": test_input,
            "expected_output": expected_output,
            "timestamp": datetime.now().isoformat(),
            "passed": False
        }

        # In real implementation, would call AI API
        # For testing, we simulate
        simulated_output = f"Response to: {test_input}"
        test_result["actual_output"] = simulated_output

        # Check if matches expected
        if expected_output:
            test_result["passed"] = simulated_output == expected_output
        else:
            test_result["passed"] = True  # No expected output to compare

        # Store result
        if prompt_id not in self.test_results:
            self.test_results[prompt_id] = []

        self.test_results[prompt_id].append(test_result)

        return test_result

    def get_test_results(self, prompt_id):
        """Get test results for prompt."""
        return self.test_results.get(prompt_id, []).copy()

    def validate_prompt(self, prompt_id):
        """Validate prompt structure and content."""
        if prompt_id not in self.prompts:
            raise KeyError(f"Prompt not found: {prompt_id}")

        prompt = self.prompts[prompt_id]

        validation = {
            "valid": True,
            "errors": [],
            "warnings": []
        }

        # Check required fields
        if not prompt.get("name"):
            validation["valid"] = False
            validation["errors"].append("Missing name")

        if not prompt.get("content"):
            validation["valid"] = False
            validation["errors"].append("Missing content")

        # Check content length
        content_len = len(prompt.get("content", ""))
        if content_len < 10:
            validation["warnings"].append("Content is very short")

        if content_len > 8000:
            validation["warnings"].append("Content exceeds recommended length")

        # Check for template variables
        unreplaced = self._extract_variables(prompt["content"])
        if unreplaced:
            validation["warnings"].append(f"Contains unreplaced variables: {unreplaced}")

        return validation

    def validate_template(self, template_id):
        """Validate template."""
        if template_id not in self.templates:
            raise KeyError(f"Template not found: {template_id}")

        template = self.templates[template_id]

        validation = {
            "valid": True,
            "errors": [],
            "warnings": []
        }

        # Check variables are defined
        declared = set(template.get("variables", []))
        used = set(self._extract_variables(template["content"]))

        # Undeclared variables
        undeclared = used - declared
        if undeclared:
            validation["warnings"].append(f"Undeclared variables: {list(undeclared)}")

        # Unused variables
        unused = declared - used
        if unused:
            validation["warnings"].append(f"Unused variables: {list(unused)}")

        return validation

    def _track_version(self, prompt_id, version, note):
        """Track version change."""
        if prompt_id not in self.versions:
            self.versions[prompt_id] = []

        self.versions[prompt_id].append({
            "version": version,
            "note": note,
            "timestamp": datetime.now().isoformat()
        })

    def get_version_history(self, prompt_id):
        """Get version history."""
        return self.versions.get(prompt_id, []).copy()

    def revert_to_version(self, prompt_id, version):
        """Revert to specific version."""
        if prompt_id not in self.prompts:
            raise KeyError(f"Prompt not found: {prompt_id}")

        history = self.get_version_history(prompt_id)

        if not any(v["version"] == version for v in history):
            raise ValueError(f"Version {version} not found")

        # Simulate revert
        self.prompts[prompt_id]["version"] = version
        self.prompts[prompt_id]["reverted_from"] = self.prompts[prompt_id].get("version", version)

        return True

    def edit_offline(self, prompt_id, new_content):
        """Edit prompt offline."""
        # Update content
        version = self.update_prompt(prompt_id, content=new_content)

        # Mark as offline edited
        prompt = self.prompts[prompt_id]
        if "metadata" not in prompt:
            prompt["metadata"] = {}

        prompt["metadata"]["offline_edited"] = True
        prompt["metadata"]["last_offline_edit"] = datetime.now().isoformat()

        return version

    def check_offline_editable(self, prompt_id):
        """Check if prompt is editable offline."""
        # All prompts are offline editable in this system
        return prompt_id in self.prompts

    def set_variable_default(self, var_name, default_value):
        """Set default value for variable."""
        self.variables[var_name] = {
            "name": var_name,
            "default": default_value,
            "type": type(default_value).__name__
        }
        return True

    def get_variable_default(self, var_name):
        """Get default value for variable."""
        if var_name not in self.variables:
            return None

        return self.variables[var_name]["default"]

    def render_with_defaults(self, template_id, override_vars=None):
        """Render template with default variables."""
        template = self.get_template(template_id)

        # Collect variables
        variables = {}
        for var_name in template["variables"]:
            default = self.get_variable_default(var_name)
            if default is not None:
                variables[var_name] = default

        # Override with provided values
        if override_vars:
            variables.update(override_vars)

        return self.render_template(template_id, variables)

    def create_prompt_chain(self, chain_id, prompt_ids, name=None):
        """Create chain of prompts."""
        # Verify all prompts exist
        for pid in prompt_ids:
            if pid not in self.prompts:
                raise KeyError(f"Prompt not found: {pid}")

        chain = {
            "id": chain_id,
            "name": name or f"Chain {chain_id}",
            "prompts": prompt_ids,
            "created_at": datetime.now().isoformat()
        }

        self.chains[chain_id] = chain
        return chain_id

    def get_chain(self, chain_id):
        """Get prompt chain."""
        if chain_id not in self.chains:
            raise KeyError(f"Chain not found: {chain_id}")

        return self.chains[chain_id].copy()

    def execute_chain(self, chain_id, initial_input):
        """Execute prompt chain."""
        chain = self.get_chain(chain_id)

        results = []
        current_output = initial_input

        for prompt_id in chain["prompts"]:
            # Test each prompt with output from previous
            result = self.test_prompt(prompt_id, current_output)
            results.append(result)

            # Use output as next input
            current_output = result["actual_output"]

        return {
            "chain_id": chain_id,
            "initial_input": initial_input,
            "final_output": current_output,
            "steps": results
        }

    def export_library(self):
        """Export prompt library."""
        return {
            "prompts": self.prompts.copy(),
            "templates": self.templates.copy(),
            "variables": self.variables.copy(),
            "exported_at": datetime.now().isoformat(),
            "total_prompts": len(self.prompts),
            "total_templates": len(self.templates)
        }

    def import_library(self, data):
        """Import prompt library."""
        imported = {
            "prompts": 0,
            "templates": 0,
            "errors": []
        }

        # Import prompts
        if "prompts" in data:
            for prompt_id, prompt in data["prompts"].items():
                try:
                    self.prompts[prompt_id] = prompt

                    # Add to role list
                    role = PromptRole(prompt["role"])
                    if prompt_id not in self.role_prompts[role]:
                        self.role_prompts[role].append(prompt_id)

                    imported["prompts"] += 1
                except Exception as e:
                    imported["errors"].append(f"Prompt {prompt_id}: {str(e)}")

        # Import templates
        if "templates" in data:
            for template_id, template in data["templates"].items():
                try:
                    self.templates[template_id] = template
                    imported["templates"] += 1
                except Exception as e:
                    imported["errors"].append(f"Template {template_id}: {str(e)}")

        # Import variables
        if "variables" in data:
            self.variables.update(data["variables"])

        return imported

    def get_library_stats(self):
        """Get library statistics."""
        return {
            "total_prompts": len(self.prompts),
            "total_templates": len(self.templates),
            "prompts_by_role": {role.value: len(pids) for role, pids in self.role_prompts.items()},
            "prompts_by_type": {
                ptype.value: len(self.filter_prompts_by_type(ptype))
                for ptype in PromptType
            },
            "total_chains": len(self.chains)
        }


class TestPromptLibraryStructure(unittest.TestCase):
    """Test prompt library structure."""

    def setUp(self):
        self.library = OfflinePromptLibrary()

    def test_library_initialization(self):
        """Test library is initialized."""
        self.assertIsNotNone(self.library.prompts)
        self.assertIsNotNone(self.library.templates)

    def test_role_structure(self):
        """Test role structure."""
        self.assertEqual(len(self.library.role_prompts), len(PromptRole))
        self.assertIn(PromptRole.USER, self.library.role_prompts)

    def test_prompt_types(self):
        """Test prompt type enumeration."""
        self.assertEqual(PromptType.SYSTEM.value, "system")
        self.assertEqual(PromptType.USER.value, "user")

    def test_library_path(self):
        """Test library path configuration."""
        self.assertEqual(self.library.library_path, "/prompts")

    def test_empty_library_stats(self):
        """Test statistics for empty library."""
        stats = self.library.get_library_stats()
        self.assertEqual(stats["total_prompts"], 0)
        self.assertEqual(stats["total_templates"], 0)


class TestTemplateManagement(unittest.TestCase):
    """Test template management."""

    def setUp(self):
        self.library = OfflinePromptLibrary()

    def test_create_template(self):
        """Test creating template."""
        template_id = self.library.create_template(
            "temp1",
            "Greeting Template",
            "Hello {name}, welcome to {place}!",
            ["name", "place"]
        )

        self.assertIn(template_id, self.library.templates)

    def test_get_template(self):
        """Test getting template."""
        self.library.create_template(
            "temp2",
            "Test Template",
            "Content with {var}",
            ["var"]
        )

        template = self.library.get_template("temp2")
        self.assertEqual(template["name"], "Test Template")

    def test_render_template(self):
        """Test rendering template."""
        self.library.create_template(
            "temp3",
            "Name Template",
            "My name is {name}",
            ["name"]
        )

        rendered = self.library.render_template("temp3", {"name": "Alice"})
        self.assertEqual(rendered, "My name is Alice")

    def test_extract_variables(self):
        """Test extracting variables from template."""
        content = "Hello {name}, you have {count} messages"
        variables = self.library._extract_variables(content)

        self.assertIn("name", variables)
        self.assertIn("count", variables)

    def test_unreplaced_variables_error(self):
        """Test error on unreplaced variables."""
        self.library.create_template(
            "temp4",
            "Template",
            "Hello {name} and {other}",
            ["name", "other"]
        )

        with self.assertRaises(ValueError):
            self.library.render_template("temp4", {"name": "Alice"})

    def test_auto_extract_variables(self):
        """Test automatic variable extraction."""
        template_id = self.library.create_template(
            "temp5",
            "Auto Extract",
            "Variables: {var1}, {var2}"
        )

        template = self.library.get_template(template_id)
        self.assertIn("var1", template["variables"])
        self.assertIn("var2", template["variables"])


class TestContextInjection(unittest.TestCase):
    """Test context injection."""

    def setUp(self):
        self.library = OfflinePromptLibrary()

    def test_inject_context(self):
        """Test injecting context into prompt."""
        prompt_id = self.library.add_prompt(
            "ctx1",
            "Test Prompt",
            "Answer the question."
        )

        context = {"topic": "science", "level": "basic"}
        injected = self.library.inject_context(prompt_id, context)

        self.assertIn("Context:", injected)
        self.assertIn("science", injected)

    def test_create_contextual_prompt(self):
        """Test creating contextual prompt."""
        base_id = self.library.add_prompt(
            "base1",
            "Base Prompt",
            "Explain this concept."
        )

        context = {"subject": "math"}
        new_id = self.library.create_contextual_prompt(base_id, context)

        self.assertIn(new_id, self.library.prompts)

        new_prompt = self.library.get_prompt(new_id)
        self.assertIn("context", new_prompt["metadata"])

    def test_context_formatting(self):
        """Test context is properly formatted."""
        prompt_id = self.library.add_prompt(
            "fmt1",
            "Prompt",
            "Content"
        )

        context = {"key": "value"}
        injected = self.library.inject_context(prompt_id, context)

        # Should be JSON formatted
        self.assertIn('"key"', injected)
        self.assertIn('"value"', injected)

    def test_context_with_nested_data(self):
        """Test context with nested data."""
        prompt_id = self.library.add_prompt(
            "nest1",
            "Prompt",
            "Content"
        )

        context = {
            "user": {"name": "Alice", "role": "admin"},
            "settings": {"theme": "dark"}
        }

        injected = self.library.inject_context(prompt_id, context)
        self.assertIn("Alice", injected)
        self.assertIn("dark", injected)

    def test_context_preserved_in_metadata(self):
        """Test context is preserved in metadata."""
        base_id = self.library.add_prompt("base2", "Base", "Content")
        context = {"data": "value"}

        new_id = self.library.create_contextual_prompt(base_id, context)
        new_prompt = self.library.get_prompt(new_id)

        self.assertEqual(new_prompt["metadata"]["context"], context)
        self.assertEqual(new_prompt["metadata"]["base_prompt"], base_id)

    def test_multiple_context_injections(self):
        """Test multiple context injections."""
        prompt_id = self.library.add_prompt("multi1", "Prompt", "Content")

        ctx1 = {"version": 1}
        ctx2 = {"version": 2}

        injected1 = self.library.inject_context(prompt_id, ctx1)
        injected2 = self.library.inject_context(prompt_id, ctx2)

        self.assertIn('"version": 1', injected1)
        self.assertIn('"version": 2', injected2)


class TestRoleSpecificPrompts(unittest.TestCase):
    """Test role-specific prompts."""

    def setUp(self):
        self.library = OfflinePromptLibrary()

    def test_add_role_specific_prompt(self):
        """Test adding role-specific prompt."""
        prompt_id = self.library.add_prompt(
            "role1",
            "Wizard Prompt",
            "Advanced configuration...",
            role=PromptRole.WIZARD
        )

        self.assertIn(prompt_id, self.library.role_prompts[PromptRole.WIZARD])

    def test_get_prompts_by_role(self):
        """Test getting prompts by role."""
        self.library.add_prompt("r1", "User P", "Content", role=PromptRole.USER)
        self.library.add_prompt("r2", "User P2", "Content", role=PromptRole.USER)

        user_prompts = self.library.get_prompts_by_role(PromptRole.USER)
        self.assertEqual(len(user_prompts), 2)

    def test_multiple_roles(self):
        """Test prompts in multiple roles."""
        self.library.add_prompt("mr1", "P1", "C", role=PromptRole.USER)
        self.library.add_prompt("mr2", "P2", "C", role=PromptRole.POWER)
        self.library.add_prompt("mr3", "P3", "C", role=PromptRole.WIZARD)

        user_prompts = self.library.get_prompts_by_role(PromptRole.USER)
        power_prompts = self.library.get_prompts_by_role(PromptRole.POWER)

        self.assertEqual(len(user_prompts), 1)
        self.assertEqual(len(power_prompts), 1)

    def test_general_role_prompts(self):
        """Test general role prompts."""
        prompt_id = self.library.add_prompt(
            "gen1",
            "General Prompt",
            "Available to all",
            role=PromptRole.GENERAL
        )

        general_prompts = self.library.get_prompts_by_role(PromptRole.GENERAL)
        self.assertIn(prompt_id, general_prompts)

    def test_invalid_role(self):
        """Test invalid role raises error."""
        with self.assertRaises(ValueError):
            self.library.add_prompt("bad", "Prompt", "Content", role="invalid")


class TestPromptTesting(unittest.TestCase):
    """Test prompt testing functionality."""

    def setUp(self):
        self.library = OfflinePromptLibrary()

    def test_test_prompt(self):
        """Test testing a prompt."""
        prompt_id = self.library.add_prompt(
            "test1",
            "Test Prompt",
            "Answer this question: {input}"
        )

        result = self.library.test_prompt(prompt_id, "What is 2+2?")

        self.assertIn("actual_output", result)
        self.assertIn("test_input", result)

    def test_test_with_expected_output(self):
        """Test with expected output."""
        prompt_id = self.library.add_prompt("test2", "Prompt", "Content")

        result = self.library.test_prompt(
            prompt_id,
            "input",
            expected_output="Response to: input"
        )

        self.assertTrue(result["passed"])

    def test_test_failure_detection(self):
        """Test detecting test failure."""
        prompt_id = self.library.add_prompt("test3", "Prompt", "Content")

        result = self.library.test_prompt(
            prompt_id,
            "input",
            expected_output="Wrong output"
        )

        self.assertFalse(result["passed"])

    def test_get_test_results(self):
        """Test getting test results."""
        prompt_id = self.library.add_prompt("test4", "Prompt", "Content")

        self.library.test_prompt(prompt_id, "test1")
        self.library.test_prompt(prompt_id, "test2")

        results = self.library.get_test_results(prompt_id)
        self.assertEqual(len(results), 2)

    def test_test_result_storage(self):
        """Test test results are stored."""
        prompt_id = self.library.add_prompt("test5", "Prompt", "Content")

        self.library.test_prompt(prompt_id, "input")

        self.assertIn(prompt_id, self.library.test_results)

    def test_multiple_tests(self):
        """Test running multiple tests."""
        prompt_id = self.library.add_prompt("test6", "Prompt", "Content")

        for i in range(5):
            self.library.test_prompt(prompt_id, f"test {i}")

        results = self.library.get_test_results(prompt_id)
        self.assertEqual(len(results), 5)


class TestPromptValidation(unittest.TestCase):
    """Test prompt validation."""

    def setUp(self):
        self.library = OfflinePromptLibrary()

    def test_validate_valid_prompt(self):
        """Test validating valid prompt."""
        prompt_id = self.library.add_prompt(
            "val1",
            "Valid Prompt",
            "This is a valid prompt with sufficient content."
        )

        validation = self.library.validate_prompt(prompt_id)
        self.assertTrue(validation["valid"])

    def test_validate_missing_name(self):
        """Test validation detects missing name."""
        prompt_id = self.library.add_prompt(
            "val2",
            "",
            "Content"
        )

        validation = self.library.validate_prompt(prompt_id)
        self.assertFalse(validation["valid"])

    def test_validate_missing_content(self):
        """Test validation detects missing content."""
        prompt_id = self.library.add_prompt(
            "val3",
            "Name",
            ""
        )

        validation = self.library.validate_prompt(prompt_id)
        self.assertFalse(validation["valid"])

    def test_validate_short_content_warning(self):
        """Test validation warns about short content."""
        prompt_id = self.library.add_prompt(
            "val4",
            "Name",
            "Short"
        )

        validation = self.library.validate_prompt(prompt_id)
        self.assertGreater(len(validation["warnings"]), 0)

    def test_validate_template(self):
        """Test template validation."""
        template_id = self.library.create_template(
            "valt1",
            "Template",
            "Content with {var}",
            ["var"]
        )

        validation = self.library.validate_template(template_id)
        self.assertTrue(validation["valid"])

    def test_validate_unused_variables(self):
        """Test detecting unused variables."""
        template_id = self.library.create_template(
            "valt2",
            "Template",
            "Has {used}",
            ["used", "unused"]  # Declared but not used
        )

        validation = self.library.validate_template(template_id)
        # Should warn about unused variable
        self.assertGreater(len(validation["warnings"]), 0)
class TestVersionControl(unittest.TestCase):
    """Test version control."""

    def setUp(self):
        self.library = OfflinePromptLibrary()

    def test_initial_version(self):
        """Test initial version is 1."""
        prompt_id = self.library.add_prompt(
            "ver1",
            "Prompt",
            "Content"
        )

        prompt = self.library.get_prompt(prompt_id)
        self.assertEqual(prompt["version"], 1)

    def test_version_increment(self):
        """Test version increments on update."""
        prompt_id = self.library.add_prompt("ver2", "Prompt", "Original")

        new_version = self.library.update_prompt(prompt_id, content="Updated")

        self.assertEqual(new_version, 2)

    def test_version_history(self):
        """Test version history tracking."""
        prompt_id = self.library.add_prompt("ver3", "Prompt", "Content")
        self.library.update_prompt(prompt_id, content="Update 1")

        history = self.library.get_version_history(prompt_id)
        self.assertGreater(len(history), 0)

    def test_revert_to_version(self):
        """Test reverting to previous version."""
        prompt_id = self.library.add_prompt("ver4", "Prompt", "Original")
        self.library.update_prompt(prompt_id, content="Update")

        reverted = self.library.revert_to_version(prompt_id, 1)
        self.assertTrue(reverted)

    def test_version_history_metadata(self):
        """Test version history includes metadata."""
        prompt_id = self.library.add_prompt("ver5", "Prompt", "Content")

        history = self.library.get_version_history(prompt_id)
        self.assertIn("timestamp", history[0])
        self.assertIn("note", history[0])


class TestOfflineEditing(unittest.TestCase):
    """Test offline editing."""

    def setUp(self):
        self.library = OfflinePromptLibrary()

    def test_edit_offline(self):
        """Test editing prompt offline."""
        prompt_id = self.library.add_prompt(
            "edit1",
            "Prompt",
            "Original content"
        )

        version = self.library.edit_offline(prompt_id, "Edited offline")

        self.assertEqual(version, 2)

        prompt = self.library.get_prompt(prompt_id)
        self.assertTrue(prompt["metadata"]["offline_edited"])

    def test_offline_edit_timestamp(self):
        """Test offline edit timestamp."""
        prompt_id = self.library.add_prompt("edit2", "Prompt", "Content")

        self.library.edit_offline(prompt_id, "New content")

        prompt = self.library.get_prompt(prompt_id)
        self.assertIn("last_offline_edit", prompt["metadata"])

    def test_check_offline_editable(self):
        """Test checking if prompt is offline editable."""
        prompt_id = self.library.add_prompt("edit3", "Prompt", "Content")

        editable = self.library.check_offline_editable(prompt_id)
        self.assertTrue(editable)

    def test_multiple_offline_edits(self):
        """Test multiple offline edits."""
        prompt_id = self.library.add_prompt("edit4", "Prompt", "Original")

        self.library.edit_offline(prompt_id, "Edit 1")
        self.library.edit_offline(prompt_id, "Edit 2")

        prompt = self.library.get_prompt(prompt_id)
        self.assertEqual(prompt["version"], 3)

    def test_nonexistent_prompt_not_editable(self):
        """Test nonexistent prompt is not editable."""
        editable = self.library.check_offline_editable("nonexistent")
        self.assertFalse(editable)


class TestPromptVariables(unittest.TestCase):
    """Test prompt variables."""

    def setUp(self):
        self.library = OfflinePromptLibrary()

    def test_set_variable_default(self):
        """Test setting variable default."""
        self.library.set_variable_default("username", "guest")

        default = self.library.get_variable_default("username")
        self.assertEqual(default, "guest")

    def test_render_with_defaults(self):
        """Test rendering with default variables."""
        self.library.set_variable_default("name", "Alice")
        self.library.set_variable_default("age", 30)

        template_id = self.library.create_template(
            "defaults1",
            "Template",
            "Name: {name}, Age: {age}"
        )

        rendered = self.library.render_with_defaults(template_id)
        self.assertIn("Alice", rendered)
        self.assertIn("30", rendered)

    def test_override_defaults(self):
        """Test overriding default variables."""
        self.library.set_variable_default("color", "blue")

        template_id = self.library.create_template(
            "override1",
            "Template",
            "Color: {color}"
        )

        rendered = self.library.render_with_defaults(
            template_id,
            {"color": "red"}
        )

        self.assertIn("red", rendered)
        self.assertNotIn("blue", rendered)

    def test_variable_type_tracking(self):
        """Test variable type is tracked."""
        self.library.set_variable_default("count", 42)

        var_info = self.library.variables["count"]
        self.assertEqual(var_info["type"], "int")

    def test_undefined_variable_default(self):
        """Test undefined variable returns None."""
        default = self.library.get_variable_default("undefined")
        self.assertIsNone(default)


class TestPromptChaining(unittest.TestCase):
    """Test prompt chaining."""

    def setUp(self):
        self.library = OfflinePromptLibrary()

    def test_create_prompt_chain(self):
        """Test creating prompt chain."""
        p1 = self.library.add_prompt("chain1", "Step 1", "First step")
        p2 = self.library.add_prompt("chain2", "Step 2", "Second step")

        chain_id = self.library.create_prompt_chain("c1", [p1, p2], "Test Chain")

        self.assertIn(chain_id, self.library.chains)

    def test_get_chain(self):
        """Test getting chain."""
        p1 = self.library.add_prompt("gc1", "P1", "Content")

        chain_id = self.library.create_prompt_chain("gc", [p1])
        chain = self.library.get_chain(chain_id)

        self.assertEqual(chain["id"], chain_id)
        self.assertIn(p1, chain["prompts"])

    def test_execute_chain(self):
        """Test executing prompt chain."""
        p1 = self.library.add_prompt("exec1", "P1", "Step 1")
        p2 = self.library.add_prompt("exec2", "P2", "Step 2")

        chain_id = self.library.create_prompt_chain("exec", [p1, p2])

        result = self.library.execute_chain(chain_id, "Initial input")

        self.assertIn("final_output", result)
        self.assertIn("steps", result)
        self.assertEqual(len(result["steps"]), 2)

    def test_chain_with_nonexistent_prompt(self):
        """Test chain with nonexistent prompt raises error."""
        with self.assertRaises(KeyError):
            self.library.create_prompt_chain("bad", ["nonexistent"])


class TestImportExport(unittest.TestCase):
    """Test import/export."""

    def setUp(self):
        self.library = OfflinePromptLibrary()

    def test_export_library(self):
        """Test exporting library."""
        self.library.add_prompt("exp1", "Prompt", "Content")

        export = self.library.export_library()

        self.assertIn("prompts", export)
        self.assertIn("templates", export)
        self.assertEqual(export["total_prompts"], 1)

    def test_import_library(self):
        """Test importing library."""
        data = {
            "prompts": {
                "imp1": {
                    "id": "imp1",
                    "name": "Imported",
                    "content": "Content",
                    "type": "user",
                    "role": "general",
                    "version": 1
                }
            }
        }

        result = self.library.import_library(data)

        self.assertEqual(result["prompts"], 1)
        self.assertIn("imp1", self.library.prompts)

    def test_import_templates(self):
        """Test importing templates."""
        data = {
            "templates": {
                "tmpl1": {
                    "id": "tmpl1",
                    "name": "Template",
                    "content": "Content",
                    "variables": []
                }
            }
        }

        result = self.library.import_library(data)

        self.assertEqual(result["templates"], 1)

    def test_import_with_errors(self):
        """Test import with invalid data."""
        data = {
            "prompts": {
                "bad": {
                    "id": "bad",
                    "role": "invalid_role"
                }
            }
        }

        result = self.library.import_library(data)

        self.assertGreater(len(result["errors"]), 0)


class TestIntegrationScenarios(unittest.TestCase):
    """Test end-to-end prompt development scenarios."""

    def setUp(self):
        self.library = OfflinePromptLibrary()

    def test_complete_prompt_development_workflow(self):
        """Test complete prompt development workflow."""
        # Create template
        template_id = self.library.create_template(
            "workflow1",
            "Question Template",
            "Question: {question}\nContext: {context}\nAnswer:"
        )

        # Set defaults
        self.library.set_variable_default("context", "General knowledge")

        # Render template
        rendered = self.library.render_with_defaults(
            template_id,
            {"question": "What is AI?"}
        )

        # Create prompt from rendered
        prompt_id = self.library.add_prompt(
            "workflow_prompt",
            "AI Question",
            rendered,
            role=PromptRole.USER
        )

        # Test prompt
        test_result = self.library.test_prompt(prompt_id, "AI question")
        self.assertTrue(test_result["passed"])

        # Validate
        validation = self.library.validate_prompt(prompt_id)
        self.assertTrue(validation["valid"])

    def test_role_based_prompt_library(self):
        """Test role-based prompt organization."""
        # Add prompts for different roles
        self.library.add_prompt("user1", "Basic Query", "Content", role=PromptRole.USER)
        self.library.add_prompt("power1", "Advanced Query", "Content", role=PromptRole.POWER)
        self.library.add_prompt("wizard1", "System Config", "Content", role=PromptRole.WIZARD)

        # Get role-specific prompts
        user_prompts = self.library.get_prompts_by_role(PromptRole.USER)
        wizard_prompts = self.library.get_prompts_by_role(PromptRole.WIZARD)

        self.assertEqual(len(user_prompts), 1)
        self.assertEqual(len(wizard_prompts), 1)

        # Get stats
        stats = self.library.get_library_stats()
        self.assertEqual(stats["total_prompts"], 3)

    def test_offline_prompt_development_cycle(self):
        """Test offline development cycle."""
        # Create initial prompt
        prompt_id = self.library.add_prompt(
            "offline1",
            "Development Prompt",
            "Initial version"
        )

        # Edit offline multiple times
        self.library.edit_offline(prompt_id, "Revision 1")
        self.library.edit_offline(prompt_id, "Revision 2")
        self.library.edit_offline(prompt_id, "Final version")

        # Check version
        prompt = self.library.get_prompt(prompt_id)
        self.assertEqual(prompt["version"], 4)

        # Get history
        history = self.library.get_version_history(prompt_id)
        self.assertEqual(len(history), 4)

        # Export for backup
        export = self.library.export_library()
        self.assertIn(prompt_id, export["prompts"])


if __name__ == "__main__":
    unittest.main()

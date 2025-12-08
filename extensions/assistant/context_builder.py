"""
Context Builder for OK Assistant
Builds rich context for AI prompts with workspace awareness

Features:
- Prompt augmentation with workspace context
- Knowledge bank integration
- Recent command context
- Error context for debugging
- Git change awareness
- File content integration

Version: 1.0.0 (v1.2.21)
Author: Fred Porter
"""

from typing import Optional, Dict, Any, List
from pathlib import Path
from core.services.ok_context_manager import get_ok_context_manager
from core.config import Config


class ContextBuilder:
    """Builds context-aware prompts for OK assistant"""

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize context builder.

        Args:
            config: Config instance (auto-creates if None)
        """
        self.config = config or Config()
        self.context_manager = get_ok_context_manager()

    def build_prompt(self, user_prompt: str, context_type: str = "general") -> str:
        """
        Build context-aware prompt for AI.

        Args:
            user_prompt: User's original prompt
            context_type: general | code | debug | generate | explain

        Returns:
            Enhanced prompt with context
        """
        context = self.context_manager.get_context()
        
        # Base context sections
        sections = []

        # System context
        sections.append("# uDOS Context\n")

        # Workspace context
        workspace_info = []
        if context["workspace"]["path"]:
            workspace_info.append(f"Working directory: {context['workspace']['path']}")
        
        if context["workspace"]["current_file"]:
            workspace_info.append(f"Current file: {context['workspace']['current_file']}")
        
        if context["workspace"]["tile_location"]:
            workspace_info.append(f"TILE location: {context['workspace']['tile_location']}")

        if workspace_info:
            sections.append("\n".join(workspace_info))

        # Recent commands (for debugging context)
        if context_type in ["debug", "explain"] and context["history"]["commands"]:
            sections.append("\n## Recent Commands")
            for cmd in context["history"]["commands"][-3:]:
                sections.append(f"- {cmd['command']} ({cmd['status']})")

        # Recent errors (for debug context)
        if context_type == "debug" and context["history"]["errors"]:
            sections.append("\n## Recent Errors")
            for error in context["history"]["errors"]:
                sections.append(f"- {error}")

        # Git status (for code context)
        if context_type in ["code", "generate"] and context["git"]:
            git = context["git"]
            if any(git.values()):
                sections.append("\n## Git Status")
                if git["modified"]:
                    sections.append(f"Modified: {', '.join(git['modified'][:5])}")
                if git["added"]:
                    sections.append(f"Added: {', '.join(git['added'][:5])}")

        # Build final prompt
        context_header = "\n".join(sections)
        
        # Add user prompt
        final_prompt = f"{context_header}\n\n# User Request\n{user_prompt}"

        return final_prompt

    def build_workflow_prompt(self, workflow_type: str, details: str) -> str:
        """
        Build prompt for workflow generation.

        Args:
            workflow_type: Type of workflow (mission, automation, test)
            details: Workflow details from user

        Returns:
            Context-aware workflow generation prompt
        """
        context = self.context_manager.get_context()
        
        prompt = f"""# Generate uPY Workflow Script

Workflow Type: {workflow_type}
Details: {details}

## Requirements
- Use uPY v1.2.x syntax (COMMAND|args format)
- Include error handling
- Add progress indicators
- Follow uDOS conventions

## Context
"""
        # Add workspace context
        if context["workspace"]["tile_location"]:
            prompt += f"- Location: {context['workspace']['tile_location']}\n"

        return prompt

    def build_svg_prompt(self, description: str, category: str = "diagram") -> str:
        """
        Build prompt for SVG generation.

        Args:
            description: SVG description from user
            category: diagram | icon | map | chart

        Returns:
            Context-aware SVG generation prompt
        """
        prompt = f"""# Generate SVG Graphic

Category: {category}
Description: {description}

## Requirements
- Valid SVG syntax
- Minimal design aesthetic
- Text-friendly (readable at small sizes)
- Monochrome or limited palette
- Include viewBox attribute

Generate only the SVG code, no explanations.
"""
        return prompt

    def build_doc_prompt(self, topic: str, doc_type: str = "guide") -> str:
        """
        Build prompt for documentation generation.

        Args:
            topic: Documentation topic
            doc_type: guide | reference | tutorial | api

        Returns:
            Context-aware documentation prompt
        """
        context = self.context_manager.get_context()
        
        prompt = f"""# Generate uDOS Documentation

Type: {doc_type}
Topic: {topic}

## Style Guidelines
- Clear, concise language
- Practical examples
- Offline-first focus
- Markdown format
- Code blocks with syntax highlighting

"""
        # Add file context if relevant
        if context["workspace"]["current_file"]:
            prompt += f"Context: Currently viewing {context['workspace']['current_file']}\n"

        return prompt

    def build_test_prompt(self, code_file: str, test_type: str = "unit") -> str:
        """
        Build prompt for test generation.

        Args:
            code_file: File to generate tests for
            test_type: unit | integration | shakedown

        Returns:
            Context-aware test generation prompt
        """
        prompt = f"""# Generate Python Tests

Test Type: {test_type}
Target File: {code_file}

## Requirements
- Use pytest framework
- Test coverage > 80%
- Include edge cases
- Clear test names (test_feature_scenario)
- Docstrings for each test

Generate test file for memory/ucode/tests/
"""
        return prompt


# Singleton instance
_context_builder: Optional[ContextBuilder] = None


def get_context_builder() -> ContextBuilder:
    """
    Get singleton context builder instance.

    Returns:
        ContextBuilder instance
    """
    global _context_builder
    if _context_builder is None:
        _context_builder = ContextBuilder()
    return _context_builder

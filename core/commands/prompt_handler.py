"""
PROMPT Command Handler (v1.2.15)

Admin-only prompt management for AI-assisted graphics generation.

Commands:
    PROMPT LIST [format]           - List all prompts or filter by format
    PROMPT SHOW <id>               - Display full prompt with metadata
    PROMPT EDIT <id>               - Edit prompt (opens in editor)
    PROMPT TEST <id> <input>       - Test prompt with sample input
    PROMPT STATS                   - Show usage statistics
    PROMPT CREATE <format>         - Create new prompt template
    PROMPT DELETE <id>             - Delete prompt (with confirmation)

Requirements:
    - DEV MODE must be enabled
    - Prompts stored in core/data/prompts/graphics/
    - YAML frontmatter for metadata
    - Version tracking

Author: uDOS Core Team
Version: 1.2.15
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from core.config import Config
from core.utils.paths import PATHS
from core.services.unified_logger import get_unified_logger

logger = get_unified_logger()


class PromptHandler:
    """Handler for PROMPT command - AI prompt management."""
    
    PROMPT_DIR = PATHS.CORE / "data" / "prompts" / "graphics"
    
    FORMATS = ["ascii", "teletext", "svg", "sequence", "flow"]
    
    PROMPT_TEMPLATE = """---
id: {id}
format: {format}
version: 1.0.0
created: {created}
updated: {updated}
author: {author}
usage_count: 0
success_rate: 0.0
tags: []
---

# Prompt: {title}

## Purpose
Brief description of what this prompt accomplishes.

## Input Variables
- {{input}}: Main content/description
- {{style}}: Style/theme preference
- {{complexity}}: Level of detail (simple/detailed/technical)

## System Prompt
You are an expert diagram generator. Generate a {format} graphic based on the following:

Input: {{input}}
Style: {{style}}
Complexity: {{complexity}}

Requirements:
- Follow {format} syntax exactly
- Be concise and clear
- Focus on essential information
- Use appropriate visual hierarchy

## Output Format
{format_specific_instructions}

## Examples
### Example 1
Input: "water filter system"
Output:
[Example output here]

## Notes
- Version history tracked in metadata
- Test before deploying to production
- Monitor success_rate for optimization
"""
    
    def __init__(self):
        """Initialize prompt handler."""
        self.config = Config()
        self.prompts_cache = {}
        self._ensure_prompt_directory()
    
    def _ensure_prompt_directory(self):
        """Create prompt directory structure if missing."""
        self.PROMPT_DIR.mkdir(parents=True, exist_ok=True)
        for format_type in self.FORMATS:
            format_dir = self.PROMPT_DIR / format_type
            format_dir.mkdir(exist_ok=True)
    
    def _check_dev_mode(self) -> bool:
        """Check if DEV MODE is enabled."""
        dev_mode = self.config.get('dev_mode', False)
        if not dev_mode:
            return False
        return True
    
    def handle(self, parts: List[str]) -> str:
        """Handle PROMPT command routing.
        
        Args:
            parts: Command parts (e.g., ['PROMPT', 'LIST', 'ascii'])
        
        Returns:
            Command output
        """
        # DEV MODE check
        if not self._check_dev_mode():
            return (
                "❌ PROMPT command requires DEV MODE\n\n"
                "Enable with: CONFIG SET dev_mode true\n\n"
                "⚠️  WARNING: DEV MODE is for development only.\n"
                "Prompts control AI behavior and should only be modified by admins."
            )
        
        if len(parts) < 2:
            return self._help()
        
        subcommand = parts[1].upper()
        
        if subcommand == "LIST":
            format_filter = parts[2].lower() if len(parts) > 2 else None
            return self._list_prompts(format_filter)
        
        elif subcommand == "SHOW":
            if len(parts) < 3:
                return "❌ Usage: PROMPT SHOW <id>"
            return self._show_prompt(parts[2])
        
        elif subcommand == "EDIT":
            if len(parts) < 3:
                return "❌ Usage: PROMPT EDIT <id>"
            return self._edit_prompt(parts[2])
        
        elif subcommand == "TEST":
            if len(parts) < 4:
                return "❌ Usage: PROMPT TEST <id> <input>"
            prompt_id = parts[2]
            test_input = " ".join(parts[3:])
            return self._test_prompt(prompt_id, test_input)
        
        elif subcommand == "STATS":
            return self._show_stats()
        
        elif subcommand == "CREATE":
            if len(parts) < 3:
                return "❌ Usage: PROMPT CREATE <format>"
            format_type = parts[2].lower()
            return self._create_prompt(format_type)
        
        elif subcommand == "DELETE":
            if len(parts) < 3:
                return "❌ Usage: PROMPT DELETE <id>"
            return self._delete_prompt(parts[2])
        
        else:
            return self._help()
    
    def _list_prompts(self, format_filter: Optional[str] = None) -> str:
        """List all prompts or filter by format.
        
        Args:
            format_filter: Optional format to filter (ascii, svg, etc.)
        
        Returns:
            Formatted list of prompts
        """
        prompts = self._load_all_prompts(format_filter)
        
        if not prompts:
            if format_filter:
                return f"📋 No prompts found for format: {format_filter}"
            return "📋 No prompts found. Use PROMPT CREATE <format> to create one."
        
        output = []
        output.append("📋 AI Prompts Library\n")
        output.append("=" * 70)
        
        # Group by format
        by_format = {}
        for prompt in prompts:
            fmt = prompt.get('format', 'unknown')
            if fmt not in by_format:
                by_format[fmt] = []
            by_format[fmt].append(prompt)
        
        for fmt in sorted(by_format.keys()):
            output.append(f"\n{fmt.upper()} Prompts ({len(by_format[fmt])}):")
            output.append("-" * 70)
            
            for prompt in by_format[fmt]:
                pid = prompt.get('id', 'unknown')
                version = prompt.get('version', '1.0.0')
                usage = prompt.get('usage_count', 0)
                success = prompt.get('success_rate', 0.0)
                
                output.append(f"  {pid:30} v{version}  Used: {usage:4}  Success: {success:.1%}")
        
        output.append("\n" + "=" * 70)
        output.append(f"Total: {len(prompts)} prompts")
        output.append("\nUse 'PROMPT SHOW <id>' to view full prompt")
        
        return "\n".join(output)
    
    def _show_prompt(self, prompt_id: str) -> str:
        """Display full prompt with metadata.
        
        Args:
            prompt_id: Prompt identifier
        
        Returns:
            Formatted prompt display
        """
        prompt = self._load_prompt(prompt_id)
        if not prompt:
            return f"❌ Prompt not found: {prompt_id}"
        
        output = []
        output.append(f"📄 Prompt: {prompt_id}")
        output.append("=" * 70)
        
        # Metadata
        output.append("\nMetadata:")
        output.append(f"  Format:       {prompt.get('format', 'unknown')}")
        output.append(f"  Version:      {prompt.get('version', '1.0.0')}")
        output.append(f"  Created:      {prompt.get('created', 'unknown')}")
        output.append(f"  Updated:      {prompt.get('updated', 'unknown')}")
        output.append(f"  Author:       {prompt.get('author', 'unknown')}")
        output.append(f"  Usage Count:  {prompt.get('usage_count', 0)}")
        output.append(f"  Success Rate: {prompt.get('success_rate', 0.0):.1%}")
        
        tags = prompt.get('tags', [])
        if tags:
            output.append(f"  Tags:         {', '.join(tags)}")
        
        # Prompt content
        output.append("\nPrompt Content:")
        output.append("-" * 70)
        output.append(prompt.get('content', 'No content'))
        
        output.append("\n" + "=" * 70)
        output.append(f"File: {prompt.get('filepath', 'unknown')}")
        
        return "\n".join(output)
    
    def _edit_prompt(self, prompt_id: str) -> str:
        """Edit prompt in default editor.
        
        Args:
            prompt_id: Prompt identifier
        
        Returns:
            Status message
        """
        prompt = self._load_prompt(prompt_id)
        if not prompt:
            return f"❌ Prompt not found: {prompt_id}"
        
        filepath = prompt.get('filepath')
        if not filepath or not os.path.exists(filepath):
            return f"❌ Prompt file not found: {filepath}"
        
        # Open in editor (VS Code by default, fallback to nano)
        editor = os.environ.get('EDITOR', 'nano')
        
        return (
            f"📝 Opening {prompt_id} in editor...\n\n"
            f"File: {filepath}\n"
            f"Editor: {editor}\n\n"
            f"Run: {editor} {filepath}\n\n"
            "💡 Tip: Update the 'updated' timestamp and increment version after changes."
        )
    
    def _test_prompt(self, prompt_id: str, test_input: str) -> str:
        """Test prompt with sample input.
        
        Args:
            prompt_id: Prompt identifier
            test_input: Test input string
        
        Returns:
            Test results
        """
        prompt = self._load_prompt(prompt_id)
        if not prompt:
            return f"❌ Prompt not found: {prompt_id}"
        
        content = prompt.get('content', '')
        
        # Replace variables
        test_output = content.replace('{{input}}', test_input)
        test_output = test_output.replace('{{style}}', 'default')
        test_output = test_output.replace('{{complexity}}', 'detailed')
        
        output = []
        output.append(f"🧪 Testing Prompt: {prompt_id}")
        output.append("=" * 70)
        output.append(f"\nTest Input: {test_input}")
        output.append("\nRendered Prompt:")
        output.append("-" * 70)
        output.append(test_output)
        output.append("\n" + "=" * 70)
        output.append("\n✅ Prompt rendered successfully")
        output.append("\n💡 To use with AI: Copy rendered prompt above")
        
        return "\n".join(output)
    
    def _show_stats(self) -> str:
        """Show usage statistics for all prompts.
        
        Returns:
            Statistics summary
        """
        prompts = self._load_all_prompts()
        
        if not prompts:
            return "📊 No prompts found. No statistics to display."
        
        # Calculate stats
        total_usage = sum(p.get('usage_count', 0) for p in prompts)
        avg_success = sum(p.get('success_rate', 0.0) for p in prompts) / len(prompts)
        
        # Top performers
        by_usage = sorted(prompts, key=lambda p: p.get('usage_count', 0), reverse=True)[:5]
        by_success = sorted(prompts, key=lambda p: p.get('success_rate', 0.0), reverse=True)[:5]
        
        output = []
        output.append("📊 Prompt Usage Statistics")
        output.append("=" * 70)
        output.append(f"\nTotal Prompts: {len(prompts)}")
        output.append(f"Total Usage:   {total_usage}")
        output.append(f"Avg Success:   {avg_success:.1%}")
        
        output.append("\n\nTop 5 Most Used:")
        output.append("-" * 70)
        for prompt in by_usage:
            pid = prompt.get('id', 'unknown')
            usage = prompt.get('usage_count', 0)
            output.append(f"  {pid:30} {usage:5} uses")
        
        output.append("\n\nTop 5 Highest Success Rate:")
        output.append("-" * 70)
        for prompt in by_success:
            pid = prompt.get('id', 'unknown')
            success = prompt.get('success_rate', 0.0)
            usage = prompt.get('usage_count', 0)
            output.append(f"  {pid:30} {success:6.1%}  ({usage} uses)")
        
        return "\n".join(output)
    
    def _create_prompt(self, format_type: str) -> str:
        """Create new prompt template.
        
        Args:
            format_type: Format (ascii, svg, etc.)
        
        Returns:
            Status message with filepath
        """
        if format_type not in self.FORMATS:
            return f"❌ Invalid format: {format_type}. Must be one of: {', '.join(self.FORMATS)}"
        
        # Generate ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prompt_id = f"{format_type}_{timestamp}"
        
        # Create filepath
        format_dir = self.PROMPT_DIR / format_type
        filepath = format_dir / f"{prompt_id}.md"
        
        # Generate content from template
        content = self.PROMPT_TEMPLATE.format(
            id=prompt_id,
            format=format_type,
            created=datetime.now().isoformat(),
            updated=datetime.now().isoformat(),
            author=os.environ.get('USER', 'unknown'),
            title=f"{format_type.upper()} Generation",
            format_specific_instructions=self._get_format_instructions(format_type)
        )
        
        # Write file
        with open(filepath, 'w') as f:
            f.write(content)
        
        return (
            f"✅ Created new prompt: {prompt_id}\n\n"
            f"File: {filepath}\n"
            f"Format: {format_type}\n\n"
            f"Next steps:\n"
            f"  1. PROMPT EDIT {prompt_id} - Edit prompt content\n"
            f"  2. PROMPT TEST {prompt_id} 'sample input' - Test prompt\n"
            f"  3. Deploy to production (manual step)"
        )
    
    def _delete_prompt(self, prompt_id: str) -> str:
        """Delete prompt with confirmation.
        
        Args:
            prompt_id: Prompt identifier
        
        Returns:
            Status message
        """
        prompt = self._load_prompt(prompt_id)
        if not prompt:
            return f"❌ Prompt not found: {prompt_id}"
        
        filepath = prompt.get('filepath')
        
        # Safety check: require explicit confirmation
        return (
            f"⚠️  DELETE CONFIRMATION REQUIRED\n\n"
            f"Prompt: {prompt_id}\n"
            f"File: {filepath}\n\n"
            f"This action cannot be undone.\n"
            f"To delete, manually run:\n\n"
            f"  rm {filepath}\n\n"
            f"Or move to archive:\n"
            f"  mv {filepath} {filepath}.archive"
        )
    
    def _get_format_instructions(self, format_type: str) -> str:
        """Get format-specific output instructions.
        
        Args:
            format_type: Format type
        
        Returns:
            Format-specific instructions
        """
        instructions = {
            'ascii': "Plain text with box-drawing characters (─│┌┐└┘├┤┬┴┼)",
            'teletext': "8-color ANSI codes using {0-7} tags for colors",
            'svg': "Valid SVG XML with proper namespaces and viewBox",
            'sequence': "js-sequence-diagrams syntax (Actor->Object: Message)",
            'flow': "flowchart.js syntax (start=>start: Label)"
        }
        return instructions.get(format_type, "Format-specific output")
    
    def _load_prompt(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """Load single prompt by ID.
        
        Args:
            prompt_id: Prompt identifier
        
        Returns:
            Prompt dict or None if not found
        """
        # Check cache
        if prompt_id in self.prompts_cache:
            return self.prompts_cache[prompt_id]
        
        # Search all format directories
        for format_type in self.FORMATS:
            format_dir = self.PROMPT_DIR / format_type
            filepath = format_dir / f"{prompt_id}.md"
            
            if filepath.exists():
                prompt_data = self._parse_prompt_file(filepath)
                if prompt_data:
                    self.prompts_cache[prompt_id] = prompt_data
                    return prompt_data
        
        return None
    
    def _load_all_prompts(self, format_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Load all prompts, optionally filtered by format.
        
        Args:
            format_filter: Optional format to filter
        
        Returns:
            List of prompt dicts
        """
        prompts = []
        
        formats = [format_filter] if format_filter else self.FORMATS
        
        for format_type in formats:
            format_dir = self.PROMPT_DIR / format_type
            if not format_dir.exists():
                continue
            
            for filepath in format_dir.glob("*.md"):
                prompt_data = self._parse_prompt_file(filepath)
                if prompt_data:
                    prompts.append(prompt_data)
        
        return prompts
    
    def _parse_prompt_file(self, filepath: Path) -> Optional[Dict[str, Any]]:
        """Parse prompt file with YAML frontmatter.
        
        Args:
            filepath: Path to prompt file
        
        Returns:
            Prompt data dict or None if invalid
        """
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Extract YAML frontmatter
            match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
            if not match:
                logger.log_system(f"No YAML frontmatter in {filepath}", level='warning')
                return None
            
            frontmatter = yaml.safe_load(match.group(1))
            prompt_content = match.group(2).strip()
            
            return {
                **frontmatter,
                'content': prompt_content,
                'filepath': str(filepath)
            }
        
        except Exception as e:
            logger.log_error(f"Failed to parse prompt file {filepath}", exception=e)
            return None
    
    def _help(self) -> str:
        """Show PROMPT command help.
        
        Returns:
            Help text
        """
        return """
📋 PROMPT Command - AI Prompt Management (v1.2.15)

⚠️  ADMIN ONLY - Requires DEV MODE

Commands:
  PROMPT LIST [format]           List all prompts or filter by format
  PROMPT SHOW <id>               Display full prompt with metadata
  PROMPT EDIT <id>               Edit prompt (opens in editor)
  PROMPT TEST <id> <input>       Test prompt with sample input
  PROMPT STATS                   Show usage statistics
  PROMPT CREATE <format>         Create new prompt template
  PROMPT DELETE <id>             Delete prompt (with confirmation)

Formats:
  ascii, teletext, svg, sequence, flow

Examples:
  PROMPT LIST ascii              List all ASCII prompts
  PROMPT SHOW ascii_20251207     Show prompt details
  PROMPT TEST ascii_20251207 "water filter"
  PROMPT STATS                   View usage statistics
  PROMPT CREATE svg              Create new SVG prompt

Prompt Storage:
  core/data/prompts/graphics/<format>/<id>.md

File Format:
  - YAML frontmatter for metadata (id, version, stats)
  - Markdown content for prompt text
  - Variable substitution: {{input}}, {{style}}, {{complexity}}

Version Control:
  - Track version in frontmatter
  - Update timestamp on changes
  - Monitor usage_count and success_rate

See Also:
  MAKE --format <type> --ai-assisted   (uses prompts)
  CONFIG SET dev_mode true             (enable DEV MODE)
"""


def handle_prompt(parts: List[str]) -> str:
    """Entry point for PROMPT command.
    
    Args:
        parts: Command parts
    
    Returns:
        Command output
    """
    handler = PromptHandler()
    return handler.handle(parts)

"""
ASSETS Command Handler (v1.5.3+)

Provides commands for browsing, previewing, and loading shared assets.

Commands:
- ASSETS LIST [type] - List all assets or filter by type
- ASSETS SEARCH <query> - Search assets by name or tag
- ASSETS INFO <name> - Show detailed information about an asset
- ASSETS PREVIEW <name> - Preview asset contents
- ASSETS LOAD <name> - Load an asset into memory
- ASSETS STATS - Show asset manager statistics
- ASSETS RELOAD <name> - Hot-reload an asset from disk

Usage Examples:
    ASSETS LIST fonts
    ASSETS SEARCH water
    ASSETS INFO teletext-single
    ASSETS PREVIEW mac-checkerboard
    ASSETS LOAD chicago
    ASSETS STATS
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
from core.services.asset_manager import get_asset_manager
import json


class AssetsHandler:
    """Handler for ASSETS commands."""

    def __init__(self):
        """Initialize ASSETS handler."""
        self.asset_mgr = get_asset_manager()

        # Command routing
        self.commands = {
            'LIST': self.handle_list,
            'SEARCH': self.handle_search,
            'INFO': self.handle_info,
            'PREVIEW': self.handle_preview,
            'LOAD': self.handle_load,
            'STATS': self.handle_stats,
            'RELOAD': self.handle_reload,
            'HELP': self.handle_help
        }

    def handle_assets_command(self, params: List[str], grid: Any, parser: Any) -> str:
        """
        Main entry point for ASSETS commands.

        Args:
            params: Command parameters
            grid: Grid object (for display)
            parser: Parser object

        Returns:
            Response message
        """
        if not params or params[0].upper() == 'HELP':
            return self.handle_help(params, grid, parser)

        subcommand = params[0].upper()
        if subcommand not in self.commands:
            return f"❌ Unknown ASSETS command: {subcommand}\n\nUse 'ASSETS HELP' for available commands."

        return self.commands[subcommand](params[1:], grid, parser)

    def handle_list(self, params: List[str], grid: Any, parser: Any) -> str:
        """
        List all assets or filter by type.

        Args:
            params: [type] (optional)

        Returns:
            Formatted asset list
        """
        asset_type = params[0] if params else None

        # Validate type
        valid_types = ['fonts', 'icons', 'patterns', 'css', 'js']
        if asset_type and asset_type not in valid_types:
            return f"❌ Invalid asset type: {asset_type}\n\nValid types: {', '.join(valid_types)}"

        assets = self.asset_mgr.list_assets(asset_type)

        if not assets:
            type_msg = f" of type '{asset_type}'" if asset_type else ""
            return f"📦 No assets found{type_msg}"

        # Group by type
        by_type: Dict[str, List[str]] = {}
        for asset_name in assets:
            parts = asset_name.split('/', 1)
            asset_type_key = parts[0] if len(parts) > 1 else 'other'
            asset_base_name = parts[1] if len(parts) > 1 else asset_name

            if asset_type_key not in by_type:
                by_type[asset_type_key] = []
            by_type[asset_type_key].append(asset_base_name)

        # Format output
        output = []
        output.append("=" * 80)
        output.append("📦 ASSETS LIBRARY")
        output.append("=" * 80)
        output.append("")

        for atype in sorted(by_type.keys()):
            items = sorted(by_type[atype])
            output.append(f"▸ {atype.upper()} ({len(items)} assets)")
            output.append("")

            # Display in columns
            col_width = 30
            cols = 2
            for i in range(0, len(items), cols):
                row_items = items[i:i + cols]
                row = "  " + "".join(f"{item:<{col_width}}" for item in row_items)
                output.append(row.rstrip())

            output.append("")

        output.append("=" * 80)
        output.append(f"Total: {len(assets)} assets")
        output.append("")
        output.append("Use 'ASSETS INFO <name>' for details")
        output.append("Use 'ASSETS SEARCH <query>' to search")

        return "\n".join(output)

    def handle_search(self, params: List[str], grid: Any, parser: Any) -> str:
        """
        Search assets by name or metadata.

        Args:
            params: [query]

        Returns:
            Search results
        """
        if not params:
            return "❌ Missing search query\n\nUsage: ASSETS SEARCH <query>"

        query = " ".join(params)
        results = self.asset_mgr.search_assets(query)

        if not results:
            return f"🔍 No assets found matching '{query}'"

        output = []
        output.append("=" * 80)
        output.append(f"🔍 SEARCH RESULTS: '{query}'")
        output.append("=" * 80)
        output.append("")

        for name, asset in results[:50]:  # Limit to 50 results
            info = asset.get_info()
            tags = info['metadata'].get('tags', [])
            tags_str = f" [{', '.join(tags[:3])}]" if tags else ""

            output.append(f"  📄 {name}{tags_str}")
            if 'description' in info['metadata']:
                output.append(f"     {info['metadata']['description']}")
            output.append("")

        if len(results) > 50:
            output.append(f"... and {len(results) - 50} more results")
            output.append("")

        output.append("=" * 80)
        output.append(f"Found {len(results)} assets")
        output.append("")
        output.append("Use 'ASSETS INFO <name>' for details")

        return "\n".join(output)

    def handle_info(self, params: List[str], grid: Any, parser: Any) -> str:
        """
        Show detailed information about an asset.

        Args:
            params: [asset_name]

        Returns:
            Asset information
        """
        if not params:
            return "❌ Missing asset name\n\nUsage: ASSETS INFO <name>"

        name = " ".join(params)
        info = self.asset_mgr.get_asset_info(name)

        if not info:
            return f"❌ Asset not found: {name}\n\nUse 'ASSETS LIST' to see available assets"

        output = []
        output.append("=" * 80)
        output.append(f"📄 ASSET INFO: {info['name']}")
        output.append("=" * 80)
        output.append("")

        output.append(f"Type:     {info['type']}")
        output.append(f"Version:  {info.get('version', 'unknown')}")
        output.append(f"Path:     {info['path']}")
        output.append(f"Size:     {info['size']:,} bytes")
        output.append(f"Loaded:   {info['loaded'] or 'Not loaded'}")
        output.append("")

        # Metadata
        if info['metadata']:
            output.append("Metadata:")
            for key, value in info['metadata'].items():
                if isinstance(value, list):
                    output.append(f"  {key}: {', '.join(str(v) for v in value)}")
                else:
                    output.append(f"  {key}: {value}")
            output.append("")

        output.append("=" * 80)
        output.append("Use 'ASSETS PREVIEW <name>' to see contents")
        output.append("Use 'ASSETS LOAD <name>' to load into memory")

        return "\n".join(output)

    def handle_preview(self, params: List[str], grid: Any, parser: Any) -> str:
        """
        Preview asset contents.

        Args:
            params: [asset_name]

        Returns:
            Asset preview
        """
        if not params:
            return "❌ Missing asset name\n\nUsage: ASSETS PREVIEW <name>"

        name = " ".join(params)

        # Try to find asset
        asset = None
        for asset_type in ['patterns', 'fonts', 'icons', 'css', 'js']:
            temp_asset = getattr(self.asset_mgr, f"load_{asset_type.rstrip('s')}")(name)
            if temp_asset:
                asset = temp_asset
                break

        if not asset:
            return f"❌ Asset not found: {name}\n\nUse 'ASSETS LIST' to see available assets"

        try:
            data = asset.load()
        except Exception as e:
            return f"❌ Error loading asset: {e}"

        output = []
        output.append("=" * 80)
        output.append(f"👁️  PREVIEW: {asset.name}")
        output.append("=" * 80)
        output.append("")

        # Format based on type
        if isinstance(data, dict):
            # JSON data - pretty print
            if 'pattern' in data:
                # Pattern preview
                output.append("Pattern:")
                output.append("")
                for line in data['pattern']:
                    output.append(f"  {line}")
            elif 'example' in data:
                # Border example
                output.append("Example:")
                output.append("")
                for line in data['example']:
                    output.append(f"  {line}")
            else:
                # General JSON
                output.append(json.dumps(data, indent=2))
        elif isinstance(data, str):
            # Text content - show first 50 lines
            lines = data.split('\n')
            output.extend(lines[:50])
            if len(lines) > 50:
                output.append("")
                output.append(f"... {len(lines) - 50} more lines")
        else:
            # Binary data
            output.append(f"[Binary data: {len(data)} bytes]")

        output.append("")
        output.append("=" * 80)

        return "\n".join(output)

    def handle_load(self, params: List[str], grid: Any, parser: Any) -> str:
        """
        Load an asset into memory.

        Args:
            params: [asset_name]

        Returns:
            Success message
        """
        if not params:
            return "❌ Missing asset name\n\nUsage: ASSETS LOAD <name>"

        name = " ".join(params)

        # Try to find and load asset
        asset = None
        for asset_type in ['fonts', 'icons', 'patterns', 'css', 'js']:
            loader_method = f"load_{asset_type.rstrip('s')}"
            temp_asset = getattr(self.asset_mgr, loader_method)(name)
            if temp_asset:
                asset = temp_asset
                break

        if not asset:
            return f"❌ Asset not found: {name}\n\nUse 'ASSETS LIST' to see available assets"

        try:
            data = asset.load()
            size = len(str(data)) if isinstance(data, (str, dict)) else len(data)

            return f"✅ Loaded asset: {asset.name}\n   Type: {asset.type}\n   Size: {size:,} bytes"
        except Exception as e:
            return f"❌ Error loading asset: {e}"

    def handle_stats(self, params: List[str], grid: Any, parser: Any) -> str:
        """
        Show asset manager statistics.

        Returns:
            Statistics display
        """
        stats = self.asset_mgr.get_stats()

        output = []
        output.append("=" * 80)
        output.append("📊 ASSET MANAGER STATISTICS")
        output.append("=" * 80)
        output.append("")

        output.append(f"Total Assets:     {stats['total_assets']}")
        output.append(f"Loaded in Memory: {stats['loaded']}")
        output.append(f"Total Size:       {stats['total_size_mb']} MB ({stats['total_size_bytes']:,} bytes)")
        output.append("")

        output.append("By Type:")
        for asset_type, count in sorted(stats['by_type'].items()):
            if count > 0:
                output.append(f"  {asset_type.capitalize():<15} {count:>5} assets")

        output.append("")
        output.append(f"Assets Root: {stats['assets_root']}")
        output.append("")
        output.append("=" * 80)

        return "\n".join(output)

    def handle_reload(self, params: List[str], grid: Any, parser: Any) -> str:
        """
        Hot-reload an asset from disk.

        Args:
            params: [asset_name]

        Returns:
            Success message
        """
        if not params:
            return "❌ Missing asset name\n\nUsage: ASSETS RELOAD <name>"

        name = " ".join(params)

        # Find full asset name
        info = self.asset_mgr.get_asset_info(name)
        if not info:
            return f"❌ Asset not found: {name}"

        full_name = info['name']
        success = self.asset_mgr.reload_asset(full_name)

        if success:
            return f"✅ Reloaded asset: {full_name}"
        else:
            return f"❌ Failed to reload asset: {full_name}"

    def handle_help(self, params: List[str], grid: Any, parser: Any) -> str:
        """Show ASSETS command help."""
        output = []
        output.append("=" * 80)
        output.append("📦 ASSETS COMMAND REFERENCE")
        output.append("=" * 80)
        output.append("")
        output.append("ASSETS LIST [type]          - List all assets or filter by type")
        output.append("                             Types: fonts, icons, patterns, css, js")
        output.append("")
        output.append("ASSETS SEARCH <query>       - Search assets by name or tags")
        output.append("                             Supports regex patterns")
        output.append("")
        output.append("ASSETS INFO <name>          - Show detailed asset information")
        output.append("                             Includes path, size, metadata")
        output.append("")
        output.append("ASSETS PREVIEW <name>       - Preview asset contents")
        output.append("                             Shows first 50 lines for text")
        output.append("")
        output.append("ASSETS LOAD <name>          - Load asset into memory")
        output.append("                             Caches for faster access")
        output.append("")
        output.append("ASSETS STATS                - Show asset manager statistics")
        output.append("                             Total assets, memory usage")
        output.append("")
        output.append("ASSETS RELOAD <name>        - Hot-reload asset from disk")
        output.append("                             Updates cached copy")
        output.append("")
        output.append("ASSETS HELP                 - Show this help message")
        output.append("")
        output.append("=" * 80)
        output.append("Examples:")
        output.append("  ASSETS LIST fonts")
        output.append("  ASSETS SEARCH teletext")
        output.append("  ASSETS INFO mac-checkerboard")
        output.append("  ASSETS PREVIEW teletext-single")
        output.append("  ASSETS LOAD chicago")
        output.append("=" * 80)

        return "\n".join(output)


# For integration with uDOS command system
def handle_assets_command(params: List[str], grid: Any, parser: Any) -> str:
    """
    Entry point for ASSETS commands from uDOS main.

    Args:
        params: Command parameters
        grid: Grid object
        parser: Parser object

    Returns:
        Command response
    """
    handler = AssetsHandler()
    return handler.handle_assets_command(params, grid, parser)

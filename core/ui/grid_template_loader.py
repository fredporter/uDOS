#!/usr/bin/env python3
"""
uDOS Grid Template Loader - JSON template loading and rendering

Loads grid templates from core/data/grid_templates/ and renders them using
GridRenderer. Supports variable substitution, heatmap generation, and
multi-section dashboards.

Version: v1.2.14
Author: Fred Porter
Date: December 7, 2025
"""

import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path

from core.ui.grid_renderer import GridRenderer, GridCell, ViewportTier, Symbols


class GridTemplateLoader:
    """Load and render grid templates from JSON."""
    
    TEMPLATE_DIR = Path(__file__).parent.parent / "data" / "grid_templates"
    
    def __init__(self):
        """Initialize template loader."""
        self.templates: Dict[str, Dict] = {}
        self.load_all_templates()
    
    def load_all_templates(self) -> None:
        """Load all JSON templates from template directory."""
        if not self.TEMPLATE_DIR.exists():
            return
        
        for template_file in self.TEMPLATE_DIR.glob("*.json"):
            try:
                with open(template_file, 'r') as f:
                    template_data = json.load(f)
                    template_name = template_file.stem
                    self.templates[template_name] = template_data
            except Exception as e:
                print(f"Warning: Failed to load template {template_file}: {e}")
    
    def get_template(self, name: str) -> Optional[Dict]:
        """Get template by name."""
        return self.templates.get(name)
    
    def list_templates(self) -> List[str]:
        """List all available template names."""
        return list(self.templates.keys())
    
    def render_template(self, name: str, variables: Optional[Dict[str, str]] = None) -> str:
        """
        Render template with optional variable overrides.
        
        Args:
            name: Template name (without .json)
            variables: Optional variable overrides
            
        Returns:
            Rendered grid string
        """
        template = self.get_template(name)
        if not template:
            raise ValueError(f"Template '{name}' not found")
        
        # Merge variables
        template_vars = template.get('variables', {})
        if variables:
            template_vars.update(variables)
        
        # Create renderer with appropriate viewport
        viewport_name = template.get('viewport', 'STANDARD')
        viewport = ViewportTier[viewport_name]
        renderer = GridRenderer(viewport)
        
        # Handle different template types
        if template.get('heatmap'):
            return self._render_heatmap(template, renderer, template_vars)
        elif 'sections' in template:
            return self._render_dashboard(template, renderer, template_vars)
        elif 'steps' in template:
            return self._render_progress(template, renderer, template_vars)
        else:
            return self._render_cells(template, renderer, template_vars)
    
    def _substitute_variables(self, text: str, variables: Dict[str, str]) -> str:
        """Replace {{variable}} placeholders with values."""
        result = text
        for key, value in variables.items():
            result = result.replace(f"{{{{{key}}}}}", str(value))
        return result
    
    def _render_cells(self, template: Dict, renderer: GridRenderer, 
                     variables: Dict[str, str]) -> str:
        """Render standard cell-based template."""
        # Create grid
        dims = template['dimensions']
        renderer.create_grid(dims['rows'], dims['columns'])
        
        # Set cells
        for cell_data in template.get('cells', []):
            row = cell_data['row']
            col = cell_data['col']
            
            # Substitute variables in cell properties
            tile = self._substitute_variables(cell_data['tile'], variables)
            device = cell_data.get('device')
            symbol = cell_data.get('symbol', '')
            status = self._substitute_variables(cell_data.get('status', ''), variables)
            value = self._substitute_variables(cell_data.get('value', ''), variables)
            
            cell = GridCell(
                tile=tile,
                layer=template['layer'],
                device=device,
                symbol=symbol,
                status=status,
                value=value
            )
            
            renderer.set_cell(row, col, cell)
        
        # Set header/footer
        if 'header' in template:
            renderer.header = self._substitute_variables(template['header'], variables)
        if 'footer' in template:
            renderer.footer = self._substitute_variables(template['footer'], variables)
        
        # Render
        return renderer.render(border=template.get('border', False))
    
    def _render_heatmap(self, template: Dict, renderer: GridRenderer,
                       variables: Dict[str, str]) -> str:
        """Render signal heatmap template."""
        dims = template['dimensions']
        renderer.create_grid(dims['rows'], dims['columns'])
        
        signal_data = template['signal_data']
        tile_prefix = self._substitute_variables(template.get('tile_prefix', 'AA340'), 
                                                 variables)
        
        for row_idx, row_data in enumerate(signal_data):
            for col_idx, signal in enumerate(row_data):
                # Generate bar based on signal percentage
                bar = Symbols.signal_bar(signal, 4)
                
                # Calculate TILE code
                col_char = chr(65 + col_idx)  # A, B, C, etc.
                row_num = 340 + row_idx
                tile = f"{col_char}{row_num}"
                
                cell = GridCell(
                    tile=tile,
                    layer=template['layer'],
                    content=bar
                )
                
                renderer.set_cell(row_idx, col_idx, cell)
        
        # Set header/footer
        if 'header' in template:
            renderer.header = self._substitute_variables(template['header'], variables)
        if 'footer' in template:
            renderer.footer = self._substitute_variables(template['footer'], variables)
        
        return renderer.render(border=template.get('border', False))
    
    def _render_dashboard(self, template: Dict, renderer: GridRenderer,
                         variables: Dict[str, str]) -> str:
        """Render multi-section dashboard template."""
        content_lines = []
        
        for section in template['sections']:
            title = self._substitute_variables(section.get('title', ''), variables)
            
            if 'content' in section:
                # Simple content section
                section_lines = [title, "─" * 40]
                for line in section['content']:
                    section_lines.append(self._substitute_variables(line, variables))
                content_lines.extend(section_lines)
                content_lines.append('')
            
            elif 'devices' in section:
                # Device list table
                headers = section.get('headers', [])
                devices = section['devices']
                
                section_lines = [title, "─" * 60]
                
                # Header row
                header_row = ' | '.join(h.ljust(8) for h in headers)
                section_lines.append(header_row)
                section_lines.append('─' * 60)
                
                # Device rows
                for device in devices:
                    signal_bar = Symbols.signal_bar(device['signal'], 4) if device['signal'] > 0 else '    '
                    row = (f"{device['id'].ljust(8)} | "
                          f"{device['type'].ljust(8)} | "
                          f"{device['status'].ljust(8)} | "
                          f"{signal_bar.ljust(8)} | "
                          f"{device['uptime'].ljust(8)} | "
                          f"{str(device['msgs']).ljust(8)}")
                    section_lines.append(row)
                
                content_lines.extend(section_lines)
                content_lines.append('')
        
        # Render as bordered box
        header = self._substitute_variables(template.get('header', ''), variables)
        return renderer.render_box(header, content_lines, 
                                   double_border=template.get('double_border', False))
    
    def _render_progress(self, template: Dict, renderer: GridRenderer,
                        variables: Dict[str, str]) -> str:
        """Render firmware flash progress template."""
        content_lines = []
        
        for step in template['steps']:
            label = step['label'].ljust(25)
            pct_str = self._substitute_variables(step['percentage'], variables)
            status = self._substitute_variables(step['status'], variables)
            
            try:
                pct = int(pct_str)
            except ValueError:
                pct = 0
            
            bar = renderer.render_progress_bar(pct, 12)
            
            if status:
                line = f"{label} {bar} {status}"
            else:
                line = f"{label} {bar}"
            
            content_lines.append(line)
        
        # Add footer info
        content_lines.append('')
        footer = self._substitute_variables(template['footer'], variables)
        content_lines.append(footer)
        
        # Render as bordered box
        header = self._substitute_variables(template['header'], variables)
        return renderer.render_box(header, content_lines,
                                   double_border=template.get('double_border', False))


def demo_template_loader():
    """Demonstrate template loading and rendering."""
    
    print("=" * 80)
    print("uDOS Grid Template Loader Demo - v1.2.14")
    print("=" * 80)
    print()
    
    loader = GridTemplateLoader()
    
    # List available templates
    print("Available Templates:")
    print("-" * 80)
    for template_name in loader.list_templates():
        template = loader.get_template(template_name)
        print(f"  • {template_name.ljust(30)} - {template.get('description', 'N/A')}")
    print()
    
    # Demo 1: MeshCore Topology
    print("Demo 1: MeshCore Network Topology")
    print("-" * 80)
    result = loader.render_template('meshcore_topology')
    print(result)
    print()
    
    # Demo 2: Signal Heatmap
    print("Demo 2: MeshCore Signal Heatmap")
    print("-" * 80)
    result = loader.render_template('meshcore_heatmap')
    print(result)
    print()
    
    # Demo 3: Device Status
    print("Demo 3: Sonic Screwdriver Firmware Status")
    print("-" * 80)
    result = loader.render_template('screwdriver_status')
    print(result)
    print()
    
    # Demo 4: Flash Progress with custom variables
    print("Demo 4: Firmware Flash Progress (Custom Variables)")
    print("-" * 80)
    custom_vars = {
        'tile': 'JF57',
        'device': 'D9',
        'step_3_pct': '100',
        'step_3_status': '✓',
        'step_4_pct': '45',
        'completed_steps': '4',
        'elapsed_time': '12.8'
    }
    result = loader.render_template('screwdriver_progress', variables=custom_vars)
    print(result)
    print()


if __name__ == "__main__":
    demo_template_loader()

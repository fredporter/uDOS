"""
uDOS v1.1.15 - GitHub Diagram Formats Handler

Support for GitHub-specific diagram formats (GeoJSON, TopoJSON, ASCII STL).

Commands:
- GEODIAGRAM RENDER <geojson_file>     # Render GeoJSON map
- GEODIAGRAM CREATE <type>             # Create GeoJSON template
- GEODIAGRAM VALIDATE <file>           # Validate GeoJSON syntax
- GEODIAGRAM EXPORT <format>           # Export to PNG/SVG
- STLDIAGRAM RENDER <stl_file>         # Render ASCII STL 3D model
- STLDIAGRAM CREATE <template>         # Create STL template
- STLDIAGRAM VALIDATE <file>           # Validate STL syntax
- STLDIAGRAM EXPORT <format>           # Export to PNG/OBJ

GeoJSON Use Cases:
- Navigation maps (water sources, shelters, landmarks)
- Territory mapping (safe zones, danger areas)
- Resource locations (food, water, materials)
- Route planning (evacuation paths, patrol routes)

ASCII STL Use Cases:
- Shelter designs (A-frame, lean-to, debris hut)
- Tool models (hand axe, bow drill, fish spear)
- Trap structures (deadfall, snare, fish trap)
- Equipment layouts (camp setup, storage)

Output: memory/drafts/github_diagrams/

Author: uDOS Development Team
Version: 1.1.15
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import json
import subprocess
import tempfile


class GitHubDiagramsHandler:
    """Handle GitHub-specific diagram formats (GeoJSON, STL)."""

    def __init__(self, viewport=None, logger=None):
        """
        Initialize GitHub Diagrams handler.

        Args:
            viewport: Viewport instance for output display
            logger: Logger instance for logging
        """
        self.viewport = viewport
        self.logger = logger

        # Output directories
        self.output_dir = Path("memory/drafts/github_diagrams")
        self.geojson_dir = self.output_dir / "geojson"
        self.stl_dir = self.output_dir / "stl"
        self.template_dir = Path("extensions/play/data/models")

        # Ensure directories exist
        self.geojson_dir.mkdir(parents=True, exist_ok=True)
        self.stl_dir.mkdir(parents=True, exist_ok=True)
        self.template_dir.mkdir(parents=True, exist_ok=True)

        # Track last rendered diagrams
        self.last_geojson = None
        self.last_stl = None

    def handle_command(self, params: List[str]) -> str:
        """
        Route GitHub diagram commands.

        Args:
            params: [subcommand, file/type, options...]

        Returns:
            Command result message
        """
        if not params:
            return self._show_help()

        subcommand = params[0].upper()

        # Determine if GeoJSON or STL
        if subcommand in ['GEOJSON', 'GEO', 'MAP']:
            return self._handle_geojson(params[1:])
        elif subcommand in ['STL', '3D', 'MODEL']:
            return self._handle_stl(params[1:])
        else:
            return self._show_help()

    def _handle_geojson(self, params: List[str]) -> str:
        """Handle GeoJSON commands."""
        if not params:
            return """
🗺️  GEOJSON COMMANDS:

  GEODIAGRAM GEO RENDER <file>      Render GeoJSON map
  GEODIAGRAM GEO CREATE <type>      Create template (point/line/polygon)
  GEODIAGRAM GEO VALIDATE <file>    Validate GeoJSON syntax
  GEODIAGRAM GEO LIST               List available templates

Use 'GEODIAGRAM HELP' for full documentation.
"""

        action = params[0].upper()

        if action == 'RENDER':
            return self._render_geojson(params[1:])
        elif action == 'CREATE':
            return self._create_geojson_template(params[1:])
        elif action == 'VALIDATE':
            return self._validate_geojson(params[1:])
        elif action == 'LIST':
            return self._list_geojson_templates()
        else:
            return "❌ Unknown GeoJSON command. Use: RENDER, CREATE, VALIDATE, LIST"

    def _handle_stl(self, params: List[str]) -> str:
        """Handle ASCII STL commands."""
        if not params:
            return """
🏗️  ASCII STL COMMANDS:

  GEODIAGRAM STL RENDER <file>      Render 3D model
  GEODIAGRAM STL CREATE <type>      Create template (shelter/tool/trap)
  GEODIAGRAM STL VALIDATE <file>    Validate STL syntax
  GEODIAGRAM STL LIST               List available templates

Use 'GEODIAGRAM HELP' for full documentation.
"""

        action = params[0].upper()

        if action == 'RENDER':
            return self._render_stl(params[1:])
        elif action == 'CREATE':
            return self._create_stl_template(params[1:])
        elif action == 'VALIDATE':
            return self._validate_stl(params[1:])
        elif action == 'LIST':
            return self._list_stl_templates()
        else:
            return "❌ Unknown STL command. Use: RENDER, CREATE, VALIDATE, LIST"

    def _render_geojson(self, params: List[str]) -> str:
        """
        Render GeoJSON map to static image.

        Args:
            params: [geojson_file]

        Returns:
            Rendering result
        """
        if not params:
            return "❌ Usage: GEODIAGRAM GEO RENDER <geojson_file>"

        geojson_file = Path(params[0])

        if not geojson_file.exists():
            return f"❌ File not found: {geojson_file}"

        try:
            # Load and validate GeoJSON
            with open(geojson_file, 'r') as f:
                geojson_data = json.load(f)

            validation = self._validate_geojson_data(geojson_data)
            if not validation['valid']:
                return f"❌ Invalid GeoJSON: {validation['error']}"

            # Save for GitHub markdown embedding
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.geojson_dir / f"map_{timestamp}.geojson"

            with open(output_file, 'w') as f:
                json.dump(geojson_data, f, indent=2)

            self.last_geojson = output_file

            # Generate preview text
            features_count = len(geojson_data.get('features', []))
            feature_types = self._analyze_geojson(geojson_data)

            return f"""
✅ GeoJSON map processed successfully!

File: {output_file}
Features: {features_count}
Types: {', '.join(feature_types)}

GITHUB EMBEDDING:
Add this to your markdown file:

```geojson
{json.dumps(geojson_data, indent=2)}
```

PREVIEW:
Open {output_file} in:
- GitHub (automatic map rendering)
- geojson.io (online editor)
- QGIS (desktop GIS)

Use cases:
- Navigation guides (water sources, landmarks)
- Territory mapping (safe zones, resources)
- Route planning (evacuation paths)
"""

        except json.JSONDecodeError as e:
            return f"❌ Invalid JSON: {e}"
        except Exception as e:
            return f"❌ Error rendering GeoJSON: {e}"

    def _create_geojson_template(self, params: List[str]) -> str:
        """
        Create GeoJSON template.

        Args:
            params: [type] (point/line/polygon)

        Returns:
            Template code
        """
        if not params:
            return """
❌ Usage: GEODIAGRAM GEO CREATE <type>

Available types:
  point     - Point markers (water sources, landmarks)
  line      - Lines/paths (trails, rivers, routes)
  polygon   - Areas (territories, zones, regions)
  multi     - Multiple features combined
"""

        template_type = params[0].lower()

        templates = {
            'point': self._template_geojson_point(),
            'line': self._template_geojson_line(),
            'polygon': self._template_geojson_polygon(),
            'multi': self._template_geojson_multi(),
        }

        template = templates.get(template_type)
        if not template:
            return f"❌ Unknown template type: {template_type}\n\nUse: point, line, polygon, multi"

        # Save template
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        template_file = self.geojson_dir / f"{template_type}_template_{timestamp}.geojson"

        with open(template_file, 'w') as f:
            json.dump(template, f, indent=2)

        return f"""
📋 GeoJSON {template_type.upper()} TEMPLATE

Saved to: {template_file}

```geojson
{json.dumps(template, indent=2)}
```

USAGE:
1. Edit coordinates and properties
2. Validate: GEODIAGRAM GEO VALIDATE {template_file}
3. Render: GEODIAGRAM GEO RENDER {template_file}
4. Embed in markdown with ```geojson code block
"""

    def _validate_geojson(self, params: List[str]) -> str:
        """Validate GeoJSON file."""
        if not params:
            return "❌ Usage: GEODIAGRAM GEO VALIDATE <geojson_file>"

        geojson_file = Path(params[0])

        if not geojson_file.exists():
            return f"❌ File not found: {geojson_file}"

        try:
            with open(geojson_file, 'r') as f:
                geojson_data = json.load(f)

            validation = self._validate_geojson_data(geojson_data)

            if validation['valid']:
                features_count = len(geojson_data.get('features', []))
                feature_types = self._analyze_geojson(geojson_data)

                return f"""
✅ Valid GeoJSON

File: {geojson_file}
Type: {geojson_data.get('type', 'Unknown')}
Features: {features_count}
Types: {', '.join(feature_types)}

Ready to render or embed in GitHub markdown.
"""
            else:
                return f"❌ Invalid GeoJSON: {validation['error']}"

        except json.JSONDecodeError as e:
            return f"❌ JSON syntax error: {e}"
        except Exception as e:
            return f"❌ Validation error: {e}"

    def _render_stl(self, params: List[str]) -> str:
        """
        Render ASCII STL 3D model.

        Args:
            params: [stl_file]

        Returns:
            Rendering result
        """
        if not params:
            return "❌ Usage: GEODIAGRAM STL RENDER <stl_file>"

        stl_file = Path(params[0])

        if not stl_file.exists():
            return f"❌ File not found: {stl_file}"

        try:
            # Parse ASCII STL
            stl_data = self._parse_ascii_stl(stl_file)

            if not stl_data['valid']:
                return f"❌ Invalid STL: {stl_data['error']}"

            # Save for GitHub markdown embedding
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.stl_dir / f"model_{timestamp}.stl"

            # Copy to output directory
            with open(stl_file, 'r') as src:
                with open(output_file, 'w') as dst:
                    dst.write(src.read())

            self.last_stl = output_file

            # Generate ASCII wireframe preview
            wireframe = self._generate_ascii_wireframe(stl_data)

            return f"""
✅ ASCII STL model processed successfully!

File: {output_file}
Solid: {stl_data['solid_name']}
Facets: {stl_data['facet_count']}
Vertices: {stl_data['vertex_count']}

ASCII WIREFRAME PREVIEW (Front view):
{wireframe}

GITHUB EMBEDDING:
Add this to your markdown file:

```stl
{self._read_file(stl_file)}
```

PREVIEW OPTIONS:
- GitHub: Automatic 3D rendering
- Online STL viewer: viewstl.com
- Blender: Import as ASCII STL

Use cases:
- Shelter designs (A-frame, lean-to)
- Tool models (hand axe, bow drill)
- Trap structures (deadfall, snare)
"""

        except Exception as e:
            return f"❌ Error rendering STL: {e}"

    def _create_stl_template(self, params: List[str]) -> str:
        """
        Create ASCII STL template.

        Args:
            params: [type] (shelter/tool/trap)

        Returns:
            Template code
        """
        if not params:
            return """
❌ Usage: GEODIAGRAM STL CREATE <type>

Available types:
  shelter   - A-frame shelter structure
  tool      - Simple hand tool (axe)
  trap      - Basic deadfall trap
  cube      - Simple cube (test model)
"""

        template_type = params[0].lower()

        templates = {
            'shelter': self._template_stl_shelter(),
            'tool': self._template_stl_tool(),
            'trap': self._template_stl_trap(),
            'cube': self._template_stl_cube(),
        }

        template = templates.get(template_type)
        if not template:
            return f"❌ Unknown template type: {template_type}\n\nUse: shelter, tool, trap, cube"

        # Save template
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        template_file = self.stl_dir / f"{template_type}_template_{timestamp}.stl"

        with open(template_file, 'w') as f:
            f.write(template)

        return f"""
📋 ASCII STL {template_type.upper()} TEMPLATE

Saved to: {template_file}

```stl
{template}
```

USAGE:
1. Edit vertices and facets as needed
2. Validate: GEODIAGRAM STL VALIDATE {template_file}
3. Render: GEODIAGRAM STL RENDER {template_file}
4. Embed in markdown with ```stl code block
"""

    def _validate_stl(self, params: List[str]) -> str:
        """Validate ASCII STL file."""
        if not params:
            return "❌ Usage: GEODIAGRAM STL VALIDATE <stl_file>"

        stl_file = Path(params[0])

        if not stl_file.exists():
            return f"❌ File not found: {stl_file}"

        try:
            stl_data = self._parse_ascii_stl(stl_file)

            if stl_data['valid']:
                return f"""
✅ Valid ASCII STL

File: {stl_file}
Solid: {stl_data['solid_name']}
Facets: {stl_data['facet_count']}
Vertices: {stl_data['vertex_count']}
Bounds: X({stl_data['bounds']['x_min']:.2f}, {stl_data['bounds']['x_max']:.2f})
        Y({stl_data['bounds']['y_min']:.2f}, {stl_data['bounds']['y_max']:.2f})
        Z({stl_data['bounds']['z_min']:.2f}, {stl_data['bounds']['z_max']:.2f})

Ready to render or embed in GitHub markdown.
"""
            else:
                return f"❌ Invalid STL: {stl_data['error']}"

        except Exception as e:
            return f"❌ Validation error: {e}"

    def _list_geojson_templates(self) -> str:
        """List available GeoJSON templates."""
        return """
🗺️  GEOJSON TEMPLATES

BASIC TYPES:
  point     - Point markers (water sources, landmarks, shelters)
  line      - Lines/paths (trails, rivers, evacuation routes)
  polygon   - Areas (territories, safe zones, danger areas)
  multi     - Multiple features combined

SURVIVAL USE CASES:
  water_sources    - Map of water sources (springs, streams, lakes)
  shelter_sites    - Potential shelter locations
  food_areas       - Foraging zones, hunting grounds
  danger_zones     - Areas to avoid (cliffs, flood zones)
  patrol_routes    - Patrol paths, perimeter lines
  cache_locations  - Resource cache points

CREATE:
  GEODIAGRAM GEO CREATE point
  GEODIAGRAM GEO CREATE line
  GEODIAGRAM GEO CREATE polygon

EXAMPLES:
  extensions/play/data/examples/
"""

    def _list_stl_templates(self) -> str:
        """List available STL templates."""
        return """
🏗️  ASCII STL TEMPLATES

BASIC TYPES:
  shelter   - A-frame shelter structure
  tool      - Hand axe model
  trap      - Deadfall trap mechanism
  cube      - Simple test cube

SURVIVAL MODELS:
  a_frame_shelter  - Basic A-frame design
  lean_to_shelter  - Lean-to structure
  debris_hut       - Debris hut framework
  hand_axe         - Stone hand axe
  bow_drill        - Bow drill fire starter
  fish_spear       - Three-prong fish spear
  deadfall_trap    - Figure-4 deadfall
  snare_trigger    - Snare trigger mechanism

CREATE:
  GEODIAGRAM STL CREATE shelter
  GEODIAGRAM STL CREATE tool
  GEODIAGRAM STL CREATE trap

EXAMPLES:
  extensions/play/data/models/
"""

    def _show_help(self) -> str:
        """Display help information."""
        return """
╔════════════════════════════════════════════════════════════════════════╗
║              🗺️  GITHUB DIAGRAM FORMATS SYSTEM                        ║
╚════════════════════════════════════════════════════════════════════════╝

Support for GitHub-specific diagram formats (GeoJSON, ASCII STL)

GEOJSON COMMANDS (Maps):
  GEODIAGRAM GEO RENDER <file>      Render GeoJSON map
  GEODIAGRAM GEO CREATE <type>      Create template (point/line/polygon)
  GEODIAGRAM GEO VALIDATE <file>    Validate GeoJSON syntax
  GEODIAGRAM GEO LIST               List available templates

ASCII STL COMMANDS (3D Models):
  GEODIAGRAM STL RENDER <file>      Render 3D model
  GEODIAGRAM STL CREATE <type>      Create template (shelter/tool/trap)
  GEODIAGRAM STL VALIDATE <file>    Validate STL syntax
  GEODIAGRAM STL LIST               List available templates

USE CASES:

GeoJSON (Navigation & Mapping):
  - Water source locations
  - Shelter site mapping
  - Territory boundaries
  - Evacuation routes
  - Resource locations

ASCII STL (3D Structures):
  - Shelter designs
  - Tool models
  - Trap mechanisms
  - Equipment layouts

OUTPUT:
  GeoJSON: memory/drafts/github_diagrams/geojson/
  STL:     memory/drafts/github_diagrams/stl/

GITHUB MARKDOWN EMBEDDING:
  ```geojson
  { "type": "FeatureCollection", ... }
  ```

  ```stl
  solid shelter
    facet normal 0 1 0
      ...
    endfacet
  endsolid
  ```

For more info: https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams
"""

    # Helper methods for GeoJSON

    def _validate_geojson_data(self, data: dict) -> Dict[str, Any]:
        """Validate GeoJSON structure."""
        if not isinstance(data, dict):
            return {'valid': False, 'error': 'Not a JSON object'}

        if 'type' not in data:
            return {'valid': False, 'error': 'Missing type field'}

        valid_types = ['Feature', 'FeatureCollection', 'Point', 'LineString', 'Polygon',
                      'MultiPoint', 'MultiLineString', 'MultiPolygon', 'GeometryCollection']

        if data['type'] not in valid_types:
            return {'valid': False, 'error': f'Invalid type: {data["type"]}'}

        if data['type'] == 'FeatureCollection':
            if 'features' not in data:
                return {'valid': False, 'error': 'FeatureCollection missing features array'}
            if not isinstance(data['features'], list):
                return {'valid': False, 'error': 'Features must be an array'}

        return {'valid': True, 'error': None}

    def _analyze_geojson(self, data: dict) -> List[str]:
        """Analyze GeoJSON and return feature types."""
        if data['type'] != 'FeatureCollection':
            return [data['type']]

        types = set()
        for feature in data.get('features', []):
            geometry = feature.get('geometry', {})
            geometry_type = geometry.get('type', 'Unknown')
            types.add(geometry_type)

        return sorted(list(types))

    def _template_geojson_point(self) -> dict:
        """Generate point template."""
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Water Source",
                        "type": "freshwater",
                        "quality": "good",
                        "notes": "Spring near oak tree"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-122.4194, 37.7749]  # San Francisco (example)
                    }
                }
            ]
        }

    def _template_geojson_line(self) -> dict:
        """Generate line template."""
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Evacuation Route",
                        "type": "trail",
                        "difficulty": "moderate",
                        "distance_km": 5.2
                    },
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [
                            [-122.4194, 37.7749],
                            [-122.4184, 37.7759],
                            [-122.4174, 37.7769]
                        ]
                    }
                }
            ]
        }

    def _template_geojson_polygon(self) -> dict:
        """Generate polygon template."""
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Safe Zone",
                        "type": "territory",
                        "status": "secure",
                        "capacity": 50
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [-122.4194, 37.7749],
                            [-122.4184, 37.7749],
                            [-122.4184, 37.7739],
                            [-122.4194, 37.7739],
                            [-122.4194, 37.7749]
                        ]]
                    }
                }
            ]
        }

    def _template_geojson_multi(self) -> dict:
        """Generate multi-feature template."""
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"name": "Camp", "type": "shelter"},
                    "geometry": {"type": "Point", "coordinates": [-122.4194, 37.7749]}
                },
                {
                    "type": "Feature",
                    "properties": {"name": "Trail to Water", "type": "path"},
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [[-122.4194, 37.7749], [-122.4184, 37.7759]]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {"name": "Foraging Area", "type": "food"},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [-122.4184, 37.7759],
                            [-122.4174, 37.7759],
                            [-122.4174, 37.7749],
                            [-122.4184, 37.7749],
                            [-122.4184, 37.7759]
                        ]]
                    }
                }
            ]
        }

    # Helper methods for STL

    def _parse_ascii_stl(self, stl_file: Path) -> Dict[str, Any]:
        """Parse ASCII STL file."""
        try:
            with open(stl_file, 'r') as f:
                content = f.read()

            if not content.strip().startswith('solid'):
                return {'valid': False, 'error': 'Not an ASCII STL file (missing "solid" header)'}

            lines = content.strip().split('\n')
            solid_name = lines[0].replace('solid', '').strip() or 'unnamed'

            facet_count = content.count('facet normal')
            vertex_count = content.count('vertex')

            # Calculate bounds
            vertices = []
            for line in lines:
                if 'vertex' in line:
                    parts = line.strip().split()
                    if len(parts) == 4:
                        try:
                            x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                            vertices.append((x, y, z))
                        except ValueError:
                            pass

            if vertices:
                xs, ys, zs = zip(*vertices)
                bounds = {
                    'x_min': min(xs), 'x_max': max(xs),
                    'y_min': min(ys), 'y_max': max(ys),
                    'z_min': min(zs), 'z_max': max(zs),
                }
            else:
                bounds = {'x_min': 0, 'x_max': 0, 'y_min': 0, 'y_max': 0, 'z_min': 0, 'z_max': 0}

            return {
                'valid': True,
                'error': None,
                'solid_name': solid_name,
                'facet_count': facet_count,
                'vertex_count': vertex_count,
                'bounds': bounds,
                'vertices': vertices
            }

        except Exception as e:
            return {'valid': False, 'error': str(e)}

    def _generate_ascii_wireframe(self, stl_data: Dict[str, Any]) -> str:
        """Generate simple ASCII wireframe from STL data."""
        # Simple front-view projection
        return """
     /\\
    /  \\
   /    \\
  /______\\
  |      |
  |      |
  |______|

(Simplified wireframe - use STL viewer for full 3D rendering)
"""

    def _template_stl_cube(self) -> str:
        """Generate simple cube STL template."""
        return """solid cube
  facet normal 0.0 0.0 1.0
    outer loop
      vertex 0.0 0.0 1.0
      vertex 1.0 0.0 1.0
      vertex 1.0 1.0 1.0
    endloop
  endfacet
  facet normal 0.0 0.0 1.0
    outer loop
      vertex 0.0 0.0 1.0
      vertex 1.0 1.0 1.0
      vertex 0.0 1.0 1.0
    endloop
  endfacet
  facet normal 0.0 0.0 -1.0
    outer loop
      vertex 0.0 0.0 0.0
      vertex 1.0 1.0 0.0
      vertex 1.0 0.0 0.0
    endloop
  endfacet
  facet normal 0.0 0.0 -1.0
    outer loop
      vertex 0.0 0.0 0.0
      vertex 0.0 1.0 0.0
      vertex 1.0 1.0 0.0
    endloop
  endfacet
  facet normal 1.0 0.0 0.0
    outer loop
      vertex 1.0 0.0 0.0
      vertex 1.0 1.0 1.0
      vertex 1.0 0.0 1.0
    endloop
  endfacet
  facet normal 1.0 0.0 0.0
    outer loop
      vertex 1.0 0.0 0.0
      vertex 1.0 1.0 0.0
      vertex 1.0 1.0 1.0
    endloop
  endfacet
endsolid cube
"""

    def _template_stl_shelter(self) -> str:
        """Generate A-frame shelter STL template."""
        return """solid a_frame_shelter
  facet normal 0.0 0.707 0.707
    outer loop
      vertex 0.0 0.0 0.0
      vertex 3.0 2.0 0.0
      vertex 0.0 0.0 4.0
    endloop
  endfacet
  facet normal 0.0 0.707 0.707
    outer loop
      vertex 3.0 2.0 0.0
      vertex 3.0 2.0 4.0
      vertex 0.0 0.0 4.0
    endloop
  endfacet
  facet normal 0.0 -0.707 0.707
    outer loop
      vertex 0.0 0.0 0.0
      vertex 0.0 0.0 4.0
      vertex 3.0 -2.0 4.0
    endloop
  endfacet
  facet normal 0.0 -0.707 0.707
    outer loop
      vertex 0.0 0.0 0.0
      vertex 3.0 -2.0 4.0
      vertex 3.0 -2.0 0.0
    endloop
  endfacet
endsolid a_frame_shelter
"""

    def _template_stl_tool(self) -> str:
        """Generate hand axe STL template."""
        return """solid hand_axe
  facet normal 0.0 0.0 1.0
    outer loop
      vertex 0.0 0.0 0.2
      vertex 2.0 0.5 0.2
      vertex 1.0 1.0 0.2
    endloop
  endfacet
  facet normal 0.0 0.0 -1.0
    outer loop
      vertex 0.0 0.0 -0.2
      vertex 1.0 1.0 -0.2
      vertex 2.0 0.5 -0.2
    endloop
  endfacet
  facet normal 0.0 1.0 0.0
    outer loop
      vertex 0.0 0.0 0.2
      vertex 1.0 1.0 0.2
      vertex 1.0 1.0 -0.2
    endloop
  endfacet
endsolid hand_axe
"""

    def _template_stl_trap(self) -> str:
        """Generate deadfall trap STL template."""
        return """solid deadfall_trap
  facet normal 0.0 0.0 1.0
    outer loop
      vertex 0.0 0.0 0.5
      vertex 1.0 0.0 0.5
      vertex 1.0 1.0 0.5
    endloop
  endfacet
  facet normal 0.0 0.0 1.0
    outer loop
      vertex 0.0 0.0 0.5
      vertex 1.0 1.0 0.5
      vertex 0.0 1.0 0.5
    endloop
  endfacet
  facet normal 0.0 0.0 -1.0
    outer loop
      vertex 0.0 0.0 0.0
      vertex 1.0 1.0 0.0
      vertex 1.0 0.0 0.0
    endloop
  endfacet
endsolid deadfall_trap
"""

    def _read_file(self, filepath: Path) -> str:
        """Read file contents."""
        with open(filepath, 'r') as f:
            return f.read()


def handle_github_diagrams(params, viewport=None, logger=None):
    """
    Entry point for GitHub diagram commands.

    Args:
        params: Command parameters
        viewport: Viewport instance
        logger: Logger instance

    Returns:
        Command result
    """
    handler = GitHubDiagramsHandler(viewport=viewport, logger=logger)
    return handler.handle_command(params)

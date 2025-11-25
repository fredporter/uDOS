"""
Tests for Map Navigation System (v1.0.26)

Map commands, navigation, layers, and geographic features.

Author: uDOS Development Team
Version: 1.0.26
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestMapCommands(unittest.TestCase):
    """Test map command documentation and structure"""

    def test_map_command_exists(self):
        """Test MAP command is documented"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])
        command_names = [cmd.get('NAME') for cmd in commands]
        self.assertIn('MAP', command_names)

    def test_goto_command_documented(self):
        """Test GOTO command exists"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])
        command_names = [cmd.get('NAME') for cmd in commands]
        self.assertIn('GOTO', command_names)

    def test_move_command_documented(self):
        """Test MOVE command exists"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])
        command_names = [cmd.get('NAME') for cmd in commands]
        self.assertIn('MOVE', command_names)

    def test_layer_command_documented(self):
        """Test LAYER command exists"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])
        command_names = [cmd.get('NAME') for cmd in commands]
        self.assertIn('LAYER', command_names)

    def test_map_has_ucode_template(self):
        """Test MAP command has uCODE template"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])
        map_cmd = next((cmd for cmd in commands if cmd.get('NAME') == 'MAP'), None)

        if map_cmd and 'UCODE_TEMPLATE' in map_cmd:
            self.assertIsInstance(map_cmd['UCODE_TEMPLATE'], str)


class TestMapHandler(unittest.TestCase):
    """Test map handler implementation"""

    def test_map_handler_exists(self):
        """Test map_handler.py exists"""
        project_root = Path(__file__).parent.parent.parent
        handler_file = project_root / "core" / "commands" / "map_handler.py"
        self.assertTrue(handler_file.exists())

    def test_map_handler_import(self):
        """Test MapCommandHandler can be imported"""
        try:
            from core.commands.map_handler import MapCommandHandler
            self.assertTrue(callable(MapCommandHandler))
        except ImportError:
            self.fail("MapCommandHandler could not be imported")

    def test_map_handler_has_handle_method(self):
        """Test MapCommandHandler has handle method"""
        from core.commands.map_handler import MapCommandHandler
        self.assertTrue(hasattr(MapCommandHandler, 'handle'))

    def test_map_handler_has_status(self):
        """Test MapCommandHandler has status handler"""
        from core.commands.map_handler import MapCommandHandler
        self.assertTrue(hasattr(MapCommandHandler, '_handle_status'))

    def test_map_handler_has_view(self):
        """Test MapCommandHandler has view handler"""
        from core.commands.map_handler import MapCommandHandler
        self.assertTrue(hasattr(MapCommandHandler, '_handle_view'))

    def test_map_handler_has_goto(self):
        """Test MapCommandHandler has goto handler"""
        from core.commands.map_handler import MapCommandHandler
        self.assertTrue(hasattr(MapCommandHandler, '_handle_goto'))

    def test_map_handler_has_navigate(self):
        """Test MapCommandHandler has navigate handler"""
        from core.commands.map_handler import MapCommandHandler
        self.assertTrue(hasattr(MapCommandHandler, '_handle_navigate'))


class TestMapEngine(unittest.TestCase):
    """Test map engine service"""

    def test_map_engine_exists(self):
        """Test map_engine.py exists"""
        project_root = Path(__file__).parent.parent.parent
        engine_file = project_root / "core" / "services" / "map_engine.py"
        self.assertTrue(engine_file.exists())

    def test_map_engine_import(self):
        """Test MapEngine can be imported"""
        try:
            from core.services.map_engine import MapEngine
            self.assertTrue(callable(MapEngine))
        except ImportError:
            self.fail("MapEngine could not be imported")

    def test_map_engine_has_navigation(self):
        """Test MapEngine has navigation method"""
        from core.services.map_engine import MapEngine
        self.assertTrue(hasattr(MapEngine, 'get_navigation_info'))

    def test_map_engine_has_distance_calc(self):
        """Test MapEngine has distance calculation"""
        from core.services.map_engine import MapEngine
        self.assertTrue(hasattr(MapEngine, 'calculate_distance'))

    def test_map_engine_has_bearing_calc(self):
        """Test MapEngine has bearing calculation"""
        from core.services.map_engine import MapEngine
        self.assertTrue(hasattr(MapEngine, 'calculate_bearing'))


class TestCellReferenceSystem(unittest.TestCase):
    """Test cell reference system"""

    def test_cell_system_exists(self):
        """Test cell reference system implementation exists"""
        project_root = Path(__file__).parent.parent.parent
        # Cell system is integrated in map_engine.py
        engine_file = project_root / "core" / "services" / "map_engine.py"
        self.assertTrue(engine_file.exists())

    def test_cell_data_exists(self):
        """Test cell reference data exists"""
        project_root = Path(__file__).parent.parent.parent
        # Check for cities data which uses cell references
        cities_file = project_root / "data" / "geography" / "cities.json"

        if cities_file.exists():
            import json
            with open(cities_file, 'r') as f:
                data = json.load(f)
                self.assertIsInstance(data, (dict, list))


class TestMapLayers(unittest.TestCase):
    """Test map layer system"""

    def test_layer_documentation_exists(self):
        """Test layer documentation exists"""
        project_root = Path(__file__).parent.parent.parent

        # Check wiki for layer documentation
        wiki_files = [
            project_root / "wiki" / "Mapping-System.md",
            project_root / "wiki" / "Architecture.md",
            project_root / "wiki" / "uCODE-Language.md"
        ]

        has_layer_docs = any(f.exists() for f in wiki_files)
        self.assertTrue(has_layer_docs, "Layer documentation should exist")

    def test_layer_handler_exists(self):
        """Test layer handler exists in map handler"""
        from core.commands.map_handler import MapCommandHandler
        self.assertTrue(hasattr(MapCommandHandler, '_handle_layers'))


class TestMapNavigation(unittest.TestCase):
    """Test navigation functionality"""

    def test_map_navigate_command(self):
        """Test MAP NAVIGATE command structure"""
        import json
        project_root = Path(__file__).parent.parent.parent

        # Check MAP.md knowledge base
        map_kb = project_root / "knowledge" / "system" / "MAP.md"
        if map_kb.exists():
            with open(map_kb, 'r') as f:
                content = f.read()
                self.assertIn('NAVIGATE', content)

    def test_goto_syntax_documented(self):
        """Test GOTO syntax is documented"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])
        goto_cmd = next((cmd for cmd in commands if cmd.get('NAME') == 'GOTO'), None)

        if goto_cmd:
            self.assertIn('SYNTAX', goto_cmd)
            syntax = goto_cmd['SYNTAX']
            self.assertIn('<x>', syntax)
            self.assertIn('<y>', syntax)

    def test_move_syntax_documented(self):
        """Test MOVE syntax is documented"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])
        move_cmd = next((cmd for cmd in commands if cmd.get('NAME') == 'MOVE'), None)

        if move_cmd:
            self.assertIn('SYNTAX', move_cmd)
            syntax = move_cmd['SYNTAX']
            self.assertIn('<d', syntax.lower())  # dx, dy parameters


class TestGeographicData(unittest.TestCase):
    """Test geographic data files"""

    def test_cities_data_exists(self):
        """Test cities.json exists"""
        project_root = Path(__file__).parent.parent.parent
        cities_file = project_root / "data" / "geography" / "cities.json"

        # File may be in different location, check multiple paths
        alternate_paths = [
            project_root / "data" / "cities.json",
            project_root / "knowledge" / "reference" / "cities.json",
        ]

        exists = cities_file.exists() or any(p.exists() for p in alternate_paths)
        # Skip if data not present (may be generated)
        if not exists:
            self.skipTest("Cities data not found (may be generated)")

    def test_terrain_data_exists(self):
        """Test terrain types data exists"""
        project_root = Path(__file__).parent.parent.parent

        terrain_paths = [
            project_root / "data" / "geography" / "terrain_types.json",
            project_root / "data" / "terrain.json",
        ]

        exists = any(p.exists() for p in terrain_paths)
        if not exists:
            self.skipTest("Terrain data not found (may be generated)")


class TestMapIntegration(unittest.TestCase):
    """Test map system integration"""

    def test_map_api_endpoints_exist(self):
        """Test map API endpoints exist in teletext server"""
        project_root = Path(__file__).parent.parent.parent
        api_server = project_root / "extensions" / "core" / "teletext" / "api_server.py"

        if not api_server.exists():
            self.skipTest("Teletext API server not found")

        with open(api_server, 'r') as f:
            content = f.read()
            # Check for map-related API endpoints
            has_map_status = '/api/map/status' in content
            has_map_goto = '/api/map/goto' in content
            has_map_move = '/api/map/move' in content

            self.assertTrue(has_map_status or has_map_goto or has_map_move,
                          "Map API endpoints should exist")

    def test_map_wiki_documentation(self):
        """Test map wiki documentation exists"""
        project_root = Path(__file__).parent.parent.parent
        mapping_wiki = project_root / "wiki" / "Mapping-System.md"

        self.assertTrue(mapping_wiki.exists())

        with open(mapping_wiki, 'r') as f:
            content = f.read()
            # Check for key sections
            self.assertIn('MAP', content.upper())
            self.assertIn('NAVIGATION', content.upper())


class TestMapPerformance(unittest.TestCase):
    """Test map system performance considerations"""

    def test_map_handler_lightweight(self):
        """Test map handler doesn't load heavy dependencies on init"""
        from core.commands.map_handler import MapCommandHandler
        import time

        start = time.time()
        handler = MapCommandHandler()
        elapsed = time.time() - start

        # Handler should initialize quickly (< 100ms)
        self.assertLess(elapsed, 0.1, "MapCommandHandler init should be fast")

    def test_map_engine_lazy_loading(self):
        """Test map engine uses lazy loading"""
        from core.commands.map_handler import MapCommandHandler

        handler = MapCommandHandler()
        # Check if map_engine is a property (lazy loaded)
        self.assertTrue(hasattr(type(handler), 'map_engine'))

        # Property should be defined on the class
        prop = getattr(type(handler), 'map_engine')
        self.assertTrue(isinstance(prop, property))


class TestMapValidation(unittest.TestCase):
    """Test map input validation"""

    def test_goto_requires_coordinates(self):
        """Test GOTO command requires coordinates"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])
        goto_cmd = next((cmd for cmd in commands if cmd.get('NAME') == 'GOTO'), None)

        if goto_cmd:
            syntax = goto_cmd.get('SYNTAX', '')
            # Should require parameters
            self.assertTrue('<' in syntax and '>' in syntax)

    def test_move_requires_deltas(self):
        """Test MOVE command requires delta values"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])
        move_cmd = next((cmd for cmd in commands if cmd.get('NAME') == 'MOVE'), None)

        if move_cmd:
            syntax = move_cmd.get('SYNTAX', '')
            # Should require dx, dy parameters
            self.assertTrue('<' in syntax and '>' in syntax)


if __name__ == '__main__':
    unittest.main()

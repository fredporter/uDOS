"""
AssetManager Test Suite (v1.5.3)

Comprehensive tests for the unified asset management system:
- Asset discovery and catalog building
- Loading fonts, icons, patterns, CSS, JS
- Search and filtering functionality
- Caching and hot-reload
- Asset metadata extraction
- Statistics and info display
- Error handling

Version: 1.0.0
Author: uDOS Asset Team
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import json
import sys

# Add core to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.services.asset_manager import AssetManager, Asset, get_asset_manager, reset_asset_manager


class TestAssetBasics(unittest.TestCase):
    """Test basic Asset class functionality"""

    def setUp(self):
        """Create temporary test directory"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_file = self.test_dir / 'test.txt'
        self.test_file.write_text('Test content')

        reset_asset_manager()

    def tearDown(self):
        """Clean up test directory"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        reset_asset_manager()

    def test_asset_initialization(self):
        """Test Asset object initialization"""
        asset = Asset('test', 'fonts', self.test_file, version='1.0.0')
        self.assertEqual(asset.name, 'test')
        self.assertEqual(asset.type, 'fonts')
        self.assertEqual(asset.version, '1.0.0')
        self.assertIsNone(asset.loaded_at)

    def test_asset_load_text(self):
        """Test loading text file"""
        asset = Asset('test', 'fonts', self.test_file)
        data = asset.load()
        self.assertEqual(data, 'Test content')
        self.assertIsNotNone(asset.loaded_at)

    def test_asset_load_json(self):
        """Test loading JSON file"""
        json_file = self.test_dir / 'test.json'
        test_data = {'key': 'value', 'number': 42}
        json_file.write_text(json.dumps(test_data))

        asset = Asset('test', 'patterns', json_file)
        data = asset.load()
        self.assertEqual(data, test_data)

    def test_asset_caching(self):
        """Test that loaded data is cached"""
        asset = Asset('test', 'fonts', self.test_file)
        data1 = asset.load()

        # Modify file
        self.test_file.write_text('Modified content')

        # Should return cached data
        data2 = asset.load()
        self.assertEqual(data1, data2)
        self.assertEqual(data2, 'Test content')  # Still cached

    def test_asset_reload(self):
        """Test hot-reload functionality"""
        asset = Asset('test', 'fonts', self.test_file)
        data1 = asset.load()

        # Modify file
        self.test_file.write_text('Modified content')

        # Reload should get new data
        data2 = asset.reload()
        self.assertEqual(data2, 'Modified content')

    def test_asset_get_info(self):
        """Test asset info retrieval"""
        asset = Asset('test', 'fonts', self.test_file, metadata={'author': 'Test'})
        info = asset.get_info()

        self.assertEqual(info['name'], 'test')
        self.assertEqual(info['type'], 'fonts')
        self.assertIn('path', info)
        self.assertIn('size', info)
        self.assertEqual(info['metadata']['author'], 'Test')


class TestAssetManager(unittest.TestCase):
    """Test AssetManager functionality"""

    def setUp(self):
        """Create test environment with sample assets"""
        self.test_dir = Path(tempfile.mkdtemp())

        # Create asset directories
        self.fonts_dir = self.test_dir / 'extensions' / 'assets' / 'fonts'
        self.icons_dir = self.test_dir / 'extensions' / 'assets' / 'icons'
        self.patterns_dir = self.test_dir / 'extensions' / 'assets' / 'patterns'

        self.fonts_dir.mkdir(parents=True, exist_ok=True)
        self.icons_dir.mkdir(parents=True, exist_ok=True)
        self.patterns_dir.mkdir(parents=True, exist_ok=True)

        # Create sample assets
        (self.fonts_dir / 'chicago.woff2').write_bytes(b'font data')
        (self.fonts_dir / 'monaco.ttf').write_bytes(b'monaco font')

        (self.icons_dir / 'water.svg').write_text('<svg>water</svg>')
        (self.icons_dir / 'fire.png').write_bytes(b'PNG data')

        pattern_data = {'name': 'grid', 'type': 'background'}
        (self.patterns_dir / 'grid.json').write_text(json.dumps(pattern_data))

        reset_asset_manager()

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        reset_asset_manager()

    def test_manager_initialization(self):
        """Test AssetManager initializes correctly"""
        manager = AssetManager(base_path=self.test_dir)
        self.assertEqual(manager.base_path, self.test_dir)
        self.assertTrue(manager.assets_root.exists())

    def test_catalog_loading(self):
        """Test asset catalog is built on init"""
        manager = AssetManager(base_path=self.test_dir)

        # Check fonts were found
        self.assertIn('chicago', manager._index['fonts'])
        self.assertIn('monaco', manager._index['fonts'])

        # Check icons were found
        self.assertIn('water', manager._index['icons'])
        self.assertIn('fire', manager._index['icons'])

        # Check patterns were found
        self.assertIn('grid', manager._index['patterns'])

    def test_load_font(self):
        """Test font loading"""
        manager = AssetManager(base_path=self.test_dir)

        # Load by name
        font = manager.load_font('chicago', format='woff2')
        self.assertIsNotNone(font)
        self.assertEqual(font.type, 'fonts')

    def test_load_icon(self):
        """Test icon loading"""
        manager = AssetManager(base_path=self.test_dir)

        icon = manager.load_icon('water', format='svg')
        self.assertIsNotNone(icon)
        self.assertEqual(icon.type, 'icons')

    def test_load_pattern(self):
        """Test pattern loading"""
        manager = AssetManager(base_path=self.test_dir)

        pattern = manager.load_pattern('grid')
        self.assertIsNotNone(pattern)
        self.assertEqual(pattern.type, 'patterns')

        # Load data
        data = pattern.load()
        self.assertEqual(data['name'], 'grid')

    def test_list_assets(self):
        """Test listing assets"""
        manager = AssetManager(base_path=self.test_dir)

        # List all
        all_assets = manager.list_assets()
        self.assertTrue(len(all_assets) >= 5)

        # List by type
        fonts = manager.list_assets('fonts')
        self.assertTrue(any('chicago' in f for f in fonts))

        icons = manager.list_assets('icons')
        self.assertTrue(any('water' in i for i in icons))

    def test_search_assets(self):
        """Test asset search"""
        manager = AssetManager(base_path=self.test_dir)

        # Search by name
        results = manager.search_assets('water')
        self.assertTrue(len(results) > 0)
        self.assertTrue(any('water' in name for name, _ in results))

        # Search with regex
        results = manager.search_assets('chi.*go')
        self.assertTrue(len(results) > 0)

    def test_get_asset_info(self):
        """Test asset info retrieval"""
        manager = AssetManager(base_path=self.test_dir)

        info = manager.get_asset_info('fonts/chicago')
        self.assertIsNotNone(info)
        self.assertEqual(info['type'], 'fonts')
        self.assertIn('size', info)

    def test_reload_asset(self):
        """Test hot-reload functionality"""
        manager = AssetManager(base_path=self.test_dir)

        # Load and cache
        pattern = manager.load_pattern('grid')
        data1 = pattern.load()

        # Modify file
        new_data = {'name': 'grid', 'type': 'background', 'modified': True}
        (self.patterns_dir / 'grid.json').write_text(json.dumps(new_data))

        # Reload
        success = manager.reload_asset('patterns/grid')
        self.assertTrue(success)

        # Check new data
        data2 = pattern.load()
        self.assertIn('modified', data2)

    def test_get_stats(self):
        """Test statistics retrieval"""
        manager = AssetManager(base_path=self.test_dir)

        stats = manager.get_stats()
        self.assertIn('total_assets', stats)
        self.assertIn('by_type', stats)
        self.assertIn('total_size_bytes', stats)
        self.assertGreater(stats['total_assets'], 0)


class TestMetadataExtraction(unittest.TestCase):
    """Test metadata extraction from assets"""

    def setUp(self):
        """Create test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.assets_dir = self.test_dir / 'extensions' / 'assets' / 'fonts'
        self.assets_dir.mkdir(parents=True, exist_ok=True)

        reset_asset_manager()

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        reset_asset_manager()

    def test_metadata_from_companion_file(self):
        """Test loading metadata from .meta.json companion file"""
        # Create asset
        font_file = self.assets_dir / 'chicago.woff2'
        font_file.write_bytes(b'font data')

        # Create companion metadata
        meta_file = self.assets_dir / 'chicago.woff2.meta.json'
        metadata = {
            'author': 'Susan Kare',
            'license': 'MIT',
            'tags': ['mac', 'system', 'retro']
        }
        meta_file.write_text(json.dumps(metadata))

        manager = AssetManager(base_path=self.test_dir)
        asset = manager.load_font('chicago')

        self.assertIsNotNone(asset)
        self.assertEqual(asset.metadata.get('author'), 'Susan Kare')
        self.assertIn('mac', asset.metadata.get('tags', []))


class TestSingletonPattern(unittest.TestCase):
    """Test global singleton pattern"""

    def setUp(self):
        """Reset singleton"""
        reset_asset_manager()

    def tearDown(self):
        """Clean up"""
        reset_asset_manager()

    def test_get_asset_manager_singleton(self):
        """Test get_asset_manager returns same instance"""
        manager1 = get_asset_manager()
        manager2 = get_asset_manager()

        self.assertIs(manager1, manager2)

    def test_reset_asset_manager(self):
        """Test reset creates new instance"""
        manager1 = get_asset_manager()
        reset_asset_manager()
        manager2 = get_asset_manager()

        self.assertIsNot(manager1, manager2)


class TestErrorHandling(unittest.TestCase):
    """Test error handling"""

    def setUp(self):
        """Create test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        reset_asset_manager()

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        reset_asset_manager()

    def test_missing_asset_returns_none(self):
        """Test loading non-existent asset returns None"""
        manager = AssetManager(base_path=self.test_dir)

        font = manager.load_font('nonexistent')
        self.assertIsNone(font)

        icon = manager.load_icon('missing')
        self.assertIsNone(icon)

    def test_invalid_asset_type(self):
        """Test list_assets with invalid type"""
        manager = AssetManager(base_path=self.test_dir)

        assets = manager.list_assets('invalid_type')
        self.assertEqual(assets, [])

    def test_corrupted_json_handling(self):
        """Test handling of corrupted JSON files"""
        assets_dir = self.test_dir / 'extensions' / 'assets' / 'patterns'
        assets_dir.mkdir(parents=True, exist_ok=True)

        # Create corrupted JSON
        corrupted = assets_dir / 'bad.json'
        corrupted.write_text('{invalid json')

        manager = AssetManager(base_path=self.test_dir)
        pattern = manager.load_pattern('bad')

        if pattern:
            # Should raise exception on load
            with self.assertRaises(Exception):
                pattern.load()


if __name__ == '__main__':
    unittest.main(verbosity=2)

"""
Unit tests for DeviceManager (v1.2.25).

Tests device management including:
- Device profile creation and loading
- Hardware scanning (CPU, memory, disk)
- System information
- Network detection
- Location and timezone management
- Health monitoring
- Input device detection (v1.2.25)
- Input mode management
- Mouse enable/disable
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from core.services.device_manager import DeviceManager


class TestDeviceManagerInit:
    """Test DeviceManager initialization."""
    
    def setup_method(self):
        """Setup for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.device_file = Path(self.temp_dir) / "device.json"
    
    def teardown_method(self):
        """Cleanup after each test."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('core.services.device_manager.Path')
    def test_init_creates_profile(self, mock_path):
        """Test initialization creates device profile."""
        mock_path.return_value = self.device_file
        manager = DeviceManager()
        
        assert manager.device_data is not None
        assert "device" in manager.device_data
        assert "hardware" in manager.device_data
        assert "system" in manager.device_data
    
    @patch('core.services.device_manager.Path')
    def test_init_with_config(self, mock_path):
        """Test initialization with config."""
        mock_path.return_value = self.device_file
        config = Mock()
        config.get_env.return_value = "America/New_York"
        config.get.return_value = "LE180"
        
        manager = DeviceManager(config=config)
        assert manager.config is config


class TestDeviceProfile:
    """Test device profile creation."""
    
    def setup_method(self):
        """Setup for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.device_file = Path(self.temp_dir) / "device.json"
    
    def teardown_method(self):
        """Cleanup after each test."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('core.services.device_manager.Path')
    @patch('socket.gethostname')
    def test_device_section(self, mock_hostname, mock_path):
        """Test device section contains required fields."""
        mock_path.return_value = self.device_file
        mock_hostname.return_value = "test-device"
        
        manager = DeviceManager()
        device = manager.device_data["device"]
        
        assert "id" in device
        assert device["name"] == "test-device"
        assert device["type"] == "terminal"
        assert "platform" in device
        assert "architecture" in device
        assert "initialized" in device
    
    @patch('core.services.device_manager.Path')
    def test_hardware_section(self, mock_path):
        """Test hardware section contains required fields."""
        mock_path.return_value = self.device_file
        manager = DeviceManager()
        hw = manager.device_data["hardware"]
        
        assert "cpu" in hw
        assert "memory" in hw
        assert "storage" in hw
        assert hw["cpu"]["cores"] > 0
        assert hw["memory"]["total_gb"] > 0
        assert hw["storage"]["total_gb"] > 0
    
    @patch('core.services.device_manager.Path')
    def test_system_section(self, mock_path):
        """Test system section contains required fields."""
        mock_path.return_value = self.device_file
        manager = DeviceManager()
        sys = manager.device_data["system"]
        
        assert "os" in sys
        assert "version" in sys
        assert "hostname" in sys
        assert "uptime_hours" in sys
        assert "python_version" in sys
    
    @patch('core.services.device_manager.Path')
    def test_network_section(self, mock_path):
        """Test network section contains required fields."""
        mock_path.return_value = self.device_file
        manager = DeviceManager()
        net = manager.device_data["network"]
        
        assert "hostname" in net
        assert "interfaces" in net
        assert isinstance(net["interfaces"], list)
    
    @patch('core.services.device_manager.Path')
    def test_location_section(self, mock_path):
        """Test location section contains required fields."""
        mock_path.return_value = self.device_file
        manager = DeviceManager()
        loc = manager.device_data["location"]
        
        assert "timezone" in loc
        assert "tile_code" in loc
        assert "city" in loc
        assert "country" in loc
    
    @patch('core.services.device_manager.Path')
    def test_capabilities_section(self, mock_path):
        """Test capabilities detection."""
        mock_path.return_value = self.device_file
        manager = DeviceManager()
        caps = manager.device_data["capabilities"]
        
        assert "audio" in caps
        assert "network" in caps
        assert isinstance(caps["audio"], bool)
    
    @patch('core.services.device_manager.Path')
    def test_monitoring_section(self, mock_path):
        """Test monitoring configuration."""
        mock_path.return_value = self.device_file
        manager = DeviceManager()
        mon = manager.device_data["monitoring"]
        
        assert mon["disk_scan_interval_minutes"] > 0
        assert mon["warn_disk_threshold_percent"] > 0
        assert mon["warn_memory_threshold_percent"] > 0


class TestSaveLoad:
    """Test saving and loading device profiles."""
    
    def setup_method(self):
        """Setup for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.device_file = Path(self.temp_dir) / "device.json"
    
    def teardown_method(self):
        """Cleanup after each test."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('core.services.device_manager.Path')
    def test_save_creates_file(self, mock_path):
        """Test save creates device.json file."""
        device_path = self.device_file
        mock_path_instance = Mock()
        mock_path_instance.parent.mkdir = Mock()
        mock_path_instance.__truediv__ = lambda self, other: device_path
        mock_path.return_value = mock_path_instance
        
        # Override the device_file path
        manager = DeviceManager()
        manager.device_file = device_path
        
        result = manager.save()
        assert result is True
        assert device_path.exists()
    
    @patch('core.services.device_manager.Path')
    def test_load_existing_file(self, mock_path):
        """Test loading existing device.json."""
        device_path = self.device_file
        
        # Create test file
        test_data = {
            "device": {"id": "test-123"},
            "metadata": {"version": "1.0.0"}
        }
        device_path.parent.mkdir(parents=True, exist_ok=True)
        with open(device_path, 'w') as f:
            json.dump(test_data, f)
        
        # Mock Path to return our test file
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.__truediv__ = lambda self, other: device_path
        mock_path.return_value = mock_path_instance
        
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__ = lambda s: s
            mock_open.return_value.__exit__ = Mock(return_value=False)
            mock_open.return_value.read.return_value = json.dumps(test_data)
            
            manager = DeviceManager()
            manager.device_file = device_path
            loaded = manager._load_or_create()
        
        assert loaded["device"]["id"] == "test-123"


class TestHardwareScan:
    """Test hardware scanning functions."""
    
    @patch('core.services.device_manager.Path')
    @patch('psutil.cpu_count')
    @patch('psutil.cpu_freq')
    @patch('psutil.virtual_memory')
    def test_scan_hardware_cpu(self, mock_mem, mock_freq, mock_cpu, mock_path):
        """Test CPU scanning."""
        mock_cpu.return_value = 4
        mock_freq.return_value = Mock(current=2400.0)
        mock_mem.return_value = Mock(total=8589934592, available=4294967296, percent=50.0)
        
        manager = DeviceManager()
        hw = manager._scan_hardware()
        
        assert hw["cpu"]["cores"] == 4
        assert hw["cpu"]["frequency_ghz"] == 2.4
    
    @patch('core.services.device_manager.Path')
    @patch('psutil.virtual_memory')
    def test_scan_hardware_memory(self, mock_mem, mock_path):
        """Test memory scanning."""
        mock_mem.return_value = Mock(
            total=8589934592,  # 8 GB
            available=4294967296,  # 4 GB
            percent=50.0
        )
        
        manager = DeviceManager()
        hw = manager._scan_hardware()
        
        assert hw["memory"]["total_gb"] == 8.0
        assert hw["memory"]["available_gb"] == 4.0
        assert hw["memory"]["used_percent"] == 50.0
    
    @patch('core.services.device_manager.Path')
    @patch('psutil.disk_usage')
    def test_scan_hardware_storage(self, mock_disk, mock_path):
        """Test storage scanning."""
        mock_disk.return_value = Mock(
            total=107374182400,  # 100 GB
            free=53687091200,    # 50 GB
            percent=50.0
        )
        
        manager = DeviceManager()
        hw = manager._scan_hardware()
        
        assert hw["storage"]["total_gb"] == 100.0
        assert hw["storage"]["used_percent"] == 50.0


class TestLocationManagement:
    """Test location and timezone management."""
    
    def setup_method(self):
        """Setup for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.device_file = Path(self.temp_dir) / "device.json"
    
    def teardown_method(self):
        """Cleanup after each test."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('core.services.device_manager.Path')
    def test_get_city_from_tile(self, mock_path):
        """Test getting city from TILE code."""
        mock_path.return_value = self.device_file
        manager = DeviceManager()
        
        assert manager._get_city_from_tile("AA340") == "Sydney"
        assert manager._get_city_from_tile("JF57") == "London"
        assert manager._get_city_from_tile("UNKNOWN") == "Unknown"
    
    @patch('core.services.device_manager.Path')
    def test_get_country_from_tile(self, mock_path):
        """Test getting country from TILE code."""
        mock_path.return_value = self.device_file
        manager = DeviceManager()
        
        assert manager._get_country_from_tile("AA340") == "Australia"
        assert manager._get_country_from_tile("LE180") == "United States"
    
    @patch('core.services.device_manager.Path')
    def test_get_tz_abbr(self, mock_path):
        """Test timezone abbreviation lookup."""
        mock_path.return_value = self.device_file
        manager = DeviceManager()
        
        assert manager._get_tz_abbr("UTC") == "UTC"
        assert manager._get_tz_abbr("America/New_York") == "EST"
        assert manager._get_tz_abbr("Unknown") == "UTC"
    
    @patch('core.services.device_manager.Path')
    def test_update_location(self, mock_path):
        """Test updating location."""
        device_path = self.device_file
        mock_path.return_value = device_path
        
        manager = DeviceManager()
        manager.device_file = device_path
        device_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Call update_location (datetime is not mocked, will use real time)
        result = manager.update_location("JF57", "Europe/London")
        
        assert result is True
        assert manager.device_data["location"]["tile_code"] == "JF57"
        assert manager.device_data["location"]["city"] == "London"
        assert manager.device_data["location"]["timezone"] == "Europe/London"


class TestHealthMonitoring:
    """Test health monitoring functions."""
    
    def setup_method(self):
        """Setup for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.device_file = Path(self.temp_dir) / "device.json"
    
    def teardown_method(self):
        """Cleanup after each test."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('core.services.device_manager.Path')
    def test_get_monitoring_thresholds(self, mock_path):
        """Test getting monitoring thresholds."""
        mock_path.return_value = self.device_file
        manager = DeviceManager()
        
        thresholds = manager.get_monitoring_thresholds()
        
        assert "disk" in thresholds
        assert "memory" in thresholds
        assert thresholds["disk"] > 0
        assert thresholds["memory"] > 0
    
    @patch('core.services.device_manager.Path')
    @patch('psutil.disk_usage')
    @patch('psutil.virtual_memory')
    @patch('psutil.cpu_percent')
    @patch('psutil.cpu_freq')
    @patch('psutil.cpu_count')
    def test_check_health_ok(self, mock_cpu_count, mock_cpu_freq, mock_cpu_percent, mock_mem, mock_disk, mock_path):
        """Test health check when all OK."""
        # Mock all psutil calls used in _scan_hardware
        mock_disk.return_value = Mock(
            total=107374182400,  # 100 GB
            free=32212254720,    # 30 GB  
            percent=70.0
        )
        mock_mem.return_value = Mock(
            total=8589934592, available=4294967296, percent=50.0
        )
        mock_cpu_count.return_value = 4
        mock_cpu_freq.return_value = Mock(current=2400.0)
        mock_cpu_percent.return_value = 25.0
        
        manager = DeviceManager()
        health = manager.check_health()
        
        assert health["disk"]["status"] == "ok"
        assert health["memory"]["status"] == "ok"
    
    @patch('core.services.device_manager.Path')
    @patch('psutil.disk_usage')
    @patch('psutil.virtual_memory')
    @patch('psutil.cpu_percent')
    @patch('psutil.cpu_freq')
    @patch('psutil.cpu_count')
    def test_check_health_warning(self, mock_cpu_count, mock_cpu_freq, mock_cpu_percent, mock_mem, mock_disk, mock_path):
        """Test health check with warnings."""
        # Mock all psutil calls used in _scan_hardware
        mock_disk.return_value = Mock(
            total=107374182400,  # 100 GB
            free=10737418240,    # 10 GB
            percent=90.0  # Above threshold
        )
        mock_mem.return_value = Mock(
            total=8589934592, available=858993459, percent=95.0  # Above threshold
        )
        mock_cpu_count.return_value = 4
        mock_cpu_freq.return_value = Mock(current=2400.0)
        mock_cpu_percent.return_value = 75.0
        
        manager = DeviceManager()
        health = manager.check_health()
        
        assert health["disk"]["status"] == "warning"
        assert health["memory"]["status"] == "warning"


class TestInputDetection:
    """Test input device detection (v1.2.25)."""
    
    def setup_method(self):
        """Setup for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.device_file = Path(self.temp_dir) / "device.json"
    
    def teardown_method(self):
        """Cleanup after each test."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('core.services.device_manager.Path')
    def test_detect_input_capabilities(self, mock_path):
        """Test input capability detection."""
        device_path = self.device_file
        mock_path.return_value = device_path
        
        manager = DeviceManager()
        manager.device_file = device_path
        device_path.parent.mkdir(parents=True, exist_ok=True)
        
        caps = manager.detect_input_capabilities()
        
        assert "keyboard" in caps
        assert "mouse" in caps
        assert "touch" in caps
        assert "terminal" in caps
        assert caps["keyboard"]["available"] is True
    
    @patch('core.services.device_manager.Path')
    @patch('os.environ.get')
    def test_supports_xterm_mouse(self, mock_env, mock_path):
        """Test xterm mouse detection."""
        mock_path.return_value = self.device_file
        mock_env.side_effect = lambda key, default='': {
            'TERM': 'xterm-256color',
            'TERM_PROGRAM': ''
        }.get(key, default)
        
        manager = DeviceManager()
        result = manager._supports_xterm_mouse()
        
        assert result is True
    
    @patch('core.services.device_manager.Path')
    @patch('os.environ.get')
    def test_supports_256_colors(self, mock_env, mock_path):
        """Test 256 color detection."""
        mock_path.return_value = self.device_file
        mock_env.return_value = 'xterm-256color'
        
        manager = DeviceManager()
        result = manager._supports_256_colors()
        
        assert result is True
    
    @patch('core.services.device_manager.Path')
    def test_terminal_dimensions(self, mock_path):
        """Test getting terminal dimensions."""
        mock_path.return_value = self.device_file
        manager = DeviceManager()
        
        width = manager._get_terminal_width()
        height = manager._get_terminal_height()
        
        assert width > 0
        assert height > 0


class TestInputModeManagement:
    """Test input mode management (v1.2.25)."""
    
    def setup_method(self):
        """Setup for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.device_file = Path(self.temp_dir) / "device.json"
    
    def teardown_method(self):
        """Cleanup after each test."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('core.services.device_manager.Path')
    def test_get_input_mode_default(self, mock_path):
        """Test getting default input mode."""
        device_path = self.device_file
        mock_path.return_value = device_path
        
        manager = DeviceManager()
        manager.device_file = device_path
        device_path.parent.mkdir(parents=True, exist_ok=True)
        
        mode = manager.get_input_mode()
        assert mode == "keypad"
    
    @patch('core.services.device_manager.Path')
    def test_set_input_mode_valid(self, mock_path):
        """Test setting valid input mode."""
        device_path = self.device_file
        mock_path.return_value = device_path
        
        manager = DeviceManager()
        manager.device_file = device_path
        device_path.parent.mkdir(parents=True, exist_ok=True)
        
        result = manager.set_input_mode("full_keyboard")
        assert result is True
        assert manager.get_input_mode() == "full_keyboard"
    
    @patch('core.services.device_manager.Path')
    def test_set_input_mode_invalid(self, mock_path):
        """Test setting invalid input mode."""
        device_path = self.device_file
        mock_path.return_value = device_path
        
        manager = DeviceManager()
        manager.device_file = device_path
        device_path.parent.mkdir(parents=True, exist_ok=True)
        
        result = manager.set_input_mode("invalid_mode")
        assert result is False


class TestMouseManagement:
    """Test mouse enable/disable (v1.2.25)."""
    
    def setup_method(self):
        """Setup for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.device_file = Path(self.temp_dir) / "device.json"
    
    def teardown_method(self):
        """Cleanup after each test."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('core.services.device_manager.Path')
    def test_is_mouse_enabled_default(self, mock_path):
        """Test mouse enabled status default."""
        device_path = self.device_file
        mock_path.return_value = device_path
        
        manager = DeviceManager()
        manager.device_file = device_path
        device_path.parent.mkdir(parents=True, exist_ok=True)
        
        enabled = manager.is_mouse_enabled()
        assert isinstance(enabled, bool)
    
    @patch('core.services.device_manager.Path')
    def test_enable_mouse(self, mock_path):
        """Test enabling mouse."""
        device_path = self.device_file
        mock_path.return_value = device_path
        
        manager = DeviceManager()
        manager.device_file = device_path
        device_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Ensure input capabilities are detected
        manager.detect_input_capabilities()
        
        if manager.device_data["input"]["mouse"]["available"]:
            result = manager.enable_mouse()
            assert result is True
            assert manager.is_mouse_enabled() is True
    
    @patch('core.services.device_manager.Path')
    def test_disable_mouse(self, mock_path):
        """Test disabling mouse."""
        device_path = self.device_file
        mock_path.return_value = device_path
        
        manager = DeviceManager()
        manager.device_file = device_path
        device_path.parent.mkdir(parents=True, exist_ok=True)
        
        manager.detect_input_capabilities()
        manager.disable_mouse()
        
        assert manager.is_mouse_enabled() is False


class TestStatusReport:
    """Test input status reporting (v1.2.25)."""
    
    def setup_method(self):
        """Setup for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.device_file = Path(self.temp_dir) / "device.json"
    
    def teardown_method(self):
        """Cleanup after each test."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('core.services.device_manager.Path')
    def test_get_input_status_report(self, mock_path):
        """Test generating input status report."""
        device_path = self.device_file
        mock_path.return_value = device_path
        
        manager = DeviceManager()
        manager.device_file = device_path
        device_path.parent.mkdir(parents=True, exist_ok=True)
        
        report = manager.get_input_status_report()
        
        assert isinstance(report, str)
        assert "INPUT DEVICE STATUS" in report
        assert "Keyboard:" in report
        assert "Mouse:" in report
        assert "Terminal:" in report


class TestRefresh:
    """Test refresh functionality."""
    
    def setup_method(self):
        """Setup for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.device_file = Path(self.temp_dir) / "device.json"
    
    def teardown_method(self):
        """Cleanup after each test."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('core.services.device_manager.Path')
    def test_refresh_updates_data(self, mock_path):
        """Test refresh updates hardware data."""
        mock_path.return_value = self.device_file
        manager = DeviceManager()
        
        old_scan_time = manager.device_data["monitoring"]["last_full_scan"]
        
        # Small delay to ensure timestamp changes
        import time
        time.sleep(0.01)
        
        result = manager.refresh()
        new_scan_time = result["monitoring"]["last_full_scan"]
        
        assert new_scan_time != old_scan_time


class TestGetInfo:
    """Test get_info functionality."""
    
    def setup_method(self):
        """Setup for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.device_file = Path(self.temp_dir) / "device.json"
    
    def teardown_method(self):
        """Cleanup after each test."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('core.services.device_manager.Path')
    def test_get_info_all(self, mock_path):
        """Test getting all device info."""
        mock_path.return_value = self.device_file
        manager = DeviceManager()
        
        info = manager.get_info()
        
        assert "device" in info
        assert "hardware" in info
        assert "system" in info
    
    @patch('core.services.device_manager.Path')
    def test_get_info_section(self, mock_path):
        """Test getting specific section."""
        mock_path.return_value = self.device_file
        manager = DeviceManager()
        
        hardware = manager.get_info("hardware")
        
        assert "cpu" in hardware
        assert "memory" in hardware
    
    @patch('core.services.device_manager.Path')
    def test_get_info_nonexistent_section(self, mock_path):
        """Test getting nonexistent section."""
        mock_path.return_value = self.device_file
        manager = DeviceManager()
        
        result = manager.get_info("nonexistent")
        
        assert result == {}


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

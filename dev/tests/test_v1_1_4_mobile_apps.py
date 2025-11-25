"""
uDOS v1.1.4.3 - Mobile Apps (iOS & Android) Test Suite

Tests touch-optimized mobile field companion apps for iOS and Android.
Validates curated feature set, touch UI, mesh networking, and session sync.

Test Coverage:
- Touch-Optimized UI (8 tests)
- Mobile Core Features (10 tests)
- Mobile Barter System (8 tests)
- Battery-Aware Mesh (9 tests)
- Session Sync (7 tests)
- Platform Compatibility (6 tests)
"""

import unittest
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum


# ============================================================================
# MOBILE PLATFORM & UI
# ============================================================================

class MobilePlatform(Enum):
    """Supported mobile platforms"""
    IOS = "ios"
    ANDROID = "android"


class ScreenSize(Enum):
    """Mobile screen sizes"""
    SMALL = "small"      # Phone (< 6")
    MEDIUM = "medium"    # Large phone (6-7")
    LARGE = "large"      # Tablet (> 7")


class GestureType(Enum):
    """Touch gestures"""
    TAP = "tap"
    LONG_PRESS = "long_press"
    SWIPE_LEFT = "swipe_left"
    SWIPE_RIGHT = "swipe_right"
    SWIPE_UP = "swipe_up"
    SWIPE_DOWN = "swipe_down"
    PINCH_ZOOM = "pinch_zoom"
    DOUBLE_TAP = "double_tap"


@dataclass
class TouchUIComponent:
    """Touch-optimized UI component"""
    component_id: str
    component_type: str  # button, card, list, map, input
    label: str
    touch_target_size: int = 44  # Minimum 44pt for iOS, 48dp for Android
    gesture_handlers: List[GestureType] = field(default_factory=list)
    accessible: bool = True
    haptic_feedback: bool = False

    def is_touch_friendly(self) -> bool:
        """Check if component meets touch target guidelines"""
        return self.touch_target_size >= 44


class TeletextMobileUI:
    """Touch-optimized Teletext UI for mobile"""

    def __init__(self, platform: MobilePlatform, screen_size: ScreenSize):
        self.platform = platform
        self.screen_size = screen_size
        self.components: Dict[str, TouchUIComponent] = {}
        self.theme = "retro_teletext"
        self.font_scaling = 1.0

    def add_component(self, component: TouchUIComponent) -> None:
        """Add UI component"""
        self.components[component.component_id] = component

    def handle_gesture(self, component_id: str, gesture: GestureType) -> Dict[str, Any]:
        """Handle touch gesture on component"""
        if component_id not in self.components:
            return {"success": False, "error": "Component not found"}

        component = self.components[component_id]
        if gesture not in component.gesture_handlers:
            return {"success": False, "error": f"Gesture {gesture.value} not supported"}

        # Simulate gesture handling
        result = {
            "success": True,
            "component_id": component_id,
            "gesture": gesture.value,
            "haptic": component.haptic_feedback
        }

        return result

    def get_layout(self) -> Dict[str, Any]:
        """Get current UI layout configuration"""
        return {
            "platform": self.platform.value,
            "screen_size": self.screen_size.value,
            "theme": self.theme,
            "font_scaling": self.font_scaling,
            "component_count": len(self.components)
        }

    def validate_accessibility(self) -> List[str]:
        """Validate accessibility compliance"""
        issues = []

        for comp_id, comp in self.components.items():
            if not comp.accessible:
                issues.append(f"{comp_id}: Not marked as accessible")

            if not comp.is_touch_friendly():
                issues.append(f"{comp_id}: Touch target too small ({comp.touch_target_size}pt)")

        return issues

    def adapt_for_screen_size(self, new_size: ScreenSize) -> None:
        """Adapt UI for different screen size"""
        self.screen_size = new_size

        # Adjust font scaling based on screen size
        if new_size == ScreenSize.SMALL:
            self.font_scaling = 0.9
        elif new_size == ScreenSize.LARGE:
            self.font_scaling = 1.2
        else:
            self.font_scaling = 1.0


# ============================================================================
# MOBILE CORE FEATURES
# ============================================================================

@dataclass
class MobileMission:
    """Mobile-optimized mission"""
    mission_id: str
    title: str
    description: str
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    distance_km: Optional[float] = None
    progress: int = 0
    status: str = "active"  # active, completed, failed
    offline_data: Dict[str, Any] = field(default_factory=dict)


class MobileMissionTracker:
    """Mobile mission tracking with GPS integration"""

    def __init__(self, device_id: str):
        self.device_id = device_id
        self.missions: Dict[str, MobileMission] = {}
        self.current_location: Optional[Tuple[float, float]] = None
        self.gps_enabled = False

    def enable_gps(self, latitude: float, longitude: float) -> None:
        """Enable GPS and set current location"""
        self.gps_enabled = True
        self.current_location = (latitude, longitude)

    def add_mission(self, mission: MobileMission) -> None:
        """Add mission to tracker"""
        self.missions[mission.mission_id] = mission

        # Calculate distance if GPS enabled
        if self.gps_enabled and mission.latitude and mission.longitude:
            mission.distance_km = self._calculate_distance(
                self.current_location,
                (mission.latitude, mission.longitude)
            )

    def _calculate_distance(self, loc1: Tuple[float, float], loc2: Tuple[float, float]) -> float:
        """Calculate distance between two coordinates (simplified)"""
        # Simplified distance calculation (not accurate Haversine)
        lat_diff = abs(loc1[0] - loc2[0])
        lon_diff = abs(loc1[1] - loc2[1])
        return ((lat_diff ** 2 + lon_diff ** 2) ** 0.5) * 111  # Rough km conversion

    def get_nearby_missions(self, max_distance_km: float = 10.0) -> List[MobileMission]:
        """Get missions within distance threshold"""
        if not self.gps_enabled:
            return []

        nearby = []
        for mission in self.missions.values():
            if mission.distance_km and mission.distance_km <= max_distance_km:
                nearby.append(mission)

        return sorted(nearby, key=lambda m: m.distance_km)

    def update_progress(self, mission_id: str, progress: int) -> bool:
        """Update mission progress"""
        if mission_id not in self.missions:
            return False

        self.missions[mission_id].progress = min(100, max(0, progress))

        if self.missions[mission_id].progress >= 100:
            self.missions[mission_id].status = "completed"

        return True

    def get_active_missions(self) -> List[MobileMission]:
        """Get all active missions"""
        return [m for m in self.missions.values() if m.status == "active"]


@dataclass
class SurvivalGuide:
    """Mobile survival guide entry"""
    guide_id: str
    title: str
    category: str
    content: str
    offline_available: bool = True
    images: List[str] = field(default_factory=list)
    related_guides: List[str] = field(default_factory=list)


class MobileSurvivalGuides:
    """Offline survival guide system for mobile"""

    def __init__(self):
        self.guides: Dict[str, SurvivalGuide] = {}
        self.categories: Dict[str, List[str]] = {}
        self.search_index: Dict[str, List[str]] = {}

    def add_guide(self, guide: SurvivalGuide) -> None:
        """Add survival guide"""
        self.guides[guide.guide_id] = guide

        # Add to category index
        if guide.category not in self.categories:
            self.categories[guide.category] = []
        self.categories[guide.category].append(guide.guide_id)

        # Build search index
        keywords = guide.title.lower().split() + guide.category.lower().split()
        for keyword in keywords:
            if keyword not in self.search_index:
                self.search_index[keyword] = []
            self.search_index[keyword].append(guide.guide_id)

    def search(self, query: str) -> List[SurvivalGuide]:
        """Search guides by keyword"""
        results = set()
        keywords = query.lower().split()

        for keyword in keywords:
            if keyword in self.search_index:
                results.update(self.search_index[keyword])

        return [self.guides[gid] for gid in results if gid in self.guides]

    def get_by_category(self, category: str) -> List[SurvivalGuide]:
        """Get guides by category"""
        guide_ids = self.categories.get(category, [])
        return [self.guides[gid] for gid in guide_ids]

    def get_offline_guides(self) -> List[SurvivalGuide]:
        """Get guides available offline"""
        return [g for g in self.guides.values() if g.offline_available]

    def get_guide_stats(self) -> Dict[str, int]:
        """Get guide statistics"""
        return {
            "total_guides": len(self.guides),
            "categories": len(self.categories),
            "offline_available": len(self.get_offline_guides())
        }


class MobileMapNavigation:
    """Touch-optimized map navigation"""

    def __init__(self):
        self.current_position: Optional[Tuple[float, float]] = None
        self.zoom_level = 1.0
        self.markers: List[Dict[str, Any]] = []
        self.route: List[Tuple[float, float]] = []

    def set_position(self, latitude: float, longitude: float) -> None:
        """Set current position on map"""
        self.current_position = (latitude, longitude)

    def zoom_in(self) -> float:
        """Zoom in (pinch gesture)"""
        self.zoom_level = min(5.0, self.zoom_level * 1.5)
        return self.zoom_level

    def zoom_out(self) -> float:
        """Zoom out (pinch gesture)"""
        self.zoom_level = max(0.5, self.zoom_level / 1.5)
        return self.zoom_level

    def add_marker(self, latitude: float, longitude: float, label: str, marker_type: str) -> None:
        """Add marker to map"""
        self.markers.append({
            "position": (latitude, longitude),
            "label": label,
            "type": marker_type
        })

    def calculate_route(self, destination: Tuple[float, float]) -> List[Tuple[float, float]]:
        """Calculate route to destination"""
        if not self.current_position:
            return []

        # Simplified route (straight line)
        self.route = [self.current_position, destination]
        return self.route

    def get_visible_markers(self) -> List[Dict[str, Any]]:
        """Get markers visible at current zoom level"""
        # Simplified: return all markers
        return self.markers


# ============================================================================
# MOBILE BARTER SYSTEM
# ============================================================================

@dataclass
class MobileBarterOffer:
    """Mobile barter offer"""
    offer_id: str
    user_id: str
    title: str
    description: str
    offer_type: str
    tags: List[str]
    images: List[str] = field(default_factory=list)
    location: Optional[str] = None
    distance_km: Optional[float] = None
    posted_at: datetime = field(default_factory=datetime.now)
    status: str = "active"


class MobileBarterInterface:
    """Touch-optimized barter interface"""

    def __init__(self, device_id: str):
        self.device_id = device_id
        self.my_offers: Dict[str, MobileBarterOffer] = {}
        self.discovered_offers: Dict[str, MobileBarterOffer] = {}
        self.favorites: List[str] = []
        self.image_cache: Dict[str, bytes] = {}

    def post_offer(
        self,
        title: str,
        description: str,
        offer_type: str,
        tags: List[str],
        images: Optional[List[str]] = None
    ) -> str:
        """Post barter offer from mobile"""
        offer_id = f"mobile_offer_{len(self.my_offers)}"

        offer = MobileBarterOffer(
            offer_id=offer_id,
            user_id=self.device_id,
            title=title,
            description=description,
            offer_type=offer_type,
            tags=tags,
            images=images or []
        )

        self.my_offers[offer_id] = offer
        return offer_id

    def discover_offer(self, offer: MobileBarterOffer) -> None:
        """Discover offer from mesh network"""
        self.discovered_offers[offer.offer_id] = offer

    def add_to_favorites(self, offer_id: str) -> bool:
        """Add offer to favorites"""
        if offer_id in self.discovered_offers and offer_id not in self.favorites:
            self.favorites.append(offer_id)
            return True
        return False

    def search_offers(self, query: str, max_distance: Optional[float] = None) -> List[MobileBarterOffer]:
        """Search discovered offers"""
        results = []
        query_lower = query.lower()

        for offer in self.discovered_offers.values():
            # Search in title, description, tags
            if (query_lower in offer.title.lower() or
                query_lower in offer.description.lower() or
                any(query_lower in tag.lower() for tag in offer.tags)):

                # Filter by distance if specified
                if max_distance is None or (offer.distance_km and offer.distance_km <= max_distance):
                    results.append(offer)

        return results

    def get_favorite_offers(self) -> List[MobileBarterOffer]:
        """Get favorited offers"""
        return [self.discovered_offers[oid] for oid in self.favorites if oid in self.discovered_offers]

    def cache_image(self, image_url: str, image_data: bytes) -> None:
        """Cache offer image for offline viewing"""
        self.image_cache[image_url] = image_data

    def get_cached_image(self, image_url: str) -> Optional[bytes]:
        """Get cached image"""
        return self.image_cache.get(image_url)

    def get_barter_stats(self) -> Dict[str, int]:
        """Get barter statistics"""
        return {
            "my_offers": len(self.my_offers),
            "discovered_offers": len(self.discovered_offers),
            "favorites": len(self.favorites),
            "cached_images": len(self.image_cache)
        }


# ============================================================================
# BATTERY-AWARE MESH NETWORKING
# ============================================================================

class BatteryLevel(Enum):
    """Battery levels"""
    CRITICAL = "critical"  # < 10%
    LOW = "low"           # 10-30%
    MEDIUM = "medium"     # 30-70%
    HIGH = "high"         # > 70%


class NetworkMode(Enum):
    """Network operation modes"""
    AGGRESSIVE = "aggressive"  # Full sync, frequent updates
    BALANCED = "balanced"      # Moderate sync
    POWER_SAVE = "power_save"  # Minimal sync, background only
    OFFLINE = "offline"        # No network activity


@dataclass
class BatteryStatus:
    """Device battery status"""
    level: int  # 0-100%
    charging: bool
    battery_level: BatteryLevel = field(init=False)

    def __post_init__(self):
        if self.level < 10:
            self.battery_level = BatteryLevel.CRITICAL
        elif self.level < 30:
            self.battery_level = BatteryLevel.LOW
        elif self.level < 70:
            self.battery_level = BatteryLevel.MEDIUM
        else:
            self.battery_level = BatteryLevel.HIGH


class MobileMeshNetworking:
    """Battery-aware mesh networking for mobile"""

    def __init__(self, device_id: str):
        self.device_id = device_id
        self.network_mode = NetworkMode.BALANCED
        self.battery_status = BatteryStatus(level=100, charging=False)
        self.sync_queue: List[Dict[str, Any]] = []
        self.background_sync_enabled = True
        self.last_sync: Optional[datetime] = None

    def update_battery_status(self, level: int, charging: bool) -> None:
        """Update battery status and adjust network mode"""
        self.battery_status = BatteryStatus(level=level, charging=charging)

        # Auto-adjust network mode based on battery
        if not charging:
            if self.battery_status.battery_level == BatteryLevel.CRITICAL:
                self.network_mode = NetworkMode.OFFLINE
            elif self.battery_status.battery_level == BatteryLevel.LOW:
                self.network_mode = NetworkMode.POWER_SAVE
            elif self.battery_status.battery_level == BatteryLevel.MEDIUM:
                self.network_mode = NetworkMode.BALANCED
            else:  # HIGH battery
                self.network_mode = NetworkMode.AGGRESSIVE
        else:
            # Charging: use aggressive mode
            self.network_mode = NetworkMode.AGGRESSIVE

    def queue_for_sync(self, data: Dict[str, Any]) -> None:
        """Add data to sync queue"""
        self.sync_queue.append({
            "data": data,
            "queued_at": datetime.now(),
            "priority": data.get("priority", "normal")
        })

    def should_sync_now(self) -> bool:
        """Determine if sync should happen now based on mode"""
        if self.network_mode == NetworkMode.OFFLINE:
            return False

        if not self.last_sync:
            return True

        # Check sync interval based on mode
        time_since_sync = (datetime.now() - self.last_sync).total_seconds()

        if self.network_mode == NetworkMode.AGGRESSIVE:
            return time_since_sync >= 60  # Every minute
        elif self.network_mode == NetworkMode.BALANCED:
            return time_since_sync >= 300  # Every 5 minutes
        elif self.network_mode == NetworkMode.POWER_SAVE:
            return time_since_sync >= 900  # Every 15 minutes

        return False

    def perform_sync(self) -> Dict[str, Any]:
        """Perform sync operation"""
        if not self.should_sync_now():
            return {"synced": False, "reason": "Not time to sync"}

        # Sync high-priority items in power save mode
        if self.network_mode == NetworkMode.POWER_SAVE:
            items_to_sync = [item for item in self.sync_queue if item["priority"] == "high"]
        else:
            items_to_sync = self.sync_queue.copy()

        synced_count = len(items_to_sync)

        # Remove synced items from queue
        for item in items_to_sync:
            self.sync_queue.remove(item)

        self.last_sync = datetime.now()

        return {
            "synced": True,
            "items_synced": synced_count,
            "queue_remaining": len(self.sync_queue),
            "network_mode": self.network_mode.value
        }

    def get_network_stats(self) -> Dict[str, Any]:
        """Get network statistics"""
        return {
            "network_mode": self.network_mode.value,
            "battery_level": self.battery_status.level,
            "charging": self.battery_status.charging,
            "sync_queue_size": len(self.sync_queue),
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "background_sync": self.background_sync_enabled
        }

    def enable_airplane_mode(self) -> None:
        """Enable airplane mode (offline)"""
        self.network_mode = NetworkMode.OFFLINE

    def disable_airplane_mode(self) -> None:
        """Disable airplane mode (restore based on battery)"""
        self.update_battery_status(self.battery_status.level, self.battery_status.charging)


# ============================================================================
# SESSION SYNC
# ============================================================================

@dataclass
class MobileSessionEvent:
    """Mobile-specific session event"""
    event_id: str
    event_type: str
    timestamp: datetime
    data: Dict[str, Any]
    gps_location: Optional[Tuple[float, float]] = None
    battery_level: Optional[int] = None
    network_mode: Optional[str] = None
    synced: bool = False


class MobileSessionTracker:
    """Track mobile session events"""

    def __init__(self, device_id: str):
        self.device_id = device_id
        self.events: List[MobileSessionEvent] = []
        self.session_start = datetime.now()
        self.sync_pending: List[str] = []

    def log_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        gps_location: Optional[Tuple[float, float]] = None,
        battery_level: Optional[int] = None,
        network_mode: Optional[str] = None
    ) -> str:
        """Log mobile session event"""
        event_id = f"mobile_evt_{len(self.events)}"

        event = MobileSessionEvent(
            event_id=event_id,
            event_type=event_type,
            timestamp=datetime.now(),
            data=data,
            gps_location=gps_location,
            battery_level=battery_level,
            network_mode=network_mode
        )

        self.events.append(event)
        self.sync_pending.append(event_id)

        return event_id

    def sync_to_desktop(self, event_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Sync events to desktop"""
        if event_ids is None:
            event_ids = self.sync_pending.copy()

        synced = []
        for event_id in event_ids:
            event = next((e for e in self.events if e.event_id == event_id), None)
            if event and not event.synced:
                event.synced = True
                synced.append(event_id)
                if event_id in self.sync_pending:
                    self.sync_pending.remove(event_id)

        return {
            "device_id": self.device_id,
            "synced_events": len(synced),
            "pending_events": len(self.sync_pending),
            "session_duration": (datetime.now() - self.session_start).total_seconds()
        }

    def get_unsynced_events(self) -> List[MobileSessionEvent]:
        """Get events not yet synced"""
        return [e for e in self.events if not e.synced]

    def get_events_by_type(self, event_type: str) -> List[MobileSessionEvent]:
        """Get events filtered by type"""
        return [e for e in self.events if e.event_type == event_type]

    def get_session_summary(self) -> Dict[str, Any]:
        """Get session summary"""
        gps_events = len([e for e in self.events if e.gps_location])

        return {
            "device_id": self.device_id,
            "total_events": len(self.events),
            "synced_events": len([e for e in self.events if e.synced]),
            "pending_sync": len(self.sync_pending),
            "gps_tracked_events": gps_events,
            "session_duration_seconds": (datetime.now() - self.session_start).total_seconds()
        }


# ============================================================================
# PLATFORM COMPATIBILITY
# ============================================================================

class PlatformFeatures:
    """Platform-specific features and capabilities"""

    def __init__(self, platform: MobilePlatform):
        self.platform = platform
        self.features: Dict[str, bool] = self._detect_features()

    def _detect_features(self) -> Dict[str, bool]:
        """Detect platform-specific features"""
        base_features = {
            "gps": True,
            "camera": True,
            "notifications": True,
            "background_sync": True,
            "haptics": True,
            "biometric_auth": True
        }

        if self.platform == MobilePlatform.IOS:
            base_features.update({
                "3d_touch": True,
                "faceid": True,
                "icloud_sync": True,
                "apple_watch": True
            })
        elif self.platform == MobilePlatform.ANDROID:
            base_features.update({
                "nfc": True,
                "widgets": True,
                "file_system_access": True,
                "custom_launchers": True
            })

        return base_features

    def has_feature(self, feature: str) -> bool:
        """Check if platform has specific feature"""
        return self.features.get(feature, False)

    def get_storage_path(self) -> str:
        """Get platform-specific storage path"""
        if self.platform == MobilePlatform.IOS:
            return "/var/mobile/Containers/Data/Application/udos/"
        else:  # Android
            return "/data/data/com.udos.app/files/"

    def get_notification_permissions(self) -> str:
        """Get notification permission model"""
        if self.platform == MobilePlatform.IOS:
            return "request_on_first_use"
        else:  # Android
            return "granted_by_default"

    def supports_background_location(self) -> bool:
        """Check if background location tracking is supported"""
        return self.platform == MobilePlatform.IOS or self.platform == MobilePlatform.ANDROID


class MobileAppOptimizations:
    """Mobile-specific optimizations"""

    def __init__(self, platform: MobilePlatform):
        self.platform = platform
        self.cache_size_mb = 0
        self.offline_data_mb = 0

    def optimize_images(self, image_count: int, original_size_mb: float) -> float:
        """Optimize images for mobile"""
        # Reduce to 50% size for mobile
        optimized_size = original_size_mb * 0.5
        return optimized_size

    def cache_offline_data(self, data_size_mb: float) -> bool:
        """Cache data for offline use"""
        max_cache_mb = 500  # Max 500MB cache

        if self.cache_size_mb + data_size_mb <= max_cache_mb:
            self.cache_size_mb += data_size_mb
            return True

        return False

    def clear_cache(self) -> float:
        """Clear cache and return freed space"""
        freed = self.cache_size_mb
        self.cache_size_mb = 0
        return freed

    def get_storage_stats(self) -> Dict[str, float]:
        """Get storage statistics"""
        return {
            "cache_size_mb": self.cache_size_mb,
            "offline_data_mb": self.offline_data_mb,
            "total_mb": self.cache_size_mb + self.offline_data_mb
        }


# ============================================================================
# TEST SUITES
# ============================================================================

class TestTouchUI(unittest.TestCase):
    """Test touch-optimized UI"""

    def setUp(self):
        self.ui = TeletextMobileUI(MobilePlatform.IOS, ScreenSize.MEDIUM)

    def test_create_ui(self):
        """Test UI creation"""
        self.assertEqual(self.ui.platform, MobilePlatform.IOS)
        self.assertEqual(self.ui.screen_size, ScreenSize.MEDIUM)
        self.assertEqual(self.ui.theme, "retro_teletext")

    def test_add_component(self):
        """Test adding UI component"""
        comp = TouchUIComponent(
            component_id="btn_mission",
            component_type="button",
            label="Start Mission",
            gesture_handlers=[GestureType.TAP]
        )

        self.ui.add_component(comp)
        self.assertIn("btn_mission", self.ui.components)

    def test_handle_gesture(self):
        """Test gesture handling"""
        comp = TouchUIComponent(
            component_id="btn_test",
            component_type="button",
            label="Test",
            gesture_handlers=[GestureType.TAP, GestureType.LONG_PRESS]
        )

        self.ui.add_component(comp)
        result = self.ui.handle_gesture("btn_test", GestureType.TAP)

        self.assertTrue(result["success"])
        self.assertEqual(result["gesture"], "tap")

    def test_unsupported_gesture(self):
        """Test unsupported gesture fails"""
        comp = TouchUIComponent(
            component_id="btn_test",
            component_type="button",
            label="Test",
            gesture_handlers=[GestureType.TAP]
        )

        self.ui.add_component(comp)
        result = self.ui.handle_gesture("btn_test", GestureType.SWIPE_LEFT)

        self.assertFalse(result["success"])

    def test_touch_target_validation(self):
        """Test touch target size validation"""
        comp = TouchUIComponent(
            component_id="btn_small",
            component_type="button",
            label="Small",
            touch_target_size=32  # Too small
        )

        self.assertFalse(comp.is_touch_friendly())

    def test_accessibility_validation(self):
        """Test accessibility compliance"""
        good_comp = TouchUIComponent("btn1", "button", "OK", touch_target_size=48)
        bad_comp = TouchUIComponent("btn2", "button", "Cancel", touch_target_size=30)

        self.ui.add_component(good_comp)
        self.ui.add_component(bad_comp)

        issues = self.ui.validate_accessibility()
        self.assertGreater(len(issues), 0)
        self.assertTrue(any("btn2" in issue for issue in issues))

    def test_screen_size_adaptation(self):
        """Test UI adaptation to screen size"""
        self.ui.adapt_for_screen_size(ScreenSize.SMALL)
        self.assertEqual(self.ui.font_scaling, 0.9)

        self.ui.adapt_for_screen_size(ScreenSize.LARGE)
        self.assertEqual(self.ui.font_scaling, 1.2)

    def test_get_layout(self):
        """Test getting UI layout"""
        layout = self.ui.get_layout()

        self.assertEqual(layout["platform"], "ios")
        self.assertEqual(layout["screen_size"], "medium")
        self.assertEqual(layout["theme"], "retro_teletext")


class TestMobileCoreFeatures(unittest.TestCase):
    """Test mobile core features"""

    def setUp(self):
        self.mission_tracker = MobileMissionTracker("mobile_001")
        self.guides = MobileSurvivalGuides()
        self.map_nav = MobileMapNavigation()

    def test_enable_gps(self):
        """Test GPS enablement"""
        self.mission_tracker.enable_gps(45.5231, -122.6765)
        self.assertTrue(self.mission_tracker.gps_enabled)
        self.assertEqual(self.mission_tracker.current_location, (45.5231, -122.6765))

    def test_add_mission_with_gps(self):
        """Test adding mission with GPS distance calculation"""
        self.mission_tracker.enable_gps(45.5231, -122.6765)

        mission = MobileMission(
            mission_id="mission_001",
            title="Water Purification",
            description="Set up filter",
            location="Downtown",
            latitude=45.5200,
            longitude=-122.6800
        )

        self.mission_tracker.add_mission(mission)
        self.assertIsNotNone(mission.distance_km)
        self.assertGreater(mission.distance_km, 0)

    def test_get_nearby_missions(self):
        """Test finding nearby missions"""
        self.mission_tracker.enable_gps(45.5231, -122.6765)

        nearby_mission = MobileMission(
            "m1", "Nearby", "Close", "Here",
            latitude=45.5230, longitude=-122.6760
        )
        far_mission = MobileMission(
            "m2", "Far", "Distant", "There",
            latitude=46.0000, longitude=-123.0000
        )

        self.mission_tracker.add_mission(nearby_mission)
        self.mission_tracker.add_mission(far_mission)

        nearby = self.mission_tracker.get_nearby_missions(max_distance_km=10.0)
        self.assertEqual(len(nearby), 1)
        self.assertEqual(nearby[0].mission_id, "m1")

    def test_update_mission_progress(self):
        """Test updating mission progress"""
        mission = MobileMission("m1", "Test", "Desc", "Loc")
        self.mission_tracker.add_mission(mission)

        success = self.mission_tracker.update_progress("m1", 75)
        self.assertTrue(success)
        self.assertEqual(self.mission_tracker.missions["m1"].progress, 75)

    def test_mission_completion(self):
        """Test mission auto-completion at 100%"""
        mission = MobileMission("m1", "Test", "Desc", "Loc")
        self.mission_tracker.add_mission(mission)

        self.mission_tracker.update_progress("m1", 100)
        self.assertEqual(self.mission_tracker.missions["m1"].status, "completed")

    def test_add_survival_guide(self):
        """Test adding survival guide"""
        guide = SurvivalGuide(
            guide_id="guide_001",
            title="Water Purification",
            category="Water",
            content="How to purify water..."
        )

        self.guides.add_guide(guide)
        self.assertIn("guide_001", self.guides.guides)

    def test_search_guides(self):
        """Test searching survival guides"""
        guide1 = SurvivalGuide("g1", "Water Purification", "Water", "Content")
        guide2 = SurvivalGuide("g2", "Fire Starting", "Fire", "Content")

        self.guides.add_guide(guide1)
        self.guides.add_guide(guide2)

        results = self.guides.search("water")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].guide_id, "g1")

    def test_get_guides_by_category(self):
        """Test getting guides by category"""
        guide1 = SurvivalGuide("g1", "Water Filter", "Water", "Content")
        guide2 = SurvivalGuide("g2", "Water Boiling", "Water", "Content")

        self.guides.add_guide(guide1)
        self.guides.add_guide(guide2)

        water_guides = self.guides.get_by_category("Water")
        self.assertEqual(len(water_guides), 2)

    def test_map_zoom(self):
        """Test map zoom gestures"""
        initial_zoom = self.map_nav.zoom_level

        new_zoom = self.map_nav.zoom_in()
        self.assertGreater(new_zoom, initial_zoom)

        # Store zoom level before zooming out
        before_zoom_out = self.map_nav.zoom_level
        new_zoom = self.map_nav.zoom_out()
        self.assertLess(new_zoom, before_zoom_out)

    def test_map_markers(self):
        """Test adding map markers"""
        self.map_nav.add_marker(45.5231, -122.6765, "Camp", "shelter")
        self.map_nav.add_marker(45.5300, -122.6800, "Water", "water_source")

        markers = self.map_nav.get_visible_markers()
        self.assertEqual(len(markers), 2)
class TestMobileBarterSystem(unittest.TestCase):
    """Test mobile barter system"""

    def setUp(self):
        self.barter = MobileBarterInterface("mobile_001")

    def test_post_offer(self):
        """Test posting barter offer from mobile"""
        offer_id = self.barter.post_offer(
            title="Fresh Vegetables",
            description="Homegrown",
            offer_type="goods",
            tags=["food", "organic"]
        )

        self.assertIn(offer_id, self.barter.my_offers)

    def test_discover_offer(self):
        """Test discovering offer from mesh"""
        offer = MobileBarterOffer(
            offer_id="offer_001",
            user_id="other_user",
            title="Tools",
            description="Hand tools",
            offer_type="goods",
            tags=["tools"]
        )

        self.barter.discover_offer(offer)
        self.assertIn("offer_001", self.barter.discovered_offers)

    def test_add_to_favorites(self):
        """Test adding offer to favorites"""
        offer = MobileBarterOffer(
            offer_id="offer_001",
            user_id="other_user",
            title="Tools",
            description="Hand tools",
            offer_type="goods",
            tags=["tools"]
        )

        self.barter.discover_offer(offer)
        success = self.barter.add_to_favorites("offer_001")

        self.assertTrue(success)
        self.assertIn("offer_001", self.barter.favorites)

    def test_search_offers(self):
        """Test searching discovered offers"""
        offer1 = MobileBarterOffer("o1", "u1", "Vegetables", "Food", "goods", ["food"])
        offer2 = MobileBarterOffer("o2", "u2", "Tools", "Hand tools", "goods", ["tools"])

        self.barter.discover_offer(offer1)
        self.barter.discover_offer(offer2)

        results = self.barter.search_offers("food")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].offer_id, "o1")

    def test_image_caching(self):
        """Test offer image caching"""
        image_data = b"fake_image_data"
        self.barter.cache_image("image_url", image_data)

        cached = self.barter.get_cached_image("image_url")
        self.assertEqual(cached, image_data)

    def test_get_favorite_offers(self):
        """Test retrieving favorite offers"""
        offer = MobileBarterOffer("o1", "u1", "Item", "Desc", "goods", ["tag"])
        self.barter.discover_offer(offer)
        self.barter.add_to_favorites("o1")

        favorites = self.barter.get_favorite_offers()
        self.assertEqual(len(favorites), 1)

    def test_barter_stats(self):
        """Test barter statistics"""
        self.barter.post_offer("Title", "Desc", "goods", ["tag"])

        offer = MobileBarterOffer("o1", "u1", "Item", "Desc", "goods", ["tag"])
        self.barter.discover_offer(offer)

        stats = self.barter.get_barter_stats()
        self.assertEqual(stats["my_offers"], 1)
        self.assertEqual(stats["discovered_offers"], 1)

    def test_search_with_distance_filter(self):
        """Test searching offers with distance filter"""
        offer = MobileBarterOffer("o1", "u1", "Item", "Desc", "goods", ["tag"])
        offer.distance_km = 5.0

        self.barter.discover_offer(offer)

        results = self.barter.search_offers("item", max_distance=10.0)
        self.assertEqual(len(results), 1)


class TestBatteryAwareMesh(unittest.TestCase):
    """Test battery-aware mesh networking"""

    def setUp(self):
        self.mesh = MobileMeshNetworking("mobile_001")

    def test_initial_battery_status(self):
        """Test initial battery status"""
        self.assertEqual(self.mesh.battery_status.level, 100)
        self.assertEqual(self.mesh.battery_status.battery_level, BatteryLevel.HIGH)

    def test_battery_level_classification(self):
        """Test battery level classification"""
        self.mesh.update_battery_status(5, False)
        self.assertEqual(self.mesh.battery_status.battery_level, BatteryLevel.CRITICAL)

        self.mesh.update_battery_status(25, False)
        self.assertEqual(self.mesh.battery_status.battery_level, BatteryLevel.LOW)

        self.mesh.update_battery_status(50, False)
        self.assertEqual(self.mesh.battery_status.battery_level, BatteryLevel.MEDIUM)

    def test_network_mode_auto_adjust(self):
        """Test network mode auto-adjustment based on battery"""
        # Critical battery -> offline
        self.mesh.update_battery_status(5, False)
        self.assertEqual(self.mesh.network_mode, NetworkMode.OFFLINE)

        # Low battery -> power save
        self.mesh.update_battery_status(20, False)
        self.assertEqual(self.mesh.network_mode, NetworkMode.POWER_SAVE)

        # Charging -> aggressive
        self.mesh.update_battery_status(20, True)
        self.assertEqual(self.mesh.network_mode, NetworkMode.AGGRESSIVE)

    def test_sync_queue(self):
        """Test sync queue management"""
        self.mesh.queue_for_sync({"type": "mission", "data": "test"})
        self.mesh.queue_for_sync({"type": "barter", "data": "offer"})

        self.assertEqual(len(self.mesh.sync_queue), 2)

    def test_should_sync_offline_mode(self):
        """Test sync disabled in offline mode"""
        self.mesh.network_mode = NetworkMode.OFFLINE
        self.assertFalse(self.mesh.should_sync_now())

    def test_sync_priority_in_power_save(self):
        """Test priority sync in power save mode"""
        self.mesh.network_mode = NetworkMode.POWER_SAVE
        self.mesh.queue_for_sync({"type": "data", "priority": "high"})
        self.mesh.queue_for_sync({"type": "data", "priority": "normal"})

        result = self.mesh.perform_sync()

        # Only high priority synced in power save mode
        self.assertEqual(result["items_synced"], 1)

    def test_airplane_mode(self):
        """Test airplane mode toggle"""
        # Start with good battery (75% = HIGH = AGGRESSIVE mode when not charging)
        self.mesh.update_battery_status(75, False)
        initial_mode = self.mesh.network_mode
        self.assertEqual(initial_mode, NetworkMode.AGGRESSIVE)

        self.mesh.enable_airplane_mode()
        self.assertEqual(self.mesh.network_mode, NetworkMode.OFFLINE)

        self.mesh.disable_airplane_mode()
        # After disabling, should restore to battery-appropriate mode
        # With 75% battery (HIGH), not charging, should be AGGRESSIVE
        self.assertEqual(self.mesh.network_mode, NetworkMode.AGGRESSIVE)

    def test_network_stats(self):
        """Test network statistics"""
        self.mesh.update_battery_status(75, False)
        self.mesh.queue_for_sync({"data": "test"})

        stats = self.mesh.get_network_stats()

        self.assertEqual(stats["battery_level"], 75)
        self.assertEqual(stats["sync_queue_size"], 1)
        self.assertIn("network_mode", stats)

    def test_perform_sync_success(self):
        """Test successful sync operation"""
        self.mesh.network_mode = NetworkMode.AGGRESSIVE
        self.mesh.queue_for_sync({"data": "test1"})
        self.mesh.queue_for_sync({"data": "test2"})

        result = self.mesh.perform_sync()

        self.assertTrue(result["synced"])
        self.assertEqual(result["items_synced"], 2)
        self.assertEqual(result["queue_remaining"], 0)


class TestSessionSync(unittest.TestCase):
    """Test session synchronization"""

    def setUp(self):
        self.session = MobileSessionTracker("mobile_001")

    def test_log_event(self):
        """Test logging session event"""
        event_id = self.session.log_event(
            event_type="mission_start",
            data={"mission_id": "m1"},
            gps_location=(45.5231, -122.6765),
            battery_level=85
        )

        self.assertEqual(len(self.session.events), 1)
        self.assertIn(event_id, self.session.sync_pending)

    def test_sync_to_desktop(self):
        """Test syncing events to desktop"""
        self.session.log_event("event1", {"data": "test1"})
        self.session.log_event("event2", {"data": "test2"})

        result = self.session.sync_to_desktop()

        self.assertEqual(result["synced_events"], 2)
        self.assertEqual(result["pending_events"], 0)

    def test_get_unsynced_events(self):
        """Test getting unsynced events"""
        self.session.log_event("event1", {"data": "test"})

        unsynced = self.session.get_unsynced_events()
        self.assertEqual(len(unsynced), 1)

        self.session.sync_to_desktop()
        unsynced = self.session.get_unsynced_events()
        self.assertEqual(len(unsynced), 0)

    def test_get_events_by_type(self):
        """Test filtering events by type"""
        self.session.log_event("mission_start", {"id": "m1"})
        self.session.log_event("barter_post", {"id": "b1"})
        self.session.log_event("mission_start", {"id": "m2"})

        mission_events = self.session.get_events_by_type("mission_start")
        self.assertEqual(len(mission_events), 2)

    def test_session_summary(self):
        """Test session summary generation"""
        self.session.log_event("e1", {}, gps_location=(45.0, -122.0), battery_level=90)
        self.session.log_event("e2", {}, battery_level=85)

        summary = self.session.get_session_summary()

        self.assertEqual(summary["total_events"], 2)
        self.assertEqual(summary["gps_tracked_events"], 1)
        self.assertGreater(summary["session_duration_seconds"], 0)

    def test_partial_sync(self):
        """Test syncing specific events"""
        evt1 = self.session.log_event("e1", {})
        evt2 = self.session.log_event("e2", {})

        result = self.session.sync_to_desktop([evt1])

        self.assertEqual(result["synced_events"], 1)
        self.assertEqual(result["pending_events"], 1)

    def test_event_metadata(self):
        """Test event metadata tracking"""
        event_id = self.session.log_event(
            "gps_update",
            {"accuracy": 10},
            gps_location=(45.5, -122.6),
            battery_level=75,
            network_mode="balanced"
        )

        event = next(e for e in self.session.events if e.event_id == event_id)

        self.assertEqual(event.gps_location, (45.5, -122.6))
        self.assertEqual(event.battery_level, 75)
        self.assertEqual(event.network_mode, "balanced")


class TestPlatformCompatibility(unittest.TestCase):
    """Test platform compatibility"""

    def test_ios_features(self):
        """Test iOS-specific features"""
        platform = PlatformFeatures(MobilePlatform.IOS)

        self.assertTrue(platform.has_feature("3d_touch"))
        self.assertTrue(platform.has_feature("faceid"))
        self.assertTrue(platform.has_feature("icloud_sync"))

    def test_android_features(self):
        """Test Android-specific features"""
        platform = PlatformFeatures(MobilePlatform.ANDROID)

        self.assertTrue(platform.has_feature("nfc"))
        self.assertTrue(platform.has_feature("widgets"))
        self.assertTrue(platform.has_feature("file_system_access"))

    def test_common_features(self):
        """Test features common to both platforms"""
        ios = PlatformFeatures(MobilePlatform.IOS)
        android = PlatformFeatures(MobilePlatform.ANDROID)

        for feature in ["gps", "camera", "notifications", "haptics"]:
            self.assertTrue(ios.has_feature(feature))
            self.assertTrue(android.has_feature(feature))

    def test_storage_paths(self):
        """Test platform-specific storage paths"""
        ios = PlatformFeatures(MobilePlatform.IOS)
        android = PlatformFeatures(MobilePlatform.ANDROID)

        self.assertIn("mobile/Containers", ios.get_storage_path())
        self.assertIn("data/data", android.get_storage_path())

    def test_image_optimization(self):
        """Test image optimization for mobile"""
        optimizer = MobileAppOptimizations(MobilePlatform.IOS)

        original_size = 10.0  # MB
        optimized_size = optimizer.optimize_images(10, original_size)

        self.assertLess(optimized_size, original_size)
        self.assertEqual(optimized_size, 5.0)  # 50% reduction

    def test_offline_data_caching(self):
        """Test offline data caching"""
        optimizer = MobileAppOptimizations(MobilePlatform.ANDROID)

        success = optimizer.cache_offline_data(100.0)
        self.assertTrue(success)

        stats = optimizer.get_storage_stats()
        self.assertEqual(stats["cache_size_mb"], 100.0)


# ============================================================================
# TEST RUNNER
# ============================================================================

if __name__ == '__main__':
    unittest.main(verbosity=2)

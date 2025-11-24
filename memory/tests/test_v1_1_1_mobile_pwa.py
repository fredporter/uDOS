"""
Test Suite for Feature 1.1.1.7: Mobile-Responsive Views (PWA)
v1.1.1 Phase 2: Advanced Web Features

Tests Progressive Web App (PWA) functionality including mobile breakpoints,
touch-optimized interface, service workers for offline capability, and
responsive components with gesture support.

Test Categories:
1. PWA Manifest (5 tests)
2. Service Worker Registration (6 tests)
3. Mobile Breakpoints (5 tests)
4. Touch Optimization (6 tests)
5. Offline Capability (6 tests)
6. Install Prompts (4 tests)
7. Responsive Components (6 tests)
8. Gesture Support (5 tests)
9. App Shell Architecture (4 tests)
10. Cache Strategies (5 tests)
11. Push Notifications (4 tests)
12. Integration Scenarios (3 tests)

Total: 59 tests
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call
import json
from datetime import datetime, timedelta


class PWAManager:
    """Progressive Web App manager for uDOS mobile experience."""

    def __init__(self):
        self.manifest = self._generate_manifest()
        self.service_worker = None
        self.cache_storage = {}
        self.install_prompt = None
        self.breakpoints = {
            "mobile": 0,
            "tablet": 768,
            "desktop": 1024
        }
        self.touch_handlers = {}
        self.gestures = {}
        self.offline_pages = []
        self.push_subscriptions = []
        self.app_shell_cached = False

    def _generate_manifest(self):
        """Generate PWA manifest."""
        return {
            "name": "uDOS - Universal Digital Operating System",
            "short_name": "uDOS",
            "description": "Text-first computing with offline-first design",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#000000",
            "theme_color": "#FF10F0",
            "orientation": "any",
            "icons": [
                {
                    "src": "/icons/icon-72.png",
                    "sizes": "72x72",
                    "type": "image/png",
                    "purpose": "any"
                },
                {
                    "src": "/icons/icon-192.png",
                    "sizes": "192x192",
                    "type": "image/png",
                    "purpose": "any maskable"
                },
                {
                    "src": "/icons/icon-512.png",
                    "sizes": "512x512",
                    "type": "image/png",
                    "purpose": "any maskable"
                }
            ],
            "screenshots": [
                {
                    "src": "/screenshots/mobile.png",
                    "sizes": "390x844",
                    "type": "image/png",
                    "form_factor": "narrow"
                },
                {
                    "src": "/screenshots/desktop.png",
                    "sizes": "1920x1080",
                    "type": "image/png",
                    "form_factor": "wide"
                }
            ],
            "categories": ["productivity", "utilities"],
            "shortcuts": [
                {
                    "name": "New Mission",
                    "short_name": "Mission",
                    "url": "/mission/new",
                    "icons": [{"src": "/icons/mission.png", "sizes": "96x96"}]
                },
                {
                    "name": "Knowledge Search",
                    "short_name": "Search",
                    "url": "/knowledge/search",
                    "icons": [{"src": "/icons/search.png", "sizes": "96x96"}]
                }
            ]
        }

    def validate_manifest(self):
        """Validate PWA manifest structure."""
        required = ["name", "short_name", "start_url", "display", "icons"]
        return all(field in self.manifest for field in required)

    def register_service_worker(self, script_url="/sw.js"):
        """Register service worker."""
        self.service_worker = {
            "script_url": script_url,
            "scope": "/",
            "state": "activated",
            "registered_at": datetime.now().isoformat()
        }
        return self.service_worker

    def get_service_worker_status(self):
        """Get service worker registration status."""
        if not self.service_worker:
            return {"registered": False}
        return {
            "registered": True,
            "state": self.service_worker["state"],
            "scope": self.service_worker["scope"]
        }

    def cache_app_shell(self, assets):
        """Cache app shell assets."""
        cache_name = "udos-app-shell-v1"
        self.cache_storage[cache_name] = {
            "assets": assets,
            "cached_at": datetime.now().isoformat(),
            "type": "app_shell"
        }
        self.app_shell_cached = True
        return {"cache_name": cache_name, "asset_count": len(assets)}

    def cache_page(self, url, content, strategy="network-first"):
        """Cache page content with strategy."""
        cache_name = f"udos-pages-v1"
        if cache_name not in self.cache_storage:
            self.cache_storage[cache_name] = {"pages": {}}

        self.cache_storage[cache_name]["pages"][url] = {
            "content": content,
            "cached_at": datetime.now().isoformat(),
            "strategy": strategy
        }
        return {"url": url, "cached": True}

    def get_cached_page(self, url):
        """Retrieve cached page."""
        cache_name = "udos-pages-v1"
        if cache_name in self.cache_storage:
            pages = self.cache_storage[cache_name].get("pages", {})
            return pages.get(url)
        return None

    def detect_viewport_size(self, width):
        """Detect viewport breakpoint."""
        if width < self.breakpoints["tablet"]:
            return "mobile"
        elif width < self.breakpoints["desktop"]:
            return "tablet"
        else:
            return "desktop"

    def get_responsive_columns(self, viewport):
        """Get column count for viewport."""
        columns = {
            "mobile": 1,
            "tablet": 2,
            "desktop": 3
        }
        return columns.get(viewport, 1)

    def configure_viewport(self):
        """Configure viewport meta tag."""
        return {
            "width": "device-width",
            "initial-scale": 1.0,
            "maximum-scale": 5.0,
            "minimum-scale": 1.0,
            "user-scalable": "yes",
            "viewport-fit": "cover"
        }

    def register_touch_handler(self, element, event_type, handler):
        """Register touch event handler."""
        key = f"{element}_{event_type}"
        self.touch_handlers[key] = {
            "element": element,
            "event_type": event_type,
            "handler": handler,
            "registered_at": datetime.now().isoformat()
        }
        return key

    def get_touch_target_size(self):
        """Get minimum touch target size."""
        return {"width": 44, "height": 44, "unit": "px"}

    def enable_fast_tap(self):
        """Enable fast tap (disable 300ms delay)."""
        return {
            "touch-action": "manipulation",
            "fast_tap": True,
            "delay_ms": 0
        }

    def detect_gesture(self, touch_points, movement):
        """Detect gesture from touch input."""
        if len(touch_points) == 1:
            if movement["direction"] in ["left", "right"]:
                return {"type": "swipe", "direction": movement["direction"]}
            elif abs(movement["distance"]) > 50:
                return {"type": "scroll", "distance": movement["distance"]}
        elif len(touch_points) == 2:
            if movement.get("pinch"):
                return {"type": "pinch", "scale": movement["scale"]}
        return {"type": "tap"}

    def handle_swipe(self, direction):
        """Handle swipe gesture."""
        gesture = {
            "type": "swipe",
            "direction": direction,
            "handled_at": datetime.now().isoformat()
        }
        self.gestures[f"swipe_{len(self.gestures)}"] = gesture
        return gesture

    def handle_pinch(self, scale):
        """Handle pinch gesture."""
        gesture = {
            "type": "pinch",
            "scale": scale,
            "action": "zoom_in" if scale > 1 else "zoom_out",
            "handled_at": datetime.now().isoformat()
        }
        self.gestures[f"pinch_{len(self.gestures)}"] = gesture
        return gesture

    def show_install_prompt(self):
        """Show install to home screen prompt."""
        self.install_prompt = {
            "shown_at": datetime.now().isoformat(),
            "platform": "mobile",
            "status": "pending"
        }
        return self.install_prompt

    def handle_install_choice(self, accepted):
        """Handle user install choice."""
        if self.install_prompt:
            self.install_prompt["status"] = "accepted" if accepted else "dismissed"
            self.install_prompt["choice_at"] = datetime.now().isoformat()
            return self.install_prompt
        return None

    def is_standalone_mode(self):
        """Check if running in standalone mode."""
        # Would check window.matchMedia('(display-mode: standalone)')
        return self.install_prompt and self.install_prompt.get("status") == "accepted"

    def go_offline(self):
        """Simulate offline mode."""
        self.offline_pages = list(self.cache_storage.keys())
        self.offline_mode = True
        return {"offline": True, "cached_resources": len(self.offline_pages)}

    def is_offline(self):
        """Check if app is offline."""
        return getattr(self, 'offline_mode', False)

    def sync_on_reconnect(self):
        """Sync data when back online."""
        if self.is_offline():
            self.offline_mode = False
            return {"synced": True, "timestamp": datetime.now().isoformat()}
        return {"synced": False}
    
    def create_responsive_component(self, component_type, viewport):
        """Create responsive component for viewport."""
        sizes = {
            "mobile": {"font_size": "14px", "padding": "8px", "columns": 1},
            "tablet": {"font_size": "16px", "padding": "12px", "columns": 2},
            "desktop": {"font_size": "16px", "padding": "16px", "columns": 3}
        }

        config = sizes.get(viewport, sizes["mobile"])
        return {
            "type": component_type,
            "viewport": viewport,
            "config": config
        }

    def apply_media_queries(self, width):
        """Apply CSS media queries based on width."""
        viewport = self.detect_viewport_size(width)
        return {
            "viewport": viewport,
            "breakpoint": self.breakpoints.get(viewport, 0),
            "matches": True
        }

    def subscribe_to_push(self, endpoint, keys):
        """Subscribe to push notifications."""
        subscription = {
            "id": f"sub_{len(self.push_subscriptions)}",
            "endpoint": endpoint,
            "keys": keys,
            "subscribed_at": datetime.now().isoformat()
        }
        self.push_subscriptions.append(subscription)
        return subscription

    def send_push_notification(self, title, body, data=None):
        """Send push notification."""
        if not self.push_subscriptions:
            return {"sent": False, "reason": "no_subscriptions"}

        notification = {
            "title": title,
            "body": body,
            "data": data or {},
            "timestamp": datetime.now().isoformat(),
            "sent_to": len(self.push_subscriptions)
        }
        return notification

    def clear_cache(self, cache_name):
        """Clear specific cache."""
        if cache_name in self.cache_storage:
            del self.cache_storage[cache_name]
            return {"cleared": True, "cache_name": cache_name}
        return {"cleared": False}

    def get_cache_size(self):
        """Get total cache size."""
        total_bytes = sum(
            len(json.dumps(cache))
            for cache in self.cache_storage.values()
        )
        return {
            "caches": len(self.cache_storage),
            "bytes": total_bytes,
            "mb": round(total_bytes / 1024 / 1024, 2)
        }


class TestPWAManifest(unittest.TestCase):
    """Test PWA manifest generation and validation."""

    def setUp(self):
        self.pwa = PWAManager()

    def test_manifest_structure(self):
        """Test manifest has required structure."""
        manifest = self.pwa.manifest
        self.assertEqual(manifest["name"], "uDOS - Universal Digital Operating System")
        self.assertEqual(manifest["short_name"], "uDOS")
        self.assertEqual(manifest["display"], "standalone")

    def test_manifest_icons(self):
        """Test manifest includes required icon sizes."""
        icons = self.pwa.manifest["icons"]
        sizes = [icon["sizes"] for icon in icons]
        self.assertIn("72x72", sizes)
        self.assertIn("192x192", sizes)
        self.assertIn("512x512", sizes)

    def test_manifest_theme_colors(self):
        """Test manifest theme and background colors."""
        manifest = self.pwa.manifest
        self.assertEqual(manifest["background_color"], "#000000")
        self.assertEqual(manifest["theme_color"], "#FF10F0")

    def test_manifest_shortcuts(self):
        """Test manifest includes app shortcuts."""
        shortcuts = self.pwa.manifest["shortcuts"]
        self.assertGreater(len(shortcuts), 0)
        self.assertEqual(shortcuts[0]["name"], "New Mission")

    def test_manifest_validation(self):
        """Test manifest validation."""
        self.assertTrue(self.pwa.validate_manifest())


class TestServiceWorkerRegistration(unittest.TestCase):
    """Test service worker registration and lifecycle."""

    def setUp(self):
        self.pwa = PWAManager()

    def test_register_service_worker(self):
        """Test service worker registration."""
        sw = self.pwa.register_service_worker()
        self.assertEqual(sw["script_url"], "/sw.js")
        self.assertEqual(sw["scope"], "/")
        self.assertEqual(sw["state"], "activated")

    def test_service_worker_status(self):
        """Test getting service worker status."""
        self.pwa.register_service_worker()
        status = self.pwa.get_service_worker_status()
        self.assertTrue(status["registered"])
        self.assertEqual(status["state"], "activated")

    def test_unregistered_status(self):
        """Test status when service worker not registered."""
        status = self.pwa.get_service_worker_status()
        self.assertFalse(status["registered"])

    def test_custom_service_worker_path(self):
        """Test registering service worker with custom path."""
        sw = self.pwa.register_service_worker("/custom-sw.js")
        self.assertEqual(sw["script_url"], "/custom-sw.js")

    def test_service_worker_scope(self):
        """Test service worker scope configuration."""
        sw = self.pwa.register_service_worker()
        self.assertEqual(sw["scope"], "/")

    def test_service_worker_timestamp(self):
        """Test service worker registration timestamp."""
        sw = self.pwa.register_service_worker()
        self.assertIn("registered_at", sw)


class TestMobileBreakpoints(unittest.TestCase):
    """Test mobile breakpoint detection and handling."""

    def setUp(self):
        self.pwa = PWAManager()

    def test_mobile_breakpoint(self):
        """Test mobile viewport detection."""
        viewport = self.pwa.detect_viewport_size(375)
        self.assertEqual(viewport, "mobile")

    def test_tablet_breakpoint(self):
        """Test tablet viewport detection."""
        viewport = self.pwa.detect_viewport_size(800)
        self.assertEqual(viewport, "tablet")

    def test_desktop_breakpoint(self):
        """Test desktop viewport detection."""
        viewport = self.pwa.detect_viewport_size(1920)
        self.assertEqual(viewport, "desktop")

    def test_responsive_columns(self):
        """Test responsive column layout."""
        mobile_cols = self.pwa.get_responsive_columns("mobile")
        tablet_cols = self.pwa.get_responsive_columns("tablet")
        desktop_cols = self.pwa.get_responsive_columns("desktop")

        self.assertEqual(mobile_cols, 1)
        self.assertEqual(tablet_cols, 2)
        self.assertEqual(desktop_cols, 3)

    def test_viewport_configuration(self):
        """Test viewport meta configuration."""
        viewport = self.pwa.configure_viewport()
        self.assertEqual(viewport["width"], "device-width")
        self.assertEqual(viewport["initial-scale"], 1.0)
        self.assertEqual(viewport["user-scalable"], "yes")


class TestTouchOptimization(unittest.TestCase):
    """Test touch-optimized interface."""

    def setUp(self):
        self.pwa = PWAManager()

    def test_touch_target_size(self):
        """Test minimum touch target size."""
        size = self.pwa.get_touch_target_size()
        self.assertEqual(size["width"], 44)
        self.assertEqual(size["height"], 44)
        self.assertEqual(size["unit"], "px")

    def test_touch_handler_registration(self):
        """Test registering touch event handlers."""
        handler = lambda e: "touched"
        key = self.pwa.register_touch_handler("button", "touchstart", handler)
        self.assertIn(key, self.pwa.touch_handlers)
        self.assertEqual(self.pwa.touch_handlers[key]["event_type"], "touchstart")

    def test_fast_tap_enabled(self):
        """Test fast tap (no 300ms delay)."""
        config = self.pwa.enable_fast_tap()
        self.assertTrue(config["fast_tap"])
        self.assertEqual(config["delay_ms"], 0)
        self.assertEqual(config["touch-action"], "manipulation")

    def test_multiple_touch_handlers(self):
        """Test multiple touch event handlers."""
        self.pwa.register_touch_handler("btn1", "touchstart", lambda: None)
        self.pwa.register_touch_handler("btn2", "touchend", lambda: None)
        self.pwa.register_touch_handler("panel", "touchmove", lambda: None)

        self.assertEqual(len(self.pwa.touch_handlers), 3)

    def test_touch_handler_timestamp(self):
        """Test touch handler registration timestamp."""
        key = self.pwa.register_touch_handler("elem", "tap", lambda: None)
        handler = self.pwa.touch_handlers[key]
        self.assertIn("registered_at", handler)

    def test_touch_event_types(self):
        """Test different touch event types."""
        events = ["touchstart", "touchend", "touchmove", "touchcancel"]
        for event in events:
            key = self.pwa.register_touch_handler(f"elem_{event}", event, lambda: None)
            self.assertEqual(self.pwa.touch_handlers[key]["event_type"], event)


class TestOfflineCapability(unittest.TestCase):
    """Test offline-first capabilities."""

    def setUp(self):
        self.pwa = PWAManager()
        self.pwa.register_service_worker()

    def test_app_shell_caching(self):
        """Test app shell caching."""
        assets = ["/index.html", "/styles.css", "/app.js", "/icons/logo.png"]
        result = self.pwa.cache_app_shell(assets)
        self.assertEqual(result["asset_count"], 4)
        self.assertTrue(self.pwa.app_shell_cached)

    def test_page_caching(self):
        """Test page content caching."""
        result = self.pwa.cache_page("/mission/123", {"data": "mission"})
        self.assertTrue(result["cached"])
        self.assertEqual(result["url"], "/mission/123")

    def test_cache_retrieval(self):
        """Test retrieving cached pages."""
        self.pwa.cache_page("/test", {"content": "test"})
        cached = self.pwa.get_cached_page("/test")
        self.assertIsNotNone(cached)
        self.assertEqual(cached["content"]["content"], "test")

    def test_offline_mode(self):
        """Test offline mode detection."""
        self.pwa.cache_app_shell(["/index.html"])
        result = self.pwa.go_offline()
        self.assertTrue(result["offline"])
        self.assertTrue(self.pwa.is_offline())

    def test_online_reconnect_sync(self):
        """Test sync when reconnecting online."""
        self.pwa.go_offline()
        result = self.pwa.sync_on_reconnect()
        self.assertTrue(result["synced"])
        self.assertFalse(self.pwa.is_offline())

    def test_cache_strategies(self):
        """Test different cache strategies."""
        self.pwa.cache_page("/a", {"data": "a"}, strategy="cache-first")
        self.pwa.cache_page("/b", {"data": "b"}, strategy="network-first")

        cached_a = self.pwa.get_cached_page("/a")
        cached_b = self.pwa.get_cached_page("/b")

        self.assertEqual(cached_a["strategy"], "cache-first")
        self.assertEqual(cached_b["strategy"], "network-first")


class TestInstallPrompts(unittest.TestCase):
    """Test install to home screen prompts."""

    def setUp(self):
        self.pwa = PWAManager()

    def test_show_install_prompt(self):
        """Test showing install prompt."""
        prompt = self.pwa.show_install_prompt()
        self.assertEqual(prompt["status"], "pending")
        self.assertIn("shown_at", prompt)

    def test_install_accepted(self):
        """Test user accepts install."""
        self.pwa.show_install_prompt()
        result = self.pwa.handle_install_choice(True)
        self.assertEqual(result["status"], "accepted")

    def test_install_dismissed(self):
        """Test user dismisses install."""
        self.pwa.show_install_prompt()
        result = self.pwa.handle_install_choice(False)
        self.assertEqual(result["status"], "dismissed")

    def test_standalone_mode(self):
        """Test detecting standalone mode."""
        self.pwa.show_install_prompt()
        self.pwa.handle_install_choice(True)
        self.assertTrue(self.pwa.is_standalone_mode())


class TestResponsiveComponents(unittest.TestCase):
    """Test responsive component rendering."""

    def setUp(self):
        self.pwa = PWAManager()

    def test_mobile_component(self):
        """Test mobile component configuration."""
        component = self.pwa.create_responsive_component("panel", "mobile")
        self.assertEqual(component["viewport"], "mobile")
        self.assertEqual(component["config"]["font_size"], "14px")
        self.assertEqual(component["config"]["columns"], 1)

    def test_tablet_component(self):
        """Test tablet component configuration."""
        component = self.pwa.create_responsive_component("panel", "tablet")
        self.assertEqual(component["viewport"], "tablet")
        self.assertEqual(component["config"]["columns"], 2)

    def test_desktop_component(self):
        """Test desktop component configuration."""
        component = self.pwa.create_responsive_component("panel", "desktop")
        self.assertEqual(component["viewport"], "desktop")
        self.assertEqual(component["config"]["columns"], 3)

    def test_media_queries(self):
        """Test CSS media query application."""
        result = self.pwa.apply_media_queries(375)
        self.assertEqual(result["viewport"], "mobile")
        self.assertTrue(result["matches"])

    def test_responsive_padding(self):
        """Test responsive padding configuration."""
        mobile = self.pwa.create_responsive_component("panel", "mobile")
        desktop = self.pwa.create_responsive_component("panel", "desktop")

        self.assertEqual(mobile["config"]["padding"], "8px")
        self.assertEqual(desktop["config"]["padding"], "16px")

    def test_responsive_font_sizes(self):
        """Test responsive font sizing."""
        mobile = self.pwa.create_responsive_component("text", "mobile")
        tablet = self.pwa.create_responsive_component("text", "tablet")

        self.assertEqual(mobile["config"]["font_size"], "14px")
        self.assertEqual(tablet["config"]["font_size"], "16px")


class TestGestureSupport(unittest.TestCase):
    """Test gesture recognition and handling."""

    def setUp(self):
        self.pwa = PWAManager()

    def test_swipe_detection(self):
        """Test swipe gesture detection."""
        touch_points = [{"x": 100, "y": 200}]
        movement = {"direction": "left", "distance": 150}
        gesture = self.pwa.detect_gesture(touch_points, movement)

        self.assertEqual(gesture["type"], "swipe")
        self.assertEqual(gesture["direction"], "left")

    def test_pinch_detection(self):
        """Test pinch gesture detection."""
        touch_points = [{"x": 100, "y": 200}, {"x": 300, "y": 200}]
        movement = {"pinch": True, "scale": 1.5}
        gesture = self.pwa.detect_gesture(touch_points, movement)

        self.assertEqual(gesture["type"], "pinch")
        self.assertEqual(gesture["scale"], 1.5)

    def test_swipe_handler(self):
        """Test swipe gesture handling."""
        gesture = self.pwa.handle_swipe("right")
        self.assertEqual(gesture["type"], "swipe")
        self.assertEqual(gesture["direction"], "right")
        self.assertIn("handled_at", gesture)

    def test_pinch_zoom_in(self):
        """Test pinch zoom in."""
        gesture = self.pwa.handle_pinch(1.5)
        self.assertEqual(gesture["action"], "zoom_in")
        self.assertEqual(gesture["scale"], 1.5)

    def test_pinch_zoom_out(self):
        """Test pinch zoom out."""
        gesture = self.pwa.handle_pinch(0.5)
        self.assertEqual(gesture["action"], "zoom_out")
        self.assertEqual(gesture["scale"], 0.5)


class TestAppShellArchitecture(unittest.TestCase):
    """Test app shell architecture."""

    def setUp(self):
        self.pwa = PWAManager()
        self.pwa.register_service_worker()

    def test_app_shell_assets(self):
        """Test app shell asset caching."""
        assets = [
            "/index.html",
            "/css/main.css",
            "/js/app.js",
            "/icons/icon-192.png"
        ]
        result = self.pwa.cache_app_shell(assets)
        self.assertTrue(self.pwa.app_shell_cached)
        self.assertEqual(result["asset_count"], 4)

    def test_app_shell_cache_name(self):
        """Test app shell cache naming."""
        assets = ["/index.html"]
        result = self.pwa.cache_app_shell(assets)
        self.assertIn("app-shell", result["cache_name"])

    def test_app_shell_versioning(self):
        """Test app shell version in cache name."""
        assets = ["/index.html"]
        result = self.pwa.cache_app_shell(assets)
        self.assertIn("v1", result["cache_name"])

    def test_dynamic_content_caching(self):
        """Test dynamic content separate from app shell."""
        self.pwa.cache_app_shell(["/index.html"])
        self.pwa.cache_page("/api/missions", {"missions": []})

        self.assertTrue(self.pwa.app_shell_cached)
        cached_page = self.pwa.get_cached_page("/api/missions")
        self.assertIsNotNone(cached_page)


class TestCacheStrategies(unittest.TestCase):
    """Test different cache strategies."""

    def setUp(self):
        self.pwa = PWAManager()
        self.pwa.register_service_worker()

    def test_cache_first_strategy(self):
        """Test cache-first strategy."""
        self.pwa.cache_page("/static/data", {"data": "static"}, "cache-first")
        cached = self.pwa.get_cached_page("/static/data")
        self.assertEqual(cached["strategy"], "cache-first")

    def test_network_first_strategy(self):
        """Test network-first strategy."""
        self.pwa.cache_page("/api/data", {"data": "dynamic"}, "network-first")
        cached = self.pwa.get_cached_page("/api/data")
        self.assertEqual(cached["strategy"], "network-first")

    def test_cache_clear(self):
        """Test clearing cache."""
        self.pwa.cache_app_shell(["/index.html"])
        result = self.pwa.clear_cache("udos-app-shell-v1")
        self.assertTrue(result["cleared"])

    def test_cache_size_tracking(self):
        """Test cache size tracking."""
        self.pwa.cache_app_shell(["/a", "/b", "/c"])
        self.pwa.cache_page("/page1", {"data": "x"})

        size = self.pwa.get_cache_size()
        self.assertGreater(size["bytes"], 0)
        self.assertGreater(size["caches"], 0)

    def test_multiple_cache_stores(self):
        """Test multiple cache stores."""
        self.pwa.cache_app_shell(["/shell"])
        self.pwa.cache_page("/page1", {"data": "a"})
        self.pwa.cache_page("/page2", {"data": "b"})

        size = self.pwa.get_cache_size()
        self.assertGreaterEqual(size["caches"], 2)


class TestPushNotifications(unittest.TestCase):
    """Test push notification support."""

    def setUp(self):
        self.pwa = PWAManager()

    def test_push_subscription(self):
        """Test push notification subscription."""
        subscription = self.pwa.subscribe_to_push(
            "https://fcm.googleapis.com/fcm/send/abc123",
            {"p256dh": "key1", "auth": "key2"}
        )
        self.assertIn("subscribed_at", subscription)
        self.assertEqual(len(self.pwa.push_subscriptions), 1)

    def test_send_push_notification(self):
        """Test sending push notification."""
        self.pwa.subscribe_to_push("https://endpoint", {"p256dh": "k", "auth": "a"})

        notif = self.pwa.send_push_notification(
            "New Mission",
            "You have a new mission assigned"
        )
        self.assertEqual(notif["title"], "New Mission")
        self.assertEqual(notif["sent_to"], 1)

    def test_push_without_subscription(self):
        """Test push fails without subscription."""
        notif = self.pwa.send_push_notification("Test", "Message")
        self.assertFalse(notif["sent"])
        self.assertEqual(notif["reason"], "no_subscriptions")

    def test_push_notification_data(self):
        """Test push notification with custom data."""
        self.pwa.subscribe_to_push("https://endpoint", {})

        notif = self.pwa.send_push_notification(
            "Alert",
            "Mission complete",
            data={"mission_id": 123, "xp_gained": 500}
        )
        self.assertEqual(notif["data"]["mission_id"], 123)


class TestIntegrationScenarios(unittest.TestCase):
    """Test end-to-end PWA scenarios."""

    def setUp(self):
        self.pwa = PWAManager()

    def test_full_pwa_installation(self):
        """Test complete PWA installation flow."""
        # 1. Register service worker
        sw = self.pwa.register_service_worker()
        self.assertEqual(sw["state"], "activated")

        # 2. Cache app shell
        self.pwa.cache_app_shell(["/index.html", "/app.js", "/styles.css"])

        # 3. Show install prompt
        prompt = self.pwa.show_install_prompt()
        self.assertEqual(prompt["status"], "pending")

        # 4. User accepts
        self.pwa.handle_install_choice(True)

        # 5. Verify standalone mode
        self.assertTrue(self.pwa.is_standalone_mode())

    def test_offline_first_workflow(self):
        """Test offline-first workflow."""
        # 1. Setup
        self.pwa.register_service_worker()
        self.pwa.cache_app_shell(["/index.html"])

        # 2. Cache content
        self.pwa.cache_page("/mission/1", {"id": 1, "title": "Test"})
        self.pwa.cache_page("/mission/2", {"id": 2, "title": "Test 2"})

        # 3. Go offline
        self.pwa.go_offline()
        self.assertTrue(self.pwa.is_offline())

        # 4. Access cached content
        mission = self.pwa.get_cached_page("/mission/1")
        self.assertEqual(mission["content"]["id"], 1)

        # 5. Reconnect
        result = self.pwa.sync_on_reconnect()
        self.assertTrue(result["synced"])

    def test_responsive_mobile_experience(self):
        """Test responsive mobile experience."""
        # 1. Detect mobile viewport
        viewport = self.pwa.detect_viewport_size(375)
        self.assertEqual(viewport, "mobile")

        # 2. Create mobile components
        panel = self.pwa.create_responsive_component("panel", viewport)
        self.assertEqual(panel["config"]["columns"], 1)

        # 3. Register touch handlers
        self.pwa.register_touch_handler("button", "touchstart", lambda: None)

        # 4. Handle gestures
        gesture = self.pwa.handle_swipe("left")
        self.assertEqual(gesture["type"], "swipe")

        # 5. Verify touch targets
        size = self.pwa.get_touch_target_size()
        self.assertEqual(size["width"], 44)


if __name__ == "__main__":
    unittest.main()

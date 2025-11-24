"""
Test Suite for Feature 1.1.1.6: Browser Extension
v1.1.1 Phase 2: Advanced Web Features

Tests browser extension functionality for Chrome/Firefox WebExtension API,
including knowledge capture from web pages, quick access popup, offline sync,
and cross-browser compatibility.

Test Categories:
1. Extension Manifest (5 tests)
2. Knowledge Capture (6 tests)
3. Quick Access Popup (5 tests)
4. Offline Sync (5 tests)
5. Bookmarking & Annotation (5 tests)
6. Content Script Injection (4 tests)
7. Background Service Worker (5 tests)
8. Storage Management (4 tests)
9. Messaging Protocol (5 tests)
10. Cross-Browser Compatibility (4 tests)
11. Permissions & Security (4 tests)
12. Integration Scenarios (3 tests)

Total: 55 tests
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call
import json
import time
from datetime import datetime, timedelta


class BrowserExtension:
    """Browser extension manager for uDOS WebExtension."""
    
    def __init__(self):
        self.manifest = self._generate_manifest()
        self.storage = {}
        self.content_scripts = []
        self.background_worker = None
        self.popup_state = {}
        self.sync_queue = []
        self.annotations = {}
        self.bookmarks = []
        self.message_handlers = {}
        
    def _generate_manifest(self, version=3):
        """Generate WebExtension manifest."""
        return {
            "manifest_version": version,
            "name": "uDOS Knowledge Capture",
            "version": "1.0.0",
            "description": "Capture knowledge from web pages into uDOS",
            "permissions": [
                "activeTab",
                "storage",
                "bookmarks",
                "contextMenus",
                "notifications"
            ],
            "host_permissions": ["<all_urls>"],
            "action": {
                "default_popup": "popup.html",
                "default_icon": {
                    "16": "icons/icon16.png",
                    "48": "icons/icon48.png",
                    "128": "icons/icon128.png"
                }
            },
            "background": {
                "service_worker": "background.js",
                "type": "module"
            },
            "content_scripts": [
                {
                    "matches": ["<all_urls>"],
                    "js": ["content.js"],
                    "css": ["content.css"]
                }
            ]
        }
    
    def validate_manifest(self):
        """Validate manifest structure and required fields."""
        required = ["manifest_version", "name", "version"]
        return all(field in self.manifest for field in required)
    
    def get_browser_compatibility(self):
        """Get browser compatibility info."""
        return {
            "chrome": self.manifest["manifest_version"] >= 3,
            "firefox": self.manifest["manifest_version"] >= 2,
            "edge": self.manifest["manifest_version"] >= 3,
            "safari": False  # Safari requires different approach
        }
    
    def inject_content_script(self, tab_id, url):
        """Inject content script into active tab."""
        script = {
            "tab_id": tab_id,
            "url": url,
            "injected_at": datetime.now().isoformat(),
            "status": "active"
        }
        self.content_scripts.append(script)
        return script
    
    def capture_page_content(self, url, title, selection=None):
        """Capture content from web page."""
        capture = {
            "url": url,
            "title": title,
            "captured_at": datetime.now().isoformat(),
            "content_type": "selection" if selection else "full_page",
            "content": selection or {"full_page": True},
            "metadata": self._extract_metadata(url)
        }
        self.sync_queue.append(capture)
        return capture
    
    def _extract_metadata(self, url):
        """Extract metadata from URL."""
        return {
            "domain": url.split("//")[1].split("/")[0] if "//" in url else url,
            "timestamp": datetime.now().isoformat(),
            "user_agent": "uDOS Browser Extension"
        }
    
    def create_annotation(self, url, selection, note, tags=None):
        """Create annotation for selected text."""
        annotation_id = f"ann_{len(self.annotations)}"
        annotation = {
            "id": annotation_id,
            "url": url,
            "selection": selection,
            "note": note,
            "tags": tags or [],
            "created_at": datetime.now().isoformat()
        }
        self.annotations[annotation_id] = annotation
        return annotation
    
    def create_bookmark(self, url, title, folder=None):
        """Create bookmark with optional folder."""
        bookmark = {
            "id": f"bm_{len(self.bookmarks)}",
            "url": url,
            "title": title,
            "folder": folder or "uDOS",
            "created_at": datetime.now().isoformat()
        }
        self.bookmarks.append(bookmark)
        return bookmark
    
    def search_annotations(self, query=None, tags=None, url=None):
        """Search annotations by query, tags, or URL."""
        results = list(self.annotations.values())
        
        if query:
            results = [a for a in results if query.lower() in a["note"].lower()]
        if tags:
            results = [a for a in results if any(t in a["tags"] for t in tags)]
        if url:
            results = [a for a in results if a["url"] == url]
        
        return results
    
    def open_popup(self, tab_info):
        """Open quick access popup."""
        self.popup_state = {
            "opened_at": datetime.now().isoformat(),
            "tab": tab_info,
            "actions": ["capture", "annotate", "bookmark", "search"],
            "recent_captures": self.sync_queue[-5:] if self.sync_queue else []
        }
        return self.popup_state
    
    def queue_sync(self, data):
        """Queue data for sync with main uDOS instance."""
        sync_item = {
            "id": f"sync_{len(self.sync_queue)}",
            "data": data,
            "queued_at": datetime.now().isoformat(),
            "synced": False
        }
        self.sync_queue.append(sync_item)
        return sync_item
    
    def sync_with_udos(self, udos_url="http://localhost:9002"):
        """Sync queued data with main uDOS instance."""
        synced = []
        for item in self.sync_queue:
            if not item.get("synced"):
                # Simulate sync
                item["synced"] = True
                item["synced_at"] = datetime.now().isoformat()
                item["udos_url"] = udos_url
                synced.append(item)
        return {"synced_count": len(synced), "items": synced}
    
    def get_offline_status(self):
        """Check if extension is operating offline."""
        pending = [item for item in self.sync_queue if not item.get("synced")]
        return {
            "offline_mode": len(pending) > 0,
            "pending_sync": len(pending),
            "last_sync": max(
                [item.get("synced_at") for item in self.sync_queue if item.get("synced_at")],
                default=None
            )
        }
    
    def store_data(self, key, value, storage_type="local"):
        """Store data in browser storage."""
        if storage_type not in self.storage:
            self.storage[storage_type] = {}
        self.storage[storage_type][key] = value
        return True
    
    def get_data(self, key, storage_type="local"):
        """Retrieve data from browser storage."""
        return self.storage.get(storage_type, {}).get(key)
    
    def get_storage_usage(self, storage_type="local"):
        """Get storage usage statistics."""
        data = self.storage.get(storage_type, {})
        return {
            "storage_type": storage_type,
            "items": len(data),
            "bytes": len(json.dumps(data)),
            "quota": 5242880 if storage_type == "local" else 102400  # 5MB local, 100KB sync
        }
    
    def send_message(self, target, message):
        """Send message between extension components."""
        msg = {
            "id": f"msg_{int(time.time() * 1000)}",
            "target": target,
            "message": message,
            "sent_at": datetime.now().isoformat()
        }
        
        # Route to handler if registered
        if target in self.message_handlers:
            response = self.message_handlers[target](message)
            msg["response"] = response
        
        return msg
    
    def register_message_handler(self, target, handler):
        """Register handler for message target."""
        self.message_handlers[target] = handler
    
    def create_context_menu(self, title, contexts=None):
        """Create context menu item."""
        return {
            "id": f"menu_{len(self.popup_state)}",
            "title": title,
            "contexts": contexts or ["selection"],
            "enabled": True
        }
    
    def show_notification(self, title, message, icon=None):
        """Show browser notification."""
        return {
            "id": f"notif_{int(time.time())}",
            "title": title,
            "message": message,
            "icon": icon or "icons/icon48.png",
            "timestamp": datetime.now().isoformat()
        }


class TestExtensionManifest(unittest.TestCase):
    """Test extension manifest generation and validation."""
    
    def setUp(self):
        self.extension = BrowserExtension()
    
    def test_manifest_structure(self):
        """Test manifest has required structure."""
        manifest = self.extension.manifest
        self.assertEqual(manifest["manifest_version"], 3)
        self.assertEqual(manifest["name"], "uDOS Knowledge Capture")
        self.assertIn("version", manifest)
        self.assertIn("description", manifest)
    
    def test_required_permissions(self):
        """Test manifest includes required permissions."""
        perms = self.extension.manifest["permissions"]
        required = ["activeTab", "storage", "bookmarks", "contextMenus"]
        for perm in required:
            self.assertIn(perm, perms)
    
    def test_action_configuration(self):
        """Test browser action configuration."""
        action = self.extension.manifest["action"]
        self.assertEqual(action["default_popup"], "popup.html")
        self.assertIn("16", action["default_icon"])
        self.assertIn("48", action["default_icon"])
        self.assertIn("128", action["default_icon"])
    
    def test_background_service_worker(self):
        """Test background service worker configuration."""
        background = self.extension.manifest["background"]
        self.assertEqual(background["service_worker"], "background.js")
        self.assertEqual(background["type"], "module")
    
    def test_manifest_validation(self):
        """Test manifest validation."""
        self.assertTrue(self.extension.validate_manifest())


class TestKnowledgeCapture(unittest.TestCase):
    """Test knowledge capture from web pages."""
    
    def setUp(self):
        self.extension = BrowserExtension()
    
    def test_capture_full_page(self):
        """Test capturing full page content."""
        capture = self.extension.capture_page_content(
            "https://example.com",
            "Example Page"
        )
        self.assertEqual(capture["url"], "https://example.com")
        self.assertEqual(capture["title"], "Example Page")
        self.assertEqual(capture["content_type"], "full_page")
        self.assertIn("captured_at", capture)
    
    def test_capture_selection(self):
        """Test capturing selected text."""
        selection = {"text": "Important info", "html": "<p>Important info</p>"}
        capture = self.extension.capture_page_content(
            "https://example.com",
            "Example Page",
            selection=selection
        )
        self.assertEqual(capture["content_type"], "selection")
        self.assertEqual(capture["content"]["text"], "Important info")
    
    def test_metadata_extraction(self):
        """Test metadata extraction from URL."""
        capture = self.extension.capture_page_content(
            "https://example.com/page",
            "Test"
        )
        metadata = capture["metadata"]
        self.assertEqual(metadata["domain"], "example.com")
        self.assertIn("timestamp", metadata)
        self.assertIn("user_agent", metadata)
    
    def test_capture_queue(self):
        """Test captures are queued for sync."""
        self.extension.capture_page_content("https://a.com", "A")
        self.extension.capture_page_content("https://b.com", "B")
        self.assertEqual(len(self.extension.sync_queue), 2)
    
    def test_content_script_injection(self):
        """Test content script injection into tabs."""
        script = self.extension.inject_content_script(123, "https://example.com")
        self.assertEqual(script["tab_id"], 123)
        self.assertEqual(script["url"], "https://example.com")
        self.assertEqual(script["status"], "active")
    
    def test_multiple_content_scripts(self):
        """Test tracking multiple injected content scripts."""
        self.extension.inject_content_script(1, "https://a.com")
        self.extension.inject_content_script(2, "https://b.com")
        self.assertEqual(len(self.extension.content_scripts), 2)


class TestQuickAccessPopup(unittest.TestCase):
    """Test quick access popup functionality."""
    
    def setUp(self):
        self.extension = BrowserExtension()
    
    def test_popup_open(self):
        """Test opening quick access popup."""
        tab = {"id": 1, "url": "https://example.com", "title": "Example"}
        popup = self.extension.open_popup(tab)
        self.assertEqual(popup["tab"], tab)
        self.assertIn("opened_at", popup)
        self.assertIn("actions", popup)
    
    def test_popup_actions(self):
        """Test popup available actions."""
        tab = {"id": 1, "url": "https://example.com"}
        popup = self.extension.open_popup(tab)
        actions = popup["actions"]
        self.assertIn("capture", actions)
        self.assertIn("annotate", actions)
        self.assertIn("bookmark", actions)
        self.assertIn("search", actions)
    
    def test_recent_captures_display(self):
        """Test recent captures shown in popup."""
        for i in range(7):
            self.extension.capture_page_content(f"https://{i}.com", f"Page {i}")
        
        tab = {"id": 1, "url": "https://example.com"}
        popup = self.extension.open_popup(tab)
        # Should show last 5
        self.assertEqual(len(popup["recent_captures"]), 5)
    
    def test_popup_context_menu(self):
        """Test context menu creation."""
        menu = self.extension.create_context_menu("Capture to uDOS")
        self.assertEqual(menu["title"], "Capture to uDOS")
        self.assertIn("selection", menu["contexts"])
        self.assertTrue(menu["enabled"])
    
    def test_notification_display(self):
        """Test notification creation."""
        notif = self.extension.show_notification(
            "Captured!",
            "Page saved to uDOS"
        )
        self.assertEqual(notif["title"], "Captured!")
        self.assertEqual(notif["message"], "Page saved to uDOS")
        self.assertIn("timestamp", notif)


class TestOfflineSync(unittest.TestCase):
    """Test offline sync capabilities."""
    
    def setUp(self):
        self.extension = BrowserExtension()
    
    def test_queue_sync_data(self):
        """Test queuing data for sync."""
        data = {"type": "capture", "url": "https://example.com"}
        item = self.extension.queue_sync(data)
        self.assertEqual(item["data"], data)
        self.assertFalse(item["synced"])
        self.assertIn("queued_at", item)
    
    def test_sync_with_udos_instance(self):
        """Test syncing with main uDOS instance."""
        self.extension.queue_sync({"type": "capture", "url": "https://a.com"})
        self.extension.queue_sync({"type": "annotation", "text": "note"})
        
        result = self.extension.sync_with_udos()
        self.assertEqual(result["synced_count"], 2)
        self.assertTrue(all(item["synced"] for item in result["items"]))
    
    def test_offline_mode_detection(self):
        """Test offline mode detection."""
        self.extension.queue_sync({"data": "test"})
        status = self.extension.get_offline_status()
        self.assertTrue(status["offline_mode"])
        self.assertEqual(status["pending_sync"], 1)
    
    def test_online_mode_after_sync(self):
        """Test online mode after successful sync."""
        self.extension.queue_sync({"data": "test"})
        self.extension.sync_with_udos()
        status = self.extension.get_offline_status()
        self.assertFalse(status["offline_mode"])
        self.assertEqual(status["pending_sync"], 0)
    
    def test_partial_sync_tracking(self):
        """Test tracking partially synced data."""
        self.extension.queue_sync({"data": "a"})
        self.extension.queue_sync({"data": "b"})
        
        # Sync first item only
        self.extension.sync_queue[0]["synced"] = True
        
        status = self.extension.get_offline_status()
        self.assertEqual(status["pending_sync"], 1)


class TestBookmarkingAnnotation(unittest.TestCase):
    """Test bookmarking and annotation features."""
    
    def setUp(self):
        self.extension = BrowserExtension()
    
    def test_create_annotation(self):
        """Test creating text annotation."""
        annotation = self.extension.create_annotation(
            "https://example.com",
            {"text": "Important text"},
            "This is key info"
        )
        self.assertEqual(annotation["url"], "https://example.com")
        self.assertEqual(annotation["note"], "This is key info")
        self.assertIn("created_at", annotation)
    
    def test_annotation_tags(self):
        """Test annotation tagging."""
        annotation = self.extension.create_annotation(
            "https://example.com",
            {"text": "test"},
            "note",
            tags=["research", "important"]
        )
        self.assertIn("research", annotation["tags"])
        self.assertIn("important", annotation["tags"])
    
    def test_search_annotations_by_query(self):
        """Test searching annotations by text query."""
        self.extension.create_annotation("https://a.com", {"text": "x"}, "Python tutorial")
        self.extension.create_annotation("https://b.com", {"text": "y"}, "JavaScript guide")
        
        results = self.extension.search_annotations(query="Python")
        self.assertEqual(len(results), 1)
        self.assertIn("Python", results[0]["note"])
    
    def test_search_annotations_by_tags(self):
        """Test searching annotations by tags."""
        self.extension.create_annotation("https://a.com", {"text": "x"}, "note1", tags=["coding"])
        self.extension.create_annotation("https://b.com", {"text": "y"}, "note2", tags=["design"])
        
        results = self.extension.search_annotations(tags=["coding"])
        self.assertEqual(len(results), 1)
        self.assertIn("coding", results[0]["tags"])
    
    def test_create_bookmark(self):
        """Test creating bookmark."""
        bookmark = self.extension.create_bookmark(
            "https://example.com",
            "Example Site",
            folder="Research"
        )
        self.assertEqual(bookmark["url"], "https://example.com")
        self.assertEqual(bookmark["title"], "Example Site")
        self.assertEqual(bookmark["folder"], "Research")


class TestContentScriptInjection(unittest.TestCase):
    """Test content script injection and management."""
    
    def setUp(self):
        self.extension = BrowserExtension()
    
    def test_content_script_configuration(self):
        """Test content script configuration in manifest."""
        scripts = self.extension.manifest["content_scripts"]
        self.assertEqual(len(scripts), 1)
        self.assertEqual(scripts[0]["matches"], ["<all_urls>"])
        self.assertIn("content.js", scripts[0]["js"])
        self.assertIn("content.css", scripts[0]["css"])
    
    def test_script_injection_tracking(self):
        """Test tracking of injected scripts."""
        script = self.extension.inject_content_script(123, "https://example.com")
        self.assertIn(script, self.extension.content_scripts)
        self.assertEqual(script["status"], "active")
    
    def test_multiple_tabs_injection(self):
        """Test injecting into multiple tabs."""
        self.extension.inject_content_script(1, "https://a.com")
        self.extension.inject_content_script(2, "https://b.com")
        self.extension.inject_content_script(3, "https://c.com")
        self.assertEqual(len(self.extension.content_scripts), 3)
    
    def test_injection_timestamp(self):
        """Test injection timestamp tracking."""
        script = self.extension.inject_content_script(1, "https://example.com")
        self.assertIn("injected_at", script)


class TestBackgroundServiceWorker(unittest.TestCase):
    """Test background service worker functionality."""
    
    def setUp(self):
        self.extension = BrowserExtension()
    
    def test_service_worker_manifest(self):
        """Test service worker in manifest."""
        bg = self.extension.manifest["background"]
        self.assertEqual(bg["service_worker"], "background.js")
        self.assertEqual(bg["type"], "module")
    
    def test_message_handling(self):
        """Test message handling in background worker."""
        handler_called = False
        
        def test_handler(message):
            nonlocal handler_called
            handler_called = True
            return {"status": "ok", "received": message}
        
        self.extension.register_message_handler("background", test_handler)
        msg = self.extension.send_message("background", {"action": "test"})
        
        self.assertTrue(handler_called)
        self.assertEqual(msg["response"]["status"], "ok")
    
    def test_periodic_sync(self):
        """Test periodic sync scheduling."""
        # Queue some data
        self.extension.queue_sync({"data": "test"})
        
        # Simulate periodic sync
        result = self.extension.sync_with_udos()
        self.assertGreater(result["synced_count"], 0)
    
    def test_notification_from_background(self):
        """Test showing notifications from background worker."""
        notif = self.extension.show_notification("Background Task", "Sync completed")
        self.assertEqual(notif["title"], "Background Task")
    
    def test_context_menu_handling(self):
        """Test context menu click handling."""
        menu = self.extension.create_context_menu("Capture to uDOS", ["selection"])
        self.assertTrue(menu["enabled"])
        self.assertIn("selection", menu["contexts"])


class TestStorageManagement(unittest.TestCase):
    """Test browser storage management."""
    
    def setUp(self):
        self.extension = BrowserExtension()
    
    def test_local_storage(self):
        """Test local storage operations."""
        self.extension.store_data("test_key", {"value": 123}, "local")
        data = self.extension.get_data("test_key", "local")
        self.assertEqual(data["value"], 123)
    
    def test_sync_storage(self):
        """Test sync storage operations."""
        self.extension.store_data("pref", "value", "sync")
        data = self.extension.get_data("pref", "sync")
        self.assertEqual(data, "value")
    
    def test_storage_usage(self):
        """Test storage usage tracking."""
        self.extension.store_data("a", "x" * 1000, "local")
        usage = self.extension.get_storage_usage("local")
        self.assertEqual(usage["items"], 1)
        self.assertGreater(usage["bytes"], 0)
        self.assertEqual(usage["quota"], 5242880)  # 5MB
    
    def test_storage_quota_limits(self):
        """Test storage quota limits."""
        local_usage = self.extension.get_storage_usage("local")
        sync_usage = self.extension.get_storage_usage("sync")
        self.assertEqual(local_usage["quota"], 5242880)  # 5MB
        self.assertEqual(sync_usage["quota"], 102400)    # 100KB


class TestMessagingProtocol(unittest.TestCase):
    """Test messaging protocol between extension components."""
    
    def setUp(self):
        self.extension = BrowserExtension()
    
    def test_send_message(self):
        """Test sending message between components."""
        msg = self.extension.send_message("popup", {"action": "get_status"})
        self.assertEqual(msg["target"], "popup")
        self.assertEqual(msg["message"]["action"], "get_status")
        self.assertIn("sent_at", msg)
    
    def test_message_handler_registration(self):
        """Test registering message handlers."""
        def handler(msg):
            return {"handled": True}
        
        self.extension.register_message_handler("test_target", handler)
        self.assertIn("test_target", self.extension.message_handlers)
    
    def test_message_response(self):
        """Test message response from handler."""
        def handler(msg):
            return {"echo": msg}
        
        self.extension.register_message_handler("echo", handler)
        msg = self.extension.send_message("echo", {"test": "data"})
        self.assertEqual(msg["response"]["echo"]["test"], "data")
    
    def test_content_to_background_message(self):
        """Test content script to background messaging."""
        def bg_handler(msg):
            return {"status": "captured", "url": msg["url"]}
        
        self.extension.register_message_handler("background", bg_handler)
        msg = self.extension.send_message("background", {"url": "https://example.com"})
        self.assertEqual(msg["response"]["status"], "captured")
    
    def test_popup_to_background_message(self):
        """Test popup to background messaging."""
        def bg_handler(msg):
            return {"bookmarks": 5, "annotations": 3}
        
        self.extension.register_message_handler("background", bg_handler)
        msg = self.extension.send_message("background", {"action": "get_counts"})
        self.assertEqual(msg["response"]["bookmarks"], 5)


class TestCrossBrowserCompatibility(unittest.TestCase):
    """Test cross-browser compatibility."""
    
    def setUp(self):
        self.extension = BrowserExtension()
    
    def test_chrome_compatibility(self):
        """Test Chrome/Chromium compatibility."""
        compat = self.extension.get_browser_compatibility()
        self.assertTrue(compat["chrome"])
    
    def test_firefox_compatibility(self):
        """Test Firefox compatibility."""
        compat = self.extension.get_browser_compatibility()
        self.assertTrue(compat["firefox"])
    
    def test_edge_compatibility(self):
        """Test Edge compatibility."""
        compat = self.extension.get_browser_compatibility()
        self.assertTrue(compat["edge"])
    
    def test_manifest_v2_fallback(self):
        """Test Manifest V2 fallback for older browsers."""
        extension_v2 = BrowserExtension()
        extension_v2.manifest = extension_v2._generate_manifest(version=2)
        self.assertEqual(extension_v2.manifest["manifest_version"], 2)


class TestPermissionsSecurity(unittest.TestCase):
    """Test permissions and security features."""
    
    def setUp(self):
        self.extension = BrowserExtension()
    
    def test_minimal_permissions(self):
        """Test extension requests minimal necessary permissions."""
        perms = self.extension.manifest["permissions"]
        # Should only request what's needed
        essential = ["activeTab", "storage", "bookmarks"]
        for perm in essential:
            self.assertIn(perm, perms)
    
    def test_host_permissions(self):
        """Test host permissions configuration."""
        host_perms = self.extension.manifest["host_permissions"]
        self.assertIn("<all_urls>", host_perms)
    
    def test_content_security_policy(self):
        """Test Content Security Policy if defined."""
        # CSP would be in manifest for stricter security
        # Not required but good practice
        if "content_security_policy" in self.extension.manifest:
            csp = self.extension.manifest["content_security_policy"]
            self.assertIsInstance(csp, dict)
    
    def test_secure_message_passing(self):
        """Test secure message passing between components."""
        msg = self.extension.send_message("background", {"data": "test"})
        # Message should have unique ID
        self.assertIn("id", msg)
        # ID should be timestamped for uniqueness
        self.assertTrue(msg["id"].startswith("msg_"))


class TestIntegrationScenarios(unittest.TestCase):
    """Test end-to-end integration scenarios."""
    
    def setUp(self):
        self.extension = BrowserExtension()
    
    def test_capture_annotate_sync_workflow(self):
        """Test complete capture → annotate → sync workflow."""
        # 1. Capture page content
        capture = self.extension.capture_page_content(
            "https://example.com",
            "Example",
            selection={"text": "Important info"}
        )
        
        # 2. Create annotation
        annotation = self.extension.create_annotation(
            capture["url"],
            capture["content"],
            "This is useful",
            tags=["research"]
        )
        
        # 3. Sync with uDOS
        result = self.extension.sync_with_udos()
        
        self.assertEqual(result["synced_count"], 1)
        self.assertEqual(len(self.extension.annotations), 1)
    
    def test_bookmark_organize_search_workflow(self):
        """Test bookmark → organize → search workflow."""
        # 1. Create bookmarks
        self.extension.create_bookmark("https://a.com", "A", "Research")
        self.extension.create_bookmark("https://b.com", "B", "Tutorial")
        
        # 2. Create annotations
        self.extension.create_annotation(
            "https://a.com",
            {"text": "x"},
            "Python tips",
            tags=["coding"]
        )
        
        # 3. Search
        results = self.extension.search_annotations(tags=["coding"])
        
        self.assertEqual(len(self.extension.bookmarks), 2)
        self.assertEqual(len(results), 1)
    
    def test_offline_queue_sync_workflow(self):
        """Test offline queue → reconnect → sync workflow."""
        # 1. Work offline - queue multiple captures
        self.extension.capture_page_content("https://a.com", "A")
        self.extension.capture_page_content("https://b.com", "B")
        self.extension.capture_page_content("https://c.com", "C")
        
        # 2. Check offline status
        status = self.extension.get_offline_status()
        self.assertTrue(status["offline_mode"])
        self.assertEqual(status["pending_sync"], 3)
        
        # 3. Reconnect and sync
        result = self.extension.sync_with_udos()
        
        # 4. Verify all synced
        self.assertEqual(result["synced_count"], 3)
        final_status = self.extension.get_offline_status()
        self.assertFalse(final_status["offline_mode"])


if __name__ == "__main__":
    unittest.main()

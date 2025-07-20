# 🌍 uDOS Web Browser Installer Template

**Template Version**: v2.0.0  
**Platform**: Web Browser (PWA)  
**Method**: Progressive Web Application  
**User Role**: {{user_role}}  
**Generated**: {{timestamp}}

---

## 🌐 Web Application Configuration

### Hosting Settings
- **Domain**: {{domain_name}}
- **CDN Provider**: {{cdn_provider}}
- **Hosting Platform**: {{hosting_platform}}
- **SSL Certificate**: {{ssl_enabled}}

### PWA Configuration
- **App Name**: {{app_name}}
- **Service Worker**: {{enable_service_worker}}
- **Offline Support**: {{enable_offline}}
- **Cache Strategy**: {{cache_strategy}}

---

## 📱 Progressive Web App Manifest

```json
{
  "name": "{{app_name}}",
  "short_name": "uDOS",
  "description": "uDOS - Markdown-Native Operating System",
  "version": "{{udos_version}}",
  "start_url": "/",
  "display": "standalone",
  "orientation": "any",
  "theme_color": "#2563eb",
  "background_color": "#ffffff",
  "categories": ["productivity", "developer", "education"],
  "lang": "en",
  "scope": "/",
  "icons": [
    {
      "src": "/icons/icon-72x72.png",
      "sizes": "72x72",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/icons/icon-96x96.png",
      "sizes": "96x96",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/icons/icon-128x128.png",
      "sizes": "128x128",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/icons/icon-144x144.png",
      "sizes": "144x144",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/icons/icon-152x152.png",
      "sizes": "152x152",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/icons/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/icons/icon-384x384.png",
      "sizes": "384x384",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/icons/icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "maskable any"
    }
  ],
  "shortcuts": [
    {
      "name": "New Mission",
      "short_name": "Mission",
      "description": "Create a new uDOS mission",
      "url": "/new-mission",
      "icons": [
        {
          "src": "/icons/mission-96x96.png",
          "sizes": "96x96"
        }
      ]
    },
    {
      "name": "Dashboard",
      "short_name": "Dashboard",
      "description": "Open uDOS dashboard",
      "url": "/dashboard",
      "icons": [
        {
          "src": "/icons/dashboard-96x96.png",
          "sizes": "96x96"
        }
      ]
    },
    {
      "name": "Chester AI",
      "short_name": "Chester",
      "description": "Chat with Chester AI",
      "url": "/chester",
      "icons": [
        {
          "src": "/icons/chester-96x96.png",
          "sizes": "96x96"
        }
      ]
    }
  ],
  "screenshots": [
    {
      "src": "/screenshots/desktop-wide.png",
      "sizes": "1280x720",
      "type": "image/png",
      "form_factor": "wide",
      "label": "uDOS Dashboard on Desktop"
    },
    {
      "src": "/screenshots/mobile-narrow.png",
      "sizes": "360x640",
      "type": "image/png",
      "form_factor": "narrow",
      "label": "uDOS Mobile Interface"
    }
  ],
  "related_applications": [],
  "prefer_related_applications": false
}
```

---

## 💻 Service Worker Implementation

```javascript
// service-worker.js - uDOS PWA Service Worker
// Generated from template: {{template_name}}

const CACHE_NAME = 'udos-v{{udos_version}}';
const OFFLINE_URL = '/offline.html';

// Files to cache for offline functionality
const CACHE_FILES = [
  '/',
  '/offline.html',
  '/manifest.json',
  '/css/main.css',
  '/css/themes/{{theme_name}}.css',
  '/js/app.js',
  '/js/udos-core.js',
  '/js/markdown-processor.js',
  '/js/template-engine.js',
  '/icons/icon-192x192.png',
  '/icons/icon-512x512.png'
];

// Install event - cache core files
self.addEventListener('install', event => {
  console.log('[SW] Installing service worker');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('[SW] Caching app shell');
        return cache.addAll(CACHE_FILES);
      })
      .then(() => {
        console.log('[SW] Installation complete');
        return self.skipWaiting();
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  console.log('[SW] Activating service worker');
  
  event.waitUntil(
    caches.keys()
      .then(cacheNames => {
        return Promise.all(
          cacheNames.map(cacheName => {
            if (cacheName !== CACHE_NAME) {
              console.log('[SW] Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('[SW] Activation complete');
        return self.clients.claim();
      })
  );
});

// Fetch event - serve from cache with network fallback
self.addEventListener('fetch', event => {
  // Skip non-GET requests
  if (event.request.method !== 'GET') return;
  
  // Skip external requests
  if (!event.request.url.startsWith(self.location.origin)) return;
  
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        if (response) {
          console.log('[SW] Serving from cache:', event.request.url);
          return response;
        }
        
        console.log('[SW] Fetching from network:', event.request.url);
        return fetch(event.request)
          .then(response => {
            // Cache successful responses
            if (response.status === 200) {
              const responseToCache = response.clone();
              caches.open(CACHE_NAME)
                .then(cache => {
                  cache.put(event.request, responseToCache);
                });
            }
            return response;
          })
          .catch(() => {
            // Return offline page for navigation requests
            if (event.request.mode === 'navigate') {
              return caches.match(OFFLINE_URL);
            }
          });
      })
  );
});

// Background sync for when connection is restored
self.addEventListener('sync', event => {
  if (event.tag === 'udos-sync') {
    console.log('[SW] Background sync triggered');
    event.waitUntil(syncData());
  }
});

// Push notifications
self.addEventListener('push', event => {
  if (event.data) {
    const data = event.data.json();
    const options = {
      body: data.body,
      icon: '/icons/icon-192x192.png',
      badge: '/icons/badge-72x72.png',
      vibrate: [100, 50, 100],
      data: {
        dateOfArrival: Date.now(),
        primaryKey: data.primaryKey || 1
      },
      actions: [
        {
          action: 'explore',
          title: 'Open uDOS',
          icon: '/icons/action-explore.png'
        },
        {
          action: 'close',
          title: 'Close',
          icon: '/icons/action-close.png'
        }
      ]
    };
    
    event.waitUntil(
      self.registration.showNotification(data.title || 'uDOS Notification', options)
    );
  }
});

// Notification click handler
self.addEventListener('notificationclick', event => {
  event.notification.close();
  
  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

// Sync data when connection is restored
async function syncData() {
  try {
    const cache = await caches.open(CACHE_NAME);
    const pendingData = await getStoredData('pending-sync');
    
    if (pendingData.length > 0) {
      for (const item of pendingData) {
        await fetch('/api/sync', {
          method: 'POST',
          body: JSON.stringify(item),
          headers: {
            'Content-Type': 'application/json'
          }
        });
      }
      
      await clearStoredData('pending-sync');
      console.log('[SW] Data sync complete');
    }
  } catch (error) {
    console.error('[SW] Sync failed:', error);
  }
}

// Helper functions for IndexedDB operations
async function getStoredData(key) {
  // Implementation for retrieving stored data
  return [];
}

async function clearStoredData(key) {
  // Implementation for clearing stored data
}
```

---

## 🏗️ Main Application Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{app_name}} - uDOS</title>
    
    <!-- PWA Meta Tags -->
    <meta name="description" content="uDOS - Markdown-Native Operating System">
    <meta name="theme-color" content="#2563eb">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="apple-mobile-web-app-title" content="uDOS">
    <meta name="msapplication-TileImage" content="/icons/icon-144x144.png">
    <meta name="msapplication-TileColor" content="#2563eb">
    
    <!-- Links -->
    <link rel="manifest" href="/manifest.json">
    <link rel="icon" type="image/png" sizes="32x32" href="/icons/icon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/icons/icon-16x16.png">
    <link rel="apple-touch-icon" href="/icons/icon-180x180.png">
    
    <!-- Stylesheets -->
    <link rel="stylesheet" href="/css/main.css">
    <link rel="stylesheet" href="/css/themes/{{theme_name}}.css">
    
    <!-- Preload critical resources -->
    <link rel="preload" href="/js/app.js" as="script">
    <link rel="preload" href="/css/main.css" as="style">
</head>
<body>
    <!-- App Shell -->
    <div id="app" class="app-container">
        <!-- Header -->
        <header class="app-header">
            <div class="header-content">
                <h1 class="app-title">
                    <span class="logo">🌀</span>
                    {{app_name}}
                </h1>
                <nav class="main-nav">
                    <button class="nav-btn" data-view="dashboard">Dashboard</button>
                    <button class="nav-btn" data-view="missions">Missions</button>
                    <button class="nav-btn" data-view="knowledge">Knowledge</button>
                    <button class="nav-btn" data-view="chester">Chester AI</button>
                    <button class="nav-btn" data-view="settings">Settings</button>
                </nav>
                <div class="connection-status">
                    <span id="online-indicator" class="status-indicator online">●</span>
                    <span id="status-text">Online</span>
                </div>
            </div>
        </header>
        
        <!-- Main Content -->
        <main class="app-main">
            <div id="content-area" class="content-area">
                <!-- Dynamic content loaded here -->
                <div class="loading-spinner" id="loading">
                    <div class="spinner"></div>
                    <p>Loading uDOS...</p>
                </div>
            </div>
        </main>
        
        <!-- Footer -->
        <footer class="app-footer">
            <div class="footer-content">
                <span class="version">uDOS v{{udos_version}}</span>
                <span class="user-role">Role: {{user_role}}</span>
                <span class="install-prompt" id="install-prompt" style="display: none;">
                    <button id="install-button" class="install-btn">📱 Install App</button>
                </span>
            </div>
        </footer>
    </div>
    
    <!-- Offline Notification -->
    <div id="offline-notification" class="notification offline-notification" style="display: none;">
        <span>📡 You're offline. Some features may be limited.</span>
        <button class="close-notification">✕</button>
    </div>
    
    <!-- Update Available Notification -->
    <div id="update-notification" class="notification update-notification" style="display: none;">
        <span>🔄 A new version is available!</span>
        <button id="refresh-app" class="refresh-btn">Update</button>
        <button class="close-notification">✕</button>
    </div>
    
    <!-- Scripts -->
    <script src="/js/udos-core.js"></script>
    <script src="/js/markdown-processor.js"></script>
    <script src="/js/template-engine.js"></script>
    <script src="/js/app.js"></script>
    
    <!-- PWA Installation Script -->
    <script>
        // Register service worker
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/service-worker.js')
                .then(registration => {
                    console.log('SW registered:', registration);
                })
                .catch(error => {
                    console.error('SW registration failed:', error);
                });
        }
        
        // Handle PWA installation
        let deferredPrompt;
        
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            document.getElementById('install-prompt').style.display = 'block';
        });
        
        document.getElementById('install-button').addEventListener('click', async () => {
            if (deferredPrompt) {
                deferredPrompt.prompt();
                const { outcome } = await deferredPrompt.userChoice;
                console.log('Install outcome:', outcome);
                deferredPrompt = null;
                document.getElementById('install-prompt').style.display = 'none';
            }
        });
        
        // Handle online/offline status
        function updateOnlineStatus() {
            const indicator = document.getElementById('online-indicator');
            const statusText = document.getElementById('status-text');
            const offlineNotification = document.getElementById('offline-notification');
            
            if (navigator.onLine) {
                indicator.className = 'status-indicator online';
                statusText.textContent = 'Online';
                offlineNotification.style.display = 'none';
            } else {
                indicator.className = 'status-indicator offline';
                statusText.textContent = 'Offline';
                offlineNotification.style.display = 'block';
            }
        }
        
        window.addEventListener('online', updateOnlineStatus);
        window.addEventListener('offline', updateOnlineStatus);
        updateOnlineStatus();
    </script>
</body>
</html>
```

---

## 🎨 CSS Styling Framework

```css
/* main.css - uDOS PWA Styles */
/* Generated from template: {{template_name}} */

:root {
  --primary-color: #2563eb;
  --secondary-color: #64748b;
  --accent-color: #06b6d4;
  --success-color: #10b981;
  --warning-color: #f59e0b;
  --error-color: #ef4444;
  --background-color: #ffffff;
  --surface-color: #f8fafc;
  --text-color: #1e293b;
  --text-muted: #64748b;
  --border-color: #e2e8f0;
  --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  --border-radius: 0.5rem;
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-mono: 'SF Mono', Monaco, 'Cascadia Code', monospace;
}

/* Base styles */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: var(--font-family);
  background-color: var(--background-color);
  color: var(--text-color);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* App container */
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  max-width: 100vw;
  overflow-x: hidden;
}

/* Header */
.app-header {
  background-color: var(--surface-color);
  border-bottom: 1px solid var(--border-color);
  box-shadow: var(--shadow);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md);
  max-width: 1200px;
  margin: 0 auto;
}

.app-title {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--primary-color);
}

.logo {
  font-size: 2rem;
}

/* Navigation */
.main-nav {
  display: flex;
  gap: var(--spacing-sm);
}

.nav-btn {
  padding: var(--spacing-sm) var(--spacing-md);
  border: none;
  border-radius: var(--border-radius);
  background-color: transparent;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 500;
}

.nav-btn:hover,
.nav-btn.active {
  background-color: var(--primary-color);
  color: white;
}

/* Connection status */
.connection-status {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: 0.875rem;
  color: var(--text-muted);
}

.status-indicator {
  font-size: 1rem;
}

.status-indicator.online {
  color: var(--success-color);
}

.status-indicator.offline {
  color: var(--error-color);
}

/* Main content */
.app-main {
  flex: 1;
  padding: var(--spacing-lg);
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.content-area {
  min-height: 60vh;
}

/* Loading spinner */
.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-xl);
}

.spinner {
  width: 3rem;
  height: 3rem;
  border: 3px solid var(--border-color);
  border-top: 3px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Footer */
.app-footer {
  background-color: var(--surface-color);
  border-top: 1px solid var(--border-color);
  padding: var(--spacing-md);
}

.footer-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1200px;
  margin: 0 auto;
  font-size: 0.875rem;
  color: var(--text-muted);
}

.install-btn {
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--primary-color);
  border-radius: var(--border-radius);
  background-color: var(--primary-color);
  color: white;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.install-btn:hover {
  background-color: transparent;
  color: var(--primary-color);
}

/* Notifications */
.notification {
  position: fixed;
  top: var(--spacing-lg);
  right: var(--spacing-lg);
  padding: var(--spacing-md);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow);
  z-index: 1001;
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  max-width: 400px;
}

.offline-notification {
  background-color: var(--warning-color);
  color: white;
}

.update-notification {
  background-color: var(--primary-color);
  color: white;
}

.refresh-btn,
.close-notification {
  padding: var(--spacing-xs) var(--spacing-sm);
  border: 1px solid currentColor;
  border-radius: calc(var(--border-radius) * 0.5);
  background-color: transparent;
  color: currentColor;
  cursor: pointer;
  font-size: 0.75rem;
}

/* Responsive design */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: var(--spacing-md);
  }
  
  .main-nav {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .footer-content {
    flex-direction: column;
    gap: var(--spacing-sm);
    text-align: center;
  }
  
  .notification {
    top: var(--spacing-sm);
    right: var(--spacing-sm);
    left: var(--spacing-sm);
    max-width: none;
  }
}

/* Print styles */
@media print {
  .app-header,
  .app-footer,
  .notification {
    display: none;
  }
  
  .app-main {
    padding: 0;
  }
}

/* High contrast mode */
@media (prefers-contrast: high) {
  :root {
    --border-color: #000000;
    --text-muted: #000000;
  }
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  .spinner {
    animation: none;
  }
  
  .nav-btn,
  .install-btn,
  .refresh-btn {
    transition: none;
  }
}
```

---

## 🚀 Deployment Script

```bash
#!/bin/bash
# uDOS PWA Deployment Script
# Generated from template: {{template_name}}

set -euo pipefail

# Configuration
APP_NAME="{{app_name}}"
DOMAIN="{{domain_name}}"
BUILD_DIR="./build"
DEPLOY_DIR="./deploy"
CDN_PROVIDER="{{cdn_provider}}"
HOSTING_PLATFORM="{{hosting_platform}}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

print_header() {
    echo -e "${BOLD}${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║              🌍 uDOS PWA Deployment Tool                        ║"
    echo "║              App: {{app_name}}                                  ║"
    echo "║              Generated: {{timestamp}}                           ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Check dependencies
check_dependencies() {
    local deps=("node" "npm")
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            log_error "$dep is not installed"
            exit 1
        fi
    done
    
    log_success "Dependencies verified"
}

# Build PWA
build_pwa() {
    log_info "Building PWA..."
    
    # Create build directory
    mkdir -p "$BUILD_DIR"
    
    # Copy static files
    cp -r static/* "$BUILD_DIR/"
    
    # Generate manifest with variables
    envsubst < manifest.template.json > "$BUILD_DIR/manifest.json"
    
    # Generate service worker
    envsubst < service-worker.template.js > "$BUILD_DIR/service-worker.js"
    
    # Generate HTML files
    envsubst < index.template.html > "$BUILD_DIR/index.html"
    envsubst < offline.template.html > "$BUILD_DIR/offline.html"
    
    # Minify CSS and JS if tools available
    if command -v npx &> /dev/null; then
        npx terser "$BUILD_DIR/js/app.js" --output "$BUILD_DIR/js/app.js" --compress --mangle || true
        npx csso "$BUILD_DIR/css/main.css" --output "$BUILD_DIR/css/main.css" || true
    fi
    
    log_success "PWA built successfully"
}

# Deploy to hosting platform
deploy_pwa() {
    log_info "Deploying to $HOSTING_PLATFORM..."
    
    case "$HOSTING_PLATFORM" in
        "netlify")
            deploy_netlify
            ;;
        "vercel")
            deploy_vercel
            ;;
        "github-pages")
            deploy_github_pages
            ;;
        "firebase")
            deploy_firebase
            ;;
        *)
            log_warning "Manual deployment required for $HOSTING_PLATFORM"
            ;;
    esac
}

# Deploy to Netlify
deploy_netlify() {
    if command -v netlify &> /dev/null; then
        netlify deploy --prod --dir="$BUILD_DIR"
        log_success "Deployed to Netlify"
    else
        log_warning "Netlify CLI not installed. Install with: npm install -g netlify-cli"
    fi
}

# Deploy to Vercel
deploy_vercel() {
    if command -v vercel &> /dev/null; then
        vercel --prod "$BUILD_DIR"
        log_success "Deployed to Vercel"
    else
        log_warning "Vercel CLI not installed. Install with: npm install -g vercel"
    fi
}

# Deploy to GitHub Pages
deploy_github_pages() {
    if [ -d ".git" ]; then
        git subtree push --prefix="$BUILD_DIR" origin gh-pages
        log_success "Deployed to GitHub Pages"
    else
        log_warning "Not a Git repository. GitHub Pages deployment skipped."
    fi
}

# Deploy to Firebase
deploy_firebase() {
    if command -v firebase &> /dev/null; then
        firebase deploy --only hosting
        log_success "Deployed to Firebase"
    else
        log_warning "Firebase CLI not installed. Install with: npm install -g firebase-tools"
    fi
}

# Generate deployment info
generate_info() {
    cat > "$DEPLOY_DIR/deployment-info.json" << EOF
{
  "app_name": "$APP_NAME",
  "domain": "$DOMAIN",
  "platform": "$HOSTING_PLATFORM",
  "cdn_provider": "$CDN_PROVIDER",
  "build_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "udos_version": "{{udos_version}}",
  "user_role": "{{user_role}}",
  "features": {
    "offline_support": {{enable_offline}},
    "service_worker": {{enable_service_worker}},
    "push_notifications": false,
    "background_sync": true
  }
}
EOF
    
    log_success "Deployment info generated"
}

# Show deployment summary
show_summary() {
    echo
    log_success "🎉 PWA deployment complete!"
    echo
    echo -e "${BOLD}${GREEN}Deployment Information:${NC}"
    echo "App Name: $APP_NAME"
    echo "Domain: $DOMAIN"
    echo "Platform: $HOSTING_PLATFORM"
    echo "User Role: {{user_role}}"
    echo
    echo -e "${BOLD}${GREEN}PWA Features:${NC}"
    echo "✓ Progressive Web App manifest"
    echo "✓ Service Worker for offline support"
    echo "✓ Responsive design"
    echo "✓ App installation prompts"
    echo "✓ Push notification support"
    echo
    echo -e "${BOLD}${GREEN}Access URLs:${NC}"
    echo "Web App: https://$DOMAIN"
    echo "Manifest: https://$DOMAIN/manifest.json"
    echo "Service Worker: https://$DOMAIN/service-worker.js"
    echo
    echo -e "${BOLD}${GREEN}Next Steps:${NC}"
    echo "1. Test PWA installation on mobile devices"
    echo "2. Configure push notification service"
    echo "3. Set up analytics and monitoring"
    echo "4. Test offline functionality"
}

# Main execution
main() {
    print_header
    
    check_dependencies
    
    # Create deployment directory
    mkdir -p "$DEPLOY_DIR"
    
    build_pwa
    deploy_pwa
    generate_info
    show_summary
}

# Error handling
trap 'log_error "Deployment failed at line $LINENO"' ERR

# Export environment variables for envsubst
export APP_NAME DOMAIN CDN_PROVIDER HOSTING_PLATFORM

# Run main function
main "$@"
```

---

## 📱 Template Variables

### Application Configuration
- `{{app_name}}` - PWA application name
- `{{domain_name}}` - Deployment domain
- `{{theme_name}}` - UI theme selection
- `{{enable_offline}}` - Offline functionality (true/false)

### Hosting Configuration
- `{{hosting_platform}}` - Platform (netlify/vercel/github-pages/firebase)
- `{{cdn_provider}}` - CDN service provider
- `{{ssl_enabled}}` - SSL certificate enabled
- `{{cache_strategy}}` - Caching strategy (cache-first/network-first)

---

*This template creates a complete Progressive Web Application that works across all devices and browsers, with offline support and app installation capabilities.*

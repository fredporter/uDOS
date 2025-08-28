const { contextBridge, ipcRenderer } = require('electron');

/**
 * uDOS Simple Browser Preload Script
 * Provides secure bridge between renderer and main process
 */

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
    // Navigation
    navigateTo: (url) => ipcRenderer.invoke('navigate-to', url),
    
    // Bookmarks
    getBookmarks: () => ipcRenderer.invoke('get-bookmarks'),
    
    // Toast notifications
    showToast: (type, title, message, duration) => 
        ipcRenderer.invoke('show-toast', type, title, message, duration),
    
    // External links
    openExternal: (url) => ipcRenderer.invoke('open-external', url),
    
    // Developer tools
    toggleDevTools: () => ipcRenderer.invoke('toggle-devtools'),
    
    // System info
    getVersion: () => '1.0.5.1',
    getPlatform: () => process.platform
});

// Security: Remove node globals
delete window.require;
delete window.exports;
delete window.module;

// Add uDOS-specific functionality
window.addEventListener('DOMContentLoaded', () => {
    // Add uDOS branding
    console.log('%cuDOS Simple Browser v1.0.5.1', 'color: #0066cc; font-weight: bold; font-size: 14px;');
    console.log('%cSecure browsing environment for uDOS services', 'color: #666666;');
    
    // Security indicator
    const isSecure = window.location.protocol === 'https:' || 
                    window.location.hostname === 'localhost' ||
                    window.location.hostname === '127.0.0.1';
    
    if (!isSecure) {
        console.warn('%cWarning: This page is not served over a secure connection', 'color: #ff6600;');
    }
});

// Handle errors gracefully
window.addEventListener('error', (event) => {
    console.error('Browser error:', event.error);
    if (window.electronAPI) {
        window.electronAPI.showToast('ERROR', 'Browser Error', event.error.message, 8);
    }
});

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    if (window.electronAPI) {
        window.electronAPI.showToast('WARNING', 'Promise Error', 'An async operation failed', 5);
    }
});

// Expose uDOS integration helpers
window.uDOS = {
    version: '1.0.5.1',
    browser: 'simple-browser',
    
    // Helper to send notifications to uDOS
    notify: (type, title, message, duration = 5) => {
        if (window.electronAPI) {
            return window.electronAPI.showToast(type, title, message, duration);
        }
        console.log(`[${type}] ${title}: ${message}`);
        return Promise.resolve(false);
    },
    
    // Helper to navigate to uDOS services
    goToService: (service) => {
        const services = {
            dashboard: 'http://localhost:8080',
            network: 'http://localhost:8081',
            status: 'http://localhost:8080/status',
            dev: 'http://localhost:3000'
        };
        
        const url = services[service];
        if (url && window.electronAPI) {
            return window.electronAPI.navigateTo(url);
        }
        return Promise.resolve(false);
    },
    
    // Helper to check if running in uDOS browser
    isUDOSBrowser: () => true
};

/**
 * uDOS Wizard Server - Client-side JavaScript
 * 
 * Minimal JavaScript for enhanced UX.
 * Most interactivity handled by HTMX + Alpine.js.
 */

// Auto-refresh timestamps
function updateTimestamps() {
    document.querySelectorAll('[data-timestamp]').forEach(el => {
        const timestamp = new Date(el.dataset.timestamp);
        el.textContent = formatRelativeTime(timestamp);
    });
}

// Format relative time (e.g., "2 hours ago")
function formatRelativeTime(date) {
    const now = new Date();
    const diff = now - date;
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (seconds < 60) return `${seconds} sec ago`;
    if (minutes < 60) return `${minutes} min ago`;
    if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    return `${days} day${days > 1 ? 's' : ''} ago`;
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard', 'success');
    });
}

// Show notification toast
function showNotification(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `fixed bottom-4 right-4 px-6 py-3 rounded-lg shadow-lg alert alert-${type} animate-fade-in`;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Update timestamps every 60 seconds
    setInterval(updateTimestamps, 60000);
    updateTimestamps();
    
    // Log HTMX events (debug)
    document.body.addEventListener('htmx:afterRequest', (event) => {
        console.log('HTMX request completed:', event.detail);
    });
});

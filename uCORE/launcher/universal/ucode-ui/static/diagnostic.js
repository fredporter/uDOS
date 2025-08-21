// Diagnostic Script - Add to browser console to debug looping issues

console.log('🔍 uDOS Diagnostic Starting...');

// Check for active intervals/timeouts
let intervalCount = 0;
let timeoutCount = 0;

const originalSetInterval = window.setInterval;
const originalSetTimeout = window.setTimeout;

window.setInterval = function(...args) {
    intervalCount++;
    console.log(`📊 Active intervals: ${intervalCount}`, args);
    return originalSetInterval.apply(this, args);
};

window.setTimeout = function(...args) {
    timeoutCount++;
    console.log(`⏱️ Active timeouts: ${timeoutCount}`, args);
    return originalSetTimeout.apply(this, args);
};

// Check for network activity
let requestCount = 0;
const originalFetch = window.fetch;
window.fetch = function(...args) {
    requestCount++;
    console.log(`🌐 Network request #${requestCount}:`, args[0]);
    return originalFetch.apply(this, args);
};

// Check for font changes
const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
        if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
            console.log('🎨 Class change detected:', mutation.target.className);
        }
    });
});

observer.observe(document.body, { attributes: true });

// Monitor console errors
window.addEventListener('error', (e) => {
    console.log('❌ JavaScript Error:', e.error);
});

console.log('🔍 Diagnostic setup complete. Watch for patterns...');

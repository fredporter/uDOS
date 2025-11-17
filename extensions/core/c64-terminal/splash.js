/**
 * uDOS C64 Terminal - Splash Sequence
 * Handles boot animation and transitions
 * Version: 1.0.24
 */

(function() {
    'use strict';

    // Splash sequence configuration
    const SPLASH_CONFIG = {
        loadingDuration: 2000,      // Loading screen duration (ms)
        splashDuration: 3000,        // Splash screen duration (ms)
        progressSteps: 20,           // Number of progress bar steps
        progressInterval: 150        // Progress update interval (ms)
    };

    // DOM Elements
    let loadingScreen;
    let splashScreen;
    let terminal;
    let progressBar;

    // Initialize when DOM is ready
    function init() {
        // Get DOM elements
        loadingScreen = document.getElementById('loadingScreen');
        splashScreen = document.getElementById('splashScreen');
        terminal = document.getElementById('terminal');
        progressBar = document.getElementById('progressBar');

        // Start the boot sequence
        startBootSequence();
    }

    /**
     * Main boot sequence orchestrator
     */
    function startBootSequence() {
        // Phase 1: Show loading screen with color bars
        showLoadingScreen();

        // Phase 2: Transition to splash screen
        setTimeout(() => {
            transitionToSplash();
        }, SPLASH_CONFIG.loadingDuration);

        // Phase 3: Transition to terminal
        setTimeout(() => {
            transitionToTerminal();
        }, SPLASH_CONFIG.loadingDuration + SPLASH_CONFIG.splashDuration);
    }

    /**
     * Phase 1: Loading Screen
     */
    function showLoadingScreen() {
        loadingScreen.classList.remove('hidden');

        // Animate the color bars (already handled by CSS)
        console.log('[uDOS] Loading screen active...');
    }

    /**
     * Phase 2: Splash Screen
     */
    function transitionToSplash() {
        // Hide loading screen
        loadingScreen.classList.add('hidden');

        // Show splash screen
        splashScreen.classList.remove('hidden');

        console.log('[uDOS] Splash screen active...');

        // Animate progress bar
        animateProgressBar();

        // Play startup sound if enabled
        playStartupSound();
    }

    /**
     * Animate the progress bar
     */
    function animateProgressBar() {
        let progress = 0;
        const step = 100 / SPLASH_CONFIG.progressSteps;

        const interval = setInterval(() => {
            progress += step;

            if (progress >= 100) {
                progress = 100;
                clearInterval(interval);
            }

            progressBar.style.width = progress + '%';
        }, SPLASH_CONFIG.progressInterval);
    }

    /**
     * Play startup sound (optional)
     */
    function playStartupSound() {
        // Optional: Add authentic C64 startup sound
        // For now, just log
        console.log('[uDOS] *BEEP* Startup sound placeholder');
    }

    /**
     * Phase 3: Terminal
     */
    function transitionToTerminal() {
        // Hide splash screen
        splashScreen.classList.add('hidden');

        // Show terminal
        terminal.classList.remove('hidden');

        console.log('[uDOS] Terminal ready.');

        // Focus on command input
        const commandInput = document.getElementById('commandInput');
        if (commandInput) {
            commandInput.focus();
        }

        // Trigger terminal ready event
        document.dispatchEvent(new CustomEvent('udos:terminal:ready'));
    }

    /**
     * Skip splash sequence (for development)
     */
    function skipSplash() {
        loadingScreen.classList.add('hidden');
        splashScreen.classList.add('hidden');
        terminal.classList.remove('hidden');

        const commandInput = document.getElementById('commandInput');
        if (commandInput) {
            commandInput.focus();
        }

        console.log('[uDOS] Splash sequence skipped');
    }

    // Allow skipping with ESC key during splash
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && !terminal.classList.contains('hidden') === false) {
            skipSplash();
        }
    });

    // Expose skip function globally for development
    window.uDOS = window.uDOS || {};
    window.uDOS.skipSplash = skipSplash;

    // Initialize when DOM is loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();

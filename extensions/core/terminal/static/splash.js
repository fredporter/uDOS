/**
 * uDOS Terminal - Splash Sequence with Color Cycling
 * Version: 1.0.24
 */

(function() {
    'use strict';

    // Configuration
    const SPLASH_CONFIG = {
        colorCycleDuration: 8000,    // Color cycle animation duration
        splashDuration: 5000,         // Total splash screen time
        progressSteps: 25,            // Number of progress increments
        progressInterval: 180,        // Progress update interval (ms)
        systemCheckDelay: 150         // Delay between system checks (ms)
    };

    // System check messages
    const SYSTEM_CHECKS = [
        '✓ INITIALIZING CORE SYSTEMS...',
        '✓ LOADING COMMAND HANDLERS...',
        '✓ MOUNTING FILE SYSTEMS...',
        '✓ CONNECTING TO uDOS CORE...',
        '✓ LOADING PETSCII CHARACTER SET...',
        '✓ INITIALIZING BLOCK GRAPHICS...',
        '✓ LOADING MONOSORT EMOJI SUPPORT...',
        '✓ CONFIGURING SYNTHWAVE PALETTE...',
        '✓ ESTABLISHING TERMINAL SESSION...',
        '✓ SYSTEMS READY'
    };

    // DOM Elements
    let splashScreen;
    let terminalContainer;
    let progressBar;
    let splashStatus;
    let systemChecks;

    /**
     * Initialize splash sequence
     */
    function init() {
        console.log('[uDOS Splash] Init starting...');

        // Get DOM elements
        splashScreen = document.getElementById('splashScreen');
        terminalContainer = document.getElementById('terminalContainer');
        progressBar = document.getElementById('progressBar');
        splashStatus = document.getElementById('splashStatus');
        systemChecks = document.getElementById('systemChecks');

        console.log('[uDOS Splash] Elements found:', {
            splashScreen: !!splashScreen,
            terminalContainer: !!terminalContainer,
            progressBar: !!progressBar,
            splashStatus: !!splashStatus,
            systemChecks: !!systemChecks
        });

        if (!splashScreen || !terminalContainer || !progressBar) {
            console.error('[uDOS Splash] Missing required elements!');
            return;
        }

        // Start the boot sequence
        startBootSequence();
    }

    /**
     * Main boot sequence
     */
    function startBootSequence() {
        console.log('[uDOS Splash] Starting boot sequence...');

        // Start progress bar animation
        animateProgressBar();

        // Start system checks
        setTimeout(() => {
            displaySystemChecks();
        }, 1000);

        // Transition to terminal after splash duration
        setTimeout(() => {
            transitionToTerminal();
        }, SPLASH_CONFIG.splashDuration);
    }

    /**
     * Animate progress bar
     */
    function animateProgressBar() {
        let progress = 0;
        const step = 100 / SPLASH_CONFIG.progressSteps;
        const totalTime = SPLASH_CONFIG.splashDuration - 1000; // Leave time for final check
        const interval = totalTime / SPLASH_CONFIG.progressSteps;

        const progressInterval = setInterval(() => {
            progress += step;

            if (progress >= 100) {
                progress = 100;
                clearInterval(progressInterval);
                splashStatus.textContent = 'SYSTEMS READY - LAUNCHING TERMINAL...';
            }

            progressBar.style.width = progress + '%';
        }, interval);
    }

    /**
     * Display system check messages sequentially
     */
    function displaySystemChecks() {
        let checkIndex = 0;

        function showNextCheck() {
            if (checkIndex < SYSTEM_CHECKS.length) {
                const checkMessage = document.createElement('p');
                checkMessage.textContent = SYSTEM_CHECKS[checkIndex];
                checkMessage.style.opacity = '0';
                checkMessage.style.transition = 'opacity 0.3s ease-in';
                systemChecks.appendChild(checkMessage);

                // Trigger animation
                setTimeout(() => {
                    checkMessage.style.opacity = '1';
                }, 10);

                // Update status
                splashStatus.textContent = SYSTEM_CHECKS[checkIndex];

                checkIndex++;

                // Schedule next check
                setTimeout(showNextCheck, SPLASH_CONFIG.systemCheckDelay);
            }
        }

        showNextCheck();
    }

    /**
     * Transition from splash to terminal
     */
    function transitionToTerminal() {
        console.log('[uDOS Splash] Transitioning to terminal...');

        // Fade out splash screen
        splashScreen.classList.add('fade-out');

        setTimeout(() => {
            splashScreen.classList.add('hidden');
            terminalContainer.classList.remove('hidden');
            terminalContainer.classList.add('fade-in');

            // Dispatch terminal ready event
            const readyEvent = new CustomEvent('udos:terminal:ready', {
                detail: {
                    timestamp: Date.now(),
                    version: '1.0.24'
                }
            });
            document.dispatchEvent(readyEvent);

            console.log('[uDOS Splash] Terminal ready');
        }, 500); // Wait for fade-out animation
    }

    /**
     * Skip splash on keypress or click
     */
    function setupSkipHandlers() {
        const skipSplash = () => {
            if (!splashScreen.classList.contains('hidden')) {
                console.log('[uDOS Splash] Skipping splash screen...');
                transitionToTerminal();
            }
        };

        document.addEventListener('keydown', skipSplash, { once: true });
        splashScreen.addEventListener('click', skipSplash, { once: true });
    }

    // Start when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            init();
            setupSkipHandlers();
        });
    } else {
        init();
        setupSkipHandlers();
    }

})();

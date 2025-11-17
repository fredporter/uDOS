/**
 * uDOS C64 Terminal - Emoji Support
 * Monocolor emoji rendering for C64 aesthetic
 * Version: 1.0.24
 */

(function() {
    'use strict';

    // Monocolor Emoji Set (grid-aligned)
    const EMOJI_SET = {
        // Faces & Emotions
        faces: [
            '😀', '😃', '😄', '😁', '😆', '😅', '🤣', '😂',
            '🙂', '🙃', '😉', '😊', '😇', '🥰', '😍', '🤩',
            '😘', '😗', '😚', '😙', '😋', '😛', '😜', '🤪',
            '😝', '🤑', '🤗', '🤭', '🤫', '🤔', '🤐', '🤨'
        ],

        // Hands & Gestures
        hands: [
            '👍', '👎', '👊', '✊', '🤛', '🤜', '🤞', '✌️',
            '🤟', '🤘', '👌', '🤏', '👈', '👉', '👆', '👇',
            '☝️', '👋', '🤚', '🖐️', '✋', '🖖', '👏', '🙌',
            '👐', '🤲', '🤝', '🙏', '✍️', '💪', '🦾', '🦿'
        ],

        // Hearts & Symbols
        hearts: [
            '❤️', '🧡', '💛', '💚', '💙', '💜', '🖤', '🤍',
            '🤎', '💔', '❤️‍🔥', '❤️‍🩹', '💕', '💞', '💓', '💗',
            '💖', '💘', '💝', '💟', '☮️', '✝️', '☪️', '🕉️',
            '☸️', '✡️', '🔯', '🕎', '☯️', '☦️', '🛐', '⛎'
        ],

        // Stars & Weather
        stars: [
            '⭐', '🌟', '✨', '💫', '🌠', '🌌', '☀️', '🌤️',
            '⛅', '🌥️', '☁️', '🌦️', '🌧️', '⛈️', '🌩️', '🌨️',
            '❄️', '☃️', '⛄', '🌬️', '💨', '🌪️', '🌫️', '🌈',
            '☔', '💧', '💦', '🌊', '⚡', '🔥', '💥', '✳️'
        ],

        // Arrows & Symbols
        arrows: [
            '↑', '↓', '←', '→', '↖️', '↗️', '↘️', '↙️',
            '↔️', '↕️', '🔄', '🔃', '⤴️', '⤵️', '🔀', '🔁',
            '🔂', '▶️', '⏸️', '⏹️', '⏺️', '⏏️', '⏮️', '⏭️',
            '⏪', '⏩', '⏫', '⏬', '◀️', '🔼', '🔽', '➡️'
        ],

        // Tech & Objects
        tech: [
            '💻', '🖥️', '🖨️', '⌨️', '🖱️', '🖲️', '💾', '💿',
            '📀', '📱', '📲', '☎️', '📞', '📟', '📠', '📺',
            '📻', '🎙️', '🎚️', '🎛️', '🧭', '⏱️', '⏲️', '⏰',
            '🔋', '🔌', '💡', '🔦', '🕯️', '🧯', '🛢️', '💸'
        ],

        // Gaming & Fun
        gaming: [
            '🎮', '🕹️', '🎯', '🎲', '🎰', '🎳', '🏀', '⚽',
            '🏈', '⚾', '🥎', '🎾', '🏐', '🏉', '🥏', '🎱',
            '🏓', '🏸', '🏒', '🏑', '🥍', '🏏', '🪀', '🪁',
            '🎣', '🤿', '🥊', '🥋', '⛳', '⛸️', '🎿', '🛷'
        ],

        // Numbers & Math
        numbers: [
            '0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣',
            '8️⃣', '9️⃣', '🔟', '➕', '➖', '✖️', '➗', '🟰',
            '#️⃣', '*️⃣', '⏏️', '▶️', '⏸️', '⏹️', '⏺️', '⏭️',
            '⏮️', '⏩', '⏪', '⏫', '⏬', '◀️', '🔼', '🔽'
        ]
    };

    /**
     * Initialize emoji support
     */
    function init() {
        // Wait for terminal to be ready
        document.addEventListener('udos:terminal:ready', function() {
            populateEmojiGrid();
        });
    }

    /**
     * Populate the emoji grid
     */
    function populateEmojiGrid() {
        const emojiGrid = document.getElementById('emojiGrid');
        if (!emojiGrid) return;

        emojiGrid.innerHTML = '';

        // Create category sections
        Object.keys(EMOJI_SET).forEach(category => {
            const section = document.createElement('div');
            section.className = 'emoji-category';

            const title = document.createElement('h5');
            title.textContent = category.toUpperCase();
            title.style.cssText = 'color: var(--c64-yellow); margin: 0.5em 0; font-size: 12px;';
            section.appendChild(title);

            const grid = document.createElement('div');
            grid.className = 'emoji-grid';
            grid.style.cssText = 'display: grid; grid-template-columns: repeat(8, 1fr); gap: 4px; margin-bottom: 1em;';

            EMOJI_SET[category].forEach(emoji => {
                const item = document.createElement('div');
                item.className = 'emoji-item';
                item.textContent = emoji;
                item.title = `Click to copy: ${emoji}`;

                // Click to copy
                item.addEventListener('click', function() {
                    copyToClipboard(emoji);
                    insertEmojiInTerminal(emoji);
                    showCopyNotification(emoji);
                });

                grid.appendChild(item);
            });

            section.appendChild(grid);
            emojiGrid.appendChild(section);
        });
    }

    /**
     * Insert emoji into terminal input
     */
    function insertEmojiInTerminal(emoji) {
        const commandInput = document.getElementById('commandInput');
        if (commandInput) {
            const cursorPos = commandInput.selectionStart;
            const textBefore = commandInput.value.substring(0, cursorPos);
            const textAfter = commandInput.value.substring(cursorPos);

            commandInput.value = textBefore + emoji + textAfter;
            commandInput.selectionStart = commandInput.selectionEnd = cursorPos + emoji.length;
            commandInput.focus();
        }
    }

    /**
     * Copy to clipboard
     */
    function copyToClipboard(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).catch(err => {
                console.error('Failed to copy:', err);
            });
        } else {
            // Fallback
            const textarea = document.createElement('textarea');
            textarea.value = text;
            textarea.style.position = 'fixed';
            textarea.style.opacity = '0';
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
        }
    }

    /**
     * Show copy notification
     */
    function showCopyNotification(emoji) {
        const status = document.getElementById('status');
        if (status) {
            const originalText = status.textContent;
            status.textContent = `COPIED: ${emoji}`;
            status.style.color = 'var(--c64-yellow)';

            setTimeout(() => {
                status.textContent = originalText;
                status.style.color = '';
            }, 1000);
        }
    }

    /**
     * Get all emoji as flat array
     */
    function getAllEmoji() {
        return Object.values(EMOJI_SET).flat();
    }

    /**
     * Get emoji by category
     */
    function getEmojiByCategory(category) {
        return EMOJI_SET[category] || [];
    }

    /**
     * Search emoji (placeholder for future enhancement)
     */
    function searchEmoji(query) {
        // Future: implement emoji search by name/keyword
        return getAllEmoji();
    }

    // Expose emoji API
    window.uDOS = window.uDOS || {};
    window.uDOS.emoji = {
        set: EMOJI_SET,
        getAll: getAllEmoji,
        getCategory: getEmojiByCategory,
        search: searchEmoji,
        insert: insertEmojiInTerminal
    };

    // Initialize
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();

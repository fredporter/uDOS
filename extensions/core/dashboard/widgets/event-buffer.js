/**
 * Event Buffer
 *
 * Circular buffer for webhook events during WebSocket disconnection.
 * Queues events for replay on reconnection to prevent data loss.
 *
 * Part of v1.2.8: Incremental Updates & Event Buffering (Part 2)
 *
 * @version 1.0.0
 * @author uDOS Development Team
 */

class EventBuffer {
    constructor(config = {}) {
        this.config = {
            maxSize: config.maxSize || 100,  // Maximum events to buffer
            persistToStorage: config.persistToStorage !== false,  // Use localStorage
            storageKey: config.storageKey || 'udos_event_buffer',
            deduplicateWindow: config.deduplicateWindow || 5000,  // 5 seconds
            ...config
        };

        this.buffer = [];
        this.sequenceNumber = 0;
        this.stats = {
            totalBuffered: 0,
            totalDeduplicated: 0,
            totalReplayed: 0,
            bufferOverflows: 0
        };

        // Load persisted buffer from localStorage
        if (this.config.persistToStorage) {
            this.loadFromStorage();
        }
    }

    /**
     * Add event to buffer
     *
     * @param {Object} event - Webhook event data
     * @returns {boolean} True if added, false if deduplicated
     */
    add(event) {
        if (!event) {
            console.warn('Cannot buffer null event');
            return false;
        }

        // Check for duplicate
        if (this.isDuplicate(event)) {
            this.stats.totalDeduplicated++;
            console.log(`Deduplicated event: ${event.id || event.event_id || 'unknown'}`);
            return false;
        }

        // Add metadata
        const bufferedEvent = {
            ...event,
            _buffered: true,
            _bufferTime: Date.now(),
            _sequence: ++this.sequenceNumber
        };

        // Add to buffer
        this.buffer.push(bufferedEvent);
        this.stats.totalBuffered++;

        // Check for overflow
        if (this.buffer.length > this.config.maxSize) {
            const removed = this.buffer.shift();
            this.stats.bufferOverflows++;
            console.warn(`Buffer overflow: removed event ${removed._sequence}`);
        }

        // Persist to storage
        if (this.config.persistToStorage) {
            this.saveToStorage();
        }

        console.log(`Buffered event ${bufferedEvent._sequence} (${this.buffer.length}/${this.config.maxSize})`);
        return true;
    }

    /**
     * Check if event is duplicate (within deduplication window)
     *
     * @param {Object} event - Event to check
     * @returns {boolean} True if duplicate
     */
    isDuplicate(event) {
        const eventId = event.id || event.event_id;
        if (!eventId) return false;

        const now = Date.now();
        const window = this.config.deduplicateWindow;

        return this.buffer.some(bufferedEvent => {
            const id = bufferedEvent.id || bufferedEvent.event_id;
            const age = now - bufferedEvent._bufferTime;

            return id === eventId && age < window;
        });
    }

    /**
     * Get all buffered events
     *
     * @param {boolean} clear - Clear buffer after retrieval (default: true)
     * @returns {Array} Buffered events
     */
    getAll(clear = true) {
        const events = [...this.buffer];

        if (clear) {
            this.clear();
        }

        return events;
    }

    /**
     * Get buffered events since timestamp
     *
     * @param {number} timestamp - Timestamp in milliseconds
     * @returns {Array} Events buffered after timestamp
     */
    getSince(timestamp) {
        return this.buffer.filter(event => event._bufferTime > timestamp);
    }

    /**
     * Peek at buffered events without removing
     *
     * @param {number} count - Number of events to peek (default: all)
     * @returns {Array} Events (most recent first)
     */
    peek(count = null) {
        const events = [...this.buffer].reverse();
        return count ? events.slice(0, count) : events;
    }

    /**
     * Get buffer size
     *
     * @returns {number} Number of buffered events
     */
    size() {
        return this.buffer.length;
    }

    /**
     * Check if buffer is empty
     *
     * @returns {boolean} True if empty
     */
    isEmpty() {
        return this.buffer.length === 0;
    }

    /**
     * Check if buffer is full
     *
     * @returns {boolean} True if at capacity
     */
    isFull() {
        return this.buffer.length >= this.config.maxSize;
    }

    /**
     * Clear all buffered events
     */
    clear() {
        this.buffer = [];

        if (this.config.persistToStorage) {
            this.clearStorage();
        }

        console.log('Event buffer cleared');
    }

    /**
     * Mark events as replayed
     *
     * @param {number} count - Number of events replayed
     */
    markReplayed(count) {
        this.stats.totalReplayed += count;
    }

    /**
     * Get buffer statistics
     *
     * @returns {Object} Statistics
     */
    getStats() {
        return {
            ...this.stats,
            currentSize: this.buffer.length,
            maxSize: this.config.maxSize,
            utilizationPercent: (this.buffer.length / this.config.maxSize) * 100,
            oldestBufferTime: this.buffer.length > 0 ? this.buffer[0]._bufferTime : null,
            newestBufferTime: this.buffer.length > 0 ? this.buffer[this.buffer.length - 1]._bufferTime : null
        };
    }

    /**
     * Save buffer to localStorage
     */
    saveToStorage() {
        if (!this.config.persistToStorage) return;

        try {
            const data = {
                buffer: this.buffer,
                sequenceNumber: this.sequenceNumber,
                stats: this.stats,
                savedAt: Date.now()
            };

            localStorage.setItem(this.config.storageKey, JSON.stringify(data));
        } catch (error) {
            console.error('Failed to save event buffer to storage:', error);
        }
    }

    /**
     * Load buffer from localStorage
     */
    loadFromStorage() {
        if (!this.config.persistToStorage) return;

        try {
            const data = localStorage.getItem(this.config.storageKey);
            if (!data) return;

            const parsed = JSON.parse(data);

            // Check if data is stale (older than 1 hour)
            const age = Date.now() - (parsed.savedAt || 0);
            const maxAge = 60 * 60 * 1000;  // 1 hour

            if (age > maxAge) {
                console.log('Event buffer data stale, clearing');
                this.clearStorage();
                return;
            }

            // Restore data
            this.buffer = parsed.buffer || [];
            this.sequenceNumber = parsed.sequenceNumber || 0;
            this.stats = parsed.stats || this.stats;

            console.log(`Loaded ${this.buffer.length} events from storage`);
        } catch (error) {
            console.error('Failed to load event buffer from storage:', error);
            this.clearStorage();
        }
    }

    /**
     * Clear localStorage
     */
    clearStorage() {
        if (!this.config.persistToStorage) return;

        try {
            localStorage.removeItem(this.config.storageKey);
        } catch (error) {
            console.error('Failed to clear event buffer storage:', error);
        }
    }

    /**
     * Export buffer state for debugging
     *
     * @returns {Object} Buffer state
     */
    exportState() {
        return {
            config: this.config,
            buffer: this.buffer,
            sequenceNumber: this.sequenceNumber,
            stats: this.getStats()
        };
    }

    /**
     * Import buffer state (for testing/recovery)
     *
     * @param {Object} state - State from exportState()
     */
    importState(state) {
        if (!state) return;

        this.buffer = state.buffer || [];
        this.sequenceNumber = state.sequenceNumber || 0;
        this.stats = state.stats || this.stats;

        if (this.config.persistToStorage) {
            this.saveToStorage();
        }

        console.log('Event buffer state imported');
    }

    /**
     * Get age of oldest buffered event
     *
     * @returns {number} Age in milliseconds (0 if empty)
     */
    getOldestEventAge() {
        if (this.buffer.length === 0) return 0;

        const oldest = this.buffer[0];
        return Date.now() - oldest._bufferTime;
    }

    /**
     * Remove old events (beyond retention period)
     *
     * @param {number} maxAge - Maximum age in milliseconds (default: 1 hour)
     * @returns {number} Number of events removed
     */
    removeOldEvents(maxAge = 60 * 60 * 1000) {
        const now = Date.now();
        const originalLength = this.buffer.length;

        this.buffer = this.buffer.filter(event => {
            const age = now - event._bufferTime;
            return age < maxAge;
        });

        const removed = originalLength - this.buffer.length;

        if (removed > 0) {
            console.log(`Removed ${removed} old events from buffer`);

            if (this.config.persistToStorage) {
                this.saveToStorage();
            }
        }

        return removed;
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EventBuffer;
}

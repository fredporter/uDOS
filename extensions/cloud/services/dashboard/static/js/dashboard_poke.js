/**
 * POKE Integration for uDOS Dashboard
 * Provides real-time memory manipulation and monitoring
 */

class DashboardPOKE {
    constructor() {
        this.memoryMap = new Map();
        this.watchList = new Map();
        this.subscriptions = new Set();
        this.setupSocket();
    }

    setupSocket() {
        this.socket = io('/poke');

        this.socket.on('memory_update', (data) => {
            this.handleMemoryUpdate(data);
        });

        this.socket.on('watch_trigger', (data) => {
            this.handleWatchTrigger(data);
        });
    }

    /**
     * Set memory value at specified address
     */
    async poke(address, value) {
        if (!this.isValidAddress(address) || !this.isValidValue(value)) {
            throw new Error('Invalid POKE parameters');
        }

        const response = await this.socket.emit('poke', { address, value });
        this.memoryMap.set(address, value);
        this.notifySubscribers({ type: 'poke', address, value });
        return response;
    }

    /**
     * Read memory value at specified address
     */
    async peek(address) {
        if (!this.isValidAddress(address)) {
            throw new Error('Invalid PEEK address');
        }

        const value = await this.socket.emit('peek', { address });
        return value;
    }

    /**
     * Set up a watch on a memory address
     */
    watchAddress(address, callback, options = {}) {
        const { threshold = 0, interval = 1000 } = options;

        const watch = {
            callback,
            threshold,
            interval,
            lastValue: null,
            timer: setInterval(async () => {
                const value = await this.peek(address);
                if (this.shouldTriggerWatch(watch.lastValue, value, threshold)) {
                    callback({ address, value, previous: watch.lastValue });
                }
                watch.lastValue = value;
            }, interval)
        };

        this.watchList.set(address, watch);
        return () => this.clearWatch(address); // Return cleanup function
    }

    /**
     * Clear a watch on a memory address
     */
    clearWatch(address) {
        const watch = this.watchList.get(address);
        if (watch) {
            clearInterval(watch.timer);
            this.watchList.delete(address);
        }
    }

    /**
     * Subscribe to memory updates
     */
    subscribe(callback) {
        this.subscriptions.add(callback);
        return () => this.subscriptions.delete(callback);
    }

    /**
     * Handle memory updates from server
     */
    handleMemoryUpdate(data) {
        const { address, value } = data;
        this.memoryMap.set(address, value);
        this.notifySubscribers({ type: 'update', address, value });
    }

    /**
     * Handle watch triggers from server
     */
    handleWatchTrigger(data) {
        const watch = this.watchList.get(data.address);
        if (watch) {
            watch.callback(data);
        }
    }

    /**
     * Notify all subscribers of changes
     */
    notifySubscribers(data) {
        this.subscriptions.forEach(callback => callback(data));
    }

    /**
     * Validate memory address
     */
    isValidAddress(address) {
        return Number.isInteger(address) && address >= 0 && address <= 65535;
    }

    /**
     * Validate memory value
     */
    isValidValue(value) {
        return Number.isInteger(value) && value >= 0 && value <= 255;
    }

    /**
     * Check if watch should trigger based on threshold
     */
    shouldTriggerWatch(oldValue, newValue, threshold) {
        if (oldValue === null) return true;
        return Math.abs(newValue - oldValue) >= threshold;
    }

    /**
     * Get current memory map snapshot
     */
    getMemoryMap() {
        return Object.fromEntries(this.memoryMap);
    }

    /**
     * Clear all watches
     */
    clearAllWatches() {
        this.watchList.forEach((watch, address) => this.clearWatch(address));
    }

    /**
     * Format memory value for display
     */
    static formatValue(value) {
        return `$${value.toString(16).toUpperCase().padStart(2, '0')}`;
    }

    /**
     * Format address for display
     */
    static formatAddress(address) {
        return `$${address.toString(16).toUpperCase().padStart(4, '0')}`;
    }
}

/**
 * uDOS Terminal - Command Integration
 * Handles communication with uDOS core command system
 * Version: 1.0.24
 */

(function() {
    'use strict';

    /**
     * Command API client for uDOS core
     */
    class CommandAPI {
        constructor(baseUrl = 'http://localhost:5001') {
            this.baseUrl = baseUrl;
            this.sessionId = null;
        }

        /**
         * Initialize session
         */
        async init() {
            this.sessionId = 'web-term-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
            console.log('[CommandAPI] Session initialized:', this.sessionId);
            return this.sessionId;
        }

        /**
         * Execute command on uDOS core
         */
        async execute(command) {
            try {
                const response = await fetch(`${this.baseUrl}/api/command`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Session-ID': this.sessionId
                    },
                    body: JSON.stringify({
                        command: command,
                        session: this.sessionId,
                        timestamp: Date.now()
                    })
                });

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                return await response.json();
            } catch (error) {
                console.error('[CommandAPI] Execute failed:', error);
                throw error;
            }
        }

        /**
         * Get system status
         */
        async getStatus() {
            try {
                const response = await fetch(`${this.baseUrl}/api/status`);
                if (response.ok) {
                    return await response.json();
                }
                return null;
            } catch (error) {
                console.error('[CommandAPI] Status check failed:', error);
                return null;
            }
        }

        /**
         * Stream command output (for long-running commands)
         */
        async *streamOutput(command) {
            try {
                const response = await fetch(`${this.baseUrl}/api/command/stream`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Session-ID': this.sessionId
                    },
                    body: JSON.stringify({
                        command: command,
                        session: this.sessionId
                    })
                });

                const reader = response.body.getReader();
                const decoder = new TextDecoder();

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    const chunk = decoder.decode(value);
                    const lines = chunk.split('\n');

                    for (const line of lines) {
                        if (line.trim()) {
                            try {
                                yield JSON.parse(line);
                            } catch (e) {
                                yield { type: 'text', content: line };
                            }
                        }
                    }
                }
            } catch (error) {
                console.error('[CommandAPI] Stream failed:', error);
                throw error;
            }
        }
    }

    /**
     * Local command handlers for standalone mode
     */
    const LocalCommands = {
        /**
         * File system commands
         */
        async LIST(args) {
            return {
                output: [
                    'DIRECTORY LISTING:',
                    '',
                    '  knowledge/     - Knowledge base',
                    '  memory/        - Memory workspace',
                    '  data/          - Data files',
                    '',
                    'Connect to uDOS Core for full file system'
                ],
                success: true
            };
        },

        async TREE(args) {
            return {
                output: [
                    'DIRECTORY TREE:',
                    '',
                    '├── knowledge/',
                    '│   ├── system/',
                    '│   ├── reference/',
                    '│   └── guides/',
                    '├── memory/',
                    '│   ├── workspace/',
                    '│   └── logs/',
                    '└── data/',
                    '',
                    'Use with uDOS Core for full tree'
                ],
                success: true
            };
        },

        /**
         * System commands
         */
        async STATUS(args) {
            const status = {
                version: '1.0.24',
                mode: 'standalone',
                uptime: Math.floor(performance.now() / 1000),
                memory: performance.memory ? {
                    used: Math.floor(performance.memory.usedJSHeapSize / 1024 / 1024),
                    total: Math.floor(performance.memory.totalJSHeapSize / 1024 / 1024)
                } : null
            };

            const lines = [
                'uDOS SYSTEM STATUS:',
                '',
                `  Version:    ${status.version}`,
                `  Mode:       ${status.mode}`,
                `  Uptime:     ${status.uptime}s`
            ];

            if (status.memory) {
                lines.push(`  Memory:     ${status.memory.used}MB / ${status.memory.total}MB`);
            }

            return { output: lines, success: true };
        },

        async TIME(args) {
            const now = new Date();
            return {
                output: [
                    'SYSTEM TIME:',
                    '',
                    `  Date: ${now.toLocaleDateString()}`,
                    `  Time: ${now.toLocaleTimeString()}`,
                    `  Timestamp: ${now.getTime()}`
                ],
                success: true
            };
        },

        /**
         * Help command
         */
        async HELP(args) {
            return {
                output: [
                    '╔════════════════════════════════════════════════════════════════════╗',
                    '║                    uDOS TERMINAL COMMANDS                          ║',
                    '╠════════════════════════════════════════════════════════════════════╣',
                    '║ SYSTEM                                                             ║',
                    '║   HELP      - Show this help                                       ║',
                    '║   STATUS    - System status                                        ║',
                    '║   VERSION   - Show version                                         ║',
                    '║   TIME      - Show system time                                     ║',
                    '║   CLEAR     - Clear screen                                         ║',
                    '║                                                                    ║',
                    '║ FILES                                                              ║',
                    '║   LIST      - List directory                                       ║',
                    '║   TREE      - Directory tree                                       ║',
                    '║   EDIT      - Edit file                                            ║',
                    '║   RUN       - Run script                                           ║',
                    '║                                                                    ║',
                    '║ KNOWLEDGE                                                          ║',
                    '║   KNOWLEDGE - Knowledge base commands                              ║',
                    '║   GUIDE     - Terminal guide                                       ║',
                    '║                                                                    ║',
                    '║ FUNCTION KEYS                                                      ║',
                    '║   F1 - Help    F2 - Knowledge  F3 - List    F4 - Edit            ║',
                    '║   F5 - Run     F6 - Status     F7 - Clear   F8 - Characters      ║',
                    '╚════════════════════════════════════════════════════════════════════╝'
                ],
                success: true
            };
        }
    };

    // Export to global scope
    window.uDOS = window.uDOS || {};
    window.uDOS.CommandAPI = CommandAPI;
    window.uDOS.LocalCommands = LocalCommands;

})();

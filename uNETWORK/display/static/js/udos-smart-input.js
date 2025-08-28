/*
 * uDOS Smart Input System
 * Advanced command processing, autocomplete, and intelligent suggestions
 * Universal Device Operating System v1.0.4.1
 */

class UDOSSmartInput {
    constructor() {
        this.commandRegistry = new Map();
        this.variableRegistry = new Map();
        this.templateRegistry = new Map();
        this.suggestionCache = new Map();
        this.inputHistory = [];
        this.currentContext = 'global';
        this.isLearningMode = true;
        this.userPatterns = new Map();

        this.init();
    }

    init() {
        console.log('🧠 Initializing uDOS Smart Input System...');

        this.initializeCommandRegistry();
        this.initializeVariableRegistry();
        this.initializeTemplateRegistry();
        this.loadUserPatterns();
        this.setupInputProcessing();
    }

    initializeCommandRegistry() {
        // uCODE command definitions
        const commands = [
            // System Commands
            {
                command: 'STATUS',
                syntax: '[STATUS]',
                description: 'Show system status',
                context: 'system',
                parameters: [],
                examples: ['[STATUS]', '[STATUS] <DETAILED>']
            },
            {
                command: 'HELP',
                syntax: '[HELP] [command]',
                description: 'Show help information',
                context: 'system',
                parameters: ['command?'],
                examples: ['[HELP]', '[HELP] STATUS', '[HELP] WORKFLOW']
            },
            {
                command: 'BACKUP',
                syntax: '[BACKUP] <type> {options}',
                description: 'Create backup',
                context: 'system',
                parameters: ['type', 'options?'],
                examples: ['[BACKUP] <FULL>', '[BACKUP] <INCREMENTAL> {COMPRESSED}']
            },

            // Data Commands
            {
                command: 'GET',
                syntax: '[GET] {variable}',
                description: 'Get variable value',
                context: 'data',
                parameters: ['variable'],
                examples: ['[GET] {USER-NAME}', '[GET] {SYSTEM-STATUS}']
            },
            {
                command: 'SET',
                syntax: '[SET] {variable} = {value}',
                description: 'Set variable value',
                context: 'data',
                parameters: ['variable', 'value'],
                examples: ['[SET] {USER-NAME} = {John}', '[SET] {THEME} = {polaroid}']
            },
            {
                command: 'DATA',
                syntax: '[DATA] <operation> {parameters}',
                description: 'Data operations',
                context: 'data',
                parameters: ['operation', 'parameters?'],
                examples: ['[DATA] <SAVE> {key} {value}', '[DATA] <LOAD> {key}']
            },

            // Workflow Commands
            {
                command: 'WORKFLOW',
                syntax: '[WORKFLOW] <action> {parameters}',
                description: 'Workflow management',
                context: 'workflow',
                parameters: ['action', 'parameters?'],
                examples: ['[WORKFLOW] <STATUS>', '[WORKFLOW] <CREATE> {project}']
            },
            {
                command: 'GRID',
                syntax: '[GRID] <display> {size}',
                description: 'Grid display operations',
                context: 'display',
                parameters: ['display', 'size?'],
                examples: ['[GRID] <DISPLAY> {medium}', '[GRID] <GENERATE> {large}']
            },
            {
                command: 'MAP',
                syntax: '[MAP] <operation> {region}',
                description: 'Map operations',
                context: 'display',
                parameters: ['operation', 'region?'],
                examples: ['[MAP] <LOAD> {global}', '[MAP] <TILES> {local}']
            },

            // Template Commands
            {
                command: 'TEMPLATE',
                syntax: '[TEMPLATE] <action> {name}',
                description: 'Template operations',
                context: 'template',
                parameters: ['action', 'name'],
                examples: ['[TEMPLATE] <LOAD> {user-profile}', '[TEMPLATE] <SAVE> {my-template}']
            },
            {
                command: 'EXPORT',
                syntax: '[EXPORT] <format> {options}',
                description: 'Export data',
                context: 'data',
                parameters: ['format', 'options?'],
                examples: ['[EXPORT] <JSON> {compressed}', '[EXPORT] <CSV> {headers}']
            }
        ];

        commands.forEach(cmd => {
            this.commandRegistry.set(cmd.command, cmd);
        });

        console.log(`📝 Loaded ${commands.length} command definitions`);
    }

    initializeVariableRegistry() {
        // System variables
        const variables = [
            { name: 'USER-NAME', type: 'string', context: 'user', description: 'Current user name' },
            { name: 'USER-ROLE', type: 'string', context: 'user', description: 'Current user role' },
            { name: 'SYSTEM-STATUS', type: 'string', context: 'system', description: 'System status' },
            { name: 'CURRENT-THEME', type: 'string', context: 'display', description: 'Active theme' },
            { name: 'GRID-SIZE', type: 'string', context: 'display', description: 'Grid display size' },
            { name: 'MEMORY-USAGE', type: 'number', context: 'system', description: 'Memory usage percentage' },
            { name: 'CPU-USAGE', type: 'number', context: 'system', description: 'CPU usage percentage' },
            { name: 'STORAGE-USAGE', type: 'number', context: 'system', description: 'Storage usage percentage' },
            { name: 'TIME-LOCAL', type: 'datetime', context: 'system', description: 'Local time' },
            { name: 'DATE-LOCAL', type: 'date', context: 'system', description: 'Local date' },
            { name: 'WORKFLOW-CURRENT', type: 'string', context: 'workflow', description: 'Current workflow' },
            { name: 'MAP-REGION', type: 'string', context: 'display', description: 'Active map region' },
            { name: 'CONNECTION-STATUS', type: 'boolean', context: 'network', description: 'Server connection status' }
        ];

        variables.forEach(variable => {
            this.variableRegistry.set(variable.name, variable);
        });

        console.log(`🔢 Loaded ${variables.length} variable definitions`);
    }

    initializeTemplateRegistry() {
        // Template definitions
        const templates = [
            {
                name: 'user-profile',
                description: 'User profile template',
                content: '[GET] {USER-NAME}\n[GET] {USER-ROLE}\n[STATUS]',
                variables: ['USER-NAME', 'USER-ROLE'],
                category: 'user'
            },
            {
                name: 'system-check',
                description: 'System health check template',
                content: '[STATUS]\n[GET] {MEMORY-USAGE}\n[GET] {CPU-USAGE}\n[GET] {STORAGE-USAGE}',
                variables: ['MEMORY-USAGE', 'CPU-USAGE', 'STORAGE-USAGE'],
                category: 'system'
            },
            {
                name: 'backup-routine',
                description: 'Complete backup routine',
                content: '[BACKUP] <FULL> {COMPRESSED}\n[WORKFLOW] <LOG> {backup-completed}',
                variables: [],
                category: 'maintenance'
            },
            {
                name: 'grid-setup',
                description: 'Grid display setup',
                content: '[GRID] <DISPLAY> {medium}\n[SET] {GRID-SIZE} = {medium}',
                variables: ['GRID-SIZE'],
                category: 'display'
            }
        ];

        templates.forEach(template => {
            this.templateRegistry.set(template.name, template);
        });

        console.log(`📋 Loaded ${templates.length} template definitions`);
    }

    setupInputProcessing() {
        // Enhance existing command input with smart features
        const commandInput = document.getElementById('commandInput');
        if (commandInput) {
            // Store original input handler
            this.originalInputHandler = commandInput.oninput;

            // Add smart input processing
            commandInput.addEventListener('input', (e) => {
                this.processSmartInput(e.target.value);
            });

            commandInput.addEventListener('keydown', (e) => {
                this.handleSmartKeydown(e);
            });
        }

        // Terminal input enhancement
        const terminalInput = document.getElementById('terminalInputField');
        if (terminalInput) {
            terminalInput.addEventListener('input', (e) => {
                this.processTerminalInput(e.target.value);
            });
        }
    }

    processSmartInput(input) {
        if (!input.trim()) {
            this.hideSuggestions();
            return;
        }

        // Analyze input structure
        const analysis = this.analyzeInput(input);

        // Generate context-aware suggestions
        const suggestions = this.generateSuggestions(input, analysis);

        // Show suggestions
        this.showSuggestions(suggestions);

        // Learn from user patterns
        if (this.isLearningMode) {
            this.learnUserPattern(input, analysis);
        }
    }

    analyzeInput(input) {
        const analysis = {
            type: 'unknown',
            command: null,
            variables: [],
            parameters: [],
            syntax: null,
            isComplete: false,
            errors: []
        };

        // Detect uCODE syntax patterns
        const ucodePatterns = {
            command: /\[([A-Z]+)\]/g,
            variable: /\{([A-Z0-9-]+)\}/g,
            parameter: /<([a-z-]+)>/g,
            action: /<([A-Z-]+)>/g
        };

        // Find command
        const commandMatch = input.match(ucodePatterns.command);
        if (commandMatch) {
            const commandName = commandMatch[0].replace(/[\[\]]/g, '');
            analysis.command = commandName;
            analysis.type = 'ucode';

            const commandDef = this.commandRegistry.get(commandName);
            if (commandDef) {
                analysis.syntax = commandDef.syntax;
                analysis.context = commandDef.context;
            } else {
                analysis.errors.push(`Unknown command: ${commandName}`);
            }
        }

        // Find variables
        const variableMatches = input.match(ucodePatterns.variable);
        if (variableMatches) {
            analysis.variables = variableMatches.map(v => v.replace(/[\{\}]/g, ''));
        }

        // Find parameters
        const parameterMatches = input.match(ucodePatterns.parameter);
        if (parameterMatches) {
            analysis.parameters = parameterMatches.map(p => p.replace(/[<>]/g, ''));
        }

        // Check if input looks like plain shell command
        if (!commandMatch && !input.startsWith('[')) {
            analysis.type = 'shell';
        }

        // Validate syntax
        if (analysis.command && analysis.syntax) {
            analysis.isComplete = this.validateSyntax(input, analysis.syntax);
        }

        return analysis;
    }

    validateSyntax(input, expectedSyntax) {
        // Simple syntax validation
        // More sophisticated validation could be implemented
        const requiredBrackets = (expectedSyntax.match(/\[/g) || []).length;
        const inputBrackets = (input.match(/\[/g) || []).length;

        return inputBrackets >= requiredBrackets;
    }

    generateSuggestions(input, analysis) {
        const suggestions = [];

        // Command suggestions
        if (analysis.type === 'unknown' || input.startsWith('[')) {
            const commandSuggestions = this.getCommandSuggestions(input);
            suggestions.push(...commandSuggestions);
        }

        // Variable suggestions
        if (input.includes('{')) {
            const variableSuggestions = this.getVariableSuggestions(input, analysis);
            suggestions.push(...variableSuggestions);
        }

        // Parameter suggestions
        if (analysis.command) {
            const parameterSuggestions = this.getParameterSuggestions(input, analysis);
            suggestions.push(...parameterSuggestions);
        }

        // Template suggestions
        if (input.startsWith('template') || input.includes('TEMPLATE')) {
            const templateSuggestions = this.getTemplateSuggestions(input);
            suggestions.push(...templateSuggestions);
        }

        // Context-aware suggestions
        const contextSuggestions = this.getContextSuggestions(input, analysis);
        suggestions.push(...contextSuggestions);

        // User pattern suggestions
        const patternSuggestions = this.getUserPatternSuggestions(input);
        suggestions.push(...patternSuggestions);

        // Remove duplicates and sort by relevance
        return this.rankSuggestions(suggestions, input);
    }

    getCommandSuggestions(input) {
        const partial = input.replace('[', '').toUpperCase();
        const suggestions = [];

        this.commandRegistry.forEach((cmd, name) => {
            if (name.startsWith(partial)) {
                suggestions.push({
                    type: 'command',
                    text: `[${name}]`,
                    description: cmd.description,
                    syntax: cmd.syntax,
                    score: 10 - (name.length - partial.length) // Prefer shorter matches
                });
            }
        });

        return suggestions;
    }

    getVariableSuggestions(input, analysis) {
        const suggestions = [];
        const variableContext = analysis.context || 'global';

        // Find partial variable name
        const openBrace = input.lastIndexOf('{');
        if (openBrace !== -1) {
            const partial = input.substring(openBrace + 1).toUpperCase();

            this.variableRegistry.forEach((variable, name) => {
                if (name.startsWith(partial) &&
                    (variable.context === variableContext || variable.context === 'global')) {
                    suggestions.push({
                        type: 'variable',
                        text: `{${name}}`,
                        description: variable.description,
                        dataType: variable.type,
                        score: 8 - (name.length - partial.length)
                    });
                }
            });
        }

        return suggestions;
    }

    getParameterSuggestions(input, analysis) {
        const suggestions = [];
        const commandDef = this.commandRegistry.get(analysis.command);

        if (commandDef && commandDef.parameters) {
            commandDef.parameters.forEach(param => {
                if (!input.includes(`<${param}>`)) {
                    suggestions.push({
                        type: 'parameter',
                        text: `<${param}>`,
                        description: `Parameter: ${param}`,
                        score: 6
                    });
                }
            });
        }

        return suggestions;
    }

    getTemplateSuggestions(input) {
        const suggestions = [];

        this.templateRegistry.forEach((template, name) => {
            if (name.toLowerCase().includes(input.toLowerCase()) ||
                template.description.toLowerCase().includes(input.toLowerCase())) {
                suggestions.push({
                    type: 'template',
                    text: `[TEMPLATE] <LOAD> {${name}}`,
                    description: template.description,
                    category: template.category,
                    score: 7
                });
            }
        });

        return suggestions;
    }

    getContextSuggestions(input, analysis) {
        const suggestions = [];

        // Context-specific suggestions based on current tab or mode
        if (window.udosApp) {
            const currentTab = window.udosApp.getCurrentTab();

            switch (currentTab) {
                case 'grid':
                    suggestions.push({
                        type: 'context',
                        text: '[GRID] <DISPLAY> {medium}',
                        description: 'Display grid view',
                        score: 5
                    });
                    break;

                case 'map':
                    suggestions.push({
                        type: 'context',
                        text: '[MAP] <LOAD> {local}',
                        description: 'Load map tiles',
                        score: 5
                    });
                    break;

                case 'memory':
                    suggestions.push({
                        type: 'context',
                        text: '[GET] {MEMORY-USAGE}',
                        description: 'Check memory usage',
                        score: 5
                    });
                    break;
            }
        }

        return suggestions;
    }

    getUserPatternSuggestions(input) {
        const suggestions = [];

        // Analyze user patterns for intelligent suggestions
        this.userPatterns.forEach((pattern, key) => {
            if (pattern.frequency > 3 && input.toLowerCase().includes(key.toLowerCase())) {
                suggestions.push({
                    type: 'pattern',
                    text: pattern.command,
                    description: `Frequently used: ${pattern.command}`,
                    frequency: pattern.frequency,
                    score: Math.min(pattern.frequency, 10)
                });
            }
        });

        return suggestions;
    }

    rankSuggestions(suggestions, input) {
        // Sort by score (descending) and relevance
        return suggestions
            .sort((a, b) => b.score - a.score)
            .slice(0, 10); // Limit to top 10 suggestions
    }

    showSuggestions(suggestions) {
        const container = document.getElementById('commandSuggestions');
        if (!container || suggestions.length === 0) {
            this.hideSuggestions();
            return;
        }

        container.innerHTML = '';

        suggestions.forEach((suggestion, index) => {
            const item = document.createElement('div');
            item.className = 'suggestion-item';
            item.dataset.index = index;

            const typeIcon = this.getSuggestionIcon(suggestion.type);

            item.innerHTML = `
                <div class="suggestion-content">
                    <span class="suggestion-icon">${typeIcon}</span>
                    <span class="suggestion-text">${suggestion.text}</span>
                    <span class="suggestion-desc">${suggestion.description}</span>
                </div>
                ${suggestion.syntax ? `<div class="suggestion-syntax">${suggestion.syntax}</div>` : ''}
            `;

            item.addEventListener('click', () => {
                this.applySuggestion(suggestion);
            });

            container.appendChild(item);
        });

        container.style.display = 'block';
    }

    getSuggestionIcon(type) {
        const icons = {
            command: '⚡',
            variable: '🔢',
            parameter: '📝',
            template: '📋',
            context: '🎯',
            pattern: '🔄'
        };
        return icons[type] || '💡';
    }

    hideSuggestions() {
        const container = document.getElementById('commandSuggestions');
        if (container) {
            container.style.display = 'none';
        }
    }

    applySuggestion(suggestion) {
        const input = document.getElementById('commandInput');
        const terminalInput = document.getElementById('terminalInputField');

        const targetInput = input && input === document.activeElement ? input : terminalInput;

        if (targetInput) {
            // Smart insertion based on suggestion type
            let newValue;

            if (suggestion.type === 'command') {
                newValue = suggestion.text + ' ';
            } else if (suggestion.type === 'variable') {
                // Replace partial variable
                const openBrace = targetInput.value.lastIndexOf('{');
                if (openBrace !== -1) {
                    newValue = targetInput.value.substring(0, openBrace) + suggestion.text + ' ';
                } else {
                    newValue = targetInput.value + suggestion.text + ' ';
                }
            } else {
                newValue = suggestion.text;
            }

            targetInput.value = newValue;
            targetInput.focus();

            // Position cursor at end
            targetInput.setSelectionRange(newValue.length, newValue.length);
        }

        this.hideSuggestions();

        // Track usage for learning
        this.trackSuggestionUsage(suggestion);
    }

    handleSmartKeydown(event) {
        const container = document.getElementById('commandSuggestions');
        if (!container || container.style.display === 'none') return;

        const items = container.querySelectorAll('.suggestion-item');
        let selectedIndex = -1;

        // Find currently selected item
        items.forEach((item, index) => {
            if (item.classList.contains('selected')) {
                selectedIndex = index;
            }
        });

        switch (event.key) {
            case 'ArrowDown':
                event.preventDefault();
                selectedIndex = Math.min(selectedIndex + 1, items.length - 1);
                this.updateSuggestionSelection(items, selectedIndex);
                break;

            case 'ArrowUp':
                event.preventDefault();
                selectedIndex = Math.max(selectedIndex - 1, 0);
                this.updateSuggestionSelection(items, selectedIndex);
                break;

            case 'Tab':
            case 'Enter':
                if (selectedIndex >= 0) {
                    event.preventDefault();
                    items[selectedIndex].click();
                }
                break;

            case 'Escape':
                event.preventDefault();
                this.hideSuggestions();
                break;
        }
    }

    updateSuggestionSelection(items, selectedIndex) {
        items.forEach((item, index) => {
            item.classList.toggle('selected', index === selectedIndex);
        });
    }

    processTerminalInput(input) {
        // Enhanced terminal input processing
        if (input.startsWith('[') || input.includes('{')) {
            // uCODE command - use smart processing
            this.processSmartInput(input);
        } else {
            // Regular shell command - provide shell-specific suggestions
            this.processShellInput(input);
        }
    }

    processShellInput(input) {
        // Shell command suggestions
        const shellCommands = [
            'ls', 'cd', 'pwd', 'cat', 'grep', 'find', 'ps', 'top', 'df', 'du',
            'chmod', 'chown', 'cp', 'mv', 'rm', 'mkdir', 'rmdir', 'tar', 'zip',
            'help', 'man', 'history', 'clear', 'exit', 'status', 'backup'
        ];

        const words = input.split(' ');
        const currentWord = words[words.length - 1];

        if (words.length === 1) {
            // Command completion
            const matches = shellCommands.filter(cmd =>
                cmd.startsWith(currentWord.toLowerCase())
            );

            if (matches.length > 0) {
                const suggestions = matches.map(cmd => ({
                    type: 'shell',
                    text: cmd,
                    description: `Shell command: ${cmd}`,
                    score: 5
                }));
                this.showSuggestions(suggestions);
            }
        }
    }

    learnUserPattern(input, analysis) {
        if (analysis.command) {
            const key = analysis.command;
            const pattern = this.userPatterns.get(key) || {
                command: input,
                frequency: 0,
                lastUsed: Date.now()
            };

            pattern.frequency++;
            pattern.lastUsed = Date.now();

            this.userPatterns.set(key, pattern);
        }
    }

    trackSuggestionUsage(suggestion) {
        // Track which suggestions are most useful
        const usage = JSON.parse(localStorage.getItem('udos-suggestion-usage') || '{}');
        const key = `${suggestion.type}:${suggestion.text}`;

        usage[key] = (usage[key] || 0) + 1;
        localStorage.setItem('udos-suggestion-usage', JSON.stringify(usage));
    }

    loadUserPatterns() {
        const saved = localStorage.getItem('udos-user-patterns');
        if (saved) {
            try {
                const patterns = JSON.parse(saved);
                Object.entries(patterns).forEach(([key, pattern]) => {
                    this.userPatterns.set(key, pattern);
                });
                console.log(`🧠 Loaded ${this.userPatterns.size} user patterns`);
            } catch (error) {
                console.warn('Error loading user patterns:', error);
            }
        }
    }

    saveUserPatterns() {
        const patterns = Object.fromEntries(this.userPatterns);
        localStorage.setItem('udos-user-patterns', JSON.stringify(patterns));
    }

    // Public API methods
    addCustomCommand(command, definition) {
        this.commandRegistry.set(command, definition);
        console.log(`➕ Added custom command: ${command}`);
    }

    addCustomVariable(name, definition) {
        this.variableRegistry.set(name, definition);
        console.log(`➕ Added custom variable: ${name}`);
    }

    addCustomTemplate(name, template) {
        this.templateRegistry.set(name, template);
        console.log(`➕ Added custom template: ${name}`);
    }

    expandTemplate(templateName) {
        const template = this.templateRegistry.get(templateName);
        if (template) {
            return template.content;
        }
        return null;
    }

    validateCommand(input) {
        const analysis = this.analyzeInput(input);
        return {
            isValid: analysis.errors.length === 0,
            errors: analysis.errors,
            analysis: analysis
        };
    }

    getCommandHelp(commandName) {
        const command = this.commandRegistry.get(commandName.toUpperCase());
        if (command) {
            return {
                syntax: command.syntax,
                description: command.description,
                examples: command.examples || [],
                parameters: command.parameters || []
            };
        }
        return null;
    }

    setLearningMode(enabled) {
        this.isLearningMode = enabled;
        console.log(`🧠 Learning mode: ${enabled ? 'enabled' : 'disabled'}`);
    }

    // Cleanup
    destroy() {
        this.saveUserPatterns();
        console.log('🧠 Smart Input System destroyed');
    }
}

// Export for external use
window.UDOSSmartInput = UDOSSmartInput;

// Auto-save patterns periodically
setInterval(() => {
    if (window.udosSmartInput) {
        window.udosSmartInput.saveUserPatterns();
    }
}, 300000); // Save every 5 minutes

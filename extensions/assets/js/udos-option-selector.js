/**
 * uDOS Option Selector v1.0.19
 * Arrow-key navigable option selector for Teletext GUI
 * Similar to file picker but for command options
 */

class uDOSOptionSelector {
    constructor() {
        this.selectedIndex = 0;
        this.selectedItems = new Set();
        this.options = [];
        this.descriptions = [];
        this.allowMulti = false;
        this.onSelect = null;
        this.onCancel = null;

        // DOM elements
        this.overlay = null;
        this.container = null;
        this.listElement = null;

        // Keyboard handler
        this.keyHandler = this.handleKeyPress.bind(this);
    }

    /**
     * Show option selector
     * @param {Object} config - Configuration object
     * @param {string} config.prompt - Question/instruction
     * @param {Array<string>} config.options - List of options
     * @param {Array<string>} config.descriptions - Optional descriptions
     * @param {string} config.default - Default option
     * @param {boolean} config.allowMulti - Allow multiple selections
     * @param {string} config.category - Category label
     * @param {Function} config.onSelect - Callback on selection
     * @param {Function} config.onCancel - Callback on cancel
     */
    show(config) {
        this.options = config.options || [];
        this.descriptions = config.descriptions || [];
        this.allowMulti = config.allowMulti || false;
        this.onSelect = config.onSelect || null;
        this.onCancel = config.onCancel || null;

        if (this.options.length === 0) {
            console.warn('No options provided to selector');
            return;
        }

        // Set default selection
        this.selectedIndex = 0;
        if (config.default) {
            const defaultIndex = this.options.indexOf(config.default);
            if (defaultIndex !== -1) {
                this.selectedIndex = defaultIndex;
            }
        }

        // Clear previous selections
        this.selectedItems.clear();
        if (config.default && this.allowMulti) {
            this.selectedItems.add(config.default);
        }

        // Build UI
        this.buildUI(config.prompt, config.category);

        // Attach keyboard listener
        document.addEventListener('keydown', this.keyHandler);

        // Show overlay
        this.overlay.style.display = 'block';

        // Render initial state
        this.render();
    }

    /**
     * Build selector UI
     */
    buildUI(prompt, category) {
        // Create overlay
        this.overlay = document.createElement('div');
        this.overlay.className = 'udos-selector-overlay';
        this.overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            display: none;
            z-index: 10000;
            backdrop-filter: blur(4px);
        `;

        // Create container
        this.container = document.createElement('div');
        this.container.className = 'udos-selector-container';
        this.container.style.cssText = `
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: #1a1a2e;
            border: 2px solid #00ff88;
            border-radius: 8px;
            padding: 20px;
            min-width: 600px;
            max-width: 80%;
            max-height: 80%;
            overflow: hidden;
            box-shadow: 0 0 30px rgba(0, 255, 136, 0.3);
            font-family: 'Courier New', monospace;
        `;

        // Header
        const header = document.createElement('div');
        header.className = 'udos-selector-header';
        header.style.cssText = `
            margin-bottom: 15px;
            border-bottom: 1px solid #00ff88;
            padding-bottom: 10px;
        `;

        if (category) {
            const categoryLabel = document.createElement('div');
            categoryLabel.textContent = category.toUpperCase();
            categoryLabel.style.cssText = `
                color: #00ff88;
                font-size: 14px;
                font-weight: bold;
                margin-bottom: 5px;
            `;
            header.appendChild(categoryLabel);
        }

        const promptLabel = document.createElement('div');
        promptLabel.textContent = prompt;
        promptLabel.style.cssText = `
            color: #ffffff;
            font-size: 16px;
        `;
        header.appendChild(promptLabel);

        // Options list
        this.listElement = document.createElement('div');
        this.listElement.className = 'udos-selector-list';
        this.listElement.style.cssText = `
            max-height: 400px;
            overflow-y: auto;
            margin-bottom: 15px;
        `;

        // Footer with instructions
        const footer = document.createElement('div');
        footer.className = 'udos-selector-footer';
        footer.style.cssText = `
            border-top: 1px solid #00ff88;
            padding-top: 10px;
            color: #00ff88;
            font-size: 12px;
        `;

        const instructions = this.allowMulti
            ? '↑/↓: Navigate  SPACE: Toggle  ENTER: Confirm  ESC: Cancel'
            : '↑/↓: Navigate  ENTER: Select  ESC: Cancel';

        footer.textContent = instructions;

        // Assemble
        this.container.appendChild(header);
        this.container.appendChild(this.listElement);
        this.container.appendChild(footer);
        this.overlay.appendChild(this.container);
        document.body.appendChild(this.overlay);

        // Click outside to cancel
        this.overlay.addEventListener('click', (e) => {
            if (e.target === this.overlay) {
                this.cancel();
            }
        });
    }

    /**
     * Render option list
     */
    render() {
        this.listElement.innerHTML = '';

        this.options.forEach((option, index) => {
            const item = document.createElement('div');
            item.className = 'udos-selector-item';

            const isSelected = index === this.selectedIndex;
            const isChecked = this.selectedItems.has(option);

            // Styling
            item.style.cssText = `
                padding: 10px 15px;
                margin: 2px 0;
                cursor: pointer;
                border-radius: 4px;
                transition: all 0.2s;
                ${isSelected ? 'background: #00ff88; color: #1a1a2e;' : 'background: #2a2a3e; color: #ffffff;'}
                border-left: 3px solid ${isSelected ? '#00ff88' : 'transparent'};
            `;

            // Checkbox for multi-select
            let checkbox = '';
            if (this.allowMulti) {
                checkbox = isChecked ? '☑ ' : '☐ ';
            }

            // Number
            const number = `${index + 1}. `;

            // Description
            const desc = this.descriptions[index] ? ` - ${this.descriptions[index]}` : '';

            item.textContent = `${checkbox}${number}${option}${desc}`;

            // Click handler
            item.addEventListener('click', () => {
                this.selectedIndex = index;
                if (this.allowMulti) {
                    this.toggleSelection(option);
                } else {
                    this.confirm();
                }
            });

            // Hover effect
            item.addEventListener('mouseenter', () => {
                if (!isSelected) {
                    item.style.background = '#3a3a4e';
                }
            });

            item.addEventListener('mouseleave', () => {
                if (!isSelected) {
                    item.style.background = '#2a2a3e';
                }
            });

            this.listElement.appendChild(item);
        });

        // Scroll selected item into view
        const selectedItem = this.listElement.children[this.selectedIndex];
        if (selectedItem) {
            selectedItem.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
        }
    }

    /**
     * Handle keyboard input
     */
    handleKeyPress(e) {
        switch (e.key) {
            case 'ArrowUp':
                e.preventDefault();
                this.selectedIndex = Math.max(0, this.selectedIndex - 1);
                this.render();
                break;

            case 'ArrowDown':
                e.preventDefault();
                this.selectedIndex = Math.min(this.options.length - 1, this.selectedIndex + 1);
                this.render();
                break;

            case ' ':
                if (this.allowMulti) {
                    e.preventDefault();
                    this.toggleSelection(this.options[this.selectedIndex]);
                    this.render();
                }
                break;

            case 'Enter':
                e.preventDefault();
                this.confirm();
                break;

            case 'Escape':
                e.preventDefault();
                this.cancel();
                break;

            default:
                // Quick jump with numbers
                if (e.key >= '1' && e.key <= '9') {
                    const index = parseInt(e.key) - 1;
                    if (index < this.options.length) {
                        this.selectedIndex = index;
                        if (!this.allowMulti) {
                            this.confirm();
                        } else {
                            this.render();
                        }
                    }
                }
                break;
        }
    }

    /**
     * Toggle selection (multi-select mode)
     */
    toggleSelection(option) {
        if (this.selectedItems.has(option)) {
            this.selectedItems.delete(option);
        } else {
            this.selectedItems.add(option);
        }
    }

    /**
     * Confirm selection
     */
    confirm() {
        let result;

        if (this.allowMulti) {
            result = this.selectedItems.size > 0
                ? Array.from(this.selectedItems)
                : [this.options[this.selectedIndex]];
        } else {
            result = this.options[this.selectedIndex];
        }

        this.hide();

        if (this.onSelect) {
            this.onSelect(result);
        }
    }

    /**
     * Cancel selection
     */
    cancel() {
        this.hide();

        if (this.onCancel) {
            this.onCancel();
        }
    }

    /**
     * Hide selector
     */
    hide() {
        document.removeEventListener('keydown', this.keyHandler);

        if (this.overlay && this.overlay.parentNode) {
            this.overlay.parentNode.removeChild(this.overlay);
        }

        this.overlay = null;
        this.container = null;
        this.listElement = null;
    }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = uDOSOptionSelector;
}

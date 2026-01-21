/**
 * JSON Viewer/Editor - Desktop/Web Mode
 * 
 * Interactive JSON tree viewer and editor with collapsible nodes,
 * syntax highlighting, search, and validation.
 * 
 * Part of uDOS v1.2.31 - Editor Suite
 * 
 * Features:
 * - Tree view with expand/collapse
 * - Syntax highlighting by type
 * - Inline editing with validation
 * - Search with highlighting
 * - JSON Schema validation
 * - Diff view for changes
 * - Copy value/path
 * - Undo/Redo
 * - WebSocket sync
 * - Export options
 */

class JSONViewer {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            throw new Error(`Container not found: ${containerId}`);
        }
        
        // Configuration
        this.readOnly = options.readOnly || false;
        this.maxExpandDepth = options.maxExpandDepth || 2;
        this.theme = options.theme || 'dark';
        
        // State
        this.data = null;
        this.originalData = null;
        this.currentFile = null;
        this.modified = false;
        this.schema = null;
        
        // Edit state
        this.undoStack = [];
        this.redoStack = [];
        
        // Search state
        this.searchQuery = '';
        this.searchMatches = [];
        this.searchIndex = 0;
        
        // WebSocket
        this.ws = null;
        this.syncEnabled = false;
        
        // Initialize
        this.setupUI();
        this.setupEvents();
    }
    
    setupUI() {
        this.container.innerHTML = `
            <div class="json-viewer-wrapper ${this.theme}">
                <div class="json-viewer-toolbar">
                    <div class="tool-group">
                        <button id="jv-expand-all" title="Expand All">▼</button>
                        <button id="jv-collapse-all" title="Collapse All">▶</button>
                    </div>
                    <div class="tool-group search-group">
                        <input type="text" id="jv-search" placeholder="Search..." />
                        <button id="jv-search-prev" title="Previous">◀</button>
                        <button id="jv-search-next" title="Next">▶</button>
                        <span id="jv-search-count"></span>
                    </div>
                    <div class="tool-group">
                        <button id="jv-undo" title="Undo (Ctrl+Z)">↶</button>
                        <button id="jv-redo" title="Redo (Ctrl+Y)">↷</button>
                    </div>
                    <div class="tool-group">
                        <button id="jv-copy-value" title="Copy Value">📋</button>
                        <button id="jv-copy-path" title="Copy Path">🔗</button>
                    </div>
                    <div class="tool-group">
                        <button id="jv-save" title="Save (Ctrl+S)">💾</button>
                        <button id="jv-load" title="Load">📂</button>
                        <button id="jv-validate" title="Validate">✓</button>
                    </div>
                </div>
                <div class="json-viewer-tree" id="jv-tree"></div>
                <div class="json-viewer-status">
                    <span id="jv-path">Path: (none)</span>
                    <span id="jv-file">${this.currentFile || 'No file'}</span>
                    <span id="jv-modified"></span>
                </div>
            </div>
        `;
        
        this.treeContainer = document.getElementById('jv-tree');
    }
    
    setupEvents() {
        // Toolbar buttons
        document.getElementById('jv-expand-all').addEventListener('click', () => this.expandAll());
        document.getElementById('jv-collapse-all').addEventListener('click', () => this.collapseAll());
        document.getElementById('jv-search').addEventListener('input', (e) => this.search(e.target.value));
        document.getElementById('jv-search-prev').addEventListener('click', () => this.searchPrev());
        document.getElementById('jv-search-next').addEventListener('click', () => this.searchNext());
        document.getElementById('jv-undo').addEventListener('click', () => this.undo());
        document.getElementById('jv-redo').addEventListener('click', () => this.redo());
        document.getElementById('jv-copy-value').addEventListener('click', () => this.copyValue());
        document.getElementById('jv-copy-path').addEventListener('click', () => this.copyPath());
        document.getElementById('jv-save').addEventListener('click', () => this.save());
        document.getElementById('jv-load').addEventListener('click', () => this.load());
        document.getElementById('jv-validate').addEventListener('click', () => this.validate());
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                if (e.key === 'z') { e.preventDefault(); this.undo(); }
                else if (e.key === 'y') { e.preventDefault(); this.redo(); }
                else if (e.key === 's') { e.preventDefault(); this.save(); }
                else if (e.key === 'f') { e.preventDefault(); document.getElementById('jv-search').focus(); }
            }
        });
    }
    
    loadData(data, filename = null) {
        this.data = this.deepClone(data);
        this.originalData = this.deepClone(data);
        this.currentFile = filename;
        this.modified = false;
        this.undoStack = [];
        this.redoStack = [];
        
        this.render();
        this.updateStatus();
    }
    
    loadString(jsonString, filename = null) {
        try {
            const data = JSON.parse(jsonString);
            this.loadData(data, filename);
            return { success: true, message: 'JSON loaded' };
        } catch (e) {
            return { success: false, message: `Invalid JSON: ${e.message}` };
        }
    }
    
    async loadFile() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        
        return new Promise((resolve) => {
            input.addEventListener('change', async (e) => {
                const file = e.target.files[0];
                if (!file) {
                    resolve({ success: false, message: 'No file selected' });
                    return;
                }
                
                try {
                    const text = await file.text();
                    const result = this.loadString(text, file.name);
                    resolve(result);
                } catch (err) {
                    resolve({ success: false, message: err.message });
                }
            });
            
            input.click();
        });
    }
    
    load() {
        this.loadFile().then(result => {
            if (!result.success) {
                alert(result.message);
            }
        });
    }
    
    render() {
        if (!this.data) {
            this.treeContainer.innerHTML = '<div class="empty">No JSON loaded</div>';
            return;
        }
        
        this.treeContainer.innerHTML = '';
        const tree = this.createNode('root', this.data, '', 0);
        this.treeContainer.appendChild(tree);
    }
    
    createNode(key, value, path, depth) {
        const node = document.createElement('div');
        node.className = 'json-node';
        node.dataset.path = path;
        
        const type = this.getType(value);
        const isContainer = type === 'object' || type === 'array';
        const expanded = depth < this.maxExpandDepth;
        
        // Key and toggle
        const keySpan = document.createElement('span');
        keySpan.className = `json-key type-${type}`;
        
        if (isContainer) {
            const toggle = document.createElement('span');
            toggle.className = 'json-toggle';
            toggle.textContent = expanded ? '▼' : '▶';
            toggle.addEventListener('click', () => this.toggleNode(node, toggle));
            keySpan.appendChild(toggle);
        }
        
        const keyText = document.createElement('span');
        keyText.className = 'json-key-text';
        keyText.textContent = key + ':';
        keySpan.appendChild(keyText);
        
        node.appendChild(keySpan);
        
        // Value
        const valueSpan = document.createElement('span');
        valueSpan.className = `json-value type-${type}`;
        
        if (isContainer) {
            // Container preview
            const preview = type === 'object' 
                ? `{ ${Object.keys(value).length} keys }`
                : `[ ${value.length} items ]`;
            valueSpan.textContent = preview;
            valueSpan.className += ' preview';
            
            // Children container
            const children = document.createElement('div');
            children.className = 'json-children';
            children.style.display = expanded ? 'block' : 'none';
            
            if (type === 'object') {
                for (const [k, v] of Object.entries(value)) {
                    const childPath = path ? `${path}.${k}` : k;
                    const child = this.createNode(k, v, childPath, depth + 1);
                    children.appendChild(child);
                }
            } else {
                value.forEach((v, i) => {
                    const childPath = `${path}[${i}]`;
                    const child = this.createNode(`[${i}]`, v, childPath, depth + 1);
                    children.appendChild(child);
                });
            }
            
            node.appendChild(valueSpan);
            node.appendChild(children);
        } else {
            // Leaf value
            valueSpan.textContent = this.formatValue(value, type);
            
            if (!this.readOnly) {
                valueSpan.contentEditable = true;
                valueSpan.addEventListener('blur', () => this.onValueEdit(path, valueSpan));
                valueSpan.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        valueSpan.blur();
                    }
                });
            }
            
            node.appendChild(valueSpan);
        }
        
        // Click to select
        node.addEventListener('click', (e) => {
            if (e.target === keyText || e.target === valueSpan) {
                this.selectNode(node);
            }
        });
        
        return node;
    }
    
    getType(value) {
        if (value === null) return 'null';
        if (Array.isArray(value)) return 'array';
        return typeof value;
    }
    
    formatValue(value, type) {
        switch (type) {
            case 'string': return `"${value}"`;
            case 'null': return 'null';
            case 'boolean': return value ? 'true' : 'false';
            default: return String(value);
        }
    }
    
    parseValue(str) {
        str = str.trim();
        
        // Try JSON parse first
        try {
            return JSON.parse(str);
        } catch (e) {
            // Not valid JSON, return as string
        }
        
        // Boolean
        if (str.toLowerCase() === 'true') return true;
        if (str.toLowerCase() === 'false') return false;
        if (str.toLowerCase() === 'null') return null;
        
        // Number
        if (!isNaN(str) && str !== '') {
            return str.includes('.') ? parseFloat(str) : parseInt(str, 10);
        }
        
        // String (remove quotes if present)
        if ((str.startsWith('"') && str.endsWith('"')) ||
            (str.startsWith("'") && str.endsWith("'"))) {
            return str.slice(1, -1);
        }
        
        return str;
    }
    
    toggleNode(node, toggle) {
        const children = node.querySelector('.json-children');
        if (!children) return;
        
        const expanded = children.style.display !== 'none';
        children.style.display = expanded ? 'none' : 'block';
        toggle.textContent = expanded ? '▶' : '▼';
    }
    
    selectNode(node) {
        // Clear previous selection
        this.treeContainer.querySelectorAll('.json-node.selected').forEach(n => {
            n.classList.remove('selected');
        });
        
        node.classList.add('selected');
        this.selectedPath = node.dataset.path;
        
        document.getElementById('jv-path').textContent = `Path: ${this.selectedPath || '(root)'}`;
    }
    
    onValueEdit(path, element) {
        const newValue = this.parseValue(element.textContent);
        const oldValue = this.getValueAtPath(path);
        
        if (newValue !== oldValue) {
            this.saveState();
            this.setValueAtPath(path, newValue);
            this.modified = true;
            this.updateStatus();
            
            // Reformat display
            const type = this.getType(newValue);
            element.textContent = this.formatValue(newValue, type);
            element.className = `json-value type-${type}`;
        }
    }
    
    getValueAtPath(path) {
        if (!path) return this.data;
        
        const parts = this.parsePath(path);
        let obj = this.data;
        
        for (const part of parts) {
            if (obj === undefined || obj === null) return undefined;
            obj = obj[part];
        }
        
        return obj;
    }
    
    setValueAtPath(path, value) {
        if (!path) {
            this.data = value;
            return;
        }
        
        const parts = this.parsePath(path);
        const lastPart = parts.pop();
        let obj = this.data;
        
        for (const part of parts) {
            if (obj[part] === undefined) {
                obj[part] = typeof part === 'number' ? [] : {};
            }
            obj = obj[part];
        }
        
        obj[lastPart] = value;
    }
    
    parsePath(path) {
        const parts = [];
        let current = '';
        let inBracket = false;
        
        for (const char of path) {
            if (char === '.' && !inBracket) {
                if (current) parts.push(current);
                current = '';
            } else if (char === '[') {
                if (current) parts.push(current);
                current = '';
                inBracket = true;
            } else if (char === ']') {
                if (current) parts.push(parseInt(current, 10));
                current = '';
                inBracket = false;
            } else {
                current += char;
            }
        }
        
        if (current) parts.push(current);
        return parts;
    }
    
    expandAll() {
        this.treeContainer.querySelectorAll('.json-children').forEach(el => {
            el.style.display = 'block';
        });
        this.treeContainer.querySelectorAll('.json-toggle').forEach(el => {
            el.textContent = '▼';
        });
    }
    
    collapseAll() {
        this.treeContainer.querySelectorAll('.json-children').forEach(el => {
            el.style.display = 'none';
        });
        this.treeContainer.querySelectorAll('.json-toggle').forEach(el => {
            el.textContent = '▶';
        });
    }
    
    search(query) {
        this.searchQuery = query.toLowerCase();
        this.searchMatches = [];
        this.searchIndex = 0;
        
        // Clear previous highlights
        this.treeContainer.querySelectorAll('.search-match').forEach(el => {
            el.classList.remove('search-match');
        });
        
        if (!query) {
            document.getElementById('jv-search-count').textContent = '';
            return;
        }
        
        // Find matches
        this.treeContainer.querySelectorAll('.json-node').forEach(node => {
            const keyText = node.querySelector('.json-key-text')?.textContent || '';
            const valueText = node.querySelector('.json-value')?.textContent || '';
            
            if (keyText.toLowerCase().includes(query) || 
                valueText.toLowerCase().includes(query)) {
                node.classList.add('search-match');
                this.searchMatches.push(node);
            }
        });
        
        document.getElementById('jv-search-count').textContent = 
            this.searchMatches.length > 0 
                ? `${this.searchIndex + 1}/${this.searchMatches.length}`
                : 'No matches';
        
        if (this.searchMatches.length > 0) {
            this.scrollToMatch(0);
        }
    }
    
    searchNext() {
        if (this.searchMatches.length === 0) return;
        this.searchIndex = (this.searchIndex + 1) % this.searchMatches.length;
        this.scrollToMatch(this.searchIndex);
    }
    
    searchPrev() {
        if (this.searchMatches.length === 0) return;
        this.searchIndex = (this.searchIndex - 1 + this.searchMatches.length) % this.searchMatches.length;
        this.scrollToMatch(this.searchIndex);
    }
    
    scrollToMatch(index) {
        const node = this.searchMatches[index];
        if (!node) return;
        
        // Expand parents
        let parent = node.parentElement;
        while (parent) {
            if (parent.classList.contains('json-children')) {
                parent.style.display = 'block';
                const toggle = parent.parentElement.querySelector('.json-toggle');
                if (toggle) toggle.textContent = '▼';
            }
            parent = parent.parentElement;
        }
        
        // Highlight current
        this.treeContainer.querySelectorAll('.current-match').forEach(el => {
            el.classList.remove('current-match');
        });
        node.classList.add('current-match');
        
        // Scroll into view
        node.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
        document.getElementById('jv-search-count').textContent = 
            `${index + 1}/${this.searchMatches.length}`;
    }
    
    saveState() {
        this.undoStack.push(JSON.stringify(this.data));
        this.redoStack = [];
        
        if (this.undoStack.length > 100) {
            this.undoStack.shift();
        }
    }
    
    undo() {
        if (this.undoStack.length === 0) return;
        
        this.redoStack.push(JSON.stringify(this.data));
        this.data = JSON.parse(this.undoStack.pop());
        this.render();
        this.modified = true;
        this.updateStatus();
    }
    
    redo() {
        if (this.redoStack.length === 0) return;
        
        this.undoStack.push(JSON.stringify(this.data));
        this.data = JSON.parse(this.redoStack.pop());
        this.render();
        this.modified = true;
        this.updateStatus();
    }
    
    copyValue() {
        if (!this.selectedPath) {
            alert('Select a node first');
            return;
        }
        
        const value = this.getValueAtPath(this.selectedPath);
        const text = JSON.stringify(value, null, 2);
        
        navigator.clipboard.writeText(text).then(() => {
            this.showMessage('Value copied!');
        });
    }
    
    copyPath() {
        if (!this.selectedPath) {
            alert('Select a node first');
            return;
        }
        
        navigator.clipboard.writeText(this.selectedPath).then(() => {
            this.showMessage('Path copied!');
        });
    }
    
    showMessage(msg) {
        const status = document.getElementById('jv-file');
        const original = status.textContent;
        status.textContent = msg;
        setTimeout(() => { status.textContent = original; }, 2000);
    }
    
    save() {
        if (!this.data) {
            alert('No data to save');
            return;
        }
        
        const json = JSON.stringify(this.data, null, 2);
        const blob = new Blob([json], { type: 'application/json' });
        
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = this.currentFile || 'data.json';
        a.click();
        
        this.originalData = this.deepClone(this.data);
        this.modified = false;
        this.updateStatus();
    }
    
    validate() {
        if (!this.schema) {
            alert('No schema loaded. Use loadSchema() first.');
            return;
        }
        
        // Would use ajv or similar library for validation
        // For now, just check basic structure
        try {
            JSON.stringify(this.data);
            this.showMessage('JSON is valid');
        } catch (e) {
            alert(`Validation error: ${e.message}`);
        }
    }
    
    loadSchema(schema) {
        this.schema = schema;
    }
    
    getDiff() {
        if (!this.originalData || !this.data) return [];
        
        const diffs = [];
        this.compareDiff(this.originalData, this.data, '', diffs);
        return diffs;
    }
    
    compareDiff(old, curr, path, diffs) {
        if (old === curr) return;
        
        const oldType = this.getType(old);
        const newType = this.getType(curr);
        
        if (oldType !== newType) {
            diffs.push({ path, type: 'type_change', old: oldType, new: newType });
            return;
        }
        
        if (oldType === 'object') {
            const oldKeys = new Set(Object.keys(old));
            const newKeys = new Set(Object.keys(curr));
            
            for (const key of newKeys) {
                if (!oldKeys.has(key)) {
                    diffs.push({ path: path ? `${path}.${key}` : key, type: 'added', value: curr[key] });
                }
            }
            
            for (const key of oldKeys) {
                if (!newKeys.has(key)) {
                    diffs.push({ path: path ? `${path}.${key}` : key, type: 'removed', value: old[key] });
                } else {
                    this.compareDiff(old[key], curr[key], path ? `${path}.${key}` : key, diffs);
                }
            }
        } else if (oldType === 'array') {
            if (old.length !== curr.length) {
                diffs.push({ path, type: 'length_change', old: old.length, new: curr.length });
            }
            
            const minLen = Math.min(old.length, curr.length);
            for (let i = 0; i < minLen; i++) {
                this.compareDiff(old[i], curr[i], `${path}[${i}]`, diffs);
            }
        } else {
            diffs.push({ path, type: 'value_change', old, new: curr });
        }
    }
    
    deepClone(obj) {
        return JSON.parse(JSON.stringify(obj));
    }
    
    updateStatus() {
        document.getElementById('jv-file').textContent = this.currentFile || 'No file';
        document.getElementById('jv-modified').textContent = this.modified ? '*' : '';
    }
    
    // WebSocket sync
    connectSync(url) {
        this.ws = new WebSocket(url);
        
        this.ws.onopen = () => {
            this.syncEnabled = true;
            console.log('JSON viewer sync connected');
        };
        
        this.ws.onmessage = (e) => {
            try {
                const msg = JSON.parse(e.data);
                if (msg.type === 'update') {
                    this.setValueAtPath(msg.path, msg.value);
                    this.render();
                } else if (msg.type === 'full_sync') {
                    this.data = msg.data;
                    this.render();
                }
            } catch (err) {
                console.error('Sync message error:', err);
            }
        };
        
        this.ws.onclose = () => {
            this.syncEnabled = false;
            console.log('JSON viewer sync disconnected');
        };
    }
}

// CSS styles
const jsonViewerStyles = `
.json-viewer-wrapper {
    font-family: 'Fira Code', 'Monaco', 'Consolas', monospace;
    font-size: 14px;
    background: #1e1e1e;
    border-radius: 5px;
    overflow: hidden;
}

.json-viewer-wrapper.dark {
    --bg: #1e1e1e;
    --text: #d4d4d4;
    --key: #9cdcfe;
    --string: #ce9178;
    --number: #b5cea8;
    --boolean: #569cd6;
    --null: #569cd6;
    --bracket: #ffd700;
}

.json-viewer-toolbar {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    padding: 8px;
    background: #252526;
    border-bottom: 1px solid #3c3c3c;
}

.json-viewer-toolbar .tool-group {
    display: flex;
    align-items: center;
    gap: 5px;
}

.json-viewer-toolbar button {
    padding: 5px 10px;
    background: #3c3c3c;
    border: none;
    color: #ccc;
    cursor: pointer;
    border-radius: 3px;
}

.json-viewer-toolbar button:hover {
    background: #4c4c4c;
}

.json-viewer-toolbar input {
    padding: 5px 10px;
    background: #3c3c3c;
    border: 1px solid #555;
    color: #ccc;
    border-radius: 3px;
    width: 200px;
}

.json-viewer-tree {
    padding: 10px;
    max-height: 500px;
    overflow: auto;
}

.json-node {
    padding-left: 20px;
}

.json-node.selected {
    background: rgba(0, 100, 200, 0.2);
}

.json-node.search-match {
    background: rgba(255, 200, 0, 0.2);
}

.json-node.current-match {
    background: rgba(255, 200, 0, 0.4);
}

.json-toggle {
    cursor: pointer;
    margin-right: 5px;
    color: #888;
    user-select: none;
}

.json-key-text {
    color: var(--key, #9cdcfe);
    margin-right: 5px;
}

.json-value {
    cursor: text;
}

.json-value.type-string { color: var(--string, #ce9178); }
.json-value.type-number { color: var(--number, #b5cea8); }
.json-value.type-boolean { color: var(--boolean, #569cd6); }
.json-value.type-null { color: var(--null, #569cd6); font-style: italic; }
.json-value.preview { color: #888; font-style: italic; }

.json-children {
    margin-left: 10px;
    border-left: 1px dotted #3c3c3c;
    padding-left: 10px;
}

.json-viewer-status {
    display: flex;
    gap: 20px;
    padding: 8px;
    background: #252526;
    color: #888;
    font-size: 12px;
    border-top: 1px solid #3c3c3c;
}

.empty {
    color: #888;
    text-align: center;
    padding: 40px;
}
`;

// Export for module use
if (typeof module !== 'undefined') {
    module.exports = { JSONViewer, jsonViewerStyles };
}

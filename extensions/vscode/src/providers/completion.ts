import * as vscode from 'vscode';

interface CommandDoc {
    label: string;
    detail: string;
    documentation: string;
    insertText?: string;
}

export class UPYCompletionProvider implements vscode.CompletionItemProvider {
    private commands: CommandDoc[] = [
        // Knowledge Management
        { label: 'GUIDE ADD', detail: 'GUIDE ADD tier<N> <type> <title>', documentation: 'Add new knowledge guide\n\nExample: GUIDE ADD tier3 guide "Water Purification"' },
        { label: 'GUIDE SEARCH', detail: 'GUIDE SEARCH <query>', documentation: 'Search knowledge base\n\nExample: GUIDE SEARCH "fire starting"' },
        { label: 'GUIDE LIST', detail: 'GUIDE LIST [category]', documentation: 'List all guides or filter by category\n\nExample: GUIDE LIST water' },
        { label: 'GUIDE TAG', detail: 'GUIDE TAG <guide_id> <tags>', documentation: 'Add tags to guide\n\nExample: GUIDE TAG guide_123 survival,water,purification' },
        { label: 'GUIDE UPDATE', detail: 'GUIDE UPDATE <guide_id> <field> <value>', documentation: 'Update guide field' },
        { label: 'GUIDE DELETE', detail: 'GUIDE DELETE <guide_id>', documentation: 'Delete guide' },
        { label: 'GUIDE EXPORT', detail: 'GUIDE EXPORT <guide_id> <format>', documentation: 'Export guide (markdown, json, pdf)' },
        { label: 'GUIDE STATS', detail: 'GUIDE STATS', documentation: 'Show knowledge bank statistics' },

        // Map & Location
        { label: 'MAP GOTO', detail: 'MAP GOTO <tile> [layer]', documentation: 'Navigate to location\n\nExample: MAP GOTO AA340 100\n(Sydney, world layer)' },
        { label: 'MAP ASCEND', detail: 'MAP ASCEND', documentation: 'Move up one map layer (surface → cloud → satellite)' },
        { label: 'MAP DESCEND', detail: 'MAP DESCEND', documentation: 'Move down one map layer (satellite → cloud → surface → underground)' },
        { label: 'MAP SEARCH', detail: 'MAP SEARCH <query>', documentation: 'Search locations\n\nExample: MAP SEARCH "Sydney"' },
        { label: 'MAP INFO', detail: 'MAP INFO [tile]', documentation: 'Show location information' },
        { label: 'MAP DISTANCE', detail: 'MAP DISTANCE <from_tile> <to_tile>', documentation: 'Calculate distance between locations' },
        { label: 'MAP ROUTE', detail: 'MAP ROUTE <from_tile> <to_tile>', documentation: 'Find route between locations' },
        { label: 'MAP NEARBY', detail: 'MAP NEARBY [radius]', documentation: 'Show nearby locations' },
        { label: 'MAP LAYER', detail: 'MAP LAYER <layer_id>', documentation: 'Jump to specific layer (100, 200, 300, 400, 500)' },

        // Mission Management
        { label: 'MISSION CREATE', detail: 'MISSION CREATE "<name>"', documentation: 'Create new mission\n\nExample: MISSION CREATE "Water Source Survey"' },
        { label: 'MISSION START', detail: 'MISSION START <mission_id>', documentation: 'Start mission execution' },
        { label: 'MISSION PAUSE', detail: 'MISSION PAUSE <mission_id>', documentation: 'Pause active mission' },
        { label: 'MISSION RESUME', detail: 'MISSION RESUME <mission_id>', documentation: 'Resume paused mission' },
        { label: 'MISSION COMPLETE', detail: 'MISSION COMPLETE <mission_id>', documentation: 'Mark mission complete' },
        { label: 'MISSION FAIL', detail: 'MISSION FAIL <mission_id> <reason>', documentation: 'Mark mission failed' },
        { label: 'MISSION STATUS', detail: 'MISSION STATUS [mission_id]', documentation: 'Show mission status' },
        { label: 'MISSION LIST', detail: 'MISSION LIST [filter]', documentation: 'List missions (active, completed, failed, all)' },
        { label: 'MISSION UPDATE', detail: 'MISSION UPDATE <mission_id> <field> <value>', documentation: 'Update mission field' },
        { label: 'MISSION DELETE', detail: 'MISSION DELETE <mission_id>', documentation: 'Delete mission' },

        // Workflow Automation
        { label: 'WORKFLOW START', detail: 'WORKFLOW START <workflow_name>', documentation: 'Execute workflow script\n\nExample: WORKFLOW START knowledge-expansion' },
        { label: 'WORKFLOW STOP', detail: 'WORKFLOW STOP <workflow_id>', documentation: 'Stop running workflow' },
        { label: 'WORKFLOW PAUSE', detail: 'WORKFLOW PAUSE <workflow_id>', documentation: 'Pause workflow execution' },
        { label: 'WORKFLOW RESUME', detail: 'WORKFLOW RESUME <workflow_id>', documentation: 'Resume paused workflow' },
        { label: 'WORKFLOW STATUS', detail: 'WORKFLOW STATUS [workflow_id]', documentation: 'Show workflow status' },
        { label: 'WORKFLOW LIST', detail: 'WORKFLOW LIST', documentation: 'List all workflows' },

        // Checkpoint System
        { label: 'CHECKPOINT SAVE', detail: 'CHECKPOINT SAVE <checkpoint_id>', documentation: 'Save execution state\n\nExample: CHECKPOINT SAVE mission_step_5' },
        { label: 'CHECKPOINT LOAD', detail: 'CHECKPOINT LOAD <checkpoint_id>', documentation: 'Load saved state' },
        { label: 'CHECKPOINT LIST', detail: 'CHECKPOINT LIST', documentation: 'List all checkpoints' },
        { label: 'CHECKPOINT DELETE', detail: 'CHECKPOINT DELETE <checkpoint_id>', documentation: 'Delete checkpoint' },
        { label: 'CHECKPOINT RESTORE', detail: 'CHECKPOINT RESTORE <checkpoint_id>', documentation: 'Restore from checkpoint' },

        // Checklist Management
        { label: 'CHECKLIST CREATE', detail: 'CHECKLIST CREATE "<name>"', documentation: 'Create new checklist' },
        { label: 'CHECKLIST ADD', detail: 'CHECKLIST ADD <checklist_id> "<item>"', documentation: 'Add item to checklist' },
        { label: 'CHECKLIST CHECK', detail: 'CHECKLIST CHECK <checklist_id> <item_id>', documentation: 'Check item as complete' },
        { label: 'CHECKLIST UNCHECK', detail: 'CHECKLIST UNCHECK <checklist_id> <item_id>', documentation: 'Uncheck item' },
        { label: 'CHECKLIST STATUS', detail: 'CHECKLIST STATUS <checklist_id>', documentation: 'Show checklist progress' },
        { label: 'CHECKLIST DELETE', detail: 'CHECKLIST DELETE <checklist_id>', documentation: 'Delete checklist' },

        // Diagram & Graphics
        { label: 'DIAGRAM GENERATE', detail: 'DIAGRAM GENERATE <type> <name>', documentation: 'Generate diagram\n\nTypes: flowchart, mindmap, timeline, network' },
        { label: 'GENERATE GUIDE', detail: 'GENERATE GUIDE <category> "<title>"', documentation: 'Generate knowledge guide using AI\n\nExample: GENERATE GUIDE water "Rainwater Collection"' },
        { label: 'GENERATE DIAGRAM', detail: 'GENERATE DIAGRAM <category> "<subject>"', documentation: 'Generate SVG diagram\n\nExample: GENERATE DIAGRAM water "Solar Still Design"' },
        { label: 'SPRITE CREATE', detail: 'SPRITE CREATE <name> <width> <height>', documentation: 'Create ASCII sprite' },
        { label: 'PANEL RENDER', detail: 'PANEL RENDER <template> [data]', documentation: 'Render panel from template' },
        { label: 'TELETEXT RENDER', detail: 'TELETEXT RENDER <page>', documentation: 'Render teletext page' },

        // File Operations
        { label: 'NEW', detail: 'NEW <path> [template]', documentation: 'Create new file\n\nExample: NEW memory/missions/search-water.upy' },
        { label: 'DELETE', detail: 'DELETE <path>', documentation: 'Delete file (soft-delete to .archive/)' },
        { label: 'COPY', detail: 'COPY <source> <destination>', documentation: 'Copy file' },
        { label: 'MOVE', detail: 'MOVE <source> <destination>', documentation: 'Move/rename file' },
        { label: 'READ', detail: 'READ <path>', documentation: 'Read file contents' },
        { label: 'WRITE', detail: 'WRITE <path> <content>', documentation: 'Write to file' },
        { label: 'APPEND', detail: 'APPEND <path> <content>', documentation: 'Append to file' },
        { label: 'LIST', detail: 'LIST <directory>', documentation: 'List directory contents' },
        { label: 'FIND', detail: 'FIND <pattern>', documentation: 'Find files matching pattern' },

        // System Commands
        { label: 'SET', detail: 'SET <variable> <value>', documentation: 'Assign value to variable\n\nExample: SET $LOCATION "AA340"' },
        { label: 'GET', detail: 'GET <variable>', documentation: 'Get variable value\n\nExample: GET $MISSION.STATUS' },
        { label: 'STATUS', detail: 'STATUS [--detailed]', documentation: 'Show system status' },
        { label: 'SETTINGS', detail: 'SETTINGS [key] [value]', documentation: 'View/update settings' },
        { label: 'THEME', detail: 'THEME <theme_name>', documentation: 'Change theme (foundation, galaxy, ocean, forest, desert, arctic)' },
        { label: 'CLEAN', detail: 'CLEAN [--scan|--purge]', documentation: 'Clean memory workspace, manage .archive/ folders' },
        { label: 'TIDY', detail: 'TIDY [--report]', documentation: 'Organize workspace files' },
        { label: 'BACKUP', detail: 'BACKUP <file>', documentation: 'Create timestamped backup in .archive/' },
        { label: 'RESTORE', detail: 'RESTORE <file> [timestamp]', documentation: 'Restore file from backup' },
        { label: 'UNDO', detail: 'UNDO <file>', documentation: 'Revert to previous version' },
        { label: 'REDO', detail: 'REDO <file>', documentation: 'Re-apply undone changes' },
        { label: 'ARCHIVE', detail: 'ARCHIVE <file>', documentation: 'Move completed work to .archive/' },
        { label: 'REPAIR', detail: 'REPAIR [RECOVER <file>]', documentation: 'System repair, recover deleted files' },

        // Extension Management
        { label: 'EXTENSION LIST', detail: 'EXTENSION LIST', documentation: 'List installed extensions' },
        { label: 'EXTENSION INFO', detail: 'EXTENSION INFO <extension_id>', documentation: 'Show extension details' },
        { label: 'EXTENSION ENABLE', detail: 'EXTENSION ENABLE <extension_id>', documentation: 'Enable extension' },
        { label: 'EXTENSION DISABLE', detail: 'EXTENSION DISABLE <extension_id>', documentation: 'Disable extension' },

        // POKE (Server Management)
        { label: 'POKE WEB', detail: 'POKE WEB [start|stop|status]', documentation: 'Manage web dashboard (port 5555)' },
        { label: 'POKE API', detail: 'POKE API [start|stop|status]', documentation: 'Manage API server (port 5001)' },
        { label: 'POKE TELETEXT', detail: 'POKE TELETEXT [start|stop|status]', documentation: 'Manage teletext server (port 9002)' },

        // Control Flow
        { label: 'IF', detail: 'IF <condition> THEN ... END', documentation: 'Conditional execution\n\nExample:\nIF $COUNT > 10 THEN\n    # do something\nEND' },
        { label: 'FOREACH', detail: 'FOREACH $item IN $list ... END', documentation: 'Loop over items\n\nExample:\nFOREACH $guide IN $guides\n    GUIDE TAG $guide survival\nEND' },
        { label: 'WHILE', detail: 'WHILE <condition> ... END', documentation: 'While loop\n\nExample:\nWHILE $count < 100\n    SET $count ($count + 1)\nEND' },
    ];

    provideCompletionItems(
        document: vscode.TextDocument,
        position: vscode.Position
    ): vscode.CompletionItem[] {
        const linePrefix = document.lineAt(position).text.substr(0, position.character);

        // Variable completion
        if (linePrefix.endsWith('$')) {
            return this.getVariableCompletions();
        }

        // System variable properties
        if (linePrefix.match(/\$MISSION\.$/)) {
            return this.getMissionPropertyCompletions();
        }
        if (linePrefix.match(/\$WORKFLOW\.$/)) {
            return this.getWorkflowPropertyCompletions();
        }
        if (linePrefix.match(/\$CHECKPOINT\.$/)) {
            return this.getCheckpointPropertyCompletions();
        }
        if (linePrefix.match(/\$GUIDE\.$/)) {
            return this.getGuidePropertyCompletions();
        }

        // Command completion
        return this.commands.map(cmd => {
            const item = new vscode.CompletionItem(cmd.label, vscode.CompletionItemKind.Function);
            item.detail = cmd.detail;
            item.documentation = new vscode.MarkdownString(cmd.documentation);
            item.insertText = cmd.insertText || cmd.label;
            return item;
        });
    }

    private getVariableCompletions(): vscode.CompletionItem[] {
        const vars = [
            { name: 'MISSION', detail: 'Current mission context' },
            { name: 'WORKFLOW', detail: 'Workflow execution context' },
            { name: 'CHECKPOINT', detail: 'Checkpoint state' },
            { name: 'GUIDE', detail: 'Guide reference' },
            { name: 'LOCATION', detail: 'Current location' },
            { name: 'TILE', detail: 'Current tile code' },
            { name: 'LAYER', detail: 'Current map layer' },
            { name: 'SYSTEM', detail: 'System settings' },
            { name: 'USER', detail: 'User settings' },
            { name: 'ENV', detail: 'Environment variables' },
            { name: 'CONFIG', detail: 'Configuration' },
            { name: 'THEME', detail: 'Current theme' },
            { name: 'MODE', detail: 'Current mode (REGULAR, DEV, ASSIST)' },
        ];

        return vars.map(v => {
            const item = new vscode.CompletionItem('$' + v.name, vscode.CompletionItemKind.Variable);
            item.detail = v.detail;
            item.insertText = '$' + v.name;
            return item;
        });
    }

    private getMissionPropertyCompletions(): vscode.CompletionItem[] {
        const props = ['ID', 'NAME', 'STATUS', 'PROGRESS', 'START_TIME', 'OBJECTIVE', 'NOTES'];
        return props.map(p => {
            const item = new vscode.CompletionItem(p, vscode.CompletionItemKind.Property);
            item.insertText = p;
            return item;
        });
    }

    private getWorkflowPropertyCompletions(): vscode.CompletionItem[] {
        const props = ['NAME', 'PHASE', 'ITERATION', 'ERRORS', 'ELAPSED_TIME', 'STATUS'];
        return props.map(p => {
            const item = new vscode.CompletionItem(p, vscode.CompletionItemKind.Property);
            item.insertText = p;
            return item;
        });
    }

    private getCheckpointPropertyCompletions(): vscode.CompletionItem[] {
        const props = ['ID', 'TIMESTAMP', 'DATA', 'PREVIOUS', 'NEXT'];
        return props.map(p => {
            const item = new vscode.CompletionItem(p, vscode.CompletionItemKind.Property);
            item.insertText = p;
            return item;
        });
    }

    private getGuidePropertyCompletions(): vscode.CompletionItem[] {
        const props = ['ID', 'TITLE', 'CATEGORY', 'TAGS', 'PATH', 'CONTENT'];
        return props.map(p => {
            const item = new vscode.CompletionItem(p, vscode.CompletionItemKind.Property);
            item.insertText = p;
            return item;
        });
    }
}

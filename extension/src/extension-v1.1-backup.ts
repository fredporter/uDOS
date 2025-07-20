import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';

// uDOS Extension v1.1.0 - Enhanced with Mission System and User Companions
export function activate(context: vscode.ExtensionContext) {
    console.log('uDOS v1.1.0 extension is now active with enhanced features!');

    // ===== CORE UDOS COMMANDS =====
    
    let runCommand = vscode.commands.registerCommand('udos.runCommand', async () => {
        const command = await vscode.window.showInputBox({
            prompt: 'Enter uDOS command (v1.1.0 enhanced)',
            placeHolder: 'e.g., HELP, DASH, CHECK, MISSION, COMPANION'
        });

        if (command) {
            await runUDOSCommand(command);
        }
    });

    let validateInstallation = vscode.commands.registerCommand('udos.validateInstallation', () => {
        runUDOSScript('./uCode/validate-installation.sh', ['full']);
    });

    let showUserRole = vscode.commands.registerCommand('udos.showUserRole', () => {
        vscode.window.showInformationMessage('uDOS v1.1.0: User roles are Wizard, Sorcerer, Imp, Drone, Ghost');
    });

    // ===== MISSION CONTROL SYSTEM =====

    let createMission = vscode.commands.registerCommand('udos.createMission', async () => {
        const missionName = await vscode.window.showInputBox({
            prompt: 'Enter mission name',
            placeHolder: 'e.g., Complete uDOS v1.1.0 Development'
        });

        if (!missionName) return;

        const missionDescription = await vscode.window.showInputBox({
            prompt: 'Enter mission description',
            placeHolder: 'e.g., Finalize all core systems and integrations'
        });

        if (!missionDescription) return;

        // Optional location coordinates
        const location = await vscode.window.showInputBox({
            prompt: 'Enter location coordinates (optional)',
            placeHolder: 'e.g., 40.7831,-73.9712 (leave empty for default)'
        });

        const locationArgs = location ? location.split(',').map(s => s.trim()) : ['0', '0'];
        runUDOSScript('./uCode/mission-system.sh', ['create', missionName, missionDescription, ...locationArgs]);
    });

    let listMissions = vscode.commands.registerCommand('udos.listMissions', () => {
        runUDOSScript('./uCode/mission-system.sh', ['list']);
    });

    let missionStats = vscode.commands.registerCommand('udos.missionStats', () => {
        runUDOSScript('./uCode/mission-system.sh', ['stats']);
    });

    let createMilestone = vscode.commands.registerCommand('udos.createMilestone', async () => {
        const missionId = await vscode.window.showInputBox({
            prompt: 'Enter mission ID',
            placeHolder: 'e.g., complete-udos-v1-1-0-development'
        });

        if (!missionId) return;

        const milestoneName = await vscode.window.showInputBox({
            prompt: 'Enter milestone name',
            placeHolder: 'e.g., Complete VS Code Extension'
        });

        if (!milestoneName) return;

        const milestoneDescription = await vscode.window.showInputBox({
            prompt: 'Enter milestone description',
            placeHolder: 'e.g., Enhance extension with new features'
        });

        runUDOSScript('./uCode/mission-system.sh', ['milestone', missionId, milestoneName, milestoneDescription || '']);
    });

    // ===== USER COMPANION SYSTEM =====

    let listCompanions = vscode.commands.registerCommand('udos.listCompanions', () => {
        runUDOSScript('./uCompanion/gemini/uc-gemini.sh', ['list']);
    });

    let startChester = vscode.commands.registerCommand('udos.startChester', () => {
        runUDOSScript('./uCompanion/gemini/uc-gemini.sh', ['chester']);
    });

    let startSorcerer = vscode.commands.registerCommand('udos.startSorcerer', () => {
        runUDOSScript('./uCompanion/gemini/uc-gemini.sh', ['sorcerer']);
    });

    let useImpCompanion = vscode.commands.registerCommand('udos.useImpCompanion', async () => {
        const task = await vscode.window.showInputBox({
            prompt: 'Enter task for Imp Companion',
            placeHolder: 'e.g., organize files in temp directory'
        });

        if (task) {
            runUDOSScript('./uCompanion/gemini/uc-gemini.sh', ['imp', task]);
        }
    });

    let useDroneCompanion = vscode.commands.registerCommand('udos.useDroneCompanion', () => {
        runUDOSScript('./uCompanion/gemini/uc-gemini.sh', ['drone']);
    });

    let useGhostCompanion = vscode.commands.registerCommand('udos.useGhostCompanion', async () => {
        const operation = await vscode.window.showInputBox({
            prompt: 'Enter stealth operation for Ghost Companion',
            placeHolder: 'e.g., clean temporary files silently'
        });

        if (operation) {
            runUDOSScript('./uCompanion/gemini/uc-gemini.sh', ['ghost', operation]);
        }
    });

    let companionStatus = vscode.commands.registerCommand('udos.companionStatus', () => {
        runUDOSScript('./uCode/uc-system-setup.sh', ['status']);
    });

    // ===== DASHBOARD & ANALYTICS =====

    let showDashboard = vscode.commands.registerCommand('udos.showDashboard', () => {
        runUDOSScript('./uCode/dash.sh', ['live']);
    });

    let generateDashboard = vscode.commands.registerCommand('udos.generateDashboard', () => {
        runUDOSScript('./uCode/dash.sh', ['build']);
    });

    let updateAnalytics = vscode.commands.registerCommand('udos.updateAnalytics', () => {
        runUDOSScript('./uCode/mission-dashboard-integration.sh', ['update']);
    });

    // ===== MAPPING SYSTEM =====

    let showMapping = vscode.commands.registerCommand('udos.showMapping', () => {
        runUDOSScript('./uTemplate/mapping/working-demo.sh', []);
    });

    let showMissionMapping = vscode.commands.registerCommand('udos.showMissionMapping', async () => {
        // Generate mission mapping data first
        await runUDOSScript('./uCode/mission-mapping-integration.sh', ['all']);
        
        // Open the demo in Simple Browser
        const demoPath = path.join(vscode.workspace.rootPath || '', 'uTemplate/mapping/mission-mapping-demo.html');
        if (fs.existsSync(demoPath)) {
            vscode.env.openExternal(vscode.Uri.file(demoPath));
        }
    });

    // ===== SYSTEM UTILITIES =====

    let systemStatus = vscode.commands.registerCommand('udos.systemStatus', () => {
        const terminal = vscode.window.createTerminal('uDOS System Status');
        terminal.sendText(`
echo "🎯 uDOS v1.1.0 System Status"
echo "================================="
echo ""
echo "📋 Mission System:"
./uCode/mission-system.sh stats
echo ""
echo "🤝 User Companions:"  
./uCode/uc-system-setup.sh status
echo ""
echo "📊 Dashboard Status:"
ps aux | grep -E 'dash\\.sh|analytics' | grep -v grep || echo 'Dashboard not running - use ctrl+shift+p > uDOS: Show Dashboard'
echo ""
echo "🗺️ Mapping System: ✅ Available"
echo "🎮 VS Code Extension: ✅ Active (v1.1.0)"
        `);
        terminal.show();
    });

    let quickSetup = vscode.commands.registerCommand('udos.quickSetup', async () => {
        const option = await vscode.window.showQuickPick([
            '🎯 Create First Mission',
            '🤝 Setup User Companions',
            '📊 Launch Dashboard',
            '🗺️ Show Mapping Demo',
            '✅ Full System Check'
        ], {
            placeHolder: 'Choose quick setup option'
        });

        switch (option) {
            case '🎯 Create First Mission':
                vscode.commands.executeCommand('udos.createMission');
                break;
            case '🤝 Setup User Companions':
                runUDOSScript('./uCode/uc-system-setup.sh', ['status']);
                break;
            case '📊 Launch Dashboard':
                vscode.commands.executeCommand('udos.showDashboard');
                break;
            case '🗺️ Show Mapping Demo':
                vscode.commands.executeCommand('udos.showMapping');
                break;
            case '✅ Full System Check':
                vscode.commands.executeCommand('udos.systemStatus');
                break;
        }
    });

    // ===== FILE OPERATIONS =====

    let processShortcodes = vscode.commands.registerCommand('udos.processShortcodes', async (uri: vscode.Uri) => {
        if (!uri && vscode.window.activeTextEditor) {
            uri = vscode.window.activeTextEditor.document.uri;
        }

        if (uri) {
            const outputPath = uri.fsPath.replace(/\.md$/, '.html');
            runUDOSScript('./uCode/process-shortcodes.sh', [uri.fsPath, outputPath]);
        } else {
            vscode.window.showErrorMessage('No file selected for shortcode processing');
        }
    });

    let viewWithGlow = vscode.commands.registerCommand('udos.viewWithGlow', (uri: vscode.Uri) => {
        if (!uri && vscode.window.activeTextEditor) {
            uri = vscode.window.activeTextEditor.document.uri;
        }

        if (uri) {
            const terminal = vscode.window.createTerminal('uDOS Glow');
            terminal.sendText(`glow "${uri.fsPath}"`);
            terminal.show();
        }
    });

    // ===== REGISTER ALL COMMANDS =====

    context.subscriptions.push(
        runCommand,
        validateInstallation,
        showUserRole,
        createMission,
        listMissions,
        missionStats,
        createMilestone,
        listCompanions,
        startChester,
        startSorcerer,
        useImpCompanion,
        useDroneCompanion,
        useGhostCompanion,
        companionStatus,
        showDashboard,
        generateDashboard,
        updateAnalytics,
        showMapping,
        showMissionMapping,
        systemStatus,
        quickSetup,
        processShortcodes,
        viewWithGlow
    );

    // ===== STATUS BAR =====

    const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.text = "$(rocket) uDOS v1.1.0";
    statusBarItem.tooltip = "uDOS Enhanced - Click for quick setup";
    statusBarItem.command = 'udos.quickSetup';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);

    // ===== WELCOME MESSAGE =====

    vscode.window.showInformationMessage(
        'uDOS v1.1.0 Extension Active! 🚀 Mission System & User Companions Ready',
        'Quick Setup',
        'System Status',
        'Show Commands'
    ).then(selection => {
        switch (selection) {
            case 'Quick Setup':
                vscode.commands.executeCommand('udos.quickSetup');
                break;
            case 'System Status':
                vscode.commands.executeCommand('udos.systemStatus');
                break;
            case 'Show Commands':
                vscode.commands.executeCommand('workbench.action.showCommands');
                break;
        }
    });
}

// ===== UTILITY FUNCTIONS =====

async function runUDOSCommand(command: string) {
    const terminal = vscode.window.createTerminal('uDOS Shell');
    terminal.sendText(`./uCode/ucode.sh`);
    terminal.sendText(command);
    terminal.show();
}

function runUDOSScript(scriptPath: string, args: string[]) {
    const terminal = vscode.window.createTerminal('uDOS Script');
    const argString = args.map(arg => `"${arg}"`).join(' ');
    terminal.sendText(`${scriptPath} ${argString}`);
    terminal.show();
}

export function deactivate() {
    console.log('uDOS v1.1.0 extension deactivated');
}

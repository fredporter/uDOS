"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const completion_1 = require("./providers/completion");
const hover_1 = require("./providers/hover");
const executor_1 = require("./commands/executor");
const knowledge_checker_1 = require("./commands/knowledge-checker");
const image_validator_1 = require("./commands/image-validator");
function activate(context) {
    console.log('uDOS Language Support extension is now active');
    // Register language providers
    const upySelector = { language: 'upy', scheme: 'file' };
    // Completion provider (IntelliSense)
    context.subscriptions.push(vscode.languages.registerCompletionItemProvider(upySelector, new completion_1.UPYCompletionProvider(), '.', // Trigger on dot for $VARIABLE.PROPERTY
    ' ' // Trigger on space for command completion
    ));
    // Hover provider (documentation)
    context.subscriptions.push(vscode.languages.registerHoverProvider(upySelector, new hover_1.UPYHoverProvider()));
    // Register commands
    context.subscriptions.push(vscode.commands.registerCommand('udos.runScript', () => (0, executor_1.runScript)(context)), vscode.commands.registerCommand('udos.runInSandbox', () => (0, executor_1.runInSandbox)(context)), vscode.commands.registerCommand('udos.checkKnowledgeQuality', () => (0, knowledge_checker_1.checkKnowledgeQuality)(context)), vscode.commands.registerCommand('udos.previewSVG', (uri) => (0, image_validator_1.previewSVG)(uri)), vscode.commands.registerCommand('udos.previewASCII', () => (0, image_validator_1.previewASCII)()), vscode.commands.registerCommand('udos.validateTeletext', () => (0, image_validator_1.validateTeletext)()));
    // Status bar
    const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.text = '$(beaker) uDOS';
    statusBarItem.tooltip = 'uDOS Extension Active';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);
}
function deactivate() {
    console.log('uDOS Language Support extension is now deactivated');
}
//# sourceMappingURL=extension.js.map
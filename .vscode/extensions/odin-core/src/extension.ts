import * as vscode from 'vscode';
import { OdinStatusProvider } from './statusProvider';
import { OdinCommandHandler } from './commandHandler';
import { OdinCliWrapper } from './cliWrapper';

export function activate(context: vscode.ExtensionContext) {
    console.log('ODIN Core extension is now active!');

    // Initialize core components
    const cliWrapper = new OdinCliWrapper();
    const statusProvider = new OdinStatusProvider(cliWrapper);
    const commandHandler = new OdinCommandHandler(cliWrapper, statusProvider);

    // Register the tree data provider for the ODIN status view
    vscode.window.createTreeView('odin-status', {
        treeDataProvider: statusProvider,
        showCollapseAll: true
    });

    // Register commands
    const commands = [
        vscode.commands.registerCommand('odin.audit', () => commandHandler.runAudit()),
        vscode.commands.registerCommand('odin.rollback', () => commandHandler.runRollback()),
        vscode.commands.registerCommand('odin.testgen', () => commandHandler.runTestGen()),
        vscode.commands.registerCommand('odin.openLearningLog', () => commandHandler.openLearningLog()),
        vscode.commands.registerCommand('odin.refreshStatus', () => statusProvider.refresh())
    ];

    // Add all commands to subscriptions
    commands.forEach(command => context.subscriptions.push(command));

    // Set up file system watcher for .odin directory changes
    const odinWatcher = vscode.workspace.createFileSystemWatcher('**/.odin/**/*');
    
    odinWatcher.onDidChange(() => {
        const config = vscode.workspace.getConfiguration('odin');
        if (config.get('autoRefresh', true)) {
            statusProvider.refresh();
        }
    });

    odinWatcher.onDidCreate(() => {
        const config = vscode.workspace.getConfiguration('odin');
        if (config.get('autoRefresh', true)) {
            statusProvider.refresh();
        }
    });

    odinWatcher.onDidDelete(() => {
        const config = vscode.workspace.getConfiguration('odin');
        if (config.get('autoRefresh', true)) {
            statusProvider.refresh();
        }
    });

    context.subscriptions.push(odinWatcher);

    // Set up auto-refresh timer
    const config = vscode.workspace.getConfiguration('odin');
    const refreshInterval = config.get('refreshInterval', 5000);
    
    if (config.get('autoRefresh', true)) {
        const refreshTimer = setInterval(() => {
            statusProvider.refresh();
        }, refreshInterval);

        // Clear timer when extension is deactivated
        context.subscriptions.push({
            dispose: () => clearInterval(refreshTimer)
        });
    }

    // Show welcome message if .odin directory exists
    if (vscode.workspace.workspaceFolders) {
        const odinExists = vscode.workspace.workspaceFolders.some(folder => {
            const odinPath = vscode.Uri.joinPath(folder.uri, '.odin');
            return vscode.workspace.fs.stat(odinPath).then(() => true, () => false);
        });

        if (odinExists) {
            vscode.window.showInformationMessage(
                'ODIN Core extension activated! Check the ODIN sidebar for project status.',
                'Open Sidebar'
            ).then(selection => {
                if (selection === 'Open Sidebar') {
                    vscode.commands.executeCommand('workbench.view.extension.odin');
                }
            });
        }
    }
}

export function deactivate() {
    console.log('ODIN Core extension deactivated');
}

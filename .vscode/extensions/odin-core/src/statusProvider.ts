import * as vscode from 'vscode';
import { OdinCliWrapper, OdinStatus } from './cliWrapper';

export class OdinStatusProvider implements vscode.TreeDataProvider<StatusItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<StatusItem | undefined | null | void> = new vscode.EventEmitter<StatusItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<StatusItem | undefined | null | void> = this._onDidChangeTreeData.event;

    private cliWrapper: OdinCliWrapper;

    constructor(cliWrapper: OdinCliWrapper) {
        this.cliWrapper = cliWrapper;
    }

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: StatusItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: StatusItem): Thenable<StatusItem[]> {
        if (element) {
            return Promise.resolve([]);
        } else {
            return this.getOdinStatus();
        }
    }

    private async getOdinStatus(): Promise<StatusItem[]> {
        const status = await this.cliWrapper.getStatus();
        if (!status) {
            vscode.window.showErrorMessage('Failed to retrieve ODIN status. Make sure ODIN is initialized properly.');
            return Promise.resolve([]);
        }

        return Promise.resolve([ 
            new StatusItem('Version', status.version, vscode.TreeItemCollapsibleState.None),
            new StatusItem('Last Action', status.last_action, vscode.TreeItemCollapsibleState.None),
            new StatusItem('Current State', status.current_state, vscode.TreeItemCollapsibleState.None),
            new StatusItem('Binary SHA-256', status.integrity.binary_sha256, vscode.TreeItemCollapsibleState.None),
            new StatusItem('Semantic Hash', status.integrity.semantic_hash, vscode.TreeItemCollapsibleState.None),
            new StatusItem('Test Coverage', `${status.test_coverage}%`, vscode.TreeItemCollapsibleState.None)
        ]);
    }
}

class StatusItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        private value: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState
    ) {
        super(label, collapsibleState);
        this.description = value;
    }

    contextValue = 'statusItem';
}

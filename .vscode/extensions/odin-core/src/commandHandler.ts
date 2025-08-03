import * as vscode from 'vscode';
import { OdinCliWrapper } from './cliWrapper';
import { OdinStatusProvider } from './statusProvider';

export class OdinCommandHandler {
    private cliWrapper: OdinCliWrapper;
    private statusProvider: OdinStatusProvider;

    constructor(cliWrapper: OdinCliWrapper, statusProvider: OdinStatusProvider) {
        this.cliWrapper = cliWrapper;
        this.statusProvider = statusProvider;
    }

    async runAudit() {
        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Running ODIN Audit...'
        }, async () => {
            const result = await this.cliWrapper.runAudit();
            if (result) {
                vscode.window.showInformationMessage(`Audit complete. Coverage: ${result.tests.coverage}%, CVEs: ${result.security.cves_detected}`);
                this.statusProvider.refresh();
            } else {
                vscode.window.showErrorMessage('ODIN audit failed. See console for details.');
            }
        });
    }

    async runRollback() {
        const confirm = await vscode.window.showWarningMessage(
            'Are you sure you want to rollback to the last checkpoint?',
            { modal: true },
            'Roll Back'
        );

        if (confirm === 'Roll Back') {
            const success = await this.cliWrapper.runRollback();
            if (success) {
                vscode.window.showInformationMessage('Rollback to last checkpoint was successful.');
                this.statusProvider.refresh();
            } else {
                vscode.window.showErrorMessage('Failed to rollback to last checkpoint. See console for details.');
            }
        }
    }

    async runTestGen(targetFile?: string) {
        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Generating Tests...'
        }, async () => {
            const success = await this.cliWrapper.runTestGen(targetFile);
            if (success) {
                vscode.window.showInformationMessage('Test generation complete.');
                this.statusProvider.refresh();
            } else {
                vscode.window.showErrorMessage('Failed to generate tests. See console for details.');
            }
        });
    }

    async openLearningLog() {
        const logPath = await this.cliWrapper.getLearningLogPath();
        if (logPath) {
            const document = await vscode.workspace.openTextDocument(logPath);
            vscode.window.showTextDocument(document);
        } else {
            vscode.window.showErrorMessage('Learning log not found.');
        }
    }
}

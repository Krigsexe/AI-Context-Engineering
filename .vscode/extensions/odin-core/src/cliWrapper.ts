import * as vscode from 'vscode';
import * as cp from 'child_process';
import * as path from 'path';
import * as fs from 'fs';

export interface OdinStatus {
    version: string;
    timestamp: string;
    current_state: string;
    last_action: string;
    integrity: {
        binary_sha256: string;
        semantic_hash: string;
    };
    context: {
        language: string;
        framework: string;
        architecture: string;
    };
    backup_ref: string;
    test_coverage: number;
}

export interface OdinAuditResult {
    integrity: {
        sha256: string;
        sih: string;
        last_rollback: string;
    };
    tests: {
        coverage: number;
        last_failure: string;
        untested_functions: number;
    };
    documentation: {
        documented_functions: number;
        readme_updated: boolean;
        changelog_updated: boolean;
    };
    security: {
        critical_dependencies: number;
        cves_detected: number;
        outdated_packages: number;
    };
    recommendations: string[];
}

export class OdinCliWrapper {
    private cliPath: string;

    constructor() {
        const config = vscode.workspace.getConfiguration('odin');
        this.cliPath = config.get('cliPath', 'odin');
    }

    private getWorkspaceRoot(): string | undefined {
        if (vscode.workspace.workspaceFolders && vscode.workspace.workspaceFolders.length > 0) {
            return vscode.workspace.workspaceFolders[0].uri.fsPath;
        }
        return undefined;
    }

    private async execOdinCommand(args: string[]): Promise<string> {
        return new Promise((resolve, reject) => {
            const workspaceRoot = this.getWorkspaceRoot();
            if (!workspaceRoot) {
                reject(new Error('No workspace folder found'));
                return;
            }

            const command = `${this.cliPath} ${args.join(' ')}`;
            
            cp.exec(command, { 
                cwd: workspaceRoot,
                timeout: 30000 // 30 second timeout
            }, (error, stdout, stderr) => {
                if (error) {
                    console.error(`ODIN CLI error: ${error.message}`);
                    console.error(`stderr: ${stderr}`);
                    reject(new Error(`ODIN CLI failed: ${error.message}`));
                    return;
                }
                
                if (stderr) {
                    console.warn(`ODIN CLI warning: ${stderr}`);
                }
                
                resolve(stdout.trim());
            });
        });
    }

    async getStatus(): Promise<OdinStatus | null> {
        try {
            const workspaceRoot = this.getWorkspaceRoot();
            if (!workspaceRoot) {
                return null;
            }

            const checkpointPath = path.join(workspaceRoot, '.odin', 'AI_CHECKPOINT.json');
            
            if (!fs.existsSync(checkpointPath)) {
                return null;
            }

            const checkpointData = fs.readFileSync(checkpointPath, 'utf8');
            return JSON.parse(checkpointData) as OdinStatus;
        } catch (error) {
            console.error('Failed to read ODIN status:', error);
            return null;
        }
    }

    async runAudit(): Promise<OdinAuditResult | null> {
        try {
            const output = await this.execOdinCommand(['audit', '--json']);
            return JSON.parse(output) as OdinAuditResult;
        } catch (error) {
            console.error('Failed to run ODIN audit:', error);
            return null;
        }
    }

    async runRollback(): Promise<boolean> {
        try {
            await this.execOdinCommand(['rollback']);
            return true;
        } catch (error) {
            console.error('Failed to run ODIN rollback:', error);
            return false;
        }
    }

    async runTestGen(targetFile?: string): Promise<boolean> {
        try {
            const args = ['testgen'];
            if (targetFile) {
                args.push('--file', targetFile);
            }
            await this.execOdinCommand(args);
            return true;
        } catch (error) {
            console.error('Failed to run ODIN testgen:', error);
            return false;
        }
    }

    async isOdinProject(): Promise<boolean> {
        try {
            const workspaceRoot = this.getWorkspaceRoot();
            if (!workspaceRoot) {
                return false;
            }

            const odinDir = path.join(workspaceRoot, '.odin');
            return fs.existsSync(odinDir);
        } catch (error) {
            return false;
        }
    }

    async getLearningLogPath(): Promise<string | null> {
        try {
            const workspaceRoot = this.getWorkspaceRoot();
            if (!workspaceRoot) {
                return null;
            }

            const logPath = path.join(workspaceRoot, '.odin', 'learning_log.json');
            return fs.existsSync(logPath) ? logPath : null;
        } catch (error) {
            return null;
        }
    }

    async getAuditReportPath(): Promise<string | null> {
        try {
            const workspaceRoot = this.getWorkspaceRoot();
            if (!workspaceRoot) {
                return null;
            }

            const reportPath = path.join(workspaceRoot, '.odin', 'audit_report.md');
            return fs.existsSync(reportPath) ? reportPath : null;
        } catch (error) {
            return null;
        }
    }

    async getLastBackupInfo(): Promise<{ count: number; lastBackup: string | null }> {
        try {
            const workspaceRoot = this.getWorkspaceRoot();
            if (!workspaceRoot) {
                return { count: 0, lastBackup: null };
            }

            const backupsDir = path.join(workspaceRoot, '.odin', 'backups');
            if (!fs.existsSync(backupsDir)) {
                return { count: 0, lastBackup: null };
            }

            const backupFiles = fs.readdirSync(backupsDir)
                .filter(file => file.endsWith('.bak.json'))
                .sort((a, b) => b.localeCompare(a)); // Sort by name descending (newest first)

            return {
                count: backupFiles.length,
                lastBackup: backupFiles.length > 0 ? backupFiles[0] : null
            };
        } catch (error) {
            console.error('Failed to get backup info:', error);
            return { count: 0, lastBackup: null };
        }
    }
}

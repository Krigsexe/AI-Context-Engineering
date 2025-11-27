import fs from 'fs-extra'
import path from 'path'
import yaml from 'yaml'
import type { DevEnvironment, OdinConfig } from '../types/index.js'
import { getOdinPath } from './detector.js'
import { ORCHESTRATOR_TEMPLATE, AGENT_TEMPLATES, RULE_TEMPLATES } from './templates.js'

/**
 * Patch structure to inject into user's project
 */
export class OdinPatcher {
    private projectPath: string
    private environment: DevEnvironment
    private odinPath: string

    constructor(projectPath: string, environment: DevEnvironment) {
        this.projectPath = projectPath
        this.environment = environment
        this.odinPath = getOdinPath(projectPath, environment)
    }

    /**
     * Create the complete ODIN directory structure
     */
    async createStructure(config: OdinConfig): Promise<void> {
        const dirs = [
            this.odinPath,
            `${this.odinPath}/rules`,
            `${this.odinPath}/agents`,
            `${this.odinPath}/db`,
            `${this.odinPath}/memory-bank`,
            `${this.odinPath}/archives`,
            `${this.odinPath}/index`,
            `${this.odinPath}/security`
        ]

        for (const dir of dirs) {
            await fs.ensureDir(dir)
        }

        // Write config file
        await this.writeConfig(config)

        // Create orchestrator markdown
        await this.writeOrchestrator()

        // Create .gitkeep files
        await fs.writeFile(`${this.odinPath}/archives/.gitkeep`, '')
        await fs.writeFile(`${this.odinPath}/memory-bank/.gitkeep`, '')
    }

    /**
     * Write config.yaml
     */
    private async writeConfig(config: OdinConfig): Promise<void> {
        const configPath = path.join(this.odinPath, 'config.yaml')
        const yamlContent = yaml.stringify(config)
        await fs.writeFile(configPath, yamlContent, 'utf-8')
    }

    /**
     * Get installation summary
     */
    getSummary(): string {
        return `
✳ ODIN Framework installed successfully!

Location: ${this.odinPath}
Environment: ${this.environment}

Structure created:
  ├── config.yaml           # LLM provider configuration
  ├── orchestrator.md       # Main orchestrator agent
  ├── rules/                # Architecture rules
  ├── agents/               # Agent definitions
  ├── db/                   # Local SQLite database
  ├── memory-bank/          # Persistent context
  ├── archives/             # Session history
  ├── index/                # Semantic index
  └── security/             # Security policies

Next steps:
  1. Review config.yaml and customize if needed
  2. Add project-specific rules to rules/
  3. Start using: Your AI assistant now has ODIN context!

Commands:
  odin status              # Check ODIN status
  odin config              # View/edit configuration
  odin agents              # List available agents
  odin sync                # Sync with latest ODIN framework
`
    }
}

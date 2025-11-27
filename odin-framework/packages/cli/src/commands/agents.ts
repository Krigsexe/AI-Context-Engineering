import { Command } from 'commander'
import pc from 'picocolors'
import path from 'path'
import fs from 'fs-extra'
import yaml from 'yaml'
import { glob } from 'glob'
import { detectEnvironment, getOdinPath, isOdinInstalled } from '../utils/detector.js'
import type { AgentDefinition } from '../types/index.js'

export const agentsCommand = new Command('agents')
    .description('List and manage ODIN agents')
    .option('-p, --path <path>', 'Project path', process.cwd())
    .option('--verbose', 'Show detailed agent information')
    .action(async (options) => {
        const projectPath = path.resolve(options.path)

        if (!isOdinInstalled(projectPath)) {
            console.log(pc.red('✗ ODIN is not installed in this project.'))
            console.log(pc.gray('Run: odin init\n'))
            return
        }

        const detectedEnvs = detectEnvironment(projectPath)
        const odinPath = getOdinPath(projectPath, detectedEnvs[0].environment)
        const agentsPath = path.join(odinPath, 'agents')

        console.log(pc.cyan('\n✳ ODIN Agents\n'))

        const agentFiles = await glob('*.{yaml,yml}', { cwd: agentsPath })

        if (agentFiles.length === 0) {
            console.log(pc.yellow('No agents configured yet.'))
            console.log(pc.gray('Agents are defined in: ' + agentsPath + '\n'))
            return
        }

        const agents: AgentDefinition[] = []

        for (const file of agentFiles) {
            const filePath = path.join(agentsPath, file)
            const content = await fs.readFile(filePath, 'utf-8')
            const agent = yaml.parse(content) as AgentDefinition
            agents.push(agent)
        }

        // Group by type
        const grouped = agents.reduce((acc, agent) => {
            if (!acc[agent.type]) {
                acc[agent.type] = []
            }
            acc[agent.type].push(agent)
            return acc
        }, {} as Record<string, AgentDefinition[]>)

        const typeIcons = {
            cognitive: '🧠',
            oracle: '🔮',
            execution: '⚡',
            system: '🔧'
        }

        for (const [type, agentList] of Object.entries(grouped)) {
            const icon = typeIcons[type as keyof typeof typeIcons] || '📦'
            console.log(pc.bold(`${icon} ${type.toUpperCase()} AGENTS`))
            console.log()

            for (const agent of agentList) {
                console.log(pc.green(`  ✓ ${agent.name}`))
                console.log(pc.gray(`    ${agent.description}`))

                if (options.verbose) {
                    console.log(pc.gray(`    Tasks: ${agent.tasks.join(', ')}`))
                    console.log(pc.gray(`    Confidence: ${agent.confidence.min}%-${agent.confidence.max}%`))
                }

                console.log()
            }
        }

        console.log(pc.gray(`Total agents: ${agents.length}\n`))
    })

import { Command } from 'commander'
import pc from 'picocolors'
import path from 'path'
import fs from 'fs-extra'
import yaml from 'yaml'
import { detectEnvironment, getOdinPath, isOdinInstalled } from '../utils/detector.js'
import type { OdinConfig } from '../types/index.js'

export const configCommand = new Command('config')
    .description('View or edit ODIN configuration')
    .option('-p, --path <path>', 'Project path', process.cwd())
    .option('--show', 'Show current configuration')
    .option('--edit', 'Open configuration file in editor')
    .action(async (options) => {
        const projectPath = path.resolve(options.path)

        if (!isOdinInstalled(projectPath)) {
            console.log(pc.red('✗ ODIN is not installed in this project.'))
            console.log(pc.gray('Run: odin init\n'))
            return
        }

        const detectedEnvs = detectEnvironment(projectPath)
        const odinPath = getOdinPath(projectPath, detectedEnvs[0].environment)
        const configPath = path.join(odinPath, 'config.yaml')

        if (!fs.existsSync(configPath)) {
            console.log(pc.red('✗ Configuration file not found.'))
            return
        }

        const configContent = await fs.readFile(configPath, 'utf-8')
        const config: OdinConfig = yaml.parse(configContent)

        console.log(pc.cyan('\n✳ ODIN Configuration\n'))
        console.log(pc.gray(`Location: ${configPath}\n`))

        console.log(pc.bold('Provider:'), pc.green(config.provider))
        console.log(pc.bold('Model:'), config.model)
        if (config.baseUrl) {
            console.log(pc.bold('Base URL:'), config.baseUrl)
        }
        console.log(pc.bold('Temperature:'), config.temperature)
        console.log(pc.bold('Max Tokens:'), config.maxTokens)
        console.log(pc.bold('Database:'), config.database.path)

        console.log(pc.bold('\nPaths:'))
        console.log(pc.gray(`  Rules:       ${config.paths.rules}`))
        console.log(pc.gray(`  Agents:      ${config.paths.agents}`))
        console.log(pc.gray(`  Memory Bank: ${config.paths.memoryBank}`))
        console.log(pc.gray(`  Archives:    ${config.paths.archives}`))
        console.log(pc.gray(`  Index:       ${config.paths.index}`))

        console.log()
    })

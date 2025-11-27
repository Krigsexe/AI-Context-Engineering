import { Command } from 'commander'
import pc from 'picocolors'
import path from 'path'
import fs from 'fs-extra'
import yaml from 'yaml'
import { detectEnvironment, getOdinPath, isOdinInstalled } from '../utils/detector.js'
import { OdinDatabase, createDatabase } from '../utils/database.js'
import type { OdinConfig } from '../types/index.js'

export const statusCommand = new Command('status')
    .description('Check ODIN installation status')
    .option('-p, --path <path>', 'Project path', process.cwd())
    .action(async (options) => {
        const projectPath = path.resolve(options.path)

        console.log(pc.cyan('\n✳ ODIN Status\n'))

        // Check if installed
        const installed = isOdinInstalled(projectPath)

        if (!installed) {
            console.log(pc.red('✗ ODIN is not installed in this project.'))
            console.log(pc.gray('\nRun: odin init\n'))
            return
        }

        console.log(pc.green('✓ ODIN is installed\n'))

        // Get details
        const detectedEnvs = detectEnvironment(projectPath)
        const env = detectedEnvs[0]
        const odinPath = getOdinPath(projectPath, env.environment)

        console.log(pc.bold('Environment:'), env.environment)
        console.log(pc.bold('Location:'), odinPath)
        console.log()

        // Check required directories
        const requiredDirs = [
            'rules',
            'agents',
            'db',
            'memory-bank',
            'archives',
            'index'
        ]

        console.log(pc.bold('Structure:'))
        for (const dir of requiredDirs) {
            const dirPath = path.join(odinPath, dir)
            const exists = fs.existsSync(dirPath)
            const icon = exists ? pc.green('✓') : pc.red('✗')
            console.log(`  ${icon} ${dir}/`)
        }
        console.log()

        // Load config
        const configPath = path.join(odinPath, 'config.yaml')
        if (fs.existsSync(configPath)) {
            const configContent = await fs.readFile(configPath, 'utf-8')
            const config: OdinConfig = yaml.parse(configContent)

            console.log(pc.bold('Configuration:'))
            console.log(pc.gray(`  Provider: ${config.provider}`))
            console.log(pc.gray(`  Model: ${config.model}`))
            console.log(pc.gray(`  Version: ${config.version}`))
            console.log()
        }

        // Database stats
        const dbPath = path.join(odinPath, 'db', 'odin.db')
        if (fs.existsSync(dbPath)) {
            try {
                const db = await createDatabase(dbPath)
                const stats = db.getStats()

                console.log(pc.bold('Database:'))
                console.log(pc.gray(`  Memories: ${stats.memories}`))
                console.log(pc.gray(`  Indexed files: ${stats.indexed}`))
                console.log(pc.gray(`  Archived events: ${stats.archives}`))

                db.close()
            } catch (e) {
                console.log(pc.yellow('  ⚠ Database error'))
            }
        }

        console.log()
    })

import { Command } from 'commander'
import inquirer from 'inquirer'
import ora from 'ora'
import pc from 'picocolors'
import path from 'path'
import {
    detectEnvironment,
    isOdinInstalled,
    getProjectInfo,
    getOdinPath
} from '../utils/detector.js'
import {
    getAvailableProviders,
    createDefaultConfig,
    requiresApiKey,
    getProviderApiKey
} from '../utils/providers.js'
import { OdinPatcher } from '../utils/patcher.js'
import { OdinDatabase, createDatabase } from '../utils/database.js'
import type { LLMProvider } from '../types/index.js'

export const initCommand = new Command('init')
    .description('Initialize ODIN in your project')
    .option('-p, --path <path>', 'Project path', process.cwd())
    .option('--provider <provider>', 'LLM provider to use')
    .option('--force', 'Force reinstall even if already installed')
    .action(async (options) => {
        const projectPath = path.resolve(options.path)

        console.log(pc.cyan('\n✳ ODIN Framework Initialization\n'))

        // Check if already installed
        if (isOdinInstalled(projectPath) && !options.force) {
            console.log(pc.yellow('⚠ ODIN is already installed in this project.'))
            console.log(pc.gray('Use --force to reinstall.\n'))
            return
        }

        // Detect environment
        const spinner = ora('Detecting development environment...').start()
        const detectedEnvs = detectEnvironment(projectPath)
        const projectInfo = getProjectInfo(projectPath)
        spinner.succeed(`Detected: ${pc.bold(detectedEnvs[0].environment)}`)

        console.log(pc.gray(`Project: ${projectInfo.name}`))
        console.log(pc.gray(`Path: ${projectPath}\n`))

        // Select LLM provider
        let selectedProvider: LLMProvider

        if (options.provider) {
            selectedProvider = options.provider as LLMProvider
        } else {
            const providers = getAvailableProviders()

            const { provider } = await inquirer.prompt([
                {
                    type: 'list',
                    name: 'provider',
                    message: 'Select LLM provider:',
                    choices: providers.map(p => ({
                        name: `${p.label}${p.local ? ' 🏠' : ' ☁️'}`,
                        value: p.name
                    })),
                    default: 'ollama'
                }
            ])

            selectedProvider = provider
        }

        // Check API key if required
        if (requiresApiKey(selectedProvider)) {
            const apiKey = getProviderApiKey(selectedProvider)

            if (!apiKey) {
                console.log(pc.yellow(`\n⚠ ${selectedProvider.toUpperCase()} requires an API key.`))
                console.log(pc.gray(`Set it in your environment: export ${selectedProvider.toUpperCase()}_API_KEY="your-key"\n`))

                const { proceed } = await inquirer.prompt([
                    {
                        type: 'confirm',
                        name: 'proceed',
                        message: 'Continue without API key? (You can set it later)',
                        default: false
                    }
                ])

                if (!proceed) {
                    return
                }
            }
        }

        // Create ODIN structure
        spinner.text = 'Creating ODIN structure...'
        spinner.start()

        const env = detectedEnvs[0].environment
        const odinPath = getOdinPath(projectPath, env)
        const config = createDefaultConfig(selectedProvider, odinPath)

        const patcher = new OdinPatcher(projectPath, env)

        try {
            await patcher.createStructure(config)
            await patcher.createSampleRules()
            await patcher.createAgentDefinitions()

            // Initialize database
            const db = await createDatabase(config.database.path)
            db.storeMemory({
                key: 'odin.initialized',
                value: new Date().toISOString(),
                category: 'system',
                timestamp: Date.now(),
                confidence: 1.0
            })
            db.storeMemory({
                key: 'project.name',
                value: projectInfo.name,
                category: 'project',
                timestamp: Date.now(),
                confidence: 1.0
            })
            db.close()

            spinner.succeed('ODIN framework installed!')

            console.log(patcher.getSummary())

        } catch (error) {
            spinner.fail('Installation failed')
            console.error(pc.red((error as Error).message))
        }
    })

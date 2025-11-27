#!/usr/bin/env node
import { Command } from 'commander'
import pc from 'picocolors'
import { initCommand } from './commands/init.js'
import { configCommand } from './commands/config.js'
import { agentsCommand } from './commands/agents.js'
import { statusCommand } from './commands/status.js'
import { syncCommand } from './commands/sync.js'
import { ODIN_VERSION } from './utils/constants.js'

const program = new Command()

// ASCII Art
const banner = `
${pc.cyan('╔═══════════════════════════════════════════════════════════════╗')}
${pc.cyan('║')}           ${pc.bold(pc.cyan('✳') + ' ODIN - Context Engineering Framework')}          ${pc.cyan('║')}
${pc.cyan('║')}     ${pc.gray('Orchestrated Development Intelligence Network')}         ${pc.cyan('║')}
${pc.cyan('╚═══════════════════════════════════════════════════════════════╝')}
`

program
    .name('odin')
    .description(banner + '\n' + pc.gray('Multi-Agent Orchestration for Reliable AI Development'))
    .version(ODIN_VERSION, '-v, --version', 'Output the current version')
    .addHelpText('beforeAll', banner)

// Add commands
program.addCommand(initCommand)
program.addCommand(statusCommand)
program.addCommand(configCommand)
program.addCommand(agentsCommand)
program.addCommand(syncCommand)

// Custom help
program.on('--help', () => {
    console.log()
    console.log(pc.bold('Quick Start:'))
    console.log(pc.gray('  $ odin init              # Initialize ODIN in your project'))
    console.log(pc.gray('  $ odin status            # Check installation status'))
    console.log(pc.gray('  $ odin agents            # List available agents'))
    console.log()
    console.log(pc.bold('Documentation:'))
    console.log(pc.gray('  https://github.com/Krigsexe/AI-Context-Engineering'))
    console.log()
})

// Parse arguments
program.parse()

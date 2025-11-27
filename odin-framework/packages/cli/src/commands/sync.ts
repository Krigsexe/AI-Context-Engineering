import { Command } from 'commander'
import pc from 'picocolors'

export const syncCommand = new Command('sync')
    .description('Sync ODIN with latest framework version')
    .option('-p, --path <path>', 'Project path', process.cwd())
    .action(async (options) => {
        console.log(pc.cyan('\n✳ ODIN Sync\n'))
        console.log(pc.yellow('Sync functionality coming soon!'))
        console.log(pc.gray('This will update your ODIN installation with the latest rules and agents.\n'))
    })

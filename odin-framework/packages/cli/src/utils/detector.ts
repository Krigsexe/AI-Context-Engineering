import fs from 'fs'
import path from 'path'
import type { DevEnvironment, DetectionResult } from '../types/index.js'
import { ENV_PATTERNS, ODIN_DIRECTORIES } from './constants.js'

/**
 * Detect which dev environment/AI tool is being used in the project
 */
export function detectEnvironment(projectPath: string = process.cwd()): DetectionResult[] {
    const results: DetectionResult[] = []

    for (const [env, patterns] of Object.entries(ENV_PATTERNS)) {
        for (const pattern of patterns) {
            const fullPath = path.join(projectPath, pattern)
            const exists = fs.existsSync(fullPath)

            if (exists || pattern.startsWith('.')) {
                results.push({
                    environment: env as DevEnvironment,
                    configPath: fullPath,
                    exists
                })
                break
            }
        }
    }

    return results.length > 0 ? results : [{
        environment: 'unknown',
        configPath: projectPath,
        exists: false
    }]
}

/**
 * Get the ODIN installation path based on detected environment
 */
export function getOdinPath(projectPath: string, env: DevEnvironment): string {
    const basePath = ODIN_DIRECTORIES[env] || ODIN_DIRECTORIES.unknown
    return path.join(projectPath, basePath)
}

/**
 * Check if ODIN is already installed in the project
 */
export function isOdinInstalled(projectPath: string): boolean {
    const detectedEnvs = detectEnvironment(projectPath)

    for (const env of detectedEnvs) {
        const odinPath = getOdinPath(projectPath, env.environment)
        if (fs.existsSync(odinPath)) {
            return true
        }
    }

    return false
}

/**
 * Get project metadata
 */
export function getProjectInfo(projectPath: string): {
    name: string
    hasPackageJson: boolean
    hasPyprojectToml: boolean
    hasGit: boolean
} {
    const packageJsonPath = path.join(projectPath, 'package.json')
    const pyprojectPath = path.join(projectPath, 'pyproject.toml')
    const gitPath = path.join(projectPath, '.git')

    let name = path.basename(projectPath)

    if (fs.existsSync(packageJsonPath)) {
        try {
            const pkg = JSON.parse(fs.readFileSync(packageJsonPath, 'utf-8'))
            name = pkg.name || name
        } catch (e) {
            // ignore
        }
    }

    return {
        name,
        hasPackageJson: fs.existsSync(packageJsonPath),
        hasPyprojectToml: fs.existsSync(pyprojectPath),
        hasGit: fs.existsSync(gitPath)
    }
}

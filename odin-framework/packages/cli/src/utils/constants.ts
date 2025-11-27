export const ODIN_VERSION = '1.0.0'

export const DEFAULT_PROVIDERS = {
    ollama: {
        baseUrl: 'http://localhost:11434',
        models: ['qwen2.5:7b', 'llama3.1:8b', 'codellama:7b']
    },
    anthropic: {
        baseUrl: 'https://api.anthropic.com',
        models: ['claude-3-5-sonnet-20241022', 'claude-3-opus-20240229']
    },
    openai: {
        baseUrl: 'https://api.openai.com/v1',
        models: ['gpt-4-turbo', 'gpt-4o', 'gpt-3.5-turbo']
    },
    google: {
        baseUrl: 'https://generativelanguage.googleapis.com',
        models: ['gemini-2.0-flash-exp', 'gemini-1.5-pro']
    },
    groq: {
        baseUrl: 'https://api.groq.com/openai/v1',
        models: ['llama-3.3-70b-versatile', 'mixtral-8x7b-32768']
    },
    mistral: {
        baseUrl: 'https://api.mistral.ai',
        models: ['mistral-large-latest', 'mistral-medium-latest']
    }
} as const

export const ENV_PATTERNS: Record<string, string[]> = {
    claude: ['.claude', 'CLAUDE.md'],
    cursor: ['.cursor', '.cursorrules'],
    windsurf: ['.windsurf', '.windsurfrules'],
    aider: ['.aider.conf.yml', '.aider'],
    continue: ['.continue'],
    cline: ['.cline'],
    'roo-cline': ['.roo-cline']
}

export const ODIN_DIRECTORIES = {
    claude: '.claude/odin',
    cursor: '.cursor/odin',
    windsurf: '.windsurf/odin',
    aider: '.aider/odin',
    continue: '.continue/odin',
    cline: '.cline/odin',
    'roo-cline': '.roo-cline/odin',
    unknown: '.odin'
} as const

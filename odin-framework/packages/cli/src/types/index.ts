export type DevEnvironment =
    | 'claude'
    | 'cursor'
    | 'windsurf'
    | 'aider'
    | 'continue'
    | 'cline'
    | 'roo-cline'
    | 'unknown'

export type LLMProvider =
    | 'ollama'
    | 'anthropic'
    | 'openai'
    | 'google'
    | 'groq'
    | 'grok'
    | 'mistral'
    | 'together'
    | 'deepseek'
    | 'huggingface'

export interface DetectionResult {
    environment: DevEnvironment
    configPath: string
    exists: boolean
}

export interface OdinConfig {
    version: string
    provider: LLMProvider
    model: string
    apiKey?: string
    baseUrl?: string
    temperature: number
    maxTokens: number
    database: {
        path: string
        type: 'sqlite'
    }
    paths: {
        rules: string
        agents: string
        memoryBank: string
        archives: string
        index: string
    }
}

export interface AgentDefinition {
    name: string
    type: 'cognitive' | 'oracle' | 'execution' | 'system'
    description: string
    tasks: string[]
    confidence: {
        min: number
        max: number
    }
}

import type { LLMProvider, OdinConfig } from '../types/index.js'
import { DEFAULT_PROVIDERS, ODIN_VERSION } from './constants.js'

/**
 * Get provider configuration
 */
export function getProviderConfig(provider: LLMProvider) {
    return DEFAULT_PROVIDERS[provider] || null
}

/**
 * Create default ODIN configuration
 */
export function createDefaultConfig(provider: LLMProvider, odinPath: string): OdinConfig {
    const providerConfig = getProviderConfig(provider)

    return {
        version: ODIN_VERSION,
        provider,
        model: providerConfig?.models[0] || '',
        baseUrl: providerConfig?.baseUrl,
        temperature: 0.3,
        maxTokens: 4096,
        database: {
            path: `${odinPath}/db/odin.db`,
            type: 'sqlite'
        },
        paths: {
            rules: `${odinPath}/rules`,
            agents: `${odinPath}/agents`,
            memoryBank: `${odinPath}/memory-bank`,
            archives: `${odinPath}/archives`,
            index: `${odinPath}/index`
        }
    }
}

/**
 * Validate provider API key from environment
 */
export function getProviderApiKey(provider: LLMProvider): string | undefined {
    const envVarMap: Record<LLMProvider, string> = {
        ollama: '', // No API key needed for local
        anthropic: 'ANTHROPIC_API_KEY',
        openai: 'OPENAI_API_KEY',
        google: 'GOOGLE_API_KEY',
        groq: 'GROQ_API_KEY',
        grok: 'GROK_API_KEY',
        mistral: 'MISTRAL_API_KEY',
        together: 'TOGETHER_API_KEY',
        deepseek: 'DEEPSEEK_API_KEY',
        huggingface: 'HUGGINGFACE_API_KEY'
    }

    const envVar = envVarMap[provider]
    return envVar ? process.env[envVar] : undefined
}

/**
 * Check if provider requires API key
 */
export function requiresApiKey(provider: LLMProvider): boolean {
    return provider !== 'ollama'
}

/**
 * Get all available providers
 */
export function getAvailableProviders(): Array<{
    name: LLMProvider
    label: string
    local: boolean
    requiresKey: boolean
}> {
    return [
        { name: 'ollama', label: 'Ollama (Local)', local: true, requiresKey: false },
        { name: 'anthropic', label: 'Anthropic (Claude)', local: false, requiresKey: true },
        { name: 'openai', label: 'OpenAI (GPT)', local: false, requiresKey: true },
        { name: 'google', label: 'Google (Gemini)', local: false, requiresKey: true },
        { name: 'groq', label: 'Groq (Fast Inference)', local: false, requiresKey: true },
        { name: 'grok', label: 'xAI (Grok)', local: false, requiresKey: true },
        { name: 'mistral', label: 'Mistral AI', local: false, requiresKey: true },
        { name: 'together', label: 'Together AI', local: false, requiresKey: true },
        { name: 'deepseek', label: 'DeepSeek', local: false, requiresKey: true },
        { name: 'huggingface', label: 'HuggingFace', local: false, requiresKey: true }
    ]
}

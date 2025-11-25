// =============================================================================
// ODIN v7.0 - Configuration Package
// =============================================================================

package config

import (
	"fmt"
	"os"
	"path/filepath"

	"github.com/spf13/viper"
)

// Config holds all orchestrator configuration
type Config struct {
	// Database configuration
	Database DatabaseConfig `mapstructure:"database"`

	// Redis configuration
	Redis RedisConfig `mapstructure:"redis"`

	// LLM configuration
	LLM LLMConfig `mapstructure:"llm"`

	// Orchestrator settings
	Orchestrator OrchestratorConfig `mapstructure:"orchestrator"`

	// Agent configuration
	Agents AgentsConfig `mapstructure:"agents"`
}

// DatabaseConfig holds PostgreSQL settings
type DatabaseConfig struct {
	URL             string `mapstructure:"url"`
	MaxConnections  int    `mapstructure:"max_connections"`
	ConnTimeout     int    `mapstructure:"conn_timeout"`
}

// RedisConfig holds Redis settings
type RedisConfig struct {
	URL      string `mapstructure:"url"`
	Password string `mapstructure:"password"`
	DB       int    `mapstructure:"db"`
}

// LLMConfig holds LLM provider settings
type LLMConfig struct {
	Primary   ProviderConfig   `mapstructure:"primary"`
	Fallback  []ProviderConfig `mapstructure:"fallback"`
	Consensus ConsensusConfig  `mapstructure:"consensus"`
}

// ProviderConfig holds individual provider settings
type ProviderConfig struct {
	Provider string `mapstructure:"provider"`
	Model    string `mapstructure:"model"`
	APIKey   string `mapstructure:"api_key"`
	BaseURL  string `mapstructure:"base_url"`
}

// ConsensusConfig holds consensus verification settings
type ConsensusConfig struct {
	Enabled      bool             `mapstructure:"enabled"`
	MinAgreement float64          `mapstructure:"min_agreement"`
	Providers    []ProviderConfig `mapstructure:"providers"`
}

// OrchestratorConfig holds orchestrator behavior settings
type OrchestratorConfig struct {
	MaxConcurrentTasks int  `mapstructure:"max_concurrent_tasks"`
	TaskTimeout        int  `mapstructure:"task_timeout"`
	CheckpointEnabled  bool `mapstructure:"checkpoint_enabled"`
	AuditEnabled       bool `mapstructure:"audit_enabled"`
}

// AgentsConfig holds agent management settings
type AgentsConfig struct {
	AutoStart    bool     `mapstructure:"auto_start"`
	HealthCheck  int      `mapstructure:"health_check_interval"`
	Enabled      []string `mapstructure:"enabled"`
	ScaleFactors map[string]int `mapstructure:"scale_factors"`
}

// Load reads configuration from file and environment
func Load(cfgFile string) (*Config, error) {
	v := viper.New()

	// Set defaults
	setDefaults(v)

	// Config file handling
	if cfgFile != "" {
		v.SetConfigFile(cfgFile)
	} else {
		// Search paths
		v.SetConfigName("odin.config")
		v.SetConfigType("yaml")
		v.AddConfigPath(".")
		v.AddConfigPath("$HOME/.odin")
		v.AddConfigPath("/etc/odin")
	}

	// Environment variables
	v.SetEnvPrefix("ODIN")
	v.AutomaticEnv()

	// Read config
	if err := v.ReadInConfig(); err != nil {
		if _, ok := err.(viper.ConfigFileNotFoundError); ok {
			// Config file not found, use defaults
			fmt.Println("No config file found, using defaults")
		} else {
			return nil, fmt.Errorf("error reading config: %w", err)
		}
	}

	// Unmarshal
	var cfg Config
	if err := v.Unmarshal(&cfg); err != nil {
		return nil, fmt.Errorf("error parsing config: %w", err)
	}

	// Override with environment variables
	applyEnvOverrides(&cfg)

	return &cfg, nil
}

func setDefaults(v *viper.Viper) {
	// Database
	v.SetDefault("database.url", "postgresql://odin:odin@localhost:5432/odin")
	v.SetDefault("database.max_connections", 20)
	v.SetDefault("database.conn_timeout", 30)

	// Redis
	v.SetDefault("redis.url", "redis://localhost:6379")
	v.SetDefault("redis.db", 0)

	// LLM
	v.SetDefault("llm.primary.provider", "ollama")
	v.SetDefault("llm.primary.model", "qwen2.5:7b")
	v.SetDefault("llm.consensus.enabled", false)
	v.SetDefault("llm.consensus.min_agreement", 0.67)

	// Orchestrator
	v.SetDefault("orchestrator.max_concurrent_tasks", 10)
	v.SetDefault("orchestrator.task_timeout", 300)
	v.SetDefault("orchestrator.checkpoint_enabled", true)
	v.SetDefault("orchestrator.audit_enabled", true)

	// Agents
	v.SetDefault("agents.auto_start", true)
	v.SetDefault("agents.health_check_interval", 30)
	v.SetDefault("agents.enabled", []string{
		"intake", "retrieval", "dev", "oracle_code",
	})
}

func applyEnvOverrides(cfg *Config) {
	// Database
	if url := os.Getenv("ODIN_DATABASE_URL"); url != "" {
		cfg.Database.URL = url
	}

	// Redis
	if url := os.Getenv("ODIN_REDIS_URL"); url != "" {
		cfg.Redis.URL = url
	}

	// LLM Provider
	if provider := os.Getenv("ODIN_LLM_PROVIDER"); provider != "" {
		cfg.LLM.Primary.Provider = provider
	}
	if model := os.Getenv("ODIN_LLM_MODEL"); model != "" {
		cfg.LLM.Primary.Model = model
	}

	// Provider API keys from environment
	cfg.LLM.Primary.APIKey = getAPIKey(cfg.LLM.Primary.Provider)
}

func getAPIKey(provider string) string {
	envMap := map[string]string{
		"anthropic":  "ANTHROPIC_API_KEY",
		"openai":     "OPENAI_API_KEY",
		"google":     "GOOGLE_API_KEY",
		"groq":       "GROQ_API_KEY",
		"together":   "TOGETHER_API_KEY",
		"deepseek":   "DEEPSEEK_API_KEY",
	}

	if envVar, ok := envMap[provider]; ok {
		return os.Getenv(envVar)
	}
	return ""
}

// GetConfigPath returns the path to the config file
func GetConfigPath() string {
	if cfgFile := os.Getenv("ODIN_CONFIG"); cfgFile != "" {
		return cfgFile
	}

	// Check common locations
	locations := []string{
		"odin.config.yaml",
		filepath.Join(os.Getenv("HOME"), ".odin", "config.yaml"),
		"/etc/odin/config.yaml",
	}

	for _, loc := range locations {
		if _, err := os.Stat(loc); err == nil {
			return loc
		}
	}

	return ""
}

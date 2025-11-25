// =============================================================================
// ODIN v7.0 - Orchestrator Main Entry Point
// =============================================================================
// Multi-agent orchestration for reliable AI-assisted development
// =============================================================================

package main

import (
	"context"
	"fmt"
	"os"
	"os/signal"
	"syscall"

	"github.com/krigsexe/odin/orchestrator/internal/router"
	"github.com/krigsexe/odin/orchestrator/internal/scheduler"
	"github.com/krigsexe/odin/orchestrator/pkg/config"
	"github.com/spf13/cobra"
	"go.uber.org/zap"
)

var (
	version   = "7.0.0"
	cfgFile   string
	logger    *zap.Logger
)

func main() {
	rootCmd := &cobra.Command{
		Use:   "odin",
		Short: "ODIN - Orchestrated Development Intelligence Network",
		Long: `ODIN v7.0 - Multi-agent orchestration for reliable AI-assisted development.

Provides:
  - Task routing and scheduling
  - Agent lifecycle management
  - Checkpoint and rollback
  - Consensus verification
  - Audit logging`,
		Version: version,
	}

	// Global flags
	rootCmd.PersistentFlags().StringVar(&cfgFile, "config", "", "config file (default: odin.config.yaml)")

	// Add commands
	rootCmd.AddCommand(serveCmd())
	rootCmd.AddCommand(statusCmd())
	rootCmd.AddCommand(taskCmd())

	if err := rootCmd.Execute(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}

// serveCmd starts the orchestrator server
func serveCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "serve",
		Short: "Start the orchestrator server",
		RunE: func(cmd *cobra.Command, args []string) error {
			return runServer()
		},
	}
	return cmd
}

// statusCmd shows orchestrator status
func statusCmd() *cobra.Command {
	return &cobra.Command{
		Use:   "status",
		Short: "Show orchestrator and agent status",
		RunE: func(cmd *cobra.Command, args []string) error {
			fmt.Println("ODIN Orchestrator Status")
			fmt.Println("========================")
			fmt.Printf("Version: %s\n", version)
			// TODO: Connect to running orchestrator and show status
			return nil
		},
	}
}

// taskCmd manages tasks
func taskCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "task",
		Short: "Task management commands",
	}

	cmd.AddCommand(&cobra.Command{
		Use:   "list",
		Short: "List recent tasks",
		RunE: func(cmd *cobra.Command, args []string) error {
			// TODO: Query task store
			fmt.Println("Recent tasks:")
			return nil
		},
	})

	cmd.AddCommand(&cobra.Command{
		Use:   "submit [description]",
		Short: "Submit a new task",
		Args:  cobra.MinimumNArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			description := args[0]
			fmt.Printf("Submitting task: %s\n", description)
			// TODO: Submit to orchestrator
			return nil
		},
	})

	return cmd
}

func runServer() error {
	var err error

	// Initialize logger
	logger, err = zap.NewProduction()
	if err != nil {
		return fmt.Errorf("failed to initialize logger: %w", err)
	}
	defer logger.Sync()

	logger.Info("Starting ODIN Orchestrator", zap.String("version", version))

	// Load configuration
	cfg, err := config.Load(cfgFile)
	if err != nil {
		return fmt.Errorf("failed to load config: %w", err)
	}

	// Create context with cancellation
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	// Initialize components
	taskRouter := router.New(cfg, logger)
	taskScheduler := scheduler.New(cfg, logger)

	// Start components
	go func() {
		if err := taskRouter.Start(ctx); err != nil {
			logger.Error("Router error", zap.Error(err))
		}
	}()

	go func() {
		if err := taskScheduler.Start(ctx); err != nil {
			logger.Error("Scheduler error", zap.Error(err))
		}
	}()

	logger.Info("Orchestrator started",
		zap.String("redis", cfg.Redis.URL),
		zap.String("postgres", cfg.Database.URL),
	)

	// Wait for shutdown signal
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)
	<-sigChan

	logger.Info("Shutting down orchestrator...")
	cancel()

	return nil
}

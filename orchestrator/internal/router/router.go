// =============================================================================
// ODIN v7.0 - Task Router
// =============================================================================
// Routes tasks to appropriate agents based on type and availability
// =============================================================================

package router

import (
	"context"
	"encoding/json"
	"fmt"
	"sync"
	"time"

	"github.com/krigsexe/odin/orchestrator/pkg/config"
	"go.uber.org/zap"
)

// TaskType represents different task categories
type TaskType string

const (
	TaskCodeWrite   TaskType = "code_write"
	TaskCodeModify  TaskType = "code_modify"
	TaskCodeDebug   TaskType = "code_debug"
	TaskCodeReview  TaskType = "code_review"
	TaskTest        TaskType = "test"
	TaskAnalysis    TaskType = "analysis"
	TaskQuestion    TaskType = "question"
)

// Task represents a unit of work
type Task struct {
	ID          string                 `json:"id"`
	Type        TaskType               `json:"type"`
	Description string                 `json:"description"`
	Input       map[string]interface{} `json:"input"`
	Context     map[string]interface{} `json:"context"`
	Priority    int                    `json:"priority"`
	CreatedAt   time.Time              `json:"created_at"`
	Timeout     time.Duration          `json:"timeout"`
}

// AgentInfo holds agent metadata
type AgentInfo struct {
	ID           string   `json:"id"`
	Name         string   `json:"name"`
	Capabilities []string `json:"capabilities"`
	Status       string   `json:"status"`
	LastSeen     time.Time `json:"last_seen"`
}

// Router handles task routing to agents
type Router struct {
	config  *config.Config
	logger  *zap.Logger
	agents  map[string]*AgentInfo
	mu      sync.RWMutex

	// Routing table: task type -> agent names
	routes map[TaskType][]string
}

// New creates a new Router instance
func New(cfg *config.Config, logger *zap.Logger) *Router {
	r := &Router{
		config:  cfg,
		logger:  logger,
		agents:  make(map[string]*AgentInfo),
		routes:  make(map[TaskType][]string),
	}

	// Initialize default routes
	r.initRoutes()

	return r
}

// initRoutes sets up default routing table
func (r *Router) initRoutes() {
	r.routes = map[TaskType][]string{
		TaskCodeWrite:  {"retrieval", "dev", "approbation"},
		TaskCodeModify: {"retrieval", "dev", "approbation"},
		TaskCodeDebug:  {"retrieval", "dev", "oracle_code"},
		TaskCodeReview: {"retrieval", "review", "security"},
		TaskTest:       {"retrieval", "test", "oracle_code"},
		TaskAnalysis:   {"retrieval", "analysis"},
		TaskQuestion:   {"retrieval", "explain"},
	}
}

// Start begins the router's operation
func (r *Router) Start(ctx context.Context) error {
	r.logger.Info("Starting task router")

	// Start agent discovery
	go r.discoverAgents(ctx)

	// Start routing loop
	return r.routingLoop(ctx)
}

// discoverAgents periodically discovers available agents
func (r *Router) discoverAgents(ctx context.Context) {
	ticker := time.NewTicker(time.Duration(r.config.Agents.HealthCheck) * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			r.refreshAgentList()
		}
	}
}

// refreshAgentList updates the list of available agents
func (r *Router) refreshAgentList() {
	// TODO: Query Redis for agent heartbeats
	// For now, assume agents from config are available
	r.mu.Lock()
	defer r.mu.Unlock()

	for _, agentName := range r.config.Agents.Enabled {
		if _, exists := r.agents[agentName]; !exists {
			r.agents[agentName] = &AgentInfo{
				ID:       fmt.Sprintf("%s-1", agentName),
				Name:     agentName,
				Status:   "ready",
				LastSeen: time.Now(),
			}
		}
	}
}

// routingLoop is the main routing loop
func (r *Router) routingLoop(ctx context.Context) error {
	// TODO: Consume tasks from Redis stream
	<-ctx.Done()
	return nil
}

// Route determines which agents should handle a task
func (r *Router) Route(task *Task) ([]string, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	agents, ok := r.routes[task.Type]
	if !ok {
		return []string{"dev"}, nil // Default to dev agent
	}

	// Filter for available agents
	available := make([]string, 0)
	for _, agentName := range agents {
		if agent, exists := r.agents[agentName]; exists {
			if agent.Status == "ready" {
				available = append(available, agentName)
			}
		}
	}

	if len(available) == 0 {
		return nil, fmt.Errorf("no available agents for task type: %s", task.Type)
	}

	return available, nil
}

// RegisterAgent registers a new agent
func (r *Router) RegisterAgent(info *AgentInfo) {
	r.mu.Lock()
	defer r.mu.Unlock()

	r.agents[info.Name] = info
	r.logger.Info("Agent registered",
		zap.String("id", info.ID),
		zap.String("name", info.Name),
	)
}

// UnregisterAgent removes an agent
func (r *Router) UnregisterAgent(agentID string) {
	r.mu.Lock()
	defer r.mu.Unlock()

	for name, agent := range r.agents {
		if agent.ID == agentID {
			delete(r.agents, name)
			r.logger.Info("Agent unregistered", zap.String("id", agentID))
			return
		}
	}
}

// GetAgents returns all registered agents
func (r *Router) GetAgents() []*AgentInfo {
	r.mu.RLock()
	defer r.mu.RUnlock()

	agents := make([]*AgentInfo, 0, len(r.agents))
	for _, agent := range r.agents {
		agents = append(agents, agent)
	}
	return agents
}

// SubmitTask submits a task to the routing queue
func (r *Router) SubmitTask(task *Task) error {
	// Determine routing
	agents, err := r.Route(task)
	if err != nil {
		return err
	}

	r.logger.Info("Task routed",
		zap.String("id", task.ID),
		zap.String("type", string(task.Type)),
		zap.Strings("agents", agents),
	)

	// TODO: Publish to Redis stream for agent consumption
	taskJSON, _ := json.Marshal(task)
	_ = taskJSON // Would publish to Redis

	return nil
}

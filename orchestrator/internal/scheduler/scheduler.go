// =============================================================================
// ODIN v7.0 - Task Scheduler
// =============================================================================
// Manages task execution order, priorities, and concurrency
// =============================================================================

package scheduler

import (
	"container/heap"
	"context"
	"sync"
	"time"

	"github.com/krigsexe/odin/orchestrator/pkg/config"
	"go.uber.org/zap"
)

// TaskPriority levels
type TaskPriority int

const (
	PriorityLow      TaskPriority = 0
	PriorityNormal   TaskPriority = 1
	PriorityHigh     TaskPriority = 2
	PriorityCritical TaskPriority = 3
)

// ScheduledTask is a task with scheduling metadata
type ScheduledTask struct {
	ID          string
	Priority    TaskPriority
	ScheduledAt time.Time
	Deadline    time.Time
	Retries     int
	MaxRetries  int
	Dependencies []string
	index       int // For heap
}

// TaskQueue is a priority queue of tasks
type TaskQueue []*ScheduledTask

func (pq TaskQueue) Len() int { return len(pq) }

func (pq TaskQueue) Less(i, j int) bool {
	// Higher priority first, then earlier scheduled time
	if pq[i].Priority != pq[j].Priority {
		return pq[i].Priority > pq[j].Priority
	}
	return pq[i].ScheduledAt.Before(pq[j].ScheduledAt)
}

func (pq TaskQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
	pq[i].index = i
	pq[j].index = j
}

func (pq *TaskQueue) Push(x interface{}) {
	n := len(*pq)
	task := x.(*ScheduledTask)
	task.index = n
	*pq = append(*pq, task)
}

func (pq *TaskQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	task := old[n-1]
	old[n-1] = nil
	task.index = -1
	*pq = old[0 : n-1]
	return task
}

// Scheduler manages task scheduling and execution
type Scheduler struct {
	config       *config.Config
	logger       *zap.Logger
	queue        TaskQueue
	mu           sync.Mutex
	running      map[string]*ScheduledTask
	completed    map[string]bool
	maxConcurrent int
	currentCount int
}

// New creates a new Scheduler instance
func New(cfg *config.Config, logger *zap.Logger) *Scheduler {
	s := &Scheduler{
		config:        cfg,
		logger:        logger,
		queue:         make(TaskQueue, 0),
		running:       make(map[string]*ScheduledTask),
		completed:     make(map[string]bool),
		maxConcurrent: cfg.Orchestrator.MaxConcurrentTasks,
	}
	heap.Init(&s.queue)
	return s
}

// Start begins the scheduler
func (s *Scheduler) Start(ctx context.Context) error {
	s.logger.Info("Starting task scheduler",
		zap.Int("max_concurrent", s.maxConcurrent),
	)

	ticker := time.NewTicker(100 * time.Millisecond)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			s.logger.Info("Scheduler shutting down")
			return nil
		case <-ticker.C:
			s.processQueue()
		}
	}
}

// Schedule adds a task to the queue
func (s *Scheduler) Schedule(task *ScheduledTask) {
	s.mu.Lock()
	defer s.mu.Unlock()

	task.ScheduledAt = time.Now()
	if task.MaxRetries == 0 {
		task.MaxRetries = 3
	}

	heap.Push(&s.queue, task)
	s.logger.Debug("Task scheduled",
		zap.String("id", task.ID),
		zap.Int("priority", int(task.Priority)),
	)
}

// processQueue dispatches tasks from the queue
func (s *Scheduler) processQueue() {
	s.mu.Lock()
	defer s.mu.Unlock()

	// Check if we can run more tasks
	for s.currentCount < s.maxConcurrent && s.queue.Len() > 0 {
		task := heap.Pop(&s.queue).(*ScheduledTask)

		// Check dependencies
		if !s.dependenciesMet(task) {
			// Re-queue with slight delay
			task.ScheduledAt = time.Now().Add(100 * time.Millisecond)
			heap.Push(&s.queue, task)
			continue
		}

		// Check deadline
		if !task.Deadline.IsZero() && time.Now().After(task.Deadline) {
			s.logger.Warn("Task expired",
				zap.String("id", task.ID),
			)
			continue
		}

		// Dispatch task
		s.running[task.ID] = task
		s.currentCount++

		go s.executeTask(task)
	}
}

// dependenciesMet checks if all task dependencies are completed
func (s *Scheduler) dependenciesMet(task *ScheduledTask) bool {
	for _, depID := range task.Dependencies {
		if !s.completed[depID] {
			return false
		}
	}
	return true
}

// executeTask runs a task (placeholder)
func (s *Scheduler) executeTask(task *ScheduledTask) {
	s.logger.Info("Executing task", zap.String("id", task.ID))

	// TODO: Actually dispatch to agent via message bus

	// Simulate execution
	time.Sleep(100 * time.Millisecond)

	s.completeTask(task.ID, nil)
}

// completeTask marks a task as completed
func (s *Scheduler) completeTask(taskID string, err error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	task, exists := s.running[taskID]
	if !exists {
		return
	}

	delete(s.running, taskID)
	s.currentCount--

	if err != nil {
		// Handle retry
		if task.Retries < task.MaxRetries {
			task.Retries++
			task.ScheduledAt = time.Now().Add(time.Duration(task.Retries) * time.Second)
			heap.Push(&s.queue, task)
			s.logger.Warn("Task failed, retrying",
				zap.String("id", taskID),
				zap.Int("retry", task.Retries),
			)
			return
		}
		s.logger.Error("Task failed permanently",
			zap.String("id", taskID),
			zap.Error(err),
		)
	} else {
		s.completed[taskID] = true
		s.logger.Info("Task completed", zap.String("id", taskID))
	}
}

// GetStatus returns scheduler status
func (s *Scheduler) GetStatus() map[string]interface{} {
	s.mu.Lock()
	defer s.mu.Unlock()

	return map[string]interface{}{
		"queued":        s.queue.Len(),
		"running":       s.currentCount,
		"completed":     len(s.completed),
		"max_concurrent": s.maxConcurrent,
	}
}

// Cancel cancels a scheduled or running task
func (s *Scheduler) Cancel(taskID string) bool {
	s.mu.Lock()
	defer s.mu.Unlock()

	// Check if running
	if _, exists := s.running[taskID]; exists {
		// TODO: Signal cancellation to agent
		delete(s.running, taskID)
		s.currentCount--
		return true
	}

	// Check queue
	for i, task := range s.queue {
		if task.ID == taskID {
			heap.Remove(&s.queue, i)
			return true
		}
	}

	return false
}

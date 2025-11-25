-- =============================================================================
-- ODIN v7.0 - Database Schema
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Tasks Table
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tasks (
    id VARCHAR(64) PRIMARY KEY,
    type VARCHAR(64) NOT NULL,
    status VARCHAR(32) DEFAULT 'pending',
    payload JSONB,
    result JSONB,
    confidence FLOAT,
    sources JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_type ON tasks(type);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);

-- -----------------------------------------------------------------------------
-- Checkpoints Table
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS checkpoints (
    id VARCHAR(64) PRIMARY KEY,
    task_id VARCHAR(64) REFERENCES tasks(id),
    state_hash VARCHAR(128) NOT NULL,
    files_modified JSONB,
    diff_summary TEXT,
    validated BOOLEAN DEFAULT FALSE,
    can_rollback BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    validated_at TIMESTAMP WITH TIME ZONE,
    validated_by VARCHAR(64)
);

CREATE INDEX idx_checkpoints_task_id ON checkpoints(task_id);
CREATE INDEX idx_checkpoints_created_at ON checkpoints(created_at);

-- -----------------------------------------------------------------------------
-- Feedback Table
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS feedback (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(64) REFERENCES tasks(id),
    checkpoint_id VARCHAR(64) REFERENCES checkpoints(id),
    rating VARCHAR(32) NOT NULL,  -- 'perfect', 'acceptable', 'false'
    reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_feedback_task_id ON feedback(task_id);
CREATE INDEX idx_feedback_rating ON feedback(rating);

-- -----------------------------------------------------------------------------
-- Learning Patterns Table
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS patterns (
    id SERIAL PRIMARY KEY,
    type VARCHAR(32) NOT NULL,  -- 'positive', 'negative'
    pattern_hash VARCHAR(128) UNIQUE,
    description TEXT,
    context JSONB,
    occurrences INTEGER DEFAULT 1,
    first_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    validated BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_patterns_type ON patterns(type);
CREATE INDEX idx_patterns_validated ON patterns(validated);

-- -----------------------------------------------------------------------------
-- Knowledge Items Table (Episodic Memory)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS knowledge_items (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    content_hash VARCHAR(128) UNIQUE,
    confidence FLOAT DEFAULT 0.5,
    source_type VARCHAR(64),  -- 'official_docs', 'community', 'internal', 'verified'
    source_url TEXT,
    source_title TEXT,
    context_constraints JSONB,
    contradictions JSONB,
    verification_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_knowledge_confidence ON knowledge_items(confidence);
CREATE INDEX idx_knowledge_source_type ON knowledge_items(source_type);

-- -----------------------------------------------------------------------------
-- Agent Logs Table
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS agent_logs (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(64),
    agent_name VARCHAR(64) NOT NULL,
    action VARCHAR(64) NOT NULL,
    input JSONB,
    output JSONB,
    duration_ms INTEGER,
    success BOOLEAN,
    error TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_agent_logs_task_id ON agent_logs(task_id);
CREATE INDEX idx_agent_logs_agent_name ON agent_logs(agent_name);
CREATE INDEX idx_agent_logs_created_at ON agent_logs(created_at);

-- -----------------------------------------------------------------------------
-- Metrics Table
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(128) NOT NULL,
    metric_value FLOAT NOT NULL,
    labels JSONB,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_metrics_name ON metrics(metric_name);
CREATE INDEX idx_metrics_recorded_at ON metrics(recorded_at);

-- -----------------------------------------------------------------------------
-- Functions
-- -----------------------------------------------------------------------------

-- Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers
CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_knowledge_items_updated_at BEFORE UPDATE ON knowledge_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

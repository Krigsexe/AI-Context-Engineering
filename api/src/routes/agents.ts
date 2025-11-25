// =============================================================================
// ODIN v7.0 - Agent Routes
// =============================================================================

import { Router, Request, Response } from 'express';
import { Agent, AgentStatus, APIResponse } from '../types/index.js';

export const agentRoutes = Router();

// In-memory store for demo (replace with actual discovery)
const agents = new Map<string, Agent>();

// Initialize with default agents
const defaultAgents: Agent[] = [
  {
    id: 'intake-1',
    name: 'intake',
    status: 'ready',
    capabilities: ['classify_task', 'extract_context', 'route_task'],
    currentTaskId: null,
    lastSeen: new Date().toISOString(),
  },
  {
    id: 'retrieval-1',
    name: 'retrieval',
    status: 'ready',
    capabilities: ['find_files', 'search_code', 'get_context', 'build_task_context'],
    currentTaskId: null,
    lastSeen: new Date().toISOString(),
  },
  {
    id: 'dev-1',
    name: 'dev',
    status: 'ready',
    capabilities: ['generate_code', 'modify_code', 'debug_code', 'explain_code'],
    currentTaskId: null,
    lastSeen: new Date().toISOString(),
  },
  {
    id: 'oracle_code-1',
    name: 'oracle_code',
    status: 'ready',
    capabilities: ['execute_code', 'run_tests', 'verify_output', 'syntax_check'],
    currentTaskId: null,
    lastSeen: new Date().toISOString(),
  },
];

// Initialize default agents
defaultAgents.forEach(agent => agents.set(agent.id, agent));

// Get all agents
agentRoutes.get('/', (req: Request, res: Response) => {
  const { status, name } = req.query;

  let filteredAgents = Array.from(agents.values());

  if (status) {
    filteredAgents = filteredAgents.filter(a => a.status === status);
  }

  if (name) {
    filteredAgents = filteredAgents.filter(a => a.name === name);
  }

  res.json({
    success: true,
    data: filteredAgents,
    meta: {
      total: filteredAgents.length,
    },
  } as APIResponse<Agent[]>);
});

// Get agent by ID
agentRoutes.get('/:id', (req: Request, res: Response) => {
  const agent = agents.get(req.params.id);

  if (!agent) {
    return res.status(404).json({
      success: false,
      error: 'Agent not found',
    } as APIResponse<null>);
  }

  res.json({
    success: true,
    data: agent,
  } as APIResponse<Agent>);
});

// Get agent capabilities
agentRoutes.get('/:id/capabilities', (req: Request, res: Response) => {
  const agent = agents.get(req.params.id);

  if (!agent) {
    return res.status(404).json({
      success: false,
      error: 'Agent not found',
    } as APIResponse<null>);
  }

  res.json({
    success: true,
    data: {
      agentId: agent.id,
      name: agent.name,
      capabilities: agent.capabilities,
    },
  });
});

// Pause an agent
agentRoutes.post('/:id/pause', (req: Request, res: Response) => {
  const agent = agents.get(req.params.id);

  if (!agent) {
    return res.status(404).json({
      success: false,
      error: 'Agent not found',
    } as APIResponse<null>);
  }

  if (agent.status === 'busy') {
    return res.status(400).json({
      success: false,
      error: 'Cannot pause agent while busy',
    } as APIResponse<null>);
  }

  agent.status = 'paused';
  agent.lastSeen = new Date().toISOString();

  res.json({
    success: true,
    data: agent,
  } as APIResponse<Agent>);
});

// Resume an agent
agentRoutes.post('/:id/resume', (req: Request, res: Response) => {
  const agent = agents.get(req.params.id);

  if (!agent) {
    return res.status(404).json({
      success: false,
      error: 'Agent not found',
    } as APIResponse<null>);
  }

  if (agent.status !== 'paused') {
    return res.status(400).json({
      success: false,
      error: 'Agent is not paused',
    } as APIResponse<null>);
  }

  agent.status = 'ready';
  agent.lastSeen = new Date().toISOString();

  res.json({
    success: true,
    data: agent,
  } as APIResponse<Agent>);
});

// Get agent metrics
agentRoutes.get('/:id/metrics', (req: Request, res: Response) => {
  const agent = agents.get(req.params.id);

  if (!agent) {
    return res.status(404).json({
      success: false,
      error: 'Agent not found',
    } as APIResponse<null>);
  }

  // TODO: Get actual metrics from store
  res.json({
    success: true,
    data: {
      agentId: agent.id,
      tasksCompleted: 0,
      tasksFailed: 0,
      averageLatency: 0,
      uptime: 0,
    },
  });
});

// List available agent types
agentRoutes.get('/types/available', (req: Request, res: Response) => {
  const agentTypes = [
    { name: 'intake', description: 'Task classification and routing' },
    { name: 'retrieval', description: 'Context and knowledge gathering' },
    { name: 'dev', description: 'Code generation and modification' },
    { name: 'oracle_code', description: 'Code execution verification' },
    { name: 'review', description: 'Code review and analysis' },
    { name: 'security', description: 'Security vulnerability scanning' },
    { name: 'test', description: 'Test generation and execution' },
    { name: 'docs', description: 'Documentation generation' },
    { name: 'architect', description: 'Architecture decisions' },
  ];

  res.json({
    success: true,
    data: agentTypes,
  });
});

// =============================================================================
// ODIN v7.0 - API Types
// =============================================================================

import { z } from 'zod';

// Task types
export const TaskStatusSchema = z.enum([
  'pending',
  'running',
  'completed',
  'failed',
  'cancelled',
]);
export type TaskStatus = z.infer<typeof TaskStatusSchema>;

export const TaskTypeSchema = z.enum([
  'code_write',
  'code_modify',
  'code_debug',
  'code_review',
  'code_explain',
  'refactor',
  'test',
  'documentation',
  'architecture',
  'question',
  'analysis',
]);
export type TaskType = z.infer<typeof TaskTypeSchema>;

export const ConfidenceLevelSchema = z.enum([
  'axiom',
  'high',
  'moderate',
  'uncertain',
  'unknown',
]);
export type ConfidenceLevel = z.infer<typeof ConfidenceLevelSchema>;

// Task schema
export const TaskSchema = z.object({
  id: z.string().uuid(),
  type: TaskTypeSchema,
  status: TaskStatusSchema,
  description: z.string(),
  input: z.record(z.any()),
  output: z.record(z.any()).nullable(),
  confidence: ConfidenceLevelSchema.nullable(),
  error: z.string().nullable(),
  agentId: z.string().nullable(),
  parentTaskId: z.string().uuid().nullable(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  completedAt: z.string().datetime().nullable(),
});
export type Task = z.infer<typeof TaskSchema>;

// Create task request
export const CreateTaskRequestSchema = z.object({
  type: TaskTypeSchema.optional(),
  description: z.string().min(1),
  input: z.record(z.any()).optional(),
  context: z.record(z.any()).optional(),
  priority: z.number().int().min(0).max(3).optional(),
  timeout: z.number().int().positive().optional(),
});
export type CreateTaskRequest = z.infer<typeof CreateTaskRequestSchema>;

// Agent types
export const AgentStatusSchema = z.enum([
  'initializing',
  'ready',
  'busy',
  'paused',
  'error',
  'stopped',
]);
export type AgentStatus = z.infer<typeof AgentStatusSchema>;

export const AgentSchema = z.object({
  id: z.string(),
  name: z.string(),
  status: AgentStatusSchema,
  capabilities: z.array(z.string()),
  currentTaskId: z.string().uuid().nullable(),
  lastSeen: z.string().datetime(),
});
export type Agent = z.infer<typeof AgentSchema>;

// WebSocket message types
export const WSMessageTypeSchema = z.enum([
  'subscribe',
  'unsubscribe',
  'task_created',
  'task_updated',
  'task_completed',
  'task_failed',
  'agent_status',
  'error',
  'ping',
  'pong',
]);
export type WSMessageType = z.infer<typeof WSMessageTypeSchema>;

export const WSMessageSchema = z.object({
  type: WSMessageTypeSchema,
  payload: z.any(),
  timestamp: z.string().datetime().optional(),
});
export type WSMessage = z.infer<typeof WSMessageSchema>;

// API response types
export interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  meta?: {
    page?: number;
    pageSize?: number;
    total?: number;
  };
}

export interface PaginationParams {
  page?: number;
  pageSize?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

// =============================================================================
// ODIN v7.0 - Task Routes
// =============================================================================

import { Router, Request, Response, NextFunction } from 'express';
import { v4 as uuidv4 } from 'uuid';
import { CreateTaskRequestSchema, Task, TaskStatus, APIResponse } from '../types/index.js';

export const taskRoutes = Router();

// In-memory store for demo (replace with actual database)
const tasks = new Map<string, Task>();

// Create a new task
taskRoutes.post('/', async (req: Request, res: Response, next: NextFunction) => {
  try {
    const validation = CreateTaskRequestSchema.safeParse(req.body);

    if (!validation.success) {
      return res.status(400).json({
        success: false,
        error: 'Invalid request',
        details: validation.error.errors,
      } as APIResponse<null>);
    }

    const { description, type, input, context, priority, timeout } = validation.data;

    const task: Task = {
      id: uuidv4(),
      type: type || 'code_write',
      status: 'pending',
      description,
      input: input || {},
      output: null,
      confidence: null,
      error: null,
      agentId: null,
      parentTaskId: null,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      completedAt: null,
    };

    tasks.set(task.id, task);

    // TODO: Publish to message bus for orchestrator

    res.status(201).json({
      success: true,
      data: task,
    } as APIResponse<Task>);
  } catch (error) {
    next(error);
  }
});

// Get all tasks
taskRoutes.get('/', async (req: Request, res: Response) => {
  const { status, type, page = 1, pageSize = 20 } = req.query;

  let filteredTasks = Array.from(tasks.values());

  if (status) {
    filteredTasks = filteredTasks.filter(t => t.status === status);
  }

  if (type) {
    filteredTasks = filteredTasks.filter(t => t.type === type);
  }

  // Sort by creation date (newest first)
  filteredTasks.sort((a, b) =>
    new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
  );

  // Paginate
  const pageNum = parseInt(page as string, 10);
  const pageSizeNum = parseInt(pageSize as string, 10);
  const start = (pageNum - 1) * pageSizeNum;
  const paginatedTasks = filteredTasks.slice(start, start + pageSizeNum);

  res.json({
    success: true,
    data: paginatedTasks,
    meta: {
      page: pageNum,
      pageSize: pageSizeNum,
      total: filteredTasks.length,
    },
  } as APIResponse<Task[]>);
});

// Get task by ID
taskRoutes.get('/:id', async (req: Request, res: Response) => {
  const task = tasks.get(req.params.id);

  if (!task) {
    return res.status(404).json({
      success: false,
      error: 'Task not found',
    } as APIResponse<null>);
  }

  res.json({
    success: true,
    data: task,
  } as APIResponse<Task>);
});

// Cancel a task
taskRoutes.post('/:id/cancel', async (req: Request, res: Response) => {
  const task = tasks.get(req.params.id);

  if (!task) {
    return res.status(404).json({
      success: false,
      error: 'Task not found',
    } as APIResponse<null>);
  }

  if (task.status === 'completed' || task.status === 'failed') {
    return res.status(400).json({
      success: false,
      error: 'Cannot cancel completed or failed task',
    } as APIResponse<null>);
  }

  task.status = 'cancelled';
  task.updatedAt = new Date().toISOString();

  // TODO: Send cancellation to orchestrator

  res.json({
    success: true,
    data: task,
  } as APIResponse<Task>);
});

// Retry a failed task
taskRoutes.post('/:id/retry', async (req: Request, res: Response) => {
  const originalTask = tasks.get(req.params.id);

  if (!originalTask) {
    return res.status(404).json({
      success: false,
      error: 'Task not found',
    } as APIResponse<null>);
  }

  if (originalTask.status !== 'failed') {
    return res.status(400).json({
      success: false,
      error: 'Can only retry failed tasks',
    } as APIResponse<null>);
  }

  // Create new task based on original
  const newTask: Task = {
    ...originalTask,
    id: uuidv4(),
    status: 'pending',
    output: null,
    error: null,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    completedAt: null,
  };

  tasks.set(newTask.id, newTask);

  res.status(201).json({
    success: true,
    data: newTask,
  } as APIResponse<Task>);
});

// Get task result (for completed tasks)
taskRoutes.get('/:id/result', async (req: Request, res: Response) => {
  const task = tasks.get(req.params.id);

  if (!task) {
    return res.status(404).json({
      success: false,
      error: 'Task not found',
    } as APIResponse<null>);
  }

  if (task.status !== 'completed') {
    return res.status(400).json({
      success: false,
      error: `Task is ${task.status}, not completed`,
    } as APIResponse<null>);
  }

  res.json({
    success: true,
    data: {
      output: task.output,
      confidence: task.confidence,
      completedAt: task.completedAt,
    },
  });
});

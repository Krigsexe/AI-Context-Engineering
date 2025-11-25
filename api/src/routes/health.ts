// =============================================================================
// ODIN v7.0 - Health Routes
// =============================================================================

import { Router } from 'express';
import { config } from '../config.js';

export const healthRoutes = Router();

// Basic health check
healthRoutes.get('/', (req, res) => {
  res.json({
    status: 'healthy',
    version: '7.0.0',
    timestamp: new Date().toISOString(),
  });
});

// Detailed health check
healthRoutes.get('/detailed', async (req, res) => {
  const checks: Record<string, { status: string; latency?: number; error?: string }> = {};

  // Check database
  const dbStart = Date.now();
  try {
    // TODO: Actually ping database
    checks.database = {
      status: 'healthy',
      latency: Date.now() - dbStart,
    };
  } catch (error) {
    checks.database = {
      status: 'unhealthy',
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }

  // Check Redis
  const redisStart = Date.now();
  try {
    // TODO: Actually ping Redis
    checks.redis = {
      status: 'healthy',
      latency: Date.now() - redisStart,
    };
  } catch (error) {
    checks.redis = {
      status: 'unhealthy',
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }

  const allHealthy = Object.values(checks).every(c => c.status === 'healthy');

  res.status(allHealthy ? 200 : 503).json({
    status: allHealthy ? 'healthy' : 'degraded',
    version: '7.0.0',
    timestamp: new Date().toISOString(),
    checks,
    config: {
      environment: config.env,
      maxConcurrentTasks: config.tasks.maxConcurrent,
    },
  });
});

// Readiness check
healthRoutes.get('/ready', (req, res) => {
  // TODO: Check if all dependencies are ready
  res.json({ ready: true });
});

// Liveness check
healthRoutes.get('/live', (req, res) => {
  res.json({ alive: true });
});

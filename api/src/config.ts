// =============================================================================
// ODIN v7.0 - API Configuration
// =============================================================================

import dotenv from 'dotenv';

dotenv.config();

export const config = {
  // Server
  port: parseInt(process.env.API_PORT || '3000', 10),
  env: process.env.NODE_ENV || 'development',

  // CORS
  corsOrigins: process.env.CORS_ORIGINS?.split(',') || ['http://localhost:3000'],

  // Database
  database: {
    url: process.env.DATABASE_URL || 'postgresql://odin:odin@localhost:5432/odin',
    maxConnections: parseInt(process.env.DB_MAX_CONNECTIONS || '20', 10),
  },

  // Redis
  redis: {
    url: process.env.REDIS_URL || 'redis://localhost:6379',
  },

  // Authentication
  auth: {
    enabled: process.env.AUTH_ENABLED === 'true',
    jwtSecret: process.env.JWT_SECRET || 'dev-secret-change-in-production',
    tokenExpiry: process.env.TOKEN_EXPIRY || '24h',
  },

  // Rate limiting
  rateLimit: {
    windowMs: parseInt(process.env.RATE_LIMIT_WINDOW || '60000', 10),
    maxRequests: parseInt(process.env.RATE_LIMIT_MAX || '100', 10),
  },

  // Task settings
  tasks: {
    maxConcurrent: parseInt(process.env.MAX_CONCURRENT_TASKS || '10', 10),
    defaultTimeout: parseInt(process.env.TASK_TIMEOUT || '300000', 10),
  },
};

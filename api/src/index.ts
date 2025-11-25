// =============================================================================
// ODIN v7.0 - API Server Entry Point
// =============================================================================
// REST/WebSocket API for ODIN orchestration
// =============================================================================

import express from 'express';
import { createServer } from 'http';
import { WebSocketServer } from 'ws';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import morgan from 'morgan';
import { config } from './config.js';
import { taskRoutes } from './routes/tasks.js';
import { agentRoutes } from './routes/agents.js';
import { healthRoutes } from './routes/health.js';
import { WebSocketHandler } from './services/websocket.js';
import { errorHandler } from './middleware/error.js';

const app = express();
const server = createServer(app);

// WebSocket server
const wss = new WebSocketServer({ server, path: '/ws' });
const wsHandler = new WebSocketHandler(wss);

// Middleware
app.use(helmet());
app.use(cors({
  origin: config.corsOrigins,
  credentials: true,
}));
app.use(compression());
app.use(express.json({ limit: '10mb' }));
app.use(morgan('combined'));

// Routes
app.use('/api/v1/health', healthRoutes);
app.use('/api/v1/tasks', taskRoutes);
app.use('/api/v1/agents', agentRoutes);

// Error handling
app.use(errorHandler);

// Start server
server.listen(config.port, () => {
  console.log(`
╔═══════════════════════════════════════════════════════════════╗
║                    ODIN v7.0 API Server                       ║
╠═══════════════════════════════════════════════════════════════╣
║  REST API:    http://localhost:${config.port}/api/v1              ║
║  WebSocket:   ws://localhost:${config.port}/ws                    ║
║  Health:      http://localhost:${config.port}/api/v1/health       ║
╚═══════════════════════════════════════════════════════════════╝
  `);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('Shutting down...');
  server.close(() => {
    process.exit(0);
  });
});

export { app, server, wss };

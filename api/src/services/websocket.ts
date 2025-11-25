// =============================================================================
// ODIN v7.0 - WebSocket Handler
// =============================================================================

import { WebSocketServer, WebSocket } from 'ws';
import { WSMessage, WSMessageType } from '../types/index.js';

interface Client {
  ws: WebSocket;
  subscriptions: Set<string>;
  id: string;
}

export class WebSocketHandler {
  private wss: WebSocketServer;
  private clients: Map<string, Client> = new Map();
  private clientIdCounter = 0;

  constructor(wss: WebSocketServer) {
    this.wss = wss;
    this.initialize();
  }

  private initialize(): void {
    this.wss.on('connection', (ws: WebSocket) => {
      const clientId = `client-${++this.clientIdCounter}`;

      const client: Client = {
        ws,
        subscriptions: new Set(),
        id: clientId,
      };

      this.clients.set(clientId, client);
      console.log(`WebSocket client connected: ${clientId}`);

      // Send welcome message
      this.send(ws, {
        type: 'task_created', // Using existing type
        payload: {
          message: 'Connected to ODIN v7.0',
          clientId,
        },
      });

      ws.on('message', (data: Buffer) => {
        this.handleMessage(client, data);
      });

      ws.on('close', () => {
        this.clients.delete(clientId);
        console.log(`WebSocket client disconnected: ${clientId}`);
      });

      ws.on('error', (error) => {
        console.error(`WebSocket error for ${clientId}:`, error);
      });

      // Ping/pong for keepalive
      ws.on('pong', () => {
        // Client is alive
      });
    });

    // Periodic ping to keep connections alive
    setInterval(() => {
      this.wss.clients.forEach((ws) => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.ping();
        }
      });
    }, 30000);
  }

  private handleMessage(client: Client, data: Buffer): void {
    try {
      const message = JSON.parse(data.toString()) as WSMessage;

      switch (message.type) {
        case 'subscribe':
          this.handleSubscribe(client, message.payload);
          break;
        case 'unsubscribe':
          this.handleUnsubscribe(client, message.payload);
          break;
        case 'ping':
          this.send(client.ws, { type: 'pong', payload: {} });
          break;
        default:
          console.log(`Unknown message type: ${message.type}`);
      }
    } catch (error) {
      console.error('Error handling WebSocket message:', error);
      this.send(client.ws, {
        type: 'error',
        payload: { message: 'Invalid message format' },
      });
    }
  }

  private handleSubscribe(client: Client, payload: any): void {
    const { channel } = payload;
    if (channel) {
      client.subscriptions.add(channel);
      console.log(`Client ${client.id} subscribed to ${channel}`);
    }
  }

  private handleUnsubscribe(client: Client, payload: any): void {
    const { channel } = payload;
    if (channel) {
      client.subscriptions.delete(channel);
      console.log(`Client ${client.id} unsubscribed from ${channel}`);
    }
  }

  private send(ws: WebSocket, message: Partial<WSMessage>): void {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        ...message,
        timestamp: new Date().toISOString(),
      }));
    }
  }

  // Broadcast to all clients subscribed to a channel
  public broadcast(channel: string, type: WSMessageType, payload: any): void {
    this.clients.forEach((client) => {
      if (client.subscriptions.has(channel) || client.subscriptions.has('*')) {
        this.send(client.ws, { type, payload });
      }
    });
  }

  // Broadcast to all connected clients
  public broadcastAll(type: WSMessageType, payload: any): void {
    this.clients.forEach((client) => {
      this.send(client.ws, { type, payload });
    });
  }

  // Send to specific client
  public sendToClient(clientId: string, type: WSMessageType, payload: any): void {
    const client = this.clients.get(clientId);
    if (client) {
      this.send(client.ws, { type, payload });
    }
  }

  // Notify task events
  public notifyTaskCreated(task: any): void {
    this.broadcast('tasks', 'task_created', task);
  }

  public notifyTaskUpdated(task: any): void {
    this.broadcast('tasks', 'task_updated', task);
  }

  public notifyTaskCompleted(task: any): void {
    this.broadcast('tasks', 'task_completed', task);
  }

  public notifyTaskFailed(task: any): void {
    this.broadcast('tasks', 'task_failed', task);
  }

  public notifyAgentStatus(agent: any): void {
    this.broadcast('agents', 'agent_status', agent);
  }

  public getClientCount(): number {
    return this.clients.size;
  }
}

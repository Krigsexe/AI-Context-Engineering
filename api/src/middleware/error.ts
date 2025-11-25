// =============================================================================
// ODIN v7.0 - Error Handler Middleware
// =============================================================================

import { Request, Response, NextFunction } from 'express';
import { config } from '../config.js';

export class APIError extends Error {
  constructor(
    public statusCode: number,
    message: string,
    public details?: any
  ) {
    super(message);
    this.name = 'APIError';
  }
}

export function errorHandler(
  err: Error,
  req: Request,
  res: Response,
  next: NextFunction
): void {
  console.error('Error:', err);

  if (err instanceof APIError) {
    res.status(err.statusCode).json({
      success: false,
      error: err.message,
      details: err.details,
    });
    return;
  }

  // Default error response
  const statusCode = 500;
  const message = config.env === 'production'
    ? 'Internal server error'
    : err.message;

  res.status(statusCode).json({
    success: false,
    error: message,
    ...(config.env !== 'production' && { stack: err.stack }),
  });
}

// Not found handler
export function notFoundHandler(
  req: Request,
  res: Response,
  next: NextFunction
): void {
  res.status(404).json({
    success: false,
    error: 'Not found',
    path: req.path,
  });
}

/**
 * Frontend logging utility
 * Provides structured logging for the React frontend
 */

class Logger {
  constructor(context = 'App') {
    this.context = context;
    this.isDevelopment = process.env.NODE_ENV === 'development';
    this.logLevel = process.env.REACT_APP_LOG_LEVEL || 'info';
    this.sendToServerEnabled = process.env.REACT_APP_SEND_LOGS_TO_SERVER !== 'false'; // Default true
    this.maxRetries = 3;
    this.retryDelay = 1000; // 1 second
  }

  /**
   * Get current timestamp
   */
  getTimestamp() {
    return new Date().toISOString();
  }

  /**
   * Format log message
   */
  formatMessage(level, message, data = null) {
    const timestamp = this.getTimestamp();
    const logData = {
      timestamp,
      level: level.toUpperCase(),
      context: this.context,
      message,
      ...(data && { data })
    };

    return logData;
  }

  /**
   * Check if log level should be output
   */
  shouldLog(level) {
    const levels = ['debug', 'info', 'warn', 'error'];
    const currentLevelIndex = levels.indexOf(this.logLevel.toLowerCase());
    const messageLevelIndex = levels.indexOf(level.toLowerCase());
    
    return messageLevelIndex >= currentLevelIndex;
  }

  /**
   * Log debug message
   */
  debug(message, data = null) {
    if (!this.shouldLog('debug')) return;
    
    const logData = this.formatMessage('debug', message, data);
    
    if (this.isDevelopment) {
      console.debug(`[${logData.timestamp}] [${logData.context}] DEBUG:`, message, data || '');
    }
    
    this.sendToServer('debug', logData);
  }

  /**
   * Log info message
   */
  info(message, data = null) {
    if (!this.shouldLog('info')) return;
    
    const logData = this.formatMessage('info', message, data);
    
    if (this.isDevelopment) {
      console.info(`[${logData.timestamp}] [${logData.context}] INFO:`, message, data || '');
    }
    
    this.sendToServer('info', logData);
  }

  /**
   * Log warning message
   */
  warn(message, data = null) {
    if (!this.shouldLog('warn')) return;
    
    const logData = this.formatMessage('warn', message, data);
    
    console.warn(`[${logData.timestamp}] [${logData.context}] WARN:`, message, data || '');
    this.sendToServer('warn', logData);
  }

  /**
   * Log error message
   */
  error(message, error = null, data = null) {
    if (!this.shouldLog('error')) return;
    
    const errorData = error ? {
      message: error.message,
      stack: error.stack,
      name: error.name
    } : null;
    
    const logData = this.formatMessage('error', message, {
      ...data,
      ...(errorData && { error: errorData })
    });
    
    console.error(`[${logData.timestamp}] [${logData.context}] ERROR:`, message, error || '', data || '');
    this.sendToServer('error', logData);
  }

  /**
   * Log API call
   */
  apiCall(method, url, requestData = null) {
    this.info(`API ${method.toUpperCase()} ${url}`, { 
      method, 
      url, 
      requestData: requestData ? JSON.stringify(requestData) : null 
    });
  }

  /**
   * Log API response
   */
  apiResponse(method, url, status, responseData = null, responseTime = null) {
    const level = status >= 400 ? 'error' : 'info';
    const message = `API ${method.toUpperCase()} ${url} - ${status}`;
    
    this[level](message, {
      method,
      url,
      status,
      responseTime: responseTime ? `${responseTime}ms` : null,
      responseData: responseData && this.isDevelopment ? JSON.stringify(responseData) : null
    });
  }

  /**
   * Log user action
   */
  userAction(action, details = null) {
    this.info(`User action: ${action}`, { action, details });
  }

  /**
   * Log navigation
   */
  navigation(from, to) {
    this.debug(`Navigation: ${from} -> ${to}`, { from, to });
  }

  /**
   * Send logs to server (optional)
   * Sends error and warn logs to backend for persistent storage
   */
  sendToServer(level, logData) {
    // Check if server logging is enabled
    if (!this.sendToServerEnabled) {
      return;
    }

    // Only send error and warn logs to server to avoid spam
    if (!['error', 'warn'].includes(level.toLowerCase())) {
      return;
    }

    this._sendLogWithRetry(logData, 0);
  }

  /**
   * Send log to server with retry logic
   */
  async _sendLogWithRetry(logData, retryCount) {
    try {
      // Get API base URL from environment or default to relative path
      const apiUrl = process.env.REACT_APP_API_URL || '/api';
      
      // Try to get auth token if available
      const token = localStorage.getItem('token');
      const headers = {
        'Content-Type': 'application/json'
      };
      
      // Add auth header if token exists
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      const response = await fetch(`${apiUrl}/frontend/logs`, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(logData)
      });

      if (!response.ok && retryCount < this.maxRetries) {
        // Retry after delay
        setTimeout(() => {
          this._sendLogWithRetry(logData, retryCount + 1);
        }, this.retryDelay * (retryCount + 1));
      }
      
    } catch (err) {
      // Retry on network errors
      if (retryCount < this.maxRetries) {
        setTimeout(() => {
          this._sendLogWithRetry(logData, retryCount + 1);
        }, this.retryDelay * (retryCount + 1));
      }
      
      // Only log to console in development to avoid infinite loops
      if (this.isDevelopment && retryCount === this.maxRetries) {
        console.error('Failed to send log to server after all retries:', err);
      }
    }
  }

  /**
   * Create a new logger instance with a specific context
   */
  createLogger(context) {
    return new Logger(context);
  }

  /**
   * Test the connection to backend logging service
   */
  async testConnection() {
    try {
      const apiUrl = process.env.REACT_APP_API_URL || '/api';
      const response = await fetch(`${apiUrl}/frontend/logs/test`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        this.info('Frontend logging connection test successful');
        return true;
      } else {
        this.warn('Frontend logging connection test failed', { status: response.status });
        return false;
      }
    } catch (error) {
      this.error('Frontend logging connection test error', error);
      return false;
    }
  }
}

// Create default logger instance
const logger = new Logger();

// Create context-specific loggers
export const authLogger = logger.createLogger('Auth');
export const apiLogger = logger.createLogger('API');
export const databaseLogger = logger.createLogger('Database');
export const settingsLogger = logger.createLogger('Settings');
export const dashboardLogger = logger.createLogger('Dashboard');

export default logger;

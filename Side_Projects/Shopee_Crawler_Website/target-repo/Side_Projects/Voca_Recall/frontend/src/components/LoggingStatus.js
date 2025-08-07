import React, { useState, useEffect } from 'react';
import logger from '../utils/logger';

const LoggingStatus = () => {
  const [connectionStatus, setConnectionStatus] = useState('unknown');
  const [isLoading, setIsLoading] = useState(false);
  const [logs, setLogs] = useState([]);
  const [loggingInfo, setLoggingInfo] = useState(null);

  useEffect(() => {
    // Test connection and fetch logging info on component mount
    testConnection();
    fetchLoggingInfo();
  }, []);

  const fetchLoggingInfo = async () => {
    try {
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5000';
      const response = await fetch(`${apiUrl}/api/frontend/logs/info`);
      if (response.ok) {
        const info = await response.json();
        setLoggingInfo(info);
      }
    } catch (error) {
      console.error('Failed to fetch logging info:', error);
    }
  };

  const testConnection = async () => {
    setIsLoading(true);
    try {
      const success = await logger.testConnection();
      setConnectionStatus(success ? 'connected' : 'failed');
    } catch (error) {
      setConnectionStatus('error');
    } finally {
      setIsLoading(false);
    }
  };

  const sendTestLogs = () => {
    logger.info('Test info log from LoggingStatus component');
    logger.warn('Test warning log from LoggingStatus component');
    logger.error('Test error log from LoggingStatus component');
    
    setLogs(prev => [
      ...prev,
      { level: 'info', message: 'Test info log sent', timestamp: new Date().toISOString() },
      { level: 'warn', message: 'Test warning log sent', timestamp: new Date().toISOString() },
      { level: 'error', message: 'Test error log sent', timestamp: new Date().toISOString() }
    ]);
  };

  const clearLogs = () => {
    setLogs([]);
  };

  const getStatusColor = () => {
    switch (connectionStatus) {
      case 'connected': return 'text-green-600';
      case 'failed': return 'text-red-600';
      case 'error': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getStatusText = () => {
    switch (connectionStatus) {
      case 'connected': return 'Connected';
      case 'failed': return 'Connection Failed';
      case 'error': return 'Connection Error';
      default: return 'Unknown';
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Frontend Logging Status</h3>
      
      {/* Connection Status */}
      <div className="mb-4">
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-600">Backend Connection:</span>
          <span className={`text-sm font-medium ${getStatusColor()}`}>
            {isLoading ? 'Testing...' : getStatusText()}
          </span>
        </div>
        
        <div className="mt-2 text-xs text-gray-500">
          <div>Log Level: {process.env.REACT_APP_LOG_LEVEL || 'info'}</div>
          <div>API URL: {process.env.REACT_APP_API_URL || 'http://localhost:5000'}</div>
          <div>Send to Server: {process.env.REACT_APP_SEND_LOGS_TO_SERVER !== 'false' ? 'Enabled' : 'Disabled'}</div>
        </div>
      </div>

      {/* Log Files Information */}
      {loggingInfo && (
        <div className="mb-4 p-3 bg-gray-50 rounded">
          <h4 className="text-sm font-medium text-gray-900 mb-2">Log Files Status:</h4>
          <div className="text-xs text-gray-600 space-y-1">
            <div className="flex items-center space-x-2">
              <span className={`w-2 h-2 rounded-full ${loggingInfo.files_exist.frontend_log ? 'bg-green-500' : 'bg-gray-300'}`}></span>
              <span>Frontend: <code>{loggingInfo.frontend_log_file}</code></span>
            </div>
            <div className="flex items-center space-x-2">
              <span className={`w-2 h-2 rounded-full ${loggingInfo.files_exist.frontend_error ? 'bg-green-500' : 'bg-gray-300'}`}></span>
              <span>Frontend Errors: <code>{loggingInfo.frontend_error_file}</code></span>
            </div>
            <div className="flex items-center space-x-2">
              <span className={`w-2 h-2 rounded-full ${loggingInfo.files_exist.backend_log ? 'bg-green-500' : 'bg-gray-300'}`}></span>
              <span>Backend: <code>{loggingInfo.backend_log_file}</code></span>
            </div>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex space-x-2 mb-4">
        <button
          onClick={testConnection}
          disabled={isLoading}
          className="px-3 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {isLoading ? 'Testing...' : 'Test Connection'}
        </button>
        
        <button
          onClick={sendTestLogs}
          className="px-3 py-2 bg-green-600 text-white text-sm rounded hover:bg-green-700"
        >
          Send Test Logs
        </button>
        
        <button
          onClick={clearLogs}
          className="px-3 py-2 bg-gray-600 text-white text-sm rounded hover:bg-gray-700"
        >
          Clear Logs
        </button>
        
        <button
          onClick={fetchLoggingInfo}
          className="px-3 py-2 bg-purple-600 text-white text-sm rounded hover:bg-purple-700"
        >
          Refresh Info
        </button>
      </div>

      {/* Recent Logs */}
      {logs.length > 0 && (
        <div className="mt-4">
          <h4 className="text-sm font-medium text-gray-900 mb-2">Recent Test Logs:</h4>
          <div className="bg-gray-50 p-3 rounded text-xs font-mono max-h-32 overflow-y-auto">
            {logs.slice(-10).map((log, index) => (
              <div key={index} className="mb-1">
                <span className={`font-semibold ${
                  log.level === 'error' ? 'text-red-600' :
                  log.level === 'warn' ? 'text-yellow-600' :
                  'text-blue-600'
                }`}>
                  [{log.level.toUpperCase()}]
                </span>
                <span className="text-gray-600 ml-2">
                  {new Date(log.timestamp).toLocaleTimeString()}
                </span>
                <span className="ml-2">{log.message}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="mt-4 p-3 bg-blue-50 rounded text-xs text-blue-800">
        <p className="font-medium mb-1">Frontend Logging Information:</p>
        <ul className="list-disc list-inside space-y-1">
          <li>Warning and Error logs are automatically sent to the backend</li>
          <li>Check the browser console for all log levels during development</li>
          <li>Frontend logs are stored separately in: <code>backend/logs/notion-email-frontend-YYYY-MM-DD.log</code></li>
          <li>Backend logs are stored in: <code>backend/logs/notion-email-backend-YYYY-MM-DD.log</code></li>
          <li>Error logs are also written to: <code>*-error-YYYY-MM-DD.log</code> files</li>
        </ul>
      </div>
    </div>
  );
};

export default LoggingStatus;

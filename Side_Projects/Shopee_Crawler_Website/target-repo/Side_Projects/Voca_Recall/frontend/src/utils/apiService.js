import { apiLogger } from './logger';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  /**
   * Get auth token from localStorage
   */
  getAuthToken() {
    return localStorage.getItem('token');
  }

  /**
   * Get common headers
   */
  getHeaders(includeAuth = true) {
    const headers = {
      'Content-Type': 'application/json',
    };

    if (includeAuth) {
      const token = this.getAuthToken();
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      }
    }

    return headers;
  }

  /**
   * Make HTTP request with logging
   */
  async request(method, endpoint, data = null, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const startTime = Date.now();
    
    // Log request
    apiLogger.apiCall(method, endpoint, data);

    const config = {
      method: method.toUpperCase(),
      headers: this.getHeaders(options.includeAuth !== false),
      ...options,
    };

    if (data && ['POST', 'PUT', 'PATCH'].includes(config.method)) {
      config.body = JSON.stringify(data);
    }

    try {
      const response = await fetch(url, config);
      const responseTime = Date.now() - startTime;
      
      let responseData = null;
      const contentType = response.headers.get('content-type');
      
      if (contentType && contentType.includes('application/json')) {
        responseData = await response.json();
      } else {
        responseData = await response.text();
      }

      // Log response
      apiLogger.apiResponse(method, endpoint, response.status, responseData, responseTime);

      if (!response.ok) {
        throw new Error(responseData?.error || responseData?.message || `HTTP ${response.status}`);
      }

      return {
        data: responseData,
        status: response.status,
        headers: response.headers,
      };
    } catch (error) {
      const responseTime = Date.now() - startTime;
      
      // Log error
      apiLogger.error(`API ${method.toUpperCase()} ${endpoint} failed`, error, {
        responseTime: `${responseTime}ms`,
        requestData: data
      });
      
      throw error;
    }
  }

  /**
   * GET request
   */
  async get(endpoint, options = {}) {
    return this.request('GET', endpoint, null, options);
  }

  /**
   * POST request
   */
  async post(endpoint, data, options = {}) {
    return this.request('POST', endpoint, data, options);
  }

  /**
   * PUT request
   */
  async put(endpoint, data, options = {}) {
    return this.request('PUT', endpoint, data, options);
  }

  /**
   * DELETE request
   */
  async delete(endpoint, options = {}) {
    return this.request('DELETE', endpoint, null, options);
  }

  // Auth endpoints
  async login(email, password) {
    try {
      apiLogger.info('Attempting user login', { email });
      const response = await this.post('/auth/login', { email, password }, { includeAuth: false });
      apiLogger.info('User login successful', { email });
      return response;
    } catch (error) {
      apiLogger.error('User login failed', error, { email });
      throw error;
    }
  }

  async register(userData) {
    try {
      apiLogger.info('Attempting user registration', { email: userData.email });
      const response = await this.post('/auth/register', userData, { includeAuth: false });
      apiLogger.info('User registration successful', { email: userData.email });
      return response;
    } catch (error) {
      apiLogger.error('User registration failed', error, { email: userData.email });
      throw error;
    }
  }

  async refreshToken() {
    try {
      apiLogger.debug('Refreshing auth token');
      const response = await this.post('/auth/refresh');
      apiLogger.debug('Auth token refreshed successfully');
      return response;
    } catch (error) {
      apiLogger.error('Token refresh failed', error);
      throw error;
    }
  }

  async forgotPassword(email) {
    try {
      apiLogger.info('Requesting password reset', { email });
      const response = await this.post('/auth/forgot-password', { email }, { includeAuth: false });
      apiLogger.info('Password reset request successful', { email });
      return response;
    } catch (error) {
      apiLogger.error('Password reset request failed', error, { email });
      throw error;
    }
  }

  async resetPassword(token, password) {
    try {
      apiLogger.info('Attempting password reset');
      const response = await this.post('/auth/reset-password', { token, password }, { includeAuth: false });
      apiLogger.info('Password reset successful');
      return response;
    } catch (error) {
      apiLogger.error('Password reset failed', error);
      throw error;
    }
  }

  async validateResetToken(token) {
    try {
      apiLogger.debug('Validating password reset token');
      const response = await this.post('/auth/validate-reset-token', { token }, { includeAuth: false });
      apiLogger.debug('Password reset token validation completed');
      return response;
    } catch (error) {
      apiLogger.error('Password reset token validation failed', error);
      throw error;
    }
  }

  // User endpoints
  async getUserProfile() {
    try {
      apiLogger.debug('Fetching user profile');
      const response = await this.get('/user/profile');
      apiLogger.debug('User profile fetched successfully');
      return response;
    } catch (error) {
      apiLogger.error('Failed to fetch user profile', error);
      throw error;
    }
  }

  async updateUserProfile(userData) {
    try {
      apiLogger.info('Updating user profile');
      const response = await this.put('/user/profile', userData);
      apiLogger.info('User profile updated successfully');
      return response;
    } catch (error) {
      apiLogger.error('Failed to update user profile', error);
      throw error;
    }
  }

  // Database endpoints
  async getDatabases() {
    try {
      apiLogger.debug('Fetching user databases');
      const response = await this.get('/databases');
      apiLogger.debug(`Fetched ${response.data?.databases?.length || 0} databases`);
      return response;
    } catch (error) {
      apiLogger.error('Failed to fetch databases', error);
      throw error;
    }
  }

  async addDatabase(databaseData) {
    try {
      apiLogger.info('Adding new database', { databaseUrl: databaseData.database_url });
      const response = await this.post('/databases', databaseData);
      apiLogger.info('Database added successfully', { databaseId: response.data?.database?.id });
      return response;
    } catch (error) {
      apiLogger.error('Failed to add database', error, { databaseUrl: databaseData.database_url });
      throw error;
    }
  }

  async updateDatabase(databaseId, databaseData) {
    try {
      apiLogger.info('Updating database', { databaseId });
      const response = await this.put(`/databases/${databaseId}`, databaseData);
      apiLogger.info('Database updated successfully', { databaseId });
      return response;
    } catch (error) {
      apiLogger.error('Failed to update database', error, { databaseId });
      throw error;
    }
  }

  async deleteDatabase(databaseId) {
    try {
      apiLogger.info('Deleting database', { databaseId });
      const response = await this.delete(`/databases/${databaseId}`);
      apiLogger.info('Database deleted successfully', { databaseId });
      return response;
    } catch (error) {
      apiLogger.error('Failed to delete database', error, { databaseId });
      throw error;
    }
  }

  // Email endpoints
  async sendTestEmail(emailData) {
    try {
      apiLogger.info('Sending test email');
      const response = await this.post('/email/send-test', emailData);
      apiLogger.info('Test email sent successfully');
      return response;
    } catch (error) {
      apiLogger.error('Failed to send test email', error);
      throw error;
    }
  }

  async getEmailLogs(page = 1, perPage = 10) {
    try {
      apiLogger.debug('Fetching email logs', { page, perPage });
      const response = await this.get(`/email/logs?page=${page}&per_page=${perPage}`);
      apiLogger.debug('Email logs fetched successfully');
      return response;
    } catch (error) {
      apiLogger.error('Failed to fetch email logs', error);
      throw error;
    }
  }

  // Settings endpoints
  async getSettings() {
    try {
      apiLogger.debug('Fetching user settings');
      const response = await this.get('/settings');
      apiLogger.debug('User settings fetched successfully');
      return response;
    } catch (error) {
      apiLogger.error('Failed to fetch settings', error);
      throw error;
    }
  }

  async updateSettings(settings) {
    try {
      apiLogger.info('Updating user settings');
      const response = await this.put('/settings', settings);
      apiLogger.info('User settings updated successfully');
      return response;
    } catch (error) {
      apiLogger.error('Failed to update settings', error);
      throw error;
    }
  }
}

// Create and export singleton instance
const apiService = new ApiService();
export default apiService;

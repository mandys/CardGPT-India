import axios, { AxiosInstance, AxiosError } from 'axios';
import { 
  ChatRequest, 
  ChatResponse, 
  ConfigResponse, 
  ApiError,
  UserPreferences,
  UserPreferenceRequest,
  UserPreferenceResponse
} from '../types';

class ApiClient {
  private client: AxiosInstance;
  private baseURL: string;

  constructor(baseURL: string = process.env.REACT_APP_API_URL || 'http://localhost:8000') {
    this.baseURL = baseURL;
    this.client = axios.create({
      baseURL: `${baseURL}/api`,
      timeout: 30000, // 30 second timeout
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('❌ API Request Error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        console.log(`✅ API Response: ${response.status} ${response.config.url}`);
        return response;
      },
      (error: AxiosError) => {
        console.error('❌ API Response Error:', error.response?.status, error.response?.data);
        return Promise.reject(this.handleError(error));
      }
    );
  }

  private handleError(error: AxiosError): ApiError {
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      return {
        error: (data as any)?.error || `HTTP Error ${status}`,
        detail: (data as any)?.detail || error.message,
        code: status.toString(),
        timestamp: new Date().toISOString(),
      };
    } else if (error.request) {
      // Network error
      return {
        error: 'Network Error',
        detail: 'Unable to connect to the server. Please check your connection.',
        code: 'NETWORK_ERROR',
        timestamp: new Date().toISOString(),
      };
    } else {
      // Other error
      return {
        error: 'Unknown Error',
        detail: error.message || 'An unexpected error occurred',
        code: 'UNKNOWN_ERROR',
        timestamp: new Date().toISOString(),
      };
    }
  }

  /**
   * Health check endpoint
   */
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }

  /**
   * Get API configuration
   */
  async getConfig(): Promise<ConfigResponse> {
    const response = await this.client.get('/config');
    return response.data;
  }

  /**
   * Get available models
   */
  async getModels() {
    const response = await this.client.get('/models');
    return response.data;
  }

  /**
   * Get supported credit cards
   */
  async getCards(): Promise<{ cards: string[] }> {
    const response = await this.client.get('/cards');
    return response.data;
  }

  /**
   * Send chat message
   */
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await this.client.post('/chat', request);
    return response.data;
  }

  /**
   * Enhance query (optional endpoint)
   */
  async enhanceQuery(query: string): Promise<{ enhanced_query: string; metadata: any }> {
    const response = await this.client.post('/query/enhance', { query });
    return response.data;
  }

  /**
   * Test connection to the API
   */
  async testConnection(): Promise<boolean> {
    try {
      await this.healthCheck();
      return true;
    } catch (error) {
      console.error('Connection test failed:', error);
      return false;
    }
  }

  // User Preference Methods

  /**
   * Get user preferences (authenticated users only)
   */
  async getUserPreferences(clerkToken?: string): Promise<UserPreferenceResponse> {
    const token = clerkToken || localStorage.getItem('jwt_token');
    if (!token) {
      throw new Error('Authentication required');
    }

    const response = await this.client.get('/preferences', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    return response.data;
  }

  /**
   * Create or update user preferences (authenticated users only)
   */
  async updateUserPreferences(preferences: UserPreferences, clerkToken?: string): Promise<UserPreferenceResponse> {
    const token = clerkToken || localStorage.getItem('jwt_token');
    if (!token) {
      throw new Error('Authentication required');
    }

    const request: UserPreferenceRequest = { preferences };
    const response = await this.client.post('/preferences', request, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    return response.data;
  }

  /**
   * Clear user preferences (authenticated users only)
   */
  async clearUserPreferences(clerkToken?: string): Promise<{ success: boolean; message: string }> {
    const token = clerkToken || localStorage.getItem('jwt_token');
    if (!token) {
      throw new Error('Authentication required');
    }

    const response = await this.client.delete('/preferences', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    return response.data;
  }

  /**
   * Save session preferences (anonymous users)
   */
  async saveSessionPreferences(preferences: UserPreferences, sessionId?: string): Promise<{ success: boolean; session_id: string; message: string }> {
    const request: UserPreferenceRequest = { 
      preferences,
      session_id: sessionId 
    };
    const response = await this.client.post('/preferences/session', request);
    return response.data;
  }

  /**
   * Get session preferences (anonymous users)
   */
  async getSessionPreferences(sessionId: string): Promise<UserPreferences> {
    const response = await this.client.get(`/preferences/session/${sessionId}`);
    return response.data;
  }


  /**
   * Helper method to get session ID from localStorage
   */
  getSessionId(): string {
    let sessionId = localStorage.getItem('session_id');
    if (!sessionId) {
      sessionId = 'session_' + Math.random().toString(36).substring(2, 15);
      localStorage.setItem('session_id', sessionId);
    }
    return sessionId;
  }

  /**
   * Get preferences for current user (authenticated or session-based)
   */
  async getCurrentUserPreferences(clerkToken?: string): Promise<UserPreferences | null> {
    try {
      if (clerkToken) {
        // Clerk authenticated user - use the provided token
        const response = await this.getUserPreferences(clerkToken);
        return response.preferences;
      } else {
        // Check if we have legacy JWT token (fallback for transition period)
        const legacyToken = localStorage.getItem('jwt_token');
        if (legacyToken) {
          try {
            const response = await this.getUserPreferences(legacyToken);
            return response.preferences;
          } catch (error) {
            // Legacy token invalid, fall back to session
            console.log('Legacy JWT token invalid, falling back to session mode');
            localStorage.removeItem('jwt_token'); // Clean up invalid token
          }
        }
        
        // Anonymous/session user
        const sessionId = this.getSessionId();
        return await this.getSessionPreferences(sessionId);
      }
    } catch (error) {
      // Enhanced error handling with proper fallback
      if (error instanceof Error) {
        console.warn('Failed to load preferences:', error.message);
        if (error.message.includes('401') || error.message.includes('unauthorized')) {
          // Authentication error - clean up and fall back to session
          localStorage.removeItem('jwt_token');
          try {
            const sessionId = this.getSessionId();
            return await this.getSessionPreferences(sessionId);
          } catch (sessionError) {
            console.log('No session preferences found, starting fresh');
            return null;
          }
        }
      }
      console.log('No preferences found or error retrieving preferences');
      return null;
    }
  }

  /**
   * Save preferences for current user (authenticated or session-based)
   */
  async saveCurrentUserPreferences(preferences: UserPreferences, clerkToken?: string): Promise<boolean> {
    try {
      if (clerkToken) {
        // Clerk authenticated user
        await this.updateUserPreferences(preferences, clerkToken);
        return true;
      }

      // Check for legacy JWT token
      const legacyToken = localStorage.getItem('jwt_token');
      if (legacyToken) {
        try {
          await this.updateUserPreferences(preferences, legacyToken);
          return true;
        } catch (error) {
          // Legacy token invalid, clean up and fall back to session
          console.log('Legacy JWT token invalid during save, falling back to session mode');
          localStorage.removeItem('jwt_token');
        }
      }

      // Fall back to session-based saving
      const sessionId = this.getSessionId();
      await this.saveSessionPreferences(preferences, sessionId);
      return true;
    } catch (error) {
      // Enhanced error handling
      if (error instanceof Error) {
        console.error('Failed to save preferences:', error.message);
        if (error.message.includes('401') || error.message.includes('unauthorized')) {
          // Authentication error - try session fallback
          try {
            const sessionId = this.getSessionId();
            await this.saveSessionPreferences(preferences, sessionId);
            console.log('Saved to session after authentication error');
            return true;
          } catch (sessionError) {
            console.error('Session fallback also failed:', sessionError);
          }
        }
      } else {
        console.error('Failed to save preferences:', error);
      }
      return false;
    }
  }
}

// Create and export a singleton instance
export const apiClient = new ApiClient();

// Export the class for custom instances
export default ApiClient;
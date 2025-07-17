import axios, { AxiosInstance, AxiosError } from 'axios';
import { ChatRequest, ChatResponse, ConfigResponse, ApiError } from '../types';

class ApiClient {
  private client: AxiosInstance;
  private baseURL: string;

  constructor(baseURL: string = 'http://localhost:8000') {
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
}

// Create and export a singleton instance
export const apiClient = new ApiClient();

// Export the class for custom instances
export default ApiClient;
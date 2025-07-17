import { create } from 'zustand';
import { ChatMessage, ApiError, AppSettings, QueryMode, CardFilter } from '../types';
import { apiClient } from '../services/api';
import { generateMessageId } from '../utils/formatMessage';

interface ChatState {
  // Messages
  messages: ChatMessage[];
  isLoading: boolean;
  error: ApiError | null;
  
  // Settings
  settings: AppSettings;
  
  // Config
  config: any;
  
  // Actions
  sendMessage: (message: string) => Promise<void>;
  clearMessages: () => void;
  setSettings: (settings: Partial<AppSettings>) => void;
  loadConfig: () => Promise<void>;
  setError: (error: ApiError | null) => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  // Initial state
  messages: [],
  isLoading: false,
  error: null,
  
  settings: {
    selectedModel: 'gemini-1.5-pro',
    queryMode: 'General Query' as QueryMode,
    cardFilter: 'None' as CardFilter,
    topK: 7,
    darkMode: false,
  },
  
  config: null,
  
  // Actions
  sendMessage: async (message: string) => {
    const state = get();
    
    // Add user message
    const userMessage: ChatMessage = {
      id: generateMessageId(),
      role: 'user',
      content: message,
      timestamp: new Date(),
    };
    
    set({
      messages: [...state.messages, userMessage],
      isLoading: true,
      error: null,
    });
    
    try {
      // Send to API
      const response = await apiClient.sendMessage({
        message,
        model: state.settings.selectedModel,
        query_mode: state.settings.queryMode,
        card_filter: state.settings.cardFilter === 'None' ? undefined : state.settings.cardFilter,
        top_k: state.settings.topK,
      });
      
      // Add assistant response
      const assistantMessage: ChatMessage = {
        id: generateMessageId(),
        role: 'assistant',
        content: response.answer,
        timestamp: new Date(),
      };
      
      set({
        messages: [...get().messages, assistantMessage],
        isLoading: false,
      });
      
    } catch (error) {
      const apiError = error as ApiError;
      
      // Add error message
      const errorMessage: ChatMessage = {
        id: generateMessageId(),
        role: 'assistant',
        content: `❌ Error: ${apiError.error}\n\n${apiError.detail || 'Please try again or check your connection.'}`,
        timestamp: new Date(),
      };
      
      set({
        messages: [...get().messages, errorMessage],
        isLoading: false,
        error: apiError,
      });
    }
  },
  
  clearMessages: () => {
    set({
      messages: [],
      error: null,
    });
  },
  
  setSettings: (newSettings: Partial<AppSettings>) => {
    set({
      settings: { ...get().settings, ...newSettings },
    });
  },
  
  loadConfig: async () => {
    try {
      const config = await apiClient.getConfig();
      set({ config });
    } catch (error) {
      console.error('Failed to load config:', error);
      set({ error: error as ApiError });
    }
  },
  
  setError: (error: ApiError | null) => {
    set({ error });
  },
}));
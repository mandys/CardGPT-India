import { create } from 'zustand';
import { ChatMessage, ApiError, AppSettings, QueryMode, CardFilter } from '../types';
import { streamingApiClient, StreamingChatResponse } from '../services/streamingApi';
import { generateMessageId } from '../utils/formatMessage';

interface StreamingChatState {
  // Messages
  messages: ChatMessage[];
  isLoading: boolean;
  isStreaming: boolean;
  currentStatus: string | null;
  error: ApiError | null;
  
  // Settings
  settings: AppSettings;
  
  // Config
  config: any;
  
  // Actions
  sendMessageStream: (message: string) => Promise<void>;
  clearMessages: () => void;
  setSettings: (settings: Partial<AppSettings>) => void;
  loadConfig: () => Promise<void>;
  setError: (error: ApiError | null) => void;
}

export const useStreamingChatStore = create<StreamingChatState>((set, get) => ({
  // Initial state
  messages: [],
  isLoading: false,
  isStreaming: false,
  currentStatus: null,
  error: null,
  
  settings: {
    selectedModel: 'gemini-1.5-flash',  // Ultra-fast default for streaming
    queryMode: 'General Query' as QueryMode,
    cardFilter: 'None' as CardFilter,
    topK: 7,
    darkMode: false,
  },
  
  config: null,
  
  // Actions
  sendMessageStream: async (message: string) => {
    const state = get();
    
    // Add user message
    const userMessage: ChatMessage = {
      id: generateMessageId(),
      role: 'user',
      content: message,
      timestamp: new Date(),
    };
    
    // Add placeholder assistant message for streaming
    const assistantMessageId = generateMessageId();
    const assistantMessage: ChatMessage = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      metadata: { isStreaming: true },
    };
    
    set({
      messages: [...state.messages, userMessage, assistantMessage],
      isLoading: true,
      isStreaming: true,
      currentStatus: null,
      error: null,
    });
    
    try {
      await streamingApiClient.sendMessageStream(
        {
          message,
          model: state.settings.selectedModel,
          query_mode: state.settings.queryMode,
          card_filter: state.settings.cardFilter === 'None' ? undefined : state.settings.cardFilter,
          top_k: state.settings.topK,
        },
        // onChunk: Update message content progressively
        (chunk: string) => {
          set((state) => ({
            messages: state.messages.map((msg) =>
              msg.id === assistantMessageId
                ? { ...msg, content: msg.content + chunk }
                : msg
            ),
            currentStatus: null, // Clear status when content starts flowing
          }));
        },
        // onComplete: Add final metadata
        (response: StreamingChatResponse) => {
          set((state) => ({
            messages: state.messages.map((msg) =>
              msg.id === assistantMessageId
                ? {
                    ...msg,
                    content: response.answer,
                    metadata: {
                      ...response.metadata,
                      isStreaming: false,
                      isComplete: true,
                    },
                    // Add debug information
                    sources: response.sources,
                    embedding_usage: response.embedding_usage,
                    llm_usage: response.llm_usage,
                    total_cost: response.total_cost,
                    enhanced_question: response.enhanced_question,
                  }
                : msg
            ),
            isLoading: false,
            isStreaming: false,
            currentStatus: null, // Clear status when complete
          }));
        },
        // onError: Handle errors
        (error: string) => {
          const apiError: ApiError = {
            error: 'Streaming Error',
            detail: error,
            timestamp: new Date().toISOString(),
          };
          
          // Update assistant message with error
          set((state) => ({
            messages: state.messages.map((msg) =>
              msg.id === assistantMessageId
                ? {
                    ...msg,
                    content: `❌ Error: ${error}\n\nPlease try again or check your connection.`,
                    metadata: { isStreaming: false, isError: true },
                  }
                : msg
            ),
            isLoading: false,
            isStreaming: false,
            currentStatus: null,
            error: apiError,
          }));
        },
        // onStatus: Update current status (replace, don't append)
        (status: string) => {
          set({ currentStatus: status });
          
          // Clear status when real content starts (if status contains emojis but content doesn't)
          if (!status.includes('🔍') && !status.includes('📊') && !status.includes('🤖')) {
            // This is actual content, clear status
            setTimeout(() => set({ currentStatus: null }), 100);
          }
        }
      );
    } catch (error) {
      const apiError = error as ApiError;
      
      // Update assistant message with error
      set((state) => ({
        messages: state.messages.map((msg) =>
          msg.id === assistantMessageId
            ? {
                ...msg,
                content: `❌ Error: ${apiError.error}\n\n${apiError.detail || 'Please try again or check your connection.'}`,
                metadata: { isStreaming: false, isError: true },
              }
            : msg
        ),
        isLoading: false,
        isStreaming: false,
        currentStatus: null,
        error: apiError,
      }));
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
      // Use regular API client for config
      const { apiClient } = await import('../services/api');
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
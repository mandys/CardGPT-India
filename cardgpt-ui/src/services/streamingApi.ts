import { ChatRequest, DocumentSource, UsageInfo } from '../types';

export interface StreamChunk {
  type: 'chunk' | 'complete' | 'error' | 'status';
  content?: string;
  sources?: DocumentSource[];
  embedding_usage?: UsageInfo;
  llm_usage?: UsageInfo;
  total_cost?: number;
  enhanced_question?: string;
  metadata?: Record<string, any>;
}

export interface StreamingChatResponse {
  answer: string;
  sources: DocumentSource[];
  embedding_usage: UsageInfo;
  llm_usage: UsageInfo;
  total_cost: number;
  enhanced_question: string;
  metadata: Record<string, any>;
}

export class StreamingApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  }

  async sendMessageStream(
    request: ChatRequest,
    onChunk: (chunk: string) => void,
    onComplete: (response: StreamingChatResponse) => void,
    onError: (error: string) => void,
    onStatus?: (status: string) => void
  ): Promise<void> {
    try {
      // Prepare headers with authentication if available
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };

      // Add JWT authorization header if user is authenticated
      const token = localStorage.getItem('jwt_token');
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
        console.log(`🔐 [STREAMING] Including JWT token in request: ${token.substring(0, 20)}...`);
      } else {
        console.log(`🔓 [STREAMING] No JWT token found - using session-based preferences`);
      }

      const response = await fetch(`${this.baseUrl}/api/chat/stream`, {
        method: 'POST',
        headers,
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('Failed to get response reader');
      }

      const decoder = new TextDecoder();
      let buffer = '';
      let fullAnswer = '';

      try {
        while (true) {
          const { done, value } = await reader.read();
          
          if (done) {
            break;
          }

          buffer += decoder.decode(value, { stream: true });
          
          // Process complete lines
          const lines = buffer.split('\n');
          buffer = lines.pop() || ''; // Keep incomplete line in buffer

          for (const line of lines) {
            if (line.trim() === '') continue;
            
            if (line.startsWith('data: ')) {
              const data = line.slice(6);
              
              if (data === '[DONE]') {
                return; // Stream completed
              }

              try {
                const chunk: StreamChunk = JSON.parse(data);
                console.log('Received chunk:', chunk); // Debug logging
                
                switch (chunk.type) {
                  case 'status':
                    // Handle status messages separately
                    if (chunk.content && onStatus) {
                      onStatus(chunk.content);
                    }
                    break;
                    
                  case 'chunk':
                    if (chunk.content) {
                      // Filter out status messages that might be in content
                      const isStatusMessage = chunk.content.includes('🔍') || 
                                            chunk.content.includes('📊') || 
                                            chunk.content.includes('🤖');
                      
                      if (!isStatusMessage) {
                        fullAnswer += chunk.content;
                        onChunk(chunk.content);
                      } else if (onStatus) {
                        onStatus(chunk.content);
                      }
                    }
                    break;
                    
                  case 'complete':
                    // Final response with metadata
                    const completeResponse: StreamingChatResponse = {
                      answer: fullAnswer,
                      sources: chunk.sources || [],
                      embedding_usage: chunk.embedding_usage || { tokens: 0, cost: 0, model: 'vertex-ai-search' },
                      llm_usage: chunk.llm_usage || { tokens: 0, cost: 0, model: 'unknown' },
                      total_cost: chunk.total_cost || 0,
                      enhanced_question: chunk.enhanced_question || '',
                      metadata: chunk.metadata || {}
                    };
                    
                    onComplete(completeResponse);
                    break;
                    
                  case 'error':
                    onError(chunk.content || 'Unknown streaming error');
                    return;
                }
              } catch (parseError) {
                console.error('Failed to parse chunk:', parseError);
                console.error('Raw data:', data);
                // Don't break the stream for parsing errors, continue processing
              }
            }
          }
        }
      } finally {
        reader.releaseLock();
      }
    } catch (error) {
      console.error('Streaming error:', error);
      onError(error instanceof Error ? error.message : 'Unknown streaming error');
    }
  }
}

// Export singleton instance
export const streamingApiClient = new StreamingApiClient();
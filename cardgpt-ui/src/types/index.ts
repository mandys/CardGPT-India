// TypeScript types for the Credit Card Assistant

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  metadata?: Record<string, any>;
  // Debug information for assistant messages
  sources?: DocumentSource[];
  embedding_usage?: UsageInfo;
  llm_usage?: UsageInfo;
  total_cost?: number;
  enhanced_question?: string;
}

export interface ChatRequest {
  message: string;
  model: string;
  query_mode: string;
  card_filter?: string;
  top_k: number;
}

export interface DocumentSource {
  cardName: string;
  section: string;
  content: string;
  similarity: number;
}

export interface UsageInfo {
  tokens: number;
  cost: number;
  model: string;
  input_tokens?: number;
  output_tokens?: number;
  total_tokens?: number;
}

export interface ChatResponse {
  answer: string;
  sources: DocumentSource[];
  embedding_usage: UsageInfo;
  llm_usage: UsageInfo;
  total_cost: number;
  enhanced_question: string;
  metadata: Record<string, any>;
}

export interface ModelInfo {
  name: string;
  provider: string;
  cost_per_1k_input: number;
  cost_per_1k_output: number;
  available: boolean;
  description: string;
}

export interface ConfigResponse {
  available_models: ModelInfo[];
  supported_cards: string[];
  default_model: string;
  max_top_k: number;
}

export interface ApiError {
  error: string;
  detail?: string;
  code?: string;
  timestamp: string;
}

export interface AppSettings {
  selectedModel: string;
  queryMode: QueryMode;
  cardFilter: CardFilter;
  topK: number;
  darkMode: boolean;
}

export interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  config: ConfigResponse | null;
}

export type QueryMode = 'General Query' | 'Specific Card' | 'Compare Cards';
export type CardFilter = 'None' | 'Axis Atlas' | 'ICICI EPM' | 'HSBC Premier';
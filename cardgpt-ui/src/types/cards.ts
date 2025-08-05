/**
 * Centralized Card Configuration Types
 * Generated from backend card configuration system
 */

export interface CardColorScheme {
  primary: string;
  secondary: string;
  gradient: string;
}

export interface CategoryInfo {
  status: 'included' | 'excluded' | 'capped';
  description: string;
}

export interface MilestoneReward {
  threshold: number;
  reward: number;
  currency: string;
}

export interface CardConfig {
  id: string;
  display_name: string;
  full_name: string;
  jsonl_name: string;
  short_name: string;
  bank: string;
  aliases: string[];
  reward_currency: string;
  reward_format: string;
  color_scheme: CardColorScheme;
  category_info: Record<string, CategoryInfo>;
  milestones?: {
    annual: MilestoneReward[];
  };
  travel_benefits?: Record<string, any>;
  accelerated_categories?: Record<string, any>;
  general_earning?: Record<string, any>;
  active: boolean;
  priority: number;
}

export interface CardsResponse {
  cards: CardConfig[];
  total_count: number;
  version: string;
}

export interface CardDisplayNamesResponse {
  display_names: string[];
  filter_options: string[];
}

export interface CategoryInfoResponse {
  category: string;
  summary?: string;
  cards: Record<string, CategoryInfo>;
}

// Type for card filter dropdown (backwards compatible)
export type CardFilter = 'None' | string;

// Helper type for generating CardFilter from config
export type CardFilterFromConfig<T extends readonly string[]> = 'None' | T[number];

// Configuration API endpoints
export interface CardConfigAPI {
  getAllCards(): Promise<CardsResponse>;
  getDisplayNames(): Promise<CardDisplayNamesResponse>;
  getCardById(cardId: string): Promise<{ card: CardConfig }>;
  searchCards(searchText: string): Promise<{ cards: CardConfig[]; search_text: string; matches_found: number }>;
  getCategoryInfo(category: string): Promise<CategoryInfoResponse>;
  reloadConfig(): Promise<{ status: string; message: string }>;
}
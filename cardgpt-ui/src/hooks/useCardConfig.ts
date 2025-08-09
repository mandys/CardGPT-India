/**
 * Card Configuration Hook
 * Provides centralized access to card configuration data from backend
 */

import { useState, useEffect, useCallback } from 'react';
import { 
  CardConfig, 
  CardsResponse, 
  CardDisplayNamesResponse, 
  CategoryInfoResponse,
  CardFilter 
} from '../types/cards';

// API base URL - use environment variable with fallback
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

interface UseCardConfigState {
  cards: CardConfig[];
  displayNames: string[];
  filterOptions: CardFilter[];
  loading: boolean;
  error: string | null;
  version: string;
}

interface UseCardConfigReturn extends UseCardConfigState {
  refreshConfig: () => Promise<void>;
  getCardById: (cardId: string) => CardConfig | undefined;
  getCardByDisplayName: (displayName: string) => CardConfig | undefined;
  searchCards: (searchText: string) => CardConfig[];
  getCategoryInfo: (category: string) => Promise<CategoryInfoResponse | null>;
}

export const useCardConfig = (): UseCardConfigReturn => {
  const [state, setState] = useState<UseCardConfigState>({
    cards: [],
    displayNames: [],
    filterOptions: ['None'],
    loading: true,
    error: null,
    version: 'unknown'
  });

  const fetchCardConfig = useCallback(async () => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));

      // Fetch all cards
      const cardsResponse = await fetch(`${API_BASE_URL}/api/cards`);
      if (!cardsResponse.ok) {
        throw new Error(`Failed to fetch cards: ${cardsResponse.statusText}`);
      }
      const cardsData: CardsResponse = await cardsResponse.json();

      // Fetch display names
      const displayNamesResponse = await fetch(`${API_BASE_URL}/api/cards/display-names`);
      if (!displayNamesResponse.ok) {
        throw new Error(`Failed to fetch display names: ${displayNamesResponse.statusText}`);
      }
      const displayNamesData: CardDisplayNamesResponse = await displayNamesResponse.json();

      setState({
        cards: cardsData.cards,
        displayNames: displayNamesData.display_names,
        filterOptions: displayNamesData.filter_options as CardFilter[],
        loading: false,
        error: null,
        version: cardsData.version
      });

    } catch (error) {
      console.error('Failed to fetch card configuration:', error);
      setState(prev => ({
        ...prev,
        loading: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      }));
    }
  }, []);

  const refreshConfig = useCallback(async () => {
    await fetchCardConfig();
  }, [fetchCardConfig]);

  const getCardById = useCallback((cardId: string): CardConfig | undefined => {
    return state.cards.find(card => card.id === cardId);
  }, [state.cards]);

  const getCardByDisplayName = useCallback((displayName: string): CardConfig | undefined => {
    return state.cards.find(card => card.display_name === displayName);
  }, [state.cards]);

  const searchCards = useCallback((searchText: string): CardConfig[] => {
    const searchLower = searchText.toLowerCase();
    return state.cards.filter(card => {
      // Check display name
      if (card.display_name.toLowerCase().includes(searchLower)) {
        return true;
      }
      // Check aliases
      return card.aliases.some(alias => alias.toLowerCase().includes(searchLower));
    });
  }, [state.cards]);

  const getCategoryInfo = useCallback(async (category: string): Promise<CategoryInfoResponse | null> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/cards/category/${category}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch category info: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error(`Failed to fetch category info for ${category}:`, error);
      return null;
    }
  }, []);

  // Load configuration on mount
  useEffect(() => {
    fetchCardConfig();
  }, [fetchCardConfig]);

  return {
    ...state,
    refreshConfig,
    getCardById,
    getCardByDisplayName,
    searchCards,
    getCategoryInfo
  };
};

// Hook for getting just the card display names (lightweight)
export const useCardDisplayNames = (): { 
  displayNames: string[]; 
  filterOptions: CardFilter[]; 
  loading: boolean; 
  error: string | null; 
} => {
  const [displayNames, setDisplayNames] = useState<string[]>([]);
  const [filterOptions, setFilterOptions] = useState<CardFilter[]>(['None']);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDisplayNames = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await fetch(`${API_BASE_URL}/api/cards/display-names`);
        if (!response.ok) {
          throw new Error(`Failed to fetch display names: ${response.statusText}`);
        }
        
        const data: CardDisplayNamesResponse = await response.json();
        setDisplayNames(data.display_names);
        setFilterOptions(data.filter_options as CardFilter[]);
      } catch (err) {
        console.error('Failed to fetch card display names:', err);
        setError(err instanceof Error ? err.message : 'Unknown error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchDisplayNames();
  }, []);

  return { displayNames, filterOptions, loading, error };
};

// Utility function to get card color scheme
export const getCardColorScheme = (cardConfig: CardConfig | undefined): { primary: string; secondary: string; gradient: string } => {
  if (!cardConfig?.color_scheme) {
    return {
      primary: 'from-gray-500 to-gray-600',
      secondary: 'gray',
      gradient: 'from-gray-500 to-gray-600'
    };
  }
  return cardConfig.color_scheme;
};

// Utility function to format card display name
export const formatCardDisplayName = (cardConfig: CardConfig | undefined): string => {
  return cardConfig?.display_name || 'Unknown Card';
};
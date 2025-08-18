import { useEffect, useCallback } from 'react';
import { usePreferenceStore } from '../stores/usePreferenceStore';
import { useUser, useAuth } from '@clerk/clerk-react';
import { UserPreferences } from '../types';

/**
 * Custom hook that integrates preference store with authentication context
 * Provides a unified interface for preference management across the app
 */
export const usePreferences = () => {
  const { isSignedIn } = useUser();
  const { getToken } = useAuth();
  
  // Zustand store selectors
  const preferences = usePreferenceStore((state) => state.preferences);
  const isLoading = usePreferenceStore((state) => state.isLoading);
  const error = usePreferenceStore((state) => state.error);
  const hasLoadedInitial = usePreferenceStore((state) => state.hasLoadedInitial);
  const completion = usePreferenceStore((state) => state.completion);
  
  // Zustand store actions
  const loadPreferences = usePreferenceStore((state) => state.loadPreferences);
  const storeUpdatePreference = usePreferenceStore((state) => state.updatePreference);
  const storeUpdatePreferences = usePreferenceStore((state) => state.updatePreferences);
  const clearPreferences = usePreferenceStore((state) => state.clearPreferences);
  const applyRefinementButton = usePreferenceStore((state) => state.applyRefinementButton);
  const hasPreferences = usePreferenceStore((state) => state.hasPreferences);
  const isPreferenceComplete = usePreferenceStore((state) => state.isPreferenceComplete);
  const syncWithAuth = usePreferenceStore((state) => state.syncWithAuth);

  // Sync preferences when authentication state changes
  useEffect(() => {
    if (hasLoadedInitial) {
      syncWithAuth(isSignedIn || false, getToken);
    }
  }, [isSignedIn, hasLoadedInitial, syncWithAuth, getToken]);

  // Helper function to get current user preferences for API calls
  const getPreferencesForAPI = useCallback((): UserPreferences | undefined => {
    return preferences || undefined;
  }, [preferences]);

  // Helper function to check if specific preference types exist
  const hasCompletePreferenceCategory = useCallback((category: 'travel' | 'financial' | 'cards' | 'spending') => {
    const categoryMap = {
      travel: 'travel_preferences',
      financial: 'financial_preferences', 
      cards: 'card_preferences',
      spending: 'spending_preferences'
    } as const;
    
    return isPreferenceComplete(categoryMap[category]);
  }, [isPreferenceComplete]);

  const shouldShowPreferencePrompt = useCallback((): boolean => {
    return completion.overall < 50;
  }, [completion.overall]);

  const getMissingPreferencesForQuery = useCallback((query: string): string[] => {
    const lowerCaseQuery = query.toLowerCase();
    const missing = [];

    if (lowerCaseQuery.includes('travel') || lowerCaseQuery.includes('lounge') || lowerCaseQuery.includes('trip')) {
      if (!preferences?.travel_type) missing.push('travel_type');
      if (!preferences?.lounge_access) missing.push('lounge_access');
    }
    if (lowerCaseQuery.includes('fee') || lowerCaseQuery.includes('cost') || lowerCaseQuery.includes('annual')) {
      if (!preferences?.fee_willingness) missing.push('fee_willingness');
    }
    if (lowerCaseQuery.includes('recommend') || lowerCaseQuery.includes('best card') || lowerCaseQuery.includes('suggest')) {
      if ((preferences?.spend_categories?.length ?? 0) === 0) missing.push('spend_categories');
    }

    // General check: if any preference is missing, add it to the list
    if (!preferences?.travel_type) missing.push('travel_type');
    if (!preferences?.lounge_access) missing.push('lounge_access');
    if (!preferences?.fee_willingness) missing.push('fee_willingness');
    if ((preferences?.spend_categories?.length ?? 0) === 0) missing.push('spend_categories');
    if ((preferences?.current_cards?.length ?? 0) === 0) missing.push('current_cards');
    if ((preferences?.preferred_banks?.length ?? 0) === 0) missing.push('preferred_banks');
    
    return missing;
  }, [preferences]);

  // Wrapper functions that include Clerk token
  const updatePreference = useCallback(async (key: keyof UserPreferences, value: any) => {
    const token = getToken ? await getToken() : undefined;
    return storeUpdatePreference(key, value, token || undefined);
  }, [storeUpdatePreference, getToken]);

  const updatePreferences = useCallback(async (preferences: Partial<UserPreferences>) => {
    const token = getToken ? await getToken() : undefined;
    return storeUpdatePreferences(preferences, token || undefined);
  }, [storeUpdatePreferences, getToken]);

  // Quick preference setters for common scenarios
  const quickSetTravelType = useCallback((type: 'domestic' | 'international' | 'both') => {
    return updatePreference('travel_type', type);
  }, [updatePreference]);

  const quickSetLoungeAccess = useCallback((access: 'solo' | 'with_guests' | 'family') => {
    return updatePreference('lounge_access', access);
  }, [updatePreference]);

  const quickSetFeeWillingness = useCallback((range: '0-1000' | '1000-5000' | '5000-10000' | '10000+') => {
    return updatePreference('fee_willingness', range);
  }, [updatePreference]);

  const addCurrentCard = useCallback((cardName: string) => {
    const currentCards = preferences?.current_cards || [];
    if (!currentCards.includes(cardName)) {
      return updatePreference('current_cards', [...currentCards, cardName]);
    }
    return Promise.resolve(true);
  }, [preferences?.current_cards, updatePreference]);

  const removeCurrentCard = useCallback((cardName: string) => {
    const currentCards = preferences?.current_cards || [];
    return updatePreference('current_cards', currentCards.filter(card => card !== cardName));
  }, [preferences?.current_cards, updatePreference]);

  const addSpendCategory = useCallback((category: string) => {
    const currentCategories = preferences?.spend_categories || [];
    if (!currentCategories.includes(category)) {
      return updatePreference('spend_categories', [...currentCategories, category]);
    }
    return Promise.resolve(true);
  }, [preferences?.spend_categories, updatePreference]);

  const removeSpendCategory = useCallback((category: string) => {
    const currentCategories = preferences?.spend_categories || [];
    return updatePreference('spend_categories', currentCategories.filter(cat => cat !== category));
  }, [preferences?.spend_categories, updatePreference]);

  return {
    // State
    preferences,
    isLoading,
    error,
    hasLoadedInitial,
    completion,
    
    // Core actions
    loadPreferences,
    updatePreference,
    updatePreferences,
    clearPreferences,
    applyRefinementButton,
    
    // Helper functions
    hasPreferences: hasPreferences(),
    hasCompletePreferenceCategory,
    shouldShowPreferencePrompt,
    getPreferencesForAPI,
    getMissingPreferencesForQuery,
    
    // Quick setters
    quickSetTravelType,
    quickSetLoungeAccess,
    quickSetFeeWillingness,
    addCurrentCard,
    removeCurrentCard,
    addSpendCategory,
    removeSpendCategory,
    
    // Status helpers
    isFullyComplete: completion.overall === 100,
    isPartiallyComplete: completion.overall > 0 && completion.overall < 100,
    isEmpty: completion.overall === 0,
    completionPercentage: completion.overall,
  };
};

// Export types for convenience
export type UsePreferencesReturn = ReturnType<typeof usePreferences>;
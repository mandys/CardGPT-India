import { useState, useCallback, useEffect } from 'react';
import { 
  OnboardingData, 
  DEFAULT_ONBOARDING_DATA,
  PrimaryGoal,
  SpendingBracket,
  SpendingCategory,
  QuickPreferences
} from '../types/onboarding';
import { UserPreferences } from '../types';

/**
 * Custom hook for managing streamlined onboarding state
 * Provides state management and conversion utilities for the compact onboarding modal
 */
export const useOnboarding = (initialData?: Partial<OnboardingData>) => {
  const [data, setData] = useState<OnboardingData>({
    ...DEFAULT_ONBOARDING_DATA,
    ...initialData,
  });
  
  // Update state when initialData changes (important for Update Preferences mode)
  useEffect(() => {
    if (initialData) {
      console.log('🔄 [useOnboarding] Updating data with new initialData:', initialData);
      setData(current => ({
        ...current,
        ...initialData,
      }));
    }
  }, [initialData]);
  
  console.log('🎯 [useOnboarding] Current state:', { 
    DEFAULT_ONBOARDING_DATA, 
    initialData, 
    finalData: data 
  });

  const updateData = useCallback((updates: Partial<OnboardingData>) => {
    setData(current => ({ ...current, ...updates }));
  }, []);

  const resetData = useCallback(() => {
    setData(DEFAULT_ONBOARDING_DATA);
  }, []);

  const setPrimaryGoal = useCallback((goal: PrimaryGoal) => {
    updateData({ primaryGoal: goal });
  }, [updateData]);

  const setMonthlySpending = useCallback((spending: SpendingBracket) => {
    updateData({ monthlySpending: spending });
  }, [updateData]);

  const toggleSpendingCategory = useCallback((category: SpendingCategory) => {
    setData(current => {
      const currentCategories = current.topCategories;
      const newCategories = currentCategories.includes(category)
        ? currentCategories.filter(cat => cat !== category)
        : currentCategories.length >= 2 
          ? [...currentCategories.slice(1), category] // Replace oldest if at limit
          : [...currentCategories, category];
      
      return { ...current, topCategories: newCategories };
    });
  }, []);

  const toggleCurrentCard = useCallback((cardName: string) => {
    setData(current => {
      const currentCards = current.currentCards;
      const newCards = currentCards.includes(cardName)
        ? currentCards.filter(card => card !== cardName)
        : [...currentCards, cardName];
      
      return { ...current, currentCards: newCards };
    });
  }, []);

  const togglePreference = useCallback((key: keyof QuickPreferences) => {
    setData(current => ({
      ...current,
      preferences: {
        ...current.preferences,
        [key]: !current.preferences[key],
      },
    }));
  }, []);

  const setPreferences = useCallback((preferences: Partial<QuickPreferences>) => {
    setData(current => ({
      ...current,
      preferences: { ...current.preferences, ...preferences },
    }));
  }, []);

  /**
   * Convert streamlined onboarding data to existing UserPreferences format
   * This ensures compatibility with the existing preference system
   */
  const convertToUserPreferences = useCallback((): UserPreferences => {
    console.log('🔄 [CONVERT] Converting onboarding data:', data);
    
    // Map primary goals to travel and fee preferences
    let travel_type: string | undefined;
    let lounge_access: string | undefined;
    let fee_willingness: string | undefined;

    // Infer travel preferences from primary goal and preferences
    if (data.primaryGoal === 'travel_benefits' || data.preferences.international) {
      travel_type = data.preferences.international ? 'international' : 'both';
      lounge_access = 'solo'; // Default, can be refined later
    } else if (data.topCategories.includes('travel')) {
      travel_type = 'domestic';
      lounge_access = 'solo';
    }

    // Map spending bracket to fee willingness
    if (data.monthlySpending) {
      switch (data.monthlySpending) {
        case '0-25000':
          fee_willingness = data.preferences.lowFees ? '0-1000' : '1000-5000';
          break;
        case '25000-75000':
          fee_willingness = data.preferences.lowFees ? '1000-5000' : '5000-10000';
          break;
        case '75000+':
          fee_willingness = data.preferences.lowFees ? '5000-10000' : '10000+';
          break;
      }
    } else if (data.preferences.lowFees) {
      fee_willingness = '0-1000';
    }

    // Convert spending categories to existing format
    const spend_categories = data.topCategories.map(category => {
      switch (category) {
        case 'online_shopping': return 'online_shopping';
        case 'dining': return 'dining';
        case 'groceries': return 'groceries';
        case 'fuel': return 'fuel';
        case 'travel': return 'travel';
        case 'utilities': return 'utilities';
        default: return category;
      }
    });

    // Basic bank preferences based on digital preference
    const preferred_banks: string[] = [];
    if (data.preferences.digitalFirst) {
      // Add digital-first banks
      preferred_banks.push('HDFC Bank', 'ICICI Bank', 'Axis Bank');
    }

    const result = {
      travel_type,
      lounge_access,
      fee_willingness,
      spend_categories,
      preferred_banks: preferred_banks.length > 0 ? preferred_banks : undefined,
      current_cards: data.currentCards, // Include selected cards from onboarding
    };
    
    console.log('✅ [CONVERT] Converted result:', result);
    return result;
  }, [data]);

  // Validation helpers
  const isStep1Complete = useCallback(() => {
    // Step 1 (Current Cards) is optional, always considered complete
    return true;
  }, []);

  const isStep2Complete = useCallback(() => {
    // Step 2 (Monthly Spending) requires spending selection
    return !!data.monthlySpending;
  }, [data.monthlySpending]);

  const hasMinimumData = useCallback(() => {
    return !!(data.monthlySpending || data.currentCards.length > 0);
  }, [data.monthlySpending, data.currentCards.length]);

  const getCompletionPercentage = useCallback(() => {
    let completed = 0;
    let total = 2; // currentCards (optional), monthlySpending (required)

    if (data.currentCards.length > 0) completed++;
    if (data.monthlySpending) completed++;

    return Math.round((completed / total) * 100);
  }, [data.currentCards.length, data.monthlySpending]);

  return {
    // State
    data,
    
    // Actions
    updateData,
    resetData,
    setPrimaryGoal,
    setMonthlySpending,
    toggleSpendingCategory,
    toggleCurrentCard,
    togglePreference,
    setPreferences,
    
    // Conversion
    convertToUserPreferences,
    
    // Validation
    isStep1Complete,
    isStep2Complete,
    hasMinimumData,
    getCompletionPercentage,
    
    // Computed values
    selectedCategories: data.topCategories,
    selectedCards: data.currentCards,
    selectedPreferences: data.preferences,
    isComplete: !!data.monthlySpending, // Minimum completion requires spending selection
    completionPercentage: getCompletionPercentage(),
  };
};
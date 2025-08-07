import { useState, useCallback } from 'react';
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
    return !!(data.primaryGoal && data.monthlySpending);
  }, [data.primaryGoal, data.monthlySpending]);

  const isStep2Complete = useCallback(() => {
    // Step 2 is optional, always considered complete
    return true;
  }, []);

  const hasMinimumData = useCallback(() => {
    return !!(data.primaryGoal || data.monthlySpending || data.topCategories.length > 0);
  }, [data.primaryGoal, data.monthlySpending, data.topCategories.length]);

  const getCompletionPercentage = useCallback(() => {
    let completed = 0;
    let total = 4; // primaryGoal, monthlySpending, topCategories (2 max), preferences (optional)

    if (data.primaryGoal) completed++;
    if (data.monthlySpending) completed++;
    if (data.topCategories.length > 0) completed++;
    
    // Preferences are optional but count if any are set
    const hasPreferences = Object.values(data.preferences).some(Boolean);
    if (hasPreferences) completed++;

    return Math.round((completed / total) * 100);
  }, [data]);

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
    isComplete: isStep1Complete(), // Minimum completion
    completionPercentage: getCompletionPercentage(),
  };
};
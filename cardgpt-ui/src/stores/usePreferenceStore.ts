import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import { UserPreferences, PreferenceCompletion } from '../types';
import { apiClient } from '../services/api';

export interface PreferenceState {
  // State
  preferences: UserPreferences | null;
  isLoading: boolean;
  error: string | null;
  hasLoadedInitial: boolean;
  
  // Derived state
  completion: PreferenceCompletion;
  
  // Actions
  loadPreferences: (clerkToken?: string) => Promise<void>;
  updatePreference: (key: keyof UserPreferences, value: any, clerkToken?: string) => Promise<boolean>;
  updatePreferences: (preferences: Partial<UserPreferences>, clerkToken?: string) => Promise<boolean>;
  clearPreferences: () => Promise<boolean>;
  calculateCompletion: () => PreferenceCompletion;
  applyRefinementButton: (preference: string, value: string, clerkToken?: string) => Promise<boolean>;
  
  // Helper methods
  hasPreferences: () => boolean;
  isPreferenceComplete: (category: keyof PreferenceCompletion['categories']) => boolean;
  getSessionId: () => string;
  syncWithAuth: (isAuthenticated: boolean, getToken?: () => Promise<string | null>) => Promise<void>;
  cleanupLegacyData: () => void;
}

const calculateCompletionFromPreferences = (preferences: UserPreferences | null): PreferenceCompletion => {
  if (!preferences) {
    return {
      overall: 0,
      categories: {
        travel_preferences: false,
        financial_preferences: false,
        card_preferences: false,
        spending_preferences: false,
      }
    };
  }

  // Updated for 2-step onboarding: focus on essential preferences
  const categories = {
    travel_preferences: !!(preferences.travel_type && preferences.lounge_access),
    financial_preferences: !!preferences.fee_willingness,
    card_preferences: !!(preferences.current_cards?.length || preferences.preferred_banks?.length),
    spending_preferences: !!(preferences.spend_categories?.length),
  };

  // For the simplified onboarding, we consider completion based on essential data:
  // - Cards selected (from step 1) 
  // - Monthly spending set (from step 2) 
  const hasEssentialData = !!(preferences.current_cards?.length && preferences.fee_willingness);
  
  if (hasEssentialData) {
    // If user has completed the 2-step onboarding, they should show 100% completion
    // since they've provided the core data needed for personalized recommendations
    return { overall: 100, categories: { ...categories, card_preferences: true, financial_preferences: true } };
  }

  const completedCount = Object.values(categories).filter(Boolean).length;
  const overall = Math.round((completedCount / 4) * 100);

  return { overall, categories };
};

export const usePreferenceStore = create<PreferenceState>()(
  subscribeWithSelector((set, get) => ({
    // Initial state
    preferences: null,
    isLoading: false,
    error: null,
    hasLoadedInitial: false,
    completion: calculateCompletionFromPreferences(null),

    // Load preferences from backend (authenticated) or localStorage (session)
    loadPreferences: async (clerkToken?: string) => {
      set({ isLoading: true, error: null });
      
      try {
        const preferences = await apiClient.getCurrentUserPreferences(clerkToken);
        const completion = calculateCompletionFromPreferences(preferences);
        
        set({ 
          preferences,
          completion,
          isLoading: false,
          hasLoadedInitial: true,
          error: null 
        });
      } catch (error) {
        console.log('No existing preferences found, starting fresh');
        set({ 
          preferences: null,
          completion: calculateCompletionFromPreferences(null),
          isLoading: false,
          hasLoadedInitial: true,
          error: null 
        });
      }
    },

    // Update a single preference
    updatePreference: async (key: keyof UserPreferences, value: any, clerkToken?: string) => {
      const currentPrefs = get().preferences || {};
      const updatedPrefs = { ...currentPrefs, [key]: value };
      
      set({ isLoading: true });
      
      try {
        const success = await apiClient.saveCurrentUserPreferences(updatedPrefs, clerkToken);
        if (success) {
          const completion = calculateCompletionFromPreferences(updatedPrefs);
          set({ 
            preferences: updatedPrefs,
            completion,
            isLoading: false,
            error: null 
          });
          return true;
        } else {
          set({ isLoading: false, error: 'Failed to save preference' });
          return false;
        }
      } catch (error) {
        set({ 
          isLoading: false, 
          error: error instanceof Error ? error.message : 'Unknown error' 
        });
        return false;
      }
    },

    // Update multiple preferences
    updatePreferences: async (newPreferences: Partial<UserPreferences>, clerkToken?: string) => {
      const currentPrefs = get().preferences || {};
      const updatedPrefs = { ...currentPrefs, ...newPreferences };
      
      set({ isLoading: true });
      
      try {
        const success = await apiClient.saveCurrentUserPreferences(updatedPrefs, clerkToken);
        if (success) {
          const completion = calculateCompletionFromPreferences(updatedPrefs);
          set({ 
            preferences: updatedPrefs,
            completion,
            isLoading: false,
            error: null 
          });
          return true;
        } else {
          set({ isLoading: false, error: 'Failed to save preferences' });
          return false;
        }
      } catch (error) {
        set({ 
          isLoading: false, 
          error: error instanceof Error ? error.message : 'Unknown error' 
        });
        return false;
      }
    },

    // Clear all preferences
    clearPreferences: async () => {
      set({ isLoading: true });
      
      try {
        // For authenticated users, call the clear API
        const token = localStorage.getItem('jwt_token');
        if (token) {
          await apiClient.clearUserPreferences();
        } else {
          // For session users, save empty preferences
          await apiClient.saveCurrentUserPreferences({});
        }
        
        const completion = calculateCompletionFromPreferences(null);
        set({ 
          preferences: null,
          completion,
          isLoading: false,
          error: null 
        });
        return true;
      } catch (error) {
        set({ 
          isLoading: false, 
          error: error instanceof Error ? error.message : 'Failed to clear preferences' 
        });
        return false;
      }
    },

    // Calculate completion status
    calculateCompletion: () => {
      const preferences = get().preferences;
      return calculateCompletionFromPreferences(preferences);
    },


    // Apply a refinement button selection
    applyRefinementButton: async (preference: string, value: string, clerkToken?: string) => {
      return get().updatePreference(preference as keyof UserPreferences, value, clerkToken);
    },

    // Helper: Check if user has any preferences set
    hasPreferences: () => {
      const preferences = get().preferences;
      if (!preferences) return false;
      
      return !!(
        preferences.travel_type ||
        preferences.lounge_access ||
        preferences.fee_willingness ||
        preferences.current_cards?.length ||
        preferences.preferred_banks?.length ||
        preferences.spend_categories?.length
      );
    },

    // Helper: Check if specific category is complete
    isPreferenceComplete: (category: keyof PreferenceCompletion['categories']) => {
      return get().completion.categories[category];
    },

    // Helper: Get session ID (consistent with auth context)
    getSessionId: () => {
      let sessionId = localStorage.getItem('session_id');
      if (!sessionId) {
        sessionId = 'session_' + Math.random().toString(36).substring(2, 11);
        localStorage.setItem('session_id', sessionId);
      }
      return sessionId;
    },

    // Sync preferences when authentication state changes
    syncWithAuth: async (isAuthenticated: boolean, getToken?: () => Promise<string | null>) => {
      if (isAuthenticated) {
        // User just logged in - migrate session preferences to user account if any exist
        const currentPrefs = get().preferences;
        if (currentPrefs && Object.keys(currentPrefs).length > 0) {
          try {
            // Get Clerk token for authenticated API call if function provided
            if (getToken) {
              const token = await getToken();
              if (token) {
                await apiClient.updateUserPreferences(currentPrefs, token);
                console.log('✅ Session preferences migrated to user account');
              } else {
                console.warn('⚠️ No Clerk token available for preference migration');
              }
            } else {
              // Fallback to token-less call (may fail but won't crash)
              await apiClient.updateUserPreferences(currentPrefs);
              console.log('✅ Session preferences migrated to user account (fallback)');
            }
          } catch (error) {
            console.error('Failed to migrate session preferences:', error);
          }
        }
        // Reload preferences from authenticated endpoint with token
        const token = getToken ? await getToken() : undefined;
        await get().loadPreferences(token || undefined);
      } else {
        // User logged out - preferences will now be session-based
        await get().loadPreferences();
      }
    },

    // Clean up legacy localStorage data that might conflict with new system
    cleanupLegacyData: () => {
      try {
        const legacyKeys = [
          'preferences',
          'user_preferences', 
          'guest_preferences',
          'cardgpt_preferences',
          'preference_completion',
          'onboarding_completed',
          'preference_version'
        ];
        
        let removedCount = 0;
        legacyKeys.forEach(key => {
          if (localStorage.getItem(key)) {
            localStorage.removeItem(key);
            removedCount++;
          }
        });
        
        if (removedCount > 0) {
          console.log(`🧹 Cleaned up ${removedCount} legacy preference keys`);
          
          // Force reload preferences after cleanup
          setTimeout(() => {
            get().loadPreferences();
          }, 100);
        }
      } catch (error) {
        console.warn('Error cleaning up legacy data:', error);
      }
    },
  }))
);

// Subscribe to store changes and log them (development only)
if (process.env.NODE_ENV === 'development') {
  usePreferenceStore.subscribe(
    (state) => state.preferences,
    (preferences) => {
      console.log('🎯 Preferences updated:', preferences);
    }
  );

  usePreferenceStore.subscribe(
    (state) => state.completion,
    (completion) => {
      console.log('📊 Completion updated:', completion);
    }
  );
}

// Auto-load preferences on store creation and cleanup legacy data
setTimeout(() => {
  const store = usePreferenceStore.getState();
  store.cleanupLegacyData();
  store.loadPreferences();
}, 0);
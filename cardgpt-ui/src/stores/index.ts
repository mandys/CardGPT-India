// Export all stores
export { usePreferenceStore } from './usePreferenceStore';

// Export store types for TypeScript
export type { PreferenceState } from './usePreferenceStore';

// Re-export the custom hook for convenience
export { usePreferences } from '../hooks/usePreferences';
export type { UsePreferencesReturn } from '../hooks/usePreferences';
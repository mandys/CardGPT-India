import React from 'react';
import { usePreferences } from '../../hooks/usePreferences';

/**
 * Debug component for preference store - only shown in development
 * Provides visibility into preference state and testing of store actions
 */
export const PreferenceDebug: React.FC = () => {
  const {
    preferences,
    isLoading,
    error,
    completion,
    hasPreferences,
    updatePreference,
    clearPreferences,
    quickSetTravelType,
    quickSetFeeWillingness,
    completionPercentage,
    isFullyComplete,
    isEmpty
  } = usePreferences();

  // Only show in development
  if (process.env.NODE_ENV !== 'development') {
    return null;
  }

  return (
    <div className="bg-gray-100 dark:bg-gray-800 p-4 rounded-lg mt-4 border-2 border-dashed border-gray-300 dark:border-gray-600">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">
          🔧 Preference Store Debug
        </h3>
        <span className="text-xs bg-yellow-100 dark:bg-yellow-800 text-yellow-800 dark:text-yellow-200 px-2 py-1 rounded">
          DEV ONLY
        </span>
      </div>

      {/* Status */}
      <div className="grid grid-cols-2 gap-2 mb-3 text-xs">
        <div>
          <span className="font-medium">Loading:</span> {isLoading ? '✅' : '❌'}
        </div>
        <div>
          <span className="font-medium">Has Prefs:</span> {hasPreferences ? '✅' : '❌'}
        </div>
        <div>
          <span className="font-medium">Completion:</span> {completionPercentage}%
        </div>
        <div>
          <span className="font-medium">Status:</span> {
            isEmpty ? 'Empty' : 
            isFullyComplete ? 'Complete' : 
            'Partial'
          }
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="text-xs text-red-600 dark:text-red-400 mb-2 p-2 bg-red-50 dark:bg-red-900 rounded">
          Error: {error}
        </div>
      )}

      {/* Current Preferences */}
      <div className="mb-3">
        <h4 className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Current Preferences:</h4>
        <pre className="text-xs bg-white dark:bg-gray-900 p-2 rounded border overflow-auto max-h-32">
          {JSON.stringify(preferences, null, 2)}
        </pre>
      </div>

      {/* Completion Status */}
      <div className="mb-3">
        <h4 className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Category Completion:</h4>
        <div className="grid grid-cols-2 gap-1 text-xs">
          {Object.entries(completion.categories).map(([key, completed]) => (
            <div key={key} className="flex items-center">
              <span className={completed ? 'text-green-600' : 'text-gray-400'}>
                {completed ? '✅' : '⭕'}
              </span>
              <span className="ml-1">{key.replace('_', ' ')}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="space-y-2">
        <h4 className="text-xs font-medium text-gray-600 dark:text-gray-400">Quick Actions:</h4>
        
        <div className="flex flex-wrap gap-1">
          <button
            onClick={() => quickSetTravelType('international')}
            disabled={isLoading}
            className="text-xs bg-blue-100 dark:bg-blue-800 text-blue-800 dark:text-blue-200 px-2 py-1 rounded hover:bg-blue-200 dark:hover:bg-blue-700 disabled:opacity-50"
          >
            Set International Travel
          </button>
          
          <button
            onClick={() => quickSetFeeWillingness('5000-10000')}
            disabled={isLoading}
            className="text-xs bg-green-100 dark:bg-green-800 text-green-800 dark:text-green-200 px-2 py-1 rounded hover:bg-green-200 dark:hover:bg-green-700 disabled:opacity-50"
          >
            Set ₹5K-10K Fee
          </button>

          <button
            onClick={() => updatePreference('current_cards', ['axis atlas', 'hdfc infinia'])}
            disabled={isLoading}
            className="text-xs bg-purple-100 dark:bg-purple-800 text-purple-800 dark:text-purple-200 px-2 py-1 rounded hover:bg-purple-200 dark:hover:bg-purple-700 disabled:opacity-50"
          >
            Set Test Cards
          </button>

          <button
            onClick={() => clearPreferences()}
            disabled={isLoading}
            className="text-xs bg-red-100 dark:bg-red-800 text-red-800 dark:text-red-200 px-2 py-1 rounded hover:bg-red-200 dark:hover:bg-red-700 disabled:opacity-50"
          >
            Clear All
          </button>
        </div>

        <div className="text-xs text-gray-500 dark:text-gray-400 mt-2">
          💡 Test the preference store by clicking buttons above. Check browser console for logs.
        </div>
      </div>
    </div>
  );
};
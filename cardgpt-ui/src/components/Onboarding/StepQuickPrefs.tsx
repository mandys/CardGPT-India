import React from 'react';
import { Check } from 'lucide-react';
import { QUICK_PREFERENCE_OPTIONS, QuickPreferences } from '../../types/onboarding';

interface StepQuickPrefsProps {
  preferences: QuickPreferences;
  onTogglePreference: (key: keyof QuickPreferences) => void;
}

const StepQuickPrefs: React.FC<StepQuickPrefsProps> = ({
  preferences,
  onTogglePreference,
}) => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          Any specific preferences?
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          These help us fine-tune our recommendations (optional)
        </p>
      </div>

      {/* Preference Options */}
      <div className="space-y-3">
        {QUICK_PREFERENCE_OPTIONS.map((option) => {
          const isSelected = preferences[option.key];
          
          return (
            <button
              key={option.key}
              onClick={() => onTogglePreference(option.key)}
              className={`w-full p-4 rounded-lg border-2 text-left transition-all ${
                isSelected
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 ring-1 ring-blue-500'
                  : 'border-gray-200 dark:border-gray-600 hover:border-blue-300 hover:bg-gray-50 dark:hover:bg-gray-700'
              }`}
            >
              <div className="flex items-start space-x-3">
                {/* Checkbox Icon */}
                <div className={`flex-shrink-0 w-5 h-5 rounded border-2 flex items-center justify-center transition-all ${
                  isSelected 
                    ? 'bg-blue-500 border-blue-500' 
                    : 'border-gray-300 dark:border-gray-600'
                }`}>
                  {isSelected && (
                    <Check className="w-3 h-3 text-white" />
                  )}
                </div>
                
                {/* Content */}
                <div className="flex-1">
                  <div className="font-medium text-gray-900 dark:text-white">
                    {option.label}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                    {option.description}
                  </div>
                </div>
              </div>
            </button>
          );
        })}
      </div>

      {/* Skip Notice */}
      <div className="text-center">
        <p className="text-xs text-gray-500 dark:text-gray-400">
          💡 You can always update these preferences later in settings
        </p>
      </div>
    </div>
  );
};

export default StepQuickPrefs;
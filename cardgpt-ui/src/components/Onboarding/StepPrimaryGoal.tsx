import React from 'react';
import { 
  PRIMARY_GOAL_OPTIONS, 
  SPENDING_BRACKET_OPTIONS, 
  SPENDING_CATEGORY_OPTIONS,
  PrimaryGoal,
  SpendingBracket,
  SpendingCategory 
} from '../../types/onboarding';

interface StepPrimaryGoalProps {
  selectedGoal?: PrimaryGoal;
  selectedSpending?: SpendingBracket;
  selectedCategories: SpendingCategory[];
  onGoalChange: (goal: PrimaryGoal) => void;
  onSpendingChange: (spending: SpendingBracket) => void;
  onCategoryToggle: (category: SpendingCategory) => void;
}

const StepPrimaryGoal: React.FC<StepPrimaryGoalProps> = ({
  selectedGoal,
  selectedSpending,
  selectedCategories,
  onGoalChange,
  onSpendingChange,
  onCategoryToggle,
}) => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          Let's find your perfect credit card
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Tell us about your goals and spending to get personalized recommendations
        </p>
      </div>

      {/* Primary Goal Selection */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
          What's your primary goal with a credit card?
        </label>
        <div className="space-y-2">
          {PRIMARY_GOAL_OPTIONS.map((option) => (
            <button
              key={option.value}
              onClick={() => onGoalChange(option.value)}
              className={`w-full p-3 rounded-lg border-2 text-left transition-all ${
                selectedGoal === option.value
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 ring-1 ring-blue-500'
                  : 'border-gray-200 dark:border-gray-600 hover:border-blue-300 hover:bg-gray-50 dark:hover:bg-gray-700'
              }`}
            >
              <div className="flex items-start space-x-3">
                <span className="text-lg flex-shrink-0">{option.label.split(' ')[0]}</span>
                <div>
                  <div className="font-medium text-gray-900 dark:text-white">
                    {option.label.substring(2)} {/* Remove emoji */}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                    {option.description}
                  </div>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Monthly Spending */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
          What's your monthly credit card spending?
        </label>
        <div className="grid grid-cols-1 gap-2">
          {SPENDING_BRACKET_OPTIONS.map((option) => (
            <button
              key={option.value}
              onClick={() => onSpendingChange(option.value)}
              className={`p-3 rounded-lg border-2 text-left transition-all ${
                selectedSpending === option.value
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 ring-1 ring-blue-500'
                  : 'border-gray-200 dark:border-gray-600 hover:border-blue-300 hover:bg-gray-50 dark:hover:bg-gray-700'
              }`}
            >
              <div className="font-medium text-gray-900 dark:text-white">
                {option.label}
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                {option.description}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Top Spending Categories */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
          Top spending categories <span className="text-gray-500">(select up to 2)</span>
        </label>
        <div className="grid grid-cols-2 gap-2">
          {SPENDING_CATEGORY_OPTIONS.map((option) => {
            const isSelected = selectedCategories.includes(option.value);
            const canSelect = selectedCategories.length < 2 || isSelected;
            
            return (
              <button
                key={option.value}
                onClick={() => onCategoryToggle(option.value)}
                disabled={!canSelect}
                className={`p-3 rounded-lg border-2 text-center transition-all ${
                  isSelected
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 ring-1 ring-blue-500'
                    : canSelect
                    ? 'border-gray-200 dark:border-gray-600 hover:border-blue-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                    : 'border-gray-200 dark:border-gray-600 opacity-50 cursor-not-allowed'
                }`}
              >
                <div className="text-lg mb-1">{option.emoji}</div>
                <div className="text-xs font-medium text-gray-900 dark:text-white">
                  {option.label.substring(3)} {/* Remove emoji from label */}
                </div>
              </button>
            );
          })}
        </div>
        {selectedCategories.length > 0 && (
          <div className="text-center text-xs text-gray-500 dark:text-gray-400 mt-2">
            {selectedCategories.length}/2 categories selected
          </div>
        )}
      </div>
    </div>
  );
};

export default StepPrimaryGoal;
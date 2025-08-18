import React from 'react';
import { SPENDING_BRACKET_OPTIONS, SpendingBracket } from '../../types/onboarding';

interface StepMonthlySpendingProps {
  selectedSpending?: SpendingBracket;
  onSpendingChange: (spending: SpendingBracket) => void;
}

const StepMonthlySpending: React.FC<StepMonthlySpendingProps> = ({
  selectedSpending,
  onSpendingChange,
}) => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          What's your monthly credit card spending?
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          This helps us recommend cards in the right tier for you
        </p>
      </div>

      {/* Monthly Spending Options */}
      <div className="space-y-3">
        {SPENDING_BRACKET_OPTIONS.map((option) => (
          <button
            key={option.value}
            onClick={() => onSpendingChange(option.value)}
            className={`w-full p-4 rounded-lg border-2 text-left transition-all ${
              selectedSpending === option.value
                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 ring-1 ring-blue-500'
                : 'border-gray-200 dark:border-gray-600 hover:border-blue-300 hover:bg-gray-50 dark:hover:bg-gray-700'
            }`}
          >
            <div className="font-medium text-gray-900 dark:text-white text-lg">
              {option.label}
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              {option.description}
            </div>
          </button>
        ))}
      </div>

      {/* Help Text */}
      <div className="text-center">
        <p className="text-xs text-gray-500 dark:text-gray-400">
          💡 Include all your regular monthly expenses like groceries, bills, dining, and shopping
        </p>
      </div>
    </div>
  );
};

export default StepMonthlySpending;
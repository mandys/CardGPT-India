import React from 'react';
import { Globe, CreditCard, ArrowLeftRight } from 'lucide-react';
import { QueryMode } from '../../types';

interface QueryModeSelectorProps {
  queryMode: QueryMode;
  onQueryModeChange: (mode: QueryMode) => void;
  disabled?: boolean;
}

const QueryModeSelector: React.FC<QueryModeSelectorProps> = ({
  queryMode,
  onQueryModeChange,
  disabled = false,
}) => {
  const queryModes: { value: QueryMode; label: string; icon: React.ReactNode; description: string }[] = [
    {
      value: 'General Query',
      label: 'General Query',
      icon: <Globe className="w-4 h-4" />,
      description: 'Ask about any credit card or compare multiple cards',
    },
    {
      value: 'Specific Card',
      label: 'Specific Card',
      icon: <CreditCard className="w-4 h-4" />,
      description: 'Focus on a particular credit card',
    },
    {
      value: 'Compare Cards',
      label: 'Compare Cards',
      icon: <ArrowLeftRight className="w-4 h-4" />,
      description: 'Compare features between multiple cards',
    },
  ];

  return (
    <div className="space-y-2">
      {queryModes.map((mode) => (
        <div
          key={mode.value}
          className={`p-3 rounded-lg border cursor-pointer transition-all duration-200 ${
            queryMode === mode.value
              ? 'border-primary-300 bg-primary-50 dark:border-primary-500 dark:bg-primary-900/20'
              : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500 bg-white dark:bg-gray-700/50'
          } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
          onClick={() => !disabled && onQueryModeChange(mode.value)}
        >
          <div className="flex items-center space-x-3">
            <div className={`p-2 rounded-md ${
              queryMode === mode.value
                ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400'
                : 'bg-gray-100 dark:bg-gray-600 text-gray-500 dark:text-gray-400'
            }`}>
              {mode.icon}
            </div>
            <div className="flex-1">
              <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                {mode.label}
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400">
                {mode.description}
              </div>
            </div>
            {queryMode === mode.value && (
              <div className="w-2 h-2 bg-primary-600 rounded-full"></div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default QueryModeSelector;
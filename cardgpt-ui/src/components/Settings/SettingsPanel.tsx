import React from 'react';
import { Settings, Zap, CreditCard, Search, User } from 'lucide-react';
import { ModelInfo, QueryMode, CardFilter } from '../../types';
import { useCardDisplayNames } from '../../hooks/useCardConfig';
import ModelSelector from './ModelSelector';
import QueryModeSelector from './QueryModeSelector';
import { ThemeToggle } from './ThemeToggle';
import { PreferenceDebug } from './PreferenceDebug';

interface SettingsPanelProps {
  models: ModelInfo[];
  selectedModel: string;
  onModelChange: (model: string) => void;
  queryMode: QueryMode;
  onQueryModeChange: (mode: QueryMode) => void;
  cardFilter: CardFilter;
  onCardFilterChange: (filter: CardFilter) => void;
  topK: number;
  onTopKChange: (topK: number) => void;
  isLoading?: boolean;
  onShowPreferences?: () => void;
  onShowPreferencesSidebar?: () => void;
}

const SettingsPanel: React.FC<SettingsPanelProps> = ({
  models,
  selectedModel,
  onModelChange,
  queryMode,
  onQueryModeChange,
  cardFilter,
  onCardFilterChange,
  topK,
  onTopKChange,
  isLoading = false,
  onShowPreferences,
  onShowPreferencesSidebar,
}) => {
  // Get card filter options from centralized configuration
  const { filterOptions: supportedCards, loading: cardsLoading } = useCardDisplayNames();

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-2">
          <Settings className="w-5 h-5 text-primary-600" />
          <h2 className="text-lg font-semibold text-gray-800 dark:text-white">Settings</h2>
        </div>
      </div>
      
      {/* Settings Content */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {/* Theme Toggle */}
        <div>
          <ThemeToggle />
        </div>
        
        {/* Model Selection */}
        <div>
          <div className="flex items-center space-x-2 mb-3">
            <Zap className="w-4 h-4 text-orange-500" />
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">AI Model</label>
          </div>
          <ModelSelector
            models={models}
            selectedModel={selectedModel}
            onModelChange={onModelChange}
            disabled={isLoading}
          />
        </div>
        
        {/* Query Mode */}
        <div>
          <div className="flex items-center space-x-2 mb-3">
            <Search className="w-4 h-4 text-blue-500" />
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Query Mode</label>
          </div>
          <QueryModeSelector
            queryMode={queryMode}
            onQueryModeChange={onQueryModeChange}
            disabled={isLoading}
          />
        </div>
        
        {/* Card Filter */}
        <div>
          <div className="flex items-center space-x-2 mb-3">
            <CreditCard className="w-4 h-4 text-purple-500" />
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Card Filter</label>
          </div>
          <select
            value={cardFilter}
            onChange={(e) => onCardFilterChange(e.target.value as CardFilter)}
            disabled={isLoading || cardsLoading}
            className="w-full input-field text-sm"
          >
            {cardsLoading ? (
              <option>Loading cards...</option>
            ) : (
              supportedCards.map((card) => (
                <option key={card} value={card}>
                  {card}
                </option>
              ))
            )}
          </select>
          <p className="text-xs text-gray-500 mt-1">
            Only for Specific Card mode
          </p>
        </div>
        
        {/* Search Results */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <label className="text-sm font-medium text-gray-700">Search Results</label>
            <span className="text-xs text-gray-500">{topK}</span>
          </div>
          <input
            type="range"
            min="1"
            max="15"
            value={topK}
            onChange={(e) => onTopKChange(Number(e.target.value))}
            disabled={isLoading}
            className="w-full h-2 bg-gray-200 dark:bg-gray-600 rounded-lg appearance-none cursor-pointer slider"
          />
          <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
            <span>1</span>
            <span>15</span>
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            More results = better accuracy, higher cost
          </p>
        </div>

        {/* User Preferences */}
        <div>
          <div className="flex items-center space-x-2 mb-3">
            <User className="w-4 h-4 text-green-500" />
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">User Preferences</label>
          </div>
          <div className="space-y-2">
            {onShowPreferences && (
              <button
                onClick={onShowPreferences}
                className="w-full btn-secondary text-sm py-2 px-3 flex items-center justify-between"
              >
                <span>Setup Preferences</span>
                <span className="text-xs text-gray-500">Quick setup</span>
              </button>
            )}
            {onShowPreferencesSidebar && (
              <button
                onClick={onShowPreferencesSidebar}
                className="w-full btn-outline text-sm py-2 px-3 flex items-center justify-between"
              >
                <span>Manage Preferences</span>
                <span className="text-xs text-gray-500">Full control</span>
              </button>
            )}
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Set your spending habits and travel preferences for personalized recommendations
          </p>
        </div>

        {/* Preference Debug Component */}
        <PreferenceDebug />
      </div>
      
      {/* Footer */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
        <div className="text-xs text-gray-500 dark:text-gray-400 text-center">
          <p>💡 Tip: Use Gemini Flash for fastest, cheapest queries</p>
        </div>
      </div>
    </div>
  );
};

export default SettingsPanel;
import React from 'react';
import { X } from 'lucide-react';
import SettingsPanel from './SettingsPanel';
import { ModelInfo, QueryMode, CardFilter } from '../../types';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
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

const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  onClose,
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
  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 z-40"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="fixed inset-0 z-50 overflow-hidden">
        <div className="flex h-full">
          <div className="w-full max-w-md ml-auto bg-white dark:bg-gray-800 shadow-xl">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                Settings
              </h2>
              <button
                onClick={onClose}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                aria-label="Close settings"
              >
                <X className="w-5 h-5 text-gray-500 dark:text-gray-400" />
              </button>
            </div>
            
            {/* Content */}
            <div className="h-full overflow-hidden">
              <SettingsPanel
                models={models}
                selectedModel={selectedModel}
                onModelChange={onModelChange}
                queryMode={queryMode}
                onQueryModeChange={onQueryModeChange}
                cardFilter={cardFilter}
                onCardFilterChange={onCardFilterChange}
                topK={topK}
                onTopKChange={onTopKChange}
                isLoading={isLoading}
                onShowPreferences={onShowPreferences}
                onShowPreferencesSidebar={onShowPreferencesSidebar}
              />
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default SettingsModal;
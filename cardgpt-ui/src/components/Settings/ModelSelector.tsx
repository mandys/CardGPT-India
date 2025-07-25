import React from 'react';
import { Check } from 'lucide-react';
import { ModelInfo } from '../../types';

interface ModelSelectorProps {
  models: ModelInfo[];
  selectedModel: string;
  onModelChange: (model: string) => void;
  disabled?: boolean;
}

const ModelSelector: React.FC<ModelSelectorProps> = ({
  models,
  selectedModel,
  onModelChange,
  disabled = false,
}) => {
  const getModelIcon = (provider: string) => {
    switch (provider) {
      case 'Google':
        return '🔥';
      case 'OpenAI':
        return '🧠';
      default:
        return '🤖';
    }
  };

  const getModelBadge = (model: ModelInfo) => {
    if (model.name.includes('flash-lite')) {
      return (
        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
          🚀 NEW
        </span>
      );
    }
    if (model.name.includes('flash')) {
      return (
        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
          Ultra Fast
        </span>
      );
    }
    if (model.name.includes('pro')) {
      return (
        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
          Pro
        </span>
      );
    }
    return null;
  };

  const formatCost = (cost: number) => {
    if (cost < 1) {
      return `$${cost.toFixed(3)}`;
    }
    return `$${cost.toFixed(2)}`;
  };

  return (
    <div className="space-y-2">
      {models.map((model) => (
        <div
          key={model.name}
          className={`p-3 rounded-lg border cursor-pointer transition-all duration-200 ${
            selectedModel === model.name
              ? 'border-primary-300 bg-primary-50 dark:border-primary-500 dark:bg-primary-900/20'
              : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500 bg-white dark:bg-gray-700/50'
          } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
          onClick={() => !disabled && onModelChange(model.name)}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="text-lg">{getModelIcon(model.provider)}</span>
              <div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                    {model.name}
                  </span>
                  {getModelBadge(model)}
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  {model.provider} • {model.description}
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <div className="text-right">
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  {formatCost(model.cost_per_1k_input)}/1K
                </div>
                <div className="text-xs text-gray-400 dark:text-gray-500">
                  input tokens
                </div>
              </div>
              
              {selectedModel === model.name && (
                <Check className="w-4 h-4 text-primary-600" />
              )}
            </div>
          </div>
          
          {!model.available && (
            <div className="mt-2 text-xs text-red-600">
              ⚠️ Not available (check API key)
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default ModelSelector;
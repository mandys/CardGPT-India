import React from 'react';
import { DollarSign, Cpu, Hash, BarChart3 } from 'lucide-react';
import { UsageInfo } from '../../types';
import { useUser } from '@clerk/clerk-react';

interface CostDisplayProps {
  llmUsage: UsageInfo;
  embeddingUsage?: UsageInfo;
  totalCost: number;
}

const CostDisplay: React.FC<CostDisplayProps> = ({ 
  llmUsage, 
  embeddingUsage, 
  totalCost 
}) => {
  const { isSignedIn } = useUser();
  const formatCost = (cost: number) => {
    const USD_TO_INR = 86; // 1 USD = 86 INR (approximate)
    const inrCost = cost * USD_TO_INR;
    
    if (inrCost < 0.01) {
      return `₹${(inrCost * 1000).toFixed(1)}p`; // Paise for very small costs
    } else if (inrCost < 1) {
      return `₹${inrCost.toFixed(2)}`;
    } else {
      return `₹${inrCost.toFixed(2)}`;
    }
  };

  const getModelDisplayName = (model: string) => {
    const modelMap: Record<string, string> = {
      'gemini-2.5-flash-lite': 'Gemini 2.5 Flash-Lite',
      'gemini-1.5-flash': 'Gemini Flash',
      'gemini-1.5-pro': 'Gemini Pro',
      'gpt-3.5-turbo': 'GPT-3.5',
      'gpt-4': 'GPT-4',
      'vertex-ai-search': 'Vertex AI'
    };
    return modelMap[model] || model;
  };

  return (
    <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3 space-y-2">
      <div className="flex items-center gap-2 text-blue-700 dark:text-blue-300 font-medium text-sm">
        <DollarSign className="w-4 h-4" />
        Cost Breakdown
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
        {/* LLM Usage */}
        <div className="bg-white dark:bg-gray-800 rounded px-3 py-2">
          <div className="flex items-center gap-1 text-gray-600 dark:text-gray-400 mb-1">
            <Cpu className="w-3 h-3" />
            LLM ({getModelDisplayName(llmUsage.model)})
          </div>
          <div className="space-y-1">
            {llmUsage.input_tokens && (
              <div className="flex justify-between">
                <span className="text-gray-500">Input:</span>
                <span className="font-mono">{llmUsage.input_tokens.toLocaleString()}</span>
              </div>
            )}
            {llmUsage.output_tokens && (
              <div className="flex justify-between">
                <span className="text-gray-500">Output:</span>
                <span className="font-mono">{llmUsage.output_tokens.toLocaleString()}</span>
              </div>
            )}
            <div className="flex justify-between border-t pt-1">
              <span className="text-gray-500">Total:</span>
              <span className="font-mono font-medium">{(llmUsage.total_tokens || llmUsage.tokens || 0).toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Cost:</span>
              <span className="font-mono text-blue-600 dark:text-blue-400 font-medium">
                {formatCost(llmUsage.cost)}
              </span>
            </div>
          </div>
        </div>

        {/* Embedding Usage (if available) */}
        {embeddingUsage && embeddingUsage.cost > 0 && (
          <div className="bg-white dark:bg-gray-800 rounded px-3 py-2">
            <div className="flex items-center gap-1 text-gray-600 dark:text-gray-400 mb-1">
              <Hash className="w-3 h-3" />
              Search ({getModelDisplayName(embeddingUsage.model)})
            </div>
            <div className="space-y-1">
              <div className="flex justify-between">
                <span className="text-gray-500">Tokens:</span>
                <span className="font-mono">{(embeddingUsage.total_tokens || embeddingUsage.tokens || 0).toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Cost:</span>
                <span className="font-mono text-blue-600 dark:text-blue-400 font-medium">
                  {formatCost(embeddingUsage.cost)}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Query Count */}
        <div className="bg-white dark:bg-gray-800 rounded px-3 py-2">
          <div className="flex items-center gap-1 text-gray-600 dark:text-gray-400 mb-1">
            <BarChart3 className="w-3 h-3" />
            Query Usage
          </div>
          <div className="space-y-1">
            {isSignedIn ? (
              <>
                <div className="flex justify-between">
                  <span className="text-gray-500">Today:</span>
                  <span className="font-mono">-</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Total:</span>
                  <span className="font-mono">-</span>
                </div>
                <div className="flex justify-between border-t pt-1">
                  <span className="text-gray-500">Plan:</span>
                  <span className="font-mono text-green-600 dark:text-green-400 font-medium">
                    Unlimited
                  </span>
                </div>
              </>
            ) : (
              <>
                <div className="flex justify-between">
                  <span className="text-gray-500">Used:</span>
                  <span className="font-mono">-</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Limit:</span>
                  <span className="font-mono">-</span>
                </div>
                <div className="flex justify-between border-t pt-1">
                  <span className="text-gray-500">Remaining:</span>
                  <span className="font-mono font-medium text-green-600 dark:text-green-400">
                    -
                  </span>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Total Cost */}
        <div className="bg-white dark:bg-gray-800 rounded px-3 py-2">
          <div className="flex items-center gap-1 text-gray-600 dark:text-gray-400 mb-1">
            <DollarSign className="w-3 h-3" />
            Total Cost
          </div>
          <div className="text-lg font-mono font-bold text-green-600 dark:text-green-400">
            {formatCost(totalCost)}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {totalCost * 86 < 0.01 ? 'Ultra-low cost!' : totalCost * 86 < 1 ? 'Very affordable' : 'Standard pricing'}
          </div>
        </div>
      </div>

      {/* Note for estimated tokens */}
      {llmUsage.model?.includes('gemini') && (
        <div className="text-xs text-gray-500 dark:text-gray-400 italic">
          * Token counts estimated for Gemini models
        </div>
      )}
    </div>
  );
};

export default CostDisplay;
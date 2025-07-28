import React, { useState } from 'react';
import TipDisplay from '../Chat/TipDisplay';
import TipsContainer from '../Chat/TipsContainer';
import { useTips } from '../../hooks/useTips';

const TipsDemo: React.FC = () => {
  const [selectedQuery, setSelectedQuery] = useState('');
  const { getContextualTip, detectCategory } = useTips();

  const sampleQueries = [
    'What welcome benefits does Axis Atlas offer?',
    'If I spend ₹50,000 on dining monthly, which card gives better rewards?',
    'Miles earned on ₹2L flight booking with Atlas?',
    'Are utility bills capped on HSBC Premier?',
    'Which card gives rewards on insurance premium payments?',
    'Annual fee waiver conditions for HDFC Infinia?',
    'Compare cash withdrawal charges between all cards',
    'Split ₹2L across dining, travel, shopping - best card strategy?'
  ];

  const handleQuerySelect = (query: string) => {
    setSelectedQuery(query);
  };

  const handleTipClick = (tip: string) => {
    alert(`You clicked on tip: ${tip}`);
  };

  const contextualTip = selectedQuery ? getContextualTip(selectedQuery) : null;
  const detectedCategories = selectedQuery ? detectCategory(selectedQuery) : [];

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          💡 Tips Module Demo
        </h1>
        <p className="text-gray-600 dark:text-gray-300">
          Interactive demo of the contextual tips system for credit card queries
        </p>
      </div>

      {/* Query Selection */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          1. Select a Sample Query
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {sampleQueries.map((query, index) => (
            <button
              key={index}
              onClick={() => handleQuerySelect(query)}
              className={`p-3 text-left rounded-lg border-2 transition-all duration-200 ${
                selectedQuery === query
                  ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                  : 'border-gray-200 dark:border-gray-700 hover:border-primary-300 dark:hover:border-primary-600 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300'
              }`}
            >
              <div className="text-sm font-medium">{query}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Analysis Results */}
      {selectedQuery && (
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            2. Category Detection Analysis
          </h2>
          <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <div className="mb-3">
              <span className="font-medium text-gray-700 dark:text-gray-300">Selected Query:</span>
              <div className="text-primary-600 dark:text-primary-400 mt-1">"{selectedQuery}"</div>
            </div>
            <div className="mb-3">
              <span className="font-medium text-gray-700 dark:text-gray-300">Detected Categories:</span>
              <div className="flex flex-wrap gap-2 mt-1">
                {detectedCategories.length > 0 ? (
                  detectedCategories.map((category) => (
                    <span
                      key={category}
                      className="px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded-full text-sm"
                    >
                      {category}
                    </span>
                  ))
                ) : (
                  <span className="text-gray-500 dark:text-gray-400 text-sm">
                    No specific categories detected (will show general tip)
                  </span>
                )}
              </div>
            </div>
            {contextualTip && (
              <div>
                <span className="font-medium text-gray-700 dark:text-gray-300">Generated Tip Category:</span>
                <div className="text-yellow-600 dark:text-yellow-400 mt-1">{contextualTip.category}</div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Contextual Tip Display */}
      {selectedQuery && contextualTip && (
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            3. Contextual Tip Display
          </h2>
          <TipDisplay
            tip={contextualTip.text}
            category={contextualTip.category}
            onTipClick={handleTipClick}
            onRefreshTip={() => window.location.reload()}
          />
        </div>
      )}

      {/* Integration Example */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          4. Integration Example (TipsContainer)
        </h2>
        <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
          <div className="text-sm text-gray-600 dark:text-gray-400 mb-3">
            This shows how the TipsContainer component would appear after an assistant message:
          </div>
          <TipsContainer
            userQuery={selectedQuery || 'What welcome benefits does Axis Atlas offer?'}
            onTipClick={handleTipClick}
            showTip={true}
          />
        </div>
      </div>

      {/* Usage Instructions */}
      <div className="card bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
        <h2 className="text-xl font-semibold text-blue-900 dark:text-blue-100 mb-4">
          📋 Implementation Notes
        </h2>
        <div className="text-blue-800 dark:text-blue-200 space-y-2 text-sm">
          <p><strong>Integration:</strong> Tips automatically appear after assistant messages are complete.</p>
          <p><strong>Context Detection:</strong> Tips are selected based on keywords in the user's query.</p>
          <p><strong>Interactivity:</strong> Users can click tips to use them as new queries.</p>
          <p><strong>Refresh:</strong> Users can get different tips using the shuffle button.</p>
          <p><strong>Categories:</strong> 12 categories with 4-5 tips each, totaling 50+ contextual suggestions.</p>
        </div>
      </div>
    </div>
  );
};

export default TipsDemo;
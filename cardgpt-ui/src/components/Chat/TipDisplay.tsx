import React from 'react';
import { Lightbulb, Shuffle } from 'lucide-react';

interface TipDisplayProps {
  tip: string;
  category?: string;
  onTipClick?: (tip: string) => void;
  onRefreshTip?: () => void;
  className?: string;
}

const TipDisplay: React.FC<TipDisplayProps> = ({
  tip,
  category,
  onTipClick,
  onRefreshTip,
  className = ''
}) => {
  const handleTipClick = () => {
    if (onTipClick) {
      // Extract the actual query from the tip (remove the "Try:" or "Ask:" prefix)
      const cleanTip = tip.replace(/^(💡 Try:|🍽️ Try:|✈️ Try:|⚡ Try:|🛡️ Try:|⛽ Try:|💰 Try:|📈 Try:|🔒 Try:|🎁 Try:|🌍 Try:|🎯 Try:|🤔 Try:|🍕 Ask:|🥘 Compare:|🧳 Explore:|💡 Ask:|🏨 Ask:|📱 Calculate:|💸 Ask:|🚗 Ask:|🏧 Ask:|💰 Ask:|📊 Ask:|⚖️ Compare:|✈️ Ask:|💎 Compare:|💱 Ask:|🏆 Ask:|📈 Compare:|💡 Compare:|📊 Ask:|🎯 Explore:)\s*/, '');
      onTipClick(cleanTip.replace(/^['"]|['"]$/g, '')); // Remove quotes if present
    }
  };

  return (
    <div className={`animate-fade-in ${className}`}>
      <div className="bg-gradient-to-r from-yellow-50 to-amber-50 dark:from-yellow-900/20 dark:to-amber-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4 shadow-sm">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start gap-3 flex-1">
            <div className="flex-shrink-0 w-8 h-8 bg-yellow-100 dark:bg-yellow-800/50 rounded-full flex items-center justify-center">
              <Lightbulb className="w-4 h-4 text-yellow-600 dark:text-yellow-400" />
            </div>
            <div className="flex-1">
              {category && (
                <div className="text-xs font-medium text-yellow-700 dark:text-yellow-300 mb-1 uppercase tracking-wide">
                  {category}
                </div>
              )}
              <div 
                className={`text-sm text-yellow-800 dark:text-yellow-200 leading-relaxed ${
                  onTipClick ? 'cursor-pointer hover:text-yellow-900 dark:hover:text-yellow-100 transition-colors' : ''
                }`}
                onClick={handleTipClick}
              >
                {tip}
              </div>
              {onTipClick && (
                <div className="text-xs text-yellow-600 dark:text-yellow-400 mt-1 opacity-75">
                  Click to try this query
                </div>
              )}
            </div>
          </div>
          
          {onRefreshTip && (
            <button
              onClick={onRefreshTip}
              className="flex-shrink-0 p-1.5 rounded-full hover:bg-yellow-100 dark:hover:bg-yellow-800/50 transition-colors duration-200 group"
              title="Get another tip"
            >
              <Shuffle className="w-4 h-4 text-yellow-600 dark:text-yellow-400 group-hover:text-yellow-700 dark:group-hover:text-yellow-300" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default TipDisplay;
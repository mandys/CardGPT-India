import React from 'react';

interface QuerySuggestion {
  icon: string;
  text: string;
  category: 'trending' | 'budget' | 'comparison' | 'smart' | 'digital' | 'lifestyle';
  onClick: (query: string) => void;
}

interface GenZQuerySuggestionsProps {
  onQuerySelect: (query: string) => void;
}

const GenZQuerySuggestions: React.FC<GenZQuerySuggestionsProps> = ({ onQuerySelect }) => {
  const suggestions: Omit<QuerySuggestion, 'onClick'>[] = [
    {
      icon: "🔥",
      text: "Which card is fire for travel rewards?",
      category: "trending"
    },
    {
      icon: "💰", 
      text: "Best cashback card that won't break me?",
      category: "budget"
    },
    {
      icon: "✈️",
      text: "Atlas vs EPM - which one slaps harder?",
      category: "comparison"
    },
    {
      icon: "🎯",
      text: "Annual fees? We don't do those here",
      category: "smart"
    },
    {
      icon: "📱",
      text: "UPI cashback cards that actually pay",
      category: "digital"
    },
    {
      icon: "🏠",
      text: "Rent payments with max rewards?", 
      category: "lifestyle"
    }
  ];

  const getCategoryStyle = (category: string) => {
    const styles = {
      trending: 'bg-gradient-to-r from-red-500 to-pink-500 text-white',
      budget: 'bg-gradient-to-r from-green-500 to-emerald-500 text-white',
      comparison: 'bg-gradient-to-r from-blue-500 to-indigo-500 text-white',
      smart: 'bg-gradient-to-r from-purple-500 to-violet-500 text-white',
      digital: 'bg-gradient-to-r from-cyan-500 to-blue-500 text-white',
      lifestyle: 'bg-gradient-to-r from-pink-500 to-rose-500 text-white'
    };
    return styles[category as keyof typeof styles] || styles.smart;
  };

  return (
    <div className="space-y-4 p-4">
      <div className="text-center">
        <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">
          Popular Questions ⚡
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Tap to get instant answers 🚀
        </p>
      </div>
      
      <div className="grid grid-cols-1 gap-3">
        {suggestions.map((suggestion, index) => (
          <button
            key={index}
            onClick={() => onQuerySelect(suggestion.text)}
            className={`
              ${getCategoryStyle(suggestion.category)}
              flex items-center space-x-3 p-4 rounded-2xl shadow-lg 
              transform transition-all duration-300 hover:scale-105 hover:shadow-xl
              active:scale-95 text-left w-full
            `}
          >
            <span className="text-2xl flex-shrink-0">{suggestion.icon}</span>
            <span className="font-medium leading-tight">{suggestion.text}</span>
          </button>
        ))}
      </div>
      
      {/* Quick Tags */}
      <div className="flex flex-wrap gap-2 justify-center pt-4">
        {['💳 Best cards', '🎁 Rewards', '💸 No fees', '⚡ Quick cash'].map((tag, idx) => (
          <button
            key={idx}
            onClick={() => onQuerySelect(tag.replace(/[^\w\s]/g, '').trim())}
            className="px-3 py-1 bg-purple-500/20 hover:bg-purple-500/30 text-purple-700 dark:text-purple-300 rounded-full text-xs font-medium transition-colors duration-300"
          >
            {tag}
          </button>
        ))}
      </div>
    </div>
  );
};

export default GenZQuerySuggestions;
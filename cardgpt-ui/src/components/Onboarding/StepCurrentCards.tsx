import React, { useState, useEffect } from 'react';
import { CreditCard, Search, Loader } from 'lucide-react';

// Use the same API URL logic as other components
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

interface StepCurrentCardsProps {
  selectedCards: string[];
  onCardToggle: (cardName: string) => void;
}

interface Card {
  name: string;
  displayName: string;
}

const StepCurrentCards: React.FC<StepCurrentCardsProps> = ({
  selectedCards,
  onCardToggle,
}) => {
  const [availableCards, setAvailableCards] = useState<Card[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const fetchCards = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await fetch(`${API_BASE_URL}/api/cards/display-names`);
        if (!response.ok) {
          throw new Error(`Failed to fetch cards: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('📋 [CARDS API] Response:', data);
        
        // Convert display names to Card objects
        const cards = (data.display_names || []).map((displayName: string) => ({
          name: displayName,
          displayName: displayName
        }));
        
        setAvailableCards(cards);
      } catch (err) {
        console.error('❌ [CARDS API] Error:', err);
        setError('Failed to load credit cards');
        // Fallback to hardcoded cards for development
        setAvailableCards([
          { name: 'ICICI Emeralde', displayName: 'ICICI Emeralde Private Metal' },
          { name: 'Axis Atlas', displayName: 'Axis Atlas' },
          { name: 'HDFC Infinia', displayName: 'HDFC Infinia' },
          { name: 'HSBC Premier', displayName: 'HSBC Premier' },
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchCards();
  }, []);

  const filteredCards = availableCards.filter(card =>
    card.displayName.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          Which cards do you currently have?
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          This helps us give you personalized recommendations and comparisons
        </p>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          type="text"
          placeholder="Search for your cards..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-8">
          <Loader className="w-6 h-6 text-blue-500 animate-spin mr-2" />
          <span className="text-sm text-gray-600 dark:text-gray-400">Loading available cards...</span>
        </div>
      )}

      {/* Error State */}
      {error && !loading && (
        <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-lg">
          <p className="text-sm text-red-700 dark:text-red-400">
            ⚠️ {error}. Using fallback card list.
          </p>
        </div>
      )}

      {/* Cards Grid */}
      {!loading && (
        <div>
          <div className="grid grid-cols-1 gap-3">
            {filteredCards.length > 0 ? (
              filteredCards.map((card) => {
                const isSelected = selectedCards.includes(card.name);
                
                console.log('🎯 [StepCurrentCards] Card selection check:', {
                  cardName: card.name,
                  selectedCards,
                  isSelected
                });
                
                return (
                  <button
                    key={card.name}
                    onClick={() => onCardToggle(card.name)}
                    className={`p-4 rounded-lg border-2 text-left transition-all ${
                      isSelected
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 ring-1 ring-blue-500'
                        : 'border-gray-200 dark:border-gray-600 hover:border-blue-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <div className={`p-2 rounded-lg ${
                        isSelected 
                          ? 'bg-blue-100 dark:bg-blue-800' 
                          : 'bg-gray-100 dark:bg-gray-600'
                      }`}>
                        <CreditCard className={`w-4 h-4 ${
                          isSelected 
                            ? 'text-blue-600 dark:text-blue-400' 
                            : 'text-gray-500 dark:text-gray-400'
                        }`} />
                      </div>
                      <div className="flex-1">
                        <div className="font-medium text-gray-900 dark:text-white">
                          {card.displayName}
                        </div>
                        {isSelected && (
                          <div className="text-xs text-blue-600 dark:text-blue-400 mt-0.5">
                            ✓ Added to your profile
                          </div>
                        )}
                      </div>
                    </div>
                  </button>
                );
              })
            ) : (
              <div className="text-center py-8">
                <CreditCard className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-3" />
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  No cards found matching "{searchTerm}"
                </p>
              </div>
            )}
          </div>

          {/* Selection Summary */}
          {selectedCards.length > 0 && (
            <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg">
              <div className="flex items-center space-x-2">
                <CreditCard className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                <span className="text-sm font-medium text-blue-900 dark:text-blue-100">
                  {selectedCards.length} card{selectedCards.length !== 1 ? 's' : ''} selected
                </span>
              </div>
              <div className="text-xs text-blue-700 dark:text-blue-300 mt-1">
                {selectedCards.join(', ')}
              </div>
            </div>
          )}

          {/* Skip Option */}
          <div className="mt-4 text-center">
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Don't have any cards yet? That's okay - we'll help you find your first one!
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default StepCurrentCards;
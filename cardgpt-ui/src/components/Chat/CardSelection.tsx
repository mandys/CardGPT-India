import React, { useState } from 'react';
import { Check } from 'lucide-react';

interface CardSelectionProps {
  availableCards: string[];
  originalQuery: string;
  onSelectionComplete: (selectedCards: string[], originalQuery: string) => void;
}

const CardSelection: React.FC<CardSelectionProps> = ({
  availableCards,
  originalQuery,
  onSelectionComplete,
}) => {
  const [selectedCards, setSelectedCards] = useState<string[]>([]);

  const handleCardToggle = (cardName: string) => {
    setSelectedCards(prev => {
      if (prev.includes(cardName)) {
        return prev.filter(card => card !== cardName);
      } else {
        // Limit to maximum 3 cards for focused comparison
        if (prev.length >= 3) {
          return prev;
        }
        return [...prev, cardName];
      }
    });
  };

  const handleSubmit = () => {
    if (selectedCards.length >= 2) {
      onSelectionComplete(selectedCards, originalQuery);
    }
  };

  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 space-y-4">
      <div className="text-center">
        <h3 className="text-lg font-semibold text-gray-800 mb-2">
          Select Cards to Compare
        </h3>
        <p className="text-sm text-gray-600 mb-4">
          Choose 2-3 cards for your query: "{originalQuery}"
        </p>
      </div>

      {/* Card Selection Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {availableCards.map((cardName) => {
          const isSelected = selectedCards.includes(cardName);
          const isDisabled = !isSelected && selectedCards.length >= 3;
          
          return (
            <button
              key={cardName}
              onClick={() => handleCardToggle(cardName)}
              disabled={isDisabled}
              className={`relative p-4 rounded-lg border-2 transition-all duration-200 text-left ${
                isSelected
                  ? 'border-primary-500 bg-primary-50 text-primary-700'
                  : isDisabled
                  ? 'border-gray-200 bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'border-gray-200 bg-white text-gray-700 hover:border-primary-300 hover:bg-primary-50'
              }`}
            >
              {/* Checkbox */}
              <div className={`absolute top-2 right-2 w-5 h-5 rounded border-2 flex items-center justify-center ${
                isSelected
                  ? 'border-primary-500 bg-primary-500'
                  : 'border-gray-300 bg-white'
              }`}>
                {isSelected && <Check className="w-3 h-3 text-white" />}
              </div>
              
              {/* Card Info */}
              <div className="pr-8">
                <div className="font-semibold text-sm">{cardName}</div>
                <div className="text-xs opacity-75 mt-1">
                  {cardName.includes('Atlas') && 'Premium Miles Card'}
                  {cardName.includes('EPM') && 'Reward Points Card'}
                  {cardName.includes('Premier') && 'Premium Travel Card'}
                </div>
              </div>
            </button>
          );
        })}
      </div>

      {/* Selection Status */}
      <div className="text-center text-sm text-gray-600">
        {selectedCards.length === 0 && "Please select at least 2 cards"}
        {selectedCards.length === 1 && "Select at least 1 more card"}
        {selectedCards.length >= 2 && selectedCards.length <= 3 && (
          <span className="text-green-600 font-medium">
            ✓ {selectedCards.length} card{selectedCards.length > 1 ? 's' : ''} selected
          </span>
        )}
        {selectedCards.length >= 3 && (
          <span className="text-amber-600">
            Maximum 3 cards selected for focused comparison
          </span>
        )}
      </div>

      {/* Selected Cards Preview */}
      {selectedCards.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-lg p-3">
          <div className="text-sm font-medium text-gray-700 mb-2">Selected Cards:</div>
          <div className="flex flex-wrap gap-2">
            {selectedCards.map((card) => (
              <span
                key={card}
                className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-primary-100 text-primary-700"
              >
                {card}
                <button
                  onClick={() => handleCardToggle(card)}
                  className="ml-2 hover:text-primary-900"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Action Button */}
      <div className="text-center pt-2">
        <button
          onClick={handleSubmit}
          disabled={selectedCards.length < 2}
          className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed px-6 py-2"
        >
          Compare Selected Cards
        </button>
      </div>
    </div>
  );
};

export default CardSelection;
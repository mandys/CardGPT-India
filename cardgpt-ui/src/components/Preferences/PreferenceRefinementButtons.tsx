import React from 'react';
import { ArrowRight, Plane, IndianRupee, ShoppingBag, Utensils, CreditCard } from 'lucide-react';
import { usePreferences } from '../../hooks/usePreferences';
import { useStreamingChatStore } from '../../hooks/useStreamingChat';
import { UserPreferences } from '../../types';

interface PreferenceButton {
  text: string;
  preference: string;
  value: string;
  icon: React.ComponentType<any>;
}

interface PreferenceRefinementButtonsProps {
  message: string;
  onRefinementApplied?: (preference: string, value: string) => void;
  onRequery?: (refinedQuery: string) => void;
  className?: string;
}

const PreferenceRefinementButtons: React.FC<PreferenceRefinementButtonsProps> = ({
  message,
  onRefinementApplied,
  onRequery,
  className = ''
}) => {
  const { updatePreferences, isLoading, getMissingPreferencesForQuery, preferences } = usePreferences();
  const { config } = useStreamingChatStore();
  const supportedCards = config?.supported_cards || [];

  const handleRefinementClick = async (preference: string, value: string, buttonText: string) => {
    try {
      // Special case for "Manage Cards" button
      if (preference === 'show_card_selection_modal') {
        onRefinementApplied?.(preference, value);
        return;
      }

      let updatedPrefs: Partial<UserPreferences> = {};

      if (preference === 'current_cards') {
        const currentCards = preferences?.current_cards || [];
        const newCards = currentCards.includes(value)
          ? currentCards.filter(card => card !== value)
          : [...currentCards, value];
        updatedPrefs = { current_cards: newCards };
      } else {
        updatedPrefs = { [preference]: value };
      }

      // Update the preference
      await updatePreferences(updatedPrefs);
      console.log(`✅ [REFINEMENT] Applied ${preference}: ${value}`);
      
      // Call callbacks
      onRefinementApplied?.(preference, value);
      
      // Trigger requery with ORIGINAL message (preferences will be auto-included via streaming endpoint)
      if (onRequery) {
        // Clean the original message of any previous preference additions
        const cleanMessage = message.replace(/\s*\(User preference:.*?\)/g, '').trim();
        console.log(`🔄 [REFINEMENT] Triggering requery with clean message: ${cleanMessage}`);
        console.log(`🎯 [REFINEMENT] User preferences will be automatically included by backend`);
        onRequery(cleanMessage);
      }
    } catch (error) {
      console.error('Failed to apply refinement:', error);
    }
  };

  const allPreferenceButtons: PreferenceButton[] = [
    { text: "I travel domestically", preference: "travel_type", value: "domestic", icon: Plane },
    { text: "I travel internationally", preference: "travel_type", value: "international", icon: Plane },
    { text: "I travel with family", preference: "lounge_access", value: "family", icon: Plane },
    { text: "₹0 fee cards only", preference: "fee_willingness", value: "0-1000", icon: IndianRupee },
    { text: "₹1K-5K annual fee", preference: "fee_willingness", value: "1000-5000", icon: IndianRupee },
    { text: "₹5K+ annual fee OK", preference: "fee_willingness", value: "5000-10000", icon: IndianRupee },
    { text: "I spend on travel", preference: "spend_categories", value: "travel", icon: ShoppingBag },
    { text: "I spend on online shopping", preference: "spend_categories", value: "online_shopping", icon: ShoppingBag },
    { text: "I spend on dining", preference: "spend_categories", value: "dining", icon: Utensils },
    // Dynamically add buttons for each supported card
    ...supportedCards.map((card: string) => ({
      text: `I use ${card}`,
      preference: "current_cards",
      value: card,
      icon: CreditCard
    })),
    { text: "Manage my cards", preference: "show_card_selection_modal", value: "true", icon: CreditCard }
  ];

  const missingPreferences = getMissingPreferencesForQuery(message);
  const preferenceButtons: PreferenceButton[] = allPreferenceButtons.filter((button: PreferenceButton) => {
    // Special handling for spend_categories: if any spend category is missing, show all spend category buttons
    if (button.preference === 'spend_categories') {
      return missingPreferences.includes('spend_categories');
    }
    // Special handling for card selection: only show individual card buttons if current_cards is missing
    if (button.preference === 'current_cards') {
      const currentCards = preferences?.current_cards || [];
      // Only show the button if the card is not already selected and current_cards is considered missing
      return missingPreferences.includes('current_cards') && !currentCards.includes(button.value);
    }
    // Only show "Manage my cards" if current_cards or preferred_banks are missing
    if (button.preference === 'show_card_selection_modal') {
      return missingPreferences.includes('current_cards') || missingPreferences.includes('preferred_banks');
    }
    return missingPreferences.includes(button.preference);
  });

  if (preferenceButtons.length === 0) {
    return null;
  }

  return (
    <div className={`mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-700 ${className}`}>
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0 p-2 bg-blue-100 dark:bg-blue-800 rounded-lg">
          <ArrowRight className="w-4 h-4 text-blue-600 dark:text-blue-400" />
        </div>
        
        <div className="flex-1">
          <h4 className="text-sm font-medium text-blue-900 dark:text-blue-100 mb-2">
            💡 Make this more personal
          </h4>
          
          <p className="text-xs text-blue-700 dark:text-blue-300 mb-3">
            Tell me your preferences for better recommendations:
          </p>

          {/* Quick Refinement Buttons */}
          <div className="flex flex-wrap gap-2">
            {preferenceButtons.map((button: PreferenceButton, index: number) => {
              const IconComponent = button.icon;
              
              return (
                <button
                  key={index}
                  onClick={() => handleRefinementClick(button.preference, button.value, button.text)}
                  disabled={isLoading}
                  className="
                    inline-flex items-center px-3 py-2 rounded-lg text-xs font-medium transition-all
                    bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600
                    hover:border-blue-300 hover:bg-blue-50 dark:hover:bg-blue-900/20
                    text-gray-700 dark:text-gray-300 hover:text-blue-700 dark:hover:text-blue-300
                    disabled:opacity-50 disabled:cursor-not-allowed
                    focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1
                  "
                >
                  <IconComponent className="w-3 h-3 mr-1.5" />
                  {button.text}
                </button>
              );
            })}
          </div>

          {/* Additional hint */}
          <p className="text-xs text-blue-600 dark:text-blue-400 mt-2 opacity-75">
            ✨ Your preferences will be saved for future queries
          </p>
        </div>
      </div>
    </div>
  );
};

export default PreferenceRefinementButtons;
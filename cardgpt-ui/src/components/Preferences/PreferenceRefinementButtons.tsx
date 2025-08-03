import React from 'react';
import { ArrowRight, Plane, IndianRupee } from 'lucide-react';
import { usePreferences } from '../../hooks/usePreferences';

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
  const { updatePreferences, isLoading } = usePreferences();

  const handleRefinementClick = async (preference: string, value: string, buttonText: string) => {
    try {
      // Update the preference
      await updatePreferences({ [preference]: value });
      console.log(`✅ [REFINEMENT] Applied ${preference}: ${value}`);
      
      // Call callbacks
      onRefinementApplied?.(preference, value);
      
      // Trigger requery with enhanced message
      if (onRequery) {
        const enhancedMessage = `${message} (User preference: ${buttonText})`;
        console.log(`🔄 [REFINEMENT] Triggering requery with: ${enhancedMessage}`);
        onRequery(enhancedMessage);
      }
    } catch (error) {
      console.error('Failed to apply refinement:', error);
    }
  };

  // Simple predefined preference buttons
  const preferenceButtons = [
    { text: "I travel domestically", preference: "travel_type", value: "domestic", icon: Plane },
    { text: "I travel internationally", preference: "travel_type", value: "international", icon: Plane },
    { text: "I travel with family", preference: "lounge_access", value: "family", icon: Plane },
    { text: "₹0 fee cards only", preference: "fee_willingness", value: "0-1000", icon: IndianRupee },
    { text: "₹1K-5K annual fee", preference: "fee_willingness", value: "1000-5000", icon: IndianRupee },
    { text: "₹5K+ annual fee OK", preference: "fee_willingness", value: "5000-10000", icon: IndianRupee }
  ];

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
            {preferenceButtons.map((button, index) => {
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
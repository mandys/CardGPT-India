import React, { useState } from 'react';
import { X, ArrowRight, ArrowLeft, Plane, IndianRupee, ShoppingBag, CreditCard } from 'lucide-react';
import { usePreferences } from '../../hooks/usePreferences';
import { useStreamingChatStore } from '../../hooks/useStreamingChat';
import { UserPreferences } from '../../types';

interface UserPreferencesModalProps {
  isOpen: boolean;
  onClose: () => void;
  onComplete?: (preferences: UserPreferences) => void;
  triggerContext?: 'welcome' | 'manual';
  initialStep?: number; // New prop
}

interface PreferenceStep {
  id: string;
  title: string;
  subtitle: string;
  icon: React.ComponentType<any>;
  component: React.ComponentType<any>;
}

const UserPreferencesModal: React.FC<UserPreferencesModalProps> = ({
  isOpen,
  onClose,
  onComplete,
  triggerContext = 'welcome',
  initialStep = 0 // Initialize with new prop
}) => {
  const { updatePreferences, isLoading } = usePreferences();
  const [currentStep, setCurrentStep] = useState(initialStep); // Use initialStep here
  const [tempPreferences, setTempPreferences] = useState<Partial<UserPreferences>>({});

  // Step 1: Travel Preferences
  const TravelStep = () => (
    <div className="space-y-4">
      <div className="text-center mb-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          Tell us about your travel style
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          This helps us recommend cards with the right travel benefits for you
        </p>
      </div>

      <div className="space-y-3">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Where do you usually travel?
          </label>
          <div className="grid grid-cols-1 gap-2">
            {[
              { value: 'domestic', label: '🇮🇳 Domestic (within India)', desc: 'Domestic lounges, local partnerships' },
              { value: 'international', label: '🌍 International', desc: 'Global lounges, foreign currency benefits' },
              { value: 'both', label: '✈️ Both domestic & international', desc: 'Comprehensive travel benefits' }
            ].map((option) => (
              <button
                key={option.value}
                onClick={() => setTempPreferences(prev => ({ ...prev, travel_type: option.value }))}
                className={`p-3 rounded-lg border-2 text-left transition-all ${
                  tempPreferences.travel_type === option.value
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                    : 'border-gray-200 dark:border-gray-600 hover:border-blue-300'
                }`}
              >
                <div className="font-medium text-gray-900 dark:text-white">{option.label}</div>
                <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">{option.desc}</div>
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            How do you usually travel?
          </label>
          <div className="grid grid-cols-1 gap-2">
            {[
              { value: 'solo', label: '👤 Solo travel', desc: 'Individual lounge access' },
              { value: 'with_guests', label: '👥 With 1 companion', desc: 'Guest lounge access needed' },
              { value: 'family', label: '👨‍👩‍👧‍👦 With family', desc: 'Family lounge access & benefits' }
            ].map((option) => (
              <button
                key={option.value}
                onClick={() => setTempPreferences(prev => ({ ...prev, lounge_access: option.value }))}
                className={`p-3 rounded-lg border-2 text-left transition-all ${
                  tempPreferences.lounge_access === option.value
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                    : 'border-gray-200 dark:border-gray-600 hover:border-blue-300'
                }`}
              >
                <div className="font-medium text-gray-900 dark:text-white">{option.label}</div>
                <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">{option.desc}</div>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  // Step 2: Financial Preferences
  const FinancialStep = () => (
    <div className="space-y-4">
      <div className="text-center mb-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          What's your annual fee comfort zone?
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Higher fee cards often have better rewards, but we'll find the sweet spot for you
        </p>
      </div>

      <div className="grid grid-cols-1 gap-3">
        {[
          { value: '0-1000', label: '₹0 - ₹1,000', desc: 'Budget-friendly options', color: 'green' },
          { value: '1000-5000', label: '₹1,000 - ₹5,000', desc: 'Mid-range cards with good benefits', color: 'blue' },
          { value: '5000-10000', label: '₹5,000 - ₹10,000', desc: 'Premium cards with excellent rewards', color: 'purple' },
          { value: '10000+', label: '₹10,000+', desc: 'Luxury cards with exclusive benefits', color: 'gold' }
        ].map((option) => (
          <button
            key={option.value}
            onClick={() => setTempPreferences(prev => ({ ...prev, fee_willingness: option.value }))}
            className={`p-4 rounded-lg border-2 text-left transition-all ${
              tempPreferences.fee_willingness === option.value
                ? `border-${option.color}-500 bg-${option.color}-50 dark:bg-${option.color}-900/20`
                : 'border-gray-200 dark:border-gray-600 hover:border-blue-300'
            }`}
          >
            <div className="font-medium text-gray-900 dark:text-white">{option.label}</div>
            <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">{option.desc}</div>
          </button>
        ))}
      </div>
    </div>
  );

  // Step 3: Spending Categories
  const SpendingStep = () => {
    const categories = [
      { value: 'travel', label: '✈️ Travel', desc: 'Flights, hotels, bookings' },
      { value: 'dining', label: '🍽️ Dining', desc: 'Restaurants, food delivery' },
      { value: 'online_shopping', label: '🛒 Online Shopping', desc: 'E-commerce, digital purchases' },
      { value: 'fuel', label: '⛽ Fuel', desc: 'Petrol, CNG, electric charging' },
      { value: 'groceries', label: '🛍️ Groceries', desc: 'Supermarkets, daily essentials' },
      { value: 'utilities', label: '💡 Utilities', desc: 'Bills, recharges, subscriptions' }
    ];

    const selectedCategories = tempPreferences.spend_categories || [];

    const toggleCategory = (category: string) => {
      const newCategories = selectedCategories.includes(category)
        ? selectedCategories.filter(cat => cat !== category)
        : [...selectedCategories, category];
      
      setTempPreferences(prev => ({ ...prev, spend_categories: newCategories }));
    };

    return (
      <div className="space-y-4">
        <div className="text-center mb-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            Where do you spend the most?
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Select your top spending categories (choose 2-3 for best results)
          </p>
        </div>

        <div className="grid grid-cols-2 gap-3">
          {categories.map((category) => {
            const isSelected = selectedCategories.includes(category.value);
            return (
              <button
                key={category.value}
                onClick={() => toggleCategory(category.value)}
                className={`p-3 rounded-lg border-2 text-left transition-all ${
                  isSelected
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                    : 'border-gray-200 dark:border-gray-600 hover:border-blue-300'
                }`}
              >
                <div className="font-medium text-gray-900 dark:text-white">{category.label}</div>
                <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">{category.desc}</div>
              </button>
            );
          })}
        </div>

        {selectedCategories.length > 0 && (
          <div className="text-center text-sm text-gray-600 dark:text-gray-400">
            Selected {selectedCategories.length} categories
          </div>
        )}
      </div>
    );
  };

  

  // Step 4: Card & Bank Preferences
  const CardBankStep = () => {
    const { config } = useStreamingChatStore();
    const supportedCards = config?.supported_cards || [];

    const toggleCardSelection = (cardName: string) => {
      const currentCards = tempPreferences.current_cards || [];
      const newCards = currentCards.includes(cardName)
        ? currentCards.filter(card => card !== cardName)
        : [...currentCards, cardName];
      setTempPreferences(prev => ({ ...prev, current_cards: newCards }));
    };

    const handleBankInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const banks = e.target.value.split(',').map(bank => bank.trim()).filter(bank => bank.length > 0);
      setTempPreferences(prev => ({ ...prev, preferred_banks: banks }));
    };

    return (
      <div className="space-y-4">
        <div className="text-center mb-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            Which cards do you currently use or prefer?
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Knowing your current cards helps us give more tailored advice.
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Your current credit cards
          </label>
          <div className="grid grid-cols-2 gap-2">
            {supportedCards.map((card: string) => {
              const isSelected = (tempPreferences.current_cards || []).includes(card);
              return (
                <button
                  key={card}
                  onClick={() => toggleCardSelection(card)}
                  className={`p-3 rounded-lg border-2 text-left transition-all ${
                    isSelected
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                      : 'border-gray-200 dark:border-gray-600 hover:border-blue-300'
                  }`}
                >
                  <div className="font-medium text-gray-900 dark:text-white">{card}</div>
                </button>
              );
            })}
          </div>
        </div>

        <div>
          <label htmlFor="preferred_banks" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Preferred banks (comma-separated)
          </label>
          <input
            type="text"
            id="preferred_banks"
            value={(tempPreferences.preferred_banks || []).join(', ')}
            onChange={handleBankInputChange}
            placeholder="e.g., HDFC Bank, ICICI Bank"
            className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>
    );
  };

  const steps: PreferenceStep[] = [
    {
      id: 'travel',
      title: 'Travel Style',
      subtitle: 'How and where you travel',
      icon: Plane,
      component: TravelStep
    },
    {
      id: 'financial',
      title: 'Budget',
      subtitle: 'Annual fee preferences',
      icon: IndianRupee,
      component: FinancialStep
    },
    {
      id: 'spending',
      title: 'Spending',
      subtitle: 'Top spending categories',
      icon: ShoppingBag,
      component: SpendingStep
    },
    {
      id: 'cards',
      title: 'Cards & Banks',
      subtitle: 'Your current cards and preferred banks',
      icon: CreditCard, // Using CreditCard icon
      component: CardBankStep
    }
  ];

  const currentStepData = steps[currentStep];
  const CurrentStepComponent = currentStepData.component;

  const canProceed = () => {
    switch (currentStep) {
      case 0: // Travel step
        return tempPreferences.travel_type && tempPreferences.lounge_access;
      case 1: // Financial step
        return tempPreferences.fee_willingness;
      case 2: // Spending step
        return tempPreferences.spend_categories && tempPreferences.spend_categories.length > 0;
      case 3: // Card & Bank step
        // This step is optional, so always allow proceeding if at least one field is filled or skipped
        return true; 
      default:
        return false;
    }
  };

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleComplete();
    }
  };

  const handleComplete = async () => {
    try {
      await updatePreferences(tempPreferences);
      onComplete?.(tempPreferences as UserPreferences);
      onClose();
    } catch (error) {
      console.error('Failed to save preferences:', error);
    }
  };

  const handleSkip = () => {
    onClose();
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black bg-opacity-50 z-50" />
      
      {/* Modal */}
      <div className="fixed inset-0 z-50 overflow-hidden flex items-center justify-center p-4">
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-md max-h-[90vh] overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
                <currentStepData.icon className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                  {triggerContext === 'welcome' ? 'Welcome to CardGPT!' : 'Quick Setup'}
                </h2>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Step {currentStep + 1} of {steps.length}
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 text-gray-500 dark:text-gray-400" />
            </button>
          </div>

          {/* Progress Bar */}
          <div className="px-6 pt-4">
            <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mb-2">
              {steps.map((step, index) => (
                <span key={step.id} className={index <= currentStep ? 'text-blue-600 dark:text-blue-400' : ''}>
                  {step.title}
                </span>
              ))}
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
              />
            </div>
          </div>

          {/* Content */}
          <div className="p-6 overflow-y-auto max-h-96">
            <CurrentStepComponent />
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between p-6 border-t border-gray-200 dark:border-gray-700">
            <div className="flex space-x-3">
              {currentStep > 0 && (
                <button
                  onClick={() => setCurrentStep(currentStep - 1)}
                  disabled={isLoading}
                  className="flex items-center px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 disabled:opacity-50"
                >
                  <ArrowLeft className="w-4 h-4 mr-1" />
                  Back
                </button>
              )}
              <button
                onClick={handleSkip}
                disabled={isLoading}
                className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 disabled:opacity-50"
              >
                Skip for now
              </button>
            </div>

            <button
              onClick={handleNext}
              disabled={!canProceed() || isLoading}
              className="flex items-center px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {currentStep === steps.length - 1 ? 'Complete' : 'Next'}
              {currentStep < steps.length - 1 && <ArrowRight className="w-4 h-4 ml-1" />}
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default UserPreferencesModal;
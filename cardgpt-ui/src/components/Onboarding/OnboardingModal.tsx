import React, { useState, useEffect } from 'react';
import { X, ArrowRight, ArrowLeft, CreditCard, Sparkles } from 'lucide-react';
import { useOnboarding } from '../../hooks/useOnboarding';
import { usePreferences } from '../../hooks/usePreferences';
import StepPrimaryGoal from './StepPrimaryGoal';
import StepCurrentCards from './StepCurrentCards';
import StepQuickPrefs from './StepQuickPrefs';
import { OnboardingData } from '../../types/onboarding';

interface OnboardingModalProps {
  isOpen: boolean;
  onClose: () => void;
  onComplete?: (preferences: any) => void;
  initialData?: Partial<OnboardingData>;
}

const OnboardingModal: React.FC<OnboardingModalProps> = ({
  isOpen,
  onClose,
  onComplete,
  initialData,
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const { updatePreferences, isLoading } = usePreferences();
  
  const {
    data,
    setPrimaryGoal,
    setMonthlySpending,
    toggleSpendingCategory,
    toggleCurrentCard,
    togglePreference,
    convertToUserPreferences,
    isStep1Complete,
  } = useOnboarding(initialData);

  // Reset to step 0 when modal opens
  useEffect(() => {
    if (isOpen) {
      setCurrentStep(0);
    }
  }, [isOpen]);

  const steps = [
    {
      id: 'primary',
      title: 'Goals & Spending',
      subtitle: 'Tell us your primary needs',
      icon: CreditCard,
      component: StepPrimaryGoal,
      required: true,
    },
    {
      id: 'cards',
      title: 'Current Cards',
      subtitle: 'Cards you currently have',
      icon: CreditCard,
      component: StepCurrentCards,
      required: false,
    },
    {
      id: 'preferences', 
      title: 'Quick Preferences',
      subtitle: 'Fine-tune your recommendations',
      icon: Sparkles,
      component: StepQuickPrefs,
      required: false,
    },
  ];

  const currentStepData = steps[currentStep];
  const isLastStep = currentStep === steps.length - 1;

  const canProceed = () => {
    switch (currentStep) {
      case 0: // Primary Goal step
        return isStep1Complete();
      case 1: // Current Cards step (optional)
        return true;
      case 2: // Quick Preferences step (optional)
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

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = async () => {
    try {
      // Convert onboarding data to UserPreferences format
      const userPreferences = convertToUserPreferences();
      console.log('🎯 [ONBOARDING] Converted onboarding data to UserPreferences:', userPreferences);
      console.log('🎯 [ONBOARDING] Original onboarding data:', data);
      
      // Save preferences using existing system
      console.log('🎯 [ONBOARDING] Saving preferences via updatePreferences...');
      await updatePreferences(userPreferences);
      console.log('✅ [ONBOARDING] Preferences saved successfully');
      
      // Call completion callback
      onComplete?.(userPreferences);
      
      // Close modal
      onClose();
    } catch (error) {
      console.error('❌ [ONBOARDING] Failed to save onboarding preferences:', error);
    }
  };

  const handleSkip = () => {
    onClose();
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
        {/* Modal */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-md max-h-[90vh] overflow-hidden">
          
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
                <currentStepData.icon className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Welcome to CardGPT!
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

          {/* Progress Indicator */}
          <div className="px-4 pt-4">
            <div className="flex justify-center space-x-2 mb-4">
              {steps.map((_, index) => (
                <div
                  key={index}
                  className={`w-2 h-2 rounded-full transition-all ${
                    index <= currentStep 
                      ? 'bg-blue-500' 
                      : 'bg-gray-300 dark:bg-gray-600'
                  }`}
                />
              ))}
            </div>
          </div>

          {/* Content */}
          <div className="p-4 max-h-[60vh] overflow-y-auto">
            {currentStep === 0 && (
              <StepPrimaryGoal
                selectedGoal={data.primaryGoal}
                selectedSpending={data.monthlySpending}
                selectedCategories={data.topCategories}
                onGoalChange={setPrimaryGoal}
                onSpendingChange={setMonthlySpending}
                onCategoryToggle={toggleSpendingCategory}
              />
            )}
            
            {currentStep === 1 && (
              <StepCurrentCards
                selectedCards={data.currentCards}
                onCardToggle={toggleCurrentCard}
              />
            )}
            
            {currentStep === 2 && (
              <StepQuickPrefs
                preferences={data.preferences}
                onTogglePreference={togglePreference}
              />
            )}
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between p-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex space-x-3">
              {currentStep > 0 && (
                <button
                  onClick={handleBack}
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
              className={`flex items-center px-6 py-2 rounded-lg transition-colors ${
                canProceed() && !isLoading
                  ? 'bg-blue-600 text-white hover:bg-blue-700'
                  : 'bg-gray-300 dark:bg-gray-600 text-gray-500 cursor-not-allowed'
              }`}
            >
              {isLastStep ? (
                <>
                  Complete
                  <Sparkles className="w-4 h-4 ml-1" />
                </>
              ) : (
                <>
                  Next
                  <ArrowRight className="w-4 h-4 ml-1" />
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default OnboardingModal;
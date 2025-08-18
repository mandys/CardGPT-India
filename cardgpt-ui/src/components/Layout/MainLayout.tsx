import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
// Authentication handled by individual components
import Header from './Header';
import Sidebar from './Sidebar';
import MobileBottomNav from './MobileBottomNav';
import ChatInterface from '../Chat/ChatInterface';
import SettingsModal from '../Settings/SettingsModal';
import { OnboardingModal } from '../Onboarding';
import { usePreferences } from '../../hooks/usePreferences';
import useQueryLimits from '../../hooks/useQueryLimits';
import { useStreamingChatStore } from '../../hooks/useStreamingChat';
import { useSidebar } from '../../hooks/useSidebar';
import { apiClient } from '../../services/api';
import { QueryMode, CardFilter, UserPreferences } from '../../types';
import { OnboardingData } from '../../types/onboarding';

const MainLayout: React.FC = () => {
  const location = useLocation();
  const [isConnected, setIsConnected] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isSettingsModalOpen, setIsSettingsModalOpen] = useState(false);
  const [isOnboardingModalOpen, setIsOnboardingModalOpen] = useState(false);
  const [isUpdatePreferencesMode, setIsUpdatePreferencesMode] = useState(false);
  const [hasUserDismissedModal, setHasUserDismissedModal] = useState(false);
  
  const {
    messages,
    isLoading,
    isStreaming,
    currentStatus,
    settings,
    config,
    sendMessageStream,
    clearMessages,
    setSettings,
    loadConfig,
    setError,
  } = useStreamingChatStore();
  
  const { isOpen, isMobile } = useSidebar();
  const { checkAndIncrementQuery, openSignIn } = useQueryLimits();
  const { 
    updatePreferences, 
    preferences, 
    hasLoadedInitial, 
    isEmpty, 
    completionPercentage,
 
  } = usePreferences();

  // Test connection on mount
  useEffect(() => {
    testConnection();
    loadConfig();
  }, [loadConfig]);

  // Handle pre-filled query from landing page
  useEffect(() => {
    const state = location.state as { prefilledQuery?: string } | null;
    const prefilledQuery = state?.prefilledQuery;
    if (prefilledQuery && isConnected && typeof prefilledQuery === 'string') {
      // Small delay to ensure the interface is ready
      const timer = setTimeout(() => {
        handleSendMessage(prefilledQuery);
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [location.state, isConnected]);

  // First-time user onboarding modal (streamlined)
  useEffect(() => {
    console.log('🔍 Onboarding check:', { hasLoadedInitial, isEmpty, completionPercentage, preferences });
    // Only show if preferences have loaded and user has very few preferences
    // Also check if preferences is null or has no meaningful data
    const hasNoPrefData = !preferences || Object.keys(preferences).length === 0 || 
                         (!preferences.travel_type && !preferences.fee_willingness && 
                          (!preferences.spend_categories || preferences.spend_categories.length === 0));
    
    if (hasLoadedInitial && (isEmpty || hasNoPrefData) && completionPercentage <= 10 && !hasUserDismissedModal) {
      console.log('✅ Showing streamlined onboarding modal for first-time user');
      // Small delay to let the interface settle
      const timer = setTimeout(() => {
        setIsOnboardingModalOpen(true);
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [hasLoadedInitial, isEmpty, completionPercentage, preferences, hasUserDismissedModal]);

  const testConnection = async () => {
    try {
      const connected = await apiClient.testConnection();
      setIsConnected(connected);
    } catch (error) {
      setIsConnected(false);
      console.error('Connection test failed:', error);
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await testConnection();
    await loadConfig();
    setIsRefreshing(false);
  };

  const handleSendMessage = async (message: string) => {
    if (!isConnected) {
      setError({
        error: 'Not Connected',
        detail: 'Please check your backend connection and try again.',
        code: 'CONNECTION_ERROR',
        timestamp: new Date().toISOString(),
      });
      return;
    }
    
    // Check query limits before sending (covers all entry points)
    const canProceed = await checkAndIncrementQuery();
    if (!canProceed) {
      // Query limit reached - user will see the badge status update
      console.log('Query limit reached for:', message.substring(0, 50) + '...');
      return;
    }
    
    // Note: User preferences are now collected via post-response refinement buttons
    await sendMessageStream(message);
  };

  const handleExampleClick = (example: string) => {
    handleSendMessage(example);
  };

  const handleCardSelection = (selectedCards: string[], originalQuery: string) => {
    // Create a new query with selected cards
    const cardsList = selectedCards.join(', ');
    
    // First, extract and preserve spending amounts using Indian currency patterns
    const amountPatterns = [
      /₹\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:lakh|l\b)/gi,
      /₹\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:crore|cr\b)/gi,
      /₹\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:thousand|k\b)/gi,
      /₹\s*(\d+(?:,\d+)*(?:\.\d+)?)/gi,
      /(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:lakh|l\b)/gi,
      /(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:crore|cr\b)/gi,
      /(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:thousand|k\b)/gi,
    ];
    
    let detectedAmount = '';
    for (const pattern of amountPatterns) {
      const match = originalQuery.match(pattern);
      if (match) {
        detectedAmount = match[0].trim();
        break;
      }
    }
    
    // Extract the core topic from the original query
    // Remove common question words but preserve amounts and key context
    let topic = originalQuery.toLowerCase()
      .replace(/💸|💰|🎯|📊/g, '') // Remove emojis
      .replace(/tell me|which card|which|what|how|card|is|better|best|for|the|\?/g, '') // Remove question words only
      .replace(/\s+/g, ' ') // Collapse multiple spaces
      .trim();
    
    // If topic is too short or empty, use a more conservative approach
    if (!topic || topic.length < 3) {
      topic = originalQuery.toLowerCase()
        .replace(/💸|💰|🎯|📊/g, '') // Remove emojis
        .replace(/tell me which card is better for|which card is better for|tell me|which card|which|what|how|the|\?/g, '')
        .trim();
    }
    
    // Clean up common patterns while preserving amounts and create final topic
    if (topic.includes('insurance')) {
      topic = detectedAmount ? `${detectedAmount} insurance spends` : 'insurance spends';
    } else if (topic.includes('hotel')) {
      topic = detectedAmount ? `${detectedAmount} hotel spends` : 'hotel spends';
    } else if (topic.includes('travel')) {
      topic = detectedAmount ? `${detectedAmount} travel spends` : 'travel spends';
    } else if (topic.includes('utility') || topic.includes('utilities')) {
      topic = detectedAmount ? `${detectedAmount} utility spends` : 'utility spends';
    } else if (topic.includes('fuel')) {
      topic = detectedAmount ? `${detectedAmount} fuel spends` : 'fuel spends';
    } else if (detectedAmount) {
      // If we have an amount but no specific category, preserve the original context
      topic = topic || `${detectedAmount} spends`;
    } else if (!topic) {
      topic = 'general spending';
    }
    
    const newQuery = `Compare ${cardsList} for ${topic}`;
    handleSendMessage(newQuery);
  };

  const handleModelChange = (model: string) => {
    setSettings({ selectedModel: model });
  };

  const handleQueryModeChange = (mode: QueryMode) => {
    setSettings({ queryMode: mode });
  };

  const handleCardFilterChange = (filter: CardFilter) => {
    setSettings({ cardFilter: filter });
  };

  const handleTopKChange = (topK: number) => {
    setSettings({ topK });
  };

  const handleShowUpdatePreferences = () => {
    setIsUpdatePreferencesMode(true);
    setIsOnboardingModalOpen(true);
  };

  // Create initial data for update mode by converting current preferences
  const getInitialOnboardingData = () => {
    if (!isUpdatePreferencesMode || !preferences) return undefined;
    
    // Map fee_willingness back to monthly spending bracket
    let monthlySpending: string | undefined;
    switch (preferences.fee_willingness) {
      case '0-1000':
      case '1000-5000':
        monthlySpending = '0-25000';
        break;
      case '5000-10000':
        monthlySpending = '25000-75000';
        break;
      case '10000+':
        monthlySpending = '75000+';
        break;
    }
    
    // Simple mapping from UserPreferences to OnboardingData
    const initialData: Partial<OnboardingData> = {
      currentCards: preferences.current_cards || [],
      monthlySpending: monthlySpending as any, // Cast to match OnboardingData type
      topCategories: preferences.spend_categories?.map(cat => {
        // Map category names to onboarding categories
        const categoryMap: Record<string, any> = {
          'online': 'online_shopping',
          'dining': 'dining', 
          'groceries': 'groceries',
          'fuel': 'fuel',
          'travel': 'travel',
          'utilities': 'utilities'
        };
        return categoryMap[cat] || cat;
      }).filter(Boolean) || [],
      preferences: {
        lowFees: preferences.fee_willingness === '0-1000',
        international: preferences.travel_type === 'international' || preferences.travel_type === 'both',
        business: false, // Default as we don't have this data
        digitalFirst: false, // Default as we don't have this data
      }
    };
    
    console.log('🎯 [INITIAL DATA] Mapping preferences to onboarding data:', {
      preferences,
      initialData
    });
    
    return initialData;
  };

  const handlePreferenceRefinement = async (preference: string, value: string) => {
    try {
      // Special case: if preference is 'requery', it means we should requery with updated preferences
      if (preference === 'requery') {
        // The value is actually the query to re-send
        const queryToResend = value;
        console.log('Requerying with updated preferences:', queryToResend);
        // Send the query again with the updated preferences
        await sendMessageStream(queryToResend);
        return;
      }

      // Special case: if preference is 'show_card_selection_modal', open the onboarding modal
      if (preference === 'show_card_selection_modal') {
        setIsOnboardingModalOpen(true);
        return;
      }
      
      // Update the specific preference
      const updatedPreferences = { ...preferences };
      
      // Parse the preference path (e.g., "travelFrequency", "spendingCategories.travel")
      const keys = preference.split('.');
      let target: any = updatedPreferences;
      
      // Navigate to the nested property
      for (let i = 0; i < keys.length - 1; i++) {
        if (!(keys[i] in target)) {
          target[keys[i]] = {};
        }
        target = target[keys[i]];
      }
      
      // Set the final value
      const finalKey = keys[keys.length - 1];
      target[finalKey] = value;
      
      // Update preferences via the API
      await updatePreferences(updatedPreferences);
      
      console.log('Preference updated:', preference, '=', value);
    } catch (error) {
      console.error('Failed to update preference:', error);
    }
  };

  const availableModels = config?.available_models || [];

  return (
    <div className="h-screen flex flex-col bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <Header
        isConnected={isConnected}
        onRefresh={handleRefresh}
        isLoading={isRefreshing}
        onShowAuth={() => {}}
      />
      
      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Sidebar */}
        <Sidebar
          models={availableModels}
          selectedModel={settings.selectedModel}
          onModelChange={handleModelChange}
          queryMode={settings.queryMode}
          onQueryModeChange={handleQueryModeChange}
          cardFilter={settings.cardFilter}
          onCardFilterChange={handleCardFilterChange}
          topK={settings.topK}
          onTopKChange={handleTopKChange}
          isLoading={isLoading}
          onShowOnboarding={() => {
            setIsUpdatePreferencesMode(false);
            setIsOnboardingModalOpen(true);
          }}
          onShowUpdatePreferences={handleShowUpdatePreferences}
        />
        
        {/* Chat Interface */}
        <div className={`flex-1 flex flex-col transition-all duration-300 ${
          !isMobile && isOpen ? 'ml-0' : 'ml-0'
        } ${isMobile ? 'pb-16' : ''}`}>
          <ChatInterface
            messages={messages}
            isLoading={isLoading || isStreaming}
            currentStatus={currentStatus}
            onSendMessage={handleSendMessage}
            onExampleClick={handleExampleClick}
            onCardSelection={handleCardSelection}
            onShowAuth={() => {}}
            onPreferenceRefinement={handlePreferenceRefinement}
          />
        </div>
      </div>
      
      {/* Mobile Bottom Navigation */}
      <MobileBottomNav
        onClearChat={clearMessages}
        onShowSettings={() => setIsSettingsModalOpen(true)}
        onShowAnalytics={() => {/* TODO: Implement analytics view */}}
        onShowSignIn={openSignIn}
      />
      
      {/* Settings Modal */}
      <SettingsModal
        isOpen={isSettingsModalOpen}
        onClose={() => setIsSettingsModalOpen(false)}
        models={availableModels}
        selectedModel={settings.selectedModel}
        onModelChange={handleModelChange}
        queryMode={settings.queryMode}
        onQueryModeChange={handleQueryModeChange}
        cardFilter={settings.cardFilter}
        onCardFilterChange={handleCardFilterChange}
        topK={settings.topK}
        onTopKChange={handleTopKChange}
        isLoading={isLoading}
        onShowOnboarding={() => {
          setIsUpdatePreferencesMode(false);
          setIsOnboardingModalOpen(true);
        }}
        onShowUpdatePreferences={handleShowUpdatePreferences}
      />
      
      

      {/* Streamlined Onboarding Modal (for new users) */}
      <OnboardingModal
        isOpen={isOnboardingModalOpen}
        onClose={() => {
          setIsOnboardingModalOpen(false);
          setIsUpdatePreferencesMode(false);
          setHasUserDismissedModal(true); // Track that user dismissed modal
        }}
        onComplete={(preferences) => {
          updatePreferences(preferences);
          setIsOnboardingModalOpen(false);
          setIsUpdatePreferencesMode(false);
          setHasUserDismissedModal(true); // Track completion as dismissal too
        }}
        initialData={getInitialOnboardingData()}
      />

    </div>
  );
};

export default MainLayout;
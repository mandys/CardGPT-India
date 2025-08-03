import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import Header from './Header';
import Sidebar from './Sidebar';
import MobileBottomNav from './MobileBottomNav';
import ChatInterface from '../Chat/ChatInterface';
import SettingsModal from '../Settings/SettingsModal';
import AuthModal from '../Auth/AuthModal';
import UserProfile from '../Auth/UserProfile';
import { UserPreferencesModal, PreferenceSidebar } from '../Preferences';
import { usePreferences } from '../../hooks/usePreferences';
import { useStreamingChatStore } from '../../hooks/useStreamingChat';
import { useSidebar } from '../../hooks/useSidebar';
import { useAuth } from '../../contexts/AuthContext';
import { apiClient } from '../../services/api';
import { QueryMode, CardFilter } from '../../types';

const MainLayout: React.FC = () => {
  const location = useLocation();
  const [isConnected, setIsConnected] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isSettingsModalOpen, setIsSettingsModalOpen] = useState(false);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [isUserProfileOpen, setIsUserProfileOpen] = useState(false);
  const [isPreferencesModalOpen, setIsPreferencesModalOpen] = useState(false);
  const [isPreferencesSidebarOpen, setIsPreferencesSidebarOpen] = useState(false);
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
  const { isAuthenticated, queryLimit, incrementQuery, checkQueryLimit } = useAuth();
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

  // First-time user welcome modal
  useEffect(() => {
    console.log('🔍 Preference modal check:', { hasLoadedInitial, isEmpty, completionPercentage, preferences });
    // Only show if preferences have loaded and user has very few preferences
    // Also check if preferences is null or has no meaningful data
    const hasNoPrefData = !preferences || Object.keys(preferences).length === 0 || 
                         (!preferences.travel_type && !preferences.fee_willingness && 
                          (!preferences.spend_categories || preferences.spend_categories.length === 0));
    
    if (hasLoadedInitial && (isEmpty || hasNoPrefData) && completionPercentage <= 10 && !hasUserDismissedModal) {
      console.log('✅ Showing preference modal for first-time user');
      // Small delay to let the interface settle
      const timer = setTimeout(() => {
        setIsPreferencesModalOpen(true);
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
    
    // Check if user can make a query
    if (queryLimit && !queryLimit.can_query) {
      setIsAuthModalOpen(true);
      return;
    }
    
    // Increment query count before sending
    const canProceed = await incrementQuery();
    if (!canProceed) {
      setIsAuthModalOpen(true);
      return;
    }
    
    // Note: User preferences are now collected via post-response refinement buttons
    
    await sendMessageStream(message);
    
    // Refresh query limit after sending
    await checkQueryLimit();
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
        onShowAuth={() => setIsAuthModalOpen(true)}
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
            onShowAuth={() => setIsAuthModalOpen(true)}
            onPreferenceRefinement={handlePreferenceRefinement}
          />
        </div>
      </div>
      
      {/* Mobile Bottom Navigation */}
      <MobileBottomNav
        onClearChat={clearMessages}
        onShowSettings={() => setIsSettingsModalOpen(true)}
        onShowAnalytics={() => {/* TODO: Implement analytics view */}}
        onShowSignIn={() => {
          if (isAuthenticated) {
            setIsUserProfileOpen(true);
          } else {
            setIsAuthModalOpen(true);
          }
        }}
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
        onShowPreferences={() => setIsPreferencesModalOpen(true)}
        onShowPreferencesSidebar={() => setIsPreferencesSidebarOpen(true)}
      />
      
      {/* Auth Modal */}
      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
      />
      
      {/* User Profile Modal */}
      {isUserProfileOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="max-w-md w-full">
            <UserProfile onClose={() => setIsUserProfileOpen(false)} />
          </div>
        </div>
      )}

      {/* User Preferences Modal */}
      <UserPreferencesModal
        isOpen={isPreferencesModalOpen}
        onClose={() => {
          setIsPreferencesModalOpen(false);
          setHasUserDismissedModal(true); // Track that user dismissed modal
        }}
        onComplete={(preferences) => {
          updatePreferences(preferences);
          setIsPreferencesModalOpen(false);
          setHasUserDismissedModal(true); // Track completion as dismissal too
        }}
        triggerContext={isEmpty ? "welcome" : "manual"}
      />

      {/* Preferences Sidebar */}
      <PreferenceSidebar
        isOpen={isPreferencesSidebarOpen}
        onClose={() => setIsPreferencesSidebarOpen(false)}
      />
    </div>
  );
};

export default MainLayout;
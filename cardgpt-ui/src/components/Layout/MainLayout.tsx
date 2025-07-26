import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import Header from './Header';
import Sidebar from './Sidebar';
import MobileBottomNav from './MobileBottomNav';
import ChatInterface from '../Chat/ChatInterface';
import SettingsModal from '../Settings/SettingsModal';
import AuthModal from '../Auth/AuthModal';
import UserProfile from '../Auth/UserProfile';
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
    
    // Extract the core topic from the original query
    // Remove common question words and extract the spending category or topic
    let topic = originalQuery.toLowerCase()
      .replace(/💸|💰|🎯|📊/g, '') // Remove emojis
      .replace(/tell me|which card|which|what|how|card|is|better|best|for|spends?|spending|spend|the|\?/g, '') // Remove question words
      .replace(/\s+/g, ' ') // Collapse multiple spaces
      .trim();
    
    // If topic is too short or empty, use a generic format
    if (!topic || topic.length < 3) {
      topic = originalQuery.toLowerCase()
        .replace(/💸|💰|🎯|📊/g, '') // Remove emojis
        .replace(/tell me which card is better for|which card is better for|tell me|which card|which|what|how|the|\?/g, '')
        .trim();
    }
    
    // Clean up common patterns and create final topic
    if (topic.includes('insurance')) {
      topic = 'insurance spends';
    } else if (topic.includes('hotel')) {
      topic = 'hotel spends';
    } else if (topic.includes('travel')) {
      topic = 'travel spends';
    } else if (topic.includes('utility') || topic.includes('utilities')) {
      topic = 'utility spends';
    } else if (topic.includes('fuel')) {
      topic = 'fuel spends';
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
    </div>
  );
};

export default MainLayout;
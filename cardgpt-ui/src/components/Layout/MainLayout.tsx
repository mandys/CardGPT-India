import React, { useState, useEffect } from 'react';
import Header from './Header';
import Sidebar from './Sidebar';
import MobileBottomNav from './MobileBottomNav';
import ChatInterface from '../Chat/ChatInterface';
import { useChatStore } from '../../hooks/useChat';
import { useSidebar } from '../../hooks/useSidebar';
import { apiClient } from '../../services/api';
import { QueryMode, CardFilter } from '../../types';

const MainLayout: React.FC = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  
  const {
    messages,
    isLoading,
    settings,
    config,
    sendMessage,
    clearMessages,
    setSettings,
    loadConfig,
    setError,
  } = useChatStore();
  
  const { isOpen, isMobile } = useSidebar();

  // Test connection on mount
  useEffect(() => {
    testConnection();
    loadConfig();
  }, [loadConfig]);

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
    
    await sendMessage(message);
  };

  const handleExampleClick = (example: string) => {
    handleSendMessage(example);
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
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <Header
        isConnected={isConnected}
        onRefresh={handleRefresh}
        isLoading={isRefreshing}
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
            isLoading={isLoading}
            onSendMessage={handleSendMessage}
            onExampleClick={handleExampleClick}
          />
        </div>
      </div>
      
      {/* Mobile Bottom Navigation */}
      <MobileBottomNav
        onClearChat={clearMessages}
        onShowAnalytics={() => {/* TODO: Implement analytics view */}}
        onShowProfile={() => {/* TODO: Implement profile view */}}
      />
    </div>
  );
};

export default MainLayout;
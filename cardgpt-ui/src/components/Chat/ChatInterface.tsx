import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { ChatMessage } from '../../types';
import { useAuth } from '../../contexts/AuthContext';
import MessageBubble from './MessageBubble';
import QueryLimitWarning from './QueryLimitWarning';

interface ChatInterfaceProps {
  messages: ChatMessage[];
  isLoading: boolean;
  currentStatus?: string | null;
  onSendMessage: (message: string) => void;
  onExampleClick: (example: string) => void;
  onCardSelection?: (selectedCards: string[], originalQuery: string) => void;
  onShowAuth?: () => void;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  messages,
  isLoading,
  currentStatus,
  onSendMessage,
  onExampleClick,
  onCardSelection,
  onShowAuth,
}) => {
  const [inputMessage, setInputMessage] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const { queryLimit, isAuthenticated } = useAuth();

  // Check if input should be disabled due to query limit
  const inputDisabled = Boolean(queryLimit && !queryLimit.can_query && !isAuthenticated);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (inputMessage.trim() && !isLoading) {
      onSendMessage(inputMessage.trim());
      setInputMessage('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleInputFocus = (e: React.FocusEvent<HTMLInputElement>) => {
    if (inputDisabled) {
      e.preventDefault();
      e.target.blur();
      onShowAuth?.();
    }
  };

  const handleInputClick = (e: React.MouseEvent<HTMLInputElement>) => {
    if (inputDisabled) {
      e.preventDefault();
      onShowAuth?.();
    }
  };

  const exampleQuestions = [
    '🔥 Which card is fire for travel rewards?',
    '💰 Best cashback card that won\'t break me?',
    '✈️ Atlas vs EPM - which one slaps harder?',
    '🎯 Annual fees? We don\'t do those here',
    '📱 UPI cashback cards that actually pay',
    '🏠 Rent payments with max rewards?',
  ];

  return (
    <div className="flex flex-col h-full">
      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 dark:bg-gray-900">
        {messages.length === 0 ? (
          <div className="text-center py-8">
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-gray-800 dark:text-white mb-3 text-center">
                Ask me anything about Indian credit cards 💳
              </h2>
              <p className="text-gray-600 dark:text-gray-400 text-center">
                Get instant, personalized insights!
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-4xl mx-auto">
              {exampleQuestions.map((example, index) => (
                <button
                  key={index}
                  onClick={() => onExampleClick(example)}
                  className="glass-card p-4 text-left text-sm text-gray-700 dark:text-gray-300 hover:text-purple-600 dark:hover:text-purple-400 transform transition-all duration-300 hover:scale-105 hover:glow-purple"
                >
                  {example}
                </button>
              ))}
            </div>
            
            {/* Query Limit Warning */}
            <QueryLimitWarning onSignIn={() => onShowAuth?.()} />
          </div>
        ) : (
          <>
            {/* Query Limit Warning for existing chat */}
            <QueryLimitWarning onSignIn={() => onShowAuth?.()} />
            
            {messages.map((message) => (
              <MessageBubble 
                key={message.id} 
                message={message} 
                onCardSelection={onCardSelection}
              />
            ))}
            {/* Status Indicator - Compact style like typing indicator */}
            {currentStatus && (
              <div className="flex justify-start animate-fade-in">
                <div className="flex items-start space-x-3 max-w-4xl">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center bg-gray-200 dark:bg-gray-700">
                    <div className="w-3 h-3 rounded-full bg-blue-500 animate-pulse"></div>
                  </div>
                  <div className="bg-white dark:bg-gray-800 shadow-sm border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2">
                    <div className="text-gray-600 dark:text-gray-400 text-xs flex items-center gap-1">
                      <div className="flex space-x-1">
                        <div className="w-1 h-1 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                        <div className="w-1 h-1 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                        <div className="w-1 h-1 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                      </div>
                      {currentStatus}
                    </div>
                  </div>
                </div>
              </div>
            )}
            {/* TypingIndicator disabled for streaming - using in-message indicator instead */}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="glass-card m-4 p-4 border-0">
        {inputDisabled && (
          <div className="mb-3 flex items-center justify-center">
            <div className="text-sm text-orange-600 dark:text-orange-400 bg-orange-50 dark:bg-orange-900/20 px-3 py-2 rounded-lg border border-orange-200 dark:border-orange-800">
              ⚠️ Daily limit reached ({queryLimit?.current_count}/{queryLimit?.limit} queries). 
              <button 
                onClick={() => onShowAuth?.()} 
                className="ml-1 text-orange-700 dark:text-orange-300 underline hover:text-orange-800 dark:hover:text-orange-200"
              >
                Sign in for unlimited access
              </button>
            </div>
          </div>
        )}
        <form onSubmit={handleSubmit} className="flex space-x-2">
          <input
            ref={inputRef}
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={handleInputFocus}
            onClick={handleInputClick}
            placeholder={
              inputDisabled 
                ? "Daily limit reached. Sign in for unlimited queries..." 
                : "Ask about credit cards... 💳"
            }
            className={`flex-1 input-field ${
              inputDisabled 
                ? 'bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 cursor-pointer' 
                : ''
            }`}
            disabled={isLoading || inputDisabled}
            readOnly={inputDisabled}
          />
          <button
            type="submit"
            disabled={!inputMessage.trim() || isLoading || inputDisabled}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center min-w-[44px]"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatInterface;
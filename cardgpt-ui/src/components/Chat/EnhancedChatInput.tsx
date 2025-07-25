import React, { useState, useRef } from 'react';
import { Send, Sparkles, Mic, Smile } from 'lucide-react';

interface EnhancedChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading?: boolean;
  placeholder?: string;
}

const EnhancedChatInput: React.FC<EnhancedChatInputProps> = ({
  onSendMessage,
  isLoading = false,
  placeholder = "Ask about credit cards... 💳"
}) => {
  const [message, setMessage] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !isLoading) {
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  const quickSuggestions = [
    '💰 Best cashback',
    '✈️ Travel rewards', 
    '🔥 No annual fee',
    '🎯 Compare cards'
  ];

  const handleSuggestionClick = (suggestion: string) => {
    const cleanSuggestion = suggestion.replace(/[^\w\s]/g, '').trim();
    setMessage(cleanSuggestion);
    inputRef.current?.focus();
  };

  return (
    <div className="glass-card p-4 m-4 mb-6">
      <form onSubmit={handleSubmit} className="space-y-3">
        {/* Main Input Area */}
        <div className="flex items-center space-x-3">
          <div className="flex-1 relative">
            <input
              ref={inputRef}
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder={placeholder}
              className="w-full bg-transparent text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 border-none outline-none text-lg py-2 pr-12"
              disabled={isLoading}
            />
            <div className="absolute right-3 top-1/2 transform -translate-y-1/2 flex items-center space-x-1">
              <button
                type="button"
                className="text-gray-400 hover:text-purple-500 transition-colors p-1"
                title="Voice input"
              >
                <Mic className="w-4 h-4" />
              </button>
              <button
                type="button"
                className="text-gray-400 hover:text-purple-500 transition-colors p-1"
                title="Add emoji"
              >
                <Smile className="w-4 h-4" />
              </button>
            </div>
          </div>
          
          <button
            type="submit"
            disabled={!message.trim() || isLoading}
            className="btn-primary px-6 py-3 flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <>
                <Send className="w-4 h-4" />
                <span className="font-medium">Send</span>
              </>
            )}
          </button>
        </div>
        
        {/* Quick Suggestions */}
        <div className="flex space-x-2 overflow-x-auto scrollbar-none">
          {quickSuggestions.map((suggestion, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleSuggestionClick(suggestion)}
              className="flex-shrink-0 px-4 py-2 bg-purple-500/10 hover:bg-purple-500/20 text-purple-600 dark:text-purple-400 rounded-full text-sm font-medium transition-all duration-300 hover:scale-105"
            >
              {suggestion}
            </button>
          ))}
        </div>
        
        {/* Helper Text */}
        <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
          <div className="flex items-center space-x-4">
            <span className="flex items-center">
              <Sparkles className="w-3 h-3 mr-1" />
              AI-powered
            </span>
            <span>• Free to use</span>
            <span>• Real-time answers</span>
          </div>
          <div className="hidden sm:block">
            <kbd className="px-2 py-1 bg-gray-200 dark:bg-gray-700 rounded text-xs">Enter</kbd>
            <span className="ml-1">to send</span>
          </div>
        </div>
      </form>
    </div>
  );
};

export default EnhancedChatInput;
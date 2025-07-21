import React from 'react';
import { Bot } from 'lucide-react';

const TypingIndicator: React.FC = () => {
  return (
    <div className="flex justify-start animate-fade-in">
      <div className="flex items-start space-x-3 max-w-4xl">
        {/* Avatar */}
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
          <Bot className="w-4 h-4 text-gray-600" />
        </div>
        
        {/* Typing Animation */}
        <div className="bg-white text-gray-800 rounded-lg px-4 py-3 shadow-sm border border-gray-200">
          <div className="flex items-center space-x-1">
            <div className="text-sm text-gray-500 mr-2">Assistant is typing</div>
            <div className="loading-dots">
              <div className="loading-dot" style={{ animationDelay: '0s' }}></div>
              <div className="loading-dot" style={{ animationDelay: '0.2s' }}></div>
              <div className="loading-dot" style={{ animationDelay: '0.4s' }}></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TypingIndicator;
import React, { useState } from 'react';
import { User, ChevronDown, ChevronRight, Bug } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { ChatMessage } from '../../types';
import CardSelection from './CardSelection';
import CostDisplay from './CostDisplay';
import SourcesDisplay from './SourcesDisplay';

interface MessageBubbleProps {
  message: ChatMessage;
  onCardSelection?: (selectedCards: string[], originalQuery: string) => void;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message, onCardSelection }) => {
  const [showDebugInfo, setShowDebugInfo] = useState(false);
  const isUser = message.role === 'user';
  const requiresCardSelection = message.metadata?.requires_card_selection;
  const availableCards = message.metadata?.available_cards;
  const isStreaming = message.metadata?.isStreaming || false;
  const isComplete = message.metadata?.isComplete || false;
  
  // Check if this assistant message has debug information
  const hasDebugInfo = !isUser && isComplete && (
    (message.sources && message.sources.length > 0) || 
    message.llm_usage || 
    message.total_cost !== undefined
  );
  
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} animate-fade-in`}>
      <div className={`flex items-start space-x-3 max-w-4xl ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
          isUser ? 'glow-purple' : 'glass-card'
        }`} style={isUser ? {background: 'var(--gradient-accent)'} : {}}>
          {isUser ? (
            <User className="w-5 h-5 text-white" />
          ) : (
            <span className="text-xl">🤖</span>
          )}
        </div>
        
        {/* Message Content */}
        <div className={`flex-1 ${isUser ? 'text-right' : 'text-left'}`}>
          {!isUser && requiresCardSelection && availableCards && onCardSelection ? (
            // Special card selection interface
            <div className="w-full">
              <div className="bg-white text-gray-800 shadow-sm border border-gray-200 rounded-lg p-4 mb-4">
                <div className="prose prose-sm max-w-none prose-gray">
                  <ReactMarkdown>{message.content}</ReactMarkdown>
                </div>
              </div>
              <CardSelection
                availableCards={availableCards}
                originalQuery={message.metadata?.original_query || ''}
                onSelectionComplete={onCardSelection}
              />
            </div>
          ) : (
            // Regular message bubble
            <div className={`inline-block px-4 py-3 ${
              isUser 
                ? 'message-user' 
                : 'message-assistant'
            }`}>
              {/* Message Text */}
              <div className={`prose prose-sm max-w-none ${
                isUser ? 'prose-invert' : 'prose-gray dark:prose-invert'
              }`}>
                {isUser ? (
                  // For user messages, keep simple text rendering
                  message.content.split('\n').map((line, index) => (
                    <p key={index} className={index === 0 ? 'mt-0' : ''}>
                      {line}
                    </p>
                  ))
                ) : (
                  // For assistant messages, render markdown
                  <>
                    <ReactMarkdown>{message.content}</ReactMarkdown>
                    {/* Streaming indicator */}
                    {isStreaming && (
                      <div className="flex items-center gap-1 mt-2 text-blue-500">
                        <div className="flex space-x-1">
                          <div className="w-1 h-1 bg-current rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                          <div className="w-1 h-1 bg-current rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                          <div className="w-1 h-1 bg-current rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                        </div>
                        <span className="text-xs">Generating...</span>
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          )}
          
          {/* Debug Info Section for Assistant Messages */}
          {hasDebugInfo && (
            <div className="mt-3 w-full">
              <button
                onClick={() => setShowDebugInfo(!showDebugInfo)}
                className="flex items-center gap-2 text-xs text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 transition-colors mb-2"
              >
                <Bug className="w-3 h-3" />
                Debug Info
                {showDebugInfo ? (
                  <ChevronDown className="w-3 h-3" />
                ) : (
                  <ChevronRight className="w-3 h-3" />
                )}
              </button>
              
              {showDebugInfo && (
                <div className="space-y-3">
                  {/* Cost Information */}
                  {message.llm_usage && (
                    <CostDisplay
                      llmUsage={message.llm_usage}
                      embeddingUsage={message.embedding_usage}
                      totalCost={message.total_cost || 0}
                    />
                  )}
                  
                  {/* Sources Information */}
                  {message.sources && message.sources.length > 0 && (
                    <SourcesDisplay sources={message.sources} />
                  )}
                  
                  {/* Enhanced Question (if different from original) */}
                  {message.enhanced_question && message.enhanced_question !== message.content && (
                    <div className="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg p-3">
                      <div className="text-purple-700 dark:text-purple-300 font-medium text-sm mb-1">
                        Enhanced Query
                      </div>
                      <div className="text-xs text-purple-600 dark:text-purple-400">
                        {message.enhanced_question}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
          
          {/* Timestamp */}
          <div className={`text-xs text-gray-500 mt-1 ${isUser ? 'text-right' : 'text-left'}`}>
            {message.timestamp.toLocaleTimeString([], { 
              hour: '2-digit', 
              minute: '2-digit' 
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;
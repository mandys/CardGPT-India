import React from 'react';
import { User, Bot } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { ChatMessage } from '../../types';
import CardSelection from './CardSelection';

interface MessageBubbleProps {
  message: ChatMessage;
  onCardSelection?: (selectedCards: string[], originalQuery: string) => void;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message, onCardSelection }) => {
  const isUser = message.role === 'user';
  const requiresCardSelection = message.metadata?.requires_card_selection;
  const availableCards = message.metadata?.available_cards;
  
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} animate-fade-in`}>
      <div className={`flex items-start space-x-3 max-w-4xl ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser ? 'bg-primary-600' : 'bg-gray-200'
        }`}>
          {isUser ? (
            <User className="w-4 h-4 text-white" />
          ) : (
            <Bot className="w-4 h-4 text-gray-600" />
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
            <div className={`inline-block px-4 py-2 rounded-lg ${
              isUser 
                ? 'bg-primary-600 text-white' 
                : 'bg-white text-gray-800 shadow-sm border border-gray-200'
            }`}>
              {/* Message Text */}
              <div className={`prose prose-sm max-w-none ${
                isUser ? 'prose-invert' : 'prose-gray'
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
                  <ReactMarkdown>{message.content}</ReactMarkdown>
                )}
              </div>
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
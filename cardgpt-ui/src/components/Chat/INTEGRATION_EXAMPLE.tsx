import React from 'react';
import { ChatMessage } from '../../types';
import MessageBubble from './MessageBubble';

/**
 * INTEGRATION EXAMPLE
 * 
 * This file demonstrates how the tips module integrates with your existing chat system.
 * The tips will automatically appear after assistant messages are complete.
 */

// Example of how your chat messages would look with tips
const ExampleChatMessages: React.FC = () => {
  // Example message data - this would come from your actual chat state
  const exampleMessages: ChatMessage[] = [
    {
      id: '1',
      role: 'user',
      content: 'What welcome benefits does Axis Atlas offer?',
      timestamp: new Date(),
    },
    {
      id: '2',
      role: 'assistant',
      content: `# Axis Atlas Welcome Benefits

The Axis Atlas credit card offers several attractive welcome benefits:

## 🎁 Welcome Bonus
- **25,000 bonus miles** when you spend ₹1.5 lakhs within 45 days of card approval
- This is equivalent to approximately ₹12,500 in value

## 🏨 Complimentary Hotel Nights
- 2 complimentary hotel nights at ITC Hotels
- Valid for 1 year from card approval date

## ✈️ Airport Lounge Access
- Unlimited domestic airport lounge access
- 4 international airport lounge access per year

## 🎯 Additional Benefits
- Priority Pass membership
- Travel insurance coverage up to ₹50 lakhs
- Zero foreign exchange markup fee

The welcome benefits alone can provide significant value, especially if you're planning to travel within the first year of getting the card.`,
      timestamp: new Date(),
      metadata: {
        isComplete: true,
        original_query: 'What welcome benefits does Axis Atlas offer?'
      },
      sources: [
        {
          cardName: 'Axis Atlas',
          section: 'Welcome Benefits',
          content: 'Welcome bonus details...',
          similarity: 0.95
        }
      ],
      llm_usage: {
        tokens: 450,
        cost: 0.02,
        model: 'gemini-2.5-flash-lite'
      },
      total_cost: 0.025
    }
  ];

  // Handler for when user clicks on a tip
  const handleTipClick = (tip: string) => {
    console.log('User clicked tip:', tip);
    // In your real app, this would trigger a new query
    // onSendMessage(tip);
    alert(`In your real app, this would send: "${tip}"`);
  };

  // Handler for card selection (existing functionality)
  const handleCardSelection = (selectedCards: string[], originalQuery: string) => {
    console.log('Card selection:', selectedCards, originalQuery);
  };

  return (
    <div className="space-y-4 p-4 bg-gray-50 dark:bg-gray-900 min-h-screen">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6 text-center">
          💬 Chat Integration Example
        </h2>
        
        <div className="space-y-4">
          {exampleMessages.map((message) => (
            <MessageBubble
              key={message.id}
              message={message}
              onCardSelection={handleCardSelection}
              onTipClick={handleTipClick}
            />
          ))}
        </div>

        {/* Info Box */}
        <div className="mt-8 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
          <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-3">
            🔍 What you're seeing:
          </h3>
          <ul className="text-blue-800 dark:text-blue-200 space-y-2 text-sm">
            <li>• The user asked about Axis Atlas welcome benefits</li>
            <li>• The assistant provided a comprehensive answer</li>
            <li>• After the message is complete, a contextual tip appears</li>
            <li>• The tip is from the "Welcome Benefits" category</li>
            <li>• Users can click the tip to use it as a new query</li>
            <li>• The shuffle button lets users get different tips</li>
          </ul>
        </div>

        {/* Integration Code Example */}
        <div className="mt-6 p-4 bg-gray-900 dark:bg-gray-800 rounded-lg">
          <h3 className="text-lg font-semibold text-white mb-3">
            💻 Integration Code:
          </h3>
          <pre className="text-green-400 text-sm overflow-x-auto">
{`// In your ChatInterface.tsx
<MessageBubble 
  key={message.id} 
  message={message} 
  onCardSelection={onCardSelection}
  onTipClick={onExampleClick}  // <- Add this line
/>

// The tip will automatically appear when:
// - message.role === 'assistant'
// - message.metadata?.isComplete === true
// - !message.metadata?.requires_card_selection
// - onTipClick handler is provided`}
          </pre>
        </div>
      </div>
    </div>
  );
};

export default ExampleChatMessages;
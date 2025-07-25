import React from 'react';
import { useTheme } from '../../contexts/ThemeContext';

interface DesignShowcaseProps {
  onClose: () => void;
}

const DesignShowcase: React.FC<DesignShowcaseProps> = ({ onClose }) => {
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="glass-card max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          {/* Header */}
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              🎨 CardGPT Design System Showcase
            </h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            >
              ✕
            </button>
          </div>

          {/* New Branding */}
          <div className="mb-8">
            <h3 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
              ✨ New Branding
            </h3>
            <div className="text-center p-6 glass-card">
              <div className="flex justify-center mb-4">
                <div className="w-16 h-16 rounded-2xl floating glow-purple" style={{background: 'var(--gradient-primary)'}}>
                  <span className="flex items-center justify-center h-full text-3xl">💳</span>
                </div>
              </div>
              <h4 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                CardGPT - Your Credit Card Expert
              </h4>
              <p className="text-lg text-purple-600 dark:text-purple-400 font-medium">
                Your pocket-sized credit card expert ✨
              </p>
            </div>
          </div>

          {/* Gen Z Query Examples */}
          <div className="mb-8">
            <h3 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
              🔥 Gen Z Query Examples
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {[
                '🔥 Which card is fire for travel rewards?',
                '💰 Best cashback card that won\'t break me?',
                '✈️ Atlas vs EPM - which one slaps harder?',
                '🎯 Annual fees? We don\'t do those here',
                '📱 UPI cashback cards that actually pay',
                '🏠 Rent payments with max rewards?'
              ].map((example, index) => (
                <div
                  key={index}
                  className="glass-card p-3 text-sm text-gray-700 dark:text-gray-300 hover:glow-purple transform transition-all duration-300"
                >
                  {example}
                </div>
              ))}
            </div>
          </div>

          {/* Design System Elements */}
          <div className="mb-8">
            <h3 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
              🎨 Design System Elements
            </h3>
            
            {/* Buttons */}
            <div className="mb-6">
              <h4 className="font-medium mb-3 text-gray-900 dark:text-white">Buttons</h4>
              <div className="flex flex-wrap gap-3">
                <button className="btn-primary">Primary Button</button>
                <button className="btn-secondary">Secondary Button</button>
                <button className="btn-outline">Outline Button</button>
              </div>
            </div>

            {/* Cards */}
            <div className="mb-6">
              <h4 className="font-medium mb-3 text-gray-900 dark:text-white">Cards</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="card">
                  <h5 className="font-semibold mb-2 text-gray-900 dark:text-white">Regular Card</h5>
                  <p className="text-gray-600 dark:text-gray-400 text-sm">Standard card with solid background</p>
                </div>
                <div className="glass-card p-6">
                  <h5 className="font-semibold mb-2 text-gray-900 dark:text-white">Glass Card</h5>
                  <p className="text-gray-600 dark:text-gray-400 text-sm">Modern glassmorphism effect</p>
                </div>
                <div className="glass-card p-6 glow-blue">
                  <h5 className="font-semibold mb-2 text-gray-900 dark:text-white">Glowing Card</h5>
                  <p className="text-gray-600 dark:text-gray-400 text-sm">With glow effect</p>
                </div>
              </div>
            </div>

            {/* Animations */}
            <div className="mb-6">
              <h4 className="font-medium mb-3 text-gray-900 dark:text-white">Animations</h4>
              <div className="flex space-x-4">
                <div className="w-12 h-12 bg-purple-500 rounded-xl floating"></div>
                <div className="w-12 h-12 bg-pink-500 rounded-xl glow-pink"></div>
                <div className="w-12 h-12 bg-blue-500 rounded-xl glow-blue"></div>
              </div>
            </div>
          </div>

          {/* Theme Toggle */}
          <div className="mb-6">
            <h3 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
              🌓 Theme System
            </h3>
            <div className="flex items-center justify-between glass-card p-4">
              <span className="text-gray-900 dark:text-white">
                Current theme: <strong>{theme}</strong>
              </span>
              <button
                onClick={toggleTheme}
                className="btn-primary"
              >
                Switch to {theme === 'light' ? 'Dark' : 'Light'} Mode
              </button>
            </div>
          </div>

          {/* Implementation Status */}
          <div className="mb-6">
            <h3 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
              ✅ Implementation Status
            </h3>
            <div className="space-y-2">
              {[
                { phase: 'Phase 1: Quick Wins', status: 'completed', items: ['New branding ✨', 'Gen Z suggestions 🔥', 'Gradient headers 🎨', 'Emoji integration 💳'] },
                { phase: 'Phase 2: Core UX', status: 'completed', items: ['Glassmorphism effects 🪄', 'Modern animations ⚡', 'Mobile header redesign 📱', 'Enhanced chat bubbles 💬'] },
                { phase: 'Phase 3: Polish', status: 'in-progress', items: ['Responsive improvements 📐', 'Micro-interactions ✨', 'Performance optimization ⚡', 'A11y enhancements ♿'] }
              ].map((phase, index) => (
                <div key={index} className="glass-card p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-gray-900 dark:text-white">{phase.phase}</h4>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      phase.status === 'completed' ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400' :
                      phase.status === 'in-progress' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400' :
                      'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                    }`}>
                      {phase.status === 'completed' ? '✅ Complete' : 
                       phase.status === 'in-progress' ? '🔄 In Progress' : '⏳ Pending'}
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {phase.items.map((item, itemIndex) => (
                      <span key={itemIndex} className="text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 px-2 py-1 rounded">
                        {item}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Close Button */}
          <div className="text-center">
            <button
              onClick={onClose}
              className="btn-primary px-8 py-3"
            >
              Close Showcase
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DesignShowcase;
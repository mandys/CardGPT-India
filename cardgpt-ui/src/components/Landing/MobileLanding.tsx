import React from 'react';
import { ArrowRight, Shield, Zap, Heart } from 'lucide-react';

interface MobileLandingProps {
  onGetStarted: () => void;
}

const MobileLanding: React.FC<MobileLandingProps> = ({ onGetStarted }) => {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Hero Section */}
      <div className="header-gradient text-white relative overflow-hidden">
        {/* Background Effects */}
        <div className="absolute inset-0 opacity-20">
          <div className="absolute top-10 right-4 w-20 h-20 bg-white/10 rounded-full blur-2xl animate-pulse" />
          <div className="absolute bottom-20 left-4 w-24 h-24 bg-white/10 rounded-full blur-2xl animate-pulse delay-1000" />
          <div className="absolute top-1/2 right-8 w-16 h-16 bg-white/10 rounded-full blur-xl animate-pulse delay-500" />
        </div>
        
        <div className="relative px-6 py-12 text-center">
          {/* Logo */}
          <div className="flex justify-center mb-6">
            <div className="w-20 h-20 bg-white/20 backdrop-blur-sm rounded-3xl flex items-center justify-center floating glow-blue">
              <span className="text-4xl">💳</span>
            </div>
          </div>
          
          {/* Main Headline */}
          <h1 className="text-3xl font-bold mb-4 leading-tight">
            CardGPT
            <br />
            <span className="text-2xl font-semibold text-white/90">
              Your Credit Card Expert
            </span>
          </h1>
          
          {/* Tagline */}
          <p className="text-lg text-white/80 mb-8 leading-relaxed">
            Your pocket-sized credit card expert 💳✨
            <br />
            <span className="text-base">Get instant, personalized insights on Indian credit cards</span>
          </p>
          
          {/* CTA Button */}
          <button
            onClick={onGetStarted}
            className="btn-primary text-lg px-8 py-4 mb-8 inline-flex items-center space-x-2 glow-purple"
          >
            <span>Start Chatting</span>
            <ArrowRight className="w-5 h-5" />
          </button>
          
          {/* Quick Stats */}
          <div className="flex justify-center space-x-6 text-sm text-white/70">
            <div className="text-center">
              <div className="font-bold text-white">Free</div>
              <div>Always</div>
            </div>
            <div className="text-center">
              <div className="font-bold text-white">Instant</div>
              <div>Answers</div>
            </div>
            <div className="text-center">
              <div className="font-bold text-white">Smart</div>
              <div>AI</div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Features Section */}
      <div className="px-6 py-12 space-y-6">
        <h2 className="text-2xl font-bold text-center text-gray-900 dark:text-white mb-8">
          Why CardGPT? 🤔
        </h2>
        
        <div className="space-y-4">
          <div className="glass-card p-6 hover:glow-blue">
            <div className="flex items-start space-x-4">
              <div className="w-12 h-12 bg-blue-500/20 rounded-xl flex items-center justify-center">
                <Zap className="w-6 h-6 text-blue-500" />
              </div>
              <div>
                <h3 className="font-bold text-gray-900 dark:text-white mb-2">
                  Lightning Fast ⚡
                </h3>
                <p className="text-gray-600 dark:text-gray-400 text-sm leading-relaxed">
                  Get instant answers about credit card rewards, fees, and benefits. No more scrolling through endless T&Cs.
                </p>
              </div>
            </div>
          </div>
          
          <div className="glass-card p-6 hover:glow-purple">
            <div className="flex items-start space-x-4">
              <div className="w-12 h-12 bg-purple-500/20 rounded-xl flex items-center justify-center">
                <Shield className="w-6 h-6 text-purple-500" />
              </div>
              <div>
                <h3 className="font-bold text-gray-900 dark:text-white mb-2">
                  100% Reliable 🛡️
                </h3>
                <p className="text-gray-600 dark:text-gray-400 text-sm leading-relaxed">
                  Powered by official credit card terms and conditions. Always accurate, always up-to-date.
                </p>
              </div>
            </div>
          </div>
          
          <div className="glass-card p-6 hover:glow-pink">
            <div className="flex items-start space-x-4">
              <div className="w-12 h-12 bg-pink-500/20 rounded-xl flex items-center justify-center">
                <Heart className="w-6 h-6 text-pink-500" />
              </div>
              <div>
                <h3 className="font-bold text-gray-900 dark:text-white mb-2">
                  Made for India 🇮🇳
                </h3>
                <p className="text-gray-600 dark:text-gray-400 text-sm leading-relaxed">
                  Specialized in Indian credit cards - Atlas, EPM, HSBC Premier, and more. We speak your language.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Supported Cards */}
      <div className="px-6 py-8 bg-white dark:bg-gray-800">
        <h3 className="text-xl font-bold text-center text-gray-900 dark:text-white mb-6">
          Supported Premium Cards 💎
        </h3>
        
        <div className="grid grid-cols-1 gap-3">
          {[
            { name: 'Axis Bank Atlas', color: 'from-red-500 to-red-600' },
            { name: 'ICICI Emeralde', color: 'from-green-500 to-green-600' },
            { name: 'HSBC Premier', color: 'from-blue-500 to-blue-600' }
          ].map((card, idx) => (
            <div key={idx} className={`bg-gradient-to-r ${card.color} rounded-xl p-4 text-white text-center font-semibold shadow-lg`}>
              {card.name}
            </div>
          ))}
        </div>
      </div>
      
      {/* Final CTA */}
      <div className="px-6 py-12 text-center">
        <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
          Ready to make smarter decisions? 🧠
        </h3>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Join thousands of users who trust CardGPT for their credit card insights
        </p>
        <button
          onClick={onGetStarted}
          className="btn-primary text-lg px-8 py-4 inline-flex items-center space-x-2"
        >
          <span>Get Started Now</span>
          <ArrowRight className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
};

export default MobileLanding;
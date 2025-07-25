import React from 'react';
import { ArrowRight, Star, Shield, Zap, TrendingUp } from 'lucide-react';

interface DesktopHeroProps {
  onGetStarted: () => void;
  onViewSamples: () => void;
}

const DesktopHero: React.FC<DesktopHeroProps> = ({ onGetStarted, onViewSamples }) => {
  return (
    <div className="bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 min-h-screen relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0">
        <div className="absolute top-20 left-20 w-72 h-72 bg-purple-500/20 rounded-full blur-3xl animate-pulse floating" />
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-pulse delay-1000 floating" />
        <div className="absolute top-1/3 right-1/4 w-48 h-48 bg-pink-500/20 rounded-full blur-2xl animate-pulse delay-500 floating" />
      </div>
      
      <div className="relative z-10 container mx-auto px-6 pt-20">
        <div className="text-center max-w-6xl mx-auto">
          {/* Badge */}
          <div className="inline-flex items-center px-6 py-3 bg-purple-500/20 backdrop-blur-sm rounded-full border border-purple-300/20 mb-8 glow-purple">
            <span className="text-purple-300 text-lg font-medium flex items-center">
              <span className="text-2xl mr-2">🤖</span>
              Powered by Advanced AI
            </span>
          </div>
          
          {/* Main headline */}
          <h1 className="text-6xl md:text-8xl font-bold mb-8 leading-tight">
            <span className="text-white">CardGPT</span>
            <br />
            <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400 bg-clip-text text-transparent">
              Your Credit Card
            </span>
            <br />
            <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              Expert
            </span>
          </h1>
          
          {/* Subheadline with Gen Z vibes */}
          <p className="text-2xl text-slate-300 mb-10 leading-relaxed max-w-4xl mx-auto">
            Your pocket-sized credit card expert 💳✨
            <br />
            <span className="text-xl text-slate-400 mt-2 block">
              Get instant, personalized insights on Indian credit cards. 
              <span className="text-purple-300 font-semibold"> No more boring spreadsheets</span> or 
              confusing fine print. <span className="text-pink-300">It's giving financial clarity ✨</span>
            </span>
          </p>
          
          {/* CTA buttons */}
          <div className="flex flex-col sm:flex-row gap-6 justify-center items-center mb-16">
            <button 
              onClick={onGetStarted}
              className="group btn-primary text-xl px-10 py-5 glow-purple"
            >
              <span className="flex items-center">
                <span className="text-2xl mr-3">💳</span>
                Launch CardGPT
                <ArrowRight className="ml-3 w-6 h-6 group-hover:translate-x-1 transition-transform" />
              </span>
            </button>
            
            <button 
              onClick={onViewSamples}
              className="text-slate-300 hover:text-white px-8 py-5 rounded-xl font-medium border border-slate-700 hover:border-slate-600 transition-all duration-300 text-lg"
            >
              🎯 View Sample Queries
            </button>
          </div>
          
          {/* Feature highlights */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-16">
            {[
              { icon: Zap, label: "Lightning Fast", desc: "Instant answers" },
              { icon: Shield, label: "100% Reliable", desc: "Official data" },
              { icon: Star, label: "Premium Cards", desc: "Atlas, EPM, HSBC" },
              { icon: TrendingUp, label: "Smart Analysis", desc: "AI-powered insights" }
            ].map((feature, idx) => (
              <div key={idx} className="glass-card p-6 text-center hover:glow-blue group">
                <feature.icon className="w-8 h-8 mx-auto mb-3 text-purple-400 group-hover:text-blue-400 transition-colors" />
                <h3 className="font-semibold text-white mb-1">{feature.label}</h3>
                <p className="text-sm text-slate-400">{feature.desc}</p>
              </div>
            ))}
          </div>
          
          {/* Social proof */}
          <div className="flex items-center justify-center space-x-12 text-slate-400 text-lg">
            <div className="flex items-center">
              <div className="w-3 h-3 bg-green-400 rounded-full mr-3 animate-pulse" />
              Real-time insights
            </div>
            <div className="flex items-center">
              <span className="text-2xl mr-2">✨</span>
              100% Free
            </div>
            <div className="flex items-center">
              <span className="text-2xl mr-2">🔒</span>
              Privacy-first
            </div>
            <div className="flex items-center">
              <span className="text-2xl mr-2">⚡</span>
              Lightning fast
            </div>
          </div>
        </div>
      </div>
      
      {/* Bottom section with supported cards */}
      <div className="relative z-10 py-20 mt-20">
        <div className="container mx-auto px-6 text-center">
          <h2 className="text-4xl font-bold text-white mb-4">
            Supported Premium Cards 💎
          </h2>
          <p className="text-xl text-slate-300 mb-12">
            Get AI-powered insights on India's most exclusive credit cards
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            {[
              { 
                name: 'Axis Bank Atlas', 
                gradient: 'from-red-500 to-red-600',
                features: ['10X Miles', 'Priority Pass', '₹1.5L Milestone']
              },
              { 
                name: 'ICICI Emeralde', 
                gradient: 'from-green-500 to-green-600',
                features: ['6 Points/₹200', 'Category Caps', 'Luxury Benefits']
              },
              { 
                name: 'HSBC Premier', 
                gradient: 'from-blue-500 to-blue-600',
                features: ['Miles Transfer', 'Travel Benefits', 'Global Access']
              }
            ].map((card, idx) => (
              <div key={idx} className={`bg-gradient-to-br ${card.gradient} rounded-2xl p-8 text-white shadow-2xl transform hover:scale-105 transition-all duration-300`}>
                <h3 className="text-2xl font-bold mb-4">{card.name}</h3>
                <ul className="space-y-2">
                  {card.features.map((feature, featureIdx) => (
                    <li key={featureIdx} className="flex items-center">
                      <span className="text-lg mr-2">✓</span>
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DesktopHero;
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useTheme } from '../../contexts/ThemeContext';
import { 
  Brain, 
  Calculator, 
  Users, 
  Sun, 
  Moon,
  ArrowRight,
  Zap,
  Sparkles,
  MessageSquare
} from 'lucide-react';

const LandingPage: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const isDarkMode = theme === 'dark';

  const handleLaunchCardGPT = () => {
    navigate('/chat');
  };

  const handleTryQuery = (query: string) => {
    navigate('/chat', { state: { prefilledQuery: query } });
  };

  const supportedCards = [
    {
      name: 'Axis Bank Atlas',
      shortName: 'Atlas',
      bank: 'Axis Bank',
      image: '/images/axis-atlas-card.jpg',
      features: ['5X EDGE Miles on Travel', 'Unlimited Lounge Access', '2,500 Welcome Miles'],
      welcomeBonus: '2,500 EDGE Miles',
      annualFee: '₹5,000 + GST',
      bgGradient: 'from-slate-900 to-slate-800',
      badge: 'Travel Focused',
      badgeColor: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
      network: 'VISA',
      networkBg: 'from-yellow-400 to-yellow-500',
      networkText: 'text-slate-900',
      query: 'Tell me about Axis Atlas benefits and milestone rewards'
    },
    {
      name: 'HSBC Premier',
      shortName: 'Premier',
      bank: 'HSBC',
      image: '/images/hsbc-premier-card.jpg', 
      features: ['3X Points on All Spends', '0.99% Foreign Currency Markup', '₹12,000 Taj Voucher'],
      welcomeBonus: '₹12,000 Taj Voucher + Memberships',
      annualFee: '₹20,000 (Waived)',
      bgGradient: 'from-red-900 to-red-800',
      badge: 'Global Banking',
      badgeColor: 'bg-red-500/20 text-red-300 border-red-500/30',
      network: 'MC',
      networkBg: 'from-red-500 to-orange-500',
      networkText: 'text-white',
      query: 'Compare HSBC Premier global benefits and forex rates'
    },
    {
      name: 'ICICI Emeralde',
      shortName: 'Emeralde',
      bank: 'ICICI Bank',
      image: '/images/icici-epm-card.jpg',
      features: ['6 Points per ₹200 (3% Return)', 'Unlimited Golf Games', '12,500 Points + Memberships'],
      welcomeBonus: '12,500 Points + Memberships',
      annualFee: '₹12,499 (Free 1st year)',
      bgGradient: 'from-emerald-900 to-teal-800',
      badge: 'Metal Card',
      badgeColor: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
      network: 'VISA',
      networkBg: 'from-yellow-400 to-yellow-500',
      networkText: 'text-slate-900',
      query: 'Calculate ICICI EPM metal card rewards and insurance benefits'
    }
  ];

  const quickFeatures = [
    {
      icon: Brain,
      title: 'AI-Powered Insights',
      description: 'Understand complex terms instantly',
      bgGradient: 'from-violet-100 to-indigo-100',
      iconColor: 'text-violet-600'
    },
    {
      icon: Calculator,
      title: 'Reward Calculator',
      description: 'Calculate miles, points & cashback',
      bgGradient: 'from-emerald-100 to-teal-100',
      iconColor: 'text-emerald-600'
    },
    {
      icon: Zap,
      title: 'Smart Comparisons',
      description: 'Personalized recommendations',
      bgGradient: 'from-orange-100 to-red-100',
      iconColor: 'text-orange-600'
    },
    {
      icon: Users,
      title: 'Premium Focus',
      description: 'Top-tier cards analyzed',
      bgGradient: 'from-blue-100 to-cyan-100',
      iconColor: 'text-blue-600'
    }
  ];

  const sampleQueries = [
    "Compare Axis Atlas vs HSBC Premier for ₹2L annual spend",
    "What are the best cards for travel rewards?",
    "Calculate cashback on ₹50K monthly expenses",
    "Which card has the lowest annual fees?"
  ];

  return (
    <div className={`min-h-screen transition-colors duration-300 ${
      isDarkMode 
        ? 'bg-gray-900 text-white' 
        : 'bg-gradient-to-br from-slate-50 via-white to-slate-100'
    }`}>
      {/* Header */}
      <header className={`sticky top-0 z-50 backdrop-blur-xl border-b transition-colors duration-300 ${
        isDarkMode 
          ? 'bg-gray-900/80 border-gray-700/50' 
          : 'bg-white/80 border-slate-200/50'
      }`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-2">
              {/* Custom CardGPT Logo */}
              <div className="flex items-center">
                <div className="w-8 h-8 bg-gradient-to-br from-violet-600 to-indigo-600 rounded-lg flex items-center justify-center mr-2 shadow-sm">
                  <div className="relative">
                    {/* Chat bubble icon */}
                    <div className="w-5 h-4 bg-white rounded-sm relative">
                      <div className="absolute bottom-0 left-1 w-1 h-1 bg-white transform rotate-45 translate-y-0.5 -translate-x-0.5"></div>
                    </div>
                    {/* Sparkle accent */}
                    <div className="absolute -top-0.5 -right-0.5 w-2 h-2">
                      <Sparkles className="w-2 h-2 text-yellow-300" />
                    </div>
                  </div>
                </div>
                <span className={`text-xl font-bold tracking-tight ${
                  isDarkMode ? 'text-white' : 'text-slate-900'
                }`}>
                  Card<span className="bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent">GPT</span>
                </span>
              </div>
            </div>
            
            <nav className="hidden md:flex items-center space-x-8">
              <a 
                href="#features" 
                className={`text-sm font-medium transition-colors ${
                  isDarkMode 
                    ? 'text-gray-400 hover:text-white' 
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Features
              </a>
              <a 
                href="#cards" 
                className={`text-sm font-medium transition-colors ${
                  isDarkMode 
                    ? 'text-gray-400 hover:text-white' 
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Cards
              </a>
              <a 
                href="#about" 
                className={`text-sm font-medium transition-colors ${
                  isDarkMode 
                    ? 'text-gray-400 hover:text-white' 
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                About
              </a>
              <button 
                onClick={toggleTheme}
                className={`p-2 rounded-lg transition-colors ${
                  isDarkMode 
                    ? 'hover:bg-gray-800 text-gray-400 hover:text-white' 
                    : 'hover:bg-slate-100 text-slate-600 hover:text-slate-900'
                }`}
                title={isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'}
              >
                {isDarkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
              </button>
              <button
                onClick={handleLaunchCardGPT}
                className="px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700 rounded-lg transition-all duration-200"
              >
                Launch CardGPT
              </button>
            </nav>
            
            <button 
              onClick={toggleTheme}
              className={`md:hidden p-2 rounded-lg transition-colors ${
                isDarkMode 
                  ? 'hover:bg-gray-800' 
                  : 'hover:bg-slate-100'
              }`}
            >
              {isDarkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
            </button>
          </div>
        </div>
      </header>

      {/* Hero Section - Compact */}
      <section className="relative pt-4 sm:pt-8 pb-0">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-4xl mx-auto">
            <div className={`inline-flex items-center space-x-2 px-3 py-1 rounded-full text-sm font-medium mb-4 ${
              isDarkMode 
                ? 'bg-violet-900/50 text-violet-300 border border-violet-700/50' 
                : 'bg-violet-100 text-violet-700 border border-violet-200'
            }`}>
              <Sparkles className="w-3 h-3" />
              <span>Powered by Advanced AI</span>
            </div>
            
            <h1 className={`text-4xl sm:text-5xl lg:text-6xl font-bold mb-4 leading-tight ${
              isDarkMode ? 'text-white' : 'text-slate-900'
            }`}>
              India's Smartest
              <span className="bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent">
                {" "}Credit Card
              </span>
              <br />
              Assistant
            </h1>
            
            <p className={`text-lg mb-8 max-w-2xl mx-auto leading-relaxed ${
              isDarkMode ? 'text-gray-400' : 'text-slate-600'
            }`}>
              Compare cards, calculate rewards, and understand fine print — all powered by AI. Make smarter financial
              decisions with instant, personalized insights.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
              <button
                onClick={handleLaunchCardGPT}
                className="inline-flex items-center px-8 py-3 text-lg font-medium text-white bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700 rounded-xl shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-105"
              >
                <MessageSquare className="w-5 h-5 mr-2" />
                Launch CardGPT
                <ArrowRight className="w-5 h-5 ml-2" />
              </button>
              
              <button
                onClick={() => document.getElementById('sample-queries')?.scrollIntoView({ behavior: 'smooth' })}
                className={`px-8 py-3 text-lg font-medium rounded-xl border transition-all duration-200 ${
                  isDarkMode 
                    ? 'border-gray-600 text-gray-300 hover:bg-gray-800 hover:border-gray-500'
                    : 'border-slate-300 text-slate-700 hover:bg-slate-50 hover:border-slate-400 bg-transparent'
                }`}
              >
                View Sample Queries
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Quick Features - Above the fold */}
      <section id="features" className={`pt-0 pb-12 ${isDarkMode ? 'bg-gray-800/30' : 'bg-white/50'}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {quickFeatures.map((feature, index) => (
              <div key={index} className="text-center">
                <div className={`w-12 h-12 bg-gradient-to-br ${
                  isDarkMode ? 'from-gray-700 to-gray-600' : feature.bgGradient
                } rounded-xl flex items-center justify-center mx-auto mb-3`}>
                  <feature.icon className={`w-6 h-6 ${
                    isDarkMode ? 'text-gray-300' : feature.iconColor
                  }`} />
                </div>
                <h3 className={`font-semibold mb-1 ${
                  isDarkMode ? 'text-white' : 'text-slate-900'
                }`}>
                  {feature.title}
                </h3>
                <p className={`text-sm ${
                  isDarkMode ? 'text-gray-400' : 'text-slate-600'
                }`}>
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Supported Cards - Compact */}
      <section id="cards" className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className={`text-3xl font-bold mb-3 ${
              isDarkMode ? 'text-white' : 'text-slate-900'
            }`}>
              Supported Premium Cards
            </h2>
            <p className={`max-w-2xl mx-auto ${
              isDarkMode ? 'text-gray-400' : 'text-slate-600'
            }`}>
              Get AI-powered insights on India's most exclusive credit cards
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {supportedCards.map((card, index) => (
              <div 
                key={index} 
                className={`overflow-hidden rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 bg-gradient-to-br ${card.bgGradient}`}
              >
                <div className="p-6">
                  {/* Card Header */}
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h3 className="text-xl font-bold text-white mb-1">
                        {card.name}
                      </h3>
                      <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${card.badgeColor}`}>
                        {card.badge}
                      </div>
                    </div>
                    <div className={`w-12 h-8 bg-gradient-to-r ${card.networkBg} rounded flex items-center justify-center`}>
                      <span className={`text-xs font-bold ${card.networkText}`}>
                        {card.network}
                      </span>
                    </div>
                  </div>

                  {/* Card Image */}
                  <div className="h-32 rounded-xl mb-4 overflow-hidden bg-white/10">
                    <img 
                      src={card.image} 
                      alt={`${card.name} Credit Card`}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        const target = e.target as HTMLImageElement;
                        target.style.display = 'none';
                        const parent = target.parentElement;
                        if (parent) {
                          parent.classList.add('flex', 'items-center', 'justify-center');
                          parent.innerHTML = `
                            <div class="text-center text-white/80">
                              <svg class="h-8 w-8 mx-auto mb-1" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M20 4H4c-1.11 0-1.99.89-1.99 2L2 18c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V6c0-1.11-.89-2-2-2zm0 14H4v-6h16v6zm0-10H4V6h16v2z"/>
                              </svg>
                              <p class="text-xs font-medium">${card.shortName}</p>
                            </div>
                          `;
                        }
                      }}
                    />
                  </div>

                  {/* Features */}
                  <div className="space-y-2 mb-6 text-sm">
                    {card.features.map((feature, featureIndex) => (
                      <div key={featureIndex} className="flex items-center text-slate-300">
                        <div className="w-1.5 h-1.5 bg-violet-400 rounded-full mr-2 flex-shrink-0"></div>
                        <span>{feature}</span>
                      </div>
                    ))}
                  </div>

                  {/* Annual Fee */}
                  <div className="flex justify-between items-center mb-4 text-sm">
                    <span className="text-slate-400">Annual Fee:</span>
                    <span className="text-white font-semibold">{card.annualFee}</span>
                  </div>

                  {/* CTA Button */}
                  <button
                    onClick={() => handleTryQuery(card.query)}
                    className="w-full inline-flex items-center justify-center px-4 py-3 bg-violet-600 hover:bg-violet-700 text-white font-medium rounded-xl transition-all duration-200"
                  >
                    <span>Analyze This Card</span>
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Sample Queries - Compact */}
      <section id="sample-queries" className={`py-16 ${isDarkMode ? 'bg-gray-800/30' : 'bg-slate-50'}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className={`text-3xl font-bold mb-3 ${isDarkMode ? 'text-white' : 'text-slate-900'}`}>
              Try These Sample Queries
            </h2>
            <p className={isDarkMode ? 'text-gray-400' : 'text-slate-600'}>
              See CardGPT in action with these popular questions
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-4xl mx-auto">
            {sampleQueries.map((query, index) => (
              <div 
                key={index} 
                onClick={() => handleTryQuery(query)}
                className={`p-4 rounded-lg border cursor-pointer transition-all duration-200 hover:shadow-md ${
                  isDarkMode
                    ? 'bg-gray-800/60 border-gray-700 hover:border-violet-500/50 hover:bg-gray-700/80'
                    : 'bg-white border-slate-200 hover:border-violet-300 hover:bg-slate-50'
                }`}
              >
                <div className="flex items-start space-x-3">
                  <ArrowRight className={`w-5 h-5 mt-0.5 flex-shrink-0 ${
                    isDarkMode ? 'text-violet-400' : 'text-violet-600'
                  }`} />
                  <p className={`font-medium ${
                    isDarkMode ? 'text-gray-200' : 'text-slate-700'
                  }`}>
                    "{query}"
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Team Section - Compact */}
      <section id="about" className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className={`text-3xl font-bold mb-3 ${isDarkMode ? 'text-white' : 'text-slate-900'}`}>
              Built by Passionate Engineers
            </h2>
            <p className={`max-w-3xl mx-auto ${isDarkMode ? 'text-gray-400' : 'text-slate-600'}`}>
              We're experimenting with RAG and LLM technology to make financial decisions easier for Indian consumers
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <div className={`p-6 text-center rounded-2xl border transition-all duration-200 ${
              isDarkMode 
                ? 'bg-gray-800/50 border-gray-700/50 hover:bg-gray-800/80' 
                : 'bg-white border-slate-200 hover:shadow-md'
            }`}>
              <div className="w-16 h-16 bg-gradient-to-br from-violet-600 to-indigo-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-white font-bold text-xl">M</span>
              </div>
              <h3 className={`text-xl font-semibold mb-2 ${isDarkMode ? 'text-white' : 'text-slate-900'}`}>
                @maharajamandy
              </h3>
              <p className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-slate-600'}`}>
                Full-stack developer specializing in AI/ML integration and backend architecture
              </p>
            </div>

            <div className={`p-6 text-center rounded-2xl border transition-all duration-200 ${
              isDarkMode 
                ? 'bg-gray-800/50 border-gray-700/50 hover:bg-gray-800/80' 
                : 'bg-white border-slate-200 hover:shadow-md'
            }`}>
              <div className="w-16 h-16 bg-gradient-to-br from-teal-600 to-cyan-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-white font-bold text-xl">A</span>
              </div>
              <h3 className={`text-xl font-semibold mb-2 ${isDarkMode ? 'text-white' : 'text-slate-900'}`}>
                @jockaayush
              </h3>
              <p className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-slate-600'}`}>
                Frontend expert with a passion for creating intuitive user experiences
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer - Minimal */}
      <footer className={`py-8 border-t transition-colors duration-300 ${
        isDarkMode 
          ? 'bg-gray-900 border-gray-700/50' 
          : 'bg-white border-slate-200'
      }`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-2 mb-4 md:mb-0">
              {/* Footer Custom Logo */}
              <div className="flex items-center">
                <div className="w-7 h-7 bg-gradient-to-br from-violet-600 to-indigo-600 rounded-lg flex items-center justify-center mr-2 shadow-sm">
                  <div className="relative">
                    {/* Chat bubble icon */}
                    <div className="w-4 h-3 bg-white rounded-sm relative">
                      <div className="absolute bottom-0 left-1 w-0.5 h-0.5 bg-white transform rotate-45 translate-y-0.5 -translate-x-0.5"></div>
                    </div>
                    {/* Sparkle accent */}
                    <div className="absolute -top-0.5 -right-0.5 w-1.5 h-1.5">
                      <Sparkles className="w-1.5 h-1.5 text-yellow-300" />
                    </div>
                  </div>
                </div>
                <span className={`text-lg font-bold tracking-tight ${
                  isDarkMode ? 'text-white' : 'text-slate-900'
                }`}>
                  Card<span className="bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent">GPT</span>
                </span>
              </div>
            </div>
            
            <nav className={`flex items-center space-x-6 text-sm ${
              isDarkMode ? 'text-gray-400' : 'text-slate-600'
            }`}>
              <button 
                onClick={() => navigate('/')}
                className={`transition-colors ${
                  isDarkMode ? 'hover:text-white' : 'hover:text-slate-900'
                }`}
              >
                Home
              </button>
              <button 
                onClick={() => navigate('/privacy')}
                className={`transition-colors ${
                  isDarkMode ? 'hover:text-white' : 'hover:text-slate-900'
                }`}
              >
                Privacy Policy
              </button>
              <button 
                onClick={() => document.getElementById('about')?.scrollIntoView({ behavior: 'smooth' })}
                className={`transition-colors ${
                  isDarkMode ? 'hover:text-white' : 'hover:text-slate-900'
                }`}
              >
                About
              </button>
            </nav>
          </div>
          
          <div className={`text-center pt-4 mt-4 border-t text-xs ${
            isDarkMode ? 'border-gray-800 text-gray-500' : 'border-slate-100 text-slate-400'
          }`}>
            © 2025 CardGPT India. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
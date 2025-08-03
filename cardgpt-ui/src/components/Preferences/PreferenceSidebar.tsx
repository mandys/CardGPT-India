import React, { useState } from 'react';
import { 
  X, 
  Settings, 
  Plane, 
  IndianRupee, 
  CreditCard, 
  ShoppingBag, 
  Trash2,
  Save,
  RotateCcw,
  User,
  CheckCircle,
  Circle,
  Plus
} from 'lucide-react';
import { usePreferences } from '../../hooks/usePreferences';
import { UserPreferences } from '../../types';

interface PreferenceSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  className?: string;
}

const PreferenceSidebar: React.FC<PreferenceSidebarProps> = ({
  isOpen,
  onClose,
  className = ''
}) => {
  const {
    preferences,
    isLoading,
    error,
    completion,
    updatePreferences,
    clearPreferences,
    loadPreferences,
    completionPercentage,
    isFullyComplete
  } = usePreferences();

  const [localPreferences, setLocalPreferences] = useState<Partial<UserPreferences>>(preferences || {});
  const [hasChanges, setHasChanges] = useState(false);
  const [newCard, setNewCard] = useState('');
  const [newBank, setNewBank] = useState('');

  // Update local state when preferences change
  React.useEffect(() => {
    if (preferences) {
      setLocalPreferences(preferences);
      setHasChanges(false);
    }
  }, [preferences]);

  const handleLocalChange = (key: keyof UserPreferences, value: any) => {
    setLocalPreferences(prev => ({ ...prev, [key]: value }));
    setHasChanges(true);
  };

  const handleSave = async () => {
    try {
      await updatePreferences(localPreferences);
      setHasChanges(false);
    } catch (error) {
      console.error('Failed to save preferences:', error);
    }
  };

  const handleReset = () => {
    setLocalPreferences(preferences || {});
    setHasChanges(false);
  };

  const handleClear = async () => {
    if (window.confirm('Are you sure you want to clear all preferences? This cannot be undone.')) {
      try {
        await clearPreferences();
        setLocalPreferences({});
        setHasChanges(false);
      } catch (error) {
        console.error('Failed to clear preferences:', error);
      }
    }
  };

  const addCard = () => {
    if (newCard.trim()) {
      const currentCards = localPreferences.current_cards || [];
      if (!currentCards.includes(newCard.trim())) {
        handleLocalChange('current_cards', [...currentCards, newCard.trim()]);
        setNewCard('');
      }
    }
  };

  const removeCard = (cardToRemove: string) => {
    const currentCards = localPreferences.current_cards || [];
    handleLocalChange('current_cards', currentCards.filter(card => card !== cardToRemove));
  };

  const addBank = () => {
    if (newBank.trim()) {
      const currentBanks = localPreferences.preferred_banks || [];
      if (!currentBanks.includes(newBank.trim())) {
        handleLocalChange('preferred_banks', [...currentBanks, newBank.trim()]);
        setNewBank('');
      }
    }
  };

  const removeBank = (bankToRemove: string) => {
    const currentBanks = localPreferences.preferred_banks || [];
    handleLocalChange('preferred_banks', currentBanks.filter(bank => bank !== bankToRemove));
  };

  const toggleSpendCategory = (category: string) => {
    const currentCategories = localPreferences.spend_categories || [];
    const newCategories = currentCategories.includes(category)
      ? currentCategories.filter(cat => cat !== category)
      : [...currentCategories, category];
    handleLocalChange('spend_categories', newCategories);
  };

  const spendingCategories = [
    { value: 'travel', label: '✈️ Travel', desc: 'Flights, hotels, bookings' },
    { value: 'dining', label: '🍽️ Dining', desc: 'Restaurants, food delivery' },
    { value: 'online_shopping', label: '🛒 Online Shopping', desc: 'E-commerce, digital purchases' },
    { value: 'fuel', label: '⛽ Fuel', desc: 'Petrol, CNG, electric charging' },
    { value: 'groceries', label: '🛍️ Groceries', desc: 'Supermarkets, daily essentials' },
    { value: 'utilities', label: '💡 Utilities', desc: 'Bills, recharges, subscriptions' },
    { value: 'entertainment', label: '🎬 Entertainment', desc: 'Movies, streaming, events' },
    { value: 'education', label: '📚 Education', desc: 'Courses, books, training' }
  ];

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 z-40"
        onClick={onClose}
      />
      
      {/* Sidebar */}
      <div className={`fixed right-0 top-0 h-full w-full max-w-md bg-white dark:bg-gray-800 shadow-xl z-50 overflow-hidden ${className}`}>
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
              <Settings className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                My Preferences
              </h2>
              <div className="flex items-center space-x-2 text-sm">
                <div className="flex items-center space-x-1">
                  {isFullyComplete ? (
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  ) : (
                    <Circle className="w-4 h-4 text-gray-400" />
                  )}
                  <span className="text-gray-600 dark:text-gray-400">
                    {completionPercentage}% complete
                  </span>
                </div>
              </div>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500 dark:text-gray-400" />
          </button>
        </div>

        {/* Progress Bar */}
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mb-2">
            <span>Travel</span>
            <span>Financial</span>
            <span>Cards</span>
            <span>Spending</span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${completionPercentage}%` }}
            />
          </div>
          <div className="flex justify-between text-xs mt-2">
            {Object.entries(completion.categories).map(([key, completed]) => (
              <span key={key} className={completed ? 'text-green-500' : 'text-gray-400'}>
                {completed ? '✅' : '⭕'}
              </span>
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-6">
          {/* Error Display */}
          {error && (
            <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-lg">
              <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
            </div>
          )}

          {/* Travel Preferences */}
          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              <Plane className="w-4 h-4 text-blue-500" />
              <h3 className="font-medium text-gray-900 dark:text-white">Travel Preferences</h3>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Travel Type
              </label>
              <select
                value={localPreferences.travel_type || ''}
                onChange={(e) => handleLocalChange('travel_type', e.target.value || null)}
                className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-sm"
              >
                <option value="">Select travel type</option>
                <option value="domestic">🇮🇳 Domestic (within India)</option>
                <option value="international">🌍 International</option>
                <option value="both">✈️ Both domestic & international</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Lounge Access
              </label>
              <select
                value={localPreferences.lounge_access || ''}
                onChange={(e) => handleLocalChange('lounge_access', e.target.value || null)}
                className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-sm"
              >
                <option value="">Select lounge access</option>
                <option value="solo">👤 Solo travel</option>
                <option value="with_guests">👥 With 1 companion</option>
                <option value="family">👨‍👩‍👧‍👦 With family</option>
              </select>
            </div>
          </div>

          {/* Financial Preferences */}
          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              <IndianRupee className="w-4 h-4 text-green-500" />
              <h3 className="font-medium text-gray-900 dark:text-white">Financial Preferences</h3>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Annual Fee Range
              </label>
              <select
                value={localPreferences.fee_willingness || ''}
                onChange={(e) => handleLocalChange('fee_willingness', e.target.value || null)}
                className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-sm"
              >
                <option value="">Select fee range</option>
                <option value="0-1000">₹0 - ₹1,000</option>
                <option value="1000-5000">₹1,000 - ₹5,000</option>
                <option value="5000-10000">₹5,000 - ₹10,000</option>
                <option value="10000+">₹10,000+</option>
              </select>
            </div>
          </div>

          {/* Card Preferences */}
          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              <CreditCard className="w-4 h-4 text-purple-500" />
              <h3 className="font-medium text-gray-900 dark:text-white">Card & Bank Preferences</h3>
            </div>
            
            {/* Current Cards */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Current Cards
              </label>
              <div className="space-y-2">
                {(localPreferences.current_cards || []).map((card, index) => (
                  <div key={index} className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-700 rounded">
                    <span className="text-sm text-gray-900 dark:text-white">{card}</span>
                    <button
                      onClick={() => removeCard(card)}
                      className="text-red-500 hover:text-red-700"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ))}
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={newCard}
                    onChange={(e) => setNewCard(e.target.value)}
                    placeholder="Add current card"
                    className="flex-1 p-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-sm"
                    onKeyPress={(e) => e.key === 'Enter' && addCard()}
                  />
                  <button
                    onClick={addCard}
                    className="p-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                  >
                    <Plus className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>

            {/* Preferred Banks */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Preferred Banks
              </label>
              <div className="space-y-2">
                {(localPreferences.preferred_banks || []).map((bank, index) => (
                  <div key={index} className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-700 rounded">
                    <span className="text-sm text-gray-900 dark:text-white">{bank}</span>
                    <button
                      onClick={() => removeBank(bank)}
                      className="text-red-500 hover:text-red-700"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ))}
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={newBank}
                    onChange={(e) => setNewBank(e.target.value)}
                    placeholder="Add preferred bank"
                    className="flex-1 p-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-sm"
                    onKeyPress={(e) => e.key === 'Enter' && addBank()}
                  />
                  <button
                    onClick={addBank}
                    className="p-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                  >
                    <Plus className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Spending Categories */}
          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              <ShoppingBag className="w-4 h-4 text-orange-500" />
              <h3 className="font-medium text-gray-900 dark:text-white">Spending Categories</h3>
            </div>
            
            <div className="grid grid-cols-2 gap-2">
              {spendingCategories.map((category) => {
                const isSelected = (localPreferences.spend_categories || []).includes(category.value);
                return (
                  <button
                    key={category.value}
                    onClick={() => toggleSpendCategory(category.value)}
                    className={`p-3 rounded-lg border text-left transition-all ${
                      isSelected
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-200 dark:border-gray-600 hover:border-blue-300'
                    }`}
                  >
                    <div className="text-sm font-medium text-gray-900 dark:text-white">{category.label}</div>
                    <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">{category.desc}</div>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
          <div className="flex space-x-2">
            <button
              onClick={handleSave}
              disabled={!hasChanges || isLoading}
              className="flex-1 flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Save className="w-4 h-4 mr-2" />
              {isLoading ? 'Saving...' : 'Save Changes'}
            </button>
            
            {hasChanges && (
              <button
                onClick={handleReset}
                className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 border border-gray-300 dark:border-gray-600 rounded-lg"
              >
                <RotateCcw className="w-4 h-4" />
              </button>
            )}
            
            <button
              onClick={handleClear}
              className="px-4 py-2 text-red-600 hover:text-red-800 border border-red-300 rounded-lg"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
          
          <p className="text-xs text-gray-500 dark:text-gray-400 text-center mt-2">
            💡 Your preferences help us give you more relevant recommendations
          </p>
        </div>
      </div>
    </>
  );
};

export default PreferenceSidebar;
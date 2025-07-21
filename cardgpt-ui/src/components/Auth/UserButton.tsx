import React, { useState, useRef, useEffect } from 'react';
import { User, LogOut, BarChart3, ChevronDown } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

interface UserButtonProps {
  onShowAuth?: () => void;
}

const UserButton: React.FC<UserButtonProps> = ({ onShowAuth }) => {
  const { user, stats, queryLimit, isAuthenticated, logout } = useAuth();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [avatarError, setAvatarError] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  
  // Check if avatars are globally disabled due to rate limiting
  const checkAvatarsDisabled = () => {
    const disabled = localStorage.getItem('avatars_disabled') === 'true';
    const disabledUntil = localStorage.getItem('avatars_disabled_until');
    
    if (disabled && disabledUntil) {
      const until = parseInt(disabledUntil);
      if (Date.now() > until) {
        // Timeout expired, re-enable avatars
        localStorage.removeItem('avatars_disabled');
        localStorage.removeItem('avatars_disabled_until');
        return false;
      }
    }
    
    return disabled;
  };
  
  const avatarsDisabled = checkAvatarsDisabled();

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Reset avatar error when user changes (unless globally disabled)
  useEffect(() => {
    if (!avatarsDisabled) {
      setAvatarError(false);
    }
  }, [user?.picture, avatarsDisabled]);

  const handleAvatarError = () => {
    console.log('Avatar image failed to load (429 or network error):', user?.picture);
    setAvatarError(true);
    
    // If this might be a rate limiting issue, disable avatars globally for 1 hour
    if (user?.picture?.includes('googleusercontent.com')) {
      console.log('Disabling Google avatars globally due to rate limiting');
      localStorage.setItem('avatars_disabled', 'true');
      localStorage.setItem('avatars_disabled_until', (Date.now() + 60 * 60 * 1000).toString()); // 1 hour
    }
  };

  const handleSignOut = () => {
    logout();
    setIsDropdownOpen(false);
  };

  const getQueryCountText = () => {
    if (isAuthenticated) {
      if (stats) {
        return `${stats.today_queries} queries today`;
      }
      return 'Unlimited queries';
    }
    
    if (queryLimit) {
      return `${queryLimit.current_count}/${queryLimit.limit} free queries used`;
    }
    
    return 'Loading...';
  };

  const getAvatarFallback = (name: string) => {
    return name
      .split(' ')
      .map(word => word[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  // Optimize Google avatar URL to reduce size and potentially avoid rate limits
  const getOptimizedAvatarUrl = (url: string) => {
    if (url.includes('googleusercontent.com')) {
      // Replace with smaller size and remove unnecessary parameters
      return url.replace(/=s\d+-c/, '=s32-c');
    }
    return url;
  };

  if (!isAuthenticated) {
    // Sign-in button for unauthenticated users
    return (
      <button
        onClick={onShowAuth}
        className="flex items-center space-x-2 px-3 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors duration-200 text-sm font-medium"
      >
        <User className="w-4 h-4" />
        <span className="hidden sm:inline">Sign In</span>
      </button>
    );
  }

  // User dropdown for authenticated users
  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsDropdownOpen(!isDropdownOpen)}
        className="flex items-center space-x-2 px-3 py-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors duration-200 text-sm"
      >
        {/* User Avatar */}
        <div className="w-6 h-6 rounded-full overflow-hidden bg-primary-600 flex items-center justify-center">
          {user?.picture && !avatarError && !avatarsDisabled ? (
            <img
              src={getOptimizedAvatarUrl(user.picture)}
              alt={user.name || 'User'}
              className="w-full h-full object-cover"
              onError={handleAvatarError}
            />
          ) : (
            <span className="text-white text-xs font-medium">
              {user?.name ? getAvatarFallback(user.name) : 'U'}
            </span>
          )}
        </div>
        
        {/* User Name (hidden on small screens) */}
        <span className="hidden md:inline text-gray-700 dark:text-gray-200 font-medium">
          {user?.name ? user.name.split(' ')[0] : 'User'}
        </span>
        
        {/* Dropdown Arrow */}
        <ChevronDown className={`w-3 h-3 text-gray-500 transition-transform duration-200 ${
          isDropdownOpen ? 'rotate-180' : ''
        }`} />
      </button>

      {/* Dropdown Menu */}
      {isDropdownOpen && (
        <div className="absolute right-0 mt-2 w-64 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-2 z-50">
          {/* User Info */}
          <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 rounded-full overflow-hidden bg-primary-600 flex items-center justify-center">
                {user?.picture && !avatarError && !avatarsDisabled ? (
                  <img
                    src={getOptimizedAvatarUrl(user.picture)}
                    alt={user.name || 'User'}
                    className="w-full h-full object-cover"
                    onError={handleAvatarError}
                  />
                ) : (
                  <span className="text-white text-sm font-medium">
                    {user?.name ? getAvatarFallback(user.name) : 'U'}
                  </span>
                )}
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  {user?.name || 'User'}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {user?.email}
                </p>
              </div>
            </div>
          </div>

          {/* Query Count */}
          <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center space-x-2">
              <BarChart3 className="w-4 h-4 text-gray-500" />
              <div>
                <p className="text-sm text-gray-700 dark:text-gray-300">
                  {getQueryCountText()}
                </p>
                {stats && (
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Total: {stats.total_queries} queries
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Sign Out */}
          <button
            onClick={handleSignOut}
            className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 flex items-center space-x-2 transition-colors duration-200"
          >
            <LogOut className="w-4 h-4" />
            <span>Sign Out</span>
          </button>
        </div>
      )}
    </div>
  );
};

export default UserButton;
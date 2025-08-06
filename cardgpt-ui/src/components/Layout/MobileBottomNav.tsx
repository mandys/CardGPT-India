import React from 'react';
import { MessageCircle, Settings, BarChart3, User } from 'lucide-react';
import { useSidebar } from '../../hooks/useSidebar';
import { useUser } from '@clerk/clerk-react';

interface MobileBottomNavProps {
  onClearChat?: () => void;
  onShowSettings?: () => void;
  onShowAnalytics?: () => void;
  onShowSignIn?: () => void;
}

const MobileBottomNav: React.FC<MobileBottomNavProps> = ({
  onClearChat,
  onShowSettings,
  onShowAnalytics,
  onShowSignIn,
}) => {
  const { isMobile } = useSidebar();
  const { isSignedIn, user } = useUser();

  // Only show on mobile
  if (!isMobile) return null;

  return (
    <div className="mobile-bottom-nav fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 px-4 py-2 z-30 lg:hidden">
      <div className="flex justify-around items-center">
        {/* Chat */}
        <button
          onClick={onClearChat}
          className="flex flex-col items-center p-2 text-gray-600 dark:text-gray-400 hover:text-primary-600 transition-colors"
        >
          <MessageCircle className="w-5 h-5" />
          <span className="text-xs mt-1">Chat</span>
        </button>
        
        {/* Settings */}
        <button
          onClick={onShowSettings}
          className="flex flex-col items-center p-2 text-gray-600 dark:text-gray-400 hover:text-primary-600 transition-colors"
        >
          <Settings className="w-5 h-5" />
          <span className="text-xs mt-1">Settings</span>
        </button>
        
        {/* Analytics */}
        <button
          onClick={onShowAnalytics}
          className="flex flex-col items-center p-2 text-gray-600 dark:text-gray-400 hover:text-primary-600 transition-colors"
        >
          <BarChart3 className="w-5 h-5" />
          <span className="text-xs mt-1">Analytics</span>
        </button>
        
        {/* Profile/Sign-in */}
        <button
          onClick={onShowSignIn}
          className="flex flex-col items-center p-2 text-gray-600 dark:text-gray-400 hover:text-primary-600 transition-colors"
        >
          {isSignedIn && user?.imageUrl ? (
            <img
              src={user.imageUrl}
              alt={user.fullName || 'Profile'}
              className="w-5 h-5 rounded-full border border-gray-300"
            />
          ) : (
            <User className="w-5 h-5" />
          )}
          <span className="text-xs mt-1 truncate max-w-12">
            {isSignedIn && user?.fullName ? 
              user.fullName.split(' ')[0] : 
              'Sign-in'
            }
          </span>
        </button>
      </div>
    </div>
  );
};

export default MobileBottomNav;
import React from 'react';
import { MessageCircle, Settings, BarChart3, User } from 'lucide-react';
import { useSidebar } from '../../hooks/useSidebar';

interface MobileBottomNavProps {
  onClearChat?: () => void;
  onShowAnalytics?: () => void;
  onShowProfile?: () => void;
}

const MobileBottomNav: React.FC<MobileBottomNavProps> = ({
  onClearChat,
  onShowAnalytics,
  onShowProfile,
}) => {
  const { toggleSidebar, isMobile } = useSidebar();

  // Only show on mobile
  if (!isMobile) return null;

  return (
    <div className="mobile-bottom-nav fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-4 py-2 z-30 lg:hidden">
      <div className="flex justify-around items-center">
        {/* Chat */}
        <button
          onClick={onClearChat}
          className="flex flex-col items-center p-2 text-gray-600 hover:text-primary-600 transition-colors"
        >
          <MessageCircle className="w-5 h-5" />
          <span className="text-xs mt-1">Chat</span>
        </button>
        
        {/* Settings */}
        <button
          onClick={toggleSidebar}
          className="flex flex-col items-center p-2 text-gray-600 hover:text-primary-600 transition-colors"
        >
          <Settings className="w-5 h-5" />
          <span className="text-xs mt-1">Settings</span>
        </button>
        
        {/* Analytics */}
        <button
          onClick={onShowAnalytics}
          className="flex flex-col items-center p-2 text-gray-600 hover:text-primary-600 transition-colors"
        >
          <BarChart3 className="w-5 h-5" />
          <span className="text-xs mt-1">Analytics</span>
        </button>
        
        {/* Profile */}
        <button
          onClick={onShowProfile}
          className="flex flex-col items-center p-2 text-gray-600 hover:text-primary-600 transition-colors"
        >
          <User className="w-5 h-5" />
          <span className="text-xs mt-1">Profile</span>
        </button>
      </div>
    </div>
  );
};

export default MobileBottomNav;
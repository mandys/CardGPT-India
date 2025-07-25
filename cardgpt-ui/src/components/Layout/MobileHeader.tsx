import React from 'react';
import { Menu } from 'lucide-react';
import { useSidebar } from '../../hooks/useSidebar';
import UserButton from '../Auth/UserButton';

interface MobileHeaderProps {
  isConnected: boolean;
  onRefresh: () => void;
  isLoading?: boolean;
  onShowAuth?: () => void;
}

const MobileHeader: React.FC<MobileHeaderProps> = ({ 
  isConnected, 
  onRefresh, 
  isLoading = false, 
  onShowAuth 
}) => {
  const { toggleSidebar } = useSidebar();

  return (
    <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-3">
      <div className="flex items-center justify-between">
        {/* Left: Menu + Logo + Title */}
        <div className="flex items-center space-x-3 flex-1 min-w-0">
          <button
            onClick={toggleSidebar}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors flex-shrink-0"
            aria-label="Toggle sidebar"
          >
            <Menu className="w-5 h-5 text-gray-600 dark:text-gray-300" />
          </button>
          
          <div className="flex items-center space-x-3 min-w-0">
            <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0" style={{background: 'var(--gradient-primary)'}}>
              <span className="text-lg">💳</span>
            </div>
            <div className="min-w-0">
              <h1 className="text-lg font-bold text-gray-900 dark:text-white truncate">CardGPT</h1>
            </div>
          </div>
        </div>
        
        {/* Right: User Button Only */}
        <div className="flex-shrink-0">
          <UserButton onShowAuth={onShowAuth} />
        </div>
      </div>
    </header>
  );
};

export default MobileHeader;
import React from 'react';
import { RefreshCw, AlertCircle, Menu, X } from 'lucide-react';
import { useSidebar } from '../../hooks/useSidebar';
import UserButton from '../Auth/UserButton';

interface HeaderProps {
  isConnected: boolean;
  onRefresh: () => void;
  isLoading?: boolean;
  onShowAuth?: () => void;
}

const Header: React.FC<HeaderProps> = ({ isConnected, onRefresh, isLoading = false, onShowAuth }) => {
  const { isOpen, isMobile, toggleSidebar } = useSidebar();

  return (
    <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 lg:px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Left side: Menu toggle + Logo */}
        <div className="flex items-center space-x-3">
          {/* Sidebar Toggle Button */}
          <button
            onClick={toggleSidebar}
            className="sidebar-toggle p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors lg:block"
            aria-label="Toggle sidebar"
          >
            {isMobile ? (
              <Menu className="w-5 h-5 text-gray-600 dark:text-gray-300" />
            ) : (
              isOpen ? <X className="w-5 h-5 text-gray-600 dark:text-gray-300" /> : <Menu className="w-5 h-5 text-gray-600 dark:text-gray-300" />
            )}
          </button>
          
          {/* Logo and Title */}
          <div className="flex items-center space-x-3">
            <div className="flex items-center justify-center w-10 h-10 rounded-lg" style={{background: 'var(--gradient-primary)'}}>
              <span className="text-xl">💳</span>
            </div>
            <div className="hidden sm:block">
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                CardGPT - Your pocket-sized credit card expert ✨
              </h1>
            </div>
          </div>
        </div>
        
        {/* Status and Actions - Desktop Only */}
        <div className="flex items-center space-x-4">
          {/* Connection Status - Debug Info */}
          <div className="hidden md:flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${
              isConnected ? 'bg-green-500' : 'bg-red-500'
            }`}></div>
            <span className="text-sm text-gray-600 dark:text-gray-300">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
          
          {/* Refresh Button - Debug Info */}
          <button
            onClick={onRefresh}
            disabled={isLoading}
            className="hidden md:flex items-center space-x-2 px-3 py-1.5 text-sm bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200 rounded-lg transition-colors duration-200 disabled:opacity-50"
            title="Refresh connection"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
          
          {/* User Authentication */}
          <UserButton onShowAuth={onShowAuth} />
          
          {/* Warning if disconnected - Desktop Only */}
          {!isConnected && (
            <div className="hidden md:flex items-center space-x-1 px-2 py-1 bg-yellow-100 dark:bg-yellow-900/20 text-yellow-800 dark:text-yellow-400 rounded-lg">
              <AlertCircle className="w-4 h-4" />
              <span className="text-sm">Backend offline</span>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
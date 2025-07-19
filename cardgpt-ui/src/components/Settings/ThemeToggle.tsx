import React from 'react';
import { Sun, Moon } from 'lucide-react';
import { useTheme } from '../../contexts/ThemeContext';

export const ThemeToggle: React.FC = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
      <div className="flex items-center space-x-3">
        <div className="p-2 rounded-lg bg-white dark:bg-gray-700 shadow-sm">
          {theme === 'light' ? (
            <Sun className="w-4 h-4 text-yellow-500" />
          ) : (
            <Moon className="w-4 h-4 text-blue-400" />
          )}
        </div>
        <div>
          <h3 className="text-sm font-medium text-gray-900 dark:text-white">
            Appearance
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            {theme === 'light' ? 'Light mode' : 'Dark mode'}
          </p>
        </div>
      </div>
      
      <button
        onClick={toggleTheme}
        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800 ${
          theme === 'dark'
            ? 'bg-primary-600'
            : 'bg-gray-200'
        }`}
        aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
      >
        <span
          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
            theme === 'dark' ? 'translate-x-6' : 'translate-x-1'
          }`}
        />
      </button>
    </div>
  );
};
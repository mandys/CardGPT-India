import React from 'react';
import { LogOut, User, BarChart3, Calendar, Crown, X } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

interface UserProfileProps {
  onClose?: () => void;
}

const UserProfile: React.FC<UserProfileProps> = ({ onClose }) => {
  const { user, stats, logout, isAuthenticated } = useAuth();

  if (!isAuthenticated || !user) {
    return null;
  }

  const handleLogout = () => {
    logout();
    onClose?.();
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-6 space-y-6 relative">
      {/* Close Button */}
      <button
        onClick={onClose}
        className="absolute top-4 right-4 p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition-colors"
      >
        <X className="w-5 h-5 text-gray-500 dark:text-gray-400" />
      </button>
      
      {/* User Info */}
      <div className="flex items-center space-x-4">
        {user.picture ? (
          <img
            src={user.picture}
            alt={user.name}
            className="w-16 h-16 rounded-full border-2 border-gray-200 dark:border-gray-600"
          />
        ) : (
          <div className="w-16 h-16 bg-gray-200 dark:bg-gray-600 rounded-full flex items-center justify-center">
            <User className="w-8 h-8 text-gray-500 dark:text-gray-400" />
          </div>
        )}
        
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            {user.name}
          </h3>
          <p className="text-gray-600 dark:text-gray-400 text-sm">
            {user.email}
          </p>
          <div className="flex items-center gap-1 mt-1">
            <Crown className="w-4 h-4 text-yellow-500" />
            <span className="text-xs text-yellow-600 dark:text-yellow-400 font-medium">
              Premium User
            </span>
          </div>
        </div>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <BarChart3 className="w-4 h-4 text-blue-500" />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Total Queries
              </span>
            </div>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {stats.total_queries.toLocaleString()}
            </p>
          </div>
          
          <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Calendar className="w-4 h-4 text-green-500" />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Today
              </span>
            </div>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {stats.today_queries}
            </p>
          </div>
        </div>
      )}

      {/* Account Info */}
      <div className="space-y-3 text-sm text-gray-600 dark:text-gray-400">
        <div className="flex justify-between">
          <span>Member since:</span>
          <span className="font-medium">{formatDate(user.created_at)}</span>
        </div>
        <div className="flex justify-between">
          <span>Last login:</span>
          <span className="font-medium">{formatDate(user.last_login)}</span>
        </div>
        <div className="flex justify-between">
          <span>Query limit:</span>
          <span className="font-medium text-green-600 dark:text-green-400">
            Unlimited ✨
          </span>
        </div>
      </div>

      {/* Actions */}
      <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
        <button
          onClick={handleLogout}
          className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-red-50 hover:bg-red-100 dark:bg-red-900/20 dark:hover:bg-red-900/30 text-red-600 dark:text-red-400 rounded-lg transition-colors"
        >
          <LogOut className="w-4 h-4" />
          Sign Out
        </button>
      </div>
    </div>
  );
};

export default UserProfile;
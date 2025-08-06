import React from 'react';
import { AlertCircle, Crown, Zap, LogIn } from 'lucide-react';

interface QueryLimitBadgeProps {
  remaining: number;
  total: number;
  isGuest: boolean;
  canQuery: boolean;
  message?: string;
  onSignIn: () => void;
  className?: string;
}

const QueryLimitBadge: React.FC<QueryLimitBadgeProps> = ({
  remaining,
  total,
  isGuest,
  canQuery,
  message,
  onSignIn,
  className = '',
}) => {
  if (!isGuest) {
    // For signed-in users, show a simple status or nothing
    return null;
  }

  const percentage = (remaining / total) * 100;
  const isLow = remaining <= 1;
  const isExhausted = remaining === 0;

  if (isExhausted) {
    return (
      <div className={`glass-card border-0 bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20 border border-amber-200 dark:border-amber-800 ${className}`}>
        <div className="flex items-center gap-3 p-3">
          <div className="flex-shrink-0">
            <AlertCircle className="w-5 h-5 text-amber-600 dark:text-amber-400" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-amber-800 dark:text-amber-200">
              Free Queries Used
            </p>
            <p className="text-xs text-amber-700 dark:text-amber-300 mt-1">
              {message || 'Sign in to continue with unlimited queries'}
            </p>
          </div>
          <button
            onClick={onSignIn}
            className="flex-shrink-0 inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700 rounded-lg transition-all duration-200 transform hover:scale-105"
          >
            <LogIn className="w-3 h-3" />
            Sign In
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`inline-flex items-center gap-2 px-3 py-1.5 text-xs font-medium rounded-full border transition-all duration-200 ${
      isLow 
        ? 'bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-700 text-amber-700 dark:text-amber-300' 
        : 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-700 text-blue-700 dark:text-blue-300'
    } ${className}`}>
      <Zap className={`w-3 h-3 ${isLow ? 'text-amber-500' : 'text-blue-500'}`} />
      <span>
        {remaining} free quer{remaining === 1 ? 'y' : 'ies'} left
      </span>
      {isLow && (
        <button
          onClick={onSignIn}
          className="ml-2 inline-flex items-center gap-1 px-2 py-0.5 text-xs bg-violet-600 hover:bg-violet-700 text-white rounded transition-colors"
        >
          <Crown className="w-3 h-3" />
          Upgrade
        </button>
      )}
    </div>
  );
};

export default QueryLimitBadge;
import React from 'react';
import { AlertTriangle, Crown, LogIn } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

interface QueryLimitWarningProps {
  onSignIn: () => void;
}

const QueryLimitWarning: React.FC<QueryLimitWarningProps> = ({ onSignIn }) => {
  const { queryLimit, isAuthenticated } = useAuth();

  // Don't show if authenticated or if they can still query
  if (isAuthenticated || !queryLimit || queryLimit.can_query) {
    return null;
  }

  return (
    <div className="mb-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4">
      <div className="flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <h3 className="font-medium text-amber-800 dark:text-amber-200 mb-1">
            Daily Query Limit Reached
          </h3>
          <p className="text-amber-700 dark:text-amber-300 text-sm mb-3">
            You've used all {queryLimit.limit} free queries today. Sign in with Google to get unlimited access to our credit card assistant!
          </p>
          
          <div className="flex flex-col sm:flex-row gap-2">
            <button
              onClick={onSignIn}
              className="flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors text-sm font-medium"
            >
              <LogIn className="w-4 h-4" />
              Sign in with Google
            </button>
            
            <div className="flex items-center gap-1 text-xs text-amber-600 dark:text-amber-400">
              <Crown className="w-3 h-3" />
              <span>Unlimited queries • Personalized experience • Free forever</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QueryLimitWarning;
import React from 'react';
import { X, Shield, Zap, Users } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import GoogleSignIn from './GoogleSignIn';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose }) => {
  const { queryLimit } = useAuth();

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-xl max-w-md w-full max-h-[90vh] overflow-y-auto shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Sign In to Credit Card Assistant
          </h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Query limit warning */}
          {queryLimit && !queryLimit.can_query && (
            <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4">
              <div className="flex items-center gap-2 text-amber-800 dark:text-amber-200 font-medium mb-2">
                <Shield className="w-5 h-5" />
                Daily Limit Reached
              </div>
              <p className="text-amber-700 dark:text-amber-300 text-sm">
                You've used all {queryLimit.limit} free queries today. Sign in with Google to get unlimited access!
              </p>
            </div>
          )}

          {/* Benefits */}
          <div className="space-y-4">
            <h3 className="font-medium text-gray-900 dark:text-white">
              Why sign in?
            </h3>
            
            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <div className="bg-blue-100 dark:bg-blue-900/30 p-2 rounded-lg">
                  <Zap className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                </div>
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white text-sm">
                    Unlimited Queries
                  </h4>
                  <p className="text-gray-600 dark:text-gray-400 text-sm">
                    Ask as many questions as you want about credit cards
                  </p>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <div className="bg-green-100 dark:bg-green-900/30 p-2 rounded-lg">
                  <Shield className="w-5 h-5 text-green-600 dark:text-green-400" />
                </div>
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white text-sm">
                    Secure & Private
                  </h4>
                  <p className="text-gray-600 dark:text-gray-400 text-sm">
                    We only access your basic profile information
                  </p>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <div className="bg-purple-100 dark:bg-purple-900/30 p-2 rounded-lg">
                  <Users className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                </div>
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white text-sm">
                    Personalized Experience
                  </h4>
                  <p className="text-gray-600 dark:text-gray-400 text-sm">
                    Track your query history and preferences
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Current status for guests */}
          {queryLimit && queryLimit.can_query && (
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
              <div className="text-blue-800 dark:text-blue-200 text-sm">
                <strong>Current status:</strong> {queryLimit.current_count}/{queryLimit.limit} free queries used today
                {queryLimit.remaining && (
                  <span className="block mt-1">
                    {queryLimit.remaining} queries remaining
                  </span>
                )}
              </div>
            </div>
          )}

          {/* Google Sign In */}
          <GoogleSignIn
            onSuccess={() => {
              onClose();
            }}
            onError={() => {
              // Error handling is done in GoogleSignIn component
            }}
          />

          {/* Continue as guest option */}
          {queryLimit?.can_query && (
            <div className="text-center pt-4 border-t border-gray-200 dark:border-gray-700">
              <button
                onClick={onClose}
                className="text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 transition-colors"
              >
                Continue as guest ({queryLimit.remaining} queries left)
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AuthModal;
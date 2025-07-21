import React, { useState } from 'react';
import { GoogleLogin } from '@react-oauth/google';
import { useAuth } from '../../contexts/AuthContext';
import { AlertCircle, LogIn } from 'lucide-react';

interface GoogleSignInProps {
  onSuccess?: () => void;
  onError?: () => void;
}

const GoogleSignIn: React.FC<GoogleSignInProps> = ({ onSuccess, onError }) => {
  const { login } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSuccess = async (credentialResponse: any) => {
    setIsLoading(true);
    setError(null);

    try {
      if (credentialResponse.credential) {
        const success = await login(credentialResponse.credential);
        
        if (success) {
          onSuccess?.();
        } else {
          setError('Login failed. Please try again.');
          onError?.();
        }
      } else {
        setError('No credential received from Google');
        onError?.();
      }
    } catch (err) {
      console.error('Login error:', err);
      setError('An unexpected error occurred');
      onError?.();
    } finally {
      setIsLoading(false);
    }
  };

  const handleError = () => {
    setError('Google sign-in was cancelled or failed');
    onError?.();
  };

  return (
    <div className="w-full space-y-4">
      {error && (
        <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}
      
      <div className="flex flex-col items-center space-y-3">
        <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400 text-sm mb-2">
          <LogIn className="w-4 h-4" />
          <span>Sign in with Google for unlimited queries</span>
        </div>
        
        {isLoading ? (
          <div className="flex items-center justify-center py-3 px-6 bg-gray-100 rounded-lg">
            <div className="animate-spin h-5 w-5 border-2 border-blue-500 border-t-transparent rounded-full"></div>
            <span className="ml-2 text-gray-600">Signing in...</span>
          </div>
        ) : (
          <GoogleLogin
            onSuccess={handleSuccess}
            onError={handleError}
            useOneTap={false}
            size="large"
            theme="outline"
            shape="rectangular"
            text="signin_with"
          />
        )}
        
        <p className="text-xs text-gray-500 dark:text-gray-400 text-center max-w-sm">
          By signing in, you agree to our terms of service and privacy policy. 
          We only access your basic profile information.
        </p>
      </div>
    </div>
  );
};

export default GoogleSignIn;
import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { GoogleOAuthProvider } from '@react-oauth/google';
import { ThemeProvider } from './contexts/ThemeContext';
import { AuthProvider } from './contexts/AuthContext';
import LandingPage from './components/Landing/LandingPage';
import MainLayout from './components/Layout/MainLayout';
import PrivacyPolicy from './components/Pages/PrivacyPolicy';
import './styles/globals.css';

// Create a client for React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
    },
  },
});

const GOOGLE_CLIENT_ID = "910315304252-im8oclg36n7dun7hjs2atkv8p2ln7ng7.apps.googleusercontent.com";

const App: React.FC = () => {
  // Add error boundary and debugging
  React.useEffect(() => {
    console.log('🚀 App Component Mounted');
    console.log('🌍 API URL:', process.env.REACT_APP_API_URL);
    console.log('🔧 Environment:', process.env.NODE_ENV);
  }, []);

  try {
    return (
      <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
        <QueryClientProvider client={queryClient}>
          <AuthProvider>
            <ThemeProvider>
              <Router>
                <div className="App">
                  <Routes>
                    {/* Landing Page - Default Route */}
                    <Route path="/" element={<LandingPage />} />
                    
                    {/* Chat Interface */}
                    <Route path="/chat" element={<MainLayout />} />
                    
                    {/* Privacy Policy */}
                    <Route path="/privacy" element={<PrivacyPolicy />} />
                    
                    {/* Redirect any unknown routes to landing page */}
                    <Route path="*" element={<Navigate to="/" replace />} />
                  </Routes>
                </div>
              </Router>
            </ThemeProvider>
          </AuthProvider>
        </QueryClientProvider>
      </GoogleOAuthProvider>
    );
  } catch (error) {
    console.error('💥 App Error:', error);
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        flexDirection: 'column',
        fontFamily: 'Arial, sans-serif'
      }}>
        <h1>⚠️ App Error</h1>
        <p>Something went wrong. Check the console for details.</p>
        <p>API URL: {process.env.REACT_APP_API_URL || 'Not Set'}</p>
      </div>
    );
  }
};

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { GoogleOAuthProvider } from '@react-oauth/google';
import { ThemeProvider } from './contexts/ThemeContext';
import { AuthProvider } from './contexts/AuthContext';
import LandingPage from './components/Landing/LandingPage';
import MainLayout from './components/Layout/MainLayout';
import PrivacyPolicy from './components/Pages/PrivacyPolicy';
import './styles/globals.css';

// Create a client for React Query (fixed for Vercel deployment)
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
};

export default App;
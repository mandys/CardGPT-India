import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

interface User {
  id: number;
  google_id: string;
  email: string;
  name: string;
  picture: string;
  created_at: string;
  last_login: string;
}

interface UserStats {
  total_queries: number;
  today_queries: number;
  is_unlimited: boolean;
}

interface QueryLimit {
  can_query: boolean;
  current_count: number;
  limit: number;
  remaining?: number;
}

interface AuthContextType {
  user: User | null;
  stats: UserStats | null;
  queryLimit: QueryLimit | null;
  isAuthenticated: boolean;
  login: (googleToken: string) => Promise<boolean>;
  logout: () => void;
  checkQueryLimit: () => Promise<void>;
  incrementQuery: () => Promise<boolean>;
  refreshStats: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [stats, setStats] = useState<UserStats | null>(null);
  const [queryLimit, setQueryLimit] = useState<QueryLimit | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const verifyToken = useCallback(async (token: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/verify`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        if (data.valid) {
          setIsAuthenticated(true);
          // Get user stats
          await refreshStats();
          return;
        }
      }
      
      // Token invalid, remove it
      localStorage.removeItem('jwt_token');
      setIsAuthenticated(false);
      setUser(null);
      setStats(null);
      await checkQueryLimit();
    } catch (error) {
      console.error('Token verification error:', error);
      localStorage.removeItem('jwt_token');
      setIsAuthenticated(false);
      setUser(null);
      setStats(null);
      // Still check query limit for guest users even if verification fails
      try {
        await checkQueryLimit();
      } catch (limitError) {
        console.error('Query limit check failed:', limitError);
      }
    }
  }, []); // checkQueryLimit will be defined after this

  const login = async (googleToken: string): Promise<boolean> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/google`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ token: googleToken })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success && data.jwt_token) {
          localStorage.setItem('jwt_token', data.jwt_token);
          setUser(data.user);
          setIsAuthenticated(true);
          await refreshStats();
          await checkQueryLimit();
          return true;
        }
      }
      
      const errorData = await response.json();
      console.error('Login failed:', errorData);
      return false;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('jwt_token');
    setUser(null);
    setStats(null);
    setIsAuthenticated(false);
    // Check guest query limits
    checkQueryLimit();
  };

  const checkQueryLimit = useCallback(async () => {
    try {
      const headers: HeadersInit = {
        'x-session-id': getSessionId()
      };

      const token = localStorage.getItem('jwt_token');
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${API_BASE_URL}/api/auth/query-limit`, {
        headers
      });

      if (response.ok) {
        const data = await response.json();
        setQueryLimit(data);
      }
    } catch (error) {
      console.error('Query limit check error:', error);
    }
  }, []);

  const incrementQuery = async (): Promise<boolean> => {
    try {
      const sessionId = getSessionId();
      console.log('🚀 Incrementing query for session:', sessionId);
      
      const headers: HeadersInit = {
        'x-session-id': sessionId
      };

      const token = localStorage.getItem('jwt_token');
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
        console.log('🔑 Using JWT token for authenticated user');
      } else {
        console.log('👤 Using session ID for guest user');
      }

      const response = await fetch(`${API_BASE_URL}/api/auth/increment-query`, {
        method: 'POST',
        headers
      });

      console.log('📈 Increment response status:', response.status);

      if (response.ok) {
        const data = await response.json();
        console.log('✅ Query incremented successfully:', data);
        await checkQueryLimit();
        
        // Refresh stats for authenticated users to update total query count
        if (token && isAuthenticated) {
          await refreshStats();
        }
        
        return true;
      } else if (response.status === 429) {
        console.log('❌ Query limit exceeded (429)');
        // Query limit exceeded
        await checkQueryLimit();
        return false;
      }
      
      console.log('❌ Increment failed with status:', response.status);
      return false;
    } catch (error) {
      console.error('Query increment error:', error);
      return false;
    }
  };

  const refreshStats = async () => {
    const token = localStorage.getItem('jwt_token');
    if (!token) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/stats`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setUser(data.user);
        setStats(data.stats);
      } else {
        console.error(`Stats refresh failed with status: ${response.status}`);
        if (response.status === 401) {
          // Token invalid, logout user
          logout();
        }
      }
    } catch (error) {
      console.error('Stats refresh error:', error);
      // Don't logout on network errors, just log them
    }
  };

  const getSessionId = (): string => {
    let sessionId = localStorage.getItem('session_id');
    if (!sessionId) {
      sessionId = 'session_' + Math.random().toString(36).substring(2, 11);
      localStorage.setItem('session_id', sessionId);
    }
    return sessionId;
  };

  // Check for existing token on app load
  useEffect(() => {
    const token = localStorage.getItem('jwt_token');
    if (token) {
      verifyToken(token);
    } else {
      // Check query limit for guest users
      checkQueryLimit();
    }
  }, [verifyToken, checkQueryLimit]);

  // Debug: Log query limit changes
  useEffect(() => {
    console.log('🔍 Query limit updated:', queryLimit);
  }, [queryLimit]);

  return (
    <AuthContext.Provider value={{
      user,
      stats,
      queryLimit,
      isAuthenticated,
      login,
      logout,
      checkQueryLimit,
      incrementQuery,
      refreshStats
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
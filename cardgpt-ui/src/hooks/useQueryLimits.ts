import { useState, useEffect, useCallback } from 'react';
import { useUser, useClerk } from '@clerk/clerk-react';

interface QueryLimitStatus {
  canQuery: boolean;
  remaining: number;
  total: number;
  isGuest: boolean;
  message?: string;
}

interface QueryLimitHook {
  status: QueryLimitStatus;
  checkAndIncrementQuery: () => Promise<boolean>;
  openSignIn: () => void;
  resetGuestCount: () => void;
  refreshStatus: () => Promise<void>;
}

const GUEST_QUERY_LIMIT = 2;
const QUERY_COUNT_KEY = "guest_query_count";
const DAILY_RESET_KEY = "query_count_date";

export const useQueryLimits = (): QueryLimitHook => {
  const { isSignedIn, user } = useUser();
  const { openSignIn } = useClerk();
  const [status, setStatus] = useState<QueryLimitStatus>({
    canQuery: true,
    remaining: GUEST_QUERY_LIMIT,
    total: GUEST_QUERY_LIMIT,
    isGuest: true,
  });

  // Guest query management functions
  const getGuestQueryCount = useCallback((): number => {
    try {
      const today = new Date().toDateString();
      const storedDate = localStorage.getItem(DAILY_RESET_KEY);
      
      // Reset count if it's a new day
      if (storedDate !== today) {
        localStorage.setItem(DAILY_RESET_KEY, today);
        localStorage.setItem(QUERY_COUNT_KEY, "0");
        return 0;
      }
      
      return parseInt(localStorage.getItem(QUERY_COUNT_KEY) || "0", 10);
    } catch (error) {
      console.warn('Error accessing localStorage:', error);
      return 0;
    }
  }, []);

  const incrementGuestQueryCount = useCallback((): number => {
    try {
      const count = getGuestQueryCount() + 1;
      localStorage.setItem(QUERY_COUNT_KEY, count.toString());
      return count;
    } catch (error) {
      console.warn('Error updating localStorage:', error);
      return GUEST_QUERY_LIMIT; // Assume limit reached on error
    }
  }, [getGuestQueryCount]);

  const resetGuestCount = useCallback(() => {
    try {
      localStorage.setItem(QUERY_COUNT_KEY, "0");
      localStorage.setItem(DAILY_RESET_KEY, new Date().toDateString());
    } catch (error) {
      console.warn('Error resetting localStorage:', error);
    }
  }, []);

  // Fetch authenticated user query limits from backend
  const fetchUserQueryStatus = useCallback(async (): Promise<QueryLimitStatus> => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/query-limits`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user?.id}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch query limits');
      }

      const data = await response.json();
      return {
        canQuery: data.can_query,
        remaining: data.remaining,
        total: data.total,
        isGuest: false,
        message: data.message,
      };
    } catch (error) {
      console.warn('Error fetching user query status:', error);
      // Fallback: allow queries but show warning
      return {
        canQuery: true,
        remaining: 50, // Default fallback
        total: 50,
        isGuest: false,
        message: 'Unable to verify query limits',
      };
    }
  }, [user?.id]);

  // Calculate guest query status
  const calculateGuestStatus = useCallback((): QueryLimitStatus => {
    const used = getGuestQueryCount();
    const remaining = Math.max(0, GUEST_QUERY_LIMIT - used);
    
    return {
      canQuery: remaining > 0,
      remaining,
      total: GUEST_QUERY_LIMIT,
      isGuest: true,
      message: remaining === 0 ? 'Free queries exhausted. Sign in for unlimited access!' : undefined,
    };
  }, [getGuestQueryCount]);

  // Refresh the query status
  const refreshStatus = useCallback(async () => {
    if (isSignedIn && user) {
      const userStatus = await fetchUserQueryStatus();
      setStatus(userStatus);
    } else {
      const guestStatus = calculateGuestStatus();
      setStatus(guestStatus);
    }
  }, [isSignedIn, user, fetchUserQueryStatus, calculateGuestStatus]);

  // Check and increment query count
  const checkAndIncrementQuery = useCallback(async (): Promise<boolean> => {
    if (isSignedIn && user) {
      try {
        const response = await fetch(`${process.env.REACT_APP_API_URL}/api/increment-query`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${user.id}`,
          },
          body: JSON.stringify({
            user_id: user.id,
            user_email: user.primaryEmailAddress?.emailAddress,
          }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          if (response.status === 429) {
            setStatus(prev => ({
              ...prev,
              canQuery: false,
              remaining: 0,
              message: errorData.detail || 'Daily limit reached',
            }));
            return false;
          }
          throw new Error('Failed to increment query count');
        }

        // Refresh status after successful increment
        await refreshStatus();
        return true;
      } catch (error) {
        console.error('Error incrementing user query:', error);
        return false;
      }
    } else {
      // Guest user logic
      const currentCount = getGuestQueryCount();
      if (currentCount >= GUEST_QUERY_LIMIT) {
        setStatus(prev => ({
          ...prev,
          canQuery: false,
          remaining: 0,
          message: 'Free queries exhausted. Sign in for unlimited access!',
        }));
        return false;
      }

      incrementGuestQueryCount();
      await refreshStatus();
      return true;
    }
  }, [isSignedIn, user, getGuestQueryCount, incrementGuestQueryCount, refreshStatus]);

  // Initialize status on mount and when auth changes
  useEffect(() => {
    refreshStatus();
  }, [refreshStatus]);

  // Clear guest count when user signs in
  useEffect(() => {
    if (isSignedIn) {
      resetGuestCount();
    }
  }, [isSignedIn, resetGuestCount]);

  return {
    status,
    checkAndIncrementQuery,
    openSignIn,
    resetGuestCount,
    refreshStatus,
  };
};

export default useQueryLimits;
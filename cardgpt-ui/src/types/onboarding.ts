// TypeScript definitions for streamlined onboarding modal

export type PrimaryGoal = 
  | 'maximize_rewards'
  | 'build_credit'
  | 'travel_benefits'
  | 'everyday_spending'
  | 'balance_transfer';

export type SpendingBracket = 
  | '0-25000'
  | '25000-75000'
  | '75000+';

export type SpendingCategory = 
  | 'online_shopping'
  | 'dining'
  | 'groceries'
  | 'fuel'
  | 'travel'
  | 'utilities';

export interface QuickPreferences {
  lowFees: boolean;
  international: boolean;
  business: boolean;
  digitalFirst: boolean;
}

export interface OnboardingData {
  primaryGoal?: PrimaryGoal;
  monthlySpending?: SpendingBracket;
  topCategories: SpendingCategory[];
  currentCards: string[];
  preferences: QuickPreferences;
}

export interface OnboardingContextValue {
  data: OnboardingData;
  updateData: (updates: Partial<OnboardingData>) => void;
  resetData: () => void;
  convertToUserPreferences: () => import('../types').UserPreferences;
}

export const PRIMARY_GOAL_OPTIONS = [
  {
    value: 'maximize_rewards' as PrimaryGoal,
    label: '🎯 Maximize rewards',
    description: 'Cashback, points, miles',
  },
  {
    value: 'build_credit' as PrimaryGoal,
    label: '💰 Build credit history',
    description: 'New to credit cards',
  },
  {
    value: 'travel_benefits' as PrimaryGoal,
    label: '✈️ Travel benefits',
    description: 'Lounge access, travel insurance',
  },
  {
    value: 'everyday_spending' as PrimaryGoal,
    label: '🛒 Everyday spending',
    description: 'Groceries, bills, fuel',
  },
  {
    value: 'balance_transfer' as PrimaryGoal,
    label: '💳 Balance transfers',
    description: 'Consolidate existing debt',
  },
] as const;

export const SPENDING_BRACKET_OPTIONS = [
  {
    value: '0-25000' as SpendingBracket,
    label: '₹0 - ₹25,000',
    description: 'Budget-friendly cards',
  },
  {
    value: '25000-75000' as SpendingBracket,
    label: '₹25,000 - ₹75,000',
    description: 'Mid-range premium cards',
  },
  {
    value: '75000+' as SpendingBracket,
    label: '₹75,000+',
    description: 'Super premium cards',
  },
] as const;

export const SPENDING_CATEGORY_OPTIONS = [
  {
    value: 'online_shopping' as SpendingCategory,
    label: '🛒 Online Shopping',
    emoji: '🛒',
  },
  {
    value: 'dining' as SpendingCategory,
    label: '🍽️ Dining',
    emoji: '🍽️',
  },
  {
    value: 'groceries' as SpendingCategory,
    label: '🛍️ Groceries',
    emoji: '🛍️',
  },
  {
    value: 'fuel' as SpendingCategory,
    label: '⛽ Fuel',
    emoji: '⛽',
  },
  {
    value: 'travel' as SpendingCategory,
    label: '✈️ Travel',
    emoji: '✈️',
  },
  {
    value: 'utilities' as SpendingCategory,
    label: '💡 Utilities',
    emoji: '💡',
  },
] as const;

export const QUICK_PREFERENCE_OPTIONS = [
  {
    key: 'lowFees' as keyof QuickPreferences,
    label: '💸 Low/no annual fees preferred',
    description: 'Focus on cards with minimal fees',
  },
  {
    key: 'international' as keyof QuickPreferences,
    label: '✈️ International travel frequent',
    description: 'Need global acceptance and benefits',
  },
  {
    key: 'business' as keyof QuickPreferences,
    label: '🏢 Business expenses included',
    description: 'Use card for business spending',
  },
  {
    key: 'digitalFirst' as keyof QuickPreferences,
    label: '📱 Digital-first banking preferred',
    description: 'Prefer app-based banking experience',
  },
] as const;

// Default values
export const DEFAULT_ONBOARDING_DATA: OnboardingData = {
  primaryGoal: undefined,
  monthlySpending: undefined,
  topCategories: [],
  currentCards: [],
  preferences: {
    lowFees: false,
    international: false,
    business: false,
    digitalFirst: false,
  },
};
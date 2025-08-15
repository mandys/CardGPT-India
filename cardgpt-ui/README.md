# Frontend README

## Overview
**Role**: Modern React TypeScript frontend that provides a responsive chat interface for credit card queries. Built with React 18, TypeScript, Tailwind CSS, and Clerk authentication.

**Architecture**: React + TypeScript + Tailwind CSS + Clerk Auth + Zustand State Management + Vercel Deployment

## Key Directories & Files

### Component Structure (`src/components/`)

#### Chat Components (`components/Chat/`)
- **`ChatInterface.tsx`** - **🎯 Main chat UI** - Message display, input field, loading states, and query submission
- **`MessageBubble.tsx`** - Individual message rendering with user/assistant distinction and markdown support
- **`SourcesDisplay.tsx`** - Displays search result sources and document references
- **`CostDisplay.tsx`** - Shows query cost breakdown and token usage information
- **`TypingIndicator.tsx`** - Animated loading indicator during AI response generation
- **`QueryLimitBadge.tsx`** - User query limit status and authentication prompts
- **`QueryLimitWarning.tsx`** - Rate limiting notifications and upgrade prompts

#### Layout Components (`components/Layout/`)
- **`MainLayout.tsx`** - **🏗️ Root layout component** - Manages authentication state, modals, and overall app structure
- **`Header.tsx`** - Desktop header with navigation, user profile, and settings
- **`Sidebar.tsx`** - Desktop sidebar with navigation, settings panel, and tips
- **`MobileHeader.tsx`** - Mobile-optimized header with hamburger menu and user actions
- **`MobileBottomNav.tsx`** - Mobile bottom navigation with chat, settings, and authentication

#### Onboarding & Preferences (`components/Onboarding/`)
- **`OnboardingModal.tsx`** - **📝 User preference collection** - Multi-step modal for gathering user preferences
- **`StepCurrentCards.tsx`** - Current credit cards selection step
- **`StepPrimaryGoal.tsx`** - Primary financial goal selection step  
- **`StepQuickPrefs.tsx`** - Quick preference selection step

#### Settings & Configuration (`components/Settings/`)
- **`SettingsPanel.tsx`** - **⚙️ Settings management** - Model selection, preferences, and system configuration
- **`ModelSelector.tsx`** - AI model selection (Gemini Flash/Pro) with cost information
- **`SettingsModal.tsx`** - Modal overlay for settings configuration

### Custom React Hooks (`src/hooks/`)
- **`useChat.ts`** - **💬 Chat state management** - Message handling, API calls, and conversation history
- **`usePreferences.ts`** - **👤 User preferences** - Preference loading, saving, and synchronization with backend
- **`useQueryLimits.ts`** - **🔒 Query rate limiting** - Guest/user limits, authentication triggers, and usage tracking
- **`useStreamingChat.ts`** - **⚡ Real-time responses** - Streaming API integration and progressive message building
- **`useOnboarding.ts`** - Onboarding flow state and multi-step form management
- **`useCardConfig.ts`** - Credit card configuration and metadata loading
- **`useTips.ts`** - Contextual tips and smart suggestions system

### Services & API (`src/services/`)
- **`api.ts`** - **🌐 REST API client** - HTTP requests, error handling, and response processing
- **`streamingApi.ts`** - **📡 Streaming API client** - Server-sent events and real-time response handling

### State Management (`src/stores/`)
- **`usePreferenceStore.ts`** - **🏪 Global state** - Zustand store for user preferences, session management, and data persistence
- **`index.ts`** - Store exports and configuration

### Type Definitions (`src/types/`)
- **`index.ts`** - **📋 Core types** - ChatMessage, User, ApiResponse, and shared interfaces
- **`cards.ts`** - Credit card data structures and metadata types
- **`onboarding.ts`** - User preference and onboarding form types

### Utilities (`src/utils/`)
- **`formatCost.ts`** - Currency and cost formatting utilities
- **`formatMessage.ts`** - Message processing and markdown formatting

## React Concepts Guide (Since React is New to You)

### Component Hierarchy & Data Flow
```
MainLayout (root)
├── Header/MobileHeader (navigation)
├── Sidebar (desktop) / MobileBottomNav (mobile)
├── ChatInterface (main content)
│   ├── MessageBubble (individual messages)
│   ├── SourcesDisplay (search results)
│   └── CostDisplay (usage info)
└── OnboardingModal (overlay when needed)
```

**Data flows DOWN** (parent to child via props)  
**Events flow UP** (child to parent via callback functions)

### Hook Usage Patterns
**Custom hooks are like Python functions that return multiple values**:
```typescript
// Similar to: status, limits, openSignIn = get_query_limits()
const { status, limits, openSignIn } = useQueryLimits();

// Similar to: messages, sendMessage, isLoading = get_chat_state()
const { messages, sendMessage, isLoading } = useChat();
```

**useEffect = Python's event handlers**:
```typescript
// Similar to: on_component_mount()
useEffect(() => {
  // Runs when component first loads
}, []);

// Similar to: on_message_change(messages)
useEffect(() => {
  // Runs when messages array changes
}, [messages]);
```

### State Management with Zustand (Like Python Class Variables)
```typescript
// Like a Python class with methods and properties
const usePreferenceStore = create((set, get) => ({
  // Properties (like self.preferences = {})
  preferences: {},
  isLoading: false,
  
  // Methods (like def save_preferences(self, data))
  savePreferences: async (data) => {
    set({ isLoading: true });
    // API call here
    set({ preferences: data, isLoading: false });
  }
}));
```

### Authentication Flow (Clerk Integration)
1. **`useAuth()`** hook provides authentication state
2. **`useUser()`** hook provides user information
3. **Components automatically re-render** when auth state changes
4. **Protected routes** check authentication before rendering

### Component Props (Like Python Function Arguments)
```typescript
interface ChatInterfaceProps {
  messages: ChatMessage[];           // Required array
  isLoading: boolean;               // Required boolean
  onSendMessage: (msg: string) => void;  // Required callback function
  onShowAuth?: () => void;          // Optional callback (? means optional)
}
```

## Environment Setup

### Required Environment Variables
```bash
# Clerk Authentication (Required)
REACT_APP_CLERK_PUBLISHABLE_KEY="pk_test_your-clerk-key"

# API Configuration (Required)
REACT_APP_API_URL="http://localhost:8000"  # Development
# REACT_APP_API_URL="https://your-backend.railway.app"  # Production
```

### Quick Start (2 Minutes)
```bash
# 1. Install dependencies (like pip install)
npm install

# 2. Set up environment variables
cp .env.example .env.local
# Edit .env.local with your Clerk key

# 3. Start development server
npm start
# OR use the script
./start_frontend.sh
```

### Development Commands
```bash
# Start development server (hot reload)
npm start

# Build for production
npm run build

# Run tests
npm test

# Check TypeScript types
npx tsc --noEmit
```

## Key Features & How They Work

### Real-Time Chat
1. **User types message** → `ChatInterface.tsx` captures input
2. **Submit button clicked** → `onSendMessage` callback triggered
3. **MainLayout handles** → Calls backend API via `useStreamingChat.ts`
4. **Streaming response** → Words appear one by one as AI generates them
5. **Message added** → UI automatically updates with new message

### Authentication & Preferences
1. **Guest users** → Can ask 2 free questions (tracked in localStorage)
2. **After limits** → Modal prompts for sign-in via Clerk
3. **Once authenticated** → Preferences sync from session to user account
4. **Smart UI** → Shows "Setup" or "Update" preferences based on existing data

### Mobile Responsiveness
- **Desktop**: Sidebar + Header layout
- **Mobile**: Bottom navigation + Mobile header
- **Breakpoints**: Tailwind CSS handles automatic switching
- **Touch-friendly**: Large buttons and swipe gestures

### State Management Pattern
1. **Global state** in Zustand stores (like Redux but simpler)
2. **Component state** in React hooks (temporary, local data)
3. **API state** managed by custom hooks
4. **Automatic re-rendering** when any state changes

## File Modification Guide

### To Change Chat Behavior
- **Message display**: `components/Chat/MessageBubble.tsx`
- **Input handling**: `components/Chat/ChatInterface.tsx`
- **API calls**: `hooks/useStreamingChat.ts`
- **Message types**: `src/types/index.ts`

### To Modify User Interface
- **Colors/styling**: `src/styles/globals.css` + Tailwind classes in components
- **Layout structure**: `components/Layout/MainLayout.tsx`
- **Mobile design**: `components/Layout/MobileBottomNav.tsx`
- **Settings panel**: `components/Settings/SettingsPanel.tsx`

### To Update Authentication
- **Login/logout**: `components/Layout/MainLayout.tsx` (Clerk integration)
- **User preferences**: `hooks/usePreferences.ts` and `stores/usePreferenceStore.ts`
- **Rate limiting**: `hooks/useQueryLimits.ts`

### To Add New Features
1. **Create component** in appropriate `components/` subdirectory
2. **Add types** to `src/types/` files
3. **Create hook** if complex state management needed
4. **Import and use** in parent component
5. **Add to routing** if it's a new page

## Common Issues & Troubleshooting

### Development Issues
- **"Module not found"**: Run `npm install` to install missing dependencies
- **TypeScript errors**: Check `src/types/` for missing type definitions
- **Build failures**: Check `package.json` scripts and dependencies

### Authentication Issues
- **Clerk not working**: Verify `REACT_APP_CLERK_PUBLISHABLE_KEY` in `.env.local`
- **Sign-in modal not opening**: Check `useQueryLimits.ts` and `MainLayout.tsx` connection
- **Preference sync issues**: Enable browser console to see API call logs

### UI/UX Issues
- **Mobile layout broken**: Check Tailwind responsive classes (`md:`, `lg:`)
- **Streaming not working**: Verify `streamingApi.ts` connection to backend
- **Messages not scrolling**: Check `ChatInterface.tsx` auto-scroll logic

### Performance Issues
- **Slow rendering**: Use React Developer Tools to profile components
- **Memory leaks**: Check for missing cleanup in `useEffect` hooks
- **Large bundle size**: Analyze with `npm run build` and bundle analyzer

## Deployment
- **Development**: http://localhost:3000
- **Production**: Vercel automatic deployment from GitHub
- **Environment**: Variables set in Vercel dashboard
- **Build command**: `npm run build` (CI=false for warnings as non-errors)

This frontend provides a modern, responsive chat interface optimized for credit card queries with enterprise authentication and real-time AI responses.
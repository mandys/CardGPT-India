# Card Configuration Centralization Plan

## Problem Analysis

### Current State
The application has **extensive hardcoding** of credit card information across both backend and frontend, making it difficult to add new cards or modify existing ones. The hardcoding affects:

### Backend Hardcoded References (27 locations)
- **API Configuration** (`backend/api/config.py`): 6 references
- **LLM Service** (`backend/services/llm.py`): 15+ references
- **Query Enhancer** (`backend/services/query_enhancer.py`): 8 references  
- **Vertex Retriever** (`backend/services/vertex_retriever.py`): 6 references
- **Chat API** (`backend/api/chat.py`): 2 references
- **Test files**: Multiple references

### Frontend Hardcoded References (15+ locations)
- **TypeScript Types** (`cardgpt-ui/src/types/index.ts`): CardFilter type
- **Settings Panel** (`cardgpt-ui/src/components/Settings/SettingsPanel.tsx`): supportedCards array
- **Landing Pages**: Multiple components with card lists
- **Chat Interface**: Sample queries with specific card names
- **Demo Components**: Hardcoded examples

## Solution Architecture

### 1. Centralized Configuration System
Create `config/available_cards.json` with comprehensive card metadata:

```json
{
  "version": "1.0.0",
  "last_updated": "2025-08-05",
  "supported_cards": [
    {
      "id": "axis_atlas",
      "display_name": "Axis Atlas",
      "full_name": "Axis Bank Atlas Credit Card",
      "jsonl_name": "Axis Bank Atlas Credit Card",
      "aliases": ["axis atlas", "atlas", "axis", "axis bank atlas"],
      "reward_currency": "EDGE Miles",
      "reward_format": "X EDGE Miles/₹100",
      "color_scheme": {
        "primary": "from-red-500 to-red-600",
        "secondary": "red"
      },
      "category_info": {
        "insurance": "excludes_completely",
        "education": "2 EDGE Miles per ₹100 with 1% surcharge"
      },
      "active": true
    }
  ]
}
```

### 2. Backend Configuration Service
Create `backend/services/card_config.py`:
- Load and cache card configuration
- Provide methods for card lookup, aliases, and metadata
- Handle card name mapping between display names and JSONL names

### 3. Frontend Configuration Hook
Create `cardgpt-ui/src/hooks/useCardConfig.ts`:
- Fetch card configuration from backend API
- Provide TypeScript-safe card data
- Cache configuration with React Query

### 4. Migration Strategy
1. **Phase 1**: Create centralized config and loading infrastructure
2. **Phase 2**: Refactor backend services to use config
3. **Phase 3**: Refactor frontend components to use config
4. **Phase 4**: Remove all hardcoded references
5. **Phase 5**: Test and validate

## Implementation Benefits

### Immediate Benefits
- **Single Source of Truth**: All card data in one place
- **Easy Card Addition**: Just add entry to JSON file
- **Consistent Naming**: Unified card names across system
- **Type Safety**: Generated TypeScript types from config

### Long-term Benefits
- **Scalability**: Easy to add dozens of new cards
- **Maintainability**: No hunting for hardcoded references
- **Flexibility**: Runtime card enabling/disabling
- **Testing**: Easy to create test configurations

## File Structure Changes
```
config/
├── available_cards.json          # Master card configuration
└── card_categories.json          # Category-specific configurations

backend/
├── services/
│   ├── card_config.py            # Card configuration service
│   └── ...
└── api/
    ├── cards.py                  # Card configuration API endpoint
    └── ...

cardgpt-ui/src/
├── hooks/
│   ├── useCardConfig.ts          # Card configuration hook
│   └── ...
├── types/
│   ├── cards.ts                  # Generated card types
│   └── ...
└── config/
    └── cardTypes.ts              # Type definitions
```

## Risk Mitigation
- **Gradual Migration**: Implement alongside existing system
- **Backward Compatibility**: Keep existing hardcoded fallbacks initially
- **Comprehensive Testing**: Validate all card-dependent functionality
- **Rollback Plan**: Git-based rollback if issues arise

This centralized approach will transform card management from scattered hardcoding to a maintainable, scalable configuration system.
# Adding a New Credit Card to CardGPT Framework

**Complete implementation guide for integrating new credit cards into the CardGPT system.**

## Overview

This guide documents the systematic process for adding new credit cards to the CardGPT framework, based on the successful integration of the American Express Platinum Travel Credit Card. The process involves data preparation, backend configuration, frontend integration, and LLM prompt updates.

## Prerequisites

- Credit card data in the standardized JSON schema
- Access to Google Cloud Vertex AI Search data store
- Backend and frontend development environment
- Understanding of CardGPT's RAG architecture

## Phase 1: Data Pipeline Integration

### 1.1 Create Card Data File

Create a new JSON file in `data/scraped-data/` following the standardized schema:

```bash
# Example: data/scraped-data/new-card-name.json
{
  "meta": {
    "bank": "Bank Name",
    "card": "Card Name",
    "rating": "4.0"
  },
  "eligibility": { ... },
  "fees": { ... },
  "welcome_benefits": { ... },
  "reward_points": { ... },
  "government_spending": { ... },
  "milestones": { ... },
  "redemption": { ... },
  "lounge_access": { ... },
  "discounts": { ... },
  "insurance": { ... },
  "concierge": [ ... ],
  "pros": [ ... ],
  "cons": [ ... ]
}
```

**Key Requirements:**
- Follow existing schema structure exactly
- Include all required sections
- Use consistent formatting and units (₹, percentages, etc.)
- Validate against existing cards for completeness

### 1.2 Update Transform Scripts

**Add aliases to `data/scraped-data/new_transform_to_jsonl.py`:**

```python
# In generate_card_aliases() function
alias_mappings = {
    # ... existing mappings ...
    'New Card Name': ['alias1', 'alias2', 'full name', 'bank alias']
}

# In normalize_card_name() function  
card_name_mapping = {
    # ... existing mappings ...
    'New Card Name': 'Full Standardized Card Name'
}
```

### 1.3 Generate JSONL Data

Create card-specific transform script for isolated processing:

```bash
# Create transform_newcard_only.py based on transform_amex_only.py
python transform_newcard_only.py

# Verify output
ls -la card_data_newcard.jsonl
```

**Expected output:**
- JSONL file with category-level chunks (typically 10-15 chunks per card)
- Base64 encoded content with proper metadata
- Consistent aliases and normalization

### 1.4 Upload to Vertex AI Search

```bash
# Upload JSONL to Google Cloud Storage
gsutil cp card_data_newcard.jsonl gs://your-bucket/

# Update Vertex AI Search data store via console
# - Import new documents
# - Verify successful indexing
# - Test search functionality
```

## Phase 2: Backend Configuration

### 2.1 Update Available Cards Configuration

Edit `config/available_cards.json` to add the new card entry:

```json
{
  "id": "bank_cardname",
  "display_name": "Short Display Name",
  "full_name": "Full Standardized Card Name",
  "jsonl_name": "Name Matching JSONL Content",
  "short_name": "Abbreviation",
  "bank": "Bank Name",
  "aliases": ["alias1", "alias2", "full name"],
  "reward_currency": "Points/Miles Type",
  "reward_format": "X Points per ₹Y",
  "color_scheme": {
    "primary": "from-color-500 to-color-600",
    "secondary": "color",
    "gradient": "from-color-500 to-color-600"
  },
  "category_info": {
    "insurance": {
      "status": "included|excluded|capped",
      "description": "Detailed earning/exclusion info"
    },
    "education": {
      "status": "included|excluded|capped", 
      "description": "Detailed earning/exclusion info"
    }
  },
  "milestones": {
    "annual": [
      {"threshold": 300000, "reward": 2500, "currency": "Points"},
      {"threshold": 750000, "reward": 5000, "currency": "Points"}
    ]
  },
  "travel_benefits": {
    "description": "Key travel features summary"
  },
  "active": true,
  "priority": 6
}
```

**Important considerations:**
- Use unique `id` following existing patterns
- Ensure `aliases` match transform script exactly
- Set appropriate `priority` (higher numbers appear later)
- Update `category_summaries` section to include new card

### 2.2 Update LLM System Prompts

Edit `backend/services/llm.py` to include new card milestone information:

```python
# In _create_system_prompt() method, update CALCULATION RULES
CALCULATION RULES:
- ALWAYS check milestones: 
  • Atlas: ₹3L→2500, ₹7.5L→2500, ₹15L→5000 EDGE Miles
  • Amex Platinum: ₹1.9L→15000, ₹4L→25000 MR Points + ₹10K Taj voucher
  • New Card: ₹XL→Y Points, ₹ZL→W Points + bonus
- Include welcome bonus: 2500 EDGE Miles (Atlas), 10000 MR Points (Amex), X Points (New Card)
```

## Phase 3: Frontend Integration

### 3.1 Update Landing Page

Edit `cardgpt-ui/src/components/Landing/LandingPage.tsx` to add the new card to `supportedCards` array:

```typescript
{
  name: 'Display Name',
  shortName: 'Short Name',
  bank: 'Bank Name',
  image: '/images/card-image.jpg',
  features: ['Feature 1', 'Feature 2', 'Feature 3'],
  welcomeBonus: 'Welcome Offer Details',
  annualFee: '₹X,XXX + GST',
  bgGradient: 'from-color-900 to-color-700',
  badge: 'Card Category',
  badgeColor: 'bg-color-500/20 text-color-300 border-color-500/30',
  network: 'VISA|MC|AMEX',
  networkBg: 'from-color-400 to-color-500',
  networkText: 'text-white|text-slate-900',
  query: 'Sample query for testing card functionality'
}
```

**Design considerations:**
- Use appropriate color gradients that match card branding
- Ensure features list is concise but compelling
- Test responsive layout with 5+ cards (triggers horizontal scroll)

### 3.2 Add Card Images

```bash
# Add card image to public directory
cp new-card-image.jpg cardgpt-ui/public/images/

# Ensure consistent image dimensions and quality
# Recommended: 400x250px, high quality JPEG
```

## Phase 4: Testing & Validation

### 4.1 Backend Testing

```bash
# Test backend configuration
cd backend
python -c "
from services.card_config import get_card_config
config = get_card_config()
cards = config.get_supported_cards()
print([card.get('display_name') for card in cards])
"

# Test LLM milestone integration
python -c "
from services.llm import LLMService
import os
llm = LLMService(os.getenv('GEMINI_API_KEY'))
# Test calculation query with new card
"
```

### 4.2 Frontend Testing

```bash
# Test frontend compilation
cd cardgpt-ui
npm run build

# Verify landing page renders correctly
npm start
# Check http://localhost:3000 for new card display
```

### 4.3 End-to-End Testing

**Test queries to validate integration:**

1. **Basic query**: "Tell me about [New Card] benefits"
2. **Calculation query**: "How many points would I earn on ₹2L spend with [New Card]?"
3. **Comparison query**: "Compare [New Card] vs Atlas for travel rewards"
4. **Milestone query**: "What are the milestone benefits for [New Card]?"

**Expected results:**
- Vertex AI Search retrieves relevant documents
- LLM correctly identifies card from aliases
- Calculations include proper milestone logic
- Responses are accurate and well-formatted

## Phase 5: Documentation Updates

### 5.1 Update README.md

```bash
# Add new card to supported cards section
## Supported Credit Cards

- **Axis Atlas**: Premium miles card (10X travel, ₹1.5L milestone)
- **ICICI EPM**: Emeralde Private Metal (6 points per ₹200, category caps)  
- **HSBC Premier**: Miles transfer and comprehensive travel benefits
- **HDFC Infinia**: Ultra-premium card (5 points per ₹150, luxury benefits)
- **Amex Platinum**: Travel rewards (1 MR per ₹50, milestone bonuses)
- **[New Card]**: [Brief description with key features]
```

### 5.2 Update CLAUDE.md

Add new card to recent improvements section and update file structure if needed.

## Troubleshooting Guide

### Common Issues

**1. JSONL Upload Fails**
- Verify file format and encoding (UTF-8)
- Check aliases match exactly between transform script and config
- Ensure Base64 encoding is correct

**2. Card Not Found in Queries**
- Verify aliases in both `new_transform_to_jsonl.py` and `available_cards.json`
- Check Vertex AI Search indexing completed successfully
- Test alias variations in isolation

**3. Calculation Errors**
- Verify milestone information in `llm.py` matches card data exactly
- Test calculation logic with known values
- Check for currency formatting consistency

**4. Frontend Display Issues**
- Verify image path and file existence
- Check color scheme classes are valid Tailwind CSS
- Test responsive behavior with multiple cards

### Validation Checklist

**Data Pipeline:**
- [ ] JSON schema matches existing cards exactly
- [ ] Transform script generates valid JSONL
- [ ] Vertex AI Search successfully indexes documents
- [ ] Search queries return relevant chunks

**Backend Configuration:**
- [ ] `available_cards.json` entry is complete and valid
- [ ] Aliases match transform script exactly
- [ ] Milestone information added to LLM prompts
- [ ] Backend tests pass without errors

**Frontend Integration:**
- [ ] Landing page displays new card correctly
- [ ] Card image loads and displays properly
- [ ] Responsive layout works with 5+ cards
- [ ] Sample query navigates to chat interface

**End-to-End Testing:**
- [ ] Basic queries return accurate information
- [ ] Calculation queries include milestone logic
- [ ] Comparison queries work correctly
- [ ] User preferences recognize new card

## Best Practices

1. **Schema Consistency**: Always follow the exact JSON schema of existing cards
2. **Comprehensive Testing**: Test all query types thoroughly before deployment
3. **Documentation**: Update all relevant documentation immediately
4. **Incremental Deployment**: Test in development environment first
5. **Rollback Plan**: Keep previous configuration accessible for quick rollback

## Performance Considerations

- **JSONL Size**: Aim for 10-15 chunks per card for optimal retrieval
- **Alias Optimization**: Include common user variations for better recall
- **Image Optimization**: Use appropriately sized images to maintain performance
- **Cache Invalidation**: Clear relevant caches after configuration updates

## Security Notes

- Never commit sensitive card data or API keys
- Validate all user inputs in card configuration
- Ensure proper access controls for configuration files
- Test for potential injection vulnerabilities in card names/aliases

---

**Example Implementation**: See the American Express Platinum Travel Credit Card integration (commit: [hash]) for a complete reference implementation following this guide.

**Last Updated**: August 2025  
**Framework Version**: CardGPT v2.0 with Supabase integration
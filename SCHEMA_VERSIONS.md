# Schema Versions

## v2.1 - Insurance Category Standardization (2025-08-02)

### Added
- **insurance category** to `spending_categories` section across all 4 cards
- Insurance earning rates, exclusions, caps, and MCC codes (6300, 5960)
- **9th FAQ entry** for insurance premium earning comparison

### Updated
- **JSONL chunk count**: 1055 chunks (up from 1023)
- **Category coverage**: 7 standardized categories (education, fuel, utility, rent, gold/jewellery, government/tax, insurance)
- **FAQ system**: 9 pre-built comparison answers

### Cards Affected
- **HDFC Infinia**: 5 points per ₹150, 5,000 points daily cap
- **HSBC Premier**: 3 points per ₹100, ₹1L monthly cap  
- **ICICI EPM**: 6 points per ₹200, 5,000 points per statement cycle cap
- **Axis Atlas**: Excluded (0% return)

---

## v2.0 - Infrastructure Improvements (2025-08-02)

### Added
- **Incremental update system** with 83% downtime reduction
- **FAQ system** with 8 pre-built comparison answers (85-95% confidence)
- **Versioning metadata** for all chunks (v2.0 format)
- **Change detection** with hash-based tracking

### Tools Added
- `incremental_update.py` - Smart delta generation system
- `generate_faq.py` - FAQ system generator
- Enhanced `transform_to_jsonl.py` with comprehensive metadata

---

## v1.5 - Category Standardization Complete (2025-08-01)

### Added
- **6 standardized categories**: education, fuel, utility, rent, gold/jewellery, government/tax
- **spending_categories section** with consistent schema across all cards
- **1023 chunks** (488% increase from initial ~173 chunks)

### Removed
- **Hardcoded responses** from query_enhancer.py (zero hardcoded responses)

### Schema Structure
```json
"spending_categories": {
  "category_name": {
    "earning_rate": "X points/miles per ₹Y",
    "earning_conditions": ["condition1", "condition2"],
    "exclusions": ["exclusion1", "exclusion2"],
    "surcharge": {
      "rate": "X%",
      "conditions": ["condition"],
      "cap": "₹X per transaction/month"
    },
    "monthly_cap": "₹X or X points",
    "statement_cycle_cap": "X points",
    "mcc_codes": ["1234", "5678"],
    "notes": "Additional information"
  }
}
```

---

## v1.0 - Initial Structure (2025-06-29)

### Base Schema
- Card information structure
- Rewards and fees data
- Basic chunking system (~173 chunks)
- Manual query enhancement
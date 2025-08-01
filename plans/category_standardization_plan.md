# Credit Card Category Standardization Plan

## 🎯 **Problem Statement**

**Current Issue**: The query "which card gives points on education spending?" requires hardcoded responses in `query_enhancer.py` (line 287-289) because category information is scattered inconsistently across JSON files, making RAG retrieval unreliable.

**Root Cause**: Category information (earning rates, exclusions, surcharges, caps) is fragmented across different sections of each card's JSON file, making it difficult for the LLM to find complete information in retrieved chunks.

## 📊 **Current State Analysis**

### Education Category - Current Data Distribution

#### HDFC Infinia (`hdfc-infinia.json`)
```json
// SCATTERED ACROSS MULTIPLE SECTIONS:
"accrual_exclusions": [
  "Education payments via third-party apps like CRED, Cheq, MobiKwik (w.e.f. 2024-09-01)"
],
"surcharge_fees": {
  "education": "1% via third-party apps, capped at ₹4,999 per transaction"
},
"rate_general": "5 Reward Points/₹150"
```
**Interpretation**: Earns 5 points/₹150 for direct education payments, excluded for third-party apps, 1% surcharge on apps.

#### Axis Atlas (`axis-atlas.json`)
```json
// ONLY SURCHARGE INFO:
"surcharge_fees": {
  "education": "1% via third-party apps"
},
"rate_general": "2 EDGE Miles/₹100",
"accrual_exclusions": [
  "Gold/ Jewellery, Rent, Wallet, Insurance, Fuel, Government Institution, Utilities, Telecom"
  // Education NOT mentioned in exclusions
]
```
**Interpretation**: Earns 2 miles/₹100 on education (not excluded), 1% surcharge via apps.

#### ICICI EPM (`icici-epm.json`)
```json
// SCATTERED ACROSS 3 SECTIONS:
"surcharge_fees": {
  "education": "1% fee on transaction amount for education payments made through third-party apps (w.e.f. Nov 15, 2024)"
},
"reward_capping": {
  "education": "1,000 Reward Points (MCC 8220, 8241, 8249, 8211, 8299, 8244, 8493, 8494, 7911)"
},
"rate_general": "6 ICICI Bank Reward Points on every ₹200 spent at all eligible retail transactions"
```
**Interpretation**: Earns 6 points/₹200 up to 1,000 points cap per cycle, 1% surcharge via apps.

#### HSBC Premier (`hsbc-premier.json`)
```json
// MOST ORGANIZED:
"rewards": {
  "education": "3 points per ₹100 (up to ₹1,00,000 monthly)"
},
"surcharge_fees": {
  "education": "Information not available"
}
```
**Interpretation**: Earns 3 points/₹100 up to ₹1L monthly spend, surcharge unknown.

## 🎯 **Target Categories to Standardize**

Based on user query patterns and existing data:

### High Priority Categories
- **education** - Currently problematic
- **fuel** - Complex exclusion/surcharge rules
- **utility** - Various caps and surcharges
- **rent** - Mostly excluded but has surcharges
- **government/tax** - Exclusion patterns
- **insurance** - Mixed earning/exclusion rules

### Medium Priority Categories  
- **travel/flight/hotel** - Already fairly well structured
- **dining** - Generally simple
- **grocery** - Simple with some caps

### Fees & Benefits (Lower Priority)
- **annual_fee/joining_fee** - Already structured
- **milestone** - Complex but less queried
- **welcome_benefit** - Already structured

## 🏗️ **Proposed Standardized Structure**

### Schema Design

Add a new `spending_categories` section to each card JSON:

```json
{
  "spending_categories": {
    "education": {
      "earning_rate": "5 Reward Points per ₹150",
      "earning_conditions": ["Direct payments to institutions", "Website payments"],
      "exclusions": ["Third-party apps like CRED, Cheq, MobiKwik"],
      "surcharge": {
        "rate": "1%",
        "conditions": ["Via third-party apps"],
        "cap": "₹4,999 per transaction"
      },
      "monthly_cap": null,
      "statement_cycle_cap": null,
      "mcc_codes": ["8220", "8241", "8249", "8211", "8299", "8244"],
      "notes": "Effective 2024-09-01 for third-party app exclusions"
    }
  }
}
```

### Field Definitions

- **earning_rate**: Exact rate in card-specific units (points/miles per currency)
- **earning_conditions**: Positive conditions when earning applies
- **exclusions**: Specific exclusions within the category  
- **surcharge**: Object with rate, conditions, and caps
- **monthly_cap**: Monthly earning limit (null if none)
- **statement_cycle_cap**: Per-cycle earning limit (null if none)
- **mcc_codes**: Relevant merchant category codes
- **notes**: Effective dates, special conditions

## 🔄 **Implementation Strategy**

### Phase 1: Single Card Proof of Concept
1. **Choose HDFC Infinia** (has most complex education data)
2. **Extract all education-related data** from current scattered locations
3. **Create standardized education section** 
4. **Test RAG retrieval** - does it find complete info in chunks?
5. **Remove hardcoded education logic** from query_enhancer.py
6. **Validate query**: "which card gives points on education spending?"

### Phase 2: Single Category Across All Cards  
1. **Standardize education across all 4 cards**
2. **Update transform_to_jsonl.py** to create category-specific chunks
3. **Test cross-card education queries**
4. **Measure improvement in answer quality**

### Phase 3: High Priority Categories
1. **Add fuel, utility, rent, government, insurance** using same structure
2. **Progressive testing and validation**
3. **Remove corresponding hardcoded logic**

### Phase 4: Complete Migration
1. **Migrate remaining categories**
2. **Comprehensive query testing**
3. **Performance validation**
4. **Documentation update**

## ❓ **Questions & Unknowns**

### Data Interpretation Questions
1. **HDFC Infinia education**: Does "Education payments via third-party apps" exclusion mean ALL education via apps is excluded, or just the reward earning (but still processes)?

2. **Axis Atlas education**: Since education is not in accrual_exclusions, does it definitely earn the general rate of 2 miles/₹100?

3. **HSBC Premier education surcharge**: The JSON says "Information not available" - should we:
   - Leave as null in standardized structure?
   - Research and update?
   - Mark as "unknown"?

4. **MCC Codes**: Should we standardize MCC codes across cards or keep card-specific ones as found in data?

### Technical Architecture Questions
1. **Chunk Strategy**: Should category info be:
   - Separate chunks per category per card?
   - Combined category chunks?
   - Mixed with existing structure?

2. **Backward Compatibility**: Should we:
   - Keep existing structure AND add new structure?
   - Migrate completely to new structure?
   - Gradual migration approach?

3. **Transform Script**: Should `transform_to_jsonl.py`:
   - Create category-specific chunk types?
   - Use special metadata for category chunks?
   - Maintain existing chunk types?

## 🧪 **Validation Criteria**

### Success Metrics
- **Accuracy**: "which card gives points on education spending?" returns complete, accurate info for all cards
- **Performance**: No increase in search latency
- **Maintainability**: Adding new categories requires only JSON updates
- **Completeness**: LLM has all context needed without hardcoded responses

### Test Queries
```
- "Which card gives points on education spending?"
- "Education spending rewards comparison" 
- "Does Atlas have education surcharge?"
- "ICICI EPM education spending cap"
- "HDFC Infinia education exclusions"
```

## 🚨 **Risks & Mitigation**

### High Risk
- **Data Loss**: Migrating scattered data might lose nuances
- **Mitigation**: Careful manual verification of each category migration

### Medium Risk  
- **Search Performance**: New structure might not chunk well
- **Mitigation**: Test chunking strategy thoroughly in Phase 1

### Low Risk
- **Query Regression**: Existing working queries might break
- **Mitigation**: Comprehensive testing with existing query set

## 📝 **Next Steps**

1. **Answer outstanding questions** (see Questions section)
2. **Approve overall approach** and schema design
3. **Begin Phase 1** with HDFC Infinia education category
4. **Create validation framework** for testing

---

**This plan prioritizes data integrity and careful migration over speed, ensuring we don't break existing functionality while solving the category standardization problem.**
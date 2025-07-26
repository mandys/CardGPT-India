# CardGPT New Card Addition Checklist

Complete step-by-step process for adding new credit cards to the CardGPT system.

## 📋 Overview

This checklist guides you through the entire process of adding a new credit card to CardGPT, from initial data collection to final testing and deployment.

**Estimated Time**: 2-4 hours per card  
**Prerequisites**: Access to card T&Cs, Google Cloud Console, development environment  
**Tools Required**: Python 3.8+, data validation framework, testing suite

---

## Phase 1: Preparation & Research

### 1.1 Data Collection ✅
- [ ] **Obtain official card documents**
  - [ ] Most Important Terms & Conditions (MITC) PDF
  - [ ] Fee structure documents
  - [ ] Welcome benefits brochure
  - [ ] Reward program details
  - [ ] Eligibility criteria

- [ ] **Research card details**
  - [ ] Official bank website information
  - [ ] Current promotional offers
  - [ ] Recent policy changes
  - [ ] Network-specific benefits

- [ ] **Verify card status**
  - [ ] Card is currently available for new applications
  - [ ] No major recent changes to T&Cs
  - [ ] Bank hasn't announced discontinuation

### 1.2 Environment Setup ✅
- [ ] **Check development environment**
  ```bash
  # Verify Python and dependencies
  python --version  # Should be 3.8+
  pip install pyyaml requests
  ```

- [ ] **Verify existing tools**
  - [ ] `plans/card_schema.yml` exists
  - [ ] `plans/data_validation.py` works
  - [ ] `plans/add_new_card.py` is executable
  - [ ] `plans/card_testing_framework.py` is ready

- [ ] **Backend connectivity**
  - [ ] Local backend running (`npm run dev` or equivalent)
  - [ ] Backend health check passes: `curl http://localhost:8000/api/health`

---

## Phase 2: Data Creation & Validation

### 2.1 Create Card JSON ✅
- [ ] **Generate unique card ID**
  - [ ] Format: `bank_cardname` (e.g., `hdfc_regalia`, `sbi_cashback`)
  - [ ] Use lowercase, underscores only
  - [ ] Check for conflicts with existing cards

- [ ] **Create JSON file structure**
  ```bash
  # Create new file
  cp data/template_card.json data/new_card_name.json
  # Or start from existing similar card
  ```

- [ ] **Fill required sections** (refer to `plans/card_schema.yml`)
  - [ ] `common_terms` - Use bank's standard terms
  - [ ] `card.id` - Unique identifier
  - [ ] `card.name` - Official card name
  - [ ] `card.bank` - Issuing bank
  - [ ] `card.category` - Primary category
  - [ ] `card.network` - Visa/Mastercard/Amex/RuPay
  - [ ] `card.fees` - All fee structures
  - [ ] `card.rewards` - Reward rates and value
  - [ ] `card.eligibility` - Age, income, residency

### 2.2 Data Quality Check ✅
- [ ] **Run validation framework**
  ```bash
  cd plans/
  python data_validation.py ../data/new_card_name.json
  ```

- [ ] **Review validation report**
  - [ ] Overall score ≥ 85%
  - [ ] Critical score = 100%
  - [ ] No critical errors
  - [ ] Address high-priority warnings

- [ ] **Fix validation issues**
  - [ ] Correct format errors
  - [ ] Add missing required fields
  - [ ] Verify data accuracy
  - [ ] Re-run validation until passing

### 2.3 Data Completeness ✅
- [ ] **Verify critical information**
  - [ ] All fees clearly specified
  - [ ] Reward rates with value per point
  - [ ] Eligibility criteria complete
  - [ ] Welcome benefits detailed

- [ ] **Check recommended sections**
  - [ ] Lounge access (if applicable)
  - [ ] Insurance benefits
  - [ ] Dining/travel benefits
  - [ ] Golf/entertainment perks

---

## Phase 3: Automated Addition Process

### 3.1 Dry Run Validation ✅
- [ ] **Test addition pipeline**
  ```bash
  cd plans/
  python add_new_card.py ../data/new_card_name.json --dry-run
  ```

- [ ] **Review dry run results**
  - [ ] Validation passes
  - [ ] No duplicate conflicts
  - [ ] All checks successful

### 3.2 Execute Addition ✅
- [ ] **Run automated pipeline**
  ```bash
  # Standard addition
  python add_new_card.py ../data/new_card_name.json
  
  # Or rebuild entire JSONL (recommended for first card)
  python add_new_card.py ../data/new_card_name.json --rebuild-all
  ```

- [ ] **Verify pipeline success**
  - [ ] Card file copied to data/ directory
  - [ ] JSONL file updated successfully
  - [ ] Backup created automatically
  - [ ] Addition report generated

### 3.3 Manual Verification ✅
- [ ] **Check data directory**
  ```bash
  ls -la data/  # Verify new JSON file exists
  ```

- [ ] **Verify JSONL content**
  ```bash
  tail -20 card_data.jsonl  # Check new entries
  grep "CardName" card_data.jsonl | grep "NewCardName"
  ```

- [ ] **Review addition report**
  - [ ] Check `reports/card_addition_report_*.md`
  - [ ] Note any warnings or recommendations

---

## Phase 4: Testing & Quality Assurance

### 4.1 Automated Testing ✅
- [ ] **Run basic test suite**
  ```bash
  cd plans/
  python card_testing_framework.py "New Card Name"
  ```

- [ ] **Run comprehensive tests**
  ```bash
  python card_testing_framework.py "New Card Name" --full-suite
  ```

- [ ] **Run comparison tests**
  ```bash
  python card_testing_framework.py "New Card Name" --compare-cards "Axis Atlas,HSBC Premier"
  ```

### 4.2 Manual Testing ✅
- [ ] **Test basic queries**
  - [ ] "What are the annual fees for [Card Name]?"
  - [ ] "What rewards do I get with [Card Name]?"
  - [ ] "What is the foreign transaction fee for [Card Name]?"

- [ ] **Test specific scenarios**
  - [ ] "Cash withdrawal charges [Card Name]"
  - [ ] "Welcome bonus [Card Name]"
  - [ ] "Lounge access with [Card Name]"

- [ ] **Test calculations**
  - [ ] "For ₹50,000 spend on [Card Name], how many points will I get?"
  - [ ] "₹1 lakh hotel spend on [Card Name] - calculate rewards"

- [ ] **Test comparisons**
  - [ ] "Compare [Card Name] vs Axis Atlas"
  - [ ] "Which has better rewards [Card Name] or HSBC Premier?"

### 4.3 Quality Assessment ✅
- [ ] **Review test results**
  - [ ] Overall test score ≥ 75%
  - [ ] Pass rate ≥ 80%
  - [ ] Response times < 5 seconds
  - [ ] Responses mention correct card name

- [ ] **Address test failures**
  - [ ] Investigate failed queries
  - [ ] Check data accuracy
  - [ ] Verify backend processing
  - [ ] Re-test after fixes

---

## Phase 5: Deployment & Integration

### 5.1 Google Cloud Upload ✅
- [ ] **Upload to Cloud Storage**
  ```bash
  # Upload updated JSONL
  gsutil cp card_data.jsonl gs://your-bucket-name/
  ```

- [ ] **Verify upload**
  ```bash
  gsutil ls -la gs://your-bucket-name/card_data.jsonl
  ```

### 5.2 Vertex AI Search Update ✅
- [ ] **Access Google Cloud Console**
  - [ ] Navigate to Vertex AI Search
  - [ ] Select your data store
  - [ ] Go to Data management

- [ ] **Refresh data store**
  - [ ] Import updated JSONL file
  - [ ] Wait for processing to complete
  - [ ] Verify new documents indexed

- [ ] **Test search integration**
  - [ ] Use Vertex AI Search console
  - [ ] Search for new card name
  - [ ] Verify relevant chunks returned

### 5.3 Production Testing ✅
- [ ] **Test on staging/production**
  - [ ] Deploy backend if needed
  - [ ] Test through actual frontend
  - [ ] Verify end-to-end functionality

- [ ] **Performance verification**
  - [ ] Query response times acceptable
  - [ ] No errors in logs
  - [ ] Search results relevant

---

## Phase 6: Documentation & Finalization

### 6.1 Update Documentation ✅
- [ ] **Update README.md**
  - [ ] Add new card to supported cards list
  - [ ] Update card count
  - [ ] Add any special notes

- [ ] **Update CLAUDE.md** (if needed)
  - [ ] Note any new patterns or requirements
  - [ ] Update troubleshooting sections

### 6.2 Create Card Documentation ✅
- [ ] **Document card-specific features**
  - [ ] Unique benefits or restrictions
  - [ ] Special calculation logic
  - [ ] Known limitations

- [ ] **Update test queries**
  - [ ] Add card-specific test cases
  - [ ] Update comparison baselines

### 6.3 Final Verification ✅
- [ ] **End-to-end test**
  - [ ] Complete user journey test
  - [ ] Verify all major features work
  - [ ] Check edge cases

- [ ] **Backup and version control**
  - [ ] Commit all changes to git
  - [ ] Tag release if significant
  - [ ] Update deployment records

---

## 🔧 Troubleshooting Guide

### Common Issues and Solutions

#### Validation Failures
**Issue**: Schema validation fails  
**Solution**: 
- Check `plans/card_schema.yml` for requirements
- Verify JSON syntax with online validator
- Ensure all required fields present

**Issue**: Low completeness score  
**Solution**:
- Add missing high-priority fields
- Fill in recommended sections
- Provide detailed information instead of placeholders

#### Pipeline Errors
**Issue**: File not found errors  
**Solution**:
- Verify file paths are correct
- Check working directory
- Ensure all dependencies installed

**Issue**: Backend connection fails  
**Solution**:
- Start local backend server
- Check port availability (8000)
- Verify API endpoints respond

#### Testing Issues
**Issue**: Tests fail with "card not found"  
**Solution**:
- Wait for Vertex AI indexing to complete
- Check JSONL upload successful
- Verify card name matching

**Issue**: Poor response quality  
**Solution**:
- Review card data for accuracy
- Add more detailed information
- Check for data format issues

#### Google Cloud Issues
**Issue**: Upload permissions denied  
**Solution**:
- Verify Google Cloud credentials
- Check bucket permissions
- Use correct project ID

**Issue**: Vertex AI not updating  
**Solution**:
- Force refresh data store
- Check file format compliance
- Verify data store configuration

---

## 📊 Quality Standards

### Minimum Requirements
- **Schema validation**: 100% critical fields, 85% overall score
- **Test coverage**: 80% pass rate, 75% overall quality score
- **Response time**: < 5 seconds average
- **Data accuracy**: All fees and rates current and correct

### Best Practices
- **Documentation**: Clear, detailed card information
- **Testing**: Test all major features and edge cases
- **Verification**: Manual review of automated results
- **Maintenance**: Regular updates for policy changes

---

## 📝 Checklist Summary

**Pre-Addition** (30 min):
- ✅ Collect official documents
- ✅ Set up development environment
- ✅ Verify tool availability

**Data Creation** (60-90 min):
- ✅ Create JSON with all required fields
- ✅ Pass schema validation (85%+ score)
- ✅ Verify data accuracy and completeness

**Automated Addition** (15 min):
- ✅ Run dry-run validation
- ✅ Execute addition pipeline
- ✅ Verify successful integration

**Testing** (30-45 min):
- ✅ Pass automated test suite (80%+ pass rate)
- ✅ Manual verification of key scenarios
- ✅ Quality assessment and fixes

**Deployment** (15-30 min):
- ✅ Upload to Google Cloud Storage
- ✅ Refresh Vertex AI Search data store
- ✅ Production testing

**Documentation** (15 min):
- ✅ Update README.md
- ✅ Create addition notes
- ✅ Final verification

**Total Time**: 2-4 hours depending on card complexity and data availability

---

## 🎯 Success Criteria

A card addition is considered successful when:

1. **Schema Compliance**: ≥85% completeness score, all critical fields present
2. **Pipeline Success**: Automated addition completes without errors
3. **Test Quality**: ≥80% test pass rate, ≥75% quality score
4. **Search Integration**: Card discoverable through Vertex AI Search
5. **Response Quality**: Accurate, complete answers to standard queries
6. **Documentation**: README.md updated, process documented

---

*Generated by CardGPT Automated Pipeline Framework*  
*Last Updated: July 2025*
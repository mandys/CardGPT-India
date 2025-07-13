# Credit Card Assistant Test Suite

Automated testing framework to prevent regressions and validate functionality.

## Quick Start

### 1. Validate Current System
```bash
# Quick validation (3 critical tests)
python tests/run_tests.py
```

### 2. Run Full Test Suite
```bash
# Full test suite with Gemini Flash (default)
python tests/test_runner.py

# Test with different models
python tests/test_runner.py gpt-4
python tests/test_runner.py gemini-1.5-pro
```

## Test Categories

### Critical Tests (Must Pass)
- **Milestone Calculation**: Cumulative milestone logic (₹7.5L = ₹3L + ₹7.5L bonuses)
- **Hotel Cap Logic**: Split calculations (₹2L@5x + excess@2x + milestones)

### Important Tests
- **Utility Spending**: Capping and surcharge calculations
- **Exclusions**: Fuel, rent, government payments
- **Insurance**: ICICI caps vs Axis exclusions
- **Education**: Category-specific caps and rates

## Test Structure

Each test includes:
- **Query**: User question to test
- **Expected Keywords**: Must appear in response
- **Expected Winner**: For comparison queries (optional)
- **Critical Flag**: If test failure should block changes

## Scoring

- **Keywords**: 60% weight (most important for calculations)
- **Content**: 25% weight (general correctness)
- **Winner**: 15% weight (comparison accuracy)

### Status Levels
- **PASSING**: ≥90% (critical) or ≥80% (normal)
- **PARTIAL**: ≥70% (critical) or ≥50% (normal) 
- **FAILING**: Below thresholds

## Development Workflow

### Before Making Changes
```bash
# Establish baseline
python tests/run_tests.py

# If critical tests fail, fix before proceeding
```

### After Making Changes
```bash
# Run full test suite
python tests/test_runner.py

# Check for regressions
# Fix any newly failing tests
```

### Before Committing
```bash
# Ensure all critical tests pass
python tests/run_tests.py
```

## Adding New Tests

Edit `tests/test_runner.py` and add to `_load_test_cases()`:

```python
{
    "category": "New Feature",
    "query": "Test question here",
    "expected_keywords": ["keyword1", "keyword2"],
    "expected_winner": "icici",  # optional
    "critical": True,  # if must pass
}
```

## Output Files

- **Test Reports**: `tests/test_report_[model]_[timestamp].txt`
- **Console Output**: Real-time status and summary

## Environment Setup

Ensure environment variables are set:
```bash
export OPENAI_API_KEY="your-key"
export GEMINI_API_KEY="your-key"  # optional but recommended
```

## Cost Tracking

Tests automatically track:
- Token usage per test
- Cost per model
- Total test suite cost

Typical costs:
- **Gemini Flash**: ~$0.005 for full suite
- **GPT-3.5**: ~$0.03 for full suite  
- **GPT-4**: ~$0.50 for full suite

## Best Practices

1. **Run quick validation before major changes**
2. **Add tests for new features**
3. **Mark calculation tests as critical**
4. **Use keyword validation for numerical results**
5. **Test with your target model (Gemini Flash default)**
#!/usr/bin/env python3
"""
CardGPT Data Validation Framework
Validates credit card JSON data against the standardized schema.

Usage:
    from data_validation import CardDataValidator
    
    validator = CardDataValidator()
    errors = validator.validate_structure(card_data)
    score, missing_critical, missing_medium = validator.check_completeness(card_data)
    issues = validator.validate_consistency(card_data)
"""

import json
import re
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass

@dataclass
class ValidationError:
    """Represents a validation error with context"""
    field_path: str
    error_type: str
    message: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    suggestion: Optional[str] = None

@dataclass
class CompletenessResult:
    """Results of completeness check"""
    overall_score: float
    critical_score: float
    high_score: float
    medium_score: float
    low_score: float
    missing_critical: List[str]
    missing_high: List[str]
    missing_medium: List[str]
    missing_low: List[str]

class CardDataValidator:
    """Comprehensive validation framework for credit card data"""
    
    def __init__(self, schema_path: str = "plans/card_schema.yml"):
        """Initialize validator with schema"""
        self.schema_path = Path(schema_path)
        self.schema = self._load_schema()
        self.patterns = self._compile_patterns()
    
    def _load_schema(self) -> Dict[str, Any]:
        """Load and parse the schema YAML file"""
        try:
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Schema file not found: {self.schema_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in schema file: {e}")
    
    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for validation"""
        patterns = {}
        
        # Currency patterns
        patterns['currency'] = re.compile(r'^₹[0-9,]+$')
        patterns['currency_with_gst'] = re.compile(r'^(₹[0-9,]+ \+ GST|₹[0-9,]+|Nil|Free)$')
        patterns['percentage'] = re.compile(r'^[0-9.]+%$')
        patterns['card_id'] = re.compile(r'^[a-z_]+$')
        patterns['date_yyyy_mm'] = re.compile(r'^[0-9]{4}-[0-9]{2}$')
        patterns['age_range'] = re.compile(r'^[0-9]+[–\-][0-9]+ years$')
        patterns['income'] = re.compile(r'^₹[0-9.]+[LM]\+?$')
        patterns['fee_with_min'] = re.compile(r'^[0-9.]+% \(min ₹[0-9,]+\)|₹[0-9,]+$')
        
        return patterns
    
    def validate_structure(self, card_data: Dict[str, Any]) -> List[ValidationError]:
        """Validate card data structure against schema"""
        errors = []
        
        # Check top-level structure
        errors.extend(self._validate_top_level_structure(card_data))
        
        # Validate common_terms section
        if 'common_terms' in card_data:
            errors.extend(self._validate_common_terms(card_data['common_terms']))
        
        # Validate card section
        if 'card' in card_data:
            errors.extend(self._validate_card_section(card_data['card']))
        
        return errors
    
    def _validate_top_level_structure(self, card_data: Dict[str, Any]) -> List[ValidationError]:
        """Validate top-level structure requirements"""
        errors = []
        
        required_sections = ['common_terms', 'card']
        for section in required_sections:
            if section not in card_data:
                errors.append(ValidationError(
                    field_path=section,
                    error_type='missing_required_section',
                    message=f"Required section '{section}' is missing",
                    severity='critical',
                    suggestion=f"Add '{section}' section to the JSON file"
                ))
            elif not isinstance(card_data[section], dict):
                errors.append(ValidationError(
                    field_path=section,
                    error_type='invalid_type',
                    message=f"Section '{section}' must be an object/dictionary",
                    severity='critical',
                    suggestion=f"Change '{section}' to be a JSON object with key-value pairs"
                ))
        
        return errors
    
    def _validate_common_terms(self, common_terms: Dict[str, Any]) -> List[ValidationError]:
        """Validate common_terms section"""
        errors = []
        
        required_sections = [
            'interest_free_grace_period',
            'minimum_amount_due_logic',
            'finance_charges',
            'surcharge_fees',
            'cash_withdrawal',
            'fuel_surcharge_waiver',
            'other_fees',
            'card_management_policies',
            'reward_points_policy'
        ]
        
        for section in required_sections:
            if section not in common_terms:
                errors.append(ValidationError(
                    field_path=f'common_terms.{section}',
                    error_type='missing_required_section',
                    message=f"Required common_terms section '{section}' is missing",
                    severity='high',
                    suggestion=f"Add '{section}' section to common_terms"
                ))
        
        # Validate specific subsections
        if 'finance_charges' in common_terms:
            errors.extend(self._validate_finance_charges(common_terms['finance_charges']))
        
        if 'cash_withdrawal' in common_terms:
            errors.extend(self._validate_cash_withdrawal(common_terms['cash_withdrawal']))
        
        return errors
    
    def _validate_finance_charges(self, finance_charges: Dict[str, Any]) -> List[ValidationError]:
        """Validate finance charges section"""
        errors = []
        
        required_fields = [
            'rate_per_month',
            'rate_per_annum',
            'cash_withdrawal_start',
            'applicability'
        ]
        
        for field in required_fields:
            if field not in finance_charges:
                errors.append(ValidationError(
                    field_path=f'common_terms.finance_charges.{field}',
                    error_type='missing_required_field',
                    message=f"Required field '{field}' is missing from finance_charges",
                    severity='high',
                    suggestion=f"Add '{field}' field to finance_charges section"
                ))
        
        # Validate percentage fields
        percentage_fields = ['rate_per_month', 'rate_per_annum']
        for field in percentage_fields:
            if field in finance_charges:
                value = str(finance_charges[field])
                if not self.patterns['percentage'].match(value):
                    errors.append(ValidationError(
                        field_path=f'common_terms.finance_charges.{field}',
                        error_type='invalid_format',
                        message=f"Field '{field}' must be in format 'X.X%', got '{value}'",
                        severity='medium',
                        suggestion=f"Change to format like '3.75%' or '45%'"
                    ))
        
        return errors
    
    def _validate_cash_withdrawal(self, cash_withdrawal: Dict[str, Any]) -> List[ValidationError]:
        """Validate cash withdrawal section"""
        errors = []
        
        required_fields = ['fee', 'limit']
        for field in required_fields:
            if field not in cash_withdrawal:
                errors.append(ValidationError(
                    field_path=f'common_terms.cash_withdrawal.{field}',
                    error_type='missing_required_field',
                    message=f"Required field '{field}' is missing from cash_withdrawal",
                    severity='high',
                    suggestion=f"Add '{field}' field to cash_withdrawal section"
                ))
        
        # Validate fee format
        if 'fee' in cash_withdrawal:
            fee_value = str(cash_withdrawal['fee'])
            if not self.patterns['fee_with_min'].match(fee_value):
                errors.append(ValidationError(
                    field_path='common_terms.cash_withdrawal.fee',
                    error_type='invalid_format',
                    message=f"Fee must be in format '2.5% (min ₹500)' or '₹500', got '{fee_value}'",
                    severity='medium',
                    suggestion="Use format like '2.5% (min ₹500)' or fixed amount like '₹500'"
                ))
        
        return errors
    
    def _validate_card_section(self, card: Dict[str, Any]) -> List[ValidationError]:
        """Validate card section"""
        errors = []
        
        # Validate identification fields
        errors.extend(self._validate_card_identification(card))
        
        # Validate fees section
        if 'fees' in card:
            errors.extend(self._validate_card_fees(card['fees']))
        else:
            errors.append(ValidationError(
                field_path='card.fees',
                error_type='missing_required_section',
                message="Required 'fees' section is missing from card",
                severity='critical',
                suggestion="Add 'fees' section with joining_fee, annual_fee, and foreign_currency_markup"
            ))
        
        # Validate rewards section
        if 'rewards' in card:
            errors.extend(self._validate_card_rewards(card['rewards']))
        else:
            errors.append(ValidationError(
                field_path='card.rewards',
                error_type='missing_required_section',
                message="Required 'rewards' section is missing from card",
                severity='critical',
                suggestion="Add 'rewards' section with rate_general and value_per_point"
            ))
        
        # Validate eligibility section
        if 'eligibility' in card:
            errors.extend(self._validate_card_eligibility(card['eligibility']))
        else:
            errors.append(ValidationError(
                field_path='card.eligibility',
                error_type='missing_required_section',
                message="Required 'eligibility' section is missing from card",
                severity='critical',
                suggestion="Add 'eligibility' section with age, residency, and income requirements"
            ))
        
        return errors
    
    def _validate_card_identification(self, card: Dict[str, Any]) -> List[ValidationError]:
        """Validate card identification fields"""
        errors = []
        
        required_fields = {
            'id': ('card_id', 'Card ID must be lowercase letters and underscores only'),
            'name': (None, 'Card name is required'),
            'bank': (None, 'Bank name is required'),
            'category': (None, 'Card category is required'),
            'network': (None, 'Card network is required')
        }
        
        # Valid enum values
        valid_categories = ['Travel', 'Cashback', 'Rewards', 'Premium', 'Entry-level', 'Co-branded']
        valid_networks = ['Visa', 'Mastercard', 'American Express', 'RuPay', 'Diners Club']
        
        for field, (pattern_name, description) in required_fields.items():
            if field not in card:
                errors.append(ValidationError(
                    field_path=f'card.{field}',
                    error_type='missing_required_field',
                    message=f"Required field '{field}' is missing",
                    severity='critical',
                    suggestion=description
                ))
            else:
                value = str(card[field])
                
                # Pattern validation
                if pattern_name and pattern_name in self.patterns:
                    if not self.patterns[pattern_name].match(value):
                        errors.append(ValidationError(
                            field_path=f'card.{field}',
                            error_type='invalid_format',
                            message=f"Field '{field}' format is invalid: '{value}'",
                            severity='medium',
                            suggestion=description
                        ))
                
                # Enum validation
                if field == 'category' and value not in valid_categories:
                    errors.append(ValidationError(
                        field_path=f'card.{field}',
                        error_type='invalid_enum_value',
                        message=f"Category '{value}' is not valid. Must be one of: {valid_categories}",
                        severity='medium',
                        suggestion=f"Use one of: {', '.join(valid_categories)}"
                    ))
                
                if field == 'network' and value not in valid_networks:
                    errors.append(ValidationError(
                        field_path=f'card.{field}',
                        error_type='invalid_enum_value',
                        message=f"Network '{value}' is not valid. Must be one of: {valid_networks}",
                        severity='medium',
                        suggestion=f"Use one of: {', '.join(valid_networks)}"
                    ))
        
        # Validate optional launch_date
        if 'launch_date' in card:
            launch_date = str(card['launch_date'])
            if not self.patterns['date_yyyy_mm'].match(launch_date):
                errors.append(ValidationError(
                    field_path='card.launch_date',
                    error_type='invalid_format',
                    message=f"Launch date '{launch_date}' must be in YYYY-MM format",
                    severity='low',
                    suggestion="Use format like '2022-12' for December 2022"
                ))
        
        return errors
    
    def _validate_card_fees(self, fees: Dict[str, Any]) -> List[ValidationError]:
        """Validate card fees section"""
        errors = []
        
        required_fee_fields = [
            'joining_fee',
            'annual_fee',
            'add_on_card_fee',
            'foreign_currency_markup'
        ]
        
        for field in required_fee_fields:
            if field not in fees:
                errors.append(ValidationError(
                    field_path=f'card.fees.{field}',
                    error_type='missing_required_field',
                    message=f"Required fee field '{field}' is missing",
                    severity='critical',
                    suggestion=f"Add '{field}' to fees section"
                ))
            else:
                value = str(fees[field])
                
                # Validate fee format
                if field in ['joining_fee', 'annual_fee', 'add_on_card_fee']:
                    if not self.patterns['currency_with_gst'].match(value):
                        errors.append(ValidationError(
                            field_path=f'card.fees.{field}',
                            error_type='invalid_format',
                            message=f"Fee '{field}' format invalid: '{value}'",
                            severity='medium',
                            suggestion="Use format like '₹5,000 + GST', '₹1,000', 'Nil', or 'Free'"
                        ))
                
                elif field == 'foreign_currency_markup':
                    if not self.patterns['percentage'].match(value):
                        errors.append(ValidationError(
                            field_path=f'card.fees.{field}',
                            error_type='invalid_format',
                            message=f"Foreign currency markup '{value}' must be percentage format",
                            severity='medium',
                            suggestion="Use format like '3.5%'"
                        ))
        
        return errors
    
    def _validate_card_rewards(self, rewards: Dict[str, Any]) -> List[ValidationError]:
        """Validate card rewards section"""
        errors = []
        
        required_fields = ['rate_general', 'value_per_point']
        for field in required_fields:
            if field not in rewards:
                errors.append(ValidationError(
                    field_path=f'card.rewards.{field}',
                    error_type='missing_required_field',
                    message=f"Required rewards field '{field}' is missing",
                    severity='critical',
                    suggestion=f"Add '{field}' to rewards section"
                ))
        
        # Validate boolean fields
        if 'non_encashable' in rewards:
            if not isinstance(rewards['non_encashable'], bool):
                errors.append(ValidationError(
                    field_path='card.rewards.non_encashable',
                    error_type='invalid_type',
                    message="Field 'non_encashable' must be boolean (true/false)",
                    severity='medium',
                    suggestion="Use true or false (without quotes)"
                ))
        
        return errors
    
    def _validate_card_eligibility(self, eligibility: Dict[str, Any]) -> List[ValidationError]:
        """Validate card eligibility section"""
        errors = []
        
        required_fields = ['age', 'residency', 'income']
        for field in required_fields:
            if field not in eligibility:
                errors.append(ValidationError(
                    field_path=f'card.eligibility.{field}',
                    error_type='missing_required_field',
                    message=f"Required eligibility field '{field}' is missing",
                    severity='critical',
                    suggestion=f"Add '{field}' to eligibility section"
                ))
        
        # Validate age format
        if 'age' in eligibility:
            age_value = str(eligibility['age'])
            if not self.patterns['age_range'].match(age_value):
                errors.append(ValidationError(
                    field_path='card.eligibility.age',
                    error_type='invalid_format',
                    message=f"Age range '{age_value}' must be in format 'X–Y years'",
                    severity='medium',
                    suggestion="Use format like '18–70 years'"
                ))
        
        # Validate income section
        if 'income' in eligibility:
            if not isinstance(eligibility['income'], dict):
                errors.append(ValidationError(
                    field_path='card.eligibility.income',
                    error_type='invalid_type',
                    message="Income must be an object with salaried and self_employed fields",
                    severity='critical',
                    suggestion="Change income to object format: {\"salaried\": \"₹12L+\", \"self_employed\": \"₹15L+\"}"
                ))
            else:
                income = eligibility['income']
                for income_type in ['salaried', 'self_employed']:
                    if income_type not in income:
                        errors.append(ValidationError(
                            field_path=f'card.eligibility.income.{income_type}',
                            error_type='missing_required_field',
                            message=f"Required income field '{income_type}' is missing",
                            severity='critical',
                            suggestion=f"Add '{income_type}' income requirement"
                        ))
                    else:
                        income_value = str(income[income_type])
                        if not self.patterns['income'].match(income_value):
                            errors.append(ValidationError(
                                field_path=f'card.eligibility.income.{income_type}',
                                error_type='invalid_format',
                                message=f"Income '{income_value}' must be in format '₹XL+' or '₹XM+'",
                                severity='medium',
                                suggestion="Use format like '₹12L+' or '₹1.5M+'"
                            ))
        
        return errors
    
    def check_completeness(self, card_data: Dict[str, Any]) -> CompletenessResult:
        """Check data completeness against schema requirements"""
        
        # Define field paths for each priority level
        critical_fields = [
            'card.fees.joining_fee',
            'card.fees.annual_fee',
            'card.fees.foreign_currency_markup',
            'card.rewards.rate_general',
            'card.rewards.value_per_point',
            'card.eligibility.age',
            'card.eligibility.income.salaried',
            'card.eligibility.income.self_employed'
        ]
        
        high_fields = [
            'card.welcome_benefits',
            'card.rewards.accrual_exclusions',
            'card.lounge_access',
            'common_terms.cash_withdrawal',
            'common_terms.fuel_surcharge_waiver'
        ]
        
        medium_fields = [
            'card.insurance',
            'card.dining_benefits',
            'card.tier_structure',
            'card.renewal_benefits',
            'card.miles_transfer'
        ]
        
        low_fields = [
            'card.golf_benefits',
            'card.bookmyshow',
            'card.concierge',
            'card.purchase_protection'
        ]
        
        # Calculate scores for each priority level
        critical_score, missing_critical = self._calculate_field_score(card_data, critical_fields)
        high_score, missing_high = self._calculate_field_score(card_data, high_fields)
        medium_score, missing_medium = self._calculate_field_score(card_data, medium_fields)
        low_score, missing_low = self._calculate_field_score(card_data, low_fields)
        
        # Calculate overall weighted score
        overall_score = (
            critical_score * 0.4 +
            high_score * 0.3 +
            medium_score * 0.2 +
            low_score * 0.1
        )
        
        return CompletenessResult(
            overall_score=overall_score,
            critical_score=critical_score,
            high_score=high_score,
            medium_score=medium_score,
            low_score=low_score,
            missing_critical=missing_critical,
            missing_high=missing_high,
            missing_medium=missing_medium,
            missing_low=missing_low
        )
    
    def _calculate_field_score(self, data: Dict[str, Any], field_paths: List[str]) -> Tuple[float, List[str]]:
        """Calculate score for a set of field paths"""
        if not field_paths:
            return 100.0, []
        
        present_count = 0
        missing_fields = []
        
        for field_path in field_paths:
            if self._field_exists_and_valid(data, field_path):
                present_count += 1
            else:
                missing_fields.append(field_path)
        
        score = (present_count / len(field_paths)) * 100
        return score, missing_fields
    
    def _field_exists_and_valid(self, data: Dict[str, Any], field_path: str) -> bool:
        """Check if a field exists and has valid data"""
        try:
            parts = field_path.split('.')
            current = data
            
            for part in parts:
                if not isinstance(current, dict) or part not in current:
                    return False
                current = current[part]
            
            # Check if the value is meaningful (not None, empty string, etc.)
            if current is None:
                return False
            if isinstance(current, str) and current.strip() == "":
                return False
            if isinstance(current, str) and current.lower() in ["information not available", "n/a", "na"]:
                return False
            
            return True
            
        except (KeyError, TypeError, AttributeError):
            return False
    
    def validate_consistency(self, card_data: Dict[str, Any]) -> List[ValidationError]:
        """Validate cross-reference consistency"""
        errors = []
        
        # Check fee consistency between common_terms and card sections
        errors.extend(self._validate_fee_consistency(card_data))
        
        # Check reward category consistency
        errors.extend(self._validate_reward_consistency(card_data))
        
        # Check network-specific benefit alignment
        errors.extend(self._validate_network_alignment(card_data))
        
        return errors
    
    def _validate_fee_consistency(self, card_data: Dict[str, Any]) -> List[ValidationError]:
        """Validate fee consistency between sections"""
        errors = []
        
        # This is a placeholder for fee consistency checks
        # Implementation would check for conflicts between common_terms and card-specific fees
        
        return errors
    
    def _validate_reward_consistency(self, card_data: Dict[str, Any]) -> List[ValidationError]:
        """Validate reward category consistency"""
        errors = []
        
        # Check if excluded categories don't conflict with special rates
        card = card_data.get('card', {})
        rewards = card.get('rewards', {})
        
        if 'accrual_exclusions' in rewards and isinstance(rewards['accrual_exclusions'], list):
            exclusions = [exc.lower() for exc in rewards['accrual_exclusions']]
            
            # Check for common conflicts
            if 'travel' in exclusions and 'travel' in rewards:
                if 'rate' in str(rewards.get('travel', '')).lower():
                    errors.append(ValidationError(
                        field_path='card.rewards.travel',
                        error_type='consistency_conflict',
                        message="Travel is excluded from accrual but has special travel rate defined",
                        severity='high',
                        suggestion="Either remove travel from exclusions or remove travel-specific rate"
                    ))
        
        return errors
    
    def _validate_network_alignment(self, card_data: Dict[str, Any]) -> List[ValidationError]:
        """Validate network-specific benefit alignment"""
        errors = []
        
        card = card_data.get('card', {})
        network = card.get('network', '').lower()
        
        # Check Visa Infinite expectations
        if 'visa infinite' in network:
            if 'lounge_access' not in card:
                errors.append(ValidationError(
                    field_path='card.lounge_access',
                    error_type='network_expectation',
                    message="Visa Infinite cards typically have premium lounge access",
                    severity='medium',
                    suggestion="Add lounge_access section if applicable"
                ))
        
        # Check American Express expectations
        if 'american express' in network or 'amex' in network:
            if 'concierge' not in card:
                errors.append(ValidationError(
                    field_path='card.concierge',
                    error_type='network_expectation',
                    message="American Express cards typically have concierge services",
                    severity='low',
                    suggestion="Add concierge section if applicable"
                ))
        
        return errors
    
    def generate_validation_report(self, card_data: Dict[str, Any]) -> str:
        """Generate comprehensive validation report"""
        # Structure validation
        structure_errors = self.validate_structure(card_data)
        
        # Completeness check
        completeness = self.check_completeness(card_data)
        
        # Consistency validation
        consistency_errors = self.validate_consistency(card_data)
        
        # Generate report
        report_lines = []
        report_lines.append("# Credit Card Data Validation Report")
        report_lines.append(f"**Card**: {card_data.get('card', {}).get('name', 'Unknown')}")
        report_lines.append("")
        
        # Overall score
        report_lines.append("## Overall Assessment")
        if completeness.overall_score >= 85 and not any(e.severity == 'critical' for e in structure_errors):
            report_lines.append("✅ **PASSED** - Card data meets quality standards")
        else:
            report_lines.append("❌ **FAILED** - Card data requires fixes before addition")
        report_lines.append("")
        
        # Completeness scores
        report_lines.append("## Completeness Analysis")
        report_lines.append(f"- **Overall Score**: {completeness.overall_score:.1f}%")
        report_lines.append(f"- **Critical Fields**: {completeness.critical_score:.1f}%")
        report_lines.append(f"- **High Priority**: {completeness.high_score:.1f}%")
        report_lines.append(f"- **Medium Priority**: {completeness.medium_score:.1f}%")
        report_lines.append(f"- **Low Priority**: {completeness.low_score:.1f}%")
        report_lines.append("")
        
        # Structure errors
        if structure_errors:
            report_lines.append("## Structure Validation Errors")
            for error in structure_errors:
                icon = "🚨" if error.severity == 'critical' else "⚠️" if error.severity == 'high' else "ℹ️"
                report_lines.append(f"{icon} **{error.field_path}**: {error.message}")
                if error.suggestion:
                    report_lines.append(f"   *Suggestion*: {error.suggestion}")
            report_lines.append("")
        
        # Missing fields
        if completeness.missing_critical:
            report_lines.append("## Missing Critical Fields")
            for field in completeness.missing_critical:
                report_lines.append(f"- {field}")
            report_lines.append("")
        
        # Consistency issues
        if consistency_errors:
            report_lines.append("## Consistency Issues")
            for error in consistency_errors:
                report_lines.append(f"⚠️ **{error.field_path}**: {error.message}")
                if error.suggestion:
                    report_lines.append(f"   *Suggestion*: {error.suggestion}")
            report_lines.append("")
        
        # Recommendations
        report_lines.append("## Recommendations")
        if completeness.overall_score < 85:
            report_lines.append("- **Improve Completeness**: Add missing fields to reach 85% threshold")
        
        critical_errors = [e for e in structure_errors if e.severity == 'critical']
        if critical_errors:
            report_lines.append("- **Fix Critical Errors**: Address all critical validation errors")
        
        if not completeness.missing_critical and completeness.overall_score >= 85 and not critical_errors:
            report_lines.append("- **Ready for Addition**: Data meets all requirements for adding to CardGPT")
        
        return "\\n".join(report_lines)

def main():
    """CLI interface for validation"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python data_validation.py <path_to_card_json>")
        sys.exit(1)
    
    card_file = Path(sys.argv[1])
    if not card_file.exists():
        print(f"Error: File {card_file} not found")
        sys.exit(1)
    
    try:
        with open(card_file, 'r', encoding='utf-8') as f:
            card_data = json.load(f)
        
        validator = CardDataValidator()
        report = validator.generate_validation_report(card_data)
        print(report)
        
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {card_file}: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
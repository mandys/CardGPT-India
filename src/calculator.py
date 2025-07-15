"""
Credit Card Reward Calculator (Data-Driven)
Handles complex calculations by reading rules directly from JSON data sources.
"""

from typing import Dict, Any
import json
from pathlib import Path
import re

# --- Data-Access Helper ---
def get_nested(data: Dict, path: str, default: Any = None) -> Any:
    """Safely get a value from a nested dictionary using dot notation."""
    keys = path.split('.')
    for key in keys:
        try:
            if isinstance(data, list):
                data = data[int(key)]
            else:
                data = data[key]
        except (KeyError, TypeError, IndexError):
            return default
    return data

# --- Parsing Helper ---
def parse_reward_rate(rate_str: str) -> Dict:
    """Parses a rate string like '2 EDGE Miles/₹100' into a structured dict."""
    match = re.search(r'(\d+)\s*.*₹(\d+)', rate_str)
    if match:
        return {'points': int(match.group(1)), 'per_spend': int(match.group(2))}
    return {'points': 0, 'per_spend': 1}  # Default to prevent division by zero

def parse_spend_string(spend_str: str) -> int:
    """Parse spend strings like '₹3L' or '₹4 lakh annual spend' into integer values."""
    if not spend_str:
        return 0
    
    # Remove currency symbols and clean up
    clean_str = re.sub(r'[₹,]', '', str(spend_str))
    
    # Handle lakh notation (both 'L' and 'lakh')
    if 'L' in clean_str or 'l' in clean_str or 'lakh' in clean_str.lower():
        # Extract the numeric part before 'lakh' or 'L'
        number_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:lakh|L|l)', clean_str, re.IGNORECASE)
        if number_match:
            base_value = float(number_match.group(1))
            return int(base_value * 100000)
    
    # Handle thousand notation
    if 'K' in clean_str or 'k' in clean_str or 'thousand' in clean_str.lower():
        number_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:thousand|K|k)', clean_str, re.IGNORECASE)
        if number_match:
            base_value = float(number_match.group(1))
            return int(base_value * 1000)
    
    # Try to extract any number
    number_match = re.search(r'(\d+(?:\.\d+)?)', clean_str)
    if number_match:
        return int(float(number_match.group(1)))
    
    return 0

class CreditCardCalculator:
    """
    (Refactored) Precise, data-driven calculator for credit card rewards.
    This class is now stateless and relies on the passed-in card_data.
    """
    
    def calculate_rewards(self, spend: int, card_data: Dict, category: str = 'general', period: str = 'annual') -> Dict:
        """
        Calculate rewards based on dynamic card data from JSON.
        
        Args:
            spend: Amount spent in rupees.
            card_data: The parsed JSON data for a single credit card.
            category: Spending category.
            period: Calculation period (annual, monthly).
            
        Returns:
            Dict with the calculation breakdown.
        """
        card_name = get_nested(card_data, 'card.name', 'Unknown Card')
        currency = 'points'  # Default currency
        if 'miles' in get_nested(card_data, 'card.rewards.rate_general', '').lower():
            currency = 'miles'

        result = {
            'card': card_name,
            'spend': spend,
            'category': category,
            'period': period,
            'base_rewards': 0,
            'milestone_bonus': 0,
            'total_rewards': 0,
            'surcharge': 0,
            'calculation_steps': [],
            'currency': currency
        }
        
        # Check exclusions from the JSON data
        exclusions = get_nested(card_data, 'card.rewards.accrual_exclusions', [])
        if category.lower() in [ex.lower() for ex in exclusions]:
            result['calculation_steps'].append(f"❌ {category.title()} is excluded from earning rewards")
            return result
        
        # Calculate base rewards
        base_rewards = self._calculate_base_rewards(spend, category, card_data)
        result['base_rewards'] = base_rewards['rewards']
        result['calculation_steps'].extend(base_rewards['steps'])
        
        # Calculate milestones from JSON (for annual periods)
        if period == 'annual':
            milestones = get_nested(card_data, 'card.milestones', [])
            if milestones:
                milestone_bonus = self._calculate_milestones(spend, milestones)
                result['milestone_bonus'] = milestone_bonus['bonus']
                result['calculation_steps'].extend(milestone_bonus['steps'])
        
        # Calculate surcharges from JSON
        surcharge_rules = get_nested(card_data, 'common_terms.surcharge_fees', {})
        if category in surcharge_rules:
            # Parse surcharge rate and threshold from JSON string
            rate_str = surcharge_rules[category]
            try:
                rate = float(re.findall(r"(\d+(?:\.\d+)?)%", rate_str)[0]) / 100
                threshold_match = re.search(r'₹([\d,]+)', rate_str)
                threshold = int(threshold_match.group(1).replace(',', '')) if threshold_match else 0
                
                surcharge_config = {'rate': rate, 'threshold': threshold}
                surcharge = self._calculate_surcharge(spend, surcharge_config)
                result['surcharge'] = surcharge['amount']
                result['calculation_steps'].extend(surcharge['steps'])
            except (IndexError, ValueError):
                result['calculation_steps'].append(f"⚠️ Could not parse surcharge rules for {category}")

        result['total_rewards'] = result['base_rewards'] + result['milestone_bonus']
        return result
    
    def _calculate_base_rewards(self, spend: int, category: str, card_data: Dict) -> Dict:
        """Calculate base rewards by reading rules directly from card_data."""
        steps = []
        
        # Specific logic for accelerated travel rewards on Axis Atlas
        if 'Atlas' in get_nested(card_data, 'card.name', '') and category in ['hotel', 'flight']:
            travel_config = get_nested(card_data, 'card.rewards.travel', {})
            monthly_cap_str = travel_config.get('monthly_cap', '0')
            monthly_cap = parse_spend_string(monthly_cap_str)
            
            accel_rate_info = parse_reward_rate(travel_config.get('rate', ''))
            base_rate_info = parse_reward_rate(get_nested(card_data, 'card.rewards.rate_general', ''))
            
            if spend <= monthly_cap:
                rewards = (spend // accel_rate_info['per_spend']) * accel_rate_info['points']
                steps.append(f"✅ {category.title()} spend ₹{spend:,} ≤ ₹{monthly_cap:,} cap")
                steps.append(f"📊 Accelerated Rate: ({spend:,} ÷ {accel_rate_info['per_spend']}) × {accel_rate_info['points']} = {rewards:,} miles")
            else:
                # Split calculation
                cap_rewards = (monthly_cap // accel_rate_info['per_spend']) * accel_rate_info['points']
                remaining_spend = spend - monthly_cap
                base_rewards_val = (remaining_spend // base_rate_info['per_spend']) * base_rate_info['points']
                rewards = cap_rewards + base_rewards_val
                
                steps.append(f"💰 First ₹{monthly_cap:,} (Accelerated): ({monthly_cap:,} ÷ {accel_rate_info['per_spend']}) × {accel_rate_info['points']} = {cap_rewards:,} miles")
                steps.append(f"💰 Remaining ₹{remaining_spend:,} (Base): ({remaining_spend:,} ÷ {base_rate_info['per_spend']}) × {base_rate_info['points']} = {base_rewards_val:,} miles")
                steps.append(f"📊 Total: {cap_rewards:,} + {base_rewards_val:,} = {rewards:,} miles")
            
            return {'rewards': rewards, 'steps': steps}

        # Logic for capped categories (like ICICI EPM)
        capping_rules = get_nested(card_data, 'card.rewards.capping_per_statement_cycle', {})
        if category in capping_rules:
            # Parse the max points from string like "1,000 Reward Points (MCC...)"
            cap_str = capping_rules[category]
            max_points_match = re.search(r'([\d,]+)\s*Reward Points', cap_str)
            max_points = int(max_points_match.group(1).replace(',', '')) if max_points_match else 0
            
            # Parse the earning rate from JSON
            earning_rate_str = get_nested(card_data, 'card.rewards.rate_general', '')
            if not earning_rate_str:
                earning_rate_str = get_nested(card_data, 'card.rewards.earning_rate', '')
            
            base_rate_info = parse_reward_rate(earning_rate_str)
            calculated_points = (spend // base_rate_info['per_spend']) * base_rate_info['points']
            rewards = min(calculated_points, max_points)
            
            steps.append(f"📊 Calculation: ({spend:,} ÷ {base_rate_info['per_spend']}) × {base_rate_info['points']} = {calculated_points:,} points")
            if calculated_points > max_points:
                steps.append(f"🔒 Capped at {max_points:,} points per cycle")
            else:
                steps.append(f"✅ Under cap limit of {max_points:,} points")

            return {'rewards': rewards, 'steps': steps}
            
        # Default base rate from JSON
        base_rate_str = get_nested(card_data, 'card.rewards.rate_general', '')
        if not base_rate_str:
            base_rate_str = get_nested(card_data, 'card.rewards.earning_rate', '')
        
        base_rate_info = parse_reward_rate(base_rate_str)
        rewards = (spend // base_rate_info['per_spend']) * base_rate_info['points']
        
        currency = 'points'
        if 'miles' in base_rate_str.lower():
            currency = 'miles'
        
        steps.append(f"📊 Base Rate: ({spend:,} ÷ {base_rate_info['per_spend']}) × {base_rate_info['points']} = {rewards:,} {currency}")
        
        return {'rewards': rewards, 'steps': steps}
    
    def _calculate_milestones(self, spend: int, milestones) -> Dict:
        """Calculate cumulative milestone bonuses from JSON (handles both list and dict formats)."""
        steps = []
        total_bonus = 0
        
        # Handle different milestone formats
        if isinstance(milestones, dict):
            # ICICI EPM format: dict with named milestones
            for milestone_name, milestone_data in milestones.items():
                if isinstance(milestone_data, dict):
                    # Check for spend thresholds
                    if 'spend_threshold_1st_voucher' in milestone_data:
                        threshold_str = milestone_data['spend_threshold_1st_voucher']
                        threshold = parse_spend_string(threshold_str)
                        if spend >= threshold:
                            value = milestone_data.get('value', milestone_name)
                            steps.append(f"   ₹{threshold:,} threshold: Unlocked '{value}'")
                    
                    if 'spend_threshold_2nd_voucher' in milestone_data:
                        threshold_str = milestone_data['spend_threshold_2nd_voucher']
                        threshold = parse_spend_string(threshold_str)
                        if spend >= threshold:
                            value = milestone_data.get('value', milestone_name)
                            steps.append(f"   ₹{threshold:,} threshold: Unlocked additional '{value}'")
        
        elif isinstance(milestones, list):
            # Axis Atlas format: list of milestone objects
            for milestone in milestones:
                threshold_str = milestone.get('spend', '0')
                threshold = parse_spend_string(threshold_str)
                
                if spend >= threshold:
                    bonus = milestone.get('miles', milestone.get('bonus', 0))
                    if isinstance(bonus, int):
                        total_bonus += bonus
                        steps.append(f"   ₹{threshold:,} threshold: +{bonus:,} bonus")
                    else:  # Handle text bonuses like "EaseMyTrip voucher"
                        steps.append(f"   ₹{threshold:,} threshold: Unlocked '{bonus}'")
        
        if steps:
            steps.insert(0, "🎯 **CUMULATIVE MILESTONES**:")
            if total_bonus > 0:
                steps.append(f"✅ Total numeric milestone bonus: {total_bonus:,}")
        else:
            steps.append(f"❌ No milestones reached (spend ₹{spend:,} below minimum threshold)")

        return {'bonus': total_bonus, 'steps': steps}
    
    def _calculate_surcharge(self, spend: int, surcharge_config: Dict) -> Dict:
        """Calculate surcharge fees"""
        steps = []
        threshold = surcharge_config['threshold']
        rate = surcharge_config['rate']
        
        if spend > threshold:
            surcharge_amount = (spend - threshold) * rate
            steps.append(f"💸 Surcharge: {rate*100}% on amount above ₹{threshold:,}")
            steps.append(f"📊 Calculation: {rate*100}% × (₹{spend:,} - ₹{threshold:,}) = ₹{surcharge_amount:,.0f}")
            return {'amount': surcharge_amount, 'steps': steps}
        else:
            steps.append(f"✅ No surcharge (₹{spend:,} ≤ ₹{threshold:,} threshold)")
            return {'amount': 0, 'steps': steps}

# --- UPDATED WRAPPER FUNCTION FOR LLM ---

def calculate_rewards(spend: int, card: str, category: str = 'general', period: str = 'annual') -> str:
    """
    (Refactored) Main function for LLM to call. It now loads the specific
    JSON file for the requested card.
    
    Example: calculate_rewards(750000, 'Axis Atlas', 'general', 'annual')
    """
    # Map card names to filenames
    card_filename_map = {
        'axis atlas': 'axis-atlas.json',
        'icici epm': 'icici-epm.json', 
        'hsbc premier': 'hsbc-premier.json'
    }
    
    card_key = card.lower()
    if card_key not in card_filename_map:
        return f"Error: Card '{card}' not supported. Available cards: {', '.join(card_filename_map.keys())}"
    
    card_filename = card_filename_map[card_key]
    card_path = Path("data") / card_filename
    
    if not card_path.exists():
        return f"Error: Card configuration file not found for {card} at {card_path}"
    
    try:
        with open(card_path, 'r', encoding='utf-8') as f:
            card_data = json.load(f)
    except Exception as e:
        return f"Error reading or parsing card data for {card}: {e}"

    calculator = CreditCardCalculator()
    # Pass the loaded JSON data directly to the calculator
    result = calculator.calculate_rewards(spend, card_data, category, period)
    
    if 'error' in result:
        return result['error']
    
    # Format the output string
    currency = result['currency']
    output = [
        f"💳 **{result['card']} - {result['category'].title()} Spending**",
        f"💰 Spend: ₹{result['spend']:,}",
        "",
        *result['calculation_steps'],  # Unpack the list of steps
        "",
        "📊 **SUMMARY:**",
        f"Base rewards: {result['base_rewards']:,} {currency}",
    ]
    
    if result['milestone_bonus'] > 0:
        output.append(f"Milestone bonus: +{result['milestone_bonus']:,} {currency}")
    
    output.append(f"**Total rewards: {result['total_rewards']:,} {currency}**")
    
    if result['surcharge'] > 0:
        output.append(f"Surcharge fee: -₹{result['surcharge']:,.0f}")
    
    return "\n".join(output)
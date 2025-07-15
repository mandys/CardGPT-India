"""
Credit Card Reward Calculator
Handles complex calculations with precise milestone and capping logic
"""

from typing import Dict, List, Tuple
import json

class CreditCardCalculator:
    """Precise calculator for credit card rewards with milestone and capping logic"""
    
    def __init__(self):
        # Load card configuration
        self.card_configs = self._load_card_configs()
    
    def _load_card_configs(self) -> Dict:
        """Load card configurations from data files"""
        configs = {}
        
        # Axis Atlas configuration
        configs['axis_atlas'] = {
            'base_rate': {'points_per_100': 2, 'currency': 'miles'},
            'accelerated_rates': {
                'hotel': {'points_per_100': 5, 'monthly_cap': 200000},
                'flight': {'points_per_100': 5, 'monthly_cap': 200000}  # Shared cap
            },
            'exclusions': ['government', 'rent', 'fuel', 'utility', 'insurance', 'wallet', 'jewellery'],
            'milestones': [
                {'threshold': 300000, 'bonus': 2500},
                {'threshold': 750000, 'bonus': 2500}, 
                {'threshold': 1500000, 'bonus': 5000}
            ],
            'surcharges': {
                'utility': {'rate': 0.01, 'threshold': 25000}
            }
        }
        
        # ICICI EPM configuration  
        configs['icici_epm'] = {
            'base_rate': {'points_per_200': 6, 'currency': 'points'},
            'exclusions': ['government', 'rent', 'fuel'],
            'caps': {
                'utility': {'points_per_200': 6, 'max_points': 1000},
                'education': {'points_per_200': 6, 'max_points': 1000},
                'insurance': {'points_per_200': 6, 'max_points': 5000},
                'grocery': {'points_per_200': 6, 'max_points': 1000}
            },
            'milestones': [
                {'threshold': 400000, 'bonus': 'EaseMyTrip ₹4000'},
                {'threshold': 800000, 'bonus': 'EaseMyTrip ₹8000'}
            ],
            'surcharges': {
                'utility': {'rate': 0.01, 'threshold': 50000},
                'fuel': {'rate': 0.01, 'threshold': 10000},
                'education': {'rate': 0.01, 'threshold': 0}
            }
        }
        
        # HSBC Premier configuration
        configs['hsbc_premier'] = {
            'base_rate': {'points_per_100': 3, 'currency': 'points'},
            'exclusions': ['fuel'],  # Based on JSON: only cash advances, fees, disputed transactions excluded
            'caps': {
                'utility': {'points_per_100': 3, 'max_monthly_spend': 100000},
                'tax_payment': {'points_per_100': 3, 'max_monthly_spend': 100000},
                'insurance': {'points_per_100': 3, 'max_monthly_spend': 100000},
                'education': {'points_per_100': 3, 'max_monthly_spend': 100000}  # Added education capping
            }
        }
        
        return configs
    
    def calculate_rewards(self, spend: int, card: str, category: str = 'general', period: str = 'annual') -> Dict:
        """
        Calculate rewards for a given spend amount
        
        Args:
            spend: Amount spent in rupees
            card: Card name (axis_atlas, icici_epm, hsbc_premier)
            category: Spending category (general, hotel, flight, utility, etc.)
            period: Calculation period (annual, monthly)
            
        Returns:
            Dict with calculation breakdown
        """
        card_key = card.lower().replace(' ', '_').replace('-', '_')
        if card_key not in self.card_configs:
            return {'error': f'Card {card} not supported'}
        
        config = self.card_configs[card_key]
        result = {
            'card': card,
            'spend': spend,
            'category': category,
            'period': period,
            'base_rewards': 0,
            'milestone_bonus': 0,
            'total_rewards': 0,
            'surcharge': 0,
            'calculation_steps': [],
            'currency': config.get('base_rate', {}).get('currency', 'points')
        }
        
        # Check exclusions
        if category in config.get('exclusions', []):
            result['calculation_steps'].append(f"❌ {category.title()} is excluded from earning rewards")
            return result
        
        # Calculate base rewards
        base_rewards = self._calculate_base_rewards(spend, card_key, category, config)
        result['base_rewards'] = base_rewards['rewards']
        result['calculation_steps'].extend(base_rewards['steps'])
        
        # Calculate milestones (for annual periods)
        if period == 'annual' and 'milestones' in config:
            milestone_bonus = self._calculate_milestones(spend, config['milestones'])
            result['milestone_bonus'] = milestone_bonus['bonus']
            result['calculation_steps'].extend(milestone_bonus['steps'])
        
        # Calculate surcharges
        if category in config.get('surcharges', {}):
            surcharge = self._calculate_surcharge(spend, config['surcharges'][category])
            result['surcharge'] = surcharge['amount']
            result['calculation_steps'].extend(surcharge['steps'])
        
        result['total_rewards'] = result['base_rewards'] + result['milestone_bonus']
        
        return result
    
    def _calculate_base_rewards(self, spend: int, card_key: str, category: str, config: Dict) -> Dict:
        """Calculate base rewards with proper rate and capping logic"""
        steps = []
        
        # Check for accelerated rates first (Axis Atlas hotels/flights)
        if card_key == 'axis_atlas' and category in ['hotel', 'flight']:
            accel_config = config['accelerated_rates'][category]
            monthly_cap = accel_config['monthly_cap']
            
            if spend <= monthly_cap:
                # Entire spend gets accelerated rate
                rewards = (spend // 100) * accel_config['points_per_100']
                steps.append(f"✅ {category.title()} spend ₹{spend:,} ≤ ₹{monthly_cap:,} cap")
                steps.append(f"📊 Calculation: ({spend:,} ÷ 100) × {accel_config['points_per_100']} = {rewards:,} miles")
            else:
                # Split calculation: cap amount at accelerated + remainder at base
                cap_rewards = (monthly_cap // 100) * accel_config['points_per_100']
                remaining_spend = spend - monthly_cap
                base_rewards = (remaining_spend // 100) * config['base_rate']['points_per_100']
                rewards = cap_rewards + base_rewards
                
                steps.append(f"💰 First ₹{monthly_cap:,}: ({monthly_cap:,} ÷ 100) × {accel_config['points_per_100']} = {cap_rewards:,} miles")
                steps.append(f"💰 Remaining ₹{remaining_spend:,}: ({remaining_spend:,} ÷ 100) × {config['base_rate']['points_per_100']} = {base_rewards:,} miles")
                steps.append(f"📊 Total: {cap_rewards:,} + {base_rewards:,} = {rewards:,} miles")
            
            return {'rewards': rewards, 'steps': steps}
        
        # Check for capped categories (ICICI EPM)
        if card_key == 'icici_epm' and category in config.get('caps', {}):
            cap_config = config['caps'][category]
            calculated_points = (spend // 200) * cap_config['points_per_200']
            max_points = cap_config['max_points']
            
            if calculated_points <= max_points:
                rewards = calculated_points
                steps.append(f"📊 Calculation: ({spend:,} ÷ 200) × {cap_config['points_per_200']} = {calculated_points:,} points")
                steps.append(f"✅ Under cap limit of {max_points:,} points")
            else:
                rewards = max_points
                steps.append(f"📊 Calculation: ({spend:,} ÷ 200) × {cap_config['points_per_200']} = {calculated_points:,} points")
                steps.append(f"🔒 Capped at {max_points:,} points per cycle")
            
            return {'rewards': rewards, 'steps': steps}
        
        # Default base rate calculation
        if card_key == 'icici_epm':
            rewards = (spend // 200) * config['base_rate']['points_per_200']
            steps.append(f"📊 Base rate: ({spend:,} ÷ 200) × {config['base_rate']['points_per_200']} = {rewards:,} points")
        else:
            rate = config['base_rate'].get('points_per_100', 0)
            rewards = (spend // 100) * rate
            steps.append(f"📊 Base rate: ({spend:,} ÷ 100) × {rate} = {rewards:,} {config['base_rate'].get('currency', 'points')}")
        
        return {'rewards': rewards, 'steps': steps}
    
    def _calculate_milestones(self, spend: int, milestones: List[Dict]) -> Dict:
        """Calculate cumulative milestone bonuses"""
        steps = []
        total_bonus = 0
        
        applicable_milestones = [m for m in milestones if spend >= m['threshold']]
        
        if applicable_milestones:
            steps.append("🎯 **CUMULATIVE MILESTONES**:")
            for milestone in applicable_milestones:
                if isinstance(milestone['bonus'], int):
                    total_bonus += milestone['bonus']
                    steps.append(f"   ₹{milestone['threshold']:,} threshold: +{milestone['bonus']:,} bonus")
                else:
                    steps.append(f"   ₹{milestone['threshold']:,} threshold: {milestone['bonus']}")
            
            if total_bonus > 0:
                steps.append(f"✅ Total milestone bonus: {total_bonus:,}")
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

# Usage example function for LLM integration
def calculate_rewards(spend: int, card: str, category: str = 'general', period: str = 'annual') -> str:
    """
    Function for LLM to call for precise reward calculations
    
    Example: calculate_rewards(750000, 'Axis Atlas', 'general', 'annual')
    """
    calculator = CreditCardCalculator()
    result = calculator.calculate_rewards(spend, card, category, period)
    
    if 'error' in result:
        return result['error']
    
    # Format output
    output = []
    output.append(f"💳 **{result['card'].title()} - {result['category'].title()} Spending**")
    output.append(f"💰 Spend: ₹{result['spend']:,}")
    output.append("")
    
    for step in result['calculation_steps']:
        output.append(step)
    
    output.append("")
    output.append(f"📊 **SUMMARY:**")
    output.append(f"Base rewards: {result['base_rewards']:,} {result['currency']}")
    if result['milestone_bonus'] > 0:
        output.append(f"Milestone bonus: +{result['milestone_bonus']:,} {result['currency']}")
    output.append(f"**Total rewards: {result['total_rewards']:,} {result['currency']}**")
    
    if result['surcharge'] > 0:
        output.append(f"Surcharge fee: ₹{result['surcharge']:,.0f}")
    
    return "\n".join(output)
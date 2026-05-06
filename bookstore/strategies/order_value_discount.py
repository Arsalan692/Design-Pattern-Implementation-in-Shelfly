"""
Order Value Discount Strategy
==============================

Implements tiered discount based on order value.
"""

from decimal import Decimal
from typing import Dict, Any

from .discount_strategy import DiscountStrategy


class OrderValueDiscountStrategy(DiscountStrategy):
    """
    Strategy for applying automatic discounts based on order value.
    
    Discount tiers are read from ConfigManager (Singleton Pattern)
    so that changing configuration in one place updates all calculations.
    
    Default Tiers:
        - Orders >= Rs. 5,000: 15% off
        - Orders >= Rs. 2,000: 10% off
        - Orders >= Rs. 1,000: 5% off
        - Orders < Rs. 1,000: No discount
    
    Context Requirements:
        - None (only needs subtotal)
    """
    
    # Fallback discount tiers if ConfigManager is unavailable
    _DEFAULT_TIERS = [
        (Decimal('5000.00'), Decimal('15')),
        (Decimal('2000.00'), Decimal('10')),
        (Decimal('1000.00'), Decimal('5')),
    ]
    
    def _get_discount_tiers(self):
        """
        Get discount tiers from ConfigManager (Singleton).
        Falls back to hardcoded defaults if ConfigManager is unavailable.
        
        Returns:
            list: List of (min_amount, percentage) tuples, sorted descending
        """
        try:
            from ..managers.config_manager import ConfigManager
            config = ConfigManager()
            tiers_config = config.get_order_value_tiers()
            if tiers_config:
                return [
                    (tier['min_amount'], tier['percentage'])
                    for tier in tiers_config
                ]
        except Exception:
            pass
        
        return self._DEFAULT_TIERS
    
    def calculate_discount(self, subtotal: Decimal, context: Dict[str, Any]) -> Decimal:
        """
        Calculate order value discount based on tiered structure.
        
        Args:
            subtotal: Order/cart subtotal
            context: Not used for this strategy
        
        Returns:
            Decimal: Discount amount based on applicable tier
        """
        if not self.is_applicable(context):
            return Decimal('0.00')
        
        # Find applicable tier from ConfigManager
        for min_amount, discount_percentage in self._get_discount_tiers():
            if subtotal >= min_amount:
                discount = (subtotal * discount_percentage) / Decimal('100')
                return discount.quantize(Decimal('0.01'))
        
        # No tier applicable
        return Decimal('0.00')
    
    def get_description(self, discount_amount: Decimal) -> str:
        """
        Get order value discount description.
        
        Returns:
            str: Description like "Order Value Discount (15%): Rs. 750.00 off"
        """
        return f"Order Value Discount: Rs. {discount_amount:.2f} off"
    
    def is_applicable(self, context: Dict[str, Any]) -> bool:
        """
        Order value discount is applicable when subtotal is provided.
        The actual tier check happens in calculate_discount.
        
        Args:
            context: Not used
        
        Returns:
            bool: True (tier matching is done in calculate_discount)
        """
        return True
    
    def get_priority(self) -> int:
        """
        Order value discounts have medium priority.
        
        Returns:
            int: Priority 50 (medium priority)
        """
        return 50
    
    def get_applicable_tier(self, subtotal: Decimal) -> tuple:
        """
        Get the applicable discount tier for a given subtotal.
        
        Args:
            subtotal: Order/cart subtotal
        
        Returns:
            tuple: (min_amount, discount_percentage) or (None, None)
        """
        for min_amount, discount_percentage in self._get_discount_tiers():
            if subtotal >= min_amount:
                return (min_amount, discount_percentage)
        
        return (None, None)
    
    def get_tier_description(self, subtotal: Decimal) -> str:
        """
        Get a description of the applicable tier.
        
        Args:
            subtotal: Order/cart subtotal
        
        Returns:
            str: Description like "15% off (orders >= Rs. 5,000)"
        """
        for min_amount, discount_percentage in self._get_discount_tiers():
            if subtotal >= min_amount:
                return f"{discount_percentage}% off (orders >= Rs. {min_amount:,.2f})"
        
        return "No discount"
    
    @staticmethod
    def get_next_tier_info(subtotal: Decimal) -> Dict[str, Any]:
        """
        Get information about the next discount tier.
        
        Useful for showing customers how much more they need to spend
        to reach the next discount level.
        
        Args:
            subtotal: Current order/cart subtotal
        
        Returns:
            dict: {
                'next_tier_amount': Decimal or None,
                'next_tier_percentage': Decimal or None,
                'amount_needed': Decimal or None,
                'has_next_tier': bool
            }
        """
        # Create instance to get tiers
        instance = OrderValueDiscountStrategy()
        tiers = instance._get_discount_tiers()
        current_tier_index = None
        
        # Find current tier
        for i, (min_amount, _) in enumerate(tiers):
            if subtotal >= min_amount:
                current_tier_index = i
                break
        
        # Check if there's a higher tier
        if current_tier_index is None:
            # Not in any tier, show the lowest tier
            if tiers:
                lowest_tier = tiers[-1]
                return {
                    'next_tier_amount': lowest_tier[0],
                    'next_tier_percentage': lowest_tier[1],
                    'amount_needed': lowest_tier[0] - subtotal,
                    'has_next_tier': True
                }
        elif current_tier_index > 0:
            # There's a higher tier
            next_tier = tiers[current_tier_index - 1]
            return {
                'next_tier_amount': next_tier[0],
                'next_tier_percentage': next_tier[1],
                'amount_needed': next_tier[0] - subtotal,
                'has_next_tier': True
            }
        
        # Already at highest tier
        return {
            'next_tier_amount': None,
            'next_tier_percentage': None,
            'amount_needed': None,
            'has_next_tier': False
        }

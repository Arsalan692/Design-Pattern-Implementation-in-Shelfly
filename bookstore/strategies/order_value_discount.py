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
    
    Discount Tiers (configurable):
        - Orders >= Rs. 5,000: 15% off
        - Orders >= Rs. 2,000: 10% off
        - Orders >= Rs. 1,000: 5% off
        - Orders < Rs. 1,000: No discount
    
    This replaces the hardcoded logic previously in Cart and Order models.
    
    Context Requirements:
        - None (only needs subtotal)
    """
    
    # Discount tiers: (minimum_amount, discount_percentage)
    # Sorted in descending order for efficient lookup
    DISCOUNT_TIERS = [
        (Decimal('5000.00'), Decimal('15')),  # 15% off for orders >= 5000
        (Decimal('2000.00'), Decimal('10')),  # 10% off for orders >= 2000
        (Decimal('1000.00'), Decimal('5')),   # 5% off for orders >= 1000
    ]
    
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
        
        # Find applicable tier
        for min_amount, discount_percentage in self.DISCOUNT_TIERS:
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
        Order value discount is always applicable.
        
        Args:
            context: Not used
        
        Returns:
            bool: Always True
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
        for min_amount, discount_percentage in self.DISCOUNT_TIERS:
            if subtotal >= min_amount:
                return (min_amount, discount_percentage)
        
        return (None, None)
    
    @classmethod
    def get_tier_description(cls, subtotal: Decimal) -> str:
        """
        Get a description of the applicable tier.
        
        Args:
            subtotal: Order/cart subtotal
        
        Returns:
            str: Description like "15% off (orders >= Rs. 5,000)"
        """
        for min_amount, discount_percentage in cls.DISCOUNT_TIERS:
            if subtotal >= min_amount:
                return f"{discount_percentage}% off (orders >= Rs. {min_amount:,.2f})"
        
        return "No discount"
    
    @classmethod
    def get_next_tier_info(cls, subtotal: Decimal) -> Dict[str, Any]:
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
        current_tier_index = None
        
        # Find current tier
        for i, (min_amount, _) in enumerate(cls.DISCOUNT_TIERS):
            if subtotal >= min_amount:
                current_tier_index = i
                break
        
        # Check if there's a higher tier
        if current_tier_index is None:
            # Not in any tier, show the lowest tier
            if cls.DISCOUNT_TIERS:
                lowest_tier = cls.DISCOUNT_TIERS[-1]
                return {
                    'next_tier_amount': lowest_tier[0],
                    'next_tier_percentage': lowest_tier[1],
                    'amount_needed': lowest_tier[0] - subtotal,
                    'has_next_tier': True
                }
        elif current_tier_index > 0:
            # There's a higher tier
            next_tier = cls.DISCOUNT_TIERS[current_tier_index - 1]
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

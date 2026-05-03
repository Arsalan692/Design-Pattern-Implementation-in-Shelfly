"""
Coupon Discount Strategy
========================

Implements discount calculation for coupon codes.
"""

from decimal import Decimal
from typing import Dict, Any
from django.utils import timezone

from .discount_strategy import DiscountStrategy


class CouponDiscountStrategy(DiscountStrategy):
    """
    Strategy for applying coupon-based discounts.
    
    Supports:
        - Fixed amount coupons (e.g., Rs. 500 off)
        - Percentage coupons (e.g., 20% off)
        - Minimum purchase requirements
        - Expiry date validation
        - Usage limit validation
    
    Context Requirements:
        - 'coupon': Coupon model instance (or None)
    """
    
    def calculate_discount(self, subtotal: Decimal, context: Dict[str, Any]) -> Decimal:
        """
        Calculate coupon discount amount.
        
        Args:
            subtotal: Order/cart subtotal
            context: Must contain 'coupon' key with Coupon instance
        
        Returns:
            Decimal: Discount amount (0 if coupon invalid or not applicable)
        """
        coupon = context.get('coupon')
        
        if not coupon:
            return Decimal('0.00')
        
        # Check if coupon is applicable
        if not self.is_applicable(context):
            return Decimal('0.00')
        
        # Check minimum purchase requirement
        if subtotal < coupon.min_purchase:
            return Decimal('0.00')
        
        # Calculate discount based on type
        if coupon.discount_type == 'fixed':
            # Fixed amount discount (cannot exceed subtotal)
            return min(coupon.discount_value, subtotal)
        
        elif coupon.discount_type == 'percentage':
            # Percentage discount
            discount = (subtotal * coupon.discount_value) / Decimal('100')
            return discount.quantize(Decimal('0.01'))
        
        return Decimal('0.00')
    
    def get_description(self, discount_amount: Decimal) -> str:
        """
        Get coupon discount description.
        
        Returns:
            str: Description like "Coupon SAVE20: Rs. 500.00 off"
        """
        return f"Coupon Discount: Rs. {discount_amount:.2f} off"
    
    def is_applicable(self, context: Dict[str, Any]) -> bool:
        """
        Check if coupon can be applied.
        
        Validates:
            - Coupon exists
            - Coupon is active
            - Not expired
            - Usage limit not reached
        
        Args:
            context: Must contain 'coupon' key
        
        Returns:
            bool: True if coupon is valid and can be applied
        """
        coupon = context.get('coupon')
        
        if not coupon:
            return False
        
        # Check if coupon is active
        if not coupon.is_active:
            return False
        
        # Check expiry date
        now = timezone.now()
        if now > coupon.expiry_date:
            return False
        
        # Check usage limit
        if coupon.current_usage >= coupon.max_usage:
            return False
        
        return True
    
    def get_priority(self) -> int:
        """
        Coupon discounts have high priority (applied first).
        
        Returns:
            int: Priority 10 (high priority)
        """
        return 10
    
    def get_coupon_code(self, context: Dict[str, Any]) -> str:
        """
        Get the coupon code from context.
        
        Args:
            context: Context containing coupon
        
        Returns:
            str: Coupon code or empty string
        """
        coupon = context.get('coupon')
        return coupon.code if coupon else ""

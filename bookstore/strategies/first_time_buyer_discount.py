"""
First-Time Buyer Discount Strategy
===================================

Implements discount for first-time customers.
"""

from decimal import Decimal
from typing import Dict, Any

from .discount_strategy import DiscountStrategy


class FirstTimeBuyerDiscountStrategy(DiscountStrategy):
    """
    Strategy for applying first-time buyer discount.
    
    Discount percentage is read from ConfigManager (Singleton Pattern).
    Default: 15% off entire order for first-time buyers.
    
    This discount is only applied once per customer.
    After the first order, the customer's is_first_time_buyer flag
    is set to False.
    
    Context Requirements:
        - 'customer': Customer model instance
    """
    
    # Fallback discount percentage if ConfigManager is unavailable
    _DEFAULT_PERCENTAGE = Decimal('15')
    
    @property
    def DISCOUNT_PERCENTAGE(self):
        """Get discount percentage from ConfigManager or use default."""
        try:
            from ..managers.config_manager import ConfigManager
            config = ConfigManager()
            return config.get_first_time_buyer_discount()
        except Exception:
            return self._DEFAULT_PERCENTAGE
    
    def calculate_discount(self, subtotal: Decimal, context: Dict[str, Any]) -> Decimal:
        """
        Calculate first-time buyer discount.
        
        Args:
            subtotal: Order/cart subtotal
            context: Must contain 'customer' key with Customer instance
        
        Returns:
            Decimal: Discount if customer is first-time buyer, else 0
        """
        if not self.is_applicable(context):
            return Decimal('0.00')
        
        # Calculate discount using ConfigManager percentage
        discount = (subtotal * self.DISCOUNT_PERCENTAGE) / Decimal('100')
        return discount.quantize(Decimal('0.01'))
    
    def get_description(self, discount_amount: Decimal) -> str:
        """
        Get first-time buyer discount description.
        
        Returns:
            str: Description like "First-Time Buyer (15%): Rs. 300.00 off"
        """
        return f"First-Time Buyer Discount ({self.DISCOUNT_PERCENTAGE}%): Rs. {discount_amount:.2f} off"
    
    def is_applicable(self, context: Dict[str, Any]) -> bool:
        """
        Check if customer is eligible for first-time buyer discount.
        
        Args:
            context: Must contain 'customer' key
        
        Returns:
            bool: True if customer is first-time buyer
        """
        customer = context.get('customer')
        
        if not customer:
            return False
        
        # Check if customer is first-time buyer
        return customer.is_first_time_buyer
    
    def get_priority(self) -> int:
        """
        First-time buyer discounts have low priority (applied last).
        
        This ensures other discounts are calculated first.
        
        Returns:
            int: Priority 90 (low priority)
        """
        return 90
    
    @classmethod
    def get_discount_percentage(cls) -> Decimal:
        """
        Get the first-time buyer discount percentage.
        
        Returns:
            Decimal: Discount percentage (15)
        """
        return cls.DISCOUNT_PERCENTAGE
    
    @classmethod
    def get_welcome_message(cls) -> str:
        """
        Get a welcome message for first-time buyers.
        
        Returns:
            str: Welcome message with discount info
        """
        return f"Welcome! Enjoy {cls.DISCOUNT_PERCENTAGE}% off your first order!"

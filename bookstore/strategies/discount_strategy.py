"""
Base Discount Strategy Interface
=================================

Abstract base class defining the interface for all discount strategies.
"""

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict, Any


class DiscountStrategy(ABC):
    """
    Abstract base class for discount calculation strategies.
    
    This follows the Strategy Pattern, allowing different discount
    algorithms to be used interchangeably.
    
    Each concrete strategy must implement:
        - calculate_discount(): Returns the discount amount
        - get_description(): Returns human-readable description
        - is_applicable(): Checks if discount can be applied
    """
    
    @abstractmethod
    def calculate_discount(self, subtotal: Decimal, context: Dict[str, Any]) -> Decimal:
        """
        Calculate the discount amount based on the strategy.
        
        Args:
            subtotal (Decimal): The order/cart subtotal before discounts
            context (Dict): Additional context data needed for calculation
                           (e.g., customer info, coupon, cart items)
        
        Returns:
            Decimal: The discount amount (always positive or zero)
        """
        pass
    
    @abstractmethod
    def get_description(self, discount_amount: Decimal) -> str:
        """
        Get a human-readable description of the discount.
        
        Args:
            discount_amount (Decimal): The calculated discount amount
        
        Returns:
            str: Description like "Coupon SAVE20: Rs. 500 off"
        """
        pass
    
    @abstractmethod
    def is_applicable(self, context: Dict[str, Any]) -> bool:
        """
        Check if this discount strategy can be applied.
        
        Args:
            context (Dict): Context data for validation
        
        Returns:
            bool: True if discount can be applied, False otherwise
        """
        pass
    
    def get_priority(self) -> int:
        """
        Get the priority of this discount strategy.
        Lower numbers = higher priority (applied first).
        
        Default priority is 100. Override in subclasses if needed.
        
        Returns:
            int: Priority value
        """
        return 100

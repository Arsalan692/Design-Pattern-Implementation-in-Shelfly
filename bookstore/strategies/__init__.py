"""
Discount Strategy Pattern Implementation
=========================================

This module implements the Strategy Pattern for flexible discount calculations.

Design Pattern: Strategy (Behavioral Pattern)
Problem Solved: Eliminates hardcoded discount logic and code duplication
Benefits:
    - Easy to add new discount types without modifying existing code
    - Each strategy is independently testable
    - Follows Open/Closed Principle
    - Eliminates code duplication between Cart and Order models
"""

from .discount_strategy import DiscountStrategy
from .coupon_discount import CouponDiscountStrategy
from .order_value_discount import OrderValueDiscountStrategy
from .first_time_buyer_discount import FirstTimeBuyerDiscountStrategy
from .discount_context import DiscountContext

__all__ = [
    'DiscountStrategy',
    'CouponDiscountStrategy',
    'OrderValueDiscountStrategy',
    'FirstTimeBuyerDiscountStrategy',
    'DiscountContext',
]

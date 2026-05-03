"""
Discount Service
================

Service layer for discount calculations using Strategy Pattern.
"""

from decimal import Decimal
from typing import Dict, Any, Optional

from ..strategies import (
    DiscountContext,
    CouponDiscountStrategy,
    OrderValueDiscountStrategy,
    FirstTimeBuyerDiscountStrategy
)


class DiscountService:
    """
    Service for calculating discounts using Strategy Pattern.
    
    This service replaces the hardcoded discount logic previously
    scattered across Cart and Order models.
    
    Usage:
        # For Cart
        service = DiscountService.for_cart(cart)
        total_discount = service.calculate_total_discount()
        breakdown = service.get_breakdown()
        
        # For Order
        service = DiscountService.for_order(order)
        total_discount = service.calculate_total_discount()
    """
    
    def __init__(self, subtotal: Decimal, customer, coupon=None):
        """
        Initialize the discount service.
        
        Args:
            subtotal: Order/cart subtotal
            customer: Customer instance
            coupon: Optional Coupon instance
        """
        self.subtotal = subtotal
        self.customer = customer
        self.coupon = coupon
        
        # Create discount context with all strategies
        self.context = DiscountContext.create_default_context()
    
    def calculate_total_discount(self) -> Decimal:
        """
        Calculate total discount from all applicable strategies.
        
        Returns:
            Decimal: Total discount amount
        """
        context_data = self._build_context_data()
        return self.context.calculate_total_discount(self.subtotal, context_data)
    
    def calculate_coupon_discount(self) -> Decimal:
        """
        Calculate only coupon discount.
        
        Returns:
            Decimal: Coupon discount amount
        """
        if not self.coupon:
            return Decimal('0.00')
        
        strategy = CouponDiscountStrategy()
        context_data = self._build_context_data()
        
        if strategy.is_applicable(context_data):
            return strategy.calculate_discount(self.subtotal, context_data)
        
        return Decimal('0.00')
    
    def calculate_order_value_discount(self) -> Decimal:
        """
        Calculate only order value discount.
        
        Returns:
            Decimal: Order value discount amount
        """
        strategy = OrderValueDiscountStrategy()
        context_data = self._build_context_data()
        
        if strategy.is_applicable(context_data):
            return strategy.calculate_discount(self.subtotal, context_data)
        
        return Decimal('0.00')
    
    def calculate_first_time_discount(self) -> Decimal:
        """
        Calculate only first-time buyer discount.
        
        Returns:
            Decimal: First-time buyer discount amount
        """
        strategy = FirstTimeBuyerDiscountStrategy()
        context_data = self._build_context_data()
        
        if strategy.is_applicable(context_data):
            return strategy.calculate_discount(self.subtotal, context_data)
        
        return Decimal('0.00')
    
    def get_breakdown(self) -> list:
        """
        Get detailed breakdown of all discounts.
        
        Returns:
            list: List of discount details
        """
        context_data = self._build_context_data()
        return self.context.get_discount_breakdown(self.subtotal, context_data)
    
    def get_applicable_discounts(self) -> list:
        """
        Get list of applicable discounts with amounts.
        
        Returns:
            list: List of (description, amount) tuples
        """
        context_data = self._build_context_data()
        return self.context.get_applicable_discounts(self.subtotal, context_data)
    
    def calculate_all_discounts(self) -> Dict[str, Any]:
        """
        Calculate all discounts and return a comprehensive result dictionary.
        
        This method is used by views to get all discount information at once.
        
        Returns:
            dict: Dictionary containing:
                - total_discount: Total discount amount
                - coupon_discount: Coupon discount amount
                - order_value_discount: Order value discount amount
                - first_time_discount: First-time buyer discount amount
                - breakdown: List of discount details
        """
        return {
            'total_discount': self.calculate_total_discount(),
            'coupon_discount': self.calculate_coupon_discount(),
            'order_value_discount': self.calculate_order_value_discount(),
            'first_time_discount': self.calculate_first_time_discount(),
            'breakdown': self.get_breakdown(),
        }
    
    @classmethod
    def calculate_all_discounts_for(cls, subtotal: Decimal, customer, coupon=None) -> Dict[str, Any]:
        """
        Class method to calculate all discounts without creating an instance first.
        
        This is a convenience method for views that don't need to keep the service instance.
        
        Args:
            subtotal: Order/cart subtotal
            customer: Customer instance
            coupon: Optional Coupon instance
        
        Returns:
            dict: Dictionary with all discount information
        """
        service = cls(subtotal, customer, coupon)
        return service.calculate_all_discounts()
    
    def _build_context_data(self) -> Dict[str, Any]:
        """
        Build context data dictionary for strategies.
        
        Returns:
            dict: Context data with customer and coupon
        """
        return {
            'customer': self.customer,
            'coupon': self.coupon,
        }
    
    @classmethod
    def for_cart(cls, cart) -> 'DiscountService':
        """
        Create DiscountService for a Cart instance.
        
        Args:
            cart: Cart model instance
        
        Returns:
            DiscountService: Service configured for the cart
        """
        return cls(
            subtotal=cart.subtotal,
            customer=cart.customer,
            coupon=cart.applied_coupon
        )
    
    @classmethod
    def for_order(cls, order) -> 'DiscountService':
        """
        Create DiscountService for an Order instance.
        
        Args:
            order: Order model instance
        
        Returns:
            DiscountService: Service configured for the order
        """
        return cls(
            subtotal=order.subtotal,
            customer=order.customer,
            coupon=order.applied_coupon
        )

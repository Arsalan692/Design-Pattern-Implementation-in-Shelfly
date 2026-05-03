"""
Discount Context
================

Manages and applies multiple discount strategies.
"""

from decimal import Decimal
from typing import List, Dict, Any, Tuple

from .discount_strategy import DiscountStrategy


class DiscountContext:
    """
    Context class for managing multiple discount strategies.
    
    This class:
        - Holds a list of discount strategies
        - Applies them in priority order
        - Calculates total discount
        - Provides detailed breakdown
    
    Usage:
        context = DiscountContext()
        context.add_strategy(CouponDiscountStrategy())
        context.add_strategy(OrderValueDiscountStrategy())
        context.add_strategy(FirstTimeBuyerDiscountStrategy())
        
        total_discount = context.calculate_total_discount(subtotal, data)
        breakdown = context.get_discount_breakdown(subtotal, data)
    """
    
    def __init__(self):
        """Initialize the discount context with an empty strategy list."""
        self._strategies: List[DiscountStrategy] = []
    
    def add_strategy(self, strategy: DiscountStrategy) -> None:
        """
        Add a discount strategy to the context.
        
        Args:
            strategy: A DiscountStrategy instance
        """
        if not isinstance(strategy, DiscountStrategy):
            raise TypeError(f"Expected DiscountStrategy, got {type(strategy)}")
        
        self._strategies.append(strategy)
        # Sort strategies by priority (lower number = higher priority)
        self._strategies.sort(key=lambda s: s.get_priority())
    
    def remove_strategy(self, strategy_class: type) -> bool:
        """
        Remove a strategy by its class type.
        
        Args:
            strategy_class: The class of the strategy to remove
        
        Returns:
            bool: True if strategy was removed, False if not found
        """
        original_length = len(self._strategies)
        self._strategies = [s for s in self._strategies if not isinstance(s, strategy_class)]
        return len(self._strategies) < original_length
    
    def clear_strategies(self) -> None:
        """Remove all strategies from the context."""
        self._strategies.clear()
    
    def calculate_total_discount(self, subtotal: Decimal, context: Dict[str, Any]) -> Decimal:
        """
        Calculate total discount by applying all strategies.
        
        Args:
            subtotal: Order/cart subtotal before discounts
            context: Context data for strategies (customer, coupon, etc.)
        
        Returns:
            Decimal: Total discount amount
        """
        total_discount = Decimal('0.00')
        
        for strategy in self._strategies:
            if strategy.is_applicable(context):
                discount = strategy.calculate_discount(subtotal, context)
                total_discount += discount
        
        return total_discount.quantize(Decimal('0.01'))
    
    def get_discount_breakdown(self, subtotal: Decimal, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get detailed breakdown of all applied discounts.
        
        Args:
            subtotal: Order/cart subtotal before discounts
            context: Context data for strategies
        
        Returns:
            List[Dict]: List of discount details, each containing:
                - 'strategy_name': Name of the strategy class
                - 'amount': Discount amount
                - 'description': Human-readable description
                - 'applicable': Whether discount was applied
        """
        breakdown = []
        
        for strategy in self._strategies:
            applicable = strategy.is_applicable(context)
            amount = Decimal('0.00')
            
            if applicable:
                amount = strategy.calculate_discount(subtotal, context)
            
            breakdown.append({
                'strategy_name': strategy.__class__.__name__,
                'amount': amount,
                'description': strategy.get_description(amount) if applicable else "Not applicable",
                'applicable': applicable,
                'priority': strategy.get_priority()
            })
        
        return breakdown
    
    def get_applicable_discounts(self, subtotal: Decimal, context: Dict[str, Any]) -> List[Tuple[str, Decimal]]:
        """
        Get list of applicable discounts with their amounts.
        
        Args:
            subtotal: Order/cart subtotal
            context: Context data
        
        Returns:
            List[Tuple[str, Decimal]]: List of (description, amount) tuples
        """
        applicable = []
        
        for strategy in self._strategies:
            if strategy.is_applicable(context):
                amount = strategy.calculate_discount(subtotal, context)
                if amount > 0:
                    description = strategy.get_description(amount)
                    applicable.append((description, amount))
        
        return applicable
    
    def has_applicable_discounts(self, context: Dict[str, Any]) -> bool:
        """
        Check if any discount strategies are applicable.
        
        Args:
            context: Context data
        
        Returns:
            bool: True if at least one discount is applicable
        """
        return any(strategy.is_applicable(context) for strategy in self._strategies)
    
    def get_strategy_count(self) -> int:
        """
        Get the number of registered strategies.
        
        Returns:
            int: Number of strategies
        """
        return len(self._strategies)
    
    def get_strategies(self) -> List[DiscountStrategy]:
        """
        Get list of all registered strategies.
        
        Returns:
            List[DiscountStrategy]: Copy of strategies list
        """
        return self._strategies.copy()
    
    @staticmethod
    def create_default_context() -> 'DiscountContext':
        """
        Create a DiscountContext with all default strategies.
        
        Returns:
            DiscountContext: Context with all standard discount strategies
        """
        from .coupon_discount import CouponDiscountStrategy
        from .order_value_discount import OrderValueDiscountStrategy
        from .first_time_buyer_discount import FirstTimeBuyerDiscountStrategy
        
        context = DiscountContext()
        context.add_strategy(CouponDiscountStrategy())
        context.add_strategy(OrderValueDiscountStrategy())
        context.add_strategy(FirstTimeBuyerDiscountStrategy())
        
        return context

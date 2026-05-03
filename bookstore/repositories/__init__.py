"""
Repository Pattern Implementation
==================================

This module implements the Repository Pattern for data access abstraction.

Design Pattern: Repository (Structural Pattern)
Problem Solved: Eliminates direct database queries in views and provides abstraction layer
Benefits:
    - Abstraction over data access
    - Easy to mock for testing
    - Centralized query optimization
    - Database-agnostic business logic
    - Follows Single Responsibility Principle
"""

from .base_repository import BaseRepository
from .book_repository import BookRepository
from .order_repository import OrderRepository
from .customer_repository import CustomerRepository
from .coupon_repository import CouponRepository

__all__ = [
    'BaseRepository',
    'BookRepository',
    'OrderRepository',
    'CustomerRepository',
    'CouponRepository',
]

"""
Payment Processing System - Factory Pattern
============================================

This module implements the Factory Pattern for payment processing.

Design Pattern: Factory (Creational Pattern)
Problem Solved: Eliminates conditional payment logic and makes it easy to add new payment methods
Benefits:
    - Centralized payment object creation
    - Easy to extend with new payment methods
    - Encapsulates payment-specific validation logic
    - Follows Open/Closed Principle
"""

from .payment_processor import PaymentProcessor
from .cash_processor import CashOnDeliveryProcessor
from .card_processor import CardPaymentProcessor
from .payment_factory import PaymentFactory

__all__ = [
    'PaymentProcessor',
    'CashOnDeliveryProcessor',
    'CardPaymentProcessor',
    'PaymentFactory',
]

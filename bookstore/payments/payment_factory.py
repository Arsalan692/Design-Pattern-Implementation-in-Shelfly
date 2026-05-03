"""
Payment Factory
===============

Factory class for creating payment processors.
"""

from typing import Optional

from .payment_processor import PaymentProcessor
from .cash_processor import CashOnDeliveryProcessor
from .card_processor import CardPaymentProcessor


class PaymentFactory:
    """
    Factory for creating payment processor instances.
    
    This implements the Factory Pattern, providing a centralized
    way to create payment processors based on payment method.
    
    Usage:
        processor = PaymentFactory.get_processor('Cash')
        success, message, details = processor.process_payment(order, data)
    """
    
    # Registry of available payment processors
    _processors = {
        'Cash': CashOnDeliveryProcessor,
        'Card': CardPaymentProcessor,
    }
    
    @classmethod
    def get_processor(cls, payment_method: str) -> Optional[PaymentProcessor]:
        """
        Get a payment processor instance for the specified method.
        
        Args:
            payment_method (str): Payment method name ('Cash', 'Card', etc.)
        
        Returns:
            PaymentProcessor: Payment processor instance or None if not found
        
        Raises:
            ValueError: If payment method is not supported
        """
        processor_class = cls._processors.get(payment_method)
        
        if processor_class is None:
            raise ValueError(f"Unsupported payment method: {payment_method}")
        
        return processor_class()
    
    @classmethod
    def register_processor(cls, payment_method: str, processor_class: type):
        """
        Register a new payment processor.
        
        This allows adding new payment methods without modifying the factory.
        
        Args:
            payment_method (str): Payment method name
            processor_class (type): Payment processor class
        
        Raises:
            TypeError: If processor_class is not a PaymentProcessor subclass
        """
        if not issubclass(processor_class, PaymentProcessor):
            raise TypeError(f"{processor_class} must be a subclass of PaymentProcessor")
        
        cls._processors[payment_method] = processor_class
    
    @classmethod
    def unregister_processor(cls, payment_method: str) -> bool:
        """
        Unregister a payment processor.
        
        Args:
            payment_method (str): Payment method name
        
        Returns:
            bool: True if processor was removed, False if not found
        """
        if payment_method in cls._processors:
            del cls._processors[payment_method]
            return True
        return False
    
    @classmethod
    def get_available_methods(cls) -> list:
        """
        Get list of available payment methods.
        
        Returns:
            list: List of payment method names
        """
        return list(cls._processors.keys())
    
    @classmethod
    def is_method_supported(cls, payment_method: str) -> bool:
        """
        Check if a payment method is supported.
        
        Args:
            payment_method (str): Payment method name
        
        Returns:
            bool: True if method is supported
        """
        return payment_method in cls._processors
    
    @classmethod
    def get_method_info(cls, payment_method: str) -> dict:
        """
        Get information about a payment method.
        
        Args:
            payment_method (str): Payment method name
        
        Returns:
            dict: Payment method information or None if not found
        """
        if not cls.is_method_supported(payment_method):
            return None
        
        processor = cls.get_processor(payment_method)
        
        return {
            'name': payment_method,
            'display_name': processor.get_display_name(),
            'description': processor.get_description(),
            'requires_immediate_payment': processor.requires_immediate_payment(),
            'supports_refund': processor.supports_refund(),
        }
    
    @classmethod
    def get_all_methods_info(cls) -> list:
        """
        Get information about all available payment methods.
        
        Returns:
            list: List of payment method information dicts
        """
        return [cls.get_method_info(method) for method in cls.get_available_methods()]

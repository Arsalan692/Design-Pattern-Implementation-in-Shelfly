"""
Payment Service
===============

Service layer for payment processing using Factory Pattern.
"""

from typing import Dict, Any, Tuple
from decimal import Decimal

from ..payments import PaymentFactory


class PaymentService:
    """
    Service for processing payments using Factory Pattern.
    
    This service replaces the conditional payment logic previously
    in views with a clean factory-based approach.
    
    Usage:
        service = PaymentService(payment_method='Card')
        success, message, details = service.process_payment(order, payment_data)
    """
    
    def __init__(self, payment_method: str):
        """
        Initialize the payment service.
        
        Args:
            payment_method (str): Payment method name ('Cash', 'Card', etc.)
        
        Raises:
            ValueError: If payment method is not supported
        """
        self.payment_method = payment_method
        self.processor = PaymentFactory.get_processor(payment_method)
    
    def validate_payment_data(self, payment_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate payment data using the appropriate processor.
        
        Args:
            payment_data (Dict): Payment-specific data
        
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        return self.processor.validate_payment_data(payment_data)
    
    def process_payment(
        self, 
        order, 
        payment_data: Dict[str, Any]
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Process payment using the appropriate processor.
        
        Args:
            order: Order instance
            payment_data (Dict): Payment-specific data
        
        Returns:
            Tuple[bool, str, Dict]: (success, message, payment_details)
        """
        return self.processor.process_payment(order, payment_data)
    
    def get_payment_method_info(self) -> dict:
        """
        Get information about the current payment method.
        
        Returns:
            dict: Payment method information
        """
        return {
            'name': self.payment_method,
            'display_name': self.processor.get_display_name(),
            'description': self.processor.get_description(),
            'requires_immediate_payment': self.processor.requires_immediate_payment(),
            'supports_refund': self.processor.supports_refund(),
        }
    
    @staticmethod
    def get_available_payment_methods() -> list:
        """
        Get list of all available payment methods.
        
        Returns:
            list: List of payment method information dicts
        """
        return PaymentFactory.get_all_methods_info()
    
    @staticmethod
    def is_payment_method_supported(payment_method: str) -> bool:
        """
        Check if a payment method is supported.
        
        Args:
            payment_method (str): Payment method name
        
        Returns:
            bool: True if supported
        """
        return PaymentFactory.is_method_supported(payment_method)
    
    @staticmethod
    def process_payment_for(
        order,
        payment_method: str,
        payment_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Static method to process payment without creating a service instance first.
        
        This is a convenience method for views.
        
        Args:
            order: Order instance
            payment_method (str): Payment method name ('Cash', 'Card', etc.)
            payment_details (Dict): Payment-specific data
        
        Returns:
            dict: Payment result with keys:
                - success (bool): Whether payment was successful
                - message (str): Success/error message
                - payment_details (dict): Payment details dict if successful, None otherwise
        """
        try:
            # Get the appropriate payment processor
            processor = PaymentFactory.get_processor(payment_method)
            
            # Validate payment data
            is_valid, error_message = processor.validate_payment_data(payment_details)
            if not is_valid:
                return {
                    'success': False,
                    'message': error_message,
                    'payment': None
                }
            
            # Process the payment
            success, message, payment_details = processor.process_payment(order, payment_details)
            
            return {
                'success': success,
                'message': message,
                'payment_details': payment_details
            }
            
        except ValueError as e:
            return {
                'success': False,
                'message': str(e),
                'payment_details': None
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Payment processing error: {str(e)}',
                'payment_details': None
            }

"""
Payment Processor Base Class
=============================

Abstract base class for all payment processors.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
from decimal import Decimal


class PaymentProcessor(ABC):
    """
    Abstract base class for payment processing.
    
    This follows the Factory Pattern, allowing different payment
    methods to be used interchangeably.
    
    Each concrete processor must implement:
        - validate_payment_data(): Validate payment-specific data
        - process_payment(): Process the payment
        - get_payment_method_name(): Return payment method name
        - get_transaction_id(): Generate transaction ID
    """
    
    @abstractmethod
    def validate_payment_data(self, payment_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate payment-specific data.
        
        Args:
            payment_data (Dict): Payment data to validate
        
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
                - is_valid: True if data is valid
                - error_message: Error message if invalid, empty string if valid
        """
        pass
    
    @abstractmethod
    def process_payment(
        self, 
        order, 
        payment_data: Dict[str, Any]
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Process the payment for an order.
        
        Args:
            order: Order instance
            payment_data (Dict): Payment-specific data
        
        Returns:
            Tuple[bool, str, Dict]: (success, message, payment_details)
                - success: True if payment successful
                - message: Success/error message
                - payment_details: Additional payment information
        """
        pass
    
    @abstractmethod
    def get_payment_method_name(self) -> str:
        """
        Get the name of this payment method.
        
        Returns:
            str: Payment method name (e.g., "Cash", "Card")
        """
        pass
    
    @abstractmethod
    def get_transaction_id(self, order) -> str:
        """
        Generate a transaction ID for the payment.
        
        Args:
            order: Order instance
        
        Returns:
            str: Transaction ID
        """
        pass
    
    def get_payment_status(self) -> str:
        """
        Get the initial payment status.
        
        Override in subclasses if different status needed.
        
        Returns:
            str: Payment status ("Paid", "Unpaid", etc.)
        """
        return "Unpaid"
    
    def supports_refund(self) -> bool:
        """
        Check if this payment method supports refunds.
        
        Override in subclasses.
        
        Returns:
            bool: True if refunds are supported
        """
        return False
    
    def get_display_name(self) -> str:
        """
        Get user-friendly display name for this payment method.
        
        Returns:
            str: Display name
        """
        return self.get_payment_method_name()
    
    def get_description(self) -> str:
        """
        Get a description of this payment method.
        
        Override in subclasses for custom descriptions.
        
        Returns:
            str: Payment method description
        """
        return f"Pay using {self.get_display_name()}"
    
    def requires_immediate_payment(self) -> bool:
        """
        Check if this payment method requires immediate payment.
        
        Returns:
            bool: True if immediate payment required
        """
        return False
    
    def create_payment_record(self, order, amount: Decimal, transaction_id: str, status: str):
        """
        Create a Payment model instance.
        
        Args:
            order: Order instance
            amount: Payment amount
            transaction_id: Transaction ID
            status: Payment status
        
        Returns:
            Payment: Created payment instance
        """
        from bookstore.models import Payment
        
        return Payment.objects.create(
            order=order,
            amount=amount,
            method=self.get_payment_method_name(),
            status=status,
            transaction_id=transaction_id
        )

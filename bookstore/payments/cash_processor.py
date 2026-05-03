"""
Cash on Delivery Payment Processor
===================================

Handles Cash on Delivery (COD) payment processing.
"""

from typing import Dict, Any, Tuple
from decimal import Decimal

from .payment_processor import PaymentProcessor


class CashOnDeliveryProcessor(PaymentProcessor):
    """
    Payment processor for Cash on Delivery.
    
    COD payments:
        - No upfront payment required
        - Payment collected upon delivery
        - No validation needed (delivery info validated separately)
        - Status: "Unpaid" initially
    """
    
    def validate_payment_data(self, payment_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate COD payment data.
        
        COD requires minimal validation - just delivery information
        which is validated separately.
        
        Args:
            payment_data: Payment data (not used for COD)
        
        Returns:
            Tuple[bool, str]: (True, "") - COD always valid
        """
        # COD doesn't require payment data validation
        # Delivery information is validated separately
        return True, ""
    
    def process_payment(
        self, 
        order, 
        payment_data: Dict[str, Any]
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Process COD payment.
        
        For COD, we just create a payment record with "Unpaid" status.
        Payment will be collected upon delivery.
        
        Args:
            order: Order instance
            payment_data: Payment data (not used for COD)
        
        Returns:
            Tuple[bool, str, Dict]: (success, message, payment_details)
        """
        try:
            # Generate transaction ID
            transaction_id = self.get_transaction_id(order)
            
            # Create payment record
            payment = self.create_payment_record(
                order=order,
                amount=order.total_amount,
                transaction_id=transaction_id,
                status=self.get_payment_status()
            )
            
            # Prepare payment details
            payment_details = {
                'payment_id': payment.id,
                'transaction_id': transaction_id,
                'amount': float(order.total_amount),
                'method': self.get_payment_method_name(),
                'status': payment.status,
                'message': 'Payment will be collected upon delivery'
            }
            
            return True, "Order placed successfully! Pay on delivery.", payment_details
            
        except Exception as e:
            return False, f"Error processing COD payment: {str(e)}", {}
    
    def get_payment_method_name(self) -> str:
        """
        Get payment method name.
        
        Returns:
            str: "Cash"
        """
        return "Cash"
    
    def get_transaction_id(self, order) -> str:
        """
        Generate transaction ID for COD.
        
        Args:
            order: Order instance
        
        Returns:
            str: Transaction ID in format "COD-{order_id}-{timestamp}"
        """
        from django.utils import timezone
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        return f"COD-{order.id}-{timestamp}"
    
    def get_payment_status(self) -> str:
        """
        Get initial payment status for COD.
        
        Returns:
            str: "Unpaid" (payment collected on delivery)
        """
        return "Unpaid"
    
    def supports_refund(self) -> bool:
        """
        COD supports refunds (cash refund on return).
        
        Returns:
            bool: True
        """
        return True
    
    def get_display_name(self) -> str:
        """
        Get user-friendly display name.
        
        Returns:
            str: "Cash on Delivery"
        """
        return "Cash on Delivery"
    
    def get_description(self) -> str:
        """
        Get payment method description.
        
        Returns:
            str: Description of COD payment
        """
        return "Pay with cash when your order is delivered to your doorstep"
    
    def requires_immediate_payment(self) -> bool:
        """
        COD does not require immediate payment.
        
        Returns:
            bool: False
        """
        return False
    
    def get_payment_instructions(self) -> str:
        """
        Get instructions for COD payment.
        
        Returns:
            str: Payment instructions
        """
        return (
            "Your order will be delivered to your address. "
            "Please keep the exact amount ready for the delivery person. "
            "You can pay in cash upon receiving your order."
        )

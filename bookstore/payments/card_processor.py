"""
Card Payment Processor
======================

Handles Credit/Debit Card payment processing.
"""

from typing import Dict, Any, Tuple
from decimal import Decimal
import re
from datetime import datetime

from .payment_processor import PaymentProcessor


class CardPaymentProcessor(PaymentProcessor):
    """
    Payment processor for Credit/Debit Card payments.
    
    Card payments:
        - Requires card validation (number, expiry, CVV)
        - Immediate payment processing
        - Status: "Paid" on success
        - Supports Luhn algorithm validation
    """
    
    # Card type patterns
    CARD_PATTERNS = {
        'Visa': r'^4[0-9]{12}(?:[0-9]{3})?$',
        'Mastercard': r'^5[1-5][0-9]{14}$',
        'American Express': r'^3[47][0-9]{13}$',
        'Discover': r'^6(?:011|5[0-9]{2})[0-9]{12}$',
    }
    
    def validate_payment_data(self, payment_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate card payment data.
        
        Validates:
            - Card number (Luhn algorithm)
            - Expiry date (not expired)
            - CVV (3-4 digits)
            - Card holder name
        
        Args:
            payment_data: Dict containing:
                - card_number: str
                - card_holder: str
                - expiry_month: str
                - expiry_year: str
                - cvv: str
        
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        # Extract card data
        card_number = payment_data.get('card_number', '').strip()
        card_holder = payment_data.get('card_holder', '').strip()
        expiry_month = payment_data.get('expiry_month', '').strip()
        expiry_year = payment_data.get('expiry_year', '').strip()
        cvv = payment_data.get('cvv', '').strip()
        
        # Check all fields present
        if not all([card_number, card_holder, expiry_month, expiry_year, cvv]):
            return False, "All card fields are required"
        
        # Validate card number
        is_valid, msg = self._validate_card_number(card_number)
        if not is_valid:
            return False, msg
        
        # Validate expiry date
        is_valid, msg = self._validate_expiry_date(expiry_month, expiry_year)
        if not is_valid:
            return False, msg
        
        # Validate CVV
        is_valid, msg = self._validate_cvv(cvv)
        if not is_valid:
            return False, msg
        
        # Validate card holder name
        if len(card_holder) < 3:
            return False, "Card holder name must be at least 3 characters"
        
        return True, ""
    
    def process_payment(
        self, 
        order, 
        payment_data: Dict[str, Any]
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Process card payment.
        
        Args:
            order: Order instance
            payment_data: Card payment data
        
        Returns:
            Tuple[bool, str, Dict]: (success, message, payment_details)
        """
        try:
            # Validate payment data
            is_valid, error_msg = self.validate_payment_data(payment_data)
            if not is_valid:
                return False, error_msg, {}
            
            # In a real system, this would call a payment gateway API
            # For demo purposes, we'll simulate successful payment
            
            # Get card info
            card_number = payment_data.get('card_number', '').strip()
            card_holder = payment_data.get('card_holder', '').strip()
            
            # Detect card type
            card_type = self._get_card_type(card_number)
            
            # Mask card number
            masked_card = self._mask_card_number(card_number)
            
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
                'card_type': card_type,
                'masked_card': masked_card,
                'card_holder': card_holder,
                'message': 'Payment processed successfully'
            }
            
            return True, "Payment processed successfully!", payment_details
            
        except Exception as e:
            return False, f"Error processing card payment: {str(e)}", {}
    
    def get_payment_method_name(self) -> str:
        """
        Get payment method name.
        
        Returns:
            str: "Card"
        """
        return "Card"
    
    def get_transaction_id(self, order) -> str:
        """
        Generate transaction ID for card payment.
        
        Args:
            order: Order instance
        
        Returns:
            str: Transaction ID in format "CARD-{order_id}-{timestamp}"
        """
        from django.utils import timezone
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        return f"CARD-{order.id}-{timestamp}"
    
    def get_payment_status(self) -> str:
        """
        Get payment status for card payment.
        
        Returns:
            str: "Paid" (immediate payment)
        """
        return "Paid"
    
    def supports_refund(self) -> bool:
        """
        Card payments support refunds.
        
        Returns:
            bool: True
        """
        return True
    
    def get_display_name(self) -> str:
        """
        Get user-friendly display name.
        
        Returns:
            str: "Credit/Debit Card"
        """
        return "Credit/Debit Card"
    
    def get_description(self) -> str:
        """
        Get payment method description.
        
        Returns:
            str: Description of card payment
        """
        return "Pay securely using your credit or debit card (Visa, Mastercard, Amex, Discover)"
    
    def requires_immediate_payment(self) -> bool:
        """
        Card payment requires immediate processing.
        
        Returns:
            bool: True
        """
        return True
    
    # Private validation methods
    
    def _validate_card_number(self, card_number: str) -> Tuple[bool, str]:
        """
        Validate card number using Luhn algorithm.
        
        Args:
            card_number: Card number string
        
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        # Remove spaces
        card_number = card_number.replace(' ', '')
        
        # Check if only digits
        if not card_number.isdigit():
            return False, "Card number must contain only digits"
        
        # Check length
        if len(card_number) < 13 or len(card_number) > 19:
            return False, "Card number must be between 13-19 digits"
        
        # Luhn algorithm
        def luhn_check(num):
            total = 0
            reverse_digits = num[::-1]
            for i, digit in enumerate(reverse_digits):
                n = int(digit)
                if i % 2 == 1:
                    n = n * 2
                    if n > 9:
                        n = n - 9
                total += n
            return total % 10 == 0
        
        if not luhn_check(card_number):
            return False, "Invalid card number (failed Luhn check)"
        
        return True, ""
    
    def _validate_expiry_date(self, month: str, year: str) -> Tuple[bool, str]:
        """
        Validate card expiry date.
        
        Args:
            month: Expiry month (01-12)
            year: Expiry year (YY or YYYY)
        
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        try:
            month = int(month)
            year = int(year)
        except:
            return False, "Invalid expiry date format"
        
        # Validate month
        if month < 1 or month > 12:
            return False, "Month must be between 01-12"
        
        # Convert 2-digit year to 4-digit
        if year < 100:
            current_year = datetime.now().year
            current_century = (current_year // 100) * 100
            year = current_century + year
        
        # Check if expired
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        
        if year < current_year:
            return False, "Card has expired"
        
        if year == current_year and month < current_month:
            return False, "Card has expired"
        
        return True, ""
    
    def _validate_cvv(self, cvv: str) -> Tuple[bool, str]:
        """
        Validate CVV.
        
        Args:
            cvv: CVV string
        
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not cvv.isdigit():
            return False, "CVV must contain only digits"
        
        if len(cvv) not in [3, 4]:
            return False, "CVV must be 3 or 4 digits"
        
        return True, ""
    
    def _get_card_type(self, card_number: str) -> str:
        """
        Determine card type from card number.
        
        Args:
            card_number: Card number string
        
        Returns:
            str: Card type (Visa, Mastercard, etc.) or "Unknown"
        """
        card_number = card_number.replace(' ', '')
        
        for card_type, pattern in self.CARD_PATTERNS.items():
            if re.match(pattern, card_number):
                return card_type
        
        return "Unknown"
    
    def _mask_card_number(self, card_number: str) -> str:
        """
        Mask card number for display.
        
        Args:
            card_number: Card number string
        
        Returns:
            str: Masked card number (e.g., "**** **** **** 1234")
        """
        card_number = card_number.replace(' ', '')
        return '**** **** **** ' + card_number[-4:]

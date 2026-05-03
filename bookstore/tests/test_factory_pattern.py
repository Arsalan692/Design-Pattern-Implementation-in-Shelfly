"""
Unit Tests for Factory Pattern
===============================

Tests for payment processing factory pattern.
"""

from decimal import Decimal
from datetime import datetime, timedelta
from django.test import TestCase
from django.contrib.auth.models import User

from bookstore.models import Customer, Order, Payment, Book, OrderItem
from bookstore.payments import (
    PaymentFactory,
    CashOnDeliveryProcessor,
    CardPaymentProcessor
)
from bookstore.services import PaymentService


class TestPaymentFactory(TestCase):
    """Test cases for PaymentFactory."""
    
    def test_get_cash_processor(self):
        """Test getting Cash processor from factory."""
        processor = PaymentFactory.get_processor('Cash')
        
        self.assertIsInstance(processor, CashOnDeliveryProcessor)
    
    def test_get_card_processor(self):
        """Test getting Card processor from factory."""
        processor = PaymentFactory.get_processor('Card')
        
        self.assertIsInstance(processor, CardPaymentProcessor)
    
    def test_unsupported_payment_method(self):
        """Test error when requesting unsupported payment method."""
        with self.assertRaises(ValueError):
            PaymentFactory.get_processor('Bitcoin')
    
    def test_get_available_methods(self):
        """Test getting list of available payment methods."""
        methods = PaymentFactory.get_available_methods()
        
        self.assertIn('Cash', methods)
        self.assertIn('Card', methods)
        self.assertEqual(len(methods), 2)
    
    def test_is_method_supported(self):
        """Test checking if payment method is supported."""
        self.assertTrue(PaymentFactory.is_method_supported('Cash'))
        self.assertTrue(PaymentFactory.is_method_supported('Card'))
        self.assertFalse(PaymentFactory.is_method_supported('Bitcoin'))
    
    def test_get_method_info(self):
        """Test getting payment method information."""
        info = PaymentFactory.get_method_info('Cash')
        
        self.assertEqual(info['name'], 'Cash')
        self.assertEqual(info['display_name'], 'Cash on Delivery')
        self.assertFalse(info['requires_immediate_payment'])
        self.assertTrue(info['supports_refund'])
    
    def test_get_all_methods_info(self):
        """Test getting information for all payment methods."""
        all_info = PaymentFactory.get_all_methods_info()
        
        self.assertEqual(len(all_info), 2)
        self.assertTrue(all(isinstance(info, dict) for info in all_info))


class TestCashOnDeliveryProcessor(TestCase):
    """Test cases for CashOnDeliveryProcessor."""
    
    def setUp(self):
        """Set up test data."""
        self.processor = CashOnDeliveryProcessor()
        
        # Create test user and customer
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            phone='1234567890',
            address='Test Address',
            is_first_time_buyer=False
        )
        
        # Create test book
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            category='Fiction',
            price=Decimal('500.00'),
            stock=10
        )
        
        # Create test order
        self.order = Order.objects.create(
            customer=self.customer,
            shipping_fee=Decimal('50.00')
        )
        
        OrderItem.objects.create(
            order=self.order,
            book=self.book,
            quantity=2,
            unit_price=self.book.price,
            subtotal=self.book.price * 2
        )
        
        # Refresh order to get calculated total_amount
        self.order.refresh_from_db()
    
    def test_validate_payment_data(self):
        """Test COD payment data validation."""
        is_valid, msg = self.processor.validate_payment_data({})
        
        self.assertTrue(is_valid)
        self.assertEqual(msg, "")
    
    def test_process_payment(self):
        """Test COD payment processing."""
        success, message, details = self.processor.process_payment(self.order, {})
        
        self.assertTrue(success)
        self.assertIn("Pay on delivery", message)
        self.assertEqual(details['method'], 'Cash')
        self.assertEqual(details['status'], 'Unpaid')
    
    def test_get_payment_method_name(self):
        """Test getting payment method name."""
        self.assertEqual(self.processor.get_payment_method_name(), 'Cash')
    
    def test_get_display_name(self):
        """Test getting display name."""
        self.assertEqual(self.processor.get_display_name(), 'Cash on Delivery')
    
    def test_requires_immediate_payment(self):
        """Test COD does not require immediate payment."""
        self.assertFalse(self.processor.requires_immediate_payment())
    
    def test_supports_refund(self):
        """Test COD supports refunds."""
        self.assertTrue(self.processor.supports_refund())
    
    def test_payment_status(self):
        """Test COD payment status is Unpaid."""
        self.assertEqual(self.processor.get_payment_status(), 'Unpaid')


class TestCardPaymentProcessor(TestCase):
    """Test cases for CardPaymentProcessor."""
    
    def setUp(self):
        """Set up test data."""
        self.processor = CardPaymentProcessor()
        
        # Create test user and customer
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            phone='1234567890',
            address='Test Address',
            is_first_time_buyer=False
        )
        
        # Create test book
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            category='Fiction',
            price=Decimal('500.00'),
            stock=10
        )
        
        # Create test order
        self.order = Order.objects.create(
            customer=self.customer,
            shipping_fee=Decimal('50.00')
        )
        
        OrderItem.objects.create(
            order=self.order,
            book=self.book,
            quantity=2,
            unit_price=self.book.price,
            subtotal=self.book.price * 2
        )
        
        # Refresh order to get calculated total_amount
        self.order.refresh_from_db()
        
        # Valid card data
        self.valid_card_data = {
            'card_number': '4532015112830366',  # Valid Visa test card
            'card_holder': 'John Doe',
            'expiry_month': '12',
            'expiry_year': '2028',
            'cvv': '123'
        }
    
    def test_validate_valid_card_data(self):
        """Test validation of valid card data."""
        is_valid, msg = self.processor.validate_payment_data(self.valid_card_data)
        
        self.assertTrue(is_valid)
        self.assertEqual(msg, "")
    
    def test_validate_missing_fields(self):
        """Test validation fails with missing fields."""
        invalid_data = {'card_number': '4532015112830366'}
        
        is_valid, msg = self.processor.validate_payment_data(invalid_data)
        
        self.assertFalse(is_valid)
        self.assertIn("required", msg.lower())
    
    def test_validate_invalid_card_number(self):
        """Test validation fails with invalid card number."""
        invalid_data = self.valid_card_data.copy()
        invalid_data['card_number'] = '1234567890123456'  # Invalid Luhn
        
        is_valid, msg = self.processor.validate_payment_data(invalid_data)
        
        self.assertFalse(is_valid)
        self.assertIn("Invalid card number", msg)
    
    def test_validate_expired_card(self):
        """Test validation fails with expired card."""
        invalid_data = self.valid_card_data.copy()
        invalid_data['expiry_month'] = '01'
        invalid_data['expiry_year'] = '2020'
        
        is_valid, msg = self.processor.validate_payment_data(invalid_data)
        
        self.assertFalse(is_valid)
        self.assertIn("expired", msg.lower())
    
    def test_validate_invalid_cvv(self):
        """Test validation fails with invalid CVV."""
        invalid_data = self.valid_card_data.copy()
        invalid_data['cvv'] = '12'  # Too short
        
        is_valid, msg = self.processor.validate_payment_data(invalid_data)
        
        self.assertFalse(is_valid)
        self.assertIn("CVV", msg)
    
    def test_process_payment(self):
        """Test card payment processing."""
        success, message, details = self.processor.process_payment(
            self.order, 
            self.valid_card_data
        )
        
        self.assertTrue(success)
        self.assertIn("successful", message.lower())
        self.assertEqual(details['method'], 'Card')
        self.assertEqual(details['status'], 'Paid')
        self.assertIn('masked_card', details)
        self.assertIn('card_type', details)
    
    def test_get_payment_method_name(self):
        """Test getting payment method name."""
        self.assertEqual(self.processor.get_payment_method_name(), 'Card')
    
    def test_get_display_name(self):
        """Test getting display name."""
        self.assertEqual(self.processor.get_display_name(), 'Credit/Debit Card')
    
    def test_requires_immediate_payment(self):
        """Test card requires immediate payment."""
        self.assertTrue(self.processor.requires_immediate_payment())
    
    def test_supports_refund(self):
        """Test card supports refunds."""
        self.assertTrue(self.processor.supports_refund())
    
    def test_payment_status(self):
        """Test card payment status is Paid."""
        self.assertEqual(self.processor.get_payment_status(), 'Paid')
    
    def test_card_type_detection(self):
        """Test card type detection."""
        # Test Visa
        visa_data = self.valid_card_data.copy()
        visa_data['card_number'] = '4532015112830366'
        success, _, details = self.processor.process_payment(self.order, visa_data)
        self.assertEqual(details['card_type'], 'Visa')
        
        # Test Mastercard - create a new order for second payment
        order2 = Order.objects.create(
            customer=self.customer,
            shipping_fee=Decimal('50.00')
        )
        OrderItem.objects.create(
            order=order2,
            book=self.book,
            quantity=2,
            unit_price=self.book.price,
            subtotal=self.book.price * 2
        )
        order2.refresh_from_db()
        
        mastercard_data = self.valid_card_data.copy()
        mastercard_data['card_number'] = '5425233430109903'
        success, _, details = self.processor.process_payment(order2, mastercard_data)
        self.assertEqual(details['card_type'], 'Mastercard')
    
    def test_card_masking(self):
        """Test card number masking."""
        success, _, details = self.processor.process_payment(
            self.order, 
            self.valid_card_data
        )
        
        masked = details['masked_card']
        self.assertTrue(masked.startswith('****'))
        self.assertTrue(masked.endswith('0366'))


class TestPaymentService(TestCase):
    """Test cases for PaymentService."""
    
    def setUp(self):
        """Set up test data."""
        # Create test user and customer
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            phone='1234567890',
            address='Test Address',
            is_first_time_buyer=False
        )
        
        # Create test book
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            category='Fiction',
            price=Decimal('500.00'),
            stock=10
        )
        
        # Create test order
        self.order = Order.objects.create(
            customer=self.customer,
            shipping_fee=Decimal('50.00')
        )
        
        OrderItem.objects.create(
            order=self.order,
            book=self.book,
            quantity=2,
            unit_price=self.book.price,
            subtotal=self.book.price * 2
        )
        
        # Refresh order to get calculated total_amount
        self.order.refresh_from_db()
    
    def test_create_cash_service(self):
        """Test creating payment service for Cash."""
        service = PaymentService('Cash')
        
        self.assertEqual(service.payment_method, 'Cash')
        self.assertIsInstance(service.processor, CashOnDeliveryProcessor)
    
    def test_create_card_service(self):
        """Test creating payment service for Card."""
        service = PaymentService('Card')
        
        self.assertEqual(service.payment_method, 'Card')
        self.assertIsInstance(service.processor, CardPaymentProcessor)
    
    def test_unsupported_payment_method(self):
        """Test error with unsupported payment method."""
        with self.assertRaises(ValueError):
            PaymentService('Bitcoin')
    
    def test_process_cash_payment(self):
        """Test processing Cash payment through service."""
        service = PaymentService('Cash')
        success, message, details = service.process_payment(self.order, {})
        
        self.assertTrue(success)
        self.assertEqual(details['method'], 'Cash')
    
    def test_process_card_payment(self):
        """Test processing Card payment through service."""
        service = PaymentService('Card')
        card_data = {
            'card_number': '4532015112830366',
            'card_holder': 'John Doe',
            'expiry_month': '12',
            'expiry_year': '2028',
            'cvv': '123'
        }
        
        success, message, details = service.process_payment(self.order, card_data)
        
        self.assertTrue(success)
        self.assertEqual(details['method'], 'Card')
    
    def test_get_payment_method_info(self):
        """Test getting payment method info through service."""
        service = PaymentService('Cash')
        info = service.get_payment_method_info()
        
        self.assertEqual(info['name'], 'Cash')
        self.assertEqual(info['display_name'], 'Cash on Delivery')
    
    def test_get_available_payment_methods(self):
        """Test getting available payment methods."""
        methods = PaymentService.get_available_payment_methods()
        
        self.assertEqual(len(methods), 2)
        self.assertTrue(any(m['name'] == 'Cash' for m in methods))
        self.assertTrue(any(m['name'] == 'Card' for m in methods))
    
    def test_is_payment_method_supported(self):
        """Test checking if payment method is supported."""
        self.assertTrue(PaymentService.is_payment_method_supported('Cash'))
        self.assertTrue(PaymentService.is_payment_method_supported('Card'))
        self.assertFalse(PaymentService.is_payment_method_supported('Bitcoin'))

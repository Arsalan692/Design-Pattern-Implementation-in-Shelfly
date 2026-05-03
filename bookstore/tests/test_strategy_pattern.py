"""
Unit Tests for Strategy Pattern
================================

Tests for discount calculation strategies.
"""

from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from django.test import TestCase
from django.contrib.auth.models import User

from bookstore.models import Customer, Coupon
from bookstore.strategies import (
    CouponDiscountStrategy,
    OrderValueDiscountStrategy,
    FirstTimeBuyerDiscountStrategy,
    DiscountContext
)
from bookstore.services import DiscountService


class TestCouponDiscountStrategy(TestCase):
    """Test cases for CouponDiscountStrategy."""
    
    def setUp(self):
        """Set up test data."""
        self.strategy = CouponDiscountStrategy()
        
        # Create test coupon - fixed amount
        self.fixed_coupon = Coupon.objects.create(
            code='SAVE500',
            discount_type='fixed',
            discount_value=Decimal('500.00'),
            max_usage=100,
            min_purchase=Decimal('1000.00'),
            expiry_date=timezone.now() + timedelta(days=30),
            is_active=True
        )
        
        # Create test coupon - percentage
        self.percentage_coupon = Coupon.objects.create(
            code='SAVE20',
            discount_type='percentage',
            discount_value=Decimal('20'),
            max_usage=100,
            min_purchase=Decimal('500.00'),
            expiry_date=timezone.now() + timedelta(days=30),
            is_active=True
        )
    
    def test_fixed_coupon_discount(self):
        """Test fixed amount coupon discount calculation."""
        subtotal = Decimal('2000.00')
        context = {'coupon': self.fixed_coupon}
        
        discount = self.strategy.calculate_discount(subtotal, context)
        
        self.assertEqual(discount, Decimal('500.00'))
    
    def test_percentage_coupon_discount(self):
        """Test percentage coupon discount calculation."""
        subtotal = Decimal('1000.00')
        context = {'coupon': self.percentage_coupon}
        
        discount = self.strategy.calculate_discount(subtotal, context)
        
        self.assertEqual(discount, Decimal('200.00'))  # 20% of 1000
    
    def test_coupon_below_minimum_purchase(self):
        """Test coupon not applied when below minimum purchase."""
        subtotal = Decimal('500.00')  # Below 1000 minimum
        context = {'coupon': self.fixed_coupon}
        
        discount = self.strategy.calculate_discount(subtotal, context)
        
        self.assertEqual(discount, Decimal('0.00'))
    
    def test_fixed_coupon_cannot_exceed_subtotal(self):
        """Test fixed coupon discount cannot exceed subtotal."""
        # Use subtotal above minimum (1000) but below discount (500)
        # So discount should be capped at subtotal, not the full 500
        subtotal = Decimal('1200.00')  # Above minimum of 1000
        
        # Create a large discount coupon (2000 off)
        large_coupon = Coupon.objects.create(
            code='LARGE2000',
            discount_type='fixed',
            discount_value=Decimal('2000.00'),
            max_usage=100,
            min_purchase=Decimal('1000.00'),
            expiry_date=timezone.now() + timedelta(days=30),
            is_active=True
        )
        
        context = {'coupon': large_coupon}
        
        discount = self.strategy.calculate_discount(subtotal, context)
        
        # Discount should be capped at subtotal (1200), not full discount (2000)
        self.assertEqual(discount, Decimal('1200.00'))
    
    def test_inactive_coupon_not_applicable(self):
        """Test inactive coupon is not applicable."""
        self.fixed_coupon.is_active = False
        self.fixed_coupon.save()
        
        context = {'coupon': self.fixed_coupon}
        
        self.assertFalse(self.strategy.is_applicable(context))
    
    def test_expired_coupon_not_applicable(self):
        """Test expired coupon is not applicable."""
        self.fixed_coupon.expiry_date = timezone.now() - timedelta(days=1)
        self.fixed_coupon.save()
        
        context = {'coupon': self.fixed_coupon}
        
        self.assertFalse(self.strategy.is_applicable(context))
    
    def test_no_coupon_returns_zero(self):
        """Test no coupon returns zero discount."""
        subtotal = Decimal('1000.00')
        context = {'coupon': None}
        
        discount = self.strategy.calculate_discount(subtotal, context)
        
        self.assertEqual(discount, Decimal('0.00'))


class TestOrderValueDiscountStrategy(TestCase):
    """Test cases for OrderValueDiscountStrategy."""
    
    def setUp(self):
        """Set up test data."""
        self.strategy = OrderValueDiscountStrategy()
    
    def test_tier_1_discount_5000_plus(self):
        """Test 15% discount for orders >= 5000."""
        subtotal = Decimal('6000.00')
        context = {}
        
        discount = self.strategy.calculate_discount(subtotal, context)
        
        expected = Decimal('900.00')  # 15% of 6000
        self.assertEqual(discount, expected)
    
    def test_tier_2_discount_2000_to_4999(self):
        """Test 10% discount for orders >= 2000."""
        subtotal = Decimal('3000.00')
        context = {}
        
        discount = self.strategy.calculate_discount(subtotal, context)
        
        expected = Decimal('300.00')  # 10% of 3000
        self.assertEqual(discount, expected)
    
    def test_tier_3_discount_1000_to_1999(self):
        """Test 5% discount for orders >= 1000."""
        subtotal = Decimal('1500.00')
        context = {}
        
        discount = self.strategy.calculate_discount(subtotal, context)
        
        expected = Decimal('75.00')  # 5% of 1500
        self.assertEqual(discount, expected)
    
    def test_no_discount_below_1000(self):
        """Test no discount for orders < 1000."""
        subtotal = Decimal('999.00')
        context = {}
        
        discount = self.strategy.calculate_discount(subtotal, context)
        
        self.assertEqual(discount, Decimal('0.00'))
    
    def test_exact_tier_boundary_5000(self):
        """Test discount at exact tier boundary (5000)."""
        subtotal = Decimal('5000.00')
        context = {}
        
        discount = self.strategy.calculate_discount(subtotal, context)
        
        expected = Decimal('750.00')  # 15% of 5000
        self.assertEqual(discount, expected)
    
    def test_get_next_tier_info(self):
        """Test getting next tier information."""
        subtotal = Decimal('1500.00')
        
        info = OrderValueDiscountStrategy.get_next_tier_info(subtotal)
        
        self.assertTrue(info['has_next_tier'])
        self.assertEqual(info['next_tier_amount'], Decimal('2000.00'))
        self.assertEqual(info['amount_needed'], Decimal('500.00'))


class TestFirstTimeBuyerDiscountStrategy(TestCase):
    """Test cases for FirstTimeBuyerDiscountStrategy."""
    
    def setUp(self):
        """Set up test data."""
        self.strategy = FirstTimeBuyerDiscountStrategy()
        
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
            is_first_time_buyer=True
        )
    
    def test_first_time_buyer_gets_discount(self):
        """Test first-time buyer receives 15% discount."""
        subtotal = Decimal('1000.00')
        context = {'customer': self.customer}
        
        discount = self.strategy.calculate_discount(subtotal, context)
        
        expected = Decimal('150.00')  # 15% of 1000
        self.assertEqual(discount, expected)
    
    def test_returning_customer_no_discount(self):
        """Test returning customer does not get discount."""
        self.customer.is_first_time_buyer = False
        self.customer.save()
        
        subtotal = Decimal('1000.00')
        context = {'customer': self.customer}
        
        discount = self.strategy.calculate_discount(subtotal, context)
        
        self.assertEqual(discount, Decimal('0.00'))
    
    def test_no_customer_no_discount(self):
        """Test no discount when customer is None."""
        subtotal = Decimal('1000.00')
        context = {'customer': None}
        
        discount = self.strategy.calculate_discount(subtotal, context)
        
        self.assertEqual(discount, Decimal('0.00'))
    
    def test_is_applicable_for_first_time_buyer(self):
        """Test strategy is applicable for first-time buyers."""
        context = {'customer': self.customer}
        
        self.assertTrue(self.strategy.is_applicable(context))
    
    def test_not_applicable_for_returning_customer(self):
        """Test strategy not applicable for returning customers."""
        self.customer.is_first_time_buyer = False
        self.customer.save()
        
        context = {'customer': self.customer}
        
        self.assertFalse(self.strategy.is_applicable(context))


class TestDiscountContext(TestCase):
    """Test cases for DiscountContext."""
    
    def setUp(self):
        """Set up test data."""
        self.context = DiscountContext()
        
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
            is_first_time_buyer=True
        )
        
        # Create test coupon
        self.coupon = Coupon.objects.create(
            code='SAVE20',
            discount_type='percentage',
            discount_value=Decimal('20'),
            max_usage=100,
            min_purchase=Decimal('0.00'),
            expiry_date=timezone.now() + timedelta(days=30),
            is_active=True
        )
    
    def test_add_strategy(self):
        """Test adding strategies to context."""
        self.context.add_strategy(CouponDiscountStrategy())
        self.context.add_strategy(OrderValueDiscountStrategy())
        
        self.assertEqual(self.context.get_strategy_count(), 2)
    
    def test_strategies_sorted_by_priority(self):
        """Test strategies are sorted by priority."""
        self.context.add_strategy(FirstTimeBuyerDiscountStrategy())  # Priority 90
        self.context.add_strategy(CouponDiscountStrategy())  # Priority 10
        self.context.add_strategy(OrderValueDiscountStrategy())  # Priority 50
        
        strategies = self.context.get_strategies()
        priorities = [s.get_priority() for s in strategies]
        
        self.assertEqual(priorities, [10, 50, 90])
    
    def test_calculate_total_discount_multiple_strategies(self):
        """Test calculating total discount with multiple strategies."""
        self.context.add_strategy(CouponDiscountStrategy())
        self.context.add_strategy(OrderValueDiscountStrategy())
        self.context.add_strategy(FirstTimeBuyerDiscountStrategy())
        
        subtotal = Decimal('2000.00')
        context_data = {
            'customer': self.customer,
            'coupon': self.coupon
        }
        
        total_discount = self.context.calculate_total_discount(subtotal, context_data)
        
        # Expected: 20% coupon (400) + 10% order value (200) + 15% first-time (300) = 900
        expected = Decimal('900.00')
        self.assertEqual(total_discount, expected)
    
    def test_get_discount_breakdown(self):
        """Test getting detailed discount breakdown."""
        self.context.add_strategy(CouponDiscountStrategy())
        self.context.add_strategy(OrderValueDiscountStrategy())
        
        subtotal = Decimal('2000.00')
        context_data = {
            'customer': self.customer,
            'coupon': self.coupon
        }
        
        breakdown = self.context.get_discount_breakdown(subtotal, context_data)
        
        self.assertEqual(len(breakdown), 2)
        self.assertTrue(all(item['applicable'] for item in breakdown))
    
    def test_create_default_context(self):
        """Test creating default context with all strategies."""
        default_context = DiscountContext.create_default_context()
        
        self.assertEqual(default_context.get_strategy_count(), 3)


class TestDiscountService(TestCase):
    """Test cases for DiscountService."""
    
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
            is_first_time_buyer=True
        )
        
        # Create test coupon
        self.coupon = Coupon.objects.create(
            code='SAVE500',
            discount_type='fixed',
            discount_value=Decimal('500.00'),
            max_usage=100,
            min_purchase=Decimal('1000.00'),
            expiry_date=timezone.now() + timedelta(days=30),
            is_active=True
        )
    
    def test_calculate_total_discount(self):
        """Test calculating total discount through service."""
        service = DiscountService(
            subtotal=Decimal('2000.00'),
            customer=self.customer,
            coupon=self.coupon
        )
        
        total_discount = service.calculate_total_discount()
        
        # Expected: 500 (coupon) + 200 (10% order value) + 300 (15% first-time) = 1000
        expected = Decimal('1000.00')
        self.assertEqual(total_discount, expected)
    
    def test_calculate_individual_discounts(self):
        """Test calculating individual discount types."""
        service = DiscountService(
            subtotal=Decimal('2000.00'),
            customer=self.customer,
            coupon=self.coupon
        )
        
        coupon_discount = service.calculate_coupon_discount()
        order_value_discount = service.calculate_order_value_discount()
        first_time_discount = service.calculate_first_time_discount()
        
        self.assertEqual(coupon_discount, Decimal('500.00'))
        self.assertEqual(order_value_discount, Decimal('200.00'))
        self.assertEqual(first_time_discount, Decimal('300.00'))
    
    def test_get_breakdown(self):
        """Test getting discount breakdown."""
        service = DiscountService(
            subtotal=Decimal('2000.00'),
            customer=self.customer,
            coupon=self.coupon
        )
        
        breakdown = service.get_breakdown()
        
        self.assertEqual(len(breakdown), 3)
        self.assertTrue(all(item['applicable'] for item in breakdown))

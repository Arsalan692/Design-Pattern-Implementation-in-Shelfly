"""
Unit Tests for Repository Pattern
=================================

Tests for data access repositories.
"""

from decimal import Decimal
from datetime import datetime, timedelta
from django.test import TestCase
from django.contrib.auth.models import User

from bookstore.models import Customer, Book, Order, OrderItem, Coupon, CouponUsage
from bookstore.repositories import (
    BookRepository,
    OrderRepository,
    CustomerRepository,
    CouponRepository
)


class TestBookRepository(TestCase):
    """Test cases for BookRepository."""

    def setUp(self):
        """Set up test data."""
        self.repo = BookRepository()

        self.book1 = Book.objects.create(
            title='Python Programming',
            author='John Doe',
            category='Programming',
            price=Decimal('500.00'),
            stock=10,
            isbn='1234567890123'
        )

        self.book2 = Book.objects.create(
            title='Django Web Development',
            author='Jane Smith',
            category='Programming',
            price=Decimal('750.00'),
            stock=5,
            isbn='9876543210987'
        )

        self.book3 = Book.objects.create(
            title='Data Science Basics',
            author='John Doe',
            category='Data Science',
            price=Decimal('1000.00'),
            stock=0,
            isbn='1111222233334'
        )

    def test_get_all(self):
        """Test getting all books."""
        books = self.repo.get_all()
        self.assertEqual(books.count(), 3)

    def test_get_by_id(self):
        """Test getting book by ID."""
        book = self.repo.get_by_id(self.book1.id)
        self.assertEqual(book.title, 'Python Programming')

    def test_search_by_title(self):
        """Test searching books by title."""
        books = self.repo.search('Python')
        self.assertEqual(books.count(), 1)
        self.assertEqual(books.first().title, 'Python Programming')

    def test_search_by_author(self):
        """Test searching books by author."""
        books = self.repo.search('John Doe')
        self.assertEqual(books.count(), 2)

    def test_get_by_category(self):
        """Test getting books by category."""
        books = self.repo.get_by_category('Programming')
        self.assertEqual(books.count(), 2)

    def test_get_by_price_range(self):
        """Test getting books by price range."""
        books = self.repo.get_by_price_range(
            min_price=Decimal('500.00'),
            max_price=Decimal('800.00')
        )
        self.assertEqual(books.count(), 2)

    def test_get_in_stock(self):
        """Test getting books in stock."""
        books = self.repo.get_in_stock()
        self.assertEqual(books.count(), 2)

    def test_get_out_of_stock(self):
        """Test getting out of stock books."""
        books = self.repo.get_out_of_stock()
        self.assertEqual(books.count(), 1)

    def test_get_low_stock(self):
        """Test getting low stock books."""
        books = self.repo.get_low_stock(threshold=5)
        self.assertEqual(books.count(), 1)
        self.assertEqual(books.first().title, 'Django Web Development')

    def test_is_available(self):
        """Test checking book availability."""
        self.assertTrue(self.repo.is_available(self.book1.id, quantity=5))
        self.assertFalse(self.repo.is_available(self.book1.id, quantity=20))
        self.assertFalse(self.repo.is_available(self.book3.id, quantity=1))

    def test_reduce_stock(self):
        """Test reducing book stock."""
        initial_stock = self.book1.stock
        success = self.repo.reduce_stock(self.book1.id, 3)

        self.assertTrue(success)
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.stock, initial_stock - 3)

    def test_increase_stock(self):
        """Test increasing book stock."""
        initial_stock = self.book1.stock
        success = self.repo.increase_stock(self.book1.id, 5)

        self.assertTrue(success)
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.stock, initial_stock + 5)

    def test_get_by_isbn(self):
        """Test getting book by ISBN."""
        book = self.repo.get_by_isbn('1234567890123')
        self.assertEqual(book.title, 'Python Programming')

    def test_get_all_categories(self):
        """Test getting all categories."""
        categories = self.repo.get_all_categories()
        self.assertIn('Programming', categories)
        self.assertIn('Data Science', categories)

    def test_get_all_authors(self):
        """Test getting all authors."""
        authors = self.repo.get_all_authors()
        self.assertIn('John Doe', authors)
        self.assertIn('Jane Smith', authors)


class TestOrderRepository(TestCase):
    """Test cases for OrderRepository."""

    def setUp(self):
        """Set up test data."""
        self.repo = OrderRepository()

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

        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            category='Fiction',
            price=Decimal('500.00'),
            stock=10
        )

        self.order1 = Order.objects.create(
            customer=self.customer,
            status='Pending',
            shipping_fee=Decimal('50.00')
        )

        self.order2 = Order.objects.create(
            customer=self.customer,
            status='Confirmed',
            shipping_fee=Decimal('50.00')
        )

        self.order3 = Order.objects.create(
            customer=self.customer,
            status='Delivered',
            shipping_fee=Decimal('50.00')
        )

        for order in [self.order1, self.order2, self.order3]:
            OrderItem.objects.create(
                order=order,
                book=self.book,
                quantity=2,
                unit_price=self.book.price,
                subtotal=self.book.price * 2
            )

    def test_get_by_customer(self):
        """Test getting orders by customer."""
        orders = self.repo.get_by_customer(self.customer)
        self.assertEqual(orders.count(), 3)

    def test_get_by_status(self):
        """Test getting orders by status."""
        orders = self.repo.get_by_status('Pending')
        self.assertEqual(orders.count(), 1)

    def test_get_pending_orders(self):
        """Test getting pending orders."""
        orders = self.repo.get_pending_orders()
        self.assertEqual(orders.count(), 1)

    def test_get_confirmed_orders(self):
        """Test getting confirmed orders."""
        orders = self.repo.get_confirmed_orders()
        self.assertEqual(orders.count(), 1)

    def test_update_status(self):
        """Test updating order status."""
        success = self.repo.update_status(self.order1.id, 'Confirmed')

        self.assertTrue(success)
        self.order1.refresh_from_db()
        self.assertEqual(self.order1.status, 'Confirmed')

    def test_can_be_cancelled(self):
        """Test checking if order can be cancelled."""
        self.assertTrue(self.repo.can_be_cancelled(self.order1.id))
        self.assertTrue(self.repo.can_be_cancelled(self.order2.id))
        self.assertFalse(self.repo.can_be_cancelled(self.order3.id))

    def test_cancel_order(self):
        """Test cancelling an order."""
        success = self.repo.cancel_order(self.order1.id, reason='Changed mind')

        self.assertTrue(success)
        self.order1.refresh_from_db()
        self.assertEqual(self.order1.status, 'Cancelled')

    def test_get_customer_order_count(self):
        """Test getting customer order count."""
        count = self.repo.get_customer_order_count(self.customer)
        self.assertEqual(count, 3)

    def test_get_order_statistics(self):
        """Test getting order statistics."""
        stats = self.repo.get_order_statistics()

        self.assertEqual(stats['total_orders'], 3)
        self.assertEqual(stats['pending'], 1)
        self.assertEqual(stats['confirmed'], 1)
        self.assertEqual(stats['delivered'], 1)


class TestCustomerRepository(TestCase):
    """Test cases for CustomerRepository."""

    def setUp(self):
        """Set up test data."""
        self.repo = CustomerRepository()

        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='pass123'
        )
        self.customer1 = Customer.objects.create(
            user=self.user1,
            phone='1111111111',
            address='Address 1',
            is_first_time_buyer=True
        )

        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123'
        )
        self.customer2 = Customer.objects.create(
            user=self.user2,
            phone='2222222222',
            address='Address 2',
            is_first_time_buyer=False
        )

    def test_get_by_user(self):
        """Test getting customer by user."""
        customer = self.repo.get_by_user(self.user1)
        self.assertEqual(customer.phone, '1111111111')

    def test_get_by_username(self):
        """Test getting customer by username."""
        customer = self.repo.get_by_username('user1')
        self.assertEqual(customer.phone, '1111111111')

    def test_get_by_email(self):
        """Test getting customer by email."""
        customer = self.repo.get_by_email('user1@example.com')
        self.assertEqual(customer.phone, '1111111111')

    def test_get_first_time_buyers(self):
        """Test getting first-time buyers."""
        customers = self.repo.get_first_time_buyers()
        self.assertEqual(customers.count(), 1)

    def test_get_returning_customers(self):
        """Test getting returning customers."""
        customers = self.repo.get_returning_customers()
        self.assertEqual(customers.count(), 1)

    def test_update_profile(self):
        """Test updating customer profile."""
        customer = self.repo.update_profile(
            self.customer1.id,
            phone='9999999999',
            address='New Address'
        )

        self.assertEqual(customer.phone, '9999999999')
        self.assertEqual(customer.address, 'New Address')

    def test_mark_as_returning_customer(self):
        """Test marking customer as returning."""
        success = self.repo.mark_as_returning_customer(self.customer1.id)

        self.assertTrue(success)
        self.customer1.refresh_from_db()
        self.assertFalse(self.customer1.is_first_time_buyer)

    def test_get_customer_statistics(self):
        """Test getting customer statistics."""
        stats = self.repo.get_customer_statistics()

        self.assertEqual(stats['total_customers'], 2)
        self.assertEqual(stats['first_time_buyers'], 1)
        self.assertEqual(stats['returning_customers'], 1)

    def test_search_customers(self):
        """Test searching customers."""
        customers = self.repo.search_customers('user1')
        self.assertEqual(customers.count(), 1)


class TestCouponRepository(TestCase):
    """Test cases for CouponRepository."""

    def setUp(self):
        """Set up test data."""
        self.repo = CouponRepository()

        self.coupon1 = Coupon.objects.create(
            code='ACTIVE20',
            discount_type='percentage',
            discount_value=Decimal('20'),
            max_usage=100,
            min_purchase=Decimal('500.00'),
            expiry_date=datetime.now() + timedelta(days=30),
            is_active=True
        )

        self.coupon2 = Coupon.objects.create(
            code='EXPIRED10',
            discount_type='fixed',
            discount_value=Decimal('100'),
            max_usage=50,
            min_purchase=Decimal('1000.00'),
            expiry_date=datetime.now() - timedelta(days=1),
            is_active=True
        )

        self.coupon3 = Coupon.objects.create(
            code='INACTIVE15',
            discount_type='percentage',
            discount_value=Decimal('15'),
            max_usage=100,
            min_purchase=Decimal('0.00'),
            expiry_date=datetime.now() + timedelta(days=30),
            is_active=False
        )

    def test_get_by_code(self):
        """Test getting coupon by code."""
        coupon = self.repo.get_by_code('ACTIVE20')
        self.assertEqual(coupon.discount_value, Decimal('20'))

    def test_get_active_coupons(self):
        """Test getting active coupons."""
        coupons = self.repo.get_active_coupons()
        self.assertEqual(coupons.count(), 2)

    def test_get_inactive_coupons(self):
        """Test getting inactive coupons."""
        coupons = self.repo.get_inactive_coupons()
        self.assertEqual(coupons.count(), 1)

    def test_get_expired_coupons(self):
        """Test getting expired coupons."""
        coupons = self.repo.get_expired_coupons()
        self.assertEqual(coupons.count(), 1)

    def test_get_valid_coupons(self):
        """Test getting valid coupons."""
        coupons = self.repo.get_valid_coupons()
        self.assertEqual(coupons.count(), 1)

    def test_is_valid_active_coupon(self):
        """Test validating active coupon."""
        is_valid, msg = self.repo.is_valid('ACTIVE20')
        self.assertTrue(is_valid)

    def test_is_valid_expired_coupon(self):
        """Test validating expired coupon."""
        is_valid, msg = self.repo.is_valid('EXPIRED10')
        self.assertFalse(is_valid)
        self.assertIn('expired', msg.lower())

    def test_is_valid_inactive_coupon(self):
        """Test validating inactive coupon."""
        is_valid, msg = self.repo.is_valid('INACTIVE15')
        self.assertFalse(is_valid)
        self.assertIn('inactive', msg.lower())

    def test_can_be_used(self):
        """Test checking if coupon can be used."""
        can_use, msg = self.repo.can_be_used('ACTIVE20', Decimal('1000.00'))
        self.assertTrue(can_use)

    def test_can_be_used_below_minimum(self):
        """Test coupon cannot be used below minimum purchase."""
        can_use, msg = self.repo.can_be_used('ACTIVE20', Decimal('100.00'))
        self.assertFalse(can_use)
        self.assertIn('Minimum purchase', msg)

    def test_deactivate_coupon(self):
        """Test deactivating coupon."""
        success = self.repo.deactivate_coupon(self.coupon1.id)

        self.assertTrue(success)
        self.coupon1.refresh_from_db()
        self.assertFalse(self.coupon1.is_active)

    def test_activate_coupon(self):
        """Test activating coupon."""
        success = self.repo.activate_coupon(self.coupon3.id)

        self.assertTrue(success)
        self.coupon3.refresh_from_db()
        self.assertTrue(self.coupon3.is_active)

    def test_get_coupon_statistics(self):
        """Test getting coupon statistics."""
        stats = self.repo.get_coupon_statistics()

        self.assertEqual(stats['total_coupons'], 3)
        self.assertEqual(stats['active_coupons'], 2)
        self.assertEqual(stats['expired_coupons'], 1)
"""
Unit Tests for Observer Pattern
================================

Tests for Observer Pattern implementation including:
- Observer interface
- OrderSubject
- EmailNotificationObserver
- LogObserver
- InventoryObserver
"""

from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
from bookstore.models import Customer, Book, Order, Payment
from bookstore.observers.observer import Observer
from bookstore.observers.order_subject import OrderSubject
from bookstore.observers.email_observer import EmailNotificationObserver
from bookstore.observers.log_observer import LogObserver
from bookstore.observers.inventory_observer import InventoryObserver


class MockObserver(Observer):
    """Mock observer for testing."""
    
    def __init__(self):
        self.events = []
    
    def update(self, event_type: str, data: dict) -> None:
        self.events.append({'type': event_type, 'data': data})


class TestOrderSubject(TestCase):
    """Test OrderSubject class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.subject = OrderSubject()
        self.observer1 = MockObserver()
        self.observer2 = MockObserver()
    
    def test_attach_observer(self):
        """Test attaching an observer."""
        self.subject.attach(self.observer1)
        self.assertEqual(self.subject.get_observer_count(), 1)
        self.assertIn(self.observer1, self.subject.get_observers())
    
    def test_attach_duplicate_observer(self):
        """Test attaching the same observer twice."""
        self.subject.attach(self.observer1)
        self.subject.attach(self.observer1)
        self.assertEqual(self.subject.get_observer_count(), 1)
    
    def test_detach_observer(self):
        """Test detaching an observer."""
        self.subject.attach(self.observer1)
        self.subject.detach(self.observer1)
        self.assertEqual(self.subject.get_observer_count(), 0)
    
    def test_detach_nonexistent_observer(self):
        """Test detaching an observer that wasn't attached."""
        self.subject.detach(self.observer1)
        self.assertEqual(self.subject.get_observer_count(), 0)
    
    def test_notify_single_observer(self):
        """Test notifying a single observer."""
        self.subject.attach(self.observer1)
        self.subject.notify('test_event', {'key': 'value'})
        
        self.assertEqual(len(self.observer1.events), 1)
        self.assertEqual(self.observer1.events[0]['type'], 'test_event')
        self.assertEqual(self.observer1.events[0]['data']['key'], 'value')
    
    def test_notify_multiple_observers(self):
        """Test notifying multiple observers."""
        self.subject.attach(self.observer1)
        self.subject.attach(self.observer2)
        self.subject.notify('test_event', {'key': 'value'})
        
        self.assertEqual(len(self.observer1.events), 1)
        self.assertEqual(len(self.observer2.events), 1)
    
    def test_get_observers(self):
        """Test getting list of observers."""
        self.subject.attach(self.observer1)
        self.subject.attach(self.observer2)
        
        observers = self.subject.get_observers()
        self.assertEqual(len(observers), 2)
        self.assertIn(self.observer1, observers)
        self.assertIn(self.observer2, observers)


class TestOrderSubjectWithModels(TestCase):
    """Test OrderSubject with Django models."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.subject = OrderSubject()
        self.observer = MockObserver()
        self.subject.attach(self.observer)
        
        # Create test user and customer
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            phone='1234567890',
            address='Test Address'
        )
        
        # Create test book
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            price=Decimal('500.00'),
            stock=10
        )
        
        # Create test order (without total_amount - it's a property)
        self.order = Order.objects.create(
            customer=self.customer,
            status='Pending'
        )
    
    def test_notify_order_placed(self):
        """Test order placed notification."""
        self.subject.notify_order_placed(self.order)
        
        self.assertEqual(len(self.observer.events), 1)
        event = self.observer.events[0]
        self.assertEqual(event['type'], 'order_placed')
        self.assertEqual(event['data']['order_id'], self.order.id)
        self.assertEqual(event['data']['customer'], self.customer)
    
    def test_notify_order_confirmed(self):
        """Test order confirmed notification."""
        self.subject.notify_order_confirmed(self.order)
        
        self.assertEqual(len(self.observer.events), 1)
        event = self.observer.events[0]
        self.assertEqual(event['type'], 'order_confirmed')
    
    def test_notify_order_shipped(self):
        """Test order shipped notification."""
        self.subject.notify_order_shipped(self.order)
        
        self.assertEqual(len(self.observer.events), 1)
        event = self.observer.events[0]
        self.assertEqual(event['type'], 'order_shipped')
    
    def test_notify_order_delivered(self):
        """Test order delivered notification."""
        self.subject.notify_order_delivered(self.order)
        
        self.assertEqual(len(self.observer.events), 1)
        event = self.observer.events[0]
        self.assertEqual(event['type'], 'order_delivered')
    
    def test_notify_order_cancelled(self):
        """Test order cancelled notification."""
        self.subject.notify_order_cancelled(self.order, 'Customer request')
        
        self.assertEqual(len(self.observer.events), 1)
        event = self.observer.events[0]
        self.assertEqual(event['type'], 'order_cancelled')
        self.assertEqual(event['data']['reason'], 'Customer request')
    
    def test_notify_payment_received(self):
        """Test payment received notification."""
        payment = Payment.objects.create(
            order=self.order,
            amount=Decimal('500.00'),
            method='Card'
        )
        
        self.subject.notify_payment_received(self.order, payment)
        
        self.assertEqual(len(self.observer.events), 1)
        event = self.observer.events[0]
        self.assertEqual(event['type'], 'payment_received')
        self.assertEqual(event['data']['amount'], Decimal('500.00'))


class TestEmailNotificationObserver(TestCase):
    """Test EmailNotificationObserver class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.observer = EmailNotificationObserver(enabled=True)
        
        # Create test user and customer
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            phone='1234567890',
            address='Test Address'
        )
        
        # Create test order (without total_amount - it's a property)
        self.order = Order.objects.create(
            customer=self.customer,
            status='Pending'
        )
    
    def test_observer_enabled(self):
        """Test that observer is enabled."""
        self.assertTrue(self.observer.enabled)
    
    def test_observer_disabled(self):
        """Test that observer can be disabled."""
        observer = EmailNotificationObserver(enabled=False)
        observer.update('order_placed', {
            'order_id': 1,
            'customer': self.customer,
            'total_amount': Decimal('500.00'),
            'status': 'Pending'
        })
        self.assertEqual(len(observer.sent_emails), 0)
    
    def test_order_placed_email(self):
        """Test order placed email."""
        self.observer.update('order_placed', {
            'order_id': self.order.id,
            'customer': self.customer,
            'total_amount': self.order.total_amount,
            'status': 'Pending'
        })
        
        self.assertEqual(len(self.observer.sent_emails), 1)
        email = self.observer.sent_emails[0]
        self.assertEqual(email['to'], 'test@example.com')
        self.assertIn('Order #', email['subject'])
        self.assertIn('Placed Successfully', email['subject'])
    
    def test_order_confirmed_email(self):
        """Test order confirmed email."""
        self.observer.update('order_confirmed', {
            'order_id': self.order.id,
            'customer': self.customer,
            'total_amount': self.order.total_amount
        })
        
        self.assertEqual(len(self.observer.sent_emails), 1)
        email = self.observer.sent_emails[0]
        self.assertIn('Confirmed', email['subject'])
    
    def test_order_shipped_email(self):
        """Test order shipped email."""
        self.observer.update('order_shipped', {
            'order_id': self.order.id,
            'customer': self.customer
        })
        
        self.assertEqual(len(self.observer.sent_emails), 1)
        email = self.observer.sent_emails[0]
        self.assertIn('Shipped', email['subject'])
    
    def test_order_delivered_email(self):
        """Test order delivered email."""
        self.observer.update('order_delivered', {
            'order_id': self.order.id,
            'customer': self.customer
        })
        
        self.assertEqual(len(self.observer.sent_emails), 1)
        email = self.observer.sent_emails[0]
        self.assertIn('Delivered', email['subject'])
    
    def test_order_cancelled_email(self):
        """Test order cancelled email."""
        self.observer.update('order_cancelled', {
            'order_id': self.order.id,
            'customer': self.customer,
            'reason': 'Customer request'
        })
        
        self.assertEqual(len(self.observer.sent_emails), 1)
        email = self.observer.sent_emails[0]
        self.assertIn('Cancelled', email['subject'])
        self.assertIn('Customer request', email['body'])
    
    def test_payment_received_email(self):
        """Test payment received email."""
        payment = Payment.objects.create(
            order=self.order,
            amount=Decimal('500.00'),
            method='Card'
        )
        
        self.observer.update('payment_received', {
            'order_id': self.order.id,
            'customer': self.customer,
            'amount': Decimal('500.00'),
            'method': 'Card'
        })
        
        self.assertEqual(len(self.observer.sent_emails), 1)
        email = self.observer.sent_emails[0]
        self.assertIn('Payment Received', email['subject'])
    
    def test_unknown_event_type(self):
        """Test handling of unknown event type."""
        self.observer.update('unknown_event', {})
        self.assertEqual(len(self.observer.sent_emails), 0)
    
    def test_get_sent_emails(self):
        """Test getting sent emails."""
        self.observer.update('order_placed', {
            'order_id': self.order.id,
            'customer': self.customer,
            'total_amount': self.order.total_amount,
            'status': 'Pending'
        })
        
        emails = self.observer.get_sent_emails()
        self.assertEqual(len(emails), 1)
    
    def test_clear_sent_emails(self):
        """Test clearing sent emails."""
        self.observer.update('order_placed', {
            'order_id': self.order.id,
            'customer': self.customer,
            'total_amount': self.order.total_amount,
            'status': 'Pending'
        })
        
        self.observer.clear_sent_emails()
        self.assertEqual(len(self.observer.sent_emails), 0)


class TestLogObserver(TestCase):
    """Test LogObserver class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.observer = LogObserver(enabled=True)
        
        # Create test user and customer
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            phone='1234567890',
            address='Test Address'
        )
        
        # Create test order (without total_amount - it's a property)
        self.order = Order.objects.create(
            customer=self.customer,
            status='Pending'
        )
    
    def test_observer_enabled(self):
        """Test that observer is enabled."""
        self.assertTrue(self.observer.enabled)
    
    def test_observer_disabled(self):
        """Test that observer can be disabled."""
        observer = LogObserver(enabled=False)
        observer.update('order_placed', {
            'order_id': 1,
            'customer': self.customer,
            'total_amount': Decimal('0.00'),
            'status': 'Pending'
        })
        self.assertEqual(len(observer.logs), 0)
    
    def test_log_order_placed(self):
        """Test logging order placed event."""
        self.observer.update('order_placed', {
            'order_id': self.order.id,
            'customer': self.customer,
            'total_amount': self.order.total_amount,
            'status': 'Pending'
        })
        
        self.assertEqual(len(self.observer.logs), 1)
        log = self.observer.logs[0]
        self.assertEqual(log['event_type'], 'order_placed')
        self.assertIn('timestamp', log)
    
    def test_get_logs(self):
        """Test getting logs."""
        self.observer.update('order_placed', {
            'order_id': self.order.id,
            'customer': self.customer,
            'total_amount': self.order.total_amount,
            'status': 'Pending'
        })
        
        logs = self.observer.get_logs()
        self.assertEqual(len(logs), 1)
    
    def test_clear_logs(self):
        """Test clearing logs."""
        self.observer.update('order_placed', {
            'order_id': self.order.id,
            'customer': self.customer,
            'total_amount': self.order.total_amount,
            'status': 'Pending'
        })
        
        self.observer.clear_logs()
        self.assertEqual(len(self.observer.logs), 0)
    
    def test_get_logs_by_event_type(self):
        """Test filtering logs by event type."""
        self.observer.update('order_placed', {
            'order_id': self.order.id,
            'customer': self.customer,
            'total_amount': self.order.total_amount,
            'status': 'Pending'
        })
        self.observer.update('order_confirmed', {
            'order_id': self.order.id,
            'customer': self.customer,
            'total_amount': self.order.total_amount
        })
        
        placed_logs = self.observer.get_logs_by_event_type('order_placed')
        self.assertEqual(len(placed_logs), 1)
        
        confirmed_logs = self.observer.get_logs_by_event_type('order_confirmed')
        self.assertEqual(len(confirmed_logs), 1)
    
    def test_get_logs_for_order(self):
        """Test getting logs for specific order."""
        self.observer.update('order_placed', {
            'order_id': self.order.id,
            'customer': self.customer,
            'total_amount': self.order.total_amount,
            'status': 'Pending'
        })
        self.observer.update('order_confirmed', {
            'order_id': self.order.id,
            'customer': self.customer,
            'total_amount': self.order.total_amount
        })
        
        order_logs = self.observer.get_logs_for_order(self.order.id)
        self.assertEqual(len(order_logs), 2)


class TestInventoryObserver(TestCase):
    """Test InventoryObserver class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.observer = InventoryObserver(low_stock_threshold=5, enabled=True)
        
        # Create test user and customer
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            phone='1234567890',
            address='Test Address'
        )
        
        # Create test book
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            price=Decimal('500.00'),
            stock=10
        )
        
        # Create test order (without total_amount - it's a property)
        self.order = Order.objects.create(
            customer=self.customer,
            status='Pending'
        )
    
    def test_observer_enabled(self):
        """Test that observer is enabled."""
        self.assertTrue(self.observer.enabled)
    
    def test_observer_disabled(self):
        """Test that observer can be disabled."""
        observer = InventoryObserver(enabled=False)
        observer.update('order_placed', {
            'order_id': 1,
            'customer': self.customer
        })
        self.assertEqual(len(observer.alerts), 0)
    
    def test_order_placed_triggers_check(self):
        """Test that order placed triggers inventory check."""
        self.observer.update('order_placed', {
            'order_id': self.order.id,
            'customer': self.customer
        })
        
        self.assertEqual(len(self.observer.alerts), 1)
        alert = self.observer.alerts[0]
        self.assertEqual(alert['type'], 'order_placed')
    
    def test_order_cancelled_triggers_check(self):
        """Test that order cancelled triggers inventory check."""
        self.observer.update('order_cancelled', {
            'order_id': self.order.id,
            'customer': self.customer,
            'reason': 'Test'
        })
        
        self.assertEqual(len(self.observer.alerts), 1)
        alert = self.observer.alerts[0]
        self.assertEqual(alert['type'], 'order_cancelled')
    
    def test_low_stock_alert(self):
        """Test low stock alert."""
        self.book.stock = 3
        self.observer.check_book_stock(self.book)
        
        alerts = self.observer.get_low_stock_alerts()
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]['book_id'], self.book.id)
    
    def test_out_of_stock_alert(self):
        """Test out of stock alert."""
        self.book.stock = 0
        self.observer.check_book_stock(self.book)
        
        alerts = self.observer.get_out_of_stock_alerts()
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]['book_id'], self.book.id)
    
    def test_no_alert_for_sufficient_stock(self):
        """Test no alert when stock is sufficient."""
        self.book.stock = 10
        self.observer.check_book_stock(self.book)
        
        self.assertEqual(len(self.observer.get_low_stock_alerts()), 0)
        self.assertEqual(len(self.observer.get_out_of_stock_alerts()), 0)
    
    def test_get_alerts(self):
        """Test getting all alerts."""
        self.observer.update('order_placed', {
            'order_id': self.order.id,
            'customer': self.customer
        })
        
        alerts = self.observer.get_alerts()
        self.assertEqual(len(alerts), 1)
    
    def test_clear_alerts(self):
        """Test clearing alerts."""
        self.observer.update('order_placed', {
            'order_id': self.order.id,
            'customer': self.customer
        })
        
        self.observer.clear_alerts()
        self.assertEqual(len(self.observer.alerts), 0)

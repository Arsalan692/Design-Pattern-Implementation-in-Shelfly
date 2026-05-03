"""
Unit Tests for Singleton Pattern
=================================

Tests for Singleton Pattern implementation including:
- ConfigManager
- NotificationManager
- Thread safety
- Singleton behavior
"""

from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
import threading
from bookstore.models import Customer, Order
from bookstore.managers.config_manager import ConfigManager
from bookstore.managers.notification_manager import NotificationManager
from bookstore.observers.email_observer import EmailNotificationObserver
from bookstore.observers.log_observer import LogObserver


class TestConfigManagerSingleton(TestCase):
    """Test ConfigManager singleton behavior."""
    
    def setUp(self):
        """Reset singleton before each test."""
        ConfigManager.reset_instance()
    
    def tearDown(self):
        """Reset singleton after each test."""
        ConfigManager.reset_instance()
    
    def test_singleton_instance(self):
        """Test that only one instance is created."""
        config1 = ConfigManager()
        config2 = ConfigManager()
        
        self.assertIs(config1, config2)
    
    def test_singleton_across_modules(self):
        """Test singleton works across different references."""
        config1 = ConfigManager()
        config1.set('test_key', 'test_value')
        
        config2 = ConfigManager()
        self.assertEqual(config2.get('test_key'), 'test_value')
    
    def test_thread_safety(self):
        """Test that singleton is thread-safe."""
        instances = []
        
        def create_instance():
            config = ConfigManager()
            instances.append(config)
        
        threads = [threading.Thread(target=create_instance) for _ in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        # All instances should be the same
        first_instance = instances[0]
        for instance in instances:
            self.assertIs(instance, first_instance)
    
    def test_initialization_only_once(self):
        """Test that initialization happens only once."""
        config1 = ConfigManager()
        config1.set('test_key', 'test_value')
        
        config2 = ConfigManager()
        self.assertEqual(config2.get('test_key'), 'test_value')


class TestConfigManagerConfiguration(TestCase):
    """Test ConfigManager configuration methods."""
    
    def setUp(self):
        """Reset singleton and get instance."""
        ConfigManager.reset_instance()
        self.config = ConfigManager()
    
    def tearDown(self):
        """Reset singleton after each test."""
        ConfigManager.reset_instance()
    
    def test_default_configuration_loaded(self):
        """Test that default configuration is loaded."""
        shipping_config = self.config.get_shipping_config()
        self.assertIsNotNone(shipping_config)
        self.assertIn('free_shipping_threshold', shipping_config)
    
    def test_get_simple_key(self):
        """Test getting a simple configuration key."""
        self.config.set('test_key', 'test_value')
        self.assertEqual(self.config.get('test_key'), 'test_value')
    
    def test_get_nested_key(self):
        """Test getting a nested configuration key."""
        value = self.config.get('shipping.base_shipping_fee')
        self.assertEqual(value, Decimal('50.00'))
    
    def test_get_nonexistent_key(self):
        """Test getting a nonexistent key returns default."""
        value = self.config.get('nonexistent.key', 'default')
        self.assertEqual(value, 'default')
    
    def test_set_simple_key(self):
        """Test setting a simple configuration key."""
        self.config.set('new_key', 'new_value')
        self.assertEqual(self.config.get('new_key'), 'new_value')
    
    def test_set_nested_key(self):
        """Test setting a nested configuration key."""
        self.config.set('shipping.base_shipping_fee', Decimal('100.00'))
        self.assertEqual(self.config.get('shipping.base_shipping_fee'), Decimal('100.00'))
    
    def test_get_all_configuration(self):
        """Test getting all configuration."""
        all_config = self.config.get_all()
        self.assertIsInstance(all_config, dict)
        self.assertIn('shipping', all_config)
        self.assertIn('discounts', all_config)
    
    def test_reset_configuration(self):
        """Test resetting configuration to defaults."""
        self.config.set('test_key', 'test_value')
        self.config.reset()
        self.assertIsNone(self.config.get('test_key'))
    
    def test_get_shipping_config(self):
        """Test getting shipping configuration."""
        shipping = self.config.get_shipping_config()
        self.assertIn('free_shipping_threshold', shipping)
        self.assertIn('base_shipping_fee', shipping)
    
    def test_get_discount_config(self):
        """Test getting discount configuration."""
        discounts = self.config.get_discount_config()
        self.assertIn('order_value_tiers', discounts)
        self.assertIn('first_time_buyer_percentage', discounts)
    
    def test_get_inventory_config(self):
        """Test getting inventory configuration."""
        inventory = self.config.get_inventory_config()
        self.assertIn('low_stock_threshold', inventory)
    
    def test_get_order_config(self):
        """Test getting order configuration."""
        orders = self.config.get_order_config()
        self.assertIn('cancellable_statuses', orders)
    
    def test_get_payment_config(self):
        """Test getting payment configuration."""
        payment = self.config.get_payment_config()
        self.assertIn('supported_methods', payment)
    
    def test_get_notification_config(self):
        """Test getting notification configuration."""
        notifications = self.config.get_notification_config()
        self.assertIn('email_enabled', notifications)
    
    def test_get_business_rules(self):
        """Test getting business rules."""
        business = self.config.get_business_rules()
        self.assertIn('min_order_amount', business)
    
    def test_get_free_shipping_threshold(self):
        """Test getting free shipping threshold."""
        threshold = self.config.get_free_shipping_threshold()
        self.assertEqual(threshold, Decimal('5000.00'))
    
    def test_get_base_shipping_fee(self):
        """Test getting base shipping fee."""
        fee = self.config.get_base_shipping_fee()
        self.assertEqual(fee, Decimal('50.00'))
    
    def test_get_low_stock_threshold(self):
        """Test getting low stock threshold."""
        threshold = self.config.get_low_stock_threshold()
        self.assertEqual(threshold, 5)
    
    def test_get_first_time_buyer_discount(self):
        """Test getting first-time buyer discount."""
        discount = self.config.get_first_time_buyer_discount()
        self.assertEqual(discount, Decimal('15'))
    
    def test_get_order_value_tiers(self):
        """Test getting order value tiers."""
        tiers = self.config.get_order_value_tiers()
        self.assertIsInstance(tiers, list)
        self.assertGreater(len(tiers), 0)
    
    def test_is_email_enabled(self):
        """Test checking if email is enabled."""
        enabled = self.config.is_email_enabled()
        self.assertTrue(enabled)
    
    def test_get_cancellable_statuses(self):
        """Test getting cancellable statuses."""
        statuses = self.config.get_cancellable_statuses()
        self.assertIn('Pending', statuses)
        self.assertIn('Confirmed', statuses)


class TestNotificationManagerSingleton(TestCase):
    """Test NotificationManager singleton behavior."""
    
    def setUp(self):
        """Reset singletons before each test."""
        NotificationManager.reset_instance()
        ConfigManager.reset_instance()
    
    def tearDown(self):
        """Reset singletons after each test."""
        NotificationManager.reset_instance()
        ConfigManager.reset_instance()
    
    def test_singleton_instance(self):
        """Test that only one instance is created."""
        manager1 = NotificationManager()
        manager2 = NotificationManager()
        
        self.assertIs(manager1, manager2)
    
    def test_singleton_across_modules(self):
        """Test singleton works across different references."""
        manager1 = NotificationManager()
        initial_count = manager1.get_observer_count()
        
        manager2 = NotificationManager()
        self.assertEqual(manager2.get_observer_count(), initial_count)
    
    def test_thread_safety(self):
        """Test that singleton is thread-safe."""
        instances = []
        
        def create_instance():
            manager = NotificationManager()
            instances.append(manager)
        
        threads = [threading.Thread(target=create_instance) for _ in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        # All instances should be the same
        first_instance = instances[0]
        for instance in instances:
            self.assertIs(instance, first_instance)
    
    def test_initialization_only_once(self):
        """Test that initialization happens only once."""
        manager1 = NotificationManager()
        count1 = manager1.get_observer_count()
        
        manager2 = NotificationManager()
        count2 = manager2.get_observer_count()
        
        self.assertEqual(count1, count2)


class TestNotificationManagerObservers(TestCase):
    """Test NotificationManager observer management."""
    
    def setUp(self):
        """Reset singletons and get instance."""
        NotificationManager.reset_instance()
        ConfigManager.reset_instance()
        self.manager = NotificationManager()
    
    def tearDown(self):
        """Reset singletons after each test."""
        NotificationManager.reset_instance()
        ConfigManager.reset_instance()
    
    def test_default_observers_registered(self):
        """Test that default observers are registered."""
        count = self.manager.get_observer_count()
        self.assertGreater(count, 0)
    
    def test_get_observer_by_name(self):
        """Test getting observer by name."""
        email_observer = self.manager.get_observer('email')
        self.assertIsNotNone(email_observer)
        self.assertIsInstance(email_observer, EmailNotificationObserver)
    
    def test_get_all_observers(self):
        """Test getting all observers."""
        observers = self.manager.get_all_observers()
        self.assertIsInstance(observers, dict)
        self.assertIn('email', observers)
        self.assertIn('log', observers)
    
    def test_register_custom_observer(self):
        """Test registering a custom observer."""
        custom_observer = LogObserver()
        initial_count = self.manager.get_observer_count()
        
        self.manager.register_observer('custom', custom_observer)
        
        self.assertEqual(self.manager.get_observer_count(), initial_count + 1)
        self.assertIs(self.manager.get_observer('custom'), custom_observer)
    
    def test_unregister_observer(self):
        """Test unregistering an observer."""
        custom_observer = LogObserver()
        self.manager.register_observer('custom', custom_observer)
        initial_count = self.manager.get_observer_count()
        
        self.manager.unregister_observer('custom')
        
        self.assertEqual(self.manager.get_observer_count(), initial_count - 1)
        self.assertIsNone(self.manager.get_observer('custom'))
    
    def test_enable_observer(self):
        """Test enabling an observer."""
        result = self.manager.enable_observer('email')
        self.assertTrue(result)
        self.assertTrue(self.manager.is_observer_enabled('email'))
    
    def test_disable_observer(self):
        """Test disabling an observer."""
        result = self.manager.disable_observer('email')
        self.assertTrue(result)
        self.assertFalse(self.manager.is_observer_enabled('email'))
    
    def test_enable_nonexistent_observer(self):
        """Test enabling a nonexistent observer."""
        result = self.manager.enable_observer('nonexistent')
        self.assertFalse(result)
    
    def test_is_observer_enabled(self):
        """Test checking if observer is enabled."""
        enabled = self.manager.is_observer_enabled('email')
        self.assertIsInstance(enabled, bool)


class TestNotificationManagerNotifications(TestCase):
    """Test NotificationManager notification methods."""
    
    def setUp(self):
        """Reset singletons and create test data."""
        NotificationManager.reset_instance()
        ConfigManager.reset_instance()
        self.manager = NotificationManager()
        
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
    
    def tearDown(self):
        """Reset singletons after each test."""
        NotificationManager.reset_instance()
        ConfigManager.reset_instance()
    
    def test_notify_order_placed(self):
        """Test notifying order placed."""
        # Get log observer to verify notification
        log_observer = self.manager.get_observer('log')
        log_observer.clear_logs()
        
        self.manager.notify_order_placed(self.order)
        
        logs = log_observer.get_logs()
        self.assertGreater(len(logs), 0)
        self.assertEqual(logs[0]['event_type'], 'order_placed')
    
    def test_notify_order_confirmed(self):
        """Test notifying order confirmed."""
        log_observer = self.manager.get_observer('log')
        log_observer.clear_logs()
        
        self.manager.notify_order_confirmed(self.order)
        
        logs = log_observer.get_logs()
        self.assertGreater(len(logs), 0)
        self.assertEqual(logs[0]['event_type'], 'order_confirmed')
    
    def test_notify_order_shipped(self):
        """Test notifying order shipped."""
        log_observer = self.manager.get_observer('log')
        log_observer.clear_logs()
        
        self.manager.notify_order_shipped(self.order)
        
        logs = log_observer.get_logs()
        self.assertGreater(len(logs), 0)
        self.assertEqual(logs[0]['event_type'], 'order_shipped')
    
    def test_notify_order_delivered(self):
        """Test notifying order delivered."""
        log_observer = self.manager.get_observer('log')
        log_observer.clear_logs()
        
        self.manager.notify_order_delivered(self.order)
        
        logs = log_observer.get_logs()
        self.assertGreater(len(logs), 0)
        self.assertEqual(logs[0]['event_type'], 'order_delivered')
    
    def test_notify_order_cancelled(self):
        """Test notifying order cancelled."""
        log_observer = self.manager.get_observer('log')
        log_observer.clear_logs()
        
        self.manager.notify_order_cancelled(self.order, 'Customer request')
        
        logs = log_observer.get_logs()
        self.assertGreater(len(logs), 0)
        self.assertEqual(logs[0]['event_type'], 'order_cancelled')
    
    def test_notify_custom_event(self):
        """Test notifying custom event."""
        log_observer = self.manager.get_observer('log')
        log_observer.clear_logs()
        
        self.manager.notify_custom_event('custom_event', {'key': 'value'})
        
        logs = log_observer.get_logs()
        self.assertGreater(len(logs), 0)
        self.assertEqual(logs[0]['event_type'], 'custom_event')


class TestNotificationManagerUtilities(TestCase):
    """Test NotificationManager utility methods."""
    
    def setUp(self):
        """Reset singletons and get instance."""
        NotificationManager.reset_instance()
        ConfigManager.reset_instance()
        self.manager = NotificationManager()
    
    def tearDown(self):
        """Reset singletons after each test."""
        NotificationManager.reset_instance()
        ConfigManager.reset_instance()
    
    def test_clear_all_observers(self):
        """Test clearing all observers."""
        self.manager.clear_all_observers()
        self.assertEqual(self.manager.get_observer_count(), 0)
    
    def test_reset_observers(self):
        """Test resetting to default observers."""
        self.manager.clear_all_observers()
        self.assertEqual(self.manager.get_observer_count(), 0)
        
        self.manager.reset_observers()
        self.assertGreater(self.manager.get_observer_count(), 0)

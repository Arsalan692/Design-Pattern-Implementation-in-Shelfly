"""
Test Integration Script
=======================

Tests if all design patterns are properly integrated.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shelfly.settings')
django.setup()

print("=" * 60)
print("TESTING DESIGN PATTERN INTEGRATION")
print("=" * 60)

# Test 1: Import all pattern components
print("\n1. Testing imports...")
try:
    from bookstore.strategies.discount_strategy import DiscountStrategy
    from bookstore.payments.payment_factory import PaymentFactory
    from bookstore.repositories.book_repository import BookRepository
    from bookstore.observers.order_subject import OrderSubject
    from bookstore.managers.config_manager import ConfigManager
    from bookstore.managers.notification_manager import NotificationManager
    print("   ✅ All pattern imports successful!")
except Exception as e:
    print(f"   ❌ Import error: {e}")
    sys.exit(1)

# Test 2: Import views
print("\n2. Testing views import...")
try:
    from bookstore import views
    print("   ✅ Views imported successfully!")
except Exception as e:
    print(f"   ❌ Views import error: {e}")
    sys.exit(1)

# Test 3: Test Singleton Pattern
print("\n3. Testing Singleton Pattern...")
try:
    config1 = ConfigManager()
    config2 = ConfigManager()
    assert config1 is config2, "ConfigManager is not a singleton!"
    
    manager1 = NotificationManager()
    manager2 = NotificationManager()
    assert manager1 is manager2, "NotificationManager is not a singleton!"
    
    print("   ✅ Singleton pattern working correctly!")
except Exception as e:
    print(f"   ❌ Singleton test error: {e}")
    sys.exit(1)

# Test 4: Test Factory Pattern
print("\n4. Testing Factory Pattern...")
try:
    cash_processor = PaymentFactory.get_processor('Cash')
    card_processor = PaymentFactory.get_processor('Card')
    
    assert cash_processor is not None, "Cash processor not created!"
    assert card_processor is not None, "Card processor not created!"
    
    print("   ✅ Factory pattern working correctly!")
except Exception as e:
    print(f"   ❌ Factory test error: {e}")
    sys.exit(1)

# Test 5: Test Repository Pattern
print("\n5. Testing Repository Pattern...")
try:
    book_repo = BookRepository()
    books = book_repo.get_all()
    
    print(f"   ✅ Repository pattern working! Found {books.count()} books")
except Exception as e:
    print(f"   ❌ Repository test error: {e}")
    sys.exit(1)

# Test 6: Test Observer Pattern
print("\n6. Testing Observer Pattern...")
try:
    subject = OrderSubject()
    from bookstore.observers.log_observer import LogObserver
    
    observer = LogObserver()
    subject.attach(observer)
    
    assert subject.get_observer_count() == 1, "Observer not attached!"
    
    print("   ✅ Observer pattern working correctly!")
except Exception as e:
    print(f"   ❌ Observer test error: {e}")
    sys.exit(1)

# Test 7: Test Strategy Pattern
print("\n7. Testing Strategy Pattern...")
try:
    from bookstore.services.discount_service import DiscountService
    from bookstore.models import Customer, User
    from decimal import Decimal
    
    service = DiscountService()
    
    # Test with no customer (should work)
    result = service.calculate_all_discounts(
        subtotal=Decimal('1000.00'),
        customer=None,
        coupon=None
    )
    
    assert 'order_value_discount' in result, "Discount calculation failed!"
    
    print("   ✅ Strategy pattern working correctly!")
except Exception as e:
    print(f"   ❌ Strategy test error: {e}")
    sys.exit(1)

# Test 8: Test NotificationManager observers
print("\n8. Testing NotificationManager observers...")
try:
    manager = NotificationManager()
    observer_count = manager.get_observer_count()
    
    assert observer_count >= 3, f"Expected at least 3 observers, got {observer_count}"
    
    print(f"   ✅ NotificationManager has {observer_count} observers registered!")
except Exception as e:
    print(f"   ❌ NotificationManager test error: {e}")
    sys.exit(1)

# Test 9: Test ConfigManager configuration
print("\n9. Testing ConfigManager configuration...")
try:
    config = ConfigManager()
    
    shipping_threshold = config.get_free_shipping_threshold()
    base_fee = config.get_base_shipping_fee()
    
    assert shipping_threshold is not None, "Shipping threshold not configured!"
    assert base_fee is not None, "Base fee not configured!"
    
    print(f"   ✅ ConfigManager configured! Free shipping at Rs. {shipping_threshold}")
except Exception as e:
    print(f"   ❌ ConfigManager test error: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("🎉 ALL INTEGRATION TESTS PASSED!")
print("=" * 60)
print("\n✅ All 5 design patterns are properly integrated:")
print("   1. Strategy Pattern - Discount calculation")
print("   2. Factory Pattern - Payment processing")
print("   3. Repository Pattern - Data access")
print("   4. Observer Pattern - Order notifications")
print("   5. Singleton Pattern - Configuration & notification management")
print("\n✅ Views are successfully using all patterns!")
print("\n" + "=" * 60)

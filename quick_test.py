"""
Quick Pattern Test - Without Django Setup
==========================================
Tests pattern imports without full Django initialization
"""

import sys
print("=" * 60)
print("QUICK PATTERN TEST (No Django)")
print("=" * 60)

# Test 1: Import pattern modules
print("\n1. Testing pattern module imports...")
try:
    # These should work without Django
    import bookstore.strategies.discount_strategy
    import bookstore.payments.payment_factory
    import bookstore.observers.observer
    import bookstore.managers.config_manager
    print("   ✅ All pattern modules imported successfully!")
except Exception as e:
    print(f"   ❌ Import error: {e}")
    sys.exit(1)

# Test 2: Test Singleton Pattern (no Django needed)
print("\n2. Testing Singleton Pattern...")
try:
    from bookstore.managers.config_manager import ConfigManager
    
    config1 = ConfigManager()
    config2 = ConfigManager()
    
    assert config1 is config2, "ConfigManager is not a singleton!"
    print("   ✅ Singleton pattern working correctly!")
    print(f"   📊 config1 id: {id(config1)}")
    print(f"   📊 config2 id: {id(config2)}")
except Exception as e:
    print(f"   ❌ Singleton test error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Test Factory Pattern (no Django needed)
print("\n3. Testing Factory Pattern...")
try:
    from bookstore.payments.payment_factory import PaymentFactory
    
    cash_processor = PaymentFactory.get_processor('Cash')
    card_processor = PaymentFactory.get_processor('Card')
    
    assert cash_processor is not None, "Cash processor not created!"
    assert card_processor is not None, "Card processor not created!"
    
    print("   ✅ Factory pattern working correctly!")
    print(f"   📊 Cash processor: {cash_processor.__class__.__name__}")
    print(f"   📊 Card processor: {card_processor.__class__.__name__}")
except Exception as e:
    print(f"   ❌ Factory test error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Test Observer Pattern (no Django needed)
print("\n4. Testing Observer Pattern...")
try:
    from bookstore.observers.order_subject import OrderSubject
    from bookstore.observers.log_observer import LogObserver
    
    subject = OrderSubject()
    observer = LogObserver()
    subject.attach(observer)
    
    assert subject.get_observer_count() == 1, "Observer not attached!"
    
    print("   ✅ Observer pattern working correctly!")
    print(f"   📊 Observer count: {subject.get_observer_count()}")
except Exception as e:
    print(f"   ❌ Observer test error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Test NotificationManager Singleton
print("\n5. Testing NotificationManager Singleton...")
try:
    from bookstore.managers.notification_manager import NotificationManager
    
    manager1 = NotificationManager()
    manager2 = NotificationManager()
    
    assert manager1 is manager2, "NotificationManager is not a singleton!"
    
    observer_count = manager1.get_observer_count()
    print("   ✅ NotificationManager singleton working!")
    print(f"   📊 Observer count: {observer_count}")
except Exception as e:
    print(f"   ❌ NotificationManager test error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("🎉 ALL QUICK TESTS PASSED!")
print("=" * 60)
print("\n✅ Pattern implementations verified:")
print("   1. Singleton Pattern - ConfigManager & NotificationManager")
print("   2. Factory Pattern - Payment processors")
print("   3. Observer Pattern - Order notifications")
print("\n✅ Patterns are working correctly!")
print("\n" + "=" * 60)

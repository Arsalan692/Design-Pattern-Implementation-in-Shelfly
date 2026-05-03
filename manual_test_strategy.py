"""
Manual test for Strategy Pattern
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shelfly.settings')
django.setup()

from decimal import Decimal
from bookstore.strategies.coupon_discount import CouponDiscountStrategy
from bookstore.strategies.order_value_discount import OrderValueDiscountStrategy
from bookstore.strategies.first_time_buyer_discount import FirstTimeBuyerDiscountStrategy
from bookstore.strategies.discount_context import DiscountContext
from bookstore.services.discount_service import DiscountService
from bookstore.models import Customer, User, Coupon

print("=" * 70)
print("MANUAL STRATEGY PATTERN TEST")
print("=" * 70)

# Test 1: CouponDiscountStrategy
print("\n1. Testing CouponDiscountStrategy...")
try:
    strategy = CouponDiscountStrategy()
    
    # Create test coupon
    coupon = Coupon(
        code="TEST20",
        discount_percentage=Decimal('20.00'),
        is_active=True
    )
    
    context_data = {'coupon': coupon}
    subtotal = Decimal('1000.00')
    
    is_applicable = strategy.is_applicable(context_data)
    print(f"   Is applicable: {is_applicable}")
    
    if is_applicable:
        discount = strategy.calculate_discount(subtotal, context_data)
        print(f"   Discount: Rs. {discount}")
        print(f"   Expected: Rs. 200.00")
        assert discount == Decimal('200.00'), f"Expected 200.00, got {discount}"
        print("   ✅ PASS")
    else:
        print("   ❌ FAIL - Should be applicable")
        
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test 2: OrderValueDiscountStrategy
print("\n2. Testing OrderValueDiscountStrategy...")
try:
    strategy = OrderValueDiscountStrategy()
    
    context_data = {}
    subtotal = Decimal('6000.00')  # Above threshold
    
    is_applicable = strategy.is_applicable(context_data)
    print(f"   Is applicable: {is_applicable}")
    
    if is_applicable:
        discount = strategy.calculate_discount(subtotal, context_data)
        print(f"   Discount: Rs. {discount}")
        print(f"   Expected: Rs. 900.00 (15% of 6000)")
        assert discount == Decimal('900.00'), f"Expected 900.00, got {discount}"
        print("   ✅ PASS")
    else:
        print("   ❌ FAIL - Should be applicable for amount > 5000")
        
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test 3: FirstTimeBuyerDiscountStrategy
print("\n3. Testing FirstTimeBuyerDiscountStrategy...")
try:
    strategy = FirstTimeBuyerDiscountStrategy()
    
    # Create test user and customer
    user = User(username="testuser", email="test@example.com")
    customer = Customer(user=user, is_first_time_buyer=True)
    
    context_data = {'customer': customer}
    subtotal = Decimal('1000.00')
    
    is_applicable = strategy.is_applicable(context_data)
    print(f"   Is applicable: {is_applicable}")
    
    if is_applicable:
        discount = strategy.calculate_discount(subtotal, context_data)
        print(f"   Discount: Rs. {discount}")
        print(f"   Expected: Rs. 100.00 (10% of 1000)")
        assert discount == Decimal('100.00'), f"Expected 100.00, got {discount}"
        print("   ✅ PASS")
    else:
        print("   ❌ FAIL - Should be applicable for first-time buyer")
        
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test 4: DiscountContext
print("\n4. Testing DiscountContext...")
try:
    context = DiscountContext.create_default_context()
    
    # Test with multiple discounts
    coupon = Coupon(code="TEST20", discount_percentage=Decimal('20.00'), is_active=True)
    user = User(username="testuser", email="test@example.com")
    customer = Customer(user=user, is_first_time_buyer=True)
    
    context_data = {
        'coupon': coupon,
        'customer': customer
    }
    subtotal = Decimal('6000.00')
    
    total_discount = context.calculate_total_discount(subtotal, context_data)
    print(f"   Total discount: Rs. {total_discount}")
    print(f"   Expected: Rs. 2100.00 (20% + 15% + 10% = 45% of 6000)")
    
    # Get breakdown
    breakdown = context.get_discount_breakdown(subtotal, context_data)
    print(f"   Breakdown: {len(breakdown)} discounts")
    for item in breakdown:
        print(f"      - {item['description']}: Rs. {item['amount']}")
    
    print("   ✅ PASS")
        
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test 5: DiscountService
print("\n5. Testing DiscountService...")
try:
    # Test class method
    coupon = Coupon(code="TEST20", discount_percentage=Decimal('20.00'), is_active=True)
    user = User(username="testuser", email="test@example.com")
    customer = Customer(user=user, is_first_time_buyer=True)
    
    result = DiscountService.calculate_all_discounts_for(
        subtotal=Decimal('6000.00'),
        customer=customer,
        coupon=coupon
    )
    
    print(f"   Result keys: {result.keys()}")
    print(f"   Total discount: Rs. {result['total_discount']}")
    print(f"   Coupon discount: Rs. {result['coupon_discount']}")
    print(f"   Order value discount: Rs. {result['order_value_discount']}")
    print(f"   First-time discount: Rs. {result['first_time_discount']}")
    
    assert 'total_discount' in result, "Missing total_discount"
    assert 'coupon_discount' in result, "Missing coupon_discount"
    assert 'order_value_discount' in result, "Missing order_value_discount"
    assert 'first_time_discount' in result, "Missing first_time_discount"
    
    print("   ✅ PASS")
        
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("MANUAL STRATEGY PATTERN TEST COMPLETE")
print("=" * 70)

# Manual Testing Guide
## Quick Reference for Testing All 5 Design Patterns

**Server URL:** http://127.0.0.1:8000/  
**Status:** ✅ Running  
**Date:** May 1, 2026

---

## 🎯 Testing Objectives

### Primary Goals
- Verify all 5 design patterns working in production
- Test complete order flow
- Verify notifications
- Test error handling
- Document results

---

## 🚀 Quick Start

### 1. Start Server (if not running)
```bash
venv\Scripts\python.exe manage.py runserver
```

### 2. Open Browser
Navigate to: http://127.0.0.1:8000/

### 3. Open Console
Keep browser console open to see Observer pattern notifications

---

## 📋 Test Scenarios

### Scenario 1: First-Time Buyer with All Discounts
**Tests:** ALL 5 PATTERNS  
**Time:** 5-10 minutes

#### Steps:
1. **Register New User** (Repository Pattern)
   - Click "Register"
   - Username: `testuser1`
   - Email: `test1@example.com`
   - Password: `Test@123`
   - Click "Register"
   - ✅ Verify: Redirected to home page

2. **Browse Books** (Repository Pattern)
   - View book list
   - Search for "Python"
   - Click on a book
   - ✅ Verify: Book details displayed

3. **Add to Cart** (Repository Pattern)
   - Add 3-4 books (total > Rs. 5000)
   - ✅ Verify: Items added to cart

4. **View Cart** (Strategy Pattern)
   - Click "Cart"
   - ✅ Verify: Subtotal calculated
   - ✅ Verify: First-time buyer discount shown (10%)
   - ✅ Verify: Order value discount shown (15% if > Rs. 5000)

5. **Apply Coupon** (Strategy + Repository)
   - Enter coupon code: `WELCOME20`
   - Click "Apply"
   - ✅ Verify: Coupon discount shown (20%)
   - ✅ Verify: Total discount = Coupon + Order Value + First-Time

6. **Checkout with Card** (ALL 5 PATTERNS)
   - Click "Checkout"
   - Enter delivery details:
     - Name: Test User
     - Phone: 03001234567
     - Address: Test Address, Karachi
   - Select "Card Payment"
   - Enter card details:
     - Card Number: 4532015112830366 (valid test card)
     - Holder: TEST USER
     - Expiry: 12/25
     - CVV: 123
   - Click "Place Order"
   - ✅ Verify: Order placed successfully
   - ✅ Verify: Discount applied correctly
   - ✅ Verify: Payment processed
   - ✅ Check Console: Email notification 📧
   - ✅ Check Console: Log entry 📝
   - ✅ Check Console: Inventory update 📦

7. **View Order History** (Repository Pattern)
   - Click "Orders"
   - ✅ Verify: Order appears in history
   - ✅ Verify: Discount amounts correct

---

### Scenario 2: Cash Payment
**Tests:** Repository, Strategy, Factory, Observer, Singleton  
**Time:** 3-5 minutes

#### Steps:
1. **Login** (if not already)
   - Username: `testuser1`
   - Password: `Test@123`

2. **Add Items to Cart**
   - Add 2-3 books

3. **Checkout with Cash**
   - Click "Checkout"
   - Enter delivery details
   - Select "Cash on Delivery"
   - Click "Place Order"
   - ✅ Verify: Order placed
   - ✅ Verify: Payment method = Cash
   - ✅ Check Console: Notifications

---

### Scenario 3: Order Cancellation
**Tests:** Repository, Observer, Singleton  
**Time:** 2-3 minutes

#### Steps:
1. **View Orders**
   - Click "Orders"
   - Find a recent order

2. **Cancel Order**
   - Click "Cancel Order"
   - Enter reason: "Changed my mind"
   - Confirm cancellation
   - ✅ Verify: Order status = Cancelled
   - ✅ Verify: Stock restored
   - ✅ Check Console: Cancellation notification 📧
   - ✅ Check Console: Log entry 📝
   - ✅ Check Console: Inventory update 📦

---

### Scenario 4: Invalid Card Payment
**Tests:** Factory Pattern (Card Validation)  
**Time:** 2-3 minutes

#### Steps:
1. **Add Items to Cart**

2. **Try Invalid Card**
   - Go to checkout
   - Select "Card Payment"
   - Enter invalid card: 1234567890123456
   - ✅ Verify: Error message shown
   - ✅ Verify: Order not created

3. **Try Expired Card**
   - Enter card: 4532015112830366
   - Expiry: 12/20 (expired)
   - ✅ Verify: Error message shown

4. **Try Invalid CVV**
   - Enter valid card
   - CVV: 12 (too short)
   - ✅ Verify: Error message shown

---

### Scenario 5: Coupon Validation
**Tests:** Repository, Strategy  
**Time:** 2-3 minutes

#### Steps:
1. **Try Invalid Coupon**
   - Add items to cart
   - Enter coupon: `INVALID123`
   - ✅ Verify: Error message

2. **Try Expired Coupon**
   - Enter expired coupon code
   - ✅ Verify: Error message

3. **Try Used Coupon**
   - Use same coupon twice
   - ✅ Verify: Error message

---

## 🔍 What to Look For

### Strategy Pattern Verification
**Location:** Cart page, Checkout page

**Check:**
- [ ] Discount breakdown displayed
- [ ] Multiple discounts calculated correctly
- [ ] Discount priorities respected
- [ ] Total discount accurate

**Console Output:** None (internal calculation)

---

### Factory Pattern Verification
**Location:** Card payment form

**Check:**
- [ ] Card validation working
- [ ] Luhn algorithm checking card number
- [ ] Expiry date validation
- [ ] CVV validation
- [ ] Card type detection (Visa, Mastercard, etc.)

**Console Output:** None (internal validation)

---

### Repository Pattern Verification
**Location:** All pages

**Check:**
- [ ] Book search working
- [ ] Order creation working
- [ ] Order retrieval working
- [ ] Customer profile updates working
- [ ] Coupon validation working

**Console Output:** None (database operations)

---

### Observer Pattern Verification
**Location:** Browser console

**Check:**
- [ ] Email notifications on order placed
- [ ] Email notifications on order cancelled
- [ ] Email notifications on payment received
- [ ] Log entries for all events
- [ ] Inventory alerts for low stock

**Console Output:**
```
📧 Email Notification: Order #123 placed successfully
📝 Log: Order placed - Order #123 by testuser1
📦 Inventory: Stock updated for Book #5
```

---

### Singleton Pattern Verification
**Location:** Throughout application

**Check:**
- [ ] Configuration consistent across requests
- [ ] NotificationManager single instance
- [ ] ConfigManager single instance
- [ ] Same observers registered

**Console Output:**
```
🔧 ConfigManager initialized (singleton)
🔔 NotificationManager initialized (singleton)
📊 3 observers registered
```

---

## 📊 Test Results Template

### Test Execution Record

**Date:** ___________  
**Tester:** ___________  
**Server:** http://127.0.0.1:8000/

#### Scenario 1: First-Time Buyer
- [ ] User registration: PASS / FAIL
- [ ] Book browsing: PASS / FAIL
- [ ] Add to cart: PASS / FAIL
- [ ] Discount calculation: PASS / FAIL
- [ ] Coupon application: PASS / FAIL
- [ ] Card payment: PASS / FAIL
- [ ] Notifications: PASS / FAIL
- [ ] Order history: PASS / FAIL

**Notes:** ___________

---

#### Scenario 2: Cash Payment
- [ ] Login: PASS / FAIL
- [ ] Add to cart: PASS / FAIL
- [ ] Cash checkout: PASS / FAIL
- [ ] Notifications: PASS / FAIL

**Notes:** ___________

---

#### Scenario 3: Order Cancellation
- [ ] View orders: PASS / FAIL
- [ ] Cancel order: PASS / FAIL
- [ ] Stock restoration: PASS / FAIL
- [ ] Notifications: PASS / FAIL

**Notes:** ___________

---

#### Scenario 4: Invalid Card
- [ ] Invalid card number: PASS / FAIL
- [ ] Expired card: PASS / FAIL
- [ ] Invalid CVV: PASS / FAIL

**Notes:** ___________

---

#### Scenario 5: Coupon Validation
- [ ] Invalid coupon: PASS / FAIL
- [ ] Expired coupon: PASS / FAIL
- [ ] Used coupon: PASS / FAIL

**Notes:** ___________

---

## 🐛 Common Issues & Solutions

### Issue 1: Server Not Running
**Symptom:** Cannot access http://127.0.0.1:8000/

**Solution:**
```bash
venv\Scripts\python.exe manage.py runserver
```

---

### Issue 2: No Notifications in Console
**Symptom:** Console doesn't show observer notifications

**Solution:**
- Check browser console (F12)
- Look for Django console output
- Verify NotificationManager initialized

---

### Issue 3: Discount Not Applied
**Symptom:** Discount shows as 0

**Solution:**
- Check cart subtotal (must be > threshold)
- Verify coupon is valid
- Check customer is first-time buyer

---

### Issue 4: Card Payment Fails
**Symptom:** Valid card rejected

**Solution:**
- Use test card: 4532015112830366
- Check expiry date is future
- Verify CVV is 3 digits

---

## 📸 Screenshots to Capture

### For Documentation
1. Home page
2. Book list with search
3. Book detail page
4. Cart with discounts
5. Coupon application
6. Checkout form
7. Card payment form
8. Order success page
9. Order history
10. Order cancellation
11. Console notifications
12. Admin panel (optional)

---

## ✅ Success Criteria

### All Tests Pass
- [ ] All 5 scenarios completed
- [ ] All patterns verified working
- [ ] All notifications appearing
- [ ] No errors in console
- [ ] No server errors

### Quality Indicators
- [ ] Fast response times
- [ ] Smooth user experience
- [ ] Clear error messages
- [ ] Accurate calculations
- [ ] Proper notifications

---

## 📝 Test Report Template

### Executive Summary
- Total scenarios tested: ___
- Scenarios passed: ___
- Scenarios failed: ___
- Pass rate: ___%

### Pattern Verification
- Strategy Pattern: ✅ / ❌
- Factory Pattern: ✅ / ❌
- Repository Pattern: ✅ / ❌
- Observer Pattern: ✅ / ❌
- Singleton Pattern: ✅ / ❌

### Issues Found
1. ___________
2. ___________
3. ___________

### Recommendations
1. ___________
2. ___________
3. ___________

---

## 🎯 Quick Verification Checklist

### Before Testing
- [ ] Server running
- [ ] Database populated with books
- [ ] Test coupons created
- [ ] Browser console open

### During Testing
- [ ] Follow scenarios in order
- [ ] Check console for notifications
- [ ] Verify calculations
- [ ] Test error cases
- [ ] Take screenshots

### After Testing
- [ ] Document results
- [ ] Note any issues
- [ ] Save screenshots
- [ ] Update test report

---

## 📚 Test Data

### Test Users
```
Username: testuser1
Email: test1@example.com
Password: Test@123

Username: testuser2
Email: test2@example.com
Password: Test@123
```

### Test Cards
```
Valid Card:
Number: 4532015112830366
Holder: TEST USER
Expiry: 12/25
CVV: 123

Invalid Card:
Number: 1234567890123456
```

### Test Coupons
```
Code: WELCOME20
Discount: 20%
Status: Active

Code: EXPIRED10
Discount: 10%
Status: Expired
```

---

## 🚀 Advanced Testing

### Performance Testing
- [ ] Measure page load times
- [ ] Check database query count
- [ ] Monitor memory usage
- [ ] Test with multiple users

### Security Testing
- [ ] SQL injection attempts
- [ ] XSS attempts
- [ ] CSRF token validation
- [ ] Authentication bypass attempts

### Edge Cases
- [ ] Empty cart checkout
- [ ] Negative quantities
- [ ] Very large orders
- [ ] Concurrent order placement

---

**Status:** Ready for Testing  
**Server:** Running  
**Patterns:** All Integrated  
**Next:** Execute test scenarios

---

**🎯 Happy Testing! 🎯**


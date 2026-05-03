"""
Integrated Views with Design Patterns
======================================

This file integrates all 5 design patterns with the Django views:
1. Strategy Pattern - Discount calculation
2. Factory Pattern - Payment processing
3. Repository Pattern - Data access
4. Observer Pattern - Order notifications
5. Singleton Pattern - Configuration & notification management
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Book, Order, OrderItem, Customer, Payment, Cart, CartItem, Coupon, CouponUsage, ContactMessage, Delivery, OrderCancellation
from decimal import Decimal
import json
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
import re
from django.views.decorators.http import require_http_methods
from functools import wraps

# Import Design Pattern Components
from .services.discount_service import DiscountService
from .services.payment_service import PaymentService
from .payments.payment_factory import PaymentFactory
from .repositories.book_repository import BookRepository
from .repositories.order_repository import OrderRepository
from .repositories.customer_repository import CustomerRepository
from .repositories.coupon_repository import CouponRepository
from .managers.config_manager import ConfigManager
from .managers.notification_manager import NotificationManager


# Initialize repositories
book_repo = BookRepository()
order_repo = OrderRepository()
customer_repo = CustomerRepository()
coupon_repo = CouponRepository()

# Initialize services
discount_service = DiscountService()
payment_service = PaymentService()

# Initialize managers (singletons)
config_manager = ConfigManager()
notification_manager = NotificationManager()


def customer_required(view_func):
    """
    Decorator to ensure only users with Customer profiles can access the view.
    Redirects admin/staff users to admin panel with a message.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if request.user.is_staff or request.user.is_superuser:
            messages.warning(request, 'This feature is for customers only. Please use the admin panel.')
            return redirect('/admin/')
        
        if not hasattr(request.user, 'customer'):
            messages.error(request, 'Customer profile not found. Please contact support.')
            return redirect('home')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def register(request):
    """Register new customer - uses CustomerRepository"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        
        if password != password_confirm:
            messages.error(request, 'Passwords do not match!')
            return redirect('register')
        
        # Use CustomerRepository
        if customer_repo.get_by_username(username):
            messages.error(request, 'Username already exists!')
            return redirect('register')
        
        if customer_repo.get_by_email(email):
            messages.error(request, 'Email already registered!')
            return redirect('register')
        
        # Create user and customer
        user = User.objects.create_user(username=username, email=email, password=password)
        customer = Customer.objects.create(user=user, phone=phone, address=address, is_first_time_buyer=True)
        
        Cart.objects.create(customer=customer)
        messages.success(request, 'Account created successfully! Please login.')
        return redirect('login')
    
    return render(request, 'bookstore/register.html')


def login_view(request):
    """Login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password!')
            return redirect('login')
    
    return render(request, 'bookstore/login.html')


def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('home')


def home_page(request):
    """Home page"""
    return render(request, 'bookstore/home.html')


def book_list(request):
    """Book list with search - uses BookRepository"""
    search_query = request.GET.get('search', '').strip()
    
    if search_query:
        # Use BookRepository search
        books = book_repo.search(search_query)
    else:
        # Get all books
        books = book_repo.get_all()
    
    context = {
        'books': books,
        'search_query': search_query,
    }
    
    return render(request, 'bookstore/book_list.html', context)


def book_detail(request, book_id):
    """Book detail - uses BookRepository"""
    book = book_repo.get_by_id(book_id)
    if not book:
        messages.error(request, 'Book not found!')
        return redirect('book_list')
    
    return render(request, 'bookstore/book_detail.html', {'book': book})


@login_required(login_url='login')
def order_history(request):
    """Order history - uses OrderRepository"""
    customer = request.user.customer
    orders = order_repo.get_customer_orders(customer.id)
    return render(request, 'bookstore/order_history.html', {'orders': orders})


def about_page(request):
    """About page"""
    return render(request, 'bookstore/about.html')


def contact(request):
    """Contact page"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '').strip() or None
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        ContactMessage.objects.create(
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message
        )
        
        messages.success(request, 'Thank you! Your message has been sent.')
        return redirect('contact')
    
    return render(request, 'bookstore/contact.html')


@customer_required
def add_to_cart(request, book_id):
    """Add book to cart - uses BookRepository"""
    book = book_repo.get_by_id(book_id)
    if not book:
        messages.error(request, 'Book not found!')
        return redirect('book_list')
    
    customer = request.user.customer
    
    cart, created = Cart.objects.get_or_create(customer=customer)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, book=book)
    
    if not created:
        if cart_item.quantity < book.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f"Increased quantity of '{book.title}' in cart!")
        else:
            messages.warning(request, f"Cannot add more. Only {book.stock} in stock!")
    else:
        messages.success(request, f"'{book.title}' added to cart!")
    
    return redirect('view_cart')


@customer_required
def view_cart(request):
    """View cart with discount calculation - uses DiscountService"""
    customer = request.user.customer
    cart, created = Cart.objects.get_or_create(customer=customer)
    cart_items = cart.cartitem_set.all()
    
    # Calculate discounts using DiscountService
    if cart_items:
        discount_result = discount_service.calculate_all_discounts(
            subtotal=cart.subtotal,
            customer=customer,
            coupon=cart.applied_coupon
        )
        
        # Store discount amounts for display
        cart.discount_breakdown = discount_result
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'bookstore/cart.html', context)


@customer_required
def apply_coupon(request):
    """Apply coupon - uses CouponRepository and DiscountService"""
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code', '').strip().upper()
        customer = request.user.customer
        cart = get_object_or_404(Cart, customer=customer)
        
        if not coupon_code:
            messages.error(request, 'Please enter a coupon code!')
            return redirect('view_cart')
        
        # Use CouponRepository
        coupon = coupon_repo.get_by_code(coupon_code)
        if not coupon:
            messages.error(request, 'Invalid coupon code!')
            return redirect('view_cart')
        
        # Validate coupon
        is_valid, msg = coupon_repo.validate_coupon(coupon, customer, cart.subtotal)
        if not is_valid:
            messages.error(request, f"Coupon error: {msg}")
            return redirect('view_cart')
        
        cart.applied_coupon = coupon
        cart.save()
        
        # Calculate discount using DiscountService
        discount_result = discount_service.calculate_all_discounts(
            subtotal=cart.subtotal,
            customer=customer,
            coupon=coupon
        )
        
        messages.success(request, f'Coupon "{coupon_code}" applied! You saved Rs. {discount_result["coupon_discount"]:.2f}')
        return redirect('view_cart')
    
    return redirect('view_cart')


@customer_required
def remove_coupon(request):
    """Remove coupon from cart"""
    if request.method == 'POST':
        customer = request.user.customer
        cart = get_object_or_404(Cart, customer=customer)
        
        if cart.applied_coupon:
            coupon_code = cart.applied_coupon.code
            cart.applied_coupon = None
            cart.save()
            messages.success(request, f'Coupon "{coupon_code}" removed!')
        else:
            messages.warning(request, 'No coupon applied!')
        
        return redirect('view_cart')
    
    return redirect('view_cart')


@customer_required
def update_cart_item(request, item_id):
    """Update cart item quantity"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__customer=request.user.customer)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'increase':
            if cart_item.quantity < cart_item.book.stock:
                cart_item.quantity += 1
                cart_item.save()
                messages.success(request, 'Quantity updated!')
            else:
                messages.warning(request, 'Maximum stock reached!')
        
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
                messages.success(request, 'Quantity updated!')
            else:
                messages.warning(request, 'Minimum quantity is 1!')
    
    return redirect('view_cart')


@customer_required
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__customer=request.user.customer)
    book_title = cart_item.book.title
    cart_item.delete()
    messages.success(request, f"'{book_title}' removed from cart!")
    return redirect('view_cart')


@customer_required
def edit_profile(request):
    """Edit customer profile - uses CustomerRepository"""
    customer = request.user.customer
    
    if request.method == 'POST':
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        
        # Update using CustomerRepository
        customer_repo.update_profile(customer.id, email, phone, address)
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('edit_profile')
    
    return render(request, 'bookstore/edit_profile.html', {'customer': customer})


@customer_required
def cancel_order(request, order_id):
    """
    Cancel order - uses OrderRepository and NotificationManager
    """
    order = order_repo.get_by_id(order_id)
    if not order or order.customer != request.user.customer:
        messages.error(request, 'Order not found!')
        return redirect('order_history')
    
    # Check if cancellable using ConfigManager
    cancellable_statuses = config_manager.get_cancellable_statuses()
    if order.status not in cancellable_statuses:
        messages.error(request, f"Cannot cancel order in '{order.status}' status!")
        return redirect('order_history')
    
    if request.method == 'POST':
        cancellation_reason = request.POST.get('cancellation_reason', '').strip()
        
        # Cancel order using OrderRepository
        success = order_repo.cancel_order(order.id, cancellation_reason)
        
        if success:
            # Notify observers using NotificationManager
            notification_manager.notify_order_cancelled(order, cancellation_reason)
            
            messages.success(
                request, 
                f'Order #{order.id} cancelled successfully! Stock has been restored.'
            )
        else:
            messages.error(request, 'Failed to cancel order!')
        
        return redirect('order_history')
    
    context = {
        'order': order,
    }
    return render(request, 'bookstore/cancel_order.html', context)


@customer_required
def change_password(request):
    """Change password"""
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        user = request.user
        
        if not user.check_password(current_password):
            messages.error(request, 'Current password is incorrect!')
            return redirect('change_password')
        
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match!')
            return redirect('change_password')
        
        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long!')
            return redirect('change_password')
        
        user.set_password(new_password)
        user.save()
        
        update_session_auth_hash(request, user)
        
        messages.success(request, 'Password changed successfully!')
        return redirect('edit_profile')
    
    return render(request, 'bookstore/change_password.html')


@customer_required
def card_payment_form(request):
    """Display card payment form"""
    customer = request.user.customer
    cart = get_object_or_404(Cart, customer=customer)
    cart_items = cart.cartitem_set.all()
    
    if not cart_items:
        messages.warning(request, 'Your cart is empty!')
        return redirect('view_cart')
    
    delivery_name = request.POST.get('delivery_name', customer.user.get_full_name() or customer.user.username)
    delivery_phone = request.POST.get('delivery_phone', customer.phone)
    delivery_address = request.POST.get('delivery_address', customer.address)
    delivery_notes = request.POST.get('delivery_notes', '')
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'customer': customer,
        'delivery_name': delivery_name,
        'delivery_phone': delivery_phone,
        'delivery_address': delivery_address,
        'delivery_notes': delivery_notes,
    }
    
    return render(request, 'bookstore/card_payment_form.html', context)


@customer_required
@require_http_methods(["POST"])
def process_card_payment(request):
    """
    Process card payment - uses PaymentFactory and NotificationManager
    """
    customer = request.user.customer
    cart = get_object_or_404(Cart, customer=customer)
    cart_items = cart.cartitem_set.all()
    
    if not cart_items:
        return JsonResponse({'success': False, 'message': 'Cart is empty'})
    
    # Get payment details
    card_number = request.POST.get('card_number', '').strip()
    card_holder = request.POST.get('card_holder', '').strip()
    expiry_month = request.POST.get('expiry_month', '').strip()
    expiry_year = request.POST.get('expiry_year', '').strip()
    cvv = request.POST.get('cvv', '').strip()
    
    # Get delivery details
    delivery_name = request.POST.get('delivery_name', '').strip()
    delivery_phone = request.POST.get('delivery_phone', '').strip()
    delivery_address = request.POST.get('delivery_address', '').strip()
    delivery_notes = request.POST.get('delivery_notes', '').strip() or None
    
    if not all([card_number, card_holder, expiry_month, expiry_year, cvv, 
                delivery_name, delivery_phone, delivery_address]):
        return JsonResponse({
            'success': False,
            'message': 'All fields are required'
        })
    
    # Use PaymentFactory to get card processor
    try:
        payment_processor = PaymentFactory.get_processor('Card')
        
        # Validate payment using Factory Pattern
        is_valid, error_message = payment_processor.validate_payment({
            'card_number': card_number,
            'card_holder': card_holder,
            'expiry_month': expiry_month,
            'expiry_year': expiry_year,
            'cvv': cvv
        })
        
        if not is_valid:
            return JsonResponse({'success': False, 'message': error_message})
        
        # Calculate discounts using DiscountService
        discount_result = discount_service.calculate_all_discounts(
            subtotal=cart.subtotal,
            customer=customer,
            coupon=cart.applied_coupon
        )
        
        # Create order using OrderRepository
        order = order_repo.create_order(
            customer=customer,
            cart_items=cart_items,
            shipping_fee=cart.shipping_fee,
            applied_coupon=cart.applied_coupon,
            discount_amounts=discount_result
        )
        
        # Create delivery record
        Delivery.objects.create(
            order=order,
            recipient_name=delivery_name,
            phone=delivery_phone,
            address=delivery_address,
            notes=delivery_notes,
        )
        
        # Process payment using PaymentService
        payment_result = payment_service.process_payment(
            order=order,
            payment_method='Card',
            payment_details={
                'card_number': card_number,
                'card_holder': card_holder,
                'expiry_month': expiry_month,
                'expiry_year': expiry_year,
                'cvv': cvv
            }
        )
        
        if not payment_result['success']:
            return JsonResponse({
                'success': False,
                'message': payment_result['message']
            })
        
        # Update customer first-time buyer status
        if customer.is_first_time_buyer:
            customer.is_first_time_buyer = False
            customer.save()
        
        # Store payment details in session
        request.session['payment_details'] = payment_result['payment_details']
        
        # Get the Payment object for notification
        payment = Payment.objects.get(id=payment_result['payment_details']['payment_id'])
        
        # Clear cart
        cart_items.delete()
        cart.applied_coupon = None
        cart.save()
        
        # Notify observers using NotificationManager
        notification_manager.notify_order_placed(order)
        notification_manager.notify_payment_received(order, payment)
        
        return JsonResponse({
            'success': True,
            'message': 'Payment processed successfully!',
            'order_id': order.id,
            'redirect_url': f'/orders/{order.id}/payment-success/'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error processing payment: {str(e)}'
        })


@customer_required
def payment_success(request, order_id):
    """Display payment success page"""
    order = get_object_or_404(Order, id=order_id, customer=request.user.customer)
    payment = get_object_or_404(Payment, order=order)
    payment_details = request.session.get('payment_details', {})
    
    if 'payment_details' in request.session:
        del request.session['payment_details']
    request.session.modified = True
    
    context = {
        'order': order,
        'payment': payment,
        'payment_details': payment_details,
    }
    
    return render(request, 'bookstore/payment_success.html', context)


@customer_required
def payment_failed(request):
    """Display payment failed page"""
    return render(request, 'bookstore/payment_failed.html')


@customer_required
def checkout(request):
    """
    Checkout - uses all patterns:
    - DiscountService (Strategy Pattern)
    - PaymentFactory (Factory Pattern)
    - OrderRepository (Repository Pattern)
    - NotificationManager (Observer + Singleton)
    - ConfigManager (Singleton)
    """
    customer = request.user.customer
    cart = get_object_or_404(Cart, customer=customer)
    cart_items = cart.cartitem_set.all()
    
    if not cart_items:
        messages.warning(request, 'Your cart is empty!')
        return redirect('view_cart')
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'Cash')
        delivery_name = request.POST.get('delivery_name')
        delivery_phone = request.POST.get('delivery_phone')
        delivery_address = request.POST.get('delivery_address')
        delivery_notes = request.POST.get('delivery_notes', '')
        
        if not all([delivery_name, delivery_phone, delivery_address]):
            messages.error(request, 'Please fill in all delivery details!')
            return redirect('checkout')
        
        # Store delivery details in session
        request.session['delivery_name'] = delivery_name
        request.session['delivery_phone'] = delivery_phone
        request.session['delivery_address'] = delivery_address
        request.session['delivery_notes'] = delivery_notes
        
        if payment_method == 'Cash':
            try:
                # Calculate discounts using DiscountService
                discount_result = discount_service.calculate_all_discounts(
                    subtotal=cart.subtotal,
                    customer=customer,
                    coupon=cart.applied_coupon
                )
                
                # Create order using OrderRepository
                order = order_repo.create_order(
                    customer=customer,
                    cart_items=cart_items,
                    shipping_fee=cart.shipping_fee,
                    applied_coupon=cart.applied_coupon,
                    discount_amounts=discount_result
                )
                
                # Create delivery record
                Delivery.objects.create(
                    order=order,
                    recipient_name=delivery_name,
                    phone=delivery_phone,
                    address=delivery_address,
                    notes=delivery_notes if delivery_notes else None,
                )
                
                # Process payment using PaymentService
                payment_result = payment_service.process_payment(
                    order=order,
                    payment_method='Cash',
                    payment_details={}
                )
                
                # Update customer first-time buyer status
                if customer.is_first_time_buyer:
                    customer.is_first_time_buyer = False
                    customer.save()
                
                # Clear cart
                cart_items.delete()
                cart.applied_coupon = None
                cart.save()
                
                # Notify observers using NotificationManager
                notification_manager.notify_order_placed(order)
                
                messages.success(request, f'Order #{order.id} placed successfully! You saved Rs. {order.total_discount:.2f}')
                return redirect('order_history')
            
            except Exception as e:
                messages.error(request, f'Error creating order: {str(e)}')
                return redirect('checkout')
        
        elif payment_method == 'Card':
            return card_payment_form(request)
        
        else:
            messages.error(request, 'Invalid payment method!')
            return redirect('checkout')
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'customer': customer,
    }
    return render(request, 'bookstore/checkout.html', context)

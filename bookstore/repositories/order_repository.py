"""
Order Repository
================

Repository for Order model operations.
"""

from typing import List, Optional
from django.db.models import QuerySet, Sum, Count, Q
from datetime import datetime, timedelta

from .base_repository import BaseRepository
from bookstore.models import Order


class OrderRepository(BaseRepository):
    """
    Repository for Order model.
    
    Provides order-specific query methods:
        - Get orders by customer
        - Get orders by status
        - Get recent orders
        - Calculate order statistics
        - Update order status
    """
    
    model = Order
    
    def get_customer_orders(self, customer_id: int) -> QuerySet:
        """
        Get all orders for a customer by customer ID.
        
        Args:
            customer_id (int): Customer ID
        
        Returns:
            QuerySet: Customer's orders
        """
        return self.filter(customer_id=customer_id).order_by('-order_date')
    
    def create_order(self, customer, cart_items, shipping_fee, applied_coupon, discount_amounts):
        """
        Create a new order with items and discounts.
        
        Args:
            customer: Customer instance
            cart_items: QuerySet of CartItem objects
            shipping_fee: Decimal shipping fee
            applied_coupon: Coupon instance or None
            discount_amounts: Dict with discount breakdown
        
        Returns:
            Order: Created order instance
        """
        from bookstore.models import OrderItem, CouponUsage
        
        order = self.create(
            customer=customer,
            shipping_fee=shipping_fee,
            applied_coupon=applied_coupon,
            coupon_discount_amount=discount_amounts.get('coupon_discount', 0),
            order_value_discount_amount=discount_amounts.get('order_value_discount', 0),
            first_time_discount_amount=discount_amounts.get('first_time_discount', 0),
        )
        
        # Create order items
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                book=cart_item.book,
                quantity=cart_item.quantity,
                unit_price=cart_item.book.price,
                subtotal=cart_item.subtotal
            )
        
        # Create coupon usage record
        if applied_coupon:
            CouponUsage.objects.create(
                coupon=applied_coupon,
                customer=customer,
                order=order
            )
        
        return order
    
    def cancel_order(self, order_id: int, reason: str = None) -> bool:
        """
        Cancel an order and restore stock.
        
        Args:
            order_id (int): Order ID
            reason (str): Cancellation reason
        
        Returns:
            bool: True if cancelled successfully
        """
        from bookstore.models import OrderCancellation, CouponUsage
        
        order = self.get_by_id(order_id)
        if not order:
            return False
        
        # Restore stock
        for order_item in order.orderitem_set.all():
            order_item.book.stock += order_item.quantity
            order_item.book.save()
        
        # Remove coupon usage
        if order.applied_coupon:
            CouponUsage.objects.filter(order=order).delete()
        
        # Update order status
        order.status = 'Cancelled'
        order.save()
        
        # Create cancellation record
        OrderCancellation.objects.create(
            order=order,
            reason=reason if reason else None
        )
        
        return True
    
    def get_by_customer(self, customer) -> QuerySet:
        """
        Get all orders for a customer.
        
        Args:
            customer: Customer instance
        
        Returns:
            QuerySet: Customer's orders
        """
        return self.filter(customer=customer).order_by('-order_date')
    
    def get_by_status(self, status: str) -> QuerySet:
        """
        Get orders by status.
        
        Args:
            status (str): Order status
        
        Returns:
            QuerySet: Orders with specified status
        """
        return self.filter(status=status).order_by('-order_date')
    
    def get_pending_orders(self) -> QuerySet:
        """
        Get all pending orders.
        
        Returns:
            QuerySet: Pending orders
        """
        return self.get_by_status('Pending')
    
    def get_confirmed_orders(self) -> QuerySet:
        """
        Get all confirmed orders.
        
        Returns:
            QuerySet: Confirmed orders
        """
        return self.get_by_status('Confirmed')
    
    def get_shipped_orders(self) -> QuerySet:
        """
        Get all shipped orders.
        
        Returns:
            QuerySet: Shipped orders
        """
        return self.get_by_status('Shipped')
    
    def get_delivered_orders(self) -> QuerySet:
        """
        Get all delivered orders.
        
        Returns:
            QuerySet: Delivered orders
        """
        return self.get_by_status('Delivered')
    
    def get_cancelled_orders(self) -> QuerySet:
        """
        Get all cancelled orders.
        
        Returns:
            QuerySet: Cancelled orders
        """
        return self.get_by_status('Cancelled')
    
    def get_recent_orders(self, days: int = 7) -> QuerySet:
        """
        Get orders from last N days.
        
        Args:
            days (int): Number of days (default: 7)
        
        Returns:
            QuerySet: Recent orders
        """
        since_date = datetime.now() - timedelta(days=days)
        return self.filter(order_date__gte=since_date).order_by('-order_date')
    
    def get_orders_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> QuerySet:
        """
        Get orders within date range.
        
        Args:
            start_date (datetime): Start date
            end_date (datetime): End date
        
        Returns:
            QuerySet: Orders in date range
        """
        return self.filter(
            order_date__gte=start_date,
            order_date__lte=end_date
        ).order_by('-order_date')
    
    def update_status(self, order_id: int, new_status: str) -> bool:
        """
        Update order status.
        
        Args:
            order_id (int): Order ID
            new_status (str): New status
        
        Returns:
            bool: True if updated successfully
        """
        order = self.get_by_id(order_id)
        if not order:
            return False
        
        order.status = new_status
        order.save()
        return True
    
    def can_be_cancelled(self, order_id: int) -> bool:
        """
        Check if order can be cancelled.
        
        Args:
            order_id (int): Order ID
        
        Returns:
            bool: True if order can be cancelled
        """
        order = self.get_by_id(order_id)
        if not order:
            return False
        
        cancellable_statuses = ['Pending', 'Confirmed']
        return order.status in cancellable_statuses
    
    def cancel_order(self, order_id: int, reason: str = None) -> bool:
        """
        Cancel an order.
        
        Args:
            order_id (int): Order ID
            reason (str): Cancellation reason (optional)
        
        Returns:
            bool: True if cancelled successfully
        """
        if not self.can_be_cancelled(order_id):
            return False
        
        order = self.get_by_id(order_id)
        order.status = 'Cancelled'
        order.save()
        
        # Create cancellation record if reason provided
        if reason:
            from bookstore.models import OrderCancellation
            OrderCancellation.objects.create(order=order, reason=reason)
        
        return True
    
    def get_customer_order_count(self, customer) -> int:
        """
        Get total number of orders for a customer.
        
        Args:
            customer: Customer instance
        
        Returns:
            int: Order count
        """
        return self.get_by_customer(customer).count()
    
    def get_customer_total_spent(self, customer):
        """
        Calculate total amount spent by customer.
        
        Args:
            customer: Customer instance
        
        Returns:
            Decimal: Total amount spent
        """
        from decimal import Decimal
        
        orders = self.get_by_customer(customer).exclude(status='Cancelled')
        total = orders.aggregate(total=Sum('orderitem__subtotal'))['total']
        
        return total or Decimal('0.00')
    
    def get_orders_with_coupon(self, coupon) -> QuerySet:
        """
        Get orders that used a specific coupon.
        
        Args:
            coupon: Coupon instance
        
        Returns:
            QuerySet: Orders with coupon
        """
        return self.filter(applied_coupon=coupon)
    
    def get_order_statistics(self) -> dict:
        """
        Get overall order statistics.
        
        Returns:
            dict: Statistics including counts by status
        """
        from decimal import Decimal
        
        total_orders = self.count()
        
        stats = {
            'total_orders': total_orders,
            'pending': self.get_pending_orders().count(),
            'confirmed': self.get_confirmed_orders().count(),
            'shipped': self.get_shipped_orders().count(),
            'delivered': self.get_delivered_orders().count(),
            'cancelled': self.get_cancelled_orders().count(),
        }
        
        # Calculate total revenue (excluding cancelled orders)
        completed_orders = self.filter(status__in=['Confirmed', 'Shipped', 'Delivered'])
        revenue = completed_orders.aggregate(total=Sum('orderitem__subtotal'))['total']
        stats['total_revenue'] = revenue or Decimal('0.00')
        
        return stats
    
    def get_orders_needing_attention(self) -> QuerySet:
        """
        Get orders that need attention (pending for > 24 hours).
        
        Returns:
            QuerySet: Orders needing attention
        """
        threshold_date = datetime.now() - timedelta(hours=24)
        return self.filter(
            status='Pending',
            order_date__lt=threshold_date
        ).order_by('order_date')

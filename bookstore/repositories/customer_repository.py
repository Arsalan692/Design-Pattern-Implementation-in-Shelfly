"""
Customer Repository
===================

Repository for Customer model operations.
"""

from typing import Optional
from django.db.models import QuerySet, Count
from datetime import datetime, timedelta

from .base_repository import BaseRepository
from bookstore.models import Customer


class CustomerRepository(BaseRepository):
    """
    Repository for Customer model.
    
    Provides customer-specific query methods:
        - Get customer by user
        - Get first-time buyers
        - Get active customers
        - Update customer profile
    """
    
    model = Customer
    
    def get_by_user(self, user) -> Optional[Customer]:
        """
        Get customer by user instance.
        
        Args:
            user: User instance
        
        Returns:
            Customer instance or None
        """
        return self.first(user=user)
    
    def get_by_username(self, username: str) -> Optional[Customer]:
        """
        Get customer by username.
        
        Args:
            username (str): Username
        
        Returns:
            Customer instance or None
        """
        return self.first(user__username=username)
    
    def get_by_email(self, email: str) -> Optional[Customer]:
        """
        Get customer by email.
        
        Args:
            email (str): Email address
        
        Returns:
            Customer instance or None
        """
        return self.first(user__email=email)
    
    def get_first_time_buyers(self) -> QuerySet:
        """
        Get all first-time buyers.
        
        Returns:
            QuerySet: First-time buyer customers
        """
        return self.filter(is_first_time_buyer=True)
    
    def get_returning_customers(self) -> QuerySet:
        """
        Get all returning customers.
        
        Returns:
            QuerySet: Returning customers
        """
        return self.filter(is_first_time_buyer=False)
    
    def update_profile(self, customer_id: int, email: str, phone: str, address: str) -> bool:
        """
        Update customer profile.
        
        Args:
            customer_id (int): Customer ID
            email (str): New email
            phone (str): New phone
            address (str): New address
        
        Returns:
            bool: True if updated successfully
        """
        customer = self.get_by_id(customer_id)
        if not customer:
            return False
        
        # Update user email
        customer.user.email = email
        customer.user.save()
        
        # Update customer details
        customer.phone = phone
        customer.address = address
        customer.save()
        
        return True
        return self.filter(is_first_time_buyer=False)
    
    def get_recent_registrations(self, days: int = 30) -> QuerySet:
        """
        Get customers registered in last N days.
        
        Args:
            days (int): Number of days (default: 30)
        
        Returns:
            QuerySet: Recently registered customers
        """
        since_date = datetime.now() - timedelta(days=days)
        return self.filter(registration_date__gte=since_date).order_by('-registration_date')
    
    def get_active_customers(self, days: int = 90) -> QuerySet:
        """
        Get customers who placed orders in last N days.
        
        Args:
            days (int): Number of days (default: 90)
        
        Returns:
            QuerySet: Active customers
        """
        since_date = datetime.now() - timedelta(days=days)
        return self.filter(
            order__order_date__gte=since_date
        ).distinct().order_by('-order__order_date')
    
    def get_inactive_customers(self, days: int = 90) -> QuerySet:
        """
        Get customers who haven't placed orders in last N days.
        
        Args:
            days (int): Number of days (default: 90)
        
        Returns:
            QuerySet: Inactive customers
        """
        since_date = datetime.now() - timedelta(days=days)
        active_customer_ids = self.filter(
            order__order_date__gte=since_date
        ).values_list('id', flat=True)
        
        return self.get_all().exclude(id__in=active_customer_ids)
    
    def update_profile(
        self, 
        customer_id: int, 
        phone: str = None, 
        address: str = None
    ) -> Optional[Customer]:
        """
        Update customer profile.
        
        Args:
            customer_id (int): Customer ID
            phone (str): Phone number (optional)
            address (str): Address (optional)
        
        Returns:
            Customer: Updated customer or None
        """
        customer = self.get_by_id(customer_id)
        if not customer:
            return None
        
        if phone is not None:
            customer.phone = phone
        
        if address is not None:
            customer.address = address
        
        customer.save()
        return customer
    
    def mark_as_returning_customer(self, customer_id: int) -> bool:
        """
        Mark customer as returning (not first-time buyer).
        
        Args:
            customer_id (int): Customer ID
        
        Returns:
            bool: True if updated successfully
        """
        customer = self.get_by_id(customer_id)
        if not customer:
            return False
        
        customer.is_first_time_buyer = False
        customer.save()
        return True
    
    def get_customer_statistics(self) -> dict:
        """
        Get overall customer statistics.
        
        Returns:
            dict: Statistics including counts and percentages
        """
        total_customers = self.count()
        first_time_buyers = self.get_first_time_buyers().count()
        returning_customers = self.get_returning_customers().count()
        
        # Calculate percentages
        first_time_percentage = (first_time_buyers / total_customers * 100) if total_customers > 0 else 0
        returning_percentage = (returning_customers / total_customers * 100) if total_customers > 0 else 0
        
        return {
            'total_customers': total_customers,
            'first_time_buyers': first_time_buyers,
            'returning_customers': returning_customers,
            'first_time_percentage': round(first_time_percentage, 2),
            'returning_percentage': round(returning_percentage, 2),
        }
    
    def get_customers_with_order_count(self) -> QuerySet:
        """
        Get customers annotated with their order count.
        
        Returns:
            QuerySet: Customers with order_count annotation
        """
        return self.get_all().annotate(
            order_count=Count('order')
        ).order_by('-order_count')
    
    def get_top_customers(self, limit: int = 10) -> QuerySet:
        """
        Get top customers by order count.
        
        Args:
            limit (int): Number of customers to return
        
        Returns:
            QuerySet: Top customers
        """
        return self.get_customers_with_order_count()[:limit]
    
    def search_customers(self, query: str) -> QuerySet:
        """
        Search customers by username, email, or phone.
        
        Args:
            query (str): Search query
        
        Returns:
            QuerySet: Matching customers
        """
        from django.db.models import Q
        
        if not query:
            return self.get_all()
        
        return self.model.objects.filter(
            Q(user__username__icontains=query) |
            Q(user__email__icontains=query) |
            Q(phone__icontains=query)
        )

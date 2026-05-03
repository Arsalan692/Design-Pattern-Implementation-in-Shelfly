"""
Coupon Repository
=================

Repository for Coupon model operations.
"""

from typing import Optional
from django.db.models import QuerySet, Count
from datetime import datetime

from .base_repository import BaseRepository
from bookstore.models import Coupon


class CouponRepository(BaseRepository):
    """
    Repository for Coupon model.
    
    Provides coupon-specific query methods:
        - Get active coupons
        - Get expired coupons
        - Validate coupon
        - Track coupon usage
    """
    
    model = Coupon
    
    def get_by_code(self, code: str) -> Optional[Coupon]:
        """
        Get coupon by code.
        
        Args:
            code (str): Coupon code
        
        Returns:
            Coupon instance or None
        """
        return self.first(code=code.upper())
    
    def get_active_coupons(self) -> QuerySet:
        """
        Get all active coupons.
        
        Returns:
            QuerySet: Active coupons
        """
        return self.filter(is_active=True)
    
    def get_inactive_coupons(self) -> QuerySet:
        """
        Get all inactive coupons.
        
        Returns:
            QuerySet: Inactive coupons
        """
        return self.filter(is_active=False)
    
    def get_expired_coupons(self) -> QuerySet:
        """
        Get all expired coupons.
        
        Returns:
            QuerySet: Expired coupons
        """
        return self.filter(expiry_date__lt=datetime.now())
    
    def get_valid_coupons(self) -> QuerySet:
        """
        Get all valid coupons (active and not expired).
        
        Returns:
            QuerySet: Valid coupons
        """
        return self.filter(
            is_active=True,
            expiry_date__gt=datetime.now()
        )
    
    def get_by_discount_type(self, discount_type: str) -> QuerySet:
        """
        Get coupons by discount type.
        
        Args:
            discount_type (str): Discount type ('Percentage' or 'Fixed')
        
        Returns:
            QuerySet: Coupons with specified discount type
        """
        return self.filter(discount_type=discount_type)
    
    def validate_coupon(self, coupon, customer, subtotal) -> tuple:
        """
        Validate if coupon can be used.
        
        Args:
            coupon: Coupon instance
            customer: Customer instance
            subtotal: Order subtotal
        
        Returns:
            tuple: (is_valid: bool, message: str)
        """
        # Check if coupon is valid
        is_valid, msg = coupon.is_valid()
        if not is_valid:
            return False, msg
        
        # Check minimum purchase
        if subtotal < coupon.min_purchase:
            return False, f'Minimum purchase of Rs. {coupon.min_purchase} required'
        
        return True, 'Valid'
        """
        Get coupons by discount type.
        
        Args:
            discount_type (str): 'fixed' or 'percentage'
        
        Returns:
            QuerySet: Coupons of specified type
        """
        return self.filter(discount_type=discount_type)
    
    def is_valid(self, code: str) -> tuple:
        """
        Check if coupon is valid.
        
        Args:
            code (str): Coupon code
        
        Returns:
            tuple: (is_valid, message)
        """
        coupon = self.get_by_code(code)
        
        if not coupon:
            return False, "Coupon not found"
        
        if not coupon.is_active:
            return False, "Coupon is inactive"
        
        if datetime.now() > coupon.expiry_date.replace(tzinfo=None):
            return False, "Coupon has expired"
        
        if coupon.current_usage >= coupon.max_usage:
            return False, "Coupon usage limit reached"
        
        return True, "Valid"
    
    def can_be_used(self, code: str, order_amount) -> tuple:
        """
        Check if coupon can be used for an order.
        
        Args:
            code (str): Coupon code
            order_amount (Decimal): Order amount
        
        Returns:
            tuple: (can_use, message)
        """
        is_valid, msg = self.is_valid(code)
        if not is_valid:
            return False, msg
        
        coupon = self.get_by_code(code)
        
        if order_amount < coupon.min_purchase:
            return False, f"Minimum purchase of Rs. {coupon.min_purchase} required"
        
        return True, "Can be used"
    
    def get_usage_count(self, coupon_id: int) -> int:
        """
        Get usage count for a coupon.
        
        Args:
            coupon_id (int): Coupon ID
        
        Returns:
            int: Usage count
        """
        coupon = self.get_by_id(coupon_id)
        if not coupon:
            return 0
        
        return coupon.current_usage
    
    def get_remaining_uses(self, coupon_id: int) -> int:
        """
        Get remaining uses for a coupon.
        
        Args:
            coupon_id (int): Coupon ID
        
        Returns:
            int: Remaining uses
        """
        coupon = self.get_by_id(coupon_id)
        if not coupon:
            return 0
        
        return max(0, coupon.max_usage - coupon.current_usage)
    
    def deactivate_coupon(self, coupon_id: int) -> bool:
        """
        Deactivate a coupon.
        
        Args:
            coupon_id (int): Coupon ID
        
        Returns:
            bool: True if deactivated successfully
        """
        coupon = self.get_by_id(coupon_id)
        if not coupon:
            return False
        
        coupon.is_active = False
        coupon.save()
        return True
    
    def activate_coupon(self, coupon_id: int) -> bool:
        """
        Activate a coupon.
        
        Args:
            coupon_id (int): Coupon ID
        
        Returns:
            bool: True if activated successfully
        """
        coupon = self.get_by_id(coupon_id)
        if not coupon:
            return False
        
        coupon.is_active = True
        coupon.save()
        return True
    
    def get_coupons_with_usage(self) -> QuerySet:
        """
        Get coupons annotated with usage count.
        
        Returns:
            QuerySet: Coupons with usage_count annotation
        """
        return self.get_all().annotate(
            usage_count=Count('couponusage')
        ).order_by('-usage_count')
    
    def get_most_used_coupons(self, limit: int = 10) -> QuerySet:
        """
        Get most used coupons.
        
        Args:
            limit (int): Number of coupons to return
        
        Returns:
            QuerySet: Most used coupons
        """
        return self.get_coupons_with_usage()[:limit]
    
    def get_unused_coupons(self) -> QuerySet:
        """
        Get coupons that have never been used.
        
        Returns:
            QuerySet: Unused coupons
        """
        return self.get_all().annotate(
            usage_count=Count('couponusage')
        ).filter(usage_count=0)
    
    def get_expiring_soon(self, days: int = 7) -> QuerySet:
        """
        Get coupons expiring in next N days.
        
        Args:
            days (int): Number of days (default: 7)
        
        Returns:
            QuerySet: Coupons expiring soon
        """
        from datetime import timedelta
        
        end_date = datetime.now() + timedelta(days=days)
        return self.filter(
            is_active=True,
            expiry_date__gte=datetime.now(),
            expiry_date__lte=end_date
        ).order_by('expiry_date')
    
    def get_coupon_statistics(self) -> dict:
        """
        Get overall coupon statistics.
        
        Returns:
            dict: Statistics including counts and usage
        """
        total_coupons = self.count()
        active_coupons = self.get_active_coupons().count()
        expired_coupons = self.get_expired_coupons().count()
        
        # Get total usage
        from bookstore.models import CouponUsage
        total_usage = CouponUsage.objects.count()
        
        return {
            'total_coupons': total_coupons,
            'active_coupons': active_coupons,
            'expired_coupons': expired_coupons,
            'total_usage': total_usage,
        }

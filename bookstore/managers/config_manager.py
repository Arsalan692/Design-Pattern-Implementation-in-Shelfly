"""
Configuration Manager - Singleton
==================================

Singleton class for managing application configuration.
"""

from decimal import Decimal
from typing import Dict, Any, Optional
import threading


class ConfigManager:
    """
    Singleton Configuration Manager.
    
    Provides centralized access to application configuration.
    Thread-safe implementation using double-checked locking.
    
    Configuration includes:
        - Shipping rules
        - Discount rules
        - Payment settings
        - Business rules
    """
    
    _instance: Optional['ConfigManager'] = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """
        Create or return the singleton instance.
        
        Uses double-checked locking for thread safety.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize configuration (only once)."""
        if self._initialized:
            return
        
        self._initialized = True
        self._config: Dict[str, Any] = {}
        self._load_default_config()
    
    def _load_default_config(self) -> None:
        """Load default configuration values."""
        self._config = {
            # Shipping Configuration
            'shipping': {
                'free_shipping_threshold': Decimal('5000.00'),
                'base_shipping_fee': Decimal('50.00'),
                'per_book_fee_threshold': 5,
                'per_book_fee': Decimal('10.00'),
            },
            
            # Discount Configuration
            'discounts': {
                'order_value_tiers': [
                    {'min_amount': Decimal('5000.00'), 'percentage': Decimal('15')},
                    {'min_amount': Decimal('2000.00'), 'percentage': Decimal('10')},
                    {'min_amount': Decimal('1000.00'), 'percentage': Decimal('5')},
                ],
                'first_time_buyer_percentage': Decimal('15'),
            },
            
            # Inventory Configuration
            'inventory': {
                'low_stock_threshold': 5,
                'out_of_stock_threshold': 0,
                'reorder_quantity': 20,
            },
            
            # Order Configuration
            'orders': {
                'cancellable_statuses': ['Pending', 'Confirmed'],
                'auto_confirm_delay_hours': 24,
                'delivery_time_days': 5,
            },
            
            # Payment Configuration
            'payment': {
                'supported_methods': ['Cash', 'Card'],
                'card_types': ['Visa', 'Mastercard', 'American Express', 'Discover'],
            },
            
            # Notification Configuration
            'notifications': {
                'email_enabled': True,
                'sms_enabled': False,
                'push_enabled': False,
            },
            
            # Business Rules
            'business': {
                'min_order_amount': Decimal('100.00'),
                'max_order_items': 50,
                'max_quantity_per_item': 10,
            },
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.
        
        Supports nested keys using dot notation (e.g., 'shipping.base_fee').
        
        Args:
            key (str): Configuration key
            default (Any): Default value if key not found
        
        Returns:
            Any: Configuration value
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.
        
        Supports nested keys using dot notation.
        
        Args:
            key (str): Configuration key
            value (Any): Configuration value
        """
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration.
        
        Returns:
            Dict: All configuration
        """
        return self._config.copy()
    
    def reset(self) -> None:
        """Reset configuration to defaults."""
        self._load_default_config()
    
    # Convenience methods for common configurations
    
    def get_shipping_config(self) -> Dict[str, Any]:
        """Get shipping configuration."""
        return self.get('shipping', {})
    
    def get_discount_config(self) -> Dict[str, Any]:
        """Get discount configuration."""
        return self.get('discounts', {})
    
    def get_inventory_config(self) -> Dict[str, Any]:
        """Get inventory configuration."""
        return self.get('inventory', {})
    
    def get_order_config(self) -> Dict[str, Any]:
        """Get order configuration."""
        return self.get('orders', {})
    
    def get_payment_config(self) -> Dict[str, Any]:
        """Get payment configuration."""
        return self.get('payment', {})
    
    def get_notification_config(self) -> Dict[str, Any]:
        """Get notification configuration."""
        return self.get('notifications', {})
    
    def get_business_rules(self) -> Dict[str, Any]:
        """Get business rules."""
        return self.get('business', {})
    
    # Specific configuration getters
    
    def get_free_shipping_threshold(self) -> Decimal:
        """Get free shipping threshold."""
        return self.get('shipping.free_shipping_threshold', Decimal('5000.00'))
    
    def get_base_shipping_fee(self) -> Decimal:
        """Get base shipping fee."""
        return self.get('shipping.base_shipping_fee', Decimal('50.00'))
    
    def get_low_stock_threshold(self) -> int:
        """Get low stock threshold."""
        return self.get('inventory.low_stock_threshold', 5)
    
    def get_first_time_buyer_discount(self) -> Decimal:
        """Get first-time buyer discount percentage."""
        return self.get('discounts.first_time_buyer_percentage', Decimal('15'))
    
    def get_order_value_tiers(self) -> list:
        """Get order value discount tiers."""
        return self.get('discounts.order_value_tiers', [])
    
    def is_email_enabled(self) -> bool:
        """Check if email notifications are enabled."""
        return self.get('notifications.email_enabled', True)
    
    def get_cancellable_statuses(self) -> list:
        """Get list of cancellable order statuses."""
        return self.get('orders.cancellable_statuses', ['Pending', 'Confirmed'])
    
    @classmethod
    def reset_instance(cls) -> None:
        """
        Reset the singleton instance (for testing).
        
        WARNING: Only use in tests!
        """
        with cls._lock:
            cls._instance = None

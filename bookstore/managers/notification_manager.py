"""
Notification Manager - Singleton
=================================

Singleton class for managing order notifications using Observer Pattern.
"""

from typing import Optional
import threading
from ..observers.observer import Observer
from ..observers.order_subject import OrderSubject
from ..observers.email_observer import EmailNotificationObserver
from ..observers.log_observer import LogObserver
from ..observers.inventory_observer import InventoryObserver


class NotificationManager:
    """
    Singleton Notification Manager.
    
    Manages the OrderSubject and all observers for order notifications.
    Thread-safe implementation using double-checked locking.
    
    Features:
        - Centralized notification management
        - Observer registration/deregistration
        - Configuration-based observer setup
        - Thread-safe singleton pattern
    """
    
    _instance: Optional['NotificationManager'] = None
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
        """Initialize notification manager (only once)."""
        if self._initialized:
            return
        
        self._initialized = True
        self._order_subject = OrderSubject()
        self._observers = {}
        self._setup_default_observers()
    
    def _setup_default_observers(self) -> None:
        """Setup default observers based on configuration."""
        from .config_manager import ConfigManager
        
        config = ConfigManager()
        
        # Email observer
        if config.is_email_enabled():
            email_observer = EmailNotificationObserver(enabled=True)
            self.register_observer('email', email_observer)
        
        # Log observer (always enabled)
        log_observer = LogObserver(enabled=True)
        self.register_observer('log', log_observer)
        
        # Inventory observer
        low_stock_threshold = config.get_low_stock_threshold()
        inventory_observer = InventoryObserver(
            low_stock_threshold=low_stock_threshold,
            enabled=True
        )
        self.register_observer('inventory', inventory_observer)
    
    def register_observer(self, name: str, observer: Observer) -> None:
        """
        Register an observer.
        
        Args:
            name (str): Observer identifier
            observer (Observer): Observer instance
        """
        if name not in self._observers:
            self._observers[name] = observer
            self._order_subject.attach(observer)
    
    def unregister_observer(self, name: str) -> None:
        """
        Unregister an observer.
        
        Args:
            name (str): Observer identifier
        """
        if name in self._observers:
            observer = self._observers[name]
            self._order_subject.detach(observer)
            del self._observers[name]
    
    def get_observer(self, name: str) -> Optional[Observer]:
        """
        Get observer by name.
        
        Args:
            name (str): Observer identifier
        
        Returns:
            Optional[Observer]: Observer instance or None
        """
        return self._observers.get(name)
    
    def get_all_observers(self) -> dict:
        """
        Get all registered observers.
        
        Returns:
            dict: Dictionary of observers
        """
        return self._observers.copy()
    
    def get_observer_count(self) -> int:
        """
        Get number of registered observers.
        
        Returns:
            int: Observer count
        """
        return len(self._observers)
    
    # Order event notification methods
    
    def notify_order_placed(self, order) -> None:
        """
        Notify observers that an order was placed.
        
        Args:
            order: Order instance
        """
        self._order_subject.notify_order_placed(order)
    
    def notify_order_confirmed(self, order) -> None:
        """
        Notify observers that an order was confirmed.
        
        Args:
            order: Order instance
        """
        self._order_subject.notify_order_confirmed(order)
    
    def notify_order_shipped(self, order) -> None:
        """
        Notify observers that an order was shipped.
        
        Args:
            order: Order instance
        """
        self._order_subject.notify_order_shipped(order)
    
    def notify_order_delivered(self, order) -> None:
        """
        Notify observers that an order was delivered.
        
        Args:
            order: Order instance
        """
        self._order_subject.notify_order_delivered(order)
    
    def notify_order_cancelled(self, order, reason: str = None) -> None:
        """
        Notify observers that an order was cancelled.
        
        Args:
            order: Order instance
            reason (str): Cancellation reason
        """
        self._order_subject.notify_order_cancelled(order, reason)
    
    def notify_payment_received(self, order, payment) -> None:
        """
        Notify observers that payment was received.
        
        Args:
            order: Order instance
            payment: Payment instance
        """
        self._order_subject.notify_payment_received(order, payment)
    
    # Custom event notification
    
    def notify_custom_event(self, event_type: str, data: dict) -> None:
        """
        Notify observers about a custom event.
        
        Args:
            event_type (str): Event type
            data (dict): Event data
        """
        self._order_subject.notify(event_type, data)
    
    # Observer management
    
    def enable_observer(self, name: str) -> bool:
        """
        Enable an observer.
        
        Args:
            name (str): Observer identifier
        
        Returns:
            bool: True if enabled, False if not found
        """
        observer = self._observers.get(name)
        if observer and hasattr(observer, 'enabled'):
            observer.enabled = True
            return True
        return False
    
    def disable_observer(self, name: str) -> bool:
        """
        Disable an observer.
        
        Args:
            name (str): Observer identifier
        
        Returns:
            bool: True if disabled, False if not found
        """
        observer = self._observers.get(name)
        if observer and hasattr(observer, 'enabled'):
            observer.enabled = False
            return True
        return False
    
    def is_observer_enabled(self, name: str) -> bool:
        """
        Check if an observer is enabled.
        
        Args:
            name (str): Observer identifier
        
        Returns:
            bool: True if enabled, False otherwise
        """
        observer = self._observers.get(name)
        if observer and hasattr(observer, 'enabled'):
            return observer.enabled
        return False
    
    # Testing utilities
    
    def clear_all_observers(self) -> None:
        """
        Clear all observers (for testing).
        
        WARNING: Only use in tests!
        """
        for observer in list(self._observers.values()):
            self._order_subject.detach(observer)
        self._observers.clear()
    
    def reset_observers(self) -> None:
        """
        Reset to default observers (for testing).
        
        WARNING: Only use in tests!
        """
        self.clear_all_observers()
        self._setup_default_observers()
    
    @classmethod
    def reset_instance(cls) -> None:
        """
        Reset the singleton instance (for testing).
        
        WARNING: Only use in tests!
        """
        with cls._lock:
            cls._instance = None

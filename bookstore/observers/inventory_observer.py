"""
Inventory Observer
==================

Observer that monitors inventory levels and sends alerts.
"""

from typing import Dict, Any
from .observer import Observer


class InventoryObserver(Observer):
    """
    Observer that monitors inventory levels.
    
    Sends alerts when:
        - Stock is low (< threshold)
        - Stock is out (= 0)
        - Stock is restored after cancellation
    """
    
    def __init__(self, low_stock_threshold: int = 5, enabled: bool = True):
        """
        Initialize the inventory observer.
        
        Args:
            low_stock_threshold (int): Threshold for low stock alerts
            enabled (bool): Whether inventory monitoring is enabled
        """
        self.low_stock_threshold = low_stock_threshold
        self.enabled = enabled
        self.alerts = []  # For testing purposes
    
    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Handle event by checking inventory.
        
        Args:
            event_type (str): Type of event
            data (Dict): Event data
        """
        if not self.enabled:
            return
        
        # Only monitor order-related events
        if event_type in ['order_placed', 'order_confirmed']:
            self._check_inventory_after_order(data)
        elif event_type == 'order_cancelled':
            self._check_inventory_after_cancellation(data)
    
    def _check_inventory_after_order(self, data: Dict[str, Any]) -> None:
        """
        Check inventory levels after an order.
        
        Args:
            data (Dict): Event data
        """
        order_id = data['order_id']
        
        # Get order items (in real implementation, would query database)
        # For demo, we'll simulate the check
        
        alert = {
            'type': 'order_placed',
            'order_id': order_id,
            'message': f'Inventory checked after order #{order_id}'
        }
        
        self.alerts.append(alert)
        print(f"📦 Inventory check triggered for Order #{order_id}")
    
    def _check_inventory_after_cancellation(self, data: Dict[str, Any]) -> None:
        """
        Check inventory levels after cancellation.
        
        Args:
            data (Dict): Event data
        """
        order_id = data['order_id']
        
        alert = {
            'type': 'order_cancelled',
            'order_id': order_id,
            'message': f'Stock restored after Order #{order_id} cancellation'
        }
        
        self.alerts.append(alert)
        print(f"📦 Stock restored after Order #{order_id} cancellation")
    
    def check_book_stock(self, book) -> None:
        """
        Check stock level for a specific book.
        
        Args:
            book: Book instance
        """
        if not self.enabled:
            return
        
        if book.stock == 0:
            self._send_out_of_stock_alert(book)
        elif book.stock <= self.low_stock_threshold:
            self._send_low_stock_alert(book)
    
    def _send_low_stock_alert(self, book) -> None:
        """
        Send low stock alert.
        
        Args:
            book: Book instance
        """
        alert = {
            'type': 'low_stock',
            'book_id': book.id,
            'book_title': book.title,
            'stock': book.stock,
            'message': f'Low stock alert: {book.title} (Stock: {book.stock})'
        }
        
        self.alerts.append(alert)
        print(f"⚠️  LOW STOCK: {book.title} - Only {book.stock} left!")
    
    def _send_out_of_stock_alert(self, book) -> None:
        """
        Send out of stock alert.
        
        Args:
            book: Book instance
        """
        alert = {
            'type': 'out_of_stock',
            'book_id': book.id,
            'book_title': book.title,
            'stock': 0,
            'message': f'Out of stock: {book.title}'
        }
        
        self.alerts.append(alert)
        print(f"🚨 OUT OF STOCK: {book.title}")
    
    def get_alerts(self) -> list:
        """
        Get list of alerts (for testing).
        
        Returns:
            list: Alert entries
        """
        return self.alerts
    
    def clear_alerts(self) -> None:
        """Clear alerts list (for testing)."""
        self.alerts.clear()
    
    def get_low_stock_alerts(self) -> list:
        """
        Get low stock alerts only.
        
        Returns:
            list: Low stock alerts
        """
        return [alert for alert in self.alerts if alert['type'] == 'low_stock']
    
    def get_out_of_stock_alerts(self) -> list:
        """
        Get out of stock alerts only.
        
        Returns:
            list: Out of stock alerts
        """
        return [alert for alert in self.alerts if alert['type'] == 'out_of_stock']

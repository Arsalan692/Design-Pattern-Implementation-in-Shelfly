"""
Log Observer
============

Observer that logs order events.
"""

from typing import Dict, Any
from django.utils import timezone
from .observer import Observer


class LogObserver(Observer):
    """
    Observer that logs order events.
    
    Useful for debugging, auditing, and monitoring.
    """
    
    def __init__(self, enabled: bool = True):
        """
        Initialize the log observer.
        
        Args:
            enabled (bool): Whether logging is enabled
        """
        self.enabled = enabled
        self.logs = []  # For testing purposes
    
    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Handle event by logging it.
        
        Args:
            event_type (str): Type of event
            data (Dict): Event data
        """
        if not self.enabled:
            return
        
        timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = {
            'timestamp': timestamp,
            'event_type': event_type,
            'data': data
        }
        
        # Log to console
        self._log_to_console(log_entry)
        
        # Store for testing
        self.logs.append(log_entry)
        
        # Prevent memory leaks by capping the log size
        if len(self.logs) > 100:
            self.logs = self.logs[-100:]
    
    def _log_to_console(self, log_entry: Dict[str, Any]) -> None:
        """
        Log entry to console.
        
        Args:
            log_entry (Dict): Log entry
        """
        timestamp = log_entry['timestamp']
        event_type = log_entry['event_type']
        data = log_entry['data']
        
        # Format log message
        if event_type == 'order_placed':
            message = f"Order #{data['order_id']} placed by {data['customer'].user.username} - Rs. {data['total_amount']}"
        elif event_type == 'order_confirmed':
            message = f"Order #{data['order_id']} confirmed"
        elif event_type == 'order_shipped':
            message = f"Order #{data['order_id']} shipped"
        elif event_type == 'order_delivered':
            message = f"Order #{data['order_id']} delivered"
        elif event_type == 'order_cancelled':
            reason = data.get('reason', 'No reason')
            message = f"Order #{data['order_id']} cancelled - Reason: {reason}"
        elif event_type == 'payment_received':
            message = f"Payment received for Order #{data['order_id']} - Rs. {data['amount']} via {data['method']}"
        else:
            message = f"Unknown event: {event_type}"
        
        print(f"📝 [{timestamp}] {event_type.upper()}: {message}")
    
    def get_logs(self) -> list:
        """
        Get list of logs (for testing).
        
        Returns:
            list: Log entries
        """
        return self.logs
    
    def clear_logs(self) -> None:
        """Clear logs list (for testing)."""
        self.logs.clear()
    
    def get_logs_by_event_type(self, event_type: str) -> list:
        """
        Get logs filtered by event type.
        
        Args:
            event_type (str): Event type to filter
        
        Returns:
            list: Filtered log entries
        """
        return [log for log in self.logs if log['event_type'] == event_type]
    
    def get_logs_for_order(self, order_id: int) -> list:
        """
        Get logs for a specific order.
        
        Args:
            order_id (int): Order ID
        
        Returns:
            list: Log entries for the order
        """
        return [
            log for log in self.logs 
            if log['data'].get('order_id') == order_id
        ]

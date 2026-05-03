"""
Order Subject
=============

Subject that notifies observers about order events.
"""

from typing import List, Dict, Any
from .observer import Observer


class OrderSubject:
    """
    Subject for order-related events.
    
    Maintains a list of observers and notifies them when events occur.
    
    Events:
        - order_placed: New order created
        - order_confirmed: Order confirmed
        - order_shipped: Order shipped
        - order_delivered: Order delivered
        - order_cancelled: Order cancelled
        - payment_received: Payment completed
    """
    
    def __init__(self):
        """Initialize the subject with empty observer list."""
        self._observers: List[Observer] = []
    
    def attach(self, observer: Observer) -> None:
        """
        Attach an observer to the subject.
        
        Args:
            observer (Observer): Observer to attach
        """
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: Observer) -> None:
        """
        Detach an observer from the subject.
        
        Args:
            observer (Observer): Observer to detach
        """
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Notify all observers about an event.
        
        Args:
            event_type (str): Type of event
            data (Dict): Event data
        """
        for observer in self._observers:
            try:
                observer.update(event_type, data)
            except Exception as e:
                # Log error but don't stop other notifications
                print(f"Error notifying {observer.get_name()}: {str(e)}")
    
    def get_observer_count(self) -> int:
        """
        Get number of attached observers.
        
        Returns:
            int: Observer count
        """
        return len(self._observers)
    
    def get_observers(self) -> List[Observer]:
        """
        Get list of attached observers.
        
        Returns:
            List[Observer]: Observers
        """
        return self._observers.copy()
    
    # Event-specific notification methods
    
    def notify_order_placed(self, order) -> None:
        """
        Notify observers that an order was placed.
        
        Args:
            order: Order instance
        """
        data = {
            'order_id': order.id,
            'customer': order.customer,
            'total_amount': order.total_amount,
            'status': order.status,
        }
        self.notify('order_placed', data)
    
    def notify_order_confirmed(self, order) -> None:
        """
        Notify observers that an order was confirmed.
        
        Args:
            order: Order instance
        """
        data = {
            'order_id': order.id,
            'customer': order.customer,
            'total_amount': order.total_amount,
        }
        self.notify('order_confirmed', data)
    
    def notify_order_shipped(self, order) -> None:
        """
        Notify observers that an order was shipped.
        
        Args:
            order: Order instance
        """
        data = {
            'order_id': order.id,
            'customer': order.customer,
        }
        self.notify('order_shipped', data)
    
    def notify_order_delivered(self, order) -> None:
        """
        Notify observers that an order was delivered.
        
        Args:
            order: Order instance
        """
        data = {
            'order_id': order.id,
            'customer': order.customer,
        }
        self.notify('order_delivered', data)
    
    def notify_order_cancelled(self, order, reason: str = None) -> None:
        """
        Notify observers that an order was cancelled.
        
        Args:
            order: Order instance
            reason (str): Cancellation reason
        """
        data = {
            'order_id': order.id,
            'customer': order.customer,
            'reason': reason,
        }
        self.notify('order_cancelled', data)
    
    def notify_payment_received(self, order, payment) -> None:
        """
        Notify observers that payment was received.
        
        Args:
            order: Order instance
            payment: Payment instance
        """
        data = {
            'order_id': order.id,
            'customer': order.customer,
            'amount': payment.amount,
            'method': payment.method,
        }
        self.notify('payment_received', data)

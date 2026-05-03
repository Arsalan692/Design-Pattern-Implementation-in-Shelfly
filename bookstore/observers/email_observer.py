"""
Email Notification Observer
============================

Observer that sends email notifications for order events.
"""

from typing import Dict, Any
from .observer import Observer


class EmailNotificationObserver(Observer):
    """
    Observer that sends email notifications.
    
    In a real system, this would integrate with an email service
    (SendGrid, AWS SES, etc.). For demo purposes, we'll log the emails.
    """
    
    def __init__(self, enabled: bool = True):
        """
        Initialize the email observer.
        
        Args:
            enabled (bool): Whether email notifications are enabled
        """
        self.enabled = enabled
        self.sent_emails = []  # For testing purposes
    
    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Handle event by sending appropriate email.
        
        Args:
            event_type (str): Type of event
            data (Dict): Event data
        """
        if not self.enabled:
            return
        
        # Route to appropriate email handler
        handlers = {
            'order_placed': self._send_order_placed_email,
            'order_confirmed': self._send_order_confirmed_email,
            'order_shipped': self._send_order_shipped_email,
            'order_delivered': self._send_order_delivered_email,
            'order_cancelled': self._send_order_cancelled_email,
            'payment_received': self._send_payment_received_email,
        }
        
        handler = handlers.get(event_type)
        if handler:
            handler(data)
    
    def _send_order_placed_email(self, data: Dict[str, Any]) -> None:
        """Send email when order is placed."""
        customer = data['customer']
        order_id = data['order_id']
        total = data['total_amount']
        
        email_content = {
            'to': customer.user.email,
            'subject': f'Order #{order_id} Placed Successfully',
            'body': f"""
                Dear {customer.user.username},
                
                Thank you for your order!
                
                Order ID: #{order_id}
                Total Amount: Rs. {total}
                Status: {data['status']}
                
                We'll notify you when your order is confirmed.
                
                Best regards,
                Shelfly Team
            """
        }
        
        self._send_email(email_content)
    
    def _send_order_confirmed_email(self, data: Dict[str, Any]) -> None:
        """Send email when order is confirmed."""
        customer = data['customer']
        order_id = data['order_id']
        
        email_content = {
            'to': customer.user.email,
            'subject': f'Order #{order_id} Confirmed',
            'body': f"""
                Dear {customer.user.username},
                
                Your order has been confirmed and is being prepared for shipment.
                
                Order ID: #{order_id}
                
                You'll receive another email when your order ships.
                
                Best regards,
                Shelfly Team
            """
        }
        
        self._send_email(email_content)
    
    def _send_order_shipped_email(self, data: Dict[str, Any]) -> None:
        """Send email when order is shipped."""
        customer = data['customer']
        order_id = data['order_id']
        
        email_content = {
            'to': customer.user.email,
            'subject': f'Order #{order_id} Shipped',
            'body': f"""
                Dear {customer.user.username},
                
                Great news! Your order has been shipped.
                
                Order ID: #{order_id}
                
                Your order should arrive within 3-5 business days.
                
                Best regards,
                Shelfly Team
            """
        }
        
        self._send_email(email_content)
    
    def _send_order_delivered_email(self, data: Dict[str, Any]) -> None:
        """Send email when order is delivered."""
        customer = data['customer']
        order_id = data['order_id']
        
        email_content = {
            'to': customer.user.email,
            'subject': f'Order #{order_id} Delivered',
            'body': f"""
                Dear {customer.user.username},
                
                Your order has been delivered!
                
                Order ID: #{order_id}
                
                We hope you enjoy your books. Please leave us a review!
                
                Best regards,
                Shelfly Team
            """
        }
        
        self._send_email(email_content)
    
    def _send_order_cancelled_email(self, data: Dict[str, Any]) -> None:
        """Send email when order is cancelled."""
        customer = data['customer']
        order_id = data['order_id']
        reason = data.get('reason', 'No reason provided')
        
        email_content = {
            'to': customer.user.email,
            'subject': f'Order #{order_id} Cancelled',
            'body': f"""
                Dear {customer.user.username},
                
                Your order has been cancelled.
                
                Order ID: #{order_id}
                Reason: {reason}
                
                If you have any questions, please contact our support team.
                
                Best regards,
                Shelfly Team
            """
        }
        
        self._send_email(email_content)
    
    def _send_payment_received_email(self, data: Dict[str, Any]) -> None:
        """Send email when payment is received."""
        customer = data['customer']
        order_id = data['order_id']
        amount = data['amount']
        method = data['method']
        
        email_content = {
            'to': customer.user.email,
            'subject': f'Payment Received for Order #{order_id}',
            'body': f"""
                Dear {customer.user.username},
                
                We've received your payment!
                
                Order ID: #{order_id}
                Amount: Rs. {amount}
                Payment Method: {method}
                
                Your order will be processed shortly.
                
                Best regards,
                Shelfly Team
            """
        }
        
        self._send_email(email_content)
    
    def _send_email(self, email_content: Dict[str, Any]) -> None:
        """
        Send email (simulated for demo).
        
        In production, this would use an email service.
        
        Args:
            email_content (Dict): Email details
        """
        # For demo purposes, just log and store
        print(f"📧 Email sent to {email_content['to']}: {email_content['subject']}")
        
        # Store for testing
        self.sent_emails.append(email_content)
        
        # Prevent memory leak
        if len(self.sent_emails) > 100:
            self.sent_emails = self.sent_emails[-100:]
    
    def get_sent_emails(self) -> list:
        """
        Get list of sent emails (for testing).
        
        Returns:
            list: Sent emails
        """
        return self.sent_emails
    
    def clear_sent_emails(self) -> None:
        """Clear sent emails list (for testing)."""
        self.sent_emails.clear()

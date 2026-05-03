"""
Observer Pattern Implementation
================================

This module implements the Observer Pattern for event-driven notifications.

Design Pattern: Observer (Behavioral Pattern)
Problem Solved: No notification system for order events
Benefits:
    - Decoupled notification system
    - Easy to add new notification channels
    - Real-time updates without tight coupling
    - Event-driven architecture
"""

from .observer import Observer
from .order_subject import OrderSubject
from .email_observer import EmailNotificationObserver
from .log_observer import LogObserver
from .inventory_observer import InventoryObserver

__all__ = [
    'Observer',
    'OrderSubject',
    'EmailNotificationObserver',
    'LogObserver',
    'InventoryObserver',
]

"""
Manager Classes - Singleton Pattern
====================================

This module implements the Singleton Pattern for shared resources.

Design Pattern: Singleton (Creational Pattern)
Problem Solved: Multiple instances of configuration and cart management
Benefits:
    - Controlled access to shared resources
    - Memory efficiency
    - Consistent state management
    - Global access point
"""

from .config_manager import ConfigManager
from .notification_manager import NotificationManager

__all__ = [
    'ConfigManager',
    'NotificationManager',
]

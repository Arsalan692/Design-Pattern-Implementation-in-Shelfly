"""
Observer Interface
==================

Abstract base class for all observers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class Observer(ABC):
    """
    Abstract base class for observers.
    
    Observers are notified when events occur in the subject.
    Each observer must implement the update() method.
    """
    
    @abstractmethod
    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Called when the subject's state changes.
        
        Args:
            event_type (str): Type of event (e.g., 'order_placed', 'order_cancelled')
            data (Dict): Event data
        """
        pass
    
    def get_name(self) -> str:
        """
        Get observer name for identification.
        
        Returns:
            str: Observer name
        """
        return self.__class__.__name__

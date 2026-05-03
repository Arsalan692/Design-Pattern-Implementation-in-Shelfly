"""
Base Repository
===============

Generic base repository with common CRUD operations.
"""

from typing import List, Optional, Dict, Any
from django.db.models import Model, QuerySet


class BaseRepository:
    """
    Base repository providing common CRUD operations.
    
    This follows the Repository Pattern, providing an abstraction
    layer between business logic and data access.
    
    Subclasses should set the model class and can override/extend methods.
    """
    
    model = None  # Must be set by subclasses
    
    def __init__(self):
        """Initialize the repository."""
        if self.model is None:
            raise NotImplementedError("Subclasses must set the model attribute")
    
    def get_all(self) -> QuerySet:
        """
        Get all instances of the model.
        
        Returns:
            QuerySet: All model instances
        """
        return self.model.objects.all()
    
    def get_by_id(self, id: int) -> Optional[Model]:
        """
        Get a single instance by ID.
        
        Args:
            id (int): Instance ID
        
        Returns:
            Model instance or None if not found
        """
        try:
            return self.model.objects.get(id=id)
        except self.model.DoesNotExist:
            return None
    
    def filter(self, **kwargs) -> QuerySet:
        """
        Filter instances by criteria.
        
        Args:
            **kwargs: Filter criteria
        
        Returns:
            QuerySet: Filtered instances
        """
        return self.model.objects.filter(**kwargs)
    
    def create(self, **kwargs) -> Model:
        """
        Create a new instance.
        
        Args:
            **kwargs: Instance data
        
        Returns:
            Model: Created instance
        """
        return self.model.objects.create(**kwargs)
    
    def update(self, id: int, **kwargs) -> Optional[Model]:
        """
        Update an instance by ID.
        
        Args:
            id (int): Instance ID
            **kwargs: Fields to update
        
        Returns:
            Model: Updated instance or None if not found
        """
        instance = self.get_by_id(id)
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            instance.save()
        return instance
    
    def delete(self, id: int) -> bool:
        """
        Delete an instance by ID.
        
        Args:
            id (int): Instance ID
        
        Returns:
            bool: True if deleted, False if not found
        """
        instance = self.get_by_id(id)
        if instance:
            instance.delete()
            return True
        return False
    
    def exists(self, **kwargs) -> bool:
        """
        Check if instance(s) exist matching criteria.
        
        Args:
            **kwargs: Filter criteria
        
        Returns:
            bool: True if exists
        """
        return self.model.objects.filter(**kwargs).exists()
    
    def count(self, **kwargs) -> int:
        """
        Count instances matching criteria.
        
        Args:
            **kwargs: Filter criteria (optional)
        
        Returns:
            int: Count of instances
        """
        if kwargs:
            return self.model.objects.filter(**kwargs).count()
        return self.model.objects.count()
    
    def get_or_create(self, defaults: Dict = None, **kwargs) -> tuple:
        """
        Get or create an instance.
        
        Args:
            defaults (Dict): Default values for creation
            **kwargs: Lookup criteria
        
        Returns:
            tuple: (instance, created)
        """
        return self.model.objects.get_or_create(defaults=defaults, **kwargs)
    
    def bulk_create(self, instances: List[Dict]) -> List[Model]:
        """
        Create multiple instances efficiently.
        
        Args:
            instances (List[Dict]): List of instance data
        
        Returns:
            List[Model]: Created instances
        """
        objects = [self.model(**data) for data in instances]
        return self.model.objects.bulk_create(objects)
    
    def first(self, **kwargs) -> Optional[Model]:
        """
        Get first instance matching criteria.
        
        Args:
            **kwargs: Filter criteria
        
        Returns:
            Model instance or None
        """
        return self.model.objects.filter(**kwargs).first()
    
    def last(self, **kwargs) -> Optional[Model]:
        """
        Get last instance matching criteria.
        
        Args:
            **kwargs: Filter criteria
        
        Returns:
            Model instance or None
        """
        return self.model.objects.filter(**kwargs).last()

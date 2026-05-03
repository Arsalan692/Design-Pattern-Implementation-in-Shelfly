"""
Book Repository
===============

Repository for Book model operations.
"""

from typing import List, Optional
from django.db.models import Q, QuerySet
from decimal import Decimal

from .base_repository import BaseRepository
from bookstore.models import Book


class BookRepository(BaseRepository):
    """
    Repository for Book model.
    
    Provides book-specific query methods:
        - Search by title, author, category, ISBN
        - Filter by category
        - Filter by price range
        - Check stock availability
        - Get low stock books
    """
    
    model = Book
    
    def search(self, query: str) -> QuerySet:
        """
        Search books by title, author, category, or ISBN.
        
        Args:
            query (str): Search query
        
        Returns:
            QuerySet: Matching books
        """
        if not query:
            return self.get_all()
        
        return self.model.objects.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(category__icontains=query) |
            Q(isbn__icontains=query)
        )
    
    def get_by_category(self, category: str) -> QuerySet:
        """
        Get books by category.
        
        Args:
            category (str): Category name
        
        Returns:
            QuerySet: Books in category
        """
        return self.filter(category=category)
    
    def get_by_author(self, author: str) -> QuerySet:
        """
        Get books by author.
        
        Args:
            author (str): Author name
        
        Returns:
            QuerySet: Books by author
        """
        return self.filter(author__icontains=author)
    
    def get_by_price_range(
        self, 
        min_price: Optional[Decimal] = None, 
        max_price: Optional[Decimal] = None
    ) -> QuerySet:
        """
        Get books within price range.
        
        Args:
            min_price (Decimal): Minimum price (optional)
            max_price (Decimal): Maximum price (optional)
        
        Returns:
            QuerySet: Books in price range
        """
        queryset = self.get_all()
        
        if min_price is not None:
            queryset = queryset.filter(price__gte=min_price)
        
        if max_price is not None:
            queryset = queryset.filter(price__lte=max_price)
        
        return queryset
    
    def get_in_stock(self) -> QuerySet:
        """
        Get books that are in stock.
        
        Returns:
            QuerySet: Books with stock > 0
        """
        return self.filter(stock__gt=0)
    
    def get_out_of_stock(self) -> QuerySet:
        """
        Get books that are out of stock.
        
        Returns:
            QuerySet: Books with stock = 0
        """
        return self.filter(stock=0)
    
    def get_low_stock(self, threshold: int = 5) -> QuerySet:
        """
        Get books with low stock.
        
        Args:
            threshold (int): Stock threshold (default: 5)
        
        Returns:
            QuerySet: Books with stock <= threshold
        """
        return self.filter(stock__lte=threshold, stock__gt=0)
    
    def is_available(self, book_id: int, quantity: int = 1) -> bool:
        """
        Check if book is available in requested quantity.
        
        Args:
            book_id (int): Book ID
            quantity (int): Requested quantity
        
        Returns:
            bool: True if available
        """
        book = self.get_by_id(book_id)
        if not book:
            return False
        return book.stock >= quantity
    
    def reduce_stock(self, book_id: int, quantity: int) -> bool:
        """
        Reduce book stock.
        
        Args:
            book_id (int): Book ID
            quantity (int): Quantity to reduce
        
        Returns:
            bool: True if successful, False if insufficient stock
        """
        book = self.get_by_id(book_id)
        if not book or book.stock < quantity:
            return False
        
        book.stock -= quantity
        book.save()
        return True
    
    def increase_stock(self, book_id: int, quantity: int) -> bool:
        """
        Increase book stock.
        
        Args:
            book_id (int): Book ID
            quantity (int): Quantity to add
        
        Returns:
            bool: True if successful
        """
        book = self.get_by_id(book_id)
        if not book:
            return False
        
        book.stock += quantity
        book.save()
        return True
    
    def get_by_isbn(self, isbn: str) -> Optional[Book]:
        """
        Get book by ISBN.
        
        Args:
            isbn (str): ISBN number
        
        Returns:
            Book instance or None
        """
        return self.first(isbn=isbn)
    
    def get_all_categories(self) -> List[str]:
        """
        Get list of all unique categories.
        
        Returns:
            List[str]: Category names
        """
        return list(
            self.model.objects.values_list('category', flat=True)
            .distinct()
            .order_by('category')
        )
    
    def get_all_authors(self) -> List[str]:
        """
        Get list of all unique authors.
        
        Returns:
            List[str]: Author names
        """
        return list(
            self.model.objects.values_list('author', flat=True)
            .distinct()
            .order_by('author')
        )
    
    def get_featured_books(self, limit: int = 10) -> QuerySet:
        """
        Get featured books (in stock, ordered by ID).
        
        Args:
            limit (int): Number of books to return
        
        Returns:
            QuerySet: Featured books
        """
        return self.get_in_stock().order_by('-id')[:limit]

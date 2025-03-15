"""
Function Registry for the Dudoxx Extraction system.

This module provides a registry for callback functions used in domain definitions,
allowing for custom processing at various stages of the extraction pipeline.
"""

from typing import Dict, Any, Optional, Callable, List, Union
import re
from datetime import datetime


class FunctionRegistry:
    """
    Registry for callback functions used in domain definitions.
    
    This class provides methods for registering and retrieving callback functions
    that can be referenced by name in domain, sub-domain, and field definitions.
    It follows the singleton pattern to ensure a single registry instance.
    """
    
    _instance = None
    
    def __new__(cls):
        """
        Create a new instance of the function registry.
        
        Returns:
            FunctionRegistry: Function registry instance
        """
        if cls._instance is None:
            cls._instance = super(FunctionRegistry, cls).__new__(cls)
            cls._instance._functions = {}
            cls._instance._initialize_default_functions()
            
        return cls._instance
    
    def _initialize_default_functions(self) -> None:
        """Initialize the registry with default functions."""
        # Date formatting functions
        self.register_function("format_date_iso", self._format_date_iso)
        self.register_function("format_date_us", self._format_date_us)
        self.register_function("format_date_eu", self._format_date_eu)
        
        # Validation functions
        self.register_function("validate_date", self._validate_date)
        self.register_function("validate_email", self._validate_email)
        self.register_function("validate_phone", self._validate_phone)
        
        # Post-processing functions
        self.register_function("normalize_whitespace", self._normalize_whitespace)
        self.register_function("capitalize_names", self._capitalize_names)
        self.register_function("extract_numbers", self._extract_numbers)
    
    def register_function(self, name: str, func: Callable) -> None:
        """
        Register a function.
        
        Args:
            name: Name of the function
            func: Function to register
        """
        self._functions[name] = func
    
    def get_function(self, name: str) -> Optional[Callable]:
        """
        Get a function by name.
        
        Args:
            name: Name of the function
            
        Returns:
            Optional[Callable]: Function or None if not found
        """
        return self._functions.get(name)
    
    def call_function(self, name: str, *args, **kwargs) -> Any:
        """
        Call a function by name.
        
        Args:
            name: Name of the function
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Any: Function result
            
        Raises:
            ValueError: If function not found
        """
        func = self.get_function(name)
        if func is None:
            raise ValueError(f"Function '{name}' not found in registry")
        return func(*args, **kwargs)
    
    def get_all_function_names(self) -> List[str]:
        """
        Get the names of all registered functions.
        
        Returns:
            List[str]: List of function names
        """
        return list(self._functions.keys())
    
    # Default formatting functions
    def _format_date_iso(self, date_str: str) -> str:
        """
        Format date as ISO 8601 (YYYY-MM-DD).
        
        Args:
            date_str: Date string
            
        Returns:
            str: Formatted date
        """
        # Try common date formats
        formats = [
            "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", 
            "%B %d, %Y", "%b %d, %Y", "%d %B %Y", "%d %b %Y"
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        # Try to extract date using regex
        date_match = re.search(r'\d{4}-\d{2}-\d{2}', date_str)
        if date_match:
            return date_match.group(0)
        
        # Return original if parsing fails
        return date_str
    
    def _format_date_us(self, date_str: str) -> str:
        """
        Format date as US format (MM/DD/YYYY).
        
        Args:
            date_str: Date string
            
        Returns:
            str: Formatted date
        """
        iso_date = self._format_date_iso(date_str)
        try:
            dt = datetime.strptime(iso_date, "%Y-%m-%d")
            return dt.strftime("%m/%d/%Y")
        except ValueError:
            return date_str
    
    def _format_date_eu(self, date_str: str) -> str:
        """
        Format date as EU format (DD/MM/YYYY).
        
        Args:
            date_str: Date string
            
        Returns:
            str: Formatted date
        """
        iso_date = self._format_date_iso(date_str)
        try:
            dt = datetime.strptime(iso_date, "%Y-%m-%d")
            return dt.strftime("%d/%m/%Y")
        except ValueError:
            return date_str
    
    # Default validation functions
    def _validate_date(self, date_str: str) -> bool:
        """
        Validate date string.
        
        Args:
            date_str: Date string
            
        Returns:
            bool: True if valid date, False otherwise
        """
        # Try common date formats
        formats = [
            "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", 
            "%B %d, %Y", "%b %d, %Y", "%d %B %Y", "%d %b %Y"
        ]
        
        for fmt in formats:
            try:
                datetime.strptime(date_str, fmt)
                return True
            except ValueError:
                continue
        
        return False
    
    def _validate_email(self, email: str) -> bool:
        """
        Validate email address.
        
        Args:
            email: Email address
            
        Returns:
            bool: True if valid email, False otherwise
        """
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))
    
    def _validate_phone(self, phone: str) -> bool:
        """
        Validate phone number.
        
        Args:
            phone: Phone number
            
        Returns:
            bool: True if valid phone number, False otherwise
        """
        # Remove common separators
        clean_phone = re.sub(r'[\s\-\(\)\.]', '', phone)
        
        # Check if it's a valid phone number (at least 7 digits)
        return bool(re.match(r'^\+?[0-9]{7,15}$', clean_phone))
    
    # Default post-processing functions
    def _normalize_whitespace(self, text: str) -> str:
        """
        Normalize whitespace in text.
        
        Args:
            text: Input text
            
        Returns:
            str: Text with normalized whitespace
        """
        if not text:
            return text
        
        # Replace multiple whitespace with single space
        normalized = re.sub(r'\s+', ' ', text)
        
        # Trim whitespace
        return normalized.strip()
    
    def _capitalize_names(self, name: str) -> str:
        """
        Capitalize names properly.
        
        Args:
            name: Name to capitalize
            
        Returns:
            str: Properly capitalized name
        """
        if not name:
            return name
        
        # Split name into parts
        parts = name.split()
        
        # Capitalize each part
        capitalized_parts = []
        for part in parts:
            # Handle hyphenated names
            if '-' in part:
                hyphen_parts = part.split('-')
                capitalized_parts.append('-'.join(p.capitalize() for p in hyphen_parts))
            # Handle prefixes like "Mc" and "Mac"
            elif part.lower().startswith(('mc', 'mac')) and len(part) > 3:
                capitalized_parts.append(part[:3].capitalize() + part[3:].capitalize())
            else:
                capitalized_parts.append(part.capitalize())
        
        # Join parts back together
        return ' '.join(capitalized_parts)
    
    def _extract_numbers(self, text: str) -> List[str]:
        """
        Extract numbers from text.
        
        Args:
            text: Input text
            
        Returns:
            List[str]: List of extracted numbers
        """
        if not text:
            return []
        
        # Extract numbers using regex
        return re.findall(r'\b\d+(?:\.\d+)?\b', text)

"""
Null Filter for the Dudoxx Extraction system.

This module provides functionality to filter out null, N/A, and empty values
from extraction results.
"""

from typing import Dict, Any, List, Union, Optional


class DudoxxNullFilter:
    """
    Filters out null, N/A, and empty values from extraction results.
    
    This class provides methods to clean extraction results by removing fields
    with null, N/A, empty strings, or zero values, making the final output
    more concise and focused on meaningful data.
    """
    
    def __init__(self, 
                 remove_null: bool = True, 
                 remove_na: bool = True, 
                 remove_empty_strings: bool = True, 
                 remove_zeros: bool = False,
                 preserve_metadata: bool = False,
                 preserve_fields: Optional[List[str]] = None):
        """
        Initialize the null filter.
        
        Args:
            remove_null: Whether to remove null (None) values
            remove_na: Whether to remove "N/A" and similar values
            remove_empty_strings: Whether to remove empty strings
            remove_zeros: Whether to remove zero values (0, 0.0)
            preserve_metadata: Whether to preserve metadata fields (starting with "_")
                               Default is False to remove metadata and merged fields
            preserve_fields: List of field names to preserve even if they have null values
        """
        self.remove_null = remove_null
        self.remove_na = remove_na
        self.remove_empty_strings = remove_empty_strings
        self.remove_zeros = remove_zeros
        self.preserve_metadata = preserve_metadata
        self.preserve_fields = preserve_fields or []
        
        # Define NA values to filter out
        self.na_values = {"N/A", "n/a", "NA", "na", "N/a", "Not Available", "not available", 
                         "Not Applicable", "not applicable", "Unknown", "unknown"}
    
    def filter_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter out null, N/A, and empty values from extraction result.
        
        Args:
            result: Extraction result to filter
            
        Returns:
            Filtered extraction result
        """
        if not result:
            return {}
        
        filtered_result = {}
        
        for key, value in result.items():
            # Skip metadata fields if preserve_metadata is False
            if not self.preserve_metadata and key.startswith("_"):
                continue
                
            # Check if this is a metadata field that should be preserved
            if self.preserve_metadata and key.startswith("_"):
                filtered_result[key] = value
                continue
                
            # Check if this is a field that should be preserved regardless of value
            if key in self.preserve_fields:
                filtered_result[key] = value
                continue
            
            # Filter based on value type
            if isinstance(value, dict):
                # Recursively filter dictionary
                filtered_value = self.filter_result(value)
                if filtered_value or key in self.preserve_fields:
                    filtered_result[key] = filtered_value
            elif isinstance(value, list):
                # Filter list items
                filtered_value = self.filter_list(value)
                if filtered_value or key in self.preserve_fields:
                    filtered_result[key] = filtered_value
            elif not self._should_filter(value):
                # Keep value if it shouldn't be filtered
                filtered_result[key] = value
        
        return filtered_result
    
    def filter_list(self, items: List[Any]) -> List[Any]:
        """
        Filter out null, N/A, and empty values from a list.
        
        Args:
            items: List to filter
            
        Returns:
            Filtered list
        """
        if not items:
            return []
        
        filtered_items = []
        
        for item in items:
            if isinstance(item, dict):
                # Recursively filter dictionary
                filtered_item = self.filter_result(item)
                if filtered_item:  # Only add non-empty dictionaries
                    filtered_items.append(filtered_item)
            elif isinstance(item, list):
                # Recursively filter list
                filtered_item = self.filter_list(item)
                if filtered_item:  # Only add non-empty lists
                    filtered_items.append(filtered_item)
            elif not self._should_filter(item):
                # Keep item if it shouldn't be filtered
                filtered_items.append(item)
        
        return filtered_items
    
    def _should_filter(self, value: Any) -> bool:
        """
        Check if a value should be filtered out.
        
        Args:
            value: Value to check
            
        Returns:
            True if the value should be filtered out, False otherwise
        """
        # Check for null values
        if self.remove_null and value is None:
            return True
        
        # Check for N/A values
        if self.remove_na and isinstance(value, str) and value.strip() in self.na_values:
            return True
        
        # Check for empty strings
        if self.remove_empty_strings and isinstance(value, str) and not value.strip():
            return True
        
        # Check for zero values
        if self.remove_zeros and (value == 0 or value == 0.0):
            return True
        
        return False


def filter_extraction_result(
    result: Dict[str, Any],
    remove_null: bool = True,
    remove_na: bool = True,
    remove_empty_strings: bool = True,
    remove_zeros: bool = False,
    preserve_metadata: bool = False,
    preserve_fields: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Filter out null, N/A, and empty values from extraction result.
    
    This is a convenience function that creates a DudoxxNullFilter and applies it
    to the given extraction result.
    
    Args:
        result: Extraction result to filter
        remove_null: Whether to remove null (None) values
        remove_na: Whether to remove "N/A" and similar values
        remove_empty_strings: Whether to remove empty strings
        remove_zeros: Whether to remove zero values (0, 0.0)
        preserve_metadata: Whether to preserve metadata fields (starting with "_")
                           Default is False to remove metadata and merged fields
        preserve_fields: List of field names to preserve even if they have null values
        
    Returns:
        Filtered extraction result
    """
    null_filter = DudoxxNullFilter(
        remove_null=remove_null,
        remove_na=remove_na,
        remove_empty_strings=remove_empty_strings,
        remove_zeros=remove_zeros,
        preserve_metadata=preserve_metadata,
        preserve_fields=preserve_fields
    )
    
    return null_filter.filter_result(result)

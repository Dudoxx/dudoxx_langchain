"""
Test script for the DudoxxNullFilter component.

This script tests the DudoxxNullFilter component to ensure it correctly filters out
null, N/A, and empty values from extraction results.
"""

import json
from dudoxx_extraction.null_filter import DudoxxNullFilter, filter_extraction_result

def test_null_filter():
    """Test the DudoxxNullFilter component."""
    # Create a sample extraction result with null, N/A, and empty values
    sample_result = {
        "patient_name": "John Doe",
        "date_of_birth": None,
        "gender": "Male",
        "medical_record_number": "N/A",
        "allergies": ["Penicillin", None, "Peanuts"],
        "chronic_conditions": [],
        "medications": [
            {"name": "Aspirin", "dosage": "100mg", "frequency": "daily"},
            {"name": "Ibuprofen", "dosage": None, "frequency": "as needed"}
        ],
        "visits": [
            {"date": "2023-01-15", "provider": "Dr. Smith", "complaint": "Headache"},
            {"date": "2023-02-20", "provider": "", "complaint": "Fever"}
        ],
        "lab_results": None,
        "_metadata": {
            "source_chunks": {"patient_name": [0]},
            "confidence": {"patient_name": [1.0]}
        }
    }
    
    # Create a null filter
    null_filter = DudoxxNullFilter(
        remove_null=True,
        remove_na=True,
        remove_empty_strings=True,
        remove_zeros=False,
        preserve_metadata=True  # Explicitly set to True for testing metadata preservation
    )
    
    # Apply the null filter
    filtered_result = null_filter.filter_result(sample_result)
    
    # Print the original and filtered results
    print("Original Result:")
    print(json.dumps(sample_result, indent=2))
    print("\nFiltered Result:")
    print(json.dumps(filtered_result, indent=2))
    
    # Verify that null values are removed
    assert "date_of_birth" not in filtered_result
    assert "lab_results" not in filtered_result
    
    # Verify that N/A values are removed
    assert "medical_record_number" not in filtered_result
    
    # Verify that empty strings are removed
    assert "provider" not in filtered_result["visits"][1]  # Empty provider should be removed
    
    # Verify that null values in lists are removed
    assert None not in filtered_result["allergies"]
    
    # Verify that null values in dictionaries are removed
    assert "dosage" not in filtered_result["medications"][1]
    
    # Verify that metadata is preserved
    assert "_metadata" in filtered_result
    
    print("\nAll tests passed!")

if __name__ == "__main__":
    test_null_filter()

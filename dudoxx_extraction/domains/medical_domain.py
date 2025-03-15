"""
Medical domain definitions for the Dudoxx Extraction system.

This module provides domain definitions for medical documents, broken down
into smaller sub-domains for more focused extraction.
"""

from dudoxx_extraction.domains.domain_definition import DomainDefinition, SubDomainDefinition, FieldDefinition, ValidationLevel
from dudoxx_extraction.domains.domain_registry import DomainRegistry


# Patient Information Sub-Domain
patient_info_subdomain = SubDomainDefinition(
    name="patient_info",
    description="patient information",
    extraction_instructions="Look for patient information typically at the top or header section of medical documents. Pay attention to demographic details.",
    priority=10,
    fields=[
        FieldDefinition(
            name="patient_name",
            description="Full name of the patient",
            type="string",
            is_required=True,
            is_unique=True,
            examples=["John Smith", "Jane Doe"],
            extraction_instructions="Look for the patient's name near labels like 'Patient:', 'Name:', 'Patient Name:'. Include both first and last name.",
            formatting_instructions="Format as 'Last, First Middle' if all parts are available.",
            keywords=["patient", "name", "pt", "pt name"],
            extraction_priority=10,
            confidence_threshold=0.7,
            validation_rules=["Must contain at least two words", "Should not contain numbers"],
            format_function="capitalize_names"
        ),
        FieldDefinition(
            name="date_of_birth",
            description="Patient's date of birth",
            type="date",
            is_required=True,
            is_unique=True,
            examples=["05/15/1980", "1980-05-15", "May 15, 1980"],
            extraction_instructions="Look for date of birth near labels like 'DOB:', 'Birth Date:', 'Date of Birth:'.",
            formatting_instructions="Format as YYYY-MM-DD.",
            format_pattern=r"^\d{4}-\d{2}-\d{2}$",
            format_function="format_date_iso",
            keywords=["birth", "dob", "born", "birthday"],
            extraction_priority=9,
            validation_rules=["Must be a valid date", "Year should be between 1900 and current year"],
            validation_function="validate_date"
        ),
        FieldDefinition(
            name="gender",
            description="Patient's gender",
            type="string",
            is_required=False,
            is_unique=True,
            examples=["Male", "Female", "Non-binary"],
            extraction_instructions="Look for gender information near labels like 'Gender:', 'Sex:'.",
            keywords=["gender", "sex", "male", "female"],
            extraction_priority=8
        ),
        FieldDefinition(
            name="medical_record_number",
            description="Medical record number",
            type="string",
            is_required=False,
            is_unique=True,
            examples=["MRN-12345678", "12345678"],
            extraction_instructions="Look for medical record number near labels like 'MRN:', 'Medical Record Number:', 'Record #:'.",
            keywords=["mrn", "medical record", "record number", "chart number"],
            extraction_priority=7,
            format_pattern=r"^(?:MRN-)?[0-9A-Z]{6,12}$"
        )
    ]
)

# Medical History Sub-Domain
medical_history_subdomain = SubDomainDefinition(
    name="medical_history",
    description="medical history",
    extraction_instructions="Look for medical history in sections labeled 'Medical History', 'Past Medical History', or 'History'.",
    priority=8,
    fields=[
        FieldDefinition(
            name="allergies",
            description="List of patient allergies",
            type="list",
            is_required=False,
            is_unique=False,
            examples=["Penicillin", "Peanuts", "Latex"],
            extraction_instructions="Look for allergies in sections labeled 'Allergies', 'Drug Allergies', or 'Allergy List'.",
            keywords=["allergy", "allergic", "allergies", "reaction"],
            negative_keywords=["no known allergies", "nka", "none"],
            extraction_priority=6
        ),
        FieldDefinition(
            name="chronic_conditions",
            description="List of chronic conditions with diagnosis dates",
            type="list",
            is_required=False,
            is_unique=False,
            examples=["Type 2 Diabetes (diagnosed 2015)", "Hypertension (diagnosed 2018)"],
            extraction_instructions="Look for chronic conditions in sections labeled 'Chronic Conditions', 'Ongoing Conditions', or within the medical history.",
            keywords=["chronic", "condition", "ongoing", "history of", "diagnosed with"],
            extraction_priority=5
        ),
        FieldDefinition(
            name="previous_surgeries",
            description="List of previous surgeries with dates",
            type="list",
            is_required=False,
            is_unique=False,
            examples=["Appendectomy (2010)", "Knee Arthroscopy (2019)"],
            extraction_instructions="Look for surgeries in sections labeled 'Surgical History', 'Past Surgeries', or 'Procedures'.",
            keywords=["surgery", "surgical", "procedure", "operation"],
            extraction_priority=4
        ),
        FieldDefinition(
            name="family_history",
            description="Family medical history",
            type="list",
            is_required=False,
            is_unique=False,
            examples=["Father - Heart Disease", "Mother - Breast Cancer"],
            extraction_instructions="Look for family history in sections labeled 'Family History' or 'Family Medical History'.",
            keywords=["family", "father", "mother", "brother", "sister", "parent", "sibling"],
            extraction_priority=3
        )
    ]
)

# Medications Sub-Domain
medications_subdomain = SubDomainDefinition(
    name="medications",
    description="current medications",
    extraction_instructions="Look for medications in sections labeled 'Medications', 'Current Medications', or 'Prescriptions'.",
    priority=7,
    fields=[
        FieldDefinition(
            name="medications",
            description="List of current medications with dosage and frequency",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                "Metformin 500mg, twice daily (for diabetes)",
                "Lisinopril 10mg, once daily (for hypertension)"
            ],
            extraction_instructions="Extract medication name, dosage, frequency, and purpose if available.",
            keywords=["medication", "drug", "prescription", "dose", "mg", "mcg", "daily"],
            extraction_priority=9
        )
    ]
)

# Visits Sub-Domain
visits_subdomain = SubDomainDefinition(
    name="visits",
    description="medical visits",
    extraction_instructions="Look for visit information in sections labeled 'Encounters', 'Visits', or 'Appointments'.",
    priority=6,
    fields=[
        FieldDefinition(
            name="visits",
            description="List of medical visits with dates, providers, complaints, and plans",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                {
                    "date": "03/10/2023",
                    "provider": "Dr. Sarah Johnson",
                    "complaint": "Persistent cough and fever",
                    "assessment": "Upper respiratory infection, likely viral",
                    "plan": "Rest, increased fluids, over-the-counter cough suppressant",
                    "follow_up": "As needed if symptoms worsen"
                }
            ],
            extraction_instructions="Extract visit date, provider name, chief complaint, assessment/diagnosis, treatment plan, and follow-up instructions.",
            keywords=["visit", "encounter", "appointment", "seen by", "follow-up"],
            extraction_priority=2
        )
    ]
)

# Diagnoses Sub-Domain
diagnoses_subdomain = SubDomainDefinition(
    name="diagnoses",
    description="diagnoses",
    extraction_instructions="Look for diagnoses in sections labeled 'Diagnoses', 'Assessment', 'Impression', or 'Problem List'.",
    priority=9,
    fields=[
        FieldDefinition(
            name="diagnoses",
            description="List of diagnoses",
            type="list",
            is_required=False,
            is_unique=False,
            examples=["Diabetes mellitus Type II", "Hypertension", "Upper respiratory infection"],
            extraction_instructions="Extract all diagnoses mentioned, including primary and secondary diagnoses.",
            keywords=["diagnosis", "diagnosed with", "assessment", "impression", "problem"],
            extraction_priority=8
        )
    ]
)

# Lab Results Sub-Domain
lab_results_subdomain = SubDomainDefinition(
    name="lab_results",
    description="laboratory results",
    extraction_instructions="Look for lab results in sections labeled 'Laboratory Results', 'Lab Tests', or 'Diagnostic Tests'.",
    priority=5,
    fields=[
        FieldDefinition(
            name="lab_results",
            description="List of laboratory results with dates and values",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                {
                    "date": "07/22/2023",
                    "test": "HbA1c",
                    "value": "7.1%",
                    "reference": "4.0-5.6%",
                    "interpretation": "Elevated"
                }
            ],
            extraction_instructions="Extract test name, date performed, result value, reference range, and interpretation if available.",
            keywords=["lab", "test", "result", "value", "normal range", "reference"],
            extraction_priority=1
        )
    ]
)

# Create the Medical Domain
medical_domain = DomainDefinition(
    name="medical",
    description="Medical domain for healthcare documents",
    extraction_instructions="This is a medical document. Pay special attention to patient demographics, diagnoses, and treatments.",
    keywords=["patient", "diagnosis", "treatment", "medical", "hospital", "clinic", "doctor"],
    confidence_threshold=0.6,
    sub_domains=[
        patient_info_subdomain,
        medical_history_subdomain,
        medications_subdomain,
        visits_subdomain,
        diagnoses_subdomain,
        lab_results_subdomain
    ]
)

# Register the domain
def register_medical_domain():
    """Register the medical domain with the domain registry."""
    registry = DomainRegistry()
    registry.register_domain(medical_domain)

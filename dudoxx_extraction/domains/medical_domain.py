"""
Medical domain definitions for the Dudoxx Extraction system.

This module provides domain definitions for medical documents, broken down
into smaller sub-domains for more focused extraction.
"""

from dudoxx_extraction.domains.domain_definition import DomainDefinition, SubDomainDefinition, FieldDefinition
from dudoxx_extraction.domains.domain_registry import DomainRegistry


# Patient Information Sub-Domain
patient_info_subdomain = SubDomainDefinition(
    name="patient_info",
    description="patient information",
    fields=[
        FieldDefinition(
            name="patient_name",
            description="Full name of the patient",
            type="string",
            is_required=True,
            is_unique=True,
            examples=["John Smith", "Jane Doe"]
        ),
        FieldDefinition(
            name="date_of_birth",
            description="Patient's date of birth",
            type="date",
            is_required=True,
            is_unique=True,
            examples=["05/15/1980", "1980-05-15", "May 15, 1980"]
        ),
        FieldDefinition(
            name="gender",
            description="Patient's gender",
            type="string",
            is_required=False,
            is_unique=True,
            examples=["Male", "Female", "Non-binary"]
        ),
        FieldDefinition(
            name="medical_record_number",
            description="Medical record number",
            type="string",
            is_required=False,
            is_unique=True,
            examples=["MRN-12345678", "12345678"]
        )
    ]
)

# Medical History Sub-Domain
medical_history_subdomain = SubDomainDefinition(
    name="medical_history",
    description="medical history",
    fields=[
        FieldDefinition(
            name="allergies",
            description="List of patient allergies",
            type="list",
            is_required=False,
            is_unique=False,
            examples=["Penicillin", "Peanuts", "Latex"]
        ),
        FieldDefinition(
            name="chronic_conditions",
            description="List of chronic conditions with diagnosis dates",
            type="list",
            is_required=False,
            is_unique=False,
            examples=["Type 2 Diabetes (diagnosed 2015)", "Hypertension (diagnosed 2018)"]
        ),
        FieldDefinition(
            name="previous_surgeries",
            description="List of previous surgeries with dates",
            type="list",
            is_required=False,
            is_unique=False,
            examples=["Appendectomy (2010)", "Knee Arthroscopy (2019)"]
        ),
        FieldDefinition(
            name="family_history",
            description="Family medical history",
            type="list",
            is_required=False,
            is_unique=False,
            examples=["Father - Heart Disease", "Mother - Breast Cancer"]
        )
    ]
)

# Medications Sub-Domain
medications_subdomain = SubDomainDefinition(
    name="medications",
    description="current medications",
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
            ]
        )
    ]
)

# Visits Sub-Domain
visits_subdomain = SubDomainDefinition(
    name="visits",
    description="medical visits",
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
            ]
        )
    ]
)

# Diagnoses Sub-Domain
diagnoses_subdomain = SubDomainDefinition(
    name="diagnoses",
    description="diagnoses",
    fields=[
        FieldDefinition(
            name="diagnoses",
            description="List of diagnoses",
            type="list",
            is_required=False,
            is_unique=False,
            examples=["Diabetes mellitus Type II", "Hypertension", "Upper respiratory infection"]
        )
    ]
)

# Lab Results Sub-Domain
lab_results_subdomain = SubDomainDefinition(
    name="lab_results",
    description="laboratory results",
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
            ]
        )
    ]
)

# Create the Medical Domain
medical_domain = DomainDefinition(
    name="medical",
    description="Medical domain for healthcare documents",
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

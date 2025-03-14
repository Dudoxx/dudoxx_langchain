"""
Demographic domain definitions for the Dudoxx Extraction system.

This module provides domain definitions for demographic information including
persons, professionals, organizations, identification documents, and locations.
"""

from dudoxx_extraction.domains.domain_definition import DomainDefinition, SubDomainDefinition, FieldDefinition
from dudoxx_extraction.domains.domain_registry import DomainRegistry


# Person Information Sub-Domain
person_info_subdomain = SubDomainDefinition(
    name="person_info",
    description="personal demographic information",
    fields=[
        FieldDefinition(
            name="full_name",
            description="Full name of the person",
            type="string",
            is_required=True,
            is_unique=True,
            examples=["John Smith", "Jane Doe", "María García López"]
        ),
        FieldDefinition(
            name="date_of_birth",
            description="Person's date of birth",
            type="date",
            is_required=False,
            is_unique=True,
            examples=["05/15/1980", "1980-05-15", "May 15, 1980"]
        ),
        FieldDefinition(
            name="age",
            description="Person's age in years",
            type="number",
            is_required=False,
            is_unique=True,
            examples=["42", "35", "67"]
        ),
        FieldDefinition(
            name="gender",
            description="Person's gender",
            type="string",
            is_required=False,
            is_unique=True,
            examples=["Male", "Female", "Non-binary"]
        ),
        FieldDefinition(
            name="marital_status",
            description="Person's marital status",
            type="string",
            is_required=False,
            is_unique=True,
            examples=["Single", "Married", "Divorced", "Widowed"]
        ),
        FieldDefinition(
            name="nationality",
            description="Person's nationality or citizenship",
            type="string",
            is_required=False,
            is_unique=False,
            examples=["American", "French", "Japanese", "Dual citizenship: Canadian and British"]
        ),
        FieldDefinition(
            name="languages",
            description="Languages spoken by the person",
            type="list",
            is_required=False,
            is_unique=False,
            examples=["English (native)", "Spanish (fluent)", "French (basic)"]
        ),
        FieldDefinition(
            name="ethnicity",
            description="Person's ethnicity or race",
            type="string",
            is_required=False,
            is_unique=False,
            examples=["Caucasian", "African American", "Hispanic/Latino", "Asian", "Mixed"]
        ),
        FieldDefinition(
            name="religion",
            description="Person's religious affiliation",
            type="string",
            is_required=False,
            is_unique=False,
            examples=["Christian", "Muslim", "Jewish", "Hindu", "Buddhist", "None/Atheist"]
        ),
        FieldDefinition(
            name="occupation",
            description="Person's job or profession",
            type="string",
            is_required=False,
            is_unique=False,
            examples=["Software Engineer", "Teacher", "Physician", "Retired"]
        ),
        FieldDefinition(
            name="education",
            description="Person's educational background",
            type="string",
            is_required=False,
            is_unique=False,
            examples=["Bachelor's Degree in Computer Science", "Master's in Education", "High School Diploma"]
        )
    ]
)

# Contact Information Sub-Domain
contact_info_subdomain = SubDomainDefinition(
    name="contact_info",
    description="contact information",
    fields=[
        FieldDefinition(
            name="address",
            description="Physical address",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "street": "123 Main Street",
                    "city": "Anytown",
                    "state": "CA",
                    "postal_code": "12345",
                    "country": "USA"
                }
            ]
        ),
        FieldDefinition(
            name="phone_numbers",
            description="List of phone numbers with types",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                {"type": "Mobile", "number": "+1 (555) 123-4567"},
                {"type": "Home", "number": "+1 (555) 987-6543"},
                {"type": "Work", "number": "+1 (555) 456-7890"}
            ]
        ),
        FieldDefinition(
            name="email_addresses",
            description="List of email addresses with types",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                {"type": "Personal", "email": "john.smith@email.com"},
                {"type": "Work", "email": "jsmith@company.com"}
            ]
        ),
        FieldDefinition(
            name="social_media",
            description="List of social media profiles",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                {"platform": "LinkedIn", "username": "johnsmith"},
                {"platform": "Twitter", "username": "@jsmith"}
            ]
        ),
        FieldDefinition(
            name="emergency_contact",
            description="Emergency contact information",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "name": "Jane Smith",
                    "relationship": "Wife",
                    "phone": "+1 (555) 987-6543"
                }
            ]
        )
    ]
)

# Identification Documents Sub-Domain
identification_documents_subdomain = SubDomainDefinition(
    name="identification_documents",
    description="identification documents information",
    fields=[
        FieldDefinition(
            name="social_security_number",
            description="Social Security Number (SSN) or equivalent",
            type="string",
            is_required=False,
            is_unique=True,
            examples=["123-45-6789", "123456789"]
        ),
        FieldDefinition(
            name="national_id",
            description="National ID card information",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "country": "USA",
                    "type": "Driver's License",
                    "number": "DL1234567",
                    "issuing_state": "California",
                    "issue_date": "2020-05-15",
                    "expiration_date": "2028-05-15"
                }
            ]
        ),
        FieldDefinition(
            name="passport",
            description="Passport information",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "country": "USA",
                    "number": "123456789",
                    "issue_date": "2018-03-10",
                    "expiration_date": "2028-03-09",
                    "issuing_authority": "U.S. Department of State"
                }
            ]
        ),
        FieldDefinition(
            name="residency_permit",
            description="Residency permit or visa information",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "country": "France",
                    "type": "Long-stay visa",
                    "number": "FR1234567890",
                    "issue_date": "2022-01-15",
                    "expiration_date": "2023-01-14",
                    "status": "Valid"
                }
            ]
        ),
        FieldDefinition(
            name="health_insurance",
            description="Health insurance information",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "provider": "Blue Cross Blue Shield",
                    "policy_number": "XYZ123456789",
                    "group_number": "GRP-123456",
                    "coverage_type": "Family",
                    "effective_date": "2022-01-01"
                }
            ]
        ),
        FieldDefinition(
            name="tax_identification",
            description="Tax identification number",
            type="string",
            is_required=False,
            is_unique=True,
            examples=["123-45-6789", "AB123456C"]
        )
    ]
)

# Professional Information Sub-Domain
professional_info_subdomain = SubDomainDefinition(
    name="professional_info",
    description="professional information",
    fields=[
        FieldDefinition(
            name="profession",
            description="Professional title or role",
            type="string",
            is_required=False,
            is_unique=True,
            examples=["Medical Doctor", "Attorney", "Certified Public Accountant"]
        ),
        FieldDefinition(
            name="specialization",
            description="Area of specialization within profession",
            type="string",
            is_required=False,
            is_unique=True,
            examples=["Cardiology", "Corporate Law", "Tax Accounting"]
        ),
        FieldDefinition(
            name="licenses",
            description="Professional licenses and certifications",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                {
                    "type": "Medical License",
                    "number": "MD12345",
                    "issuing_authority": "California Medical Board",
                    "issue_date": "2010-06-15",
                    "expiration_date": "2024-06-14"
                },
                {
                    "type": "Board Certification",
                    "specialty": "Cardiology",
                    "issuing_authority": "American Board of Internal Medicine",
                    "issue_date": "2012-09-20",
                    "expiration_date": "2022-09-19"
                }
            ]
        ),
        FieldDefinition(
            name="education",
            description="Professional education and training",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                {
                    "degree": "Doctor of Medicine (MD)",
                    "institution": "Stanford University School of Medicine",
                    "location": "Stanford, CA",
                    "graduation_date": "2005"
                },
                {
                    "type": "Residency",
                    "specialty": "Internal Medicine",
                    "institution": "UCSF Medical Center",
                    "location": "San Francisco, CA",
                    "completion_date": "2008"
                },
                {
                    "type": "Fellowship",
                    "specialty": "Cardiology",
                    "institution": "Mayo Clinic",
                    "location": "Rochester, MN",
                    "completion_date": "2011"
                }
            ]
        ),
        FieldDefinition(
            name="professional_affiliations",
            description="Professional organizations and affiliations",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                "American Medical Association",
                "American College of Cardiology",
                "California Medical Association"
            ]
        ),
        FieldDefinition(
            name="practice_details",
            description="Details about professional practice",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "practice_name": "Bay Area Cardiology Associates",
                    "role": "Partner",
                    "start_date": "2012-01-15",
                    "hospital_affiliations": ["Stanford Hospital", "UCSF Medical Center"]
                }
            ]
        )
    ]
)

# Organization Information Sub-Domain
organization_info_subdomain = SubDomainDefinition(
    name="organization_info",
    description="organization information",
    fields=[
        FieldDefinition(
            name="organization_name",
            description="Name of the organization",
            type="string",
            is_required=True,
            is_unique=True,
            examples=["Bay Area Medical Center", "Smith & Jones Law Firm", "Acme Corporation"]
        ),
        FieldDefinition(
            name="organization_type",
            description="Type of organization",
            type="string",
            is_required=False,
            is_unique=True,
            examples=["Hospital", "Medical Clinic", "Law Firm", "Corporation", "Non-profit"]
        ),
        FieldDefinition(
            name="industry",
            description="Industry or sector",
            type="string",
            is_required=False,
            is_unique=True,
            examples=["Healthcare", "Legal Services", "Education", "Technology"]
        ),
        FieldDefinition(
            name="registration_info",
            description="Legal registration information",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "registration_number": "12345-ABC",
                    "tax_id": "12-3456789",
                    "registration_date": "2000-03-15",
                    "legal_structure": "Limited Liability Company"
                }
            ]
        ),
        FieldDefinition(
            name="address",
            description="Physical address of the organization",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "street": "123 Medical Center Drive",
                    "city": "San Francisco",
                    "state": "CA",
                    "postal_code": "94123",
                    "country": "USA"
                }
            ]
        ),
        FieldDefinition(
            name="contact_info",
            description="Contact information for the organization",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "phone": "+1 (555) 123-4567",
                    "fax": "+1 (555) 987-6543",
                    "email": "info@bayareamedical.org",
                    "website": "www.bayareamedical.org"
                }
            ]
        ),
        FieldDefinition(
            name="operating_hours",
            description="Operating hours of the organization",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "monday_to_friday": "8:00 AM - 6:00 PM",
                    "saturday": "9:00 AM - 1:00 PM",
                    "sunday": "Closed",
                    "holidays": "Closed"
                }
            ]
        ),
        FieldDefinition(
            name="departments",
            description="Departments or divisions within the organization",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                {
                    "name": "Cardiology Department",
                    "head": "Dr. Jane Smith",
                    "contact": "+1 (555) 123-4567 ext. 101"
                },
                {
                    "name": "Orthopedics Department",
                    "head": "Dr. John Johnson",
                    "contact": "+1 (555) 123-4567 ext. 102"
                }
            ]
        ),
        FieldDefinition(
            name="accreditations",
            description="Accreditations and certifications",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                {
                    "accreditation": "Joint Commission Accreditation",
                    "issue_date": "2020-05-15",
                    "expiration_date": "2023-05-14"
                },
                {
                    "accreditation": "College of American Pathologists (CAP) Accreditation",
                    "issue_date": "2021-10-20",
                    "expiration_date": "2024-10-19"
                }
            ]
        )
    ]
)

# Location Information Sub-Domain
location_info_subdomain = SubDomainDefinition(
    name="location_info",
    description="location information",
    fields=[
        FieldDefinition(
            name="country",
            description="Country information",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "name": "United States of America",
                    "code": "USA",
                    "iso_code": "US",
                    "region": "North America",
                    "capital": "Washington, D.C."
                }
            ]
        ),
        FieldDefinition(
            name="administrative_divisions",
            description="Administrative divisions (states, provinces, etc.)",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                {
                    "name": "California",
                    "type": "State",
                    "code": "CA",
                    "country": "USA",
                    "capital": "Sacramento"
                },
                {
                    "name": "Ontario",
                    "type": "Province",
                    "code": "ON",
                    "country": "Canada",
                    "capital": "Toronto"
                }
            ]
        ),
        FieldDefinition(
            name="city",
            description="City or municipality information",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "name": "San Francisco",
                    "state": "California",
                    "country": "USA",
                    "population": "approximately 875,000"
                }
            ]
        ),
        FieldDefinition(
            name="gps_coordinates",
            description="GPS coordinates",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "latitude": "37.7749° N",
                    "longitude": "122.4194° W"
                }
            ]
        ),
        FieldDefinition(
            name="postal_code",
            description="Postal or ZIP code",
            type="string",
            is_required=False,
            is_unique=True,
            examples=["94123", "SW1A 1AA", "75001"]
        ),
        FieldDefinition(
            name="timezone",
            description="Timezone information",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "name": "Pacific Standard Time",
                    "abbreviation": "PST",
                    "utc_offset": "UTC-8:00",
                    "daylight_saving": "Observes DST"
                }
            ]
        )
    ]
)

# Laboratory Information Sub-Domain
laboratory_info_subdomain = SubDomainDefinition(
    name="laboratory_info",
    description="laboratory information",
    fields=[
        FieldDefinition(
            name="laboratory_name",
            description="Name of the laboratory",
            type="string",
            is_required=True,
            is_unique=True,
            examples=["Bay Area Clinical Laboratory", "Quest Diagnostics", "LabCorp"]
        ),
        FieldDefinition(
            name="laboratory_type",
            description="Type of laboratory",
            type="string",
            is_required=False,
            is_unique=True,
            examples=["Clinical", "Pathology", "Research", "Molecular Diagnostics"]
        ),
        FieldDefinition(
            name="accreditations",
            description="Laboratory accreditations and certifications",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                {
                    "accreditation": "College of American Pathologists (CAP)",
                    "number": "12345-01",
                    "issue_date": "2020-05-15",
                    "expiration_date": "2022-05-14"
                },
                {
                    "accreditation": "Clinical Laboratory Improvement Amendments (CLIA)",
                    "number": "10D0123456",
                    "issue_date": "2019-10-20",
                    "expiration_date": "2021-10-19"
                }
            ]
        ),
        FieldDefinition(
            name="contact_info",
            description="Contact information for the laboratory",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "address": "123 Lab Drive, San Francisco, CA 94123",
                    "phone": "+1 (555) 123-4567",
                    "fax": "+1 (555) 987-6543",
                    "email": "info@bayarealab.com",
                    "website": "www.bayarealab.com"
                }
            ]
        ),
        FieldDefinition(
            name="operating_hours",
            description="Operating hours of the laboratory",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "monday_to_friday": "7:00 AM - 7:00 PM",
                    "saturday": "8:00 AM - 3:00 PM",
                    "sunday": "Closed",
                    "specimen_collection_hours": "7:00 AM - 5:00 PM (M-F)"
                }
            ]
        ),
        FieldDefinition(
            name="services",
            description="Services offered by the laboratory",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                "Clinical Chemistry",
                "Hematology",
                "Microbiology",
                "Immunology",
                "Molecular Diagnostics",
                "Toxicology"
            ]
        ),
        FieldDefinition(
            name="staff",
            description="Key laboratory staff",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                {
                    "name": "Dr. Jane Smith",
                    "title": "Laboratory Director",
                    "credentials": "MD, PhD, FCAP",
                    "contact": "jsmith@bayarealab.com"
                },
                {
                    "name": "Dr. John Johnson",
                    "title": "Chief Pathologist",
                    "credentials": "MD, FCAP",
                    "contact": "jjohnson@bayarealab.com"
                }
            ]
        )
    ]
)

# Laboratory Results Sub-Domain
laboratory_results_subdomain = SubDomainDefinition(
    name="laboratory_results",
    description="laboratory test results",
    fields=[
        FieldDefinition(
            name="patient_info",
            description="Patient information for the laboratory results",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "name": "John Smith",
                    "date_of_birth": "1980-05-15",
                    "medical_record_number": "MRN-12345678",
                    "ordering_provider": "Dr. Sarah Johnson"
                }
            ]
        ),
        FieldDefinition(
            name="specimen_info",
            description="Information about the specimen",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "specimen_type": "Blood",
                    "collection_date": "2023-03-10",
                    "collection_time": "08:15 AM",
                    "received_date": "2023-03-10",
                    "received_time": "10:30 AM",
                    "specimen_id": "SP-987654321"
                }
            ]
        ),
        FieldDefinition(
            name="test_results",
            description="Laboratory test results",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                {
                    "test_name": "Complete Blood Count (CBC)",
                    "test_code": "CBC",
                    "result_date": "2023-03-10",
                    "components": [
                        {
                            "component": "White Blood Cell Count (WBC)",
                            "result": "7.5",
                            "units": "x10^3/µL",
                            "reference_range": "4.0-11.0",
                            "flag": "Normal"
                        },
                        {
                            "component": "Red Blood Cell Count (RBC)",
                            "result": "5.2",
                            "units": "x10^6/µL",
                            "reference_range": "4.5-5.9",
                            "flag": "Normal"
                        },
                        {
                            "component": "Hemoglobin (Hgb)",
                            "result": "15.1",
                            "units": "g/dL",
                            "reference_range": "13.5-17.5",
                            "flag": "Normal"
                        },
                        {
                            "component": "Hematocrit (Hct)",
                            "result": "45",
                            "units": "%",
                            "reference_range": "41-53",
                            "flag": "Normal"
                        },
                        {
                            "component": "Platelet Count",
                            "result": "250",
                            "units": "x10^3/µL",
                            "reference_range": "150-450",
                            "flag": "Normal"
                        }
                    ]
                },
                {
                    "test_name": "Comprehensive Metabolic Panel (CMP)",
                    "test_code": "CMP",
                    "result_date": "2023-03-10",
                    "components": [
                        {
                            "component": "Glucose",
                            "result": "95",
                            "units": "mg/dL",
                            "reference_range": "70-99",
                            "flag": "Normal"
                        },
                        {
                            "component": "Blood Urea Nitrogen (BUN)",
                            "result": "15",
                            "units": "mg/dL",
                            "reference_range": "7-20",
                            "flag": "Normal"
                        },
                        {
                            "component": "Creatinine",
                            "result": "0.9",
                            "units": "mg/dL",
                            "reference_range": "0.6-1.2",
                            "flag": "Normal"
                        },
                        {
                            "component": "Sodium",
                            "result": "140",
                            "units": "mmol/L",
                            "reference_range": "136-145",
                            "flag": "Normal"
                        },
                        {
                            "component": "Potassium",
                            "result": "4.0",
                            "units": "mmol/L",
                            "reference_range": "3.5-5.1",
                            "flag": "Normal"
                        }
                    ]
                }
            ]
        ),
        FieldDefinition(
            name="interpretation",
            description="Clinical interpretation of the results",
            type="string",
            is_required=False,
            is_unique=True,
            examples=[
                "All results are within normal limits. No significant abnormalities detected.",
                "Elevated liver enzymes suggest possible hepatic dysfunction. Clinical correlation recommended."
            ]
        ),
        FieldDefinition(
            name="laboratory_info",
            description="Information about the laboratory that performed the tests",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "name": "Bay Area Clinical Laboratory",
                    "address": "123 Lab Drive, San Francisco, CA 94123",
                    "phone": "+1 (555) 123-4567",
                    "clia_number": "10D0123456",
                    "director": "Dr. Jane Smith, MD, PhD, FCAP"
                }
            ]
        )
    ]
)

# Create the Demographic Domain
demographic_domain = DomainDefinition(
    name="demographic",
    description="Demographic domain for personal and organizational information",
    sub_domains=[
        person_info_subdomain,
        contact_info_subdomain,
        identification_documents_subdomain,
        professional_info_subdomain,
        organization_info_subdomain,
        location_info_subdomain,
        laboratory_info_subdomain,
        laboratory_results_subdomain
    ]
)

# Register the domain
def register_demographic_domain():
    """Register the demographic domain with the domain registry."""
    registry = DomainRegistry()
    registry.register_domain(demographic_domain)

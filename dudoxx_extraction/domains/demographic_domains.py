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
    extraction_instructions="Look for personal information typically at the beginning of documents or in dedicated sections about the individual.",
    priority=10,
    fields=[
        FieldDefinition(
            name="full_name",
            description="Full name of the person",
            type="string",
            is_required=True,
            is_unique=True,
            examples=["John Smith", "Jane Doe", "María García López"],
            extraction_instructions="Extract the person's full name as it appears in the document.",
            extraction_priority=10,
            keywords=["name", "full name", "person", "individual"]
        ),
        FieldDefinition(
            name="date_of_birth",
            description="Person's date of birth",
            type="date",
            is_required=False,
            is_unique=True,
            examples=["05/15/1980", "1980-05-15", "May 15, 1980"],
            extraction_instructions="Extract the person's date of birth in the format provided in the document.",
            formatting_instructions="Format as YYYY-MM-DD when possible.",
            extraction_priority=9,
            keywords=["birth", "dob", "born", "birthday", "date of birth"]
        ),
        FieldDefinition(
            name="gender",
            description="Person's gender",
            type="string",
            is_required=False,
            is_unique=True,
            examples=["Male", "Female", "Non-binary"],
            extraction_instructions="Extract the person's gender as stated in the document.",
            extraction_priority=8,
            keywords=["gender", "sex", "male", "female"]
        )
    ]
)

# Contact Information Sub-Domain
contact_info_subdomain = SubDomainDefinition(
    name="contact_info",
    description="contact information",
    extraction_instructions="Look for contact information in dedicated contact sections or near personal information.",
    priority=9,
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
            ],
            extraction_instructions="Extract the complete address with all components as provided in the document.",
            extraction_priority=10,
            keywords=["address", "street", "city", "state", "zip", "postal", "residence", "location"]
        ),
        FieldDefinition(
            name="phone_numbers",
            description="List of phone numbers with types",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                {"type": "Mobile", "number": "+1 (555) 123-4567"},
                {"type": "Home", "number": "+1 (555) 987-6543"}
            ],
            extraction_instructions="Extract all phone numbers with their types as provided in the document.",
            extraction_priority=9,
            keywords=["phone", "telephone", "mobile", "cell", "contact number", "call"]
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
            ],
            extraction_instructions="Extract all email addresses with their types as provided in the document.",
            extraction_priority=8,
            keywords=["email", "e-mail", "electronic mail", "@"]
        )
    ]
)

# Organization Information Sub-Domain
organization_info_subdomain = SubDomainDefinition(
    name="organization_info",
    description="organization information",
    extraction_instructions="Look for organization information in sections about the company, institution, or entity.",
    priority=8,
    fields=[
        FieldDefinition(
            name="organization_name",
            description="Name of the organization",
            type="string",
            is_required=True,
            is_unique=True,
            examples=["Bay Area Medical Center", "Smith & Jones Law Firm", "Acme Corporation"],
            extraction_instructions="Extract the full official name of the organization as it appears in the document.",
            extraction_priority=10,
            keywords=["organization", "company", "institution", "corporation", "firm", "entity"]
        ),
        FieldDefinition(
            name="organization_type",
            description="Type of organization",
            type="string",
            is_required=False,
            is_unique=True,
            examples=["Hospital", "Medical Clinic", "Law Firm", "Corporation", "Non-profit"],
            extraction_instructions="Extract the type of organization as stated in the document.",
            extraction_priority=9,
            keywords=["type", "entity", "classification", "structure", "category"]
        ),
        FieldDefinition(
            name="industry",
            description="Industry or sector",
            type="string",
            is_required=False,
            is_unique=True,
            examples=["Healthcare", "Legal Services", "Education", "Technology"],
            extraction_instructions="Extract the industry or sector the organization operates in.",
            extraction_priority=8,
            keywords=["industry", "sector", "field", "market", "business"]
        )
    ]
)

# Location Information Sub-Domain
location_info_subdomain = SubDomainDefinition(
    name="location_info",
    description="location information",
    extraction_instructions="Look for location information in sections about geographic data or places.",
    priority=7,
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
                    "iso_code": "US"
                }
            ],
            extraction_instructions="Extract the country information as provided in the document.",
            extraction_priority=10,
            keywords=["country", "nation", "state", "territory"]
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
                    "country": "USA"
                }
            ],
            extraction_instructions="Extract the city information as provided in the document.",
            extraction_priority=9,
            keywords=["city", "town", "municipality", "urban area"]
        )
    ]
)

# Create the Demographic Domain with anti-hallucination instructions
demographic_domain = DomainDefinition(
    name="demographic",
    description="Demographic domain for personal and organizational information",
    extraction_instructions="Extract demographic information about people, organizations, and locations.",
    keywords=["demographic", "personal", "organization", "contact", "location", "identity"],
    confidence_threshold=0.7,
    anti_hallucination_instructions="""
1. Only extract demographic information that is explicitly stated in the text.
2. Do not infer, assume, or generate demographic information that is not directly present in the text.
3. For names, use the exact name as it appears in the text, preserving capitalization and formatting.
4. For dates, extract only dates that are explicitly mentioned, do not calculate or infer dates.
5. For contact information, include exact phone numbers, email addresses, and physical addresses as stated.
6. Do not use general knowledge to fill in missing demographic information.
7. Always include units with numerical values (e.g., '42 years', '180 cm').
8. Always maintain context by specifying what each value represents (e.g., 'Age: 42 years', not just '42').
9. For dates, always specify what event the date refers to (e.g., 'Date of Birth: 1980-05-15').
10. For relationships between entities, only state relationships explicitly mentioned in the text.
11. For identification numbers, preserve the exact formatting as it appears in the text.
12. For addresses, include all components as provided, maintaining the structure.
13. For organizations, use the exact official name as it appears in the text.
14. For professional information, use the exact titles and roles as stated in the text.
15. For locations, use the exact place names as they appear in the text.
""",
    sub_domains=[
        person_info_subdomain,
        contact_info_subdomain,
        organization_info_subdomain,
        location_info_subdomain
    ]
)

# Register the domain
def register_demographic_domain():
    """Register the demographic domain with the domain registry."""
    registry = DomainRegistry()
    registry.register_domain(demographic_domain)

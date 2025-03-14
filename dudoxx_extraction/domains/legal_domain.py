"""
Legal domain definitions for the Dudoxx Extraction system.

This module provides domain definitions for legal documents, broken down
into smaller sub-domains for more focused extraction.
"""

from dudoxx_extraction.domains.domain_definition import DomainDefinition, SubDomainDefinition, FieldDefinition
from dudoxx_extraction.domains.domain_registry import DomainRegistry


# Agreement Information Sub-Domain
agreement_info_subdomain = SubDomainDefinition(
    name="agreement_info",
    description="agreement information",
    fields=[
        FieldDefinition(
            name="title",
            description="Title of the agreement",
            type="string",
            is_required=True,
            is_unique=True,
            examples=["Consulting Services Agreement", "Employment Agreement"]
        ),
        FieldDefinition(
            name="effective_date",
            description="Date when the agreement becomes effective",
            type="date",
            is_required=True,
            is_unique=True,
            examples=["January 15, 2023", "2023-01-15", "01/15/2023"]
        ),
        FieldDefinition(
            name="termination_date",
            description="Date when the agreement terminates",
            type="date",
            is_required=False,
            is_unique=True,
            examples=["January 14, 2024", "2024-01-14", "01/14/2024"]
        ),
        FieldDefinition(
            name="governing_law",
            description="Governing law for the agreement",
            type="string",
            is_required=False,
            is_unique=True,
            examples=["California law", "Laws of the State of New York"]
        )
    ]
)

# Parties Sub-Domain
parties_subdomain = SubDomainDefinition(
    name="parties",
    description="parties involved in the agreement",
    fields=[
        FieldDefinition(
            name="parties",
            description="List of parties involved in the agreement with their details",
            type="list",
            is_required=True,
            is_unique=False,
            examples=[
                {
                    "name": "ABC Corporation",
                    "type": "Delaware corporation",
                    "location": "123 Corporate Drive, Business City, CA 94123",
                    "role": "Client"
                },
                {
                    "name": "XYZ Consulting LLC",
                    "type": "California limited liability company",
                    "location": "456 Consultant Avenue, Expertise City, CA 95678",
                    "role": "Consultant"
                }
            ]
        )
    ]
)

# Obligations Sub-Domain
obligations_subdomain = SubDomainDefinition(
    name="obligations",
    description="obligations of the parties",
    fields=[
        FieldDefinition(
            name="obligations",
            description="List of obligations for each party",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                {
                    "party": "Consultant",
                    "description": "Perform the Services in accordance with the highest professional standards",
                    "deadline": "Throughout the Term"
                },
                {
                    "party": "Client",
                    "description": "Pay Consultant the fees set forth in Exhibit B",
                    "deadline": "Within thirty (30) days after receipt of each invoice"
                }
            ]
        )
    ]
)

# Payment Terms Sub-Domain
payment_terms_subdomain = SubDomainDefinition(
    name="payment_terms",
    description="payment terms",
    fields=[
        FieldDefinition(
            name="payment_terms",
            description="Payment terms of the agreement",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "fee_structure": "Monthly fee of $10,000",
                    "payment_schedule": "Within thirty (30) days after receipt of each invoice",
                    "late_payment_penalty": "Interest at the rate of 1.5% per month"
                }
            ]
        )
    ]
)

# Termination Provisions Sub-Domain
termination_provisions_subdomain = SubDomainDefinition(
    name="termination_provisions",
    description="termination provisions",
    fields=[
        FieldDefinition(
            name="termination_provisions",
            description="Provisions for termination of the agreement",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                {
                    "type": "Termination for Convenience",
                    "description": "Either party may terminate this Agreement at any time without cause upon thirty (30) days' prior written notice to the other party."
                },
                {
                    "type": "Termination for Cause",
                    "description": "Either party may terminate this Agreement immediately upon written notice if the other party materially breaches this Agreement and fails to cure such breach within fifteen (15) days after receiving written notice thereof."
                }
            ]
        )
    ]
)

# Confidentiality Sub-Domain
confidentiality_subdomain = SubDomainDefinition(
    name="confidentiality",
    description="confidentiality provisions",
    fields=[
        FieldDefinition(
            name="confidentiality_provisions",
            description="Provisions related to confidentiality",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "definition": "All non-public information disclosed by one party to the other party",
                    "obligations": "Recipient shall maintain the confidentiality of the Confidential Information and shall not disclose it to any third party",
                    "exclusions": "Information that is or becomes publicly available through no fault of the Recipient",
                    "term": "Three (3) years after the termination of this Agreement"
                }
            ]
        )
    ]
)

# Create the Legal Domain
legal_domain = DomainDefinition(
    name="legal",
    description="Legal domain for agreements and contracts",
    sub_domains=[
        agreement_info_subdomain,
        parties_subdomain,
        obligations_subdomain,
        payment_terms_subdomain,
        termination_provisions_subdomain,
        confidentiality_subdomain
    ]
)

# Register the domain
def register_legal_domain():
    """Register the legal domain with the domain registry."""
    registry = DomainRegistry()
    registry.register_domain(legal_domain)

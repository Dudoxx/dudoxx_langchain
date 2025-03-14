"""
Specialized Legal Domain definitions for the Dudoxx Extraction system.

This module provides specialized domain definitions for legal documents,
focusing on specific types of legal documents like contracts, NDAs,
employment agreements, and intellectual property documents.
"""

from dudoxx_extraction.domains.domain_definition import DomainDefinition, SubDomainDefinition, FieldDefinition
from dudoxx_extraction.domains.domain_registry import DomainRegistry


# Contract Information Sub-Domain
contract_info_subdomain = SubDomainDefinition(
    name="contract_info",
    description="contract information",
    fields=[
        FieldDefinition(
            name="contract_type",
            description="Type of contract",
            type="string",
            is_required=True,
            is_unique=True,
            examples=["Service Agreement", "Employment Contract", "License Agreement"]
        ),
        FieldDefinition(
            name="contract_id",
            description="Contract identification number or reference",
            type="string",
            is_required=False,
            is_unique=True,
            examples=["CTR-2023-0456", "AGR-XYZ-789"]
        ),
        FieldDefinition(
            name="execution_date",
            description="Date when the contract was signed or executed",
            type="date",
            is_required=True,
            is_unique=True,
            examples=["March 10, 2025", "2025-03-10", "03/10/2025"]
        ),
        FieldDefinition(
            name="contract_term",
            description="Duration or term of the contract",
            type="string",
            is_required=False,
            is_unique=True,
            examples=["One year from Effective Date", "Until services are completed"]
        )
    ]
)

# Legal Representation Sub-Domain
legal_representation_subdomain = SubDomainDefinition(
    name="legal_representation",
    description="legal representation details",
    fields=[
        FieldDefinition(
            name="law_firm",
            description="Name and details of the law firm",
            type="object",
            is_required=True,
            is_unique=True,
            examples=[
                {
                    "name": "Smith & Associates, LLP",
                    "type": "New York limited liability partnership",
                    "address": "123 Legal Avenue, New York, NY 10001",
                    "primary_contact": "John Smith, Managing Partner"
                }
            ]
        ),
        FieldDefinition(
            name="attorneys",
            description="List of attorneys assigned to the matter",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                {
                    "name": "John Smith",
                    "position": "Partner",
                    "hourly_rate": "$750",
                    "practice_area": "Litigation"
                },
                {
                    "name": "Sarah Johnson",
                    "position": "Associate",
                    "hourly_rate": "$500",
                    "practice_area": "Intellectual Property"
                }
            ]
        )
    ]
)

# Legal Fees Sub-Domain
legal_fees_subdomain = SubDomainDefinition(
    name="legal_fees",
    description="legal fees and billing structure",
    fields=[
        FieldDefinition(
            name="fee_structure",
            description="Structure of legal fees",
            type="string",
            is_required=True,
            is_unique=True,
            examples=["Hourly rates", "Flat fee", "Contingency fee", "Retainer"]
        ),
        FieldDefinition(
            name="rates",
            description="Hourly rates or fee amounts",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "partners": "$650 - $850 per hour",
                    "senior_associates": "$450 - $600 per hour",
                    "junior_associates": "$350 - $450 per hour",
                    "paralegals": "$175 - $250 per hour"
                }
            ]
        ),
        FieldDefinition(
            name="retainer",
            description="Retainer amount and terms",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "amount": "$25,000",
                    "replenishment": "When depleted below $5,000",
                    "application": "Applied against future invoices"
                }
            ]
        ),
        FieldDefinition(
            name="billing_cycle",
            description="Billing frequency and payment terms",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "frequency": "Monthly",
                    "payment_terms": "30 days after receipt of invoice",
                    "late_payment_penalty": "1% per month"
                }
            ]
        )
    ]
)

# Legal Matter Sub-Domain
legal_matter_subdomain = SubDomainDefinition(
    name="legal_matter",
    description="legal matter details",
    fields=[
        FieldDefinition(
            name="matter_type",
            description="Type of legal matter",
            type="string",
            is_required=True,
            is_unique=True,
            examples=["Litigation", "Corporate Transaction", "Regulatory Compliance", "Intellectual Property"]
        ),
        FieldDefinition(
            name="case_details",
            description="Details of the case or matter",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "case_name": "Acme Corporation v. XYZ Technologies, Inc.",
                    "case_number": "25-CV-1234",
                    "court": "United States District Court for the Southern District of New York",
                    "filing_date": "January 15, 2025"
                }
            ]
        ),
        FieldDefinition(
            name="scope_of_services",
            description="Scope of legal services to be provided",
            type="list",
            is_required=True,
            is_unique=False,
            examples=[
                "Conducting legal research and analysis",
                "Drafting and filing pleadings, motions, and other court documents",
                "Conducting discovery, including document review, depositions, and expert discovery",
                "Settlement negotiations",
                "Trial preparation and representation at trial"
            ]
        )
    ]
)

# Dispute Resolution Sub-Domain
dispute_resolution_subdomain = SubDomainDefinition(
    name="dispute_resolution",
    description="dispute resolution provisions",
    fields=[
        FieldDefinition(
            name="dispute_resolution_method",
            description="Method for resolving disputes",
            type="string",
            is_required=False,
            is_unique=True,
            examples=["Arbitration", "Mediation", "Litigation", "Negotiation"]
        ),
        FieldDefinition(
            name="arbitration_details",
            description="Details of arbitration process",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "administrator": "American Arbitration Association",
                    "rules": "Commercial Arbitration Rules",
                    "location": "New York, New York",
                    "arbitrator_selection": "Single arbitrator selected by mutual agreement"
                }
            ]
        ),
        FieldDefinition(
            name="governing_law",
            description="Governing law for disputes",
            type="string",
            is_required=False,
            is_unique=True,
            examples=["Laws of the State of New York", "California law"]
        ),
        FieldDefinition(
            name="jurisdiction",
            description="Jurisdiction for legal proceedings",
            type="string",
            is_required=False,
            is_unique=True,
            examples=["Courts of the Southern District of New York", "State and federal courts located in San Francisco County, California"]
        )
    ]
)

# Create the Specialized Legal Domain
specialized_legal_domain = DomainDefinition(
    name="specialized_legal",
    description="Specialized legal domain for detailed legal document analysis",
    sub_domains=[
        contract_info_subdomain,
        legal_representation_subdomain,
        legal_fees_subdomain,
        legal_matter_subdomain,
        dispute_resolution_subdomain
    ]
)

# Register the domain
def register_specialized_legal_domain():
    """Register the specialized legal domain with the domain registry."""
    registry = DomainRegistry()
    registry.register_domain(specialized_legal_domain)

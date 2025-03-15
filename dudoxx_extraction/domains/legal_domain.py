"""
Legal domain definitions for the Dudoxx Extraction system.

This module provides domain definitions for legal documents, broken down
into smaller sub-domains for more focused extraction.
"""

from dudoxx_extraction.domains.domain_definition import DomainDefinition, SubDomainDefinition, FieldDefinition, ValidationLevel
from dudoxx_extraction.domains.domain_registry import DomainRegistry


# Parties Sub-Domain
parties_subdomain = SubDomainDefinition(
    name="parties",
    description="parties involved in the legal document",
    extraction_instructions="Look for parties typically at the beginning of legal documents, often in a section labeled 'Parties', 'Between', or in the introductory paragraph.",
    priority=10,
    fields=[
        FieldDefinition(
            name="parties",
            description="List of parties involved in the legal document",
            type="list",
            is_required=True,
            is_unique=True,
            examples=[
                {"name": "Acme Corporation", "type": "Company", "role": "Seller"},
                {"name": "John Smith", "type": "Individual", "role": "Buyer"}
            ],
            extraction_instructions="Extract the full name of each party, their type (individual, company, etc.), and their role in the agreement (buyer, seller, lessor, lessee, etc.).",
            formatting_instructions="Format company names with proper capitalization. For individuals, use full legal names.",
            keywords=["party", "parties", "between", "agreement", "contract", "hereinafter", "referred to as"],
            extraction_priority=10,
            format_function="capitalize_names"
        )
    ]
)

# Contract Dates Sub-Domain
contract_dates_subdomain = SubDomainDefinition(
    name="contract_dates",
    description="important dates in the contract",
    extraction_instructions="Look for dates throughout the document, particularly in sections about term, effective date, or termination.",
    priority=9,
    fields=[
        FieldDefinition(
            name="effective_date",
            description="Date when the contract becomes effective",
            type="date",
            is_required=True,
            is_unique=True,
            examples=["January 1, 2023", "01/01/2023", "2023-01-01"],
            extraction_instructions="Look for phrases like 'effective date', 'commencement date', or 'this agreement is made on'.",
            formatting_instructions="Format as YYYY-MM-DD.",
            format_pattern=r"^\d{4}-\d{2}-\d{2}$",
            format_function="format_date_iso",
            keywords=["effective", "commencement", "begins", "start date", "as of", "made on"],
            extraction_priority=9,
            validation_function="validate_date"
        ),
        FieldDefinition(
            name="termination_date",
            description="Date when the contract terminates",
            type="date",
            is_required=False,
            is_unique=True,
            examples=["December 31, 2025", "12/31/2025", "2025-12-31"],
            extraction_instructions="Look for phrases like 'termination date', 'expiration date', or 'end date'.",
            formatting_instructions="Format as YYYY-MM-DD.",
            format_pattern=r"^\d{4}-\d{2}-\d{2}$",
            format_function="format_date_iso",
            keywords=["termination", "expiration", "expires", "end date", "concludes", "until"],
            extraction_priority=8,
            validation_function="validate_date"
        ),
        FieldDefinition(
            name="execution_date",
            description="Date when the contract was executed or signed",
            type="date",
            is_required=False,
            is_unique=True,
            examples=["December 15, 2022", "12/15/2022", "2022-12-15"],
            extraction_instructions="Look for dates near signatures or in the signature block.",
            formatting_instructions="Format as YYYY-MM-DD.",
            format_pattern=r"^\d{4}-\d{2}-\d{2}$",
            format_function="format_date_iso",
            keywords=["executed", "signed", "signature", "dated", "in witness whereof"],
            extraction_priority=7,
            validation_function="validate_date"
        )
    ]
)

# Contract Terms Sub-Domain
contract_terms_subdomain = SubDomainDefinition(
    name="contract_terms",
    description="key terms and conditions of the contract",
    extraction_instructions="Look for terms and conditions throughout the document, particularly in numbered or lettered sections.",
    priority=8,
    fields=[
        FieldDefinition(
            name="term_length",
            description="Length of the contract term",
            type="string",
            is_required=False,
            is_unique=True,
            examples=["3 years", "36 months", "1 year with automatic renewal"],
            extraction_instructions="Look for phrases describing the duration of the agreement.",
            keywords=["term", "duration", "period", "length", "years", "months"],
            extraction_priority=6
        ),
        FieldDefinition(
            name="payment_terms",
            description="Terms related to payment",
            type="string",
            is_required=False,
            is_unique=True,
            examples=["$5,000 per month, due on the 1st of each month", "Annual fee of $60,000 payable in quarterly installments"],
            extraction_instructions="Look for sections about payment, fees, compensation, or consideration.",
            keywords=["payment", "fee", "compensation", "consideration", "price", "cost", "amount", "pay", "paid"],
            extraction_priority=5
        ),
        FieldDefinition(
            name="termination_conditions",
            description="Conditions under which the contract may be terminated",
            type="list",
            is_required=False,
            is_unique=False,
            examples=["30 days written notice", "Material breach with 10 days to cure", "Immediately upon bankruptcy"],
            extraction_instructions="Look for sections about termination, cancellation, or ending the agreement.",
            keywords=["terminate", "termination", "cancel", "cancellation", "end", "breach", "default"],
            extraction_priority=4
        )
    ]
)

# Obligations Sub-Domain
obligations_subdomain = SubDomainDefinition(
    name="obligations",
    description="obligations of the parties",
    extraction_instructions="Look for sections describing what each party must do or provide under the agreement.",
    priority=7,
    fields=[
        FieldDefinition(
            name="obligations",
            description="List of obligations for each party",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                {"party": "Seller", "obligation": "Deliver goods within 30 days of order"},
                {"party": "Buyer", "obligation": "Pay invoice within 15 days of receipt"}
            ],
            extraction_instructions="Extract which party has the obligation and what they are obligated to do.",
            keywords=["shall", "must", "will", "agrees to", "responsible for", "obligation", "duty", "required to"],
            extraction_priority=3
        )
    ]
)

# Governing Law Sub-Domain
governing_law_subdomain = SubDomainDefinition(
    name="governing_law",
    description="governing law and jurisdiction",
    extraction_instructions="Look for sections about governing law, jurisdiction, or dispute resolution, typically near the end of the document.",
    priority=6,
    fields=[
        FieldDefinition(
            name="governing_law",
            description="Law governing the contract",
            type="string",
            is_required=False,
            is_unique=True,
            examples=["Laws of the State of California", "New York law", "Laws of England and Wales"],
            extraction_instructions="Extract the jurisdiction whose laws govern the contract.",
            keywords=["govern", "governing law", "jurisdiction", "construed", "interpreted", "accordance with the laws"],
            extraction_priority=2
        ),
        FieldDefinition(
            name="dispute_resolution",
            description="Method of dispute resolution",
            type="string",
            is_required=False,
            is_unique=True,
            examples=["Arbitration in Los Angeles, California", "Litigation in the courts of New York County"],
            extraction_instructions="Extract the method (arbitration, litigation, mediation) and location for resolving disputes.",
            keywords=["dispute", "arbitration", "mediation", "litigation", "court", "venue", "forum"],
            extraction_priority=1
        )
    ]
)

# Create the Legal Domain
legal_domain = DomainDefinition(
    name="legal",
    description="Legal domain for contracts and agreements",
    extraction_instructions="This is a legal document. Pay special attention to parties, dates, terms, and obligations.",
    keywords=["contract", "agreement", "legal", "parties", "terms", "conditions", "clause", "provision"],
    confidence_threshold=0.7,
    merge_function="merge_legal_results",
    anti_hallucination_instructions="""
1. For legal terms, use the exact terminology found in the text rather than synonyms or interpretations.
2. Do not infer legal relationships or obligations not explicitly stated in the text.
3. For dates, extract exact dates only if specified, do not calculate or infer dates.
4. Do not make legal judgments or interpretations of clauses or provisions.
5. Distinguish between definitive statements and conditional language (e.g., "shall" vs "may").
6. For monetary values, include exact amounts with currency symbols as stated in the text.
7. For parties, only include those explicitly named in the agreement, not implied parties.
8. For contract terms, do not assume standard terms that aren't explicitly mentioned.
9. Always include units with numerical values (e.g., '$5,000', '30 days', '12 months').
10. Always maintain context by specifying what each value represents (e.g., 'Effective Date: 2023-03-15', not just '2023-03-15').
11. For dates, always specify what event the date refers to (e.g., 'Effective Date: 2023-03-15', 'Termination Date: 2025-03-14').
12. For measurements, include both the value and what was measured (e.g., 'Term Length: 24 months', not just '24 months').
13. For ranges, include both the lower and upper bounds with units (e.g., 'Payment window: 30-45 days').
14. For status indicators, use the exact terminology from the text (e.g., 'in effect', 'terminated').
15. For relationships between entities, only state relationships explicitly mentioned in the text.
""",
    sub_domains=[
        parties_subdomain,
        contract_dates_subdomain,
        contract_terms_subdomain,
        obligations_subdomain,
        governing_law_subdomain
    ]
)

# Register the domain
def register_legal_domain():
    """Register the legal domain with the domain registry."""
    registry = DomainRegistry()
    registry.register_domain(legal_domain)

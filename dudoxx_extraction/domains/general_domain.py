"""
General domain definitions for the Dudoxx Extraction system.

This module provides a general-purpose domain definition for extracting
information from text when no specific domain is identified.
"""

from dudoxx_extraction.domains.domain_definition import DomainDefinition, SubDomainDefinition, FieldDefinition
from dudoxx_extraction.domains.domain_registry import DomainRegistry


# General Content Sub-Domain
general_content_subdomain = SubDomainDefinition(
    name="general_content",
    description="general content information",
    extraction_instructions="""
Extract the main content and key information from the text, including entities, dates, and numerical values.
Focus on capturing the most important and relevant information without adding interpretations.
Pay attention to named entities (people, organizations, locations) and their relationships.
Identify dates and temporal information, noting what events they refer to.
Extract numerical values with their units and context about what they represent.
""",
    priority=10,
    fields=[
        FieldDefinition(
            name="content",
            description="General content extracted from the text",
            type="string",
            is_required=True,
            is_unique=True,
            examples=[
                {
                    "text": "This is some general content extracted from the text.",
                    "document_type": "Agreement",
                    "primary_purpose": "To establish terms of service between parties",
                    "key_points": [
                        "Defines scope of services",
                        "Establishes payment terms",
                        "Outlines confidentiality requirements"
                    ],
                    "context": "Business relationship between service provider and client"
                }
            ],
            extraction_instructions="""
Extract the main content of the text, focusing on the most important information.
Preserve the original meaning and key points without adding interpretations.
IMPORTANT: Identify the document type or category (e.g., "Agreement", "Report", "Article").
IMPORTANT: Determine the primary purpose or objective of the document.
IMPORTANT: List the key points, main arguments, or critical facts presented in the document.
IMPORTANT: Provide context about the overall subject matter and its significance.
Include important facts, statements, and conclusions from the text.
Maintain the original context and relationships between pieces of information.
Do not summarize or paraphrase unless the content is extremely lengthy.
Ensure that the extracted content is meaningful by providing its purpose and significance.
""",
            extraction_priority=10
        ),
        FieldDefinition(
            name="entities",
            description="Named entities found in the text (people, organizations, locations, etc.)",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                {
                    "type": "PERSON", 
                    "text": "John Smith", 
                    "position": [10, 20],
                    "role": "CEO",
                    "context": "Signatory",
                    "related_fact": "Authorized to sign on behalf of Acme Corporation",
                    "relationships": [{"entity": "Acme Corporation", "relationship": "employee"}]
                },
                {
                    "type": "ORGANIZATION", 
                    "text": "Acme Corporation", 
                    "position": [45, 60],
                    "industry": "Technology",
                    "context": "Service provider",
                    "related_fact": "Provides software development services as outlined in the agreement",
                    "relationships": [{"entity": "John Smith", "relationship": "employer"}]
                },
                {
                    "type": "LOCATION", 
                    "text": "San Francisco", 
                    "position": [75, 88],
                    "region": "California",
                    "context": "Jurisdiction",
                    "related_fact": "Laws of this jurisdiction govern the agreement",
                    "relationships": [{"entity": "Acme Corporation", "relationship": "headquarters"}]
                }
            ],
            extraction_instructions="""
Extract named entities mentioned in the text, including people, organizations, locations, etc.
Use the exact name as it appears in the text, preserving capitalization and formatting.
Classify each entity by type (PERSON, ORGANIZATION, LOCATION, etc.).
Include the position (character indices) where the entity appears in the text when possible.
IMPORTANT: For people, include titles, roles, or positions if mentioned (e.g., "Dr. Jane Smith, CEO").
IMPORTANT: For organizations, include industry, type, or sector if mentioned.
IMPORTANT: For locations, include region, country, or other geographic context if mentioned.
IMPORTANT: Include context about the entity's role or purpose in the document (e.g., "Signatory", "Service provider", "Jurisdiction").
IMPORTANT: Include any related facts or information about the entity mentioned in the text.
IMPORTANT: Include relationships between this entity and other entities in the document when explicitly stated.
For people, note their affiliations, positions, and responsibilities.
For organizations, note their business activities, roles in agreements, and relationships with other entities.
For locations, note their significance in the context of the document (e.g., place of performance, jurisdiction).
Ensure that the extracted entity is meaningful by providing its purpose and significance in the document.
""",
            extraction_priority=9,
            keywords=["name", "person", "company", "organization", "location", "place", "entity"]
        ),
        FieldDefinition(
            name="dates",
            description="Dates mentioned in the text",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                {
                    "date": "2023-05-15", 
                    "original_text": "May 15, 2023", 
                    "position": [100, 112],
                    "context": "Contract signing date",
                    "related_fact": "The agreement becomes effective on this date",
                    "entity": "Agreement"
                },
                {
                    "date": "2022-12-25", 
                    "original_text": "Christmas 2022", 
                    "position": [150, 165],
                    "context": "Holiday reference",
                    "related_fact": "Office will be closed during this period",
                    "entity": "Company"
                }
            ],
            extraction_instructions="""
Extract all dates mentioned in the text, including both explicit and implicit dates.
Normalize dates to ISO format (YYYY-MM-DD) when possible.
Include the original text of the date as it appears in the document.
Include the position (character indices) where the date appears in the text when possible.
IMPORTANT: Always include context about what the date refers to (e.g., "Publication date", "Deadline", "Contract signing").
IMPORTANT: Include any related facts or implications associated with the date (e.g., "The agreement becomes effective on this date").
IMPORTANT: Include the entity or subject that the date is associated with (e.g., "Company", "Agreement", "Employee").
For relative dates (e.g., "yesterday", "next month"), note that they are relative.
For partial dates (e.g., "December 2022", "2023"), include as much information as available.
For date ranges, extract both the start and end dates separately.
Ensure that the extracted date is meaningful by providing its purpose and significance in the document.
""",
            extraction_priority=8,
            keywords=["date", "day", "month", "year", "time", "period", "deadline", "schedule"]
        ),
        FieldDefinition(
            name="numbers",
            description="Numerical values found in the text",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                {
                    "value": 42, 
                    "original_text": "42", 
                    "position": [200, 202],
                    "units": "days",
                    "context": "Notice period",
                    "related_fact": "Employee must provide 42 days notice before termination",
                    "entity": "Employee"
                },
                {
                    "value": 3.14, 
                    "original_text": "3.14", 
                    "position": [220, 224],
                    "units": "percent",
                    "context": "Interest rate",
                    "related_fact": "Annual interest rate applied to late payments",
                    "entity": "Payment terms"
                },
                {
                    "value": 1000000, 
                    "original_text": "1 million", 
                    "position": [240, 249],
                    "units": "USD",
                    "context": "Liability cap",
                    "related_fact": "Maximum liability for damages is limited to this amount",
                    "entity": "Contract"
                }
            ],
            extraction_instructions="""
Extract all numerical values mentioned in the text, including integers, decimals, and numbers written as words.
Convert numbers written as words to their numerical form (e.g., "one million" to 1000000).
Include the original text of the number as it appears in the document.
Include the position (character indices) where the number appears in the text when possible.
IMPORTANT: Always include units with the number if they are present in the text (e.g., "$500", "42 kg", "15%").
IMPORTANT: Always include context about what the number represents (e.g., "Price", "Weight", "Percentage", "Duration").
IMPORTANT: Include any related facts or implications associated with the number (e.g., "This is the maximum allowed amount").
IMPORTANT: Include the entity or subject that the number is associated with (e.g., "Company", "Product", "Employee").
For ranges, extract both the lower and upper bounds separately with their shared context.
For approximate values, indicate that they are approximate (e.g., "approximately 500").
Ensure that the extracted number is meaningful by providing its purpose and significance in the document.
""",
            extraction_priority=7,
            keywords=["number", "value", "amount", "quantity", "measure", "count", "total", "sum"]
        )
    ]
)

# Key-Value Pairs Sub-Domain
key_value_subdomain = SubDomainDefinition(
    name="key_value_pairs",
    description="key-value pairs extracted from the text",
    extraction_instructions="Look for structured information presented as key-value pairs, such as forms, tables, or labeled data.",
    priority=8,
    fields=[
        FieldDefinition(
            name="pairs",
            description="Key-value pairs extracted from the text",
            type="list",
            is_required=True,
            is_unique=False,
            examples=[
                {
                    "key": "Name", 
                    "value": "John Smith",
                    "context": "Employee information",
                    "related_fact": "Primary contact for the project",
                    "entity": "Employee",
                    "section": "Personnel Details"
                },
                {
                    "key": "Email", 
                    "value": "john.smith@example.com",
                    "context": "Contact information",
                    "related_fact": "Preferred method of communication",
                    "entity": "Employee",
                    "section": "Contact Details"
                },
                {
                    "key": "Payment Terms", 
                    "value": "Net 30 days",
                    "context": "Financial information",
                    "related_fact": "Invoices must be paid within 30 days of receipt",
                    "entity": "Agreement",
                    "section": "Financial Terms"
                }
            ],
            extraction_instructions="""
Extract key-value pairs that are explicitly presented in the text.
Look for information structured as labels followed by values, such as "Name: John Smith".
Preserve the exact key (label) as it appears in the text, maintaining capitalization.
Include the complete value associated with each key, preserving formatting and punctuation.
IMPORTANT: Include context about what category or type of information this key-value pair represents.
IMPORTANT: Include any related facts or implications associated with this key-value pair.
IMPORTANT: Include the entity or subject that this key-value pair is associated with.
IMPORTANT: Note the section or part of the document where this key-value pair appears when relevant.
For values with multiple parts (e.g., addresses), include all components.
For values with units, include the units with the value (e.g., "Weight: 70 kg").
For dates, include the full date as presented (e.g., "Date of Birth: May 15, 1980").
For lists presented as values, include all items in the list.
Do not create key-value pairs for information that is not explicitly structured as such in the text.
Ensure that the extracted key-value pair is meaningful by providing its purpose and significance in the document.
""",
            extraction_priority=10,
            keywords=["key", "value", "field", "label", "attribute", "property", "parameter"]
        )
    ]
)

# Summary Sub-Domain
summary_subdomain = SubDomainDefinition(
    name="summary",
    description="summary information",
    extraction_instructions="Create a concise summary of the text that captures the main points and key information.",
    priority=7,
    fields=[
        FieldDefinition(
            name="summary",
            description="Summary of the text content",
            type="string",
            is_required=True,
            is_unique=True,
            examples=[
                {
                    "text": "This text discusses the benefits of renewable energy sources and their impact on climate change.",
                    "document_type": "Research article",
                    "primary_audience": "Environmental policy makers",
                    "key_conclusions": [
                        "Renewable energy reduces carbon emissions by 40%",
                        "Implementation costs have decreased significantly",
                        "Policy changes are needed for wider adoption"
                    ],
                    "significance": "Provides evidence for policy decisions on energy transition"
                }
            ],
            extraction_instructions="""
Create a concise summary of the text that captures the main points and key information.
Focus on the most important facts, arguments, and conclusions presented in the text.
IMPORTANT: Identify the document type or category (e.g., "Research article", "Policy brief", "News report").
IMPORTANT: Identify the primary intended audience of the document when possible.
IMPORTANT: List the key conclusions or findings presented in the document.
IMPORTANT: Explain the significance or implications of the document's content.
Maintain objectivity and avoid adding interpretations not present in the original text.
Use clear, straightforward language that accurately represents the content.
Keep the summary to 1-3 sentences for short texts, or 3-5 sentences for longer texts.
Ensure the summary covers the main subject matter and purpose of the text.
Do not include minor details or tangential information.
""",
            extraction_priority=10
        ),
        FieldDefinition(
            name="topics",
            description="Main topics discussed in the text",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                {
                    "topic": "Renewable Energy",
                    "prominence": "primary",
                    "context": "Main subject of the document",
                    "related_subtopics": ["Solar power", "Wind energy", "Hydroelectric"],
                    "key_points": ["Cost reduction trends", "Implementation challenges", "Environmental benefits"]
                },
                {
                    "topic": "Climate Change",
                    "prominence": "secondary",
                    "context": "Motivation for renewable energy adoption",
                    "related_subtopics": ["Carbon emissions", "Global warming", "Environmental impact"],
                    "key_points": ["Reduction targets", "International agreements", "Scientific evidence"]
                },
                {
                    "topic": "Environmental Policy",
                    "prominence": "tertiary",
                    "context": "Framework for implementation",
                    "related_subtopics": ["Regulations", "Incentives", "International cooperation"],
                    "key_points": ["Policy recommendations", "Regulatory frameworks", "Economic instruments"]
                }
            ],
            extraction_instructions="""
Identify the main topics or subjects discussed in the text.
Extract topics that are central to the text's content, not peripheral mentions.
IMPORTANT: Indicate the prominence or importance of each topic (primary, secondary, tertiary).
IMPORTANT: Provide context about how the topic relates to the overall document.
IMPORTANT: List related subtopics that fall under the main topic.
IMPORTANT: Include key points or aspects discussed about each topic.
Use the exact terminology from the text when possible.
Format topics as short phrases (1-3 words) rather than complete sentences.
Include only distinct topics, avoiding redundancy.
List topics in order of prominence or importance in the text.
For each topic, ensure it represents a significant theme or subject in the text.
Ensure that the extracted topics are meaningful by providing their context and significance in the document.
""",
            extraction_priority=9,
            keywords=["topic", "subject", "theme", "focus", "area", "category"]
        ),
        FieldDefinition(
            name="sentiment",
            description="Overall sentiment of the text",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "polarity": "positive",
                    "confidence": 0.85,
                    "explanation": "The text contains predominantly positive language about renewable energy solutions.",
                    "context": "Evaluation of renewable energy technologies",
                    "supporting_evidence": [
                        "Uses terms like 'beneficial', 'promising', and 'successful'",
                        "Emphasizes cost savings and environmental benefits",
                        "Presents case studies with positive outcomes"
                    ],
                    "subject_specific_sentiments": [
                        {"subject": "Solar power", "sentiment": "very positive"},
                        {"subject": "Implementation costs", "sentiment": "slightly negative"},
                        {"subject": "Government policies", "sentiment": "neutral"}
                    ],
                    "tone_indicators": ["Optimistic", "Encouraging", "Factual"]
                }
            ],
            extraction_instructions="""
Analyze the overall sentiment or tone of the text.
Classify the sentiment as positive, negative, neutral, or mixed.
IMPORTANT: Provide a confidence score (0.0-1.0) for your sentiment classification.
IMPORTANT: Include a detailed explanation of why you classified the sentiment as you did.
IMPORTANT: Provide context about what aspect of the document the sentiment applies to.
IMPORTANT: List specific evidence from the text that supports your sentiment classification.
IMPORTANT: Identify subject-specific sentiments for different topics or entities mentioned in the text.
IMPORTANT: Note tone indicators that characterize the author's writing style or approach.
Base your analysis on the language, tone, and content of the text.
Look for emotional language, evaluative statements, and subjective expressions.
Consider the author's apparent attitude toward the main subject matter.
Avoid inferring sentiment that isn't explicitly conveyed in the text.
Ensure that the extracted sentiment is meaningful by providing its context and supporting evidence.
""",
            extraction_priority=8,
            keywords=["sentiment", "tone", "attitude", "emotion", "feeling", "opinion", "mood"]
        )
    ]
)

# Create the General Domain
general_domain = DomainDefinition(
    name="general",
    description="General-purpose domain for extracting information when no specific domain is identified",
    extraction_instructions="This is a general document without a specific domain. Extract key information, entities, dates, and important facts.",
    keywords=["general", "content", "information", "text", "document", "data", "summary", "key", "value"],
    confidence_threshold=0.5,
    anti_hallucination_instructions="""
1. Only extract information that is explicitly stated in the text.
2. Do not infer, assume, or generate information that is not directly present in the text.
3. For entities, use the exact names as they appear in the text.
4. For dates, extract only dates that are explicitly mentioned, do not calculate or infer dates.
5. For numerical values, include exact values with units as stated in the text.
6. Do not summarize or paraphrase content unless specifically requested.
7. For key-value pairs, only extract relationships that are clearly indicated in the text.
8. Do not use general knowledge to fill in missing information.
9. Always include units with numerical values (e.g., '42 kg', '15%', '$500').
10. Always maintain context by specifying what each value represents (e.g., 'Price: $500', not just '$500').
11. For dates, always specify what event the date refers to (e.g., 'Publication date: 2023-03-15').
12. For measurements, include both the value and what was measured (e.g., 'Height: 180 cm').
13. For ranges, include both the lower and upper bounds with units (e.g., 'Temperature range: 20-25°C').
14. For status indicators, use the exact terminology from the text.
15. For relationships between entities, only state relationships explicitly mentioned in the text.
""",
    sub_domains=[
        general_content_subdomain,
        key_value_subdomain,
        summary_subdomain
    ]
)

# Register the domain
def register_general_domain():
    """Register the general domain with the domain registry."""
    registry = DomainRegistry()
    registry.register_domain(general_domain)

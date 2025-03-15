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
            extraction_instructions="""
Look for the patient's name near labels like 'Patient:', 'Name:', 'Patient Name:'.
Always specify that this is the patient's name to maintain context.
Include the full name as provided in the text (first, middle, last).
Include any prefixes (e.g., 'Dr.', 'Mr.', 'Mrs.') or suffixes (e.g., 'Jr.', 'Sr.', 'III') if present.
If multiple names are present (e.g., legal name and preferred name), include both with clear labels.
""",
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
            extraction_instructions="""
Look for date of birth near labels like 'DOB:', 'Birth Date:', 'Date of Birth:'.
Always specify that this is the patient's date of birth to maintain context.
Include the full date as provided in the text, with day, month, and year if available.
If age is provided instead of date of birth, note that it's an age and include the units (e.g., '42 years').
""",
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
            extraction_instructions="""
Look for gender information near labels like 'Gender:', 'Sex:'.
Always specify that this is the patient's gender to maintain context.
Use the exact terminology found in the text (e.g., 'Male', 'Female', 'Non-binary', 'Transgender male').
If gender identity and biological sex are both mentioned, include both with clear labels.
""",
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
            extraction_instructions="""
Look for medical record number near labels like 'MRN:', 'Medical Record Number:', 'Record #:'.
Always specify that this is the patient's medical record number to maintain context.
Include any prefixes or formatting exactly as shown in the text.
If multiple record numbers are present (e.g., hospital MRN and clinic MRN), include all with clear labels.
""",
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
            extraction_instructions="""
Look for allergies in sections labeled 'Allergies', 'Drug Allergies', or 'Allergy List'.
Always include the specific allergen as stated in the text.
Include the type of reaction if mentioned (e.g., 'Penicillin - anaphylaxis', 'Peanuts - hives').
Include severity information if mentioned (e.g., 'mild', 'moderate', 'severe').
Include any treatment information for allergic reactions if mentioned.
If 'No Known Allergies' or similar is stated, explicitly note this rather than leaving the field empty.
""",
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
            extraction_instructions="""
Look for chronic conditions in sections labeled 'Chronic Conditions', 'Ongoing Conditions', or within the medical history.
Always include the full condition name as stated in the text, using exact medical terminology.
Include diagnosis dates if mentioned, specifying that they are diagnosis dates (e.g., 'Type 2 Diabetes diagnosed in 2015').
Include severity or stage information if mentioned (e.g., 'Stage 2 Hypertension', 'Moderate COPD').
Include any treatment information associated with each condition.
Include status information if mentioned (e.g., 'well-controlled', 'poorly controlled', 'in remission').
""",
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
            extraction_instructions="""
Look for surgeries in sections labeled 'Surgical History', 'Past Surgeries', or 'Procedures'.
Always include the full name of the surgical procedure as stated in the text.
Always include the date of the surgery if mentioned, specifying that it's a surgery date.
Include the reason or indication for the surgery if mentioned.
Include the surgeon's name or the facility where the surgery was performed if mentioned.
Include any complications or outcomes related to the surgery if mentioned.
""",
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
            extraction_instructions="""
Look for family history in sections labeled 'Family History' or 'Family Medical History'.
Always specify the family relationship (e.g., 'Father', 'Mother', 'Sister') for each condition.
Include the specific medical condition using the exact terminology found in the text.
Include age of onset or diagnosis if mentioned (e.g., 'Father - Heart Disease at age 45').
Include status information if mentioned (e.g., 'Mother - Breast Cancer, in remission', 'Father - Heart Disease, deceased at 60').
Include any relevant details about treatment or outcomes if mentioned.
""",
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
            extraction_instructions="""
Extract medication name, dosage WITH UNITS, frequency, and purpose if available.
Always include units with dosages (e.g., '500mg' not just '500').
Always include frequency information (e.g., 'twice daily', 'every 8 hours').
Include the purpose or indication for each medication when available (e.g., 'for hypertension').
If start dates or duration are mentioned, include those as well.
""",
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
            extraction_instructions="""
Extract visit date, provider name, chief complaint, assessment/diagnosis, treatment plan, and follow-up instructions.
For dates, clearly specify that it's a visit date and include the full date as provided.
For complaints, include the full description of symptoms as stated in the text.
For assessments, use the exact diagnostic terminology found in the text.
For treatment plans, include all details including medications WITH DOSAGES AND UNITS.
For follow-up instructions, include specific timeframes and conditions if mentioned.
""",
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
            extraction_instructions="""
Extract all diagnoses mentioned, including primary and secondary diagnoses.
Use the exact diagnostic terminology found in the text, including any qualifiers (e.g., 'suspected', 'rule out', 'history of').
Include diagnosis dates if mentioned (e.g., 'Diabetes diagnosed in 2015').
Include severity indicators if mentioned (e.g., 'mild', 'moderate', 'severe').
For each diagnosis, include any associated context such as symptoms, treatments, or related conditions.
Distinguish between active diagnoses and past medical history.
""",
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
    anti_hallucination_instructions="""
1. Extract lab values exactly as they appear in the text, including units.
2. Do not interpret lab values as normal or abnormal unless explicitly stated.
3. Only include reference ranges if they are explicitly provided in the text.
4. Do not infer test types or categories if not specified.
5. For dates, only associate a date with a lab result if it's clearly indicated as the test date.
6. Do not calculate or derive values that aren't explicitly stated.
7. Always include the test name with each result to maintain context (e.g., 'HbA1c: 7.1%').
8. Always include units with numerical values (e.g., '7.1%', '120 mg/dL').
9. For dates, specify what the date represents (e.g., 'Collection date', 'Result date').
10. For reference ranges, include both the lower and upper bounds with units (e.g., '4.0-5.6%').
11. For interpretations, only use terms explicitly stated in the text (e.g., 'elevated', 'within normal limits').
12. For trending results, maintain the chronological order and include all dates.
13. For panels or groups of tests, clearly indicate which results belong to which panel.
14. For calculated values (e.g., eGFR), only include if explicitly stated in the text.
15. For critical values, include any flags or indicators exactly as they appear (e.g., 'H', 'L', '*').
""",
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
            extraction_instructions="""
Extract test name, date performed, result value WITH UNITS, reference range, and interpretation if available.
Always include units with numerical values (e.g., '7.1%' not just '7.1').
Always include the test name with each result to maintain context.
For dates, specify what the date represents (collection date, result date, etc.).
If multiple values are provided for the same test on different dates, include all of them with their respective dates.
""",
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
    anti_hallucination_instructions="""
1. For medical terms, use the exact terminology found in the text rather than synonyms or interpretations.
2. Do not diagnose or infer medical conditions not explicitly stated in the text.
3. For medications, extract exact dosages and frequencies only if specified.
4. Do not make clinical judgments or interpretations of test results.
5. Distinguish between patient-reported symptoms and clinician observations.
6. For lab results, include values exactly as stated without interpreting normalcy.
7. For allergies, only include those explicitly listed as allergies, not intolerances or side effects unless specified.
8. For medical history, do not assume chronology unless clearly indicated.
9. Always include units with numerical values (e.g., '7.1%', '500mg', '130/85 mmHg').
10. Always maintain context by specifying what each value represents (e.g., 'HbA1c: 7.1%', not just '7.1%').
11. For dates, always specify what event the date refers to (e.g., 'Visit date: 2023-03-15', 'Surgery date: 2020-06-10').
12. For measurements, include both the value and what was measured (e.g., 'Weight: 70 kg', not just '70 kg').
13. For ranges, include both the lower and upper bounds with units (e.g., 'Reference range: 4.0-5.6%').
14. For status indicators, use the exact terminology from the text (e.g., 'well-controlled', 'poorly managed').
15. For relationships between entities, only state relationships explicitly mentioned in the text.
""",
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

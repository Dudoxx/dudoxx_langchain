"""
Specialized medical lab results domain definitions for the Dudoxx Extraction system.

This module provides domain definitions for specialized medical lab results across
various medical specialties including hematology, biochemistry, immunology,
microbiology, pathology, radiology, cardiology, neurology, endocrinology, and genetics.
"""

from dudoxx_extraction.domains.domain_definition import DomainDefinition, SubDomainDefinition, FieldDefinition
from dudoxx_extraction.domains.domain_registry import DomainRegistry


# Hematology Lab Results Sub-Domain
hematology_lab_results_subdomain = SubDomainDefinition(
    name="hematology_lab_results",
    description="hematology laboratory results",
    fields=[
        FieldDefinition(
            name="complete_blood_count",
            description="Complete Blood Count (CBC) results",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "test_date": "2023-03-15",
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
                        }
                    ]
                }
            ]
        ),
        FieldDefinition(
            name="coagulation_studies",
            description="Coagulation studies results",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "test_date": "2023-03-15",
                    "components": [
                        {
                            "component": "Prothrombin Time (PT)",
                            "result": "12.5",
                            "units": "seconds",
                            "reference_range": "11.0-13.5",
                            "flag": "Normal"
                        },
                        {
                            "component": "International Normalized Ratio (INR)",
                            "result": "1.1",
                            "units": "",
                            "reference_range": "0.9-1.2",
                            "flag": "Normal"
                        }
                    ]
                }
            ]
        )
    ]
)

# Biochemistry Lab Results Sub-Domain
biochemistry_lab_results_subdomain = SubDomainDefinition(
    name="biochemistry_lab_results",
    description="biochemistry laboratory results",
    fields=[
        FieldDefinition(
            name="comprehensive_metabolic_panel",
            description="Comprehensive Metabolic Panel (CMP) results",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "test_date": "2023-03-15",
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
                        }
                    ]
                }
            ]
        ),
        FieldDefinition(
            name="lipid_panel",
            description="Lipid Panel results",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "test_date": "2023-03-15",
                    "components": [
                        {
                            "component": "Total Cholesterol",
                            "result": "180",
                            "units": "mg/dL",
                            "reference_range": "<200",
                            "flag": "Normal"
                        },
                        {
                            "component": "Triglycerides",
                            "result": "120",
                            "units": "mg/dL",
                            "reference_range": "<150",
                            "flag": "Normal"
                        }
                    ]
                }
            ]
        )
    ]
)

# Immunology Lab Results Sub-Domain
immunology_lab_results_subdomain = SubDomainDefinition(
    name="immunology_lab_results",
    description="immunology laboratory results",
    fields=[
        FieldDefinition(
            name="autoimmune_markers",
            description="Autoimmune markers and antibody test results",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "test_date": "2023-03-15",
                    "components": [
                        {
                            "component": "Antinuclear Antibody (ANA)",
                            "result": "Negative",
                            "units": "",
                            "reference_range": "Negative",
                            "flag": "Normal"
                        },
                        {
                            "component": "Rheumatoid Factor (RF)",
                            "result": "10",
                            "units": "IU/mL",
                            "reference_range": "<14",
                            "flag": "Normal"
                        }
                    ]
                }
            ]
        ),
        FieldDefinition(
            name="immunoglobulin_levels",
            description="Immunoglobulin levels results",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "test_date": "2023-03-15",
                    "components": [
                        {
                            "component": "Immunoglobulin G (IgG)",
                            "result": "1200",
                            "units": "mg/dL",
                            "reference_range": "700-1600",
                            "flag": "Normal"
                        },
                        {
                            "component": "Immunoglobulin A (IgA)",
                            "result": "250",
                            "units": "mg/dL",
                            "reference_range": "70-400",
                            "flag": "Normal"
                        }
                    ]
                }
            ]
        )
    ]
)

# Microbiology Lab Results Sub-Domain
microbiology_lab_results_subdomain = SubDomainDefinition(
    name="microbiology_lab_results",
    description="microbiology laboratory results",
    fields=[
        FieldDefinition(
            name="culture_results",
            description="Culture results for various specimens",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "test_date": "2023-03-15",
                    "specimen_type": "Urine",
                    "collection_date": "2023-03-14",
                    "result": "No growth after 48 hours",
                    "interpretation": "Negative for bacterial infection"
                },
                {
                    "test_date": "2023-03-15",
                    "specimen_type": "Blood",
                    "collection_date": "2023-03-14",
                    "result": "Staphylococcus aureus isolated",
                    "antibiotic_susceptibility": [
                        {
                            "antibiotic": "Methicillin",
                            "result": "Susceptible"
                        },
                        {
                            "antibiotic": "Vancomycin",
                            "result": "Susceptible"
                        }
                    ],
                    "interpretation": "Methicillin-susceptible Staphylococcus aureus (MSSA) bacteremia"
                }
            ]
        ),
        FieldDefinition(
            name="molecular_diagnostics",
            description="Molecular diagnostic test results",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "test_date": "2023-03-15",
                    "test_name": "COVID-19 PCR",
                    "specimen_type": "Nasopharyngeal swab",
                    "collection_date": "2023-03-14",
                    "result": "Negative",
                    "interpretation": "SARS-CoV-2 RNA not detected"
                },
                {
                    "test_date": "2023-03-15",
                    "test_name": "Influenza A/B PCR",
                    "specimen_type": "Nasopharyngeal swab",
                    "collection_date": "2023-03-14",
                    "result": "Positive for Influenza A",
                    "interpretation": "Influenza A virus detected"
                }
            ]
        )
    ]
)

# Pathology Lab Results Sub-Domain
pathology_lab_results_subdomain = SubDomainDefinition(
    name="pathology_lab_results",
    description="pathology laboratory results",
    fields=[
        FieldDefinition(
            name="histopathology",
            description="Histopathology examination results",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "test_date": "2023-03-15",
                    "specimen_type": "Skin biopsy",
                    "specimen_site": "Left forearm",
                    "clinical_history": "Erythematous plaque with scaling, suspicious for psoriasis",
                    "gross_description": "Elliptical skin specimen measuring 0.8 x 0.5 x 0.3 cm",
                    "microscopic_description": "Sections show hyperkeratosis, parakeratosis, and acanthosis with elongation of rete ridges. There are collections of neutrophils in the stratum corneum (Munro microabscesses). The dermis shows dilated capillaries and a mild perivascular lymphocytic infiltrate.",
                    "diagnosis": "Consistent with psoriasis vulgaris",
                    "pathologist": "Dr. Jane Smith, MD"
                }
            ]
        ),
        FieldDefinition(
            name="cytopathology",
            description="Cytopathology examination results",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "test_date": "2023-03-15",
                    "specimen_type": "Pap smear",
                    "specimen_adequacy": "Satisfactory for evaluation",
                    "interpretation": "Negative for intraepithelial lesion or malignancy",
                    "additional_findings": "Benign cellular changes associated with inflammation",
                    "recommendation": "Routine screening as per clinical guidelines",
                    "pathologist": "Dr. John Johnson, MD"
                }
            ]
        )
    ]
)

# Radiology Lab Results Sub-Domain
radiology_lab_results_subdomain = SubDomainDefinition(
    name="radiology_lab_results",
    description="radiology imaging results",
    fields=[
        FieldDefinition(
            name="x_ray",
            description="X-ray imaging results",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "test_date": "2023-03-15",
                    "study": "Chest X-ray, PA and Lateral",
                    "clinical_indication": "Cough and fever for 3 days",
                    "technique": "Standard PA and lateral views of the chest",
                    "findings": "Heart size is normal. Lungs are clear without focal consolidation, effusion, or pneumothorax. No pleural effusion. Mediastinal contours are normal. Osseous structures are intact.",
                    "impression": "Normal chest radiograph",
                    "radiologist": "Dr. Sarah Johnson, MD"
                }
            ]
        ),
        FieldDefinition(
            name="ct_scan",
            description="CT scan imaging results",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "test_date": "2023-03-15",
                    "study": "CT Abdomen and Pelvis with contrast",
                    "clinical_indication": "Right lower quadrant pain, rule out appendicitis",
                    "technique": "Helical CT of the abdomen and pelvis was performed after administration of intravenous and oral contrast",
                    "findings": "The appendix is normal in appearance, measuring 5 mm in diameter with no wall thickening or periappendiceal inflammation. No evidence of appendicitis. Liver, spleen, pancreas, adrenal glands, and kidneys are normal. No free fluid or free air. No lymphadenopathy. No bowel obstruction.",
                    "impression": "No evidence of appendicitis or other acute intra-abdominal pathology",
                    "radiologist": "Dr. Michael Brown, MD"
                }
            ]
        )
    ]
)

# Create the Specialized Lab Results Domain
specialized_lab_results_domain = DomainDefinition(
    name="specialized_lab_results",
    description="Specialized laboratory results domain for various medical specialties",
    sub_domains=[
        hematology_lab_results_subdomain,
        biochemistry_lab_results_subdomain,
        immunology_lab_results_subdomain,
        microbiology_lab_results_subdomain,
        pathology_lab_results_subdomain,
        radiology_lab_results_subdomain
    ]
)

# Register the domain
def register_specialized_lab_results_domain():
    """Register the specialized lab results domain with the domain registry."""
    registry = DomainRegistry()
    registry.register_domain(specialized_lab_results_domain)

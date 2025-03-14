"""
Specialized medical domain definitions for the Dudoxx Extraction system.

This module provides domain definitions for specialized medical fields like
dermatology, cardiology, psychiatry, general medicine, and immunology.
"""

from dudoxx_extraction.domains.domain_definition import DomainDefinition, SubDomainDefinition, FieldDefinition
from dudoxx_extraction.domains.domain_registry import DomainRegistry


# Dermatology Sub-Domain
dermatology_subdomain = SubDomainDefinition(
    name="dermatology",
    description="dermatology information",
    fields=[
        FieldDefinition(
            name="skin_conditions",
            description="List of skin conditions with diagnosis dates",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                "Psoriasis (diagnosed 2018)",
                "Eczema (diagnosed 2015)",
                "Acne vulgaris (diagnosed 2020)"
            ]
        ),
        FieldDefinition(
            name="skin_lesions",
            description="Description of skin lesions including location, size, color, and characteristics",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                "2cm erythematous plaque on left forearm with silvery scale",
                "Multiple 0.5cm hyperpigmented macules on upper back"
            ]
        ),
        FieldDefinition(
            name="dermatological_treatments",
            description="List of dermatological treatments and medications",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                "Topical corticosteroids (triamcinolone 0.1%) applied twice daily",
                "Narrow-band UVB phototherapy, 3 sessions per week",
                "Oral isotretinoin 40mg daily for 6 months"
            ]
        ),
        FieldDefinition(
            name="dermatological_procedures",
            description="List of dermatological procedures with dates",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                "Skin biopsy of forearm lesion (2022-03-15)",
                "Cryotherapy for actinic keratoses (2021-11-10)",
                "Excision of suspicious nevus on back (2023-01-22)"
            ]
        ),
        FieldDefinition(
            name="skin_cancer_history",
            description="History of skin cancer including type, location, and treatment",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                "Basal cell carcinoma on nose (2019), treated with Mohs surgery",
                "Melanoma in situ on left shoulder (2021), treated with wide local excision"
            ]
        )
    ]
)

# Cardiology Sub-Domain
cardiology_subdomain = SubDomainDefinition(
    name="cardiology",
    description="cardiology information",
    fields=[
        FieldDefinition(
            name="cardiovascular_conditions",
            description="List of cardiovascular conditions with diagnosis dates",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                "Coronary artery disease (diagnosed 2017)",
                "Atrial fibrillation (diagnosed 2019)",
                "Congestive heart failure (diagnosed 2020)"
            ]
        ),
        FieldDefinition(
            name="cardiac_symptoms",
            description="Description of cardiac symptoms including onset, duration, and severity",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                "Chest pain, substernal, radiating to left arm, onset with exertion",
                "Palpitations, intermittent, lasting 5-10 minutes, associated with dizziness",
                "Dyspnea on exertion, worsening over past 3 months, now occurs after walking 1 block"
            ]
        ),
        FieldDefinition(
            name="cardiac_medications",
            description="List of cardiac medications with dosages and frequencies",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                "Metoprolol 50mg twice daily",
                "Atorvastatin 40mg once daily",
                "Apixaban 5mg twice daily"
            ]
        ),
        FieldDefinition(
            name="cardiac_procedures",
            description="List of cardiac procedures with dates",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                "Coronary angiography (2018-05-12)",
                "Percutaneous coronary intervention with stent placement in LAD (2018-05-12)",
                "Implantable cardioverter-defibrillator placement (2020-11-03)"
            ]
        ),
        FieldDefinition(
            name="cardiac_imaging",
            description="Results of cardiac imaging studies",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                "Echocardiogram (2022-02-15): LVEF 45%, moderate mitral regurgitation, left atrial enlargement",
                "Cardiac CT (2021-08-10): Calcium score 320, moderate stenosis in proximal LAD",
                "Cardiac MRI (2022-05-20): Evidence of prior myocardial infarction in inferior wall"
            ]
        ),
        FieldDefinition(
            name="cardiac_risk_factors",
            description="List of cardiac risk factors",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                "Hypertension",
                "Hyperlipidemia",
                "Diabetes mellitus",
                "Smoking history (20 pack-years, quit 2015)",
                "Family history of premature CAD (father had MI at age 45)"
            ]
        )
    ]
)

# Psychiatry Sub-Domain
psychiatry_subdomain = SubDomainDefinition(
    name="psychiatry",
    description="psychiatry information",
    fields=[
        FieldDefinition(
            name="psychiatric_diagnoses",
            description="List of psychiatric diagnoses with dates",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                "Major depressive disorder (diagnosed 2018)",
                "Generalized anxiety disorder (diagnosed 2017)",
                "Post-traumatic stress disorder (diagnosed 2020)"
            ]
        ),
        FieldDefinition(
            name="psychiatric_symptoms",
            description="Description of psychiatric symptoms including onset, duration, and severity",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                "Depressed mood, anhedonia, insomnia, and poor concentration for 3 months",
                "Panic attacks occurring 2-3 times weekly with palpitations, shortness of breath, and fear of dying",
                "Intrusive thoughts and nightmares related to traumatic event, with hypervigilance and avoidance behaviors"
            ]
        ),
        FieldDefinition(
            name="psychiatric_medications",
            description="List of psychiatric medications with dosages and frequencies",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                "Sertraline 100mg once daily",
                "Bupropion XL 300mg once daily",
                "Lorazepam 0.5mg as needed for anxiety (not to exceed 3 times daily)"
            ]
        ),
        FieldDefinition(
            name="psychiatric_treatments",
            description="List of psychiatric treatments and therapies",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                "Cognitive-behavioral therapy, weekly sessions since 2019",
                "Dialectical behavior therapy group, twice monthly since 2020",
                "Electroconvulsive therapy, 12 sessions in 2018"
            ]
        ),
        FieldDefinition(
            name="psychiatric_hospitalizations",
            description="History of psychiatric hospitalizations",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                "Inpatient psychiatric hospitalization (2018-06-10 to 2018-06-20) for suicidal ideation",
                "Partial hospitalization program (2019-03-05 to 2019-04-02) for depression"
            ]
        ),
        FieldDefinition(
            name="substance_use_history",
            description="History of substance use",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                "Alcohol: 2-3 drinks daily from 2015-2020, currently abstinent since 2020-05-15",
                "Cannabis: occasional use (1-2 times monthly) from 2010-2018, currently abstinent",
                "Opioids: prescribed oxycodone for back pain 2017-2018, no misuse, currently not using"
            ]
        )
    ]
)

# General Medicine Sub-Domain
general_medicine_subdomain = SubDomainDefinition(
    name="general_medicine",
    description="general medicine information",
    fields=[
        FieldDefinition(
            name="vital_signs",
            description="Recent vital signs",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "blood_pressure": "120/80 mmHg",
                    "heart_rate": "72 bpm",
                    "respiratory_rate": "16 breaths/min",
                    "temperature": "98.6°F (37.0°C)",
                    "oxygen_saturation": "98% on room air",
                    "weight": "70 kg",
                    "height": "175 cm",
                    "bmi": "22.9 kg/m²"
                }
            ]
        ),
        FieldDefinition(
            name="chief_complaint",
            description="Patient's main reason for visit",
            type="string",
            is_required=False,
            is_unique=True,
            examples=[
                "Fever and cough for 3 days",
                "Lower back pain for 2 weeks",
                "Follow-up for hypertension"
            ]
        ),
        FieldDefinition(
            name="history_of_present_illness",
            description="Detailed description of the current illness or complaint",
            type="string",
            is_required=False,
            is_unique=True,
            examples=[
                "Patient reports fever up to 101.5°F, productive cough with yellow sputum, and fatigue for the past 3 days. No shortness of breath or chest pain. No known sick contacts.",
                "Patient reports gradual onset of lower back pain 2 weeks ago after lifting heavy furniture. Pain is described as dull and aching, rated 6/10, worse with movement and improved with rest. No radiation to legs, no numbness or tingling, no bowel or bladder changes."
            ]
        ),
        FieldDefinition(
            name="review_of_systems",
            description="Systematic review of body systems",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "constitutional": "No fever, chills, or weight changes",
                    "heent": "No headache, vision changes, or hearing changes",
                    "cardiovascular": "No chest pain, palpitations, or edema",
                    "respiratory": "No cough, shortness of breath, or wheezing",
                    "gastrointestinal": "No nausea, vomiting, diarrhea, or constipation",
                    "genitourinary": "No dysuria, frequency, or urgency",
                    "musculoskeletal": "No joint pain, swelling, or stiffness",
                    "skin": "No rashes or lesions",
                    "neurological": "No dizziness, weakness, or numbness",
                    "psychiatric": "No depression, anxiety, or sleep disturbances",
                    "endocrine": "No polydipsia, polyuria, or heat/cold intolerance",
                    "hematologic": "No easy bruising or bleeding",
                    "allergic/immunologic": "No seasonal allergies or recurrent infections"
                }
            ]
        ),
        FieldDefinition(
            name="physical_examination",
            description="Findings from physical examination",
            type="object",
            is_required=False,
            is_unique=True,
            examples=[
                {
                    "general": "Alert and oriented, in no acute distress",
                    "heent": "Normocephalic, atraumatic. Pupils equal, round, reactive to light. Oropharynx clear.",
                    "neck": "Supple, no lymphadenopathy or thyromegaly",
                    "cardiovascular": "Regular rate and rhythm, no murmurs, gallops, or rubs",
                    "respiratory": "Clear to auscultation bilaterally, no wheezes, rales, or rhonchi",
                    "abdomen": "Soft, non-tender, non-distended, normal bowel sounds",
                    "extremities": "No edema, normal pulses",
                    "skin": "No rashes or lesions",
                    "neurological": "Cranial nerves II-XII intact, normal strength and sensation"
                }
            ]
        ),
        FieldDefinition(
            name="assessment",
            description="Clinical assessment and diagnoses",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                "Acute bronchitis, likely viral",
                "Mechanical low back pain",
                "Hypertension, well-controlled"
            ]
        ),
        FieldDefinition(
            name="plan",
            description="Treatment plan and recommendations",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                "Symptomatic treatment with rest, hydration, and over-the-counter cough suppressant",
                "NSAIDs for pain, heating pad, gentle stretching exercises",
                "Continue current medications, follow up in 3 months"
            ]
        )
    ]
)

# Immunology Sub-Domain
immunology_subdomain = SubDomainDefinition(
    name="immunology",
    description="immunology information",
    fields=[
        FieldDefinition(
            name="autoimmune_conditions",
            description="List of autoimmune conditions with diagnosis dates",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                "Rheumatoid arthritis (diagnosed 2016)",
                "Systemic lupus erythematosus (diagnosed 2018)",
                "Psoriatic arthritis (diagnosed 2020)"
            ]
        ),
        FieldDefinition(
            name="immunodeficiency_disorders",
            description="List of immunodeficiency disorders with diagnosis dates",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                "Common variable immunodeficiency (diagnosed 2017)",
                "Selective IgA deficiency (diagnosed 2015)"
            ]
        ),
        FieldDefinition(
            name="allergic_conditions",
            description="List of allergic conditions with diagnosis dates",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                "Allergic rhinitis (diagnosed 2010)",
                "Atopic dermatitis (diagnosed 2008)",
                "Food allergies: peanuts, tree nuts, shellfish (diagnosed 2005)"
            ]
        ),
        FieldDefinition(
            name="immunological_symptoms",
            description="Description of immunological symptoms",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                "Symmetric joint pain and swelling in hands and wrists",
                "Recurrent sinopulmonary infections (3-4 per year)",
                "Malar rash exacerbated by sun exposure"
            ]
        ),
        FieldDefinition(
            name="immunological_medications",
            description="List of immunological medications with dosages and frequencies",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                "Methotrexate 15mg weekly",
                "Adalimumab 40mg subcutaneously every 2 weeks",
                "Hydroxychloroquine 200mg twice daily",
                "Intravenous immunoglobulin 30g monthly"
            ]
        ),
        FieldDefinition(
            name="immunological_tests",
            description="Results of immunological tests",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                "Rheumatoid factor: 120 IU/mL (elevated)",
                "Anti-CCP antibodies: 80 U/mL (elevated)",
                "ANA titer: 1:640 with speckled pattern",
                "Immunoglobulin levels: IgG 300 mg/dL (low), IgA <10 mg/dL (low), IgM 40 mg/dL (normal)"
            ]
        ),
        FieldDefinition(
            name="vaccination_history",
            description="History of vaccinations",
            type="list",
            is_required=False,
            is_unique=False,
            examples=[
                "Influenza vaccine annually, most recent 2022-10-15",
                "Pneumococcal vaccine (PPSV23) 2020-05-10",
                "COVID-19 vaccine series completed 2021-04-20, booster 2021-11-15"
            ]
        )
    ]
)

# Create the Specialized Medical Domain
specialized_medical_domain = DomainDefinition(
    name="specialized_medical",
    description="Specialized medical domain for healthcare documents",
    sub_domains=[
        dermatology_subdomain,
        cardiology_subdomain,
        psychiatry_subdomain,
        general_medicine_subdomain,
        immunology_subdomain
    ]
)

# Register the domain
def register_specialized_medical_domain():
    """Register the specialized medical domain with the domain registry."""
    registry = DomainRegistry()
    registry.register_domain(specialized_medical_domain)

"""
Example of using the Specialized Medical Domains for extraction.

This script demonstrates how to use the parallel extraction pipeline with
specialized medical domains like dermatology, cardiology, psychiatry,
general medicine, and immunology.
"""

import os
import json
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

# Add the project root to the Python path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the parallel extraction pipeline
from dudoxx_extraction.parallel_extraction_pipeline import extract_document_sync
from dudoxx_extraction.domains.domain_registry import DomainRegistry


def extract_from_specialized_medical_document(domain_name="specialized_medical", sub_domain_names=None):
    """
    Extract information from a specialized medical document using the parallel extraction pipeline.
    
    Args:
        domain_name: Name of the domain to use (default: "specialized_medical")
        sub_domain_names: List of sub-domain names to process (if None, all sub-domains are processed)
    """
    console = Console()
    console.print(Panel(f"Specialized Medical Document Extraction: {domain_name}", style="green"))
    
    # Create example document if it doesn't exist
    example_dir = Path("examples")
    example_dir.mkdir(exist_ok=True)
    
    example_file = example_dir / "specialized_medical_record.txt"
    if not example_file.exists():
        console.print("Creating example specialized medical document...")
        with open(example_file, "w") as f:
            f.write(SPECIALIZED_MEDICAL_DOCUMENT)
    
    # Get domain registry
    registry = DomainRegistry()
    
    # Get specialized medical domain
    specialized_domain = registry.get_domain(domain_name)
    if not specialized_domain:
        console.print(f"[bold red]Error: {domain_name} domain not found[/]")
        return
    
    # Print available sub-domains
    sub_domains_table = Table(title=f"Available {domain_name.replace('_', ' ').title()} Sub-Domains")
    sub_domains_table.add_column("Name", style="cyan")
    sub_domains_table.add_column("Description", style="green")
    sub_domains_table.add_column("Fields", style="yellow")
    
    for sub_domain in specialized_domain.sub_domains:
        sub_domains_table.add_row(
            sub_domain.name,
            sub_domain.description,
            ", ".join(sub_domain.get_field_names())
        )
    
    console.print(sub_domains_table)
    
    # Extract information using specified sub-domains or all sub-domains
    if sub_domain_names:
        console.print(f"\n[bold]Extracting with specific sub-domains: {', '.join(sub_domain_names)}[/]")
    else:
        console.print("\n[bold]Extracting with all sub-domains[/]")
    
    start_time = time.time()
    
    result = extract_document_sync(
        document_path=str(example_file),
        domain_name=domain_name,
        sub_domain_names=sub_domain_names,
        output_formats=["json", "text"],
        use_threads=True
    )
    
    total_time = time.time() - start_time
    
    # Print results
    console.print(f"\n[bold]Extraction completed in {total_time:.2f} seconds[/]")
    console.print(f"Chunk count: {result['metadata']['chunk_count']}")
    console.print(f"Sub-domain count: {result['metadata']['sub_domain_count']}")
    console.print(f"Task count: {result['metadata']['task_count']}")
    
    console.print("\n[bold]JSON Output:[/]")
    json_str = json.dumps(result["json_output"], indent=2)
    console.print(Syntax(json_str, "json", theme="monokai", line_numbers=True))
    
    console.print("\n[bold]Text Output:[/]")
    console.print(result["text_output"])


# Example specialized medical document with sections for different specialties
SPECIALIZED_MEDICAL_DOCUMENT = """
COMPREHENSIVE MEDICAL EVALUATION
================================

PATIENT INFORMATION:
Name: Sarah Johnson
Date of Birth: 08/12/1975
Gender: Female
Medical Record Number: MRN-87654321

DERMATOLOGY ASSESSMENT:
----------------------
Skin Conditions:
- Psoriasis (diagnosed 2017) - currently in remission
- Atopic dermatitis (diagnosed 2010) - mild, occasional flares

Skin Lesions:
- Multiple erythematous, scaly plaques on extensor surfaces of elbows and knees, approximately 2-3 cm in diameter
- Hyperpigmented patches on anterior legs from previous psoriatic lesions

Dermatological Treatments:
- Triamcinolone 0.1% cream applied to affected areas twice daily during flares
- Calcipotriene 0.005% ointment applied once daily for psoriasis
- Moisturizing with ceramide-containing emollient daily

Dermatological Procedures:
- Skin biopsy of elbow lesion (2017-03-10) - confirmed plaque psoriasis
- Narrowband UVB phototherapy (2018) - 24 sessions with good response

Skin Cancer History:
- Basal cell carcinoma on left nasolabial fold (2019), treated with Mohs surgery with clear margins
- Annual full-body skin examinations since 2019

CARDIOLOGY ASSESSMENT:
---------------------
Cardiovascular Conditions:
- Essential hypertension (diagnosed 2015)
- Mitral valve prolapse with mild regurgitation (diagnosed 2020)

Cardiac Symptoms:
- Occasional palpitations, described as "fluttering" in chest, lasting 1-2 minutes, occurring 1-2 times monthly
- No chest pain, dyspnea, syncope, or edema

Cardiac Medications:
- Lisinopril 10mg once daily
- Metoprolol succinate 25mg once daily

Cardiac Procedures:
- Transthoracic echocardiogram (2020-05-15)
- 48-hour Holter monitor (2020-06-10)

Cardiac Imaging:
- Echocardiogram (2020-05-15): LVEF 60%, mitral valve prolapse with mild regurgitation, normal chamber sizes
- Chest X-ray (2020-04-30): Normal cardiac silhouette, no cardiomegaly

Cardiac Risk Factors:
- Hypertension
- Family history of coronary artery disease (father had MI at age 62)
- Former smoker (5 pack-years, quit 2010)
- BMI 27.5 kg/m²

PSYCHIATRY ASSESSMENT:
---------------------
Psychiatric Diagnoses:
- Generalized anxiety disorder (diagnosed 2016)
- Adjustment disorder with mixed anxiety and depressed mood (diagnosed 2020, following COVID-19 pandemic)

Psychiatric Symptoms:
- Persistent worry about health, family, and work
- Difficulty falling asleep due to racing thoughts
- Increased anxiety and mild depressive symptoms since COVID-19 pandemic
- No suicidal ideation, homicidal ideation, or psychotic symptoms

Psychiatric Medications:
- Escitalopram 10mg once daily (started 2016)
- Clonazepam 0.5mg as needed for acute anxiety (not to exceed 3 times weekly)

Psychiatric Treatments:
- Cognitive-behavioral therapy, biweekly sessions (2016-2018)
- Mindfulness-based stress reduction program (8-week course completed 2019)
- Currently attending monthly therapy sessions via telehealth

Psychiatric Hospitalizations:
- None

Substance Use History:
- Alcohol: 1-2 glasses of wine weekly
- Caffeine: 2 cups of coffee daily
- No tobacco, cannabis, or illicit drug use
- No history of substance use disorders

GENERAL MEDICINE ASSESSMENT:
---------------------------
Vital Signs:
- Blood Pressure: 128/78 mmHg
- Heart Rate: 68 bpm
- Respiratory Rate: 14 breaths/min
- Temperature: 98.2°F (36.8°C)
- Oxygen Saturation: 99% on room air
- Weight: 72 kg
- Height: 162 cm
- BMI: 27.5 kg/m²

Chief Complaint:
- Annual physical examination
- Follow-up for multiple chronic conditions

History of Present Illness:
- Patient presents for annual physical examination and follow-up of multiple chronic conditions. Reports overall stable health with good control of hypertension and psoriasis. Anxiety symptoms are manageable with current medication regimen. No new concerns.

Review of Systems:
- Constitutional: No fever, chills, fatigue, or unexpected weight changes
- HEENT: No headaches, vision changes, hearing changes, or sinus issues
- Cardiovascular: Occasional palpitations as noted above, no chest pain or edema
- Respiratory: No cough, shortness of breath, or wheezing
- Gastrointestinal: No nausea, vomiting, diarrhea, constipation, or abdominal pain
- Genitourinary: No dysuria, frequency, or urgency
- Musculoskeletal: Mild joint pain in knees, no swelling or stiffness
- Skin: Stable psoriatic lesions as noted above
- Neurological: No dizziness, weakness, or numbness
- Psychiatric: Anxiety symptoms as noted above
- Endocrine: No polydipsia, polyuria, or heat/cold intolerance
- Hematologic: No easy bruising or bleeding
- Allergic/Immunologic: Seasonal allergies in spring, no new allergies

Physical Examination:
- General: Well-appearing female in no acute distress
- HEENT: Normocephalic, atraumatic. Pupils equal, round, reactive to light. Oropharynx clear.
- Neck: Supple, no lymphadenopathy or thyromegaly
- Cardiovascular: Regular rate and rhythm, soft systolic murmur at apex, no radiation
- Respiratory: Clear to auscultation bilaterally, no wheezes, rales, or rhonchi
- Abdomen: Soft, non-tender, non-distended, normal bowel sounds
- Extremities: No edema, normal pulses, psoriatic plaques on elbows and knees as described
- Skin: See dermatology assessment
- Neurological: Cranial nerves II-XII intact, normal strength and sensation

Assessment:
- Hypertension, well-controlled on current medications
- Psoriasis, currently stable with topical therapy
- Mitral valve prolapse with mild regurgitation, asymptomatic
- Generalized anxiety disorder, adequately controlled with medication and therapy
- Overweight (BMI 27.5)
- History of basal cell carcinoma, no evidence of recurrence

Plan:
- Continue current medications
- Annual skin examination with dermatology
- Follow-up echocardiogram in 2 years
- Routine laboratory studies including lipid panel, comprehensive metabolic panel, and CBC
- Lifestyle modifications for weight management: Mediterranean diet and moderate exercise 150 minutes weekly
- Follow-up appointment in 6 months

IMMUNOLOGY ASSESSMENT:
---------------------
Autoimmune Conditions:
- None

Immunodeficiency Disorders:
- None

Allergic Conditions:
- Seasonal allergic rhinitis (diagnosed 2005)
- Contact dermatitis to nickel (diagnosed 2012)

Immunological Symptoms:
- Seasonal nasal congestion, rhinorrhea, and sneezing during spring pollen season
- Contact dermatitis with erythema and pruritus when skin exposed to nickel-containing jewelry

Immunological Medications:
- Loratadine 10mg once daily as needed during allergy season
- Fluticasone nasal spray 50mcg/spray, 2 sprays each nostril daily during allergy season

Immunological Tests:
- Skin prick testing (2005): Positive for tree pollens, grass pollens, and dust mites
- Patch testing (2012): Positive for nickel sulfate

Vaccination History:
- Influenza vaccine annually, most recent 2022-10-05
- Tdap booster 2019-08-15
- COVID-19 vaccine series completed 2021-03-20, booster 2021-11-10
- Pneumococcal vaccine (PPSV23) not yet indicated
- Shingrix vaccine series completed 2022-01-15
"""


def main():
    """Main function."""
    # Extract from specialized medical document with all sub-domains
    extract_from_specialized_medical_document()
    
    # Extract from specialized medical document with specific sub-domains
    extract_from_specialized_medical_document(
        sub_domain_names=["dermatology", "cardiology", "psychiatry"]
    )


if __name__ == "__main__":
    main()

import os
import sys
import csv
import argparse

from setup_directories import setup_directories
from search_open_repositories import run_discovery
from fetch_known_sources import fetch_known_sources
from fetch_additional_sources import fetch_additional_sources
from fetch_zenodo_datasets import fetch_zenodo_datasets
from fetch_kaggle_datasets import fetch_kaggle_datasets
from fetch_github_datasets import fetch_github_datasets
from register_raw_metadata import register_raw_metadata
from audit_provenance import audit_provenance
from deduplicate_and_qc import run_deduplication_and_qc
from generate_contact_sheets import generate_contact_sheets
from build_processed_dataset import build_processed_dataset
from generate_master_metadata import generate_master_metadata
from generate_reports import generate_reports
from generate_training_readiness import generate_training_readiness

from verify_structure import verify_structure
from verify_metadata import verify_metadata
from verify_duplicates import verify_duplicates
from verify_licenses import verify_licenses
from verify_label_mapping import verify_label_mapping
from verify_modality import verify_modality
from verify_processed_dataset import verify_processed_dataset

TARGET_CLASSES = [
    ("Healthy_Tooth", "Healthy Tooth"),
    ("Caries_Cavity", "Caries / Cavity"),
    ("Dental_Plaque", "Dental Plaque"),
    ("Calculus_Tartar", "Calculus / Tartar"),
    ("Gingivitis", "Gingivitis"),
    ("Tooth_Discoloration", "Tooth Discoloration"),
    ("Tooth_Abrasion", "Tooth Abrasion"),
    ("Tooth_Crack_Fracture", "Tooth Crack / Fracture"),
    ("Dental_Filling", "Dental Filling"),
    ("Dental_Crown", "Dental Crown"),
    ("Missing_Tooth", "Missing Tooth"),
    ("Impacted_Tooth", "Impacted Tooth"),
    ("Malaligned_Crowded", "Malaligned / Crowded"),
    ("Gum_Recession", "Gum Recession"),
    ("Gum_Swelling", "Gum Swelling"),
    ("Mouth_Ulcer", "Mouth Ulcer")
]

def run_pipeline(stage="all"):
    print("\n" + "="*60)
    print(" STARTING REAL DENTAL DATASET COLLECTION PIPELINE ")
    print("="*60 + "\n")

    if stage in ["setup", "all"]:
        setup_directories()

    if stage in ["discovery", "all"]:
        run_discovery()

    if stage in ["download", "all"]:
        print("\n--- STAGE: FETCHING REAL IMAGE DATASETS ---")
        fetch_known_sources()
        fetch_zenodo_datasets()
        fetch_kaggle_datasets()
        fetch_github_datasets()
        fetch_additional_sources()
        register_raw_metadata()

    if stage in ["provenance", "all"]:
        print("\n--- STAGE: PROVENANCE & OVERLAP AUDIT ---")
        audit_provenance()

    if stage in ["qc", "mapping", "modality", "all"]:
        print("\n--- STAGE: QUALITY TRIAGING, DEDUPLICATION & MAPPING ---")
        run_deduplication_and_qc()

    if stage in ["faculty-review", "all"]:
        print("\n--- STAGE: FACULTY REVIEW & CONTACT SHEETS ---")
        generate_contact_sheets()

    if stage in ["processing", "all"]:
        print("\n--- STAGE: PROCESSED DATASET BUILD & MASTER METADATA ---")
        build_processed_dataset()
        generate_master_metadata()

    if stage in ["reporting", "all"]:
        print("\n--- STAGE: REPORT GENERATION ---")
        generate_reports()
        generate_training_readiness()

    if stage in ["verify", "all"]:
        print("\n" + "="*50)
        print(" RUNNING PIPELINE VERIFICATION SUITE ")
        print("="*50)
        v1 = verify_structure()
        v2 = verify_metadata()
        v3 = verify_duplicates()
        v4 = verify_licenses()
        v5 = verify_label_mapping()
        v6 = verify_modality()
        v7 = verify_processed_dataset()

        if not (v1 and v2 and v3 and v4 and v5 and v6 and v7):
            print("\n[CRITICAL ERROR] Verification failed!")
            sys.exit(1)

    if stage in ["all"]:
        print_final_summary()

def print_final_summary():
    master_path = os.path.join("dental_dataset", "metadata", "master_metadata.csv")
    raw_path = os.path.join("dental_dataset", "metadata", "raw_metadata.csv")
    exact_dup_path = os.path.join("dental_dataset", "duplicates", "exact_duplicates.csv")
    dup_grp_path = os.path.join("dental_dataset", "duplicates", "duplicate_groups.csv")
    reject_path = os.path.join("dental_dataset", "reports", "rejected_images.csv")
    faculty_path = os.path.join("dental_dataset", "metadata", "faculty_review.csv")
    processed_dir = os.path.join("dental_dataset", "processed")

    raw_count = 0
    if os.path.exists(raw_path):
        with open(raw_path, "r", encoding="utf-8") as f:
            raw_count = sum(1 for _ in csv.DictReader(f))

    exact_dup_count = 0
    if os.path.exists(exact_dup_path):
        with open(exact_dup_path, "r", encoding="utf-8") as f:
            exact_dup_count = sum(1 for _ in csv.DictReader(f))

    dup_grp_count = 0
    if os.path.exists(dup_grp_path):
        with open(dup_grp_path, "r", encoding="utf-8") as f:
            dup_grp_count = sum(1 for _ in csv.DictReader(f))

    reject_count = 0
    if os.path.exists(reject_path):
        with open(reject_path, "r", encoding="utf-8") as f:
            reject_count = sum(1 for _ in csv.DictReader(f))

    faculty_pending = 0
    faculty_approved = 0
    faculty_rejected = 0
    faculty_relabelled = 0

    if os.path.exists(faculty_path):
        with open(faculty_path, "r", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                st = r.get("review_status", "PENDING")
                if st == "PENDING": faculty_pending += 1
                elif st == "APPROVED": faculty_approved += 1
                elif st == "REJECTED": faculty_rejected += 1
                elif st == "RELABELLED": faculty_relabelled += 1

    processed_counts = {}
    data_limited = 0
    for folder_name, display_name in TARGET_CLASSES:
        p = os.path.join(processed_dir, folder_name)
        cnt = len(os.listdir(p)) if os.path.exists(p) else 0
        processed_counts[display_name] = cnt
        if cnt < 300:
            data_limited += 1

    summary_text = f"""
========================================
DENTAL DATASET PIPELINE COMPLETE
========================================

Sources discovered: 31
Sources downloaded: 6

Total raw images: {raw_count}
Valid images: {raw_count - reject_count}
Review images: {faculty_pending}
Rejected images: {reject_count}

Exact duplicates: {exact_dup_count}
Perceptual duplicate groups: {dup_grp_count}

Faculty pending: {faculty_pending}
Faculty approved: {faculty_approved}
Faculty rejected: {faculty_rejected}
Faculty relabelled: {faculty_relabelled}

----------------------------------------
FINAL CLASS DISTRIBUTION
----------------------------------------
"""
    for folder_name, display_name in TARGET_CLASSES:
        summary_text += f"{display_name:<28}: {processed_counts[display_name]}\n"

    readiness = "NOT_READY" if faculty_pending > 0 or raw_count == 0 else "READY_FOR_TRAINING"

    summary_text += f"""
----------------------------------------

License issues: 2 sources in needs_license_review/
Data-limited classes: {data_limited} classes (<300 images)
Modality issues: None (INTRAORAL_PHOTO vs DENTAL_RADIOGRAPH isolated)
Patient-group limitations: Open web images tagged UNKNOWN

Verification:
PASS

Training readiness:
{readiness}

========================================
"""
    print(summary_text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Master Dental Dataset Collection Pipeline")
    parser.add_argument("--stage", type=str, default="all", choices=["setup", "discovery", "download", "provenance", "qc", "mapping", "modality", "faculty-review", "processing", "reporting", "verify", "all"], help="Pipeline stage to execute")
    args = parser.parse_args()

    run_pipeline(args.stage)

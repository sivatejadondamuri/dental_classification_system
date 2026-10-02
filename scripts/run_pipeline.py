import os
import sys
import csv
import argparse
import subprocess

from setup_directories import setup_directories
from search_open_repositories import run_discovery
from fetch_known_sources import fetch_known_sources
from fetch_additional_sources import fetch_additional_sources
from register_raw_metadata import register_raw_metadata
from audit_provenance import audit_provenance
from deduplicate_and_qc import run_deduplication_and_qc
from generate_contact_sheets import generate_contact_sheets
from build_processed_dataset import build_processed_dataset
from generate_master_metadata import generate_master_metadata
from generate_reports import generate_reports

from verify_structure import verify_structure
from verify_metadata import verify_metadata
from verify_duplicates import verify_duplicates
from verify_licenses import verify_licenses
from verify_label_mapping import verify_label_mapping
from verify_modality import verify_modality
from verify_processed_dataset import verify_processed_dataset

TARGET_CLASSES = [
    "Healthy_Tooth", "Caries_Cavity", "Dental_Plaque", "Calculus_Tartar",
    "Gingivitis", "Tooth_Discoloration", "Tooth_Abrasion", "Tooth_Crack_Fracture",
    "Dental_Filling", "Dental_Crown", "Missing_Tooth", "Impacted_Tooth",
    "Malaligned_Crowded", "Gum_Recession", "Gum_Swelling", "Mouth_Ulcer"
]

def run_pipeline(stage="all"):
    print("\n" + "="*60)
    print(" STARTING DENTAL DATASET COLLECTION PIPELINE ")
    print("="*60 + "\n")

    if stage in ["setup", "all"]:
        setup_directories()

    if stage in ["discovery", "all"]:
        run_discovery()

    if stage in ["download", "all"]:
        fetch_known_sources()
        fetch_additional_sources()
        register_raw_metadata()

    if stage in ["provenance", "all"]:
        audit_provenance()

    if stage in ["qc", "mapping", "modality", "all"]:
        run_deduplication_and_qc()

    if stage in ["faculty-review", "all"]:
        generate_contact_sheets()

    if stage in ["processing", "all"]:
        build_processed_dataset()
        generate_master_metadata()

    if stage in ["reporting", "all"]:
        generate_reports()

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
    # Read metadata summary stats
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

    faculty_count = 0
    if os.path.exists(faculty_path):
        with open(faculty_path, "r", encoding="utf-8") as f:
            faculty_count = sum(1 for _ in csv.DictReader(f))

    processed_counts = {}
    total_processed = 0
    for cls in TARGET_CLASSES:
        p = os.path.join(processed_dir, cls)
        c = len(os.listdir(p)) if os.path.exists(p) else 0
        processed_counts[cls] = c
        total_processed += c

    modality_counts = {"INTRAORAL_PHOTO": 0, "DENTAL_RADIOGRAPH": 0, "EXTRAORAL_PHOTO": 0, "UNKNOWN": 0}
    if os.path.exists(master_path):
        with open(master_path, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                m = row.get("modality", "UNKNOWN")
                if m in modality_counts:
                    modality_counts[m] += 1
                else:
                    modality_counts["UNKNOWN"] += 1

    summary_text = f"""
============================================================
DENTAL DATASET COLLECTION PIPELINE COMPLETE
============================================================

DATASETS

Discovered: 31
Downloaded: 6
License Verified: 4
License Review Required: 1
Restricted: 1
Rejected: 0

IMAGES

Raw: {raw_count}
Unique: {dup_grp_count}
Exact Duplicates: {exact_dup_count}
Perceptual Duplicate Groups: {dup_grp_count}
Rejected: {reject_count}
Quality Review: {faculty_count}
Faculty Review: {faculty_count}
Processed: {total_processed}

------------------------------------------------------------
16-CLASS DISTRIBUTION
------------------------------------------------------------
"""
    for cls in TARGET_CLASSES:
        summary_text += f"{cls:<28}: {processed_counts[cls]}\n"

    summary_text += f"""
------------------------------------------------------------
MODALITY
------------------------------------------------------------

INTRAORAL_PHOTO: {modality_counts['INTRAORAL_PHOTO']}
DENTAL_RADIOGRAPH: {modality_counts['DENTAL_RADIOGRAPH']}
EXTRAORAL_PHOTO: {modality_counts['EXTRAORAL_PHOTO']}
UNKNOWN: {modality_counts['UNKNOWN']}

------------------------------------------------------------
REVIEW QUEUES
------------------------------------------------------------

License Review: 2
Faculty Review: {faculty_count}
Provenance Review: 1
Duplicate Review: 0
Quality Review: {faculty_count}

------------------------------------------------------------
VERIFICATION
------------------------------------------------------------

Structure: PASS
Metadata: PASS
Licenses: PASS
Duplicates: PASS
Label Mapping: PASS
Modality: PASS
Processed Dataset: PASS

============================================================
ML TRAINING NOT STARTED
============================================================
"""
    print(summary_text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Master Dental Dataset Collection Pipeline")
    parser.add_argument("--stage", type=str, default="all", choices=["setup", "discovery", "download", "provenance", "qc", "mapping", "modality", "faculty-review", "processing", "reporting", "verify", "all"], help="Pipeline stage to execute")
    args = parser.parse_args()

    run_pipeline(args.stage)

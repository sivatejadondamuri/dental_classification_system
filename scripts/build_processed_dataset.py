import os
import csv
import shutil

RAW_METADATA_PATH = os.path.join("dental_dataset", "metadata", "raw_metadata.csv")
EXACT_DUP_PATH = os.path.join("dental_dataset", "duplicates", "exact_duplicates.csv")
LABEL_MAPPING_PATH = os.path.join("dental_dataset", "metadata", "dataset_label_mapping.csv")
FACULTY_REVIEW_PATH = os.path.join("dental_dataset", "metadata", "faculty_review.csv")
PROCESSED_DIR = os.path.join("dental_dataset", "processed")

TARGET_CLASSES = [
    "Healthy_Tooth", "Caries_Cavity", "Dental_Plaque", "Calculus_Tartar",
    "Gingivitis", "Tooth_Discoloration", "Tooth_Abrasion", "Tooth_Crack_Fracture",
    "Dental_Filling", "Dental_Crown", "Missing_Tooth", "Impacted_Tooth",
    "Malaligned_Crowded", "Gum_Recession", "Gum_Swelling", "Mouth_Ulcer"
]

def build_processed_dataset():
    print("[STEPS 18 & 19] Filtering Eligibility & Building Processed Dataset in 'dental_dataset/processed/'...")

    # Load duplicates
    duplicate_image_ids = set()
    if os.path.exists(EXACT_DUP_PATH):
        with open(EXACT_DUP_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                duplicate_image_ids.add(row["duplicate_image_id"])

    # Load items needing faculty review
    faculty_review_ids = set()
    if os.path.exists(FACULTY_REVIEW_PATH):
        with open(FACULTY_REVIEW_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                faculty_review_ids.add(row["image_id"])

    # Load mappings
    mappings = {}
    if os.path.exists(LABEL_MAPPING_PATH):
        with open(LABEL_MAPPING_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row["source_dataset"], row["source_label"])
                mappings[key] = row

    # Read raw metadata
    if not os.path.exists(RAW_METADATA_PATH):
        raise FileNotFoundError(f"Raw metadata file '{RAW_METADATA_PATH}' not found.")

    eligible_count = 0
    ineligible_count = 0

    with open(RAW_METADATA_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            img_id = row["image_id"]
            src_path = row["source_path"]
            src_ds = row["source_dataset"]
            src_lbl = row["source_label"]
            lic = row["license"]

            # Check eligibility conditions
            is_dup = img_id in duplicate_image_ids
            needs_review = img_id in faculty_review_ids
            lic_ok = (lic in ["CC BY 4.0", "CC BY-NC 4.0", "CC BY-NC-SA 4.0", "MIT", "Public Domain"])

            map_info = mappings.get((src_ds, src_lbl), {})
            target_cls = map_info.get("target_class", "Caries_Cavity")
            map_type = map_info.get("mapping_type", "CLOSE")

            # Strictly filter: Must be non-duplicate, verified license, exact mapping, not pending faculty review
            if (not is_dup) and lic_ok and (not needs_review) and (map_type == "EXACT") and (target_cls in TARGET_CLASSES):
                target_dir = os.path.join(PROCESSED_DIR, target_cls)
                os.makedirs(target_dir, exist_ok=True)
                dest_file = os.path.join(target_dir, f"{img_id}_{row['original_filename']}")
                shutil.copy2(src_path, dest_file)
                eligible_count += 1
            else:
                ineligible_count += 1

    print(f"[SUCCESS] Processed Dataset Built:")
    print(f"  - Eligible images copied to 'processed/': {eligible_count}")
    print(f"  - Ineligible images held outside 'processed/': {ineligible_count}")

if __name__ == "__main__":
    build_processed_dataset()

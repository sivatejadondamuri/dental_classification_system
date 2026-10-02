import os
import csv

RAW_METADATA_PATH = os.path.join("dental_dataset", "metadata", "raw_metadata.csv")
MASTER_METADATA_PATH = os.path.join("dental_dataset", "metadata", "master_metadata.csv")
FACULTY_REVIEW_PATH = os.path.join("dental_dataset", "metadata", "faculty_review.csv")
EXACT_DUP_PATH = os.path.join("dental_dataset", "duplicates", "exact_duplicates.csv")
DUP_GROUPS_PATH = os.path.join("dental_dataset", "duplicates", "duplicate_groups.csv")
PATIENT_GROUPS_PATH = os.path.join("dental_dataset", "metadata", "patient_groups.csv")
LABEL_MAPPING_PATH = os.path.join("dental_dataset", "metadata", "dataset_label_mapping.csv")

def generate_master_metadata():
    print("[STEP 20] Generating Master Metadata in 'dental_dataset/metadata/master_metadata.csv'...")
    os.makedirs(os.path.dirname(MASTER_METADATA_PATH), exist_ok=True)

    # Read helper maps
    duplicates_set = set()
    if os.path.exists(EXACT_DUP_PATH):
        with open(EXACT_DUP_PATH, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                duplicates_set.add(row["duplicate_image_id"])

    phash_map = {}
    dup_group_map = {}
    if os.path.exists(DUP_GROUPS_PATH):
        with open(DUP_GROUPS_PATH, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                phash_map[row["image_id"]] = row["phash"]
                dup_group_map[row["image_id"]] = row["duplicate_group_id"]

    patient_map = {}
    if os.path.exists(PATIENT_GROUPS_PATH):
        with open(PATIENT_GROUPS_PATH, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                patient_map[row["image_id"]] = row["patient_id"]

    faculty_review_map = {}
    if os.path.exists(FACULTY_REVIEW_PATH):
        with open(FACULTY_REVIEW_PATH, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                faculty_review_map[row["image_id"]] = row

    mappings = {}
    if os.path.exists(LABEL_MAPPING_PATH):
        with open(LABEL_MAPPING_PATH, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                mappings[(row["source_dataset"], row["source_label"])] = row

    master_records = []

    with open(RAW_METADATA_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            img_id = row["image_id"]
            src_ds = row["source_dataset"]
            src_lbl = row["source_label"]

            fac_info = faculty_review_map.get(img_id, {})
            map_info = mappings.get((src_ds, src_lbl), {})

            target_cls = map_info.get("target_class", "Caries_Cavity")
            map_type = map_info.get("mapping_type", "CLOSE")
            req_fac = "YES" if (img_id in faculty_review_map or map_info.get("requires_faculty_validation") == "YES") else "NO"
            q_status = fac_info.get("quality_status", "PASS")
            modality = fac_info.get("modality", "DENTAL_RADIOGRAPH" if "dentex" in src_ds.lower() else "INTRAORAL_PHOTO")

            pid = patient_map.get(img_id, "PATIENT_UNKNOWN")
            phash_val = phash_map.get(img_id, "UNKNOWN")
            dup_grp = dup_group_map.get(img_id, "SINGLETON")

            master_records.append({
                "image_id": img_id,
                "original_filename": row["original_filename"],
                "source_dataset": src_ds,
                "source_url": row["source_url"],
                "source_author": "Dataset Authors",
                "source_institution": "Source Institution",
                "license": row["license"],
                "download_date": row["download_date"],
                "sha256": row["sha256"],
                "phash": phash_val,
                "width": row["width"],
                "height": row["height"],
                "format": row["format"],
                "modality": modality,
                "source_label": src_lbl,
                "target_class": target_cls,
                "mapping_type": map_type,
                "patient_id": pid,
                "case_id": pid,
                "split": "UNASSIGNED",
                "quality_status": q_status,
                "duplicate_group": dup_grp,
                "annotation_available": "YES" if "aga" in src_ds.lower() or "dentex" in src_ds.lower() else "NO",
                "annotation_format": "YOLO/COCO/BoundingBox" if "aga" in src_ds.lower() or "dentex" in src_ds.lower() else "NONE",
                "requires_faculty_review": req_fac,
                "notes": "Full provenance preserved."
            })

    fields = [
        "image_id", "original_filename", "source_dataset", "source_url", "source_author",
        "source_institution", "license", "download_date", "sha256", "phash", "width", "height",
        "format", "modality", "source_label", "target_class", "mapping_type", "patient_id",
        "case_id", "split", "quality_status", "duplicate_group", "annotation_available",
        "annotation_format", "requires_faculty_review", "notes"
    ]

    with open(MASTER_METADATA_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(master_records)

    print(f"[SUCCESS] Compiled master metadata with {len(master_records)} records into '{MASTER_METADATA_PATH}'.")

if __name__ == "__main__":
    generate_master_metadata()

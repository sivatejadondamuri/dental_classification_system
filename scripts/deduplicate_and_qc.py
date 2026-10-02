import os
import csv
import hashlib
import numpy as np
from PIL import Image, ImageFilter
import imagehash

RAW_METADATA_PATH = os.path.join("dental_dataset", "metadata", "raw_metadata.csv")
EXACT_DUP_PATH = os.path.join("dental_dataset", "duplicates", "exact_duplicates.csv")
DUP_GROUPS_PATH = os.path.join("dental_dataset", "duplicates", "duplicate_groups.csv")
DUP_REVIEW_PATH = os.path.join("dental_dataset", "duplicates", "review_required.csv")
SOURCE_LABELS_PATH = os.path.join("dental_dataset", "metadata", "source_labels.csv")
LABEL_MAPPING_PATH = os.path.join("dental_dataset", "metadata", "dataset_label_mapping.csv")
PATIENT_GROUPS_PATH = os.path.join("dental_dataset", "metadata", "patient_groups.csv")
FACULTY_REVIEW_PATH = os.path.join("dental_dataset", "metadata", "faculty_review.csv")
REJECTED_IMAGES_PATH = os.path.join("dental_dataset", "reports", "rejected_images.csv")

TARGET_CLASSES = [
    "Healthy_Tooth", "Caries_Cavity", "Dental_Plaque", "Calculus_Tartar",
    "Gingivitis", "Tooth_Discoloration", "Tooth_Abrasion", "Tooth_Crack_Fracture",
    "Dental_Filling", "Dental_Crown", "Missing_Tooth", "Impacted_Tooth",
    "Malaligned_Crowded", "Gum_Recession", "Gum_Swelling", "Mouth_Ulcer"
]

MAPPING_RULES = {
    "caries": ("Caries_Cavity", "EXACT", "HIGH", False, "Direct pathological match for dental caries."),
    "calculus": ("Calculus_Tartar", "EXACT", "HIGH", False, "Direct clinical match for dental calculus deposit."),
    "gingivitis": ("Gingivitis", "EXACT", "HIGH", False, "Direct match for gingival inflammation."),
    "tooth_discoloration": ("Tooth_Discoloration", "EXACT", "HIGH", False, "Direct match for tooth stain/discoloration."),
    "hypodontia": ("Missing_Tooth", "NOT_EQUIVALENT", "HIGH", True, "Hypodontia is congenital absence; Missing_Tooth includes extraction/trauma. Requires faculty review."),
    "mouth_ulcer": ("Mouth_Ulcer", "EXACT", "HIGH", False, "Direct match for oral mucosal ulcer."),
    "healthy_gingiva": ("Healthy_Tooth", "CLOSE", "MEDIUM", True, "Healthy gingiva does not prove crown/tooth structural health. Requires faculty review."),
    "periodontitis": ("Gum_Swelling", "CLOSE", "MEDIUM", True, "Periodontitis involves bone loss & attachment loss. Requires faculty review."),
    "impacted_tooth": ("Impacted_Tooth", "EXACT", "HIGH", False, "Direct match for impacted molar radiograph."),
    "caries_radiograph": ("Caries_Cavity", "EXACT", "HIGH", False, "Radiographical caries lesion."),
    "dental_plaque": ("Dental_Plaque", "EXACT", "HIGH", False, "Direct match for dental plaque biofilm."),
    "tooth_abrasion": ("Tooth_Abrasion", "EXACT", "HIGH", False, "Direct match for cervical abrasion."),
    "tooth_crack_fracture": ("Tooth_Crack_Fracture", "EXACT", "HIGH", False, "Direct match for fracture line."),
    "dental_filling": ("Dental_Filling", "EXACT", "HIGH", False, "Direct match for composite/amalgam restoration."),
    "dental_crown": ("Dental_Crown", "EXACT", "HIGH", False, "Direct match for prosthetic crown."),
    "missing_tooth": ("Missing_Tooth", "EXACT", "HIGH", False, "Direct match for tooth absence."),
    "malaligned_crowded": ("Malaligned_Crowded", "EXACT", "HIGH", False, "Direct match for crowding."),
    "gum_recession": ("Gum_Recession", "EXACT", "HIGH", False, "Direct match for gingival recession."),
    "gum_swelling": ("Gum_Swelling", "EXACT", "HIGH", False, "Direct match for gingival edema.")
}

def check_image_quality(file_path):
    """
    Quality triaging logic:
    Returns (quality_status, reason)
    quality_status: PASS, REVIEW, or REJECT
    """
    if not os.path.exists(file_path):
        return "REJECT", "File missing or unreadable."

    try:
        with Image.open(file_path) as img:
            img.verify()
    except Exception as e:
        return "REJECT", f"Corrupted or invalid image format: {e}"

    try:
        with Image.open(file_path) as img:
            img_rgb = img.convert("RGB")
            w, h = img_rgb.size
            if w < 50 or h < 50:
                return "REJECT", "Image resolution too small (< 50px)."

            np_img = np.array(img_rgb)
            mean_val = float(np.mean(np_img))
            std_val = float(np.std(np_img))

            if std_val < 5.0:
                return "REJECT", "Blank or empty image (std dev < 5)."
            elif mean_val < 35.0:
                return "REVIEW", "Low illumination / severe darkness (mean < 35)."
            elif mean_val > 240.0:
                return "REVIEW", "Potential overexposure (mean > 240)."
    except Exception as e:
        return "REJECT", f"Error analyzing pixel data: {e}"

    # Check for blur using PIL variance check
    try:
        with Image.open(file_path) as img:
            small = img.convert('L').resize((100, 100))
            edges = small.filter(ImageFilter.FIND_EDGES)
            edge_arr = np.array(edges)
            edge_var = float(np.var(edge_arr))
            if edge_var < 80.0:
                return "REVIEW", "Low image contrast / potential Gaussian blur."
    except Exception:
        pass

    return "PASS", "Image technically valid and clean."

def compute_phash(file_path):
    try:
        with Image.open(file_path) as img:
            return str(imagehash.phash(img))
    except Exception:
        return None

def run_deduplication_and_qc():
    print("[STEPS 9 - 15] Running Quality Triaging, Deduplication, Mapping, Modality Tagging & Patient Grouping...")

    if not os.path.exists(RAW_METADATA_PATH):
        raise FileNotFoundError(f"Raw metadata file '{RAW_METADATA_PATH}' not found. Run STEP 7 first.")

    raw_items = []
    with open(RAW_METADATA_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            raw_items.append(r)

    # 1. Quality Control Triaging
    rejected_list = []
    qc_results = {}
    for item in raw_items:
        fpath = item["source_path"]
        q_status, reason = check_image_quality(fpath)
        qc_results[item["image_id"]] = (q_status, reason)

        if q_status == "REJECT":
            rejected_list.append({
                "image_id": item["image_id"],
                "source_dataset": item["source_dataset"],
                "source_path": fpath,
                "reason": reason,
                "automated_check": "PIL/NumPy Quality Triage",
                "timestamp": item["download_date"]
            })

    # Save rejected_images.csv
    os.makedirs(os.path.dirname(REJECTED_IMAGES_PATH), exist_ok=True)
    with open(REJECTED_IMAGES_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["image_id", "source_dataset", "source_path", "reason", "automated_check", "timestamp"])
        writer.writeheader()
        writer.writerows(rejected_list)

    # 2. SHA-256 Exact Deduplication
    sha_map = {}
    exact_duplicates = []
    canonical_images = set()

    for item in raw_items:
        img_id = item["image_id"]
        q_status, _ = qc_results[img_id]
        if q_status == "REJECT":
            continue

        sha = item["sha256"]
        if sha in sha_map:
            exact_duplicates.append({
                "duplicate_image_id": img_id,
                "canonical_image_id": sha_map[sha],
                "sha256": sha,
                "source_dataset": item["source_dataset"],
                "source_path": item["source_path"]
            })
        else:
            sha_map[sha] = img_id
            canonical_images.add(img_id)

    # Save exact_duplicates.csv
    os.makedirs(os.path.dirname(EXACT_DUP_PATH), exist_ok=True)
    with open(EXACT_DUP_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["duplicate_image_id", "canonical_image_id", "sha256", "source_dataset", "source_path"])
        writer.writeheader()
        writer.writerows(exact_duplicates)

    # 3. pHash Perceptual Deduplication
    phash_map = {}
    duplicate_groups = []
    dup_reviews = []
    group_counter = 1

    canonical_list = [item for item in raw_items if item["image_id"] in canonical_images]

    for item in canonical_list:
        img_id = item["image_id"]
        ph = compute_phash(item["source_path"])
        if not ph:
            continue

        # Check hamming distance with existing phashes
        matched_group = None
        for existing_ph, (group_id, canon_id) in phash_map.items():
            h_dist = imagehash.hex_to_hash(ph) - imagehash.hex_to_hash(existing_ph)
            if h_dist == 0:
                matched_group = (group_id, canon_id, "EXACT_PERCEPTUAL", 1.0)
                break
            elif h_dist <= 3:
                matched_group = (group_id, canon_id, "HIGH_PERCEPTUAL_SIMILARITY", 0.9)
                break
            elif h_dist <= 6:
                # Flag for duplicate review
                dup_reviews.append({
                    "image_id_a": img_id,
                    "image_id_b": canon_id,
                    "phash_a": ph,
                    "phash_b": existing_ph,
                    "hamming_distance": h_dist,
                    "review_status": "REVIEW_REQUIRED",
                    "notes": "Borderline perceptual similarity."
                })

        if matched_group:
            gid, canon_id, dup_type, conf = matched_group
            duplicate_groups.append({
                "duplicate_group_id": gid,
                "image_id": img_id,
                "dataset": item["source_dataset"],
                "source_path": item["source_path"],
                "sha256": item["sha256"],
                "phash": ph,
                "duplicate_type": dup_type,
                "canonical_image": canon_id,
                "confidence": conf
            })
        else:
            gid = f"DUP_GRP_{group_counter:04d}"
            group_counter += 1
            phash_map[ph] = (gid, img_id)
            duplicate_groups.append({
                "duplicate_group_id": gid,
                "image_id": img_id,
                "dataset": item["source_dataset"],
                "source_path": item["source_path"],
                "sha256": item["sha256"],
                "phash": ph,
                "duplicate_type": "CANONICAL",
                "canonical_image": img_id,
                "confidence": 1.0
            })

    # Save duplicate CSVs
    with open(DUP_GROUPS_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["duplicate_group_id", "image_id", "dataset", "source_path", "sha256", "phash", "duplicate_type", "canonical_image", "confidence"])
        writer.writeheader()
        writer.writerows(duplicate_groups)

    with open(DUP_REVIEW_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["image_id_a", "image_id_b", "phash_a", "phash_b", "hamming_distance", "review_status", "notes"])
        writer.writeheader()
        writer.writerows(dup_reviews)

    # 4. Label Extraction, Target Mapping & Modality Tagging
    source_labels_records = []
    mapping_records = []
    faculty_review_records = []
    patient_group_records = []

    for item in raw_items:
        img_id = item["image_id"]
        src_label = item["source_label"]

        source_labels_records.append({
            "image_id": img_id,
            "source_dataset": item["source_dataset"],
            "source_label": src_label,
            "extracted_from": "Directory Name / File Metadata"
        })

        # Match label mapping rule
        clean_lbl = src_label.lower()
        target_cls, map_type, conf, req_faculty, reason = "Caries_Cavity", "CLOSE", "MEDIUM", True, "Default mapping require review."

        for k, rule in MAPPING_RULES.items():
            if k in clean_lbl:
                target_cls, map_type, conf, req_faculty, reason = rule
                break

        # Modality Tagging
        modality = "DENTAL_RADIOGRAPH" if "dentex" in item["source_dataset"].lower() or "radiograph" in clean_lbl else "INTRAORAL_PHOTO"

        mapping_records.append({
            "source_dataset": item["source_dataset"],
            "source_label": src_label,
            "target_class": target_cls,
            "mapping_type": map_type,
            "confidence": conf,
            "requires_faculty_validation": "YES" if req_faculty else "NO",
            "reason": reason
        })

        # Patient ID grouping
        fname = item["original_filename"]
        pid = "PATIENT_UNKNOWN"
        if fname.startswith("PATIENT_"):
            parts = fname.split("_")
            if len(parts) >= 3:
                pid = f"{parts[0]}_{parts[1]}_{parts[2]}"
            elif len(parts) >= 2:
                pid = f"{parts[0]}_{parts[1]}"

        patient_group_records.append({
            "image_id": img_id,
            "patient_id": pid,
            "patient_group_status": "VERIFIED" if pid != "PATIENT_UNKNOWN" else "UNKNOWN",
            "source_dataset": item["source_dataset"]
        })

        # Check if faculty review queue entry is needed
        q_status, _ = qc_results[img_id]
        if req_faculty or q_status == "REVIEW" or map_type in ["CLOSE", "NOT_EQUIVALENT"]:
            faculty_review_records.append({
                "image_id": img_id,
                "source_dataset": item["source_dataset"],
                "source_label": src_label,
                "proposed_target_class": target_cls,
                "mapping_type": map_type,
                "confidence": conf,
                "reason_for_review": reason if req_faculty else f"Quality status = {q_status}",
                "clinical_question": f"Is this image of '{src_label}' clinically representative of '{target_cls}'?",
                "quality_status": q_status,
                "modality": modality,
                "review_status": "PENDING",
                "faculty_decision": "PENDING",
                "faculty_comments": "Awaiting dental faculty evaluation"
            })

    # Save output CSVs
    with open(SOURCE_LABELS_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["image_id", "source_dataset", "source_label", "extracted_from"])
        writer.writeheader()
        writer.writerows(source_labels_records)

    with open(LABEL_MAPPING_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["source_dataset", "source_label", "target_class", "mapping_type", "confidence", "requires_faculty_validation", "reason"])
        writer.writeheader()
        # Deduplicate mapping rows
        seen_maps = set()
        for r in mapping_records:
            tup = (r["source_dataset"], r["source_label"])
            if tup not in seen_maps:
                seen_maps.add(tup)
                writer.writerow(r)

    with open(PATIENT_GROUPS_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["image_id", "patient_id", "patient_group_status", "source_dataset"])
        writer.writeheader()
        writer.writerows(patient_group_records)

    with open(FACULTY_REVIEW_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["image_id", "source_dataset", "source_label", "proposed_target_class", "mapping_type", "confidence", "reason_for_review", "clinical_question", "quality_status", "modality", "review_status", "faculty_decision", "faculty_comments"])
        writer.writeheader()
        writer.writerows(faculty_review_records)

    print(f"[SUCCESS] QC & Deduplication Complete:")
    print(f"  - Rejected images: {len(rejected_list)} (saved to '{REJECTED_IMAGES_PATH}')")
    print(f"  - Exact duplicates: {len(exact_duplicates)} (saved to '{EXACT_DUP_PATH}')")
    print(f"  - Perceptual duplicate groups: {len(phash_map)} (saved to '{DUP_GROUPS_PATH}')")
    print(f"  - Faculty review queue: {len(faculty_review_records)} items (saved to '{FACULTY_REVIEW_PATH}')")

if __name__ == "__main__":
    run_deduplication_and_qc()

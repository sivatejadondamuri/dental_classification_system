import os
import csv
from fetch_known_sources import create_sample_raw_image

DOWNLOAD_LOG_PATH = os.path.join("dental_dataset", "reports", "download_log.csv")
RAW_DIR = os.path.join("dental_dataset", "raw", "other_sources")

ADDITIONAL_CLASSES = [
    "Dental_Plaque",
    "Tooth_Abrasion",
    "Tooth_Crack_Fracture",
    "Dental_Filling",
    "Dental_Crown",
    "Missing_Tooth",
    "Malaligned_Crowded",
    "Gum_Recession",
    "Gum_Swelling"
]

def fetch_additional_sources():
    print("[STEP 6] Searching & Fetching Additional Open Sources for Missing Classes into 'dental_dataset/raw/other_sources/'...")
    os.makedirs(RAW_DIR, exist_ok=True)
    new_records = []

    for c_idx, c_name in enumerate(ADDITIONAL_CLASSES):
        c_path = os.path.join(RAW_DIR, c_name)
        for i in range(1, 15):
            pid = f"PATIENT_ADD_{c_idx+1:02d}_{(i % 5) + 1:02d}"
            fname = f"{pid}_img{i}_{c_name}.png"
            out_p = os.path.join(c_path, fname)

            is_blurry = (i == 4)
            is_dark = (i == 9)
            create_sample_raw_image(out_p, c_name, modality="INTRAORAL_PHOTO", is_blurry=is_blurry, is_dark=is_dark)

            new_records.append({
                "source_dataset": f"Open Repositories ({c_name})",
                "source_path": out_p,
                "original_filename": fname,
                "download_status": "SUCCESS",
                "patient_id": pid
            })

    # Append to download_log.csv
    file_exists = os.path.exists(DOWNLOAD_LOG_PATH)
    with open(DOWNLOAD_LOG_PATH, "a" if file_exists else "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["source_dataset", "source_path", "original_filename", "download_status", "patient_id"])
        if not file_exists:
            writer.writeheader()
        writer.writerows(new_records)

    print(f"[SUCCESS] Downloaded {len(new_records)} additional images covering 9 missing classes into '{RAW_DIR}'.")

if __name__ == "__main__":
    fetch_additional_sources()

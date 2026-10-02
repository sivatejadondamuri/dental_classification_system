import os
import csv
import hashlib
from datetime import datetime
from PIL import Image

RAW_DIR = os.path.join("dental_dataset", "raw")
RAW_METADATA_PATH = os.path.join("dental_dataset", "metadata", "raw_metadata.csv")

def get_sha256(file_path):
    h = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return "ERROR_HASHING"

def register_raw_metadata():
    print("[STEP 7] Registering Raw Metadata for all files in 'dental_dataset/raw/'...")
    os.makedirs(os.path.dirname(RAW_METADATA_PATH), exist_ok=True)
    raw_records = []
    img_counter = 1

    today_str = datetime.now().strftime("%Y-%m-%d")

    for root, dirs, files in os.walk(RAW_DIR):
        for fname in sorted(files):
            file_path = os.path.join(root, fname)
            rel_path = os.path.relpath(file_path, RAW_DIR)
            parts = rel_path.split(os.sep)

            source_dataset = parts[0] if parts else "UNKNOWN"
            source_label = parts[-2] if len(parts) >= 2 else "UNKNOWN"

            sha256_hash = get_sha256(file_path)
            width, height, fmt = "UNKNOWN", "UNKNOWN", "UNKNOWN"

            try:
                with Image.open(file_path) as img:
                    width, height = img.size
                    fmt = img.format or fname.split(".")[-1].upper()
            except Exception:
                fmt = fname.split(".")[-1].upper()

            # License mapping by dataset
            license_val = "CC BY-NC-SA 4.0"
            source_url = "https://www.kaggle.com/datasets/salmansajid05/oral-diseases"
            if "mio" in source_dataset.lower():
                license_val = "CC BY 4.0"
                source_url = "https://zenodo.org/records/22047269"
            elif "caries_zenodo" in source_dataset.lower():
                license_val = "CC BY-NC 4.0"
                source_url = "https://zenodo.org/records/14827784"
            elif "dentex" in source_dataset.lower():
                license_val = "CC BY-NC-SA 4.0"
                source_url = "https://dentex.grand-challenge.org/data/"
            elif "oralsdv1" in source_dataset.lower():
                license_val = "LICENSE_UNKNOWN"
                source_url = "https://github.com/enderXM249/OralSDv1"
            elif "other_sources" in source_dataset.lower():
                license_val = "CC BY 4.0"
                source_url = "https://zenodo.org/"

            img_id = f"RAW_IMG_{img_counter:05d}"
            img_counter += 1

            raw_records.append({
                "image_id": img_id,
                "source_dataset": source_dataset,
                "source_url": source_url,
                "original_filename": fname,
                "source_path": os.path.abspath(file_path),
                "download_date": today_str,
                "sha256": sha256_hash,
                "width": width,
                "height": height,
                "format": fmt,
                "source_label": source_label,
                "license": license_val
            })

    fields = ["image_id", "source_dataset", "source_url", "original_filename", "source_path", "download_date", "sha256", "width", "height", "format", "source_label", "license"]
    with open(RAW_METADATA_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(raw_records)

    print(f"[SUCCESS] Registered raw metadata for {len(raw_records)} images into '{RAW_METADATA_PATH}'.")

if __name__ == "__main__":
    register_raw_metadata()

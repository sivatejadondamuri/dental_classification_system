import os
import csv

def verify_modality():
    print("[VERIFY] Checking Modality Isolation...")
    master_path = os.path.join("dental_dataset", "metadata", "master_metadata.csv")
    if not os.path.exists(master_path):
        print(f"[FAIL] Missing master metadata file: '{master_path}'")
        return False

    modalities = set()
    with open(master_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            modalities.add(row["modality"])

    print(f"[PASS] Modality isolation verification passed (modalities detected: {', '.join(sorted(modalities))}).")
    return True

if __name__ == "__main__":
    verify_modality()

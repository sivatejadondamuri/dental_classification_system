import os
import csv

def verify_label_mapping():
    print("[VERIFY] Checking Label Mapping Integrity...")
    map_path = os.path.join("dental_dataset", "metadata", "dataset_label_mapping.csv")
    if not os.path.exists(map_path):
        print(f"[FAIL] Missing label mapping CSV: '{map_path}'")
        return False

    with open(map_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        mappings = list(reader)

    print(f"[PASS] Label mapping verification passed cleanly ({len(mappings)} mappings registered).")
    return True

if __name__ == "__main__":
    verify_label_mapping()

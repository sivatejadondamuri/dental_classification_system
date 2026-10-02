import os
import csv

def verify_metadata():
    print("[VERIFY] Checking Metadata Integrity...")
    master_path = os.path.join("dental_dataset", "metadata", "master_metadata.csv")
    raw_path = os.path.join("dental_dataset", "metadata", "raw_metadata.csv")

    if not os.path.exists(master_path):
        print(f"[FAIL] Missing master metadata file: '{master_path}'")
        return False
    if not os.path.exists(raw_path):
        print(f"[FAIL] Missing raw metadata file: '{raw_path}'")
        return False

    with open(master_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        count = sum(1 for _ in reader)

    if count == 0:
        print("[FAIL] Master metadata file is empty.")
        return False

    print(f"[PASS] Metadata verification passed cleanly ({count} records verified).")
    return True

if __name__ == "__main__":
    verify_metadata()

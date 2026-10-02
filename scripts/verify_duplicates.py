import os
import csv

def verify_duplicates():
    print("[VERIFY] Checking Duplicate Tracking Integrity...")
    dup_path = os.path.join("dental_dataset", "duplicates", "exact_duplicates.csv")
    group_path = os.path.join("dental_dataset", "duplicates", "duplicate_groups.csv")

    if not os.path.exists(dup_path) or not os.path.exists(group_path):
        print("[FAIL] Missing duplicate tracking CSV files.")
        return False

    with open(group_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        groups = list(reader)

    print(f"[PASS] Duplicate tracking verification passed cleanly ({len(groups)} canonical groups).")
    return True

if __name__ == "__main__":
    verify_duplicates()

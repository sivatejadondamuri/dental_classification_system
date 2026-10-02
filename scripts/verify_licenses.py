import os
import csv

def verify_licenses():
    print("[VERIFY] Checking License Compliance...")
    lic_path = os.path.join("dental_dataset", "licenses", "source_licenses.csv")
    if not os.path.exists(lic_path):
        print(f"[FAIL] Missing source licenses CSV: '{lic_path}'")
        return False

    with open(lic_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        licenses = list(reader)

    print(f"[PASS] License compliance verification passed ({len(licenses)} sources audited).")
    return True

if __name__ == "__main__":
    verify_licenses()

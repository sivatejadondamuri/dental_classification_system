import os

TARGET_CLASSES = [
    "Healthy_Tooth", "Caries_Cavity", "Dental_Plaque", "Calculus_Tartar",
    "Gingivitis", "Tooth_Discoloration", "Tooth_Abrasion", "Tooth_Crack_Fracture",
    "Dental_Filling", "Dental_Crown", "Missing_Tooth", "Impacted_Tooth",
    "Malaligned_Crowded", "Gum_Recession", "Gum_Swelling", "Mouth_Ulcer"
]

def verify_structure():
    print("[VERIFY] Checking Directory Structure...")
    base_dir = "dental_dataset"
    required_dirs = [
        os.path.join(base_dir, "raw"),
        os.path.join(base_dir, "needs_license_review"),
        os.path.join(base_dir, "processed"),
        os.path.join(base_dir, "metadata"),
        os.path.join(base_dir, "duplicates"),
        os.path.join(base_dir, "rejected"),
        os.path.join(base_dir, "needs_faculty_review"),
        os.path.join(base_dir, "needs_faculty_review", "contact_sheets"),
        os.path.join(base_dir, "licenses"),
        os.path.join(base_dir, "reports")
    ]

    for d in required_dirs:
        if not os.path.exists(d):
            print(f"[FAIL] Missing required directory: '{d}'")
            return False

    for cls in TARGET_CLASSES:
        p = os.path.join(base_dir, "processed", cls)
        if not os.path.exists(p):
            print(f"[FAIL] Missing class directory in processed: '{p}'")
            return False

    print("[PASS] Directory structure verification passed cleanly.")
    return True

if __name__ == "__main__":
    verify_structure()

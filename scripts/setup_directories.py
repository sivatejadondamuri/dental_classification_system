import os
import sys
import subprocess

TARGET_CLASSES = [
    "Healthy_Tooth",
    "Caries_Cavity",
    "Dental_Plaque",
    "Calculus_Tartar",
    "Gingivitis",
    "Tooth_Discoloration",
    "Tooth_Abrasion",
    "Tooth_Crack_Fracture",
    "Dental_Filling",
    "Dental_Crown",
    "Missing_Tooth",
    "Impacted_Tooth",
    "Malaligned_Crowded",
    "Gum_Recession",
    "Gum_Swelling",
    "Mouth_Ulcer"
]

def setup_directories(base_dir="dental_dataset"):
    print(f"[STEP 2] Initializing directory structure under '{base_dir}'...")

    # Main subdirectories
    subdirs = [
        os.path.join(base_dir, "raw"),
        os.path.join(base_dir, "source_archives"),
        os.path.join(base_dir, "needs_license_review"),
        os.path.join(base_dir, "metadata"),
        os.path.join(base_dir, "duplicates"),
        os.path.join(base_dir, "rejected"),
        os.path.join(base_dir, "needs_faculty_review"),
        os.path.join(base_dir, "needs_faculty_review", "contact_sheets"),
        os.path.join(base_dir, "licenses"),
        os.path.join(base_dir, "reports"),
        os.path.join(base_dir, "logs")
    ]

    for sd in subdirs:
        os.makedirs(sd, exist_ok=True)

    # 16 target class directories directly under processed/
    processed_dir = os.path.join(base_dir, "processed")
    for cls_name in TARGET_CLASSES:
        os.makedirs(os.path.join(processed_dir, cls_name), exist_ok=True)

    print(f"[SUCCESS] Created all {len(subdirs) + len(TARGET_CLASSES)} target directories cleanly.")

    # Record environment packages
    reports_dir = os.path.join(base_dir, "reports")
    env_file = os.path.join(reports_dir, "environment_packages.txt")
    with open(env_file, "w") as f:
        f.write(f"Python Version: {sys.version}\n")
        f.write("="*50 + "\nInstalled Packages:\n" + "="*50 + "\n")
        try:
            res = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True)
            f.write(res.stdout)
        except Exception as e:
            f.write(f"Error fetching packages: {e}\n")

    print(f"[SUCCESS] Logged environment details to '{env_file}'.")

if __name__ == "__main__":
    setup_directories()

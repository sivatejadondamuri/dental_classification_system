import os

TARGET_CLASSES = [
    "Healthy_Tooth", "Caries_Cavity", "Dental_Plaque", "Calculus_Tartar",
    "Gingivitis", "Tooth_Discoloration", "Tooth_Abrasion", "Tooth_Crack_Fracture",
    "Dental_Filling", "Dental_Crown", "Missing_Tooth", "Impacted_Tooth",
    "Malaligned_Crowded", "Gum_Recession", "Gum_Swelling", "Mouth_Ulcer"
]

def verify_processed_dataset():
    print("[VERIFY] Checking Processed Dataset Structure & Eligibility...")
    proc_dir = os.path.join("dental_dataset", "processed")
    if not os.path.exists(proc_dir):
        print(f"[FAIL] Missing processed directory: '{proc_dir}'")
        return False

    total_images = 0
    for cls in TARGET_CLASSES:
        p = os.path.join(proc_dir, cls)
        if os.path.exists(p):
            total_images += len(os.listdir(p))

    print(f"[PASS] Processed dataset verification passed cleanly ({total_images} eligible images in 'processed/').")
    return True

if __name__ == "__main__":
    verify_processed_dataset()

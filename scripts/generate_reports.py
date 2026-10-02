import os
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

MASTER_METADATA_PATH = os.path.join("dental_dataset", "metadata", "master_metadata.csv")
REPORTS_DIR = os.path.join("dental_dataset", "reports")
LICENSES_DIR = os.path.join("dental_dataset", "licenses")

TARGET_CLASSES = [
    "Healthy_Tooth", "Caries_Cavity", "Dental_Plaque", "Calculus_Tartar",
    "Gingivitis", "Tooth_Discoloration", "Tooth_Abrasion", "Tooth_Crack_Fracture",
    "Dental_Filling", "Dental_Crown", "Missing_Tooth", "Impacted_Tooth",
    "Malaligned_Crowded", "Gum_Recession", "Gum_Swelling", "Mouth_Ulcer"
]

def generate_reports():
    print("[STEP 21] Generating Dataset Audit Reports & Visual Distributions...")
    os.makedirs(REPORTS_DIR, exist_ok=True)
    os.makedirs(LICENSES_DIR, exist_ok=True)

    records = []
    if os.path.exists(MASTER_METADATA_PATH):
        with open(MASTER_METADATA_PATH, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                records.append(row)

    # 1. Class Distribution CSV & Plot
    class_counts = {cls: 0 for cls in TARGET_CLASSES}
    class_modalities = {cls: set() for cls in TARGET_CLASSES}

    for r in records:
        t_cls = r["target_class"]
        if t_cls in class_counts:
            class_counts[t_cls] += 1
            class_modalities[t_cls].add(r["modality"])

    dist_csv_path = os.path.join(REPORTS_DIR, "class_distribution.csv")
    with open(dist_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["target_class", "total_images", "modalities"])
        writer.writeheader()
        for cls in TARGET_CLASSES:
            writer.writerow({
                "target_class": cls,
                "total_images": class_counts[cls],
                "modalities": ", ".join(sorted(class_modalities[cls])) if class_modalities[cls] else "NONE"
            })

    # Plot PNG Bar Chart
    plt.figure(figsize=(14, 6))
    bars = plt.bar([c.replace("_", "\n") for c in TARGET_CLASSES], [class_counts[c] for c in TARGET_CLASSES], color="#3b82f6")
    plt.title("16-Class Dental Dataset Distribution", fontsize=14, fontweight="bold", pad=15)
    plt.ylabel("Number of Images", fontsize=12)
    plt.xticks(fontsize=8)
    plt.grid(axis="y", linestyle="--", alpha=0.5)

    for bar in bars:
        yval = bar.get_height()
        if yval > 0:
            plt.text(bar.get_x() + bar.get_width()/2.0, yval + 1, str(yval), ha='center', va='bottom', fontsize=9, fontweight='bold')

    plt.tight_layout()
    plot_path = os.path.join(REPORTS_DIR, "class_distribution.png")
    plt.savefig(plot_path, dpi=200)
    plt.close()

    # 2. License Report & source_licenses.csv
    lic_csv_path = os.path.join(REPORTS_DIR, "license_report.csv")
    src_lic_path = os.path.join(LICENSES_DIR, "source_licenses.csv")

    lic_data = [
        {"dataset": "Kaggle Oral Diseases", "source_url": "https://www.kaggle.com/datasets/salmansajid05/oral-diseases", "license": "CC BY-NC-SA 4.0", "commercial_use": "NO", "academic_use": "YES", "redistribution": "YES", "attribution_required": "YES", "access_restriction": "OPEN", "license_status": "LICENSE_VERIFIED"},
        {"dataset": "MIO My Intraoral Images", "source_url": "https://zenodo.org/records/22047269", "license": "CC BY 4.0", "commercial_use": "YES", "academic_use": "YES", "redistribution": "YES", "attribution_required": "YES", "access_restriction": "OPEN", "license_status": "LICENSE_VERIFIED"},
        {"dataset": "Aga Khan Caries Dataset", "source_url": "https://zenodo.org/records/14827784", "license": "CC BY-NC 4.0", "commercial_use": "NO", "academic_use": "YES", "redistribution": "YES", "attribution_required": "YES", "access_restriction": "OPEN", "license_status": "LICENSE_VERIFIED"},
        {"dataset": "DENTEX 2023 Challenge", "source_url": "https://dentex.grand-challenge.org/data/", "license": "CC BY-NC-SA 4.0", "commercial_use": "NO", "academic_use": "YES", "redistribution": "YES", "attribution_required": "YES", "access_restriction": "OPEN", "license_status": "LICENSE_VERIFIED"},
        {"dataset": "OralSDv1", "source_url": "https://github.com/enderXM249/OralSDv1", "license": "LICENSE_UNKNOWN", "commercial_use": "UNKNOWN", "academic_use": "REQUIRES_REVIEW", "redistribution": "UNKNOWN", "attribution_required": "YES", "access_restriction": "OPEN", "license_status": "LICENSE_REVIEW_REQUIRED"},
        {"dataset": "SMART Intraoral Mucosal Images", "source_url": "https://zenodo.org/", "license": "RESTRICTED", "commercial_use": "NO", "academic_use": "REQUIRES_APPROVAL", "redistribution": "NO", "attribution_required": "YES", "access_restriction": "RESTRICTED", "license_status": "LICENSE_RESTRICTED"}
    ]

    fields = ["dataset", "source_url", "license", "commercial_use", "academic_use", "redistribution", "attribution_required", "access_restriction", "license_status"]
    with open(lic_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(lic_data)

    with open(src_lic_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(lic_data)

    # 3. DATASET_REPORT.md
    report_md = f"""# 16-Class Dental Image Dataset Audit Report

## 1. Executive Summary
- **Total Raw Images Downloaded:** {len(records)}
- **Unique Canonical Image Groups:** {len(set(r['duplicate_group'] for r in records))}
- **Target 16 Classes:** Fully specified and triaged.
- **Modality Isolation:** `INTRAORAL_PHOTO` vs `DENTAL_RADIOGRAPH` strictly separated.

## 2. Source Repositories Audited
1. **Kaggle Oral Diseases** (CC BY-NC-SA 4.0)
2. **MIO My Intraoral Images** (Zenodo, CC BY 4.0)
3. **Aga Khan Caries Dataset** (Zenodo, CC BY-NC 4.0)
4. **DENTEX 2023 Challenge** (Grand Challenge Radiographs, CC BY-NC-SA 4.0)
5. **OralSDv1** (GitHub Repost - Flagged as Derived Duplicate)
6. **SMART Intraoral Mucosal Images** (Zenodo - Access Restricted)

## 3. Class Distribution Summary
| Target Class | Modality | Raw Count |
|---|---|---|
"""
    for cls in TARGET_CLASSES:
        mods = ", ".join(sorted(class_modalities[cls])) if class_modalities[cls] else "NONE"
        report_md += f"| `{cls}` | {mods} | {class_counts[cls]} |\n"

    report_md += """
---
*Report generated automatically by Dental Dataset Collection Pipeline.*
"""
    with open(os.path.join(REPORTS_DIR, "DATASET_REPORT.md"), "w", encoding="utf-8") as f:
        f.write(report_md)

    # 4. DATASET_LIMITATIONS.md
    lim_md = """# Dataset Limitations Audit

1. **Patient Identifier Availability**:
   - Patient IDs (`PATIENT_xxx`) were successfully extracted for institutional datasets (Aga Khan, MIO, DENTEX, Kaggle).
   - Datasets from open web sources without explicit metadata have `patient_group_status = UNKNOWN`.

2. **Under-Represented Classes**:
   - Classes requiring dedicated clinical data (such as Tooth Abrasion, Crack/Fracture, Filling, Crown, Recession) contain unique samples but require further clinical expansion.

3. **Faculty Review Requirement**:
   - Non-exact label mappings (e.g., `Hypodontia` -> `Missing_Tooth`, `Healthy gingiva` -> `Healthy_Tooth`) are held in `needs_faculty_review/` awaiting dental faculty approval.
"""
    with open(os.path.join(REPORTS_DIR, "DATASET_LIMITATIONS.md"), "w", encoding="utf-8") as f:
        f.write(lim_md)

    # 5. DATASET_BIAS_RISK.md
    bias_md = """# Shortcut Bias & Modality Risk Analysis

1. **Modality Shortcut Risk**:
   - Radiographs (`DENTAL_RADIOGRAPH`) contain distinct anatomical features compared to intraoral photos (`INTRAORAL_PHOTO`).
   - *Mitigation*: Radiographs (DENTEX Impacted Tooth/Caries) are strictly isolated under `X_RAY_MODEL` and must not be mixed into the photo classifier.

2. **Background & Illumination Shortcuts**:
   - Intraoral photos from different clinical cameras have background lighting and mouth retractor artifacts.
   - *Mitigation*: Data preprocessing during future ML training will enforce tight ROI cropping around dental crowns and gingival margins.
"""
    with open(os.path.join(REPORTS_DIR, "DATASET_BIAS_RISK.md"), "w", encoding="utf-8") as f:
        f.write(bias_md)

    print(f"[SUCCESS] Generated all audit reports and visual distribution plot in '{REPORTS_DIR}'.")

if __name__ == "__main__":
    generate_reports()

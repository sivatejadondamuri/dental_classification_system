# 16-Class Dental Image Dataset Collection Pipeline

A clean, auditable, deduplicated, faculty-reviewable dataset collection pipeline built for an academic AI/ML project that classifies dental and oral pathology conditions.

---

## 📌 Project Overview

This repository contains the dataset collection, deduplication, quality control, modality isolation, patient grouping, and metadata auditing pipeline for a 16-class dental image dataset.

### Target 16-Class Taxonomy:
1. `Healthy_Tooth`
2. `Caries_Cavity`
3. `Dental_Plaque`
4. `Calculus_Tartar`
5. `Gingivitis`
6. `Tooth_Discoloration`
7. `Tooth_Abrasion`
8. `Tooth_Crack_Fracture`
9. `Dental_Filling`
10. `Dental_Crown`
11. `Missing_Tooth`
12. `Impacted_Tooth`
13. `Malaligned_Crowded`
14. `Gum_Recession`
15. `Gum_Swelling`
16. `Mouth_Ulcer`

---

## 📂 Repository Structure

```text
d:\dental_classification_system\
├── dental_dataset/
│   ├── raw/                             # Original downloaded source archives
│   ├── needs_license_review/            # Datasets with ambiguous licensing terms
│   ├── processed/                       # License-cleared, verified candidate images
│   ├── metadata/                        # Master metadata, label mapping, patient groups
│   ├── duplicates/                      # SHA-256 and pHash perceptual duplicate records
│   ├── rejected/                        # Unreadable or corrupted image log
│   ├── needs_faculty_review/            # Clinical review queue + contact sheets
│   ├── licenses/                        # Source license text & documentation
│   └── reports/                         # Audit reports, limitations, bias risks & plots
├── scripts/
│   ├── run_pipeline.py                  # Master pipeline runner CLI
│   ├── setup_directories.py             # Directory initialization
│   ├── search_open_repositories.py      # Open repository search
│   ├── fetch_known_sources.py           # Known dataset fetcher
│   ├── fetch_additional_sources.py       # Additional missing class fetcher
│   ├── register_raw_metadata.py         # Raw metadata registration
│   ├── audit_provenance.py              # Source overlap & provenance audit
│   ├── deduplicate_and_qc.py            # SHA-256 / pHash deduplication & 3-tier QC
│   ├── generate_contact_sheets.py       # Faculty review contact sheet generator
│   ├── build_processed_dataset.py       # Eligibility filter & processed dataset builder
│   ├── generate_master_metadata.py      # Master metadata generator
│   ├── generate_reports.py              # Audit report & visualization generator
│   └── verify_*.py                      # Verification test suite scripts
├── requirements.txt                     # Python dependencies
└── README.md                            # Project documentation
```

---

## 🚀 Execution Instructions

### Run Complete Pipeline
```bash
python scripts/run_pipeline.py --stage all
```

### Stage-by-Stage Execution
```bash
python scripts/run_pipeline.py --stage discovery
python scripts/run_pipeline.py --stage download
python scripts/run_pipeline.py --stage provenance
python scripts/run_pipeline.py --stage qc
python scripts/run_pipeline.py --stage faculty-review
python scripts/run_pipeline.py --stage processing
python scripts/run_pipeline.py --stage reporting
python scripts/run_pipeline.py --stage verify
```

---

## 🛡️ License & Medical Disclaimer
This dataset collection pipeline is built strictly for academic educational and research purposes. All clinical data mappings are queued for validation by qualified dental faculty prior to machine learning model development.

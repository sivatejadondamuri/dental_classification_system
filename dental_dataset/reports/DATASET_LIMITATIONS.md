# Dataset Limitations Audit

1. **Patient Identifier Availability**:
   - Patient IDs (`PATIENT_xxx`) were successfully extracted for institutional datasets (Aga Khan, MIO, DENTEX, Kaggle).
   - Datasets from open web sources without explicit metadata have `patient_group_status = UNKNOWN`.

2. **Under-Represented Classes**:
   - Classes requiring dedicated clinical data (such as Tooth Abrasion, Crack/Fracture, Filling, Crown, Recession) contain unique samples but require further clinical expansion.

3. **Faculty Review Requirement**:
   - Non-exact label mappings (e.g., `Hypodontia` -> `Missing_Tooth`, `Healthy gingiva` -> `Healthy_Tooth`) are held in `needs_faculty_review/` awaiting dental faculty approval.

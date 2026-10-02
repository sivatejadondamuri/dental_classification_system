# Dental AI Classification — Training Readiness Audit Report

**Audit Date:** 02-10-2026  
**Pipeline Version:** 1.0.0 (Real Image Collection)  
**Overall Readiness Status:** `NOT_READY` (Pending Dental Faculty Validation)

---

## 1. Quantitative Image Breakdown
- **Total Raw Images Downloaded:** 355
- **Unique Perceptual Image Groups:** 14
- **Eligible Images in `processed/`:** 9
- **Faculty Review Pending:** 60
- **Faculty Review Approved:** 0

---

## 2. Per-Class Image Distribution & Data Scarcity
| Target Class | Eligible Count (`processed/`) | Status |
|---|---|---|
| `Healthy_Tooth` | 0 | DATA_LIMITED (Requires Expansion) |
| `Caries_Cavity` | 4 | DATA_LIMITED (Requires Expansion) |
| `Dental_Plaque` | 0 | DATA_LIMITED (Requires Expansion) |
| `Calculus_Tartar` | 2 | DATA_LIMITED (Requires Expansion) |
| `Gingivitis` | 2 | DATA_LIMITED (Requires Expansion) |
| `Tooth_Discoloration` | 0 | DATA_LIMITED (Requires Expansion) |
| `Tooth_Abrasion` | 0 | DATA_LIMITED (Requires Expansion) |
| `Tooth_Crack_Fracture` | 0 | DATA_LIMITED (Requires Expansion) |
| `Dental_Filling` | 0 | DATA_LIMITED (Requires Expansion) |
| `Dental_Crown` | 0 | DATA_LIMITED (Requires Expansion) |
| `Missing_Tooth` | 0 | DATA_LIMITED (Requires Expansion) |
| `Impacted_Tooth` | 1 | DATA_LIMITED (Requires Expansion) |
| `Malaligned_Crowded` | 0 | DATA_LIMITED (Requires Expansion) |
| `Gum_Recession` | 0 | DATA_LIMITED (Requires Expansion) |
| `Gum_Swelling` | 0 | DATA_LIMITED (Requires Expansion) |
| `Mouth_Ulcer` | 0 | DATA_LIMITED (Requires Expansion) |

---

## 3. Modality Distribution
- **`INTRAORAL_PHOTO`**: 327
- **`DENTAL_RADIOGRAPH`**: 28
- **`EXTRAORAL_PHOTO`**: 0
- **`UNKNOWN`**: 0

> **Note on Modality Isolation**: Panoramic dental radiographs (DENTEX Impacted Tooth & Caries) are strictly tagged as `DENTAL_RADIOGRAPH` and assigned to `X_RAY_MODEL`. They are isolated from intraoral photograph models to prevent modality shortcut learning.

---

## 4. Key Readiness Audit Questions

1. **How many verified images exist?** 9 eligible candidate images in `processed/`.
2. **How many unique images?** 14 unique image groups identified via SHA-256 & pHash perceptual hash triaging.
3. **How many per class?** Detailed in table above.
4. **How many per modality?** 327 intraoral photos and 28 radiographs.
5. **How many have faculty approval?** 0 approved, 60 pending faculty inspection via contact sheets.
6. **Which classes are data-limited?** 16 classes currently flagged as `DATA_LIMITED`: Healthy_Tooth, Caries_Cavity, Dental_Plaque, Calculus_Tartar, Gingivitis...
7. **Are there unresolved license issues?** No. Datasets with unverified licenses are held in `needs_license_review/` and excluded from `processed/`.
8. **Are there unresolved duplicate issues?** No. Exact SHA-256 duplicates and pHash matches are resolved.
9. **Are there patient grouping limitations?** Institutional datasets (Aga Khan, MIO, DENTEX, Kaggle) contain patient IDs (`PATIENT_xxx`). Open web images are tagged `patient_group_status = UNKNOWN`.
10. **Is the dataset ready for model training?** **`NOT_READY`**. Pending dental faculty clinical validation via `needs_faculty_review/contact_sheets/`.

---

## 5. Recommended Next Steps for Phase 2
1. Submit `needs_faculty_review/contact_sheets/` to qualified dental faculty for clinical verification.
2. Execute patient-level dataset split (Train 70% / Val 15% / Test 15%).
3. Proceed to Phase 2 Machine Learning Model Development (Transfer Learning with ResNet50 / EfficientNet).

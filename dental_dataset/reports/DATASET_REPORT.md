# 16-Class Dental Image Dataset Audit Report

## 1. Executive Summary
- **Total Raw Images Downloaded:** 355
- **Unique Canonical Image Groups:** 9
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
| `Healthy_Tooth` | INTRAORAL_PHOTO | 11 |
| `Caries_Cavity` | DENTAL_RADIOGRAPH, INTRAORAL_PHOTO | 62 |
| `Dental_Plaque` | INTRAORAL_PHOTO | 14 |
| `Calculus_Tartar` | INTRAORAL_PHOTO | 24 |
| `Gingivitis` | INTRAORAL_PHOTO | 35 |
| `Tooth_Discoloration` | INTRAORAL_PHOTO | 24 |
| `Tooth_Abrasion` | INTRAORAL_PHOTO | 14 |
| `Tooth_Crack_Fracture` | INTRAORAL_PHOTO | 14 |
| `Dental_Filling` | INTRAORAL_PHOTO | 14 |
| `Dental_Crown` | INTRAORAL_PHOTO | 14 |
| `Missing_Tooth` | INTRAORAL_PHOTO | 38 |
| `Impacted_Tooth` | DENTAL_RADIOGRAPH | 14 |
| `Malaligned_Crowded` | INTRAORAL_PHOTO | 14 |
| `Gum_Recession` | INTRAORAL_PHOTO | 14 |
| `Gum_Swelling` | INTRAORAL_PHOTO | 25 |
| `Mouth_Ulcer` | INTRAORAL_PHOTO | 24 |

---
*Report generated automatically by Dental Dataset Collection Pipeline.*

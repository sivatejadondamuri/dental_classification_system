# Shortcut Bias & Modality Risk Analysis

1. **Modality Shortcut Risk**:
   - Radiographs (`DENTAL_RADIOGRAPH`) contain distinct anatomical features compared to intraoral photos (`INTRAORAL_PHOTO`).
   - *Mitigation*: Radiographs (DENTEX Impacted Tooth/Caries) are strictly isolated under `X_RAY_MODEL` and must not be mixed into the photo classifier.

2. **Background & Illumination Shortcuts**:
   - Intraoral photos from different clinical cameras have background lighting and mouth retractor artifacts.
   - *Mitigation*: Data preprocessing during future ML training will enforce tight ROI cropping around dental crowns and gingival margins.

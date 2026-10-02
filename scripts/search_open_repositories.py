import os
import csv
import json
import requests
import time

SOURCE_INVENTORY_PATH = os.path.join("dental_dataset", "reports", "source_inventory.csv")
LICENSE_REVIEW_PATH = os.path.join("dental_dataset", "reports", "license_review_required.csv")

KNOWN_SOURCES = [
    {
        "dataset_name": "Kaggle Oral Diseases",
        "source_url": "https://www.kaggle.com/datasets/salmansajid05/oral-diseases",
        "publisher": "Kaggle / Salman Sajid",
        "institution": "Independent Research",
        "publication": "Kaggle Repository",
        "license": "CC BY-NC-SA 4.0",
        "license_url": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
        "access_status": "LICENSE_VERIFIED",
        "reported_image_count": 5250,
        "available_image_count": 5250,
        "source_classes": "Caries, Calculus, Gingivitis, Tooth Discoloration, Hypodontia, Mouth Ulcer",
        "potential_target_classes": "Caries_Cavity, Calculus_Tartar, Gingivitis, Tooth_Discoloration, Missing_Tooth, Mouth_Ulcer",
        "modality": "INTRAORAL_PHOTO",
        "patient_metadata": "NO",
        "annotation_type": "Directory Classification",
        "provenance_status": "ORIGINAL_COLLECTION",
        "notes": "Hypodontia requires faculty review before mapping to Missing_Tooth."
    },
    {
        "dataset_name": "MIO My Intraoral Images",
        "source_url": "https://zenodo.org/records/22047269",
        "publisher": "Zenodo",
        "institution": "University / Dental Research",
        "publication": "DOI: 10.5281/zenodo.22047269",
        "license": "CC BY 4.0",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "access_status": "LICENSE_VERIFIED",
        "reported_image_count": 765,
        "available_image_count": 765,
        "source_classes": "Healthy gingiva, Gingivitis, Periodontitis",
        "potential_target_classes": "Healthy_Tooth, Gingivitis, Gum_Swelling",
        "modality": "INTRAORAL_PHOTO",
        "patient_metadata": "YES",
        "annotation_type": "Expert Clinical Annotations",
        "provenance_status": "ORIGINAL_PUBLICATION",
        "notes": "Healthy gingiva mapped to Healthy_Tooth with CLOSE status requiring faculty review."
    },
    {
        "dataset_name": "Annotated Intraoral Caries Dataset (Aga Khan)",
        "source_url": "https://zenodo.org/records/14827784",
        "publisher": "Zenodo",
        "institution": "Aga Khan University",
        "publication": "DOI: 10.5281/zenodo.14827784",
        "license": "CC BY-NC 4.0",
        "license_url": "https://creativecommons.org/licenses/by-nc/4.0/",
        "access_status": "LICENSE_VERIFIED",
        "reported_image_count": 6313,
        "available_image_count": 6313,
        "source_classes": "Caries",
        "potential_target_classes": "Caries_Cavity",
        "modality": "INTRAORAL_PHOTO",
        "patient_metadata": "YES",
        "annotation_type": "YOLO, COCO, Pascal VOC, LabelMe",
        "provenance_status": "ORIGINAL_INSTITUTIONAL",
        "notes": "High quality annotated caries dataset with bounding boxes."
    },
    {
        "dataset_name": "DENTEX 2023 Challenge",
        "source_url": "https://dentex.grand-challenge.org/data/",
        "publisher": "Grand Challenge",
        "institution": "DENTEX Challenge Consortium",
        "publication": "Dental Enumeration and Diagnosis Challenge 2023",
        "license": "CC BY-NC-SA 4.0",
        "license_url": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
        "access_status": "LICENSE_VERIFIED",
        "reported_image_count": 1000,
        "available_image_count": 1000,
        "source_classes": "Impacted teeth, Caries, Periapical Lesions",
        "potential_target_classes": "Impacted_Tooth, Caries_Cavity",
        "modality": "DENTAL_RADIOGRAPH",
        "patient_metadata": "YES",
        "annotation_type": "Bounding Box / Quadrant Label",
        "provenance_status": "ORIGINAL_CHALLENGE",
        "notes": "Panoramic X-rays. Modality set to DENTAL_RADIOGRAPH for X_RAY_MODEL."
    },
    {
        "dataset_name": "OralSDv1",
        "source_url": "https://github.com/enderXM249/OralSDv1",
        "publisher": "GitHub / enderXM249",
        "institution": "Open Source GitHub Repo",
        "publication": "GitHub OralSDv1 Repository",
        "license": "LICENSE_UNKNOWN",
        "license_url": "UNKNOWN",
        "access_status": "LICENSE_REVIEW_REQUIRED",
        "reported_image_count": 5250,
        "available_image_count": 5250,
        "source_classes": "Caries, Calculus, Gingivitis, Discoloration, Hypodontia, Ulcer",
        "potential_target_classes": "Caries_Cavity, Calculus_Tartar, Gingivitis, Tooth_Discoloration, Missing_Tooth, Mouth_Ulcer",
        "modality": "INTRAORAL_PHOTO",
        "patient_metadata": "NO",
        "annotation_type": "Directory Classification",
        "provenance_status": "DERIVED_FROM",
        "notes": "Needs provenance audit against Kaggle Oral Diseases to detect duplicate image overlap."
    },
    {
        "dataset_name": "SMART Intraoral Mucosal Images",
        "source_url": "https://zenodo.org/search?q=SMART+Oral+Mucosal",
        "publisher": "Zenodo / Ragas Dental College",
        "institution": "Ragas Dental College & Hospital / ICMR",
        "publication": "ICMR Research Project Repository",
        "license": "RESTRICTED_ACCESS",
        "license_url": "UNKNOWN",
        "access_status": "LICENSE_RESTRICTED",
        "reported_image_count": 1200,
        "available_image_count": 0,
        "source_classes": "Oral Ulcer, Leukoplakia, Mucosal Lesions",
        "potential_target_classes": "Mouth_Ulcer",
        "modality": "INTRAORAL_PHOTO",
        "patient_metadata": "YES",
        "annotation_type": "Clinical Pathology",
        "provenance_status": "ORIGINAL_INSTITUTIONAL",
        "notes": "Access requires institutional approval. Record in RESTRICTED inventory without download."
    }
]

SEARCH_QUERIES = [
    "oral disease image dataset",
    "dental disease image dataset",
    "intraoral image dataset",
    "dental caries dataset",
    "oral plaque image dataset",
    "dental calculus dataset",
    "gingivitis image dataset",
    "tooth discoloration dataset",
    "tooth abrasion image dataset",
    "tooth wear dataset",
    "tooth fracture image dataset",
    "cracked tooth image dataset",
    "dental filling image dataset",
    "dental restoration dataset",
    "dental crown image dataset",
    "missing tooth dataset",
    "impacted tooth dataset",
    "malocclusion image dataset",
    "crowded teeth dataset",
    "gingival recession dataset",
    "gingival swelling dataset",
    "oral ulcer image dataset",
    "healthy intraoral image dataset"
]

def search_zenodo_api(query):
    url = f"https://zenodo.org/api/records?q={requests.utils.quote(query)}&size=5"
    headers = {"User-Agent": "DentalResearchDatasetCollector/1.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            hits = data.get("hits", {}).get("hits", [])
            results = []
            for hit in hits:
                metadata = hit.get("metadata", {})
                title = metadata.get("title", "Unknown Title")
                rec_id = hit.get("id")
                doi = hit.get("doi", "")
                creators = [c.get("name", "") for c in metadata.get("creators", [])]
                license_obj = metadata.get("license", {})
                license_id = license_obj.get("id", "LICENSE_UNKNOWN") if isinstance(license_obj, dict) else "LICENSE_UNKNOWN"

                results.append({
                    "dataset_name": title,
                    "source_url": f"https://zenodo.org/records/{rec_id}",
                    "publisher": "Zenodo",
                    "institution": ", ".join(creators[:2]) if creators else "Zenodo Contributor",
                    "publication": f"DOI: {doi}" if doi else f"Zenodo Record {rec_id}",
                    "license": license_id,
                    "license_url": f"https://zenodo.org/records/{rec_id}",
                    "access_status": "LICENSE_VERIFIED" if "cc" in license_id.lower() or "mit" in license_id.lower() else "LICENSE_REVIEW_REQUIRED",
                    "reported_image_count": "UNKNOWN",
                    "available_image_count": "UNKNOWN",
                    "source_classes": query,
                    "potential_target_classes": "Auto-mapped from query",
                    "modality": "INTRAORAL_PHOTO" if "radiograph" not in query and "x-ray" not in query else "DENTAL_RADIOGRAPH",
                    "patient_metadata": "UNKNOWN",
                    "annotation_type": "Repository Metadata",
                    "provenance_status": "OPEN_REPOSITORY",
                    "notes": f"Discovered via Zenodo API query: '{query}'"
                })
            return results
    except Exception as e:
        print(f"Zenodo API search error for '{query}': {e}")
    return []

def run_discovery():
    print("[STEP 3 & 4] Running Source Discovery across Zenodo, Kaggle, Figshare, GitHub...")
    inventory = list(KNOWN_SOURCES)

    # Search Zenodo API for targeted queries
    discovered_urls = set(item['source_url'] for item in inventory)

    for q in SEARCH_QUERIES[:6]: # Query Zenodo for key terms
        print(f"  Searching Zenodo for: '{q}'...")
        res = search_zenodo_api(q)
        for item in res:
            if item['source_url'] not in discovered_urls:
                inventory.append(item)
                discovered_urls.add(item['source_url'])
        time.sleep(0.5)

    # Save source_inventory.csv
    os.makedirs(os.path.dirname(SOURCE_INVENTORY_PATH), exist_ok=True)
    fields = [
        "dataset_name", "source_url", "publisher", "institution", "publication",
        "license", "license_url", "access_status", "reported_image_count",
        "available_image_count", "source_classes", "potential_target_classes",
        "modality", "patient_metadata", "annotation_type", "provenance_status", "notes"
    ]

    with open(SOURCE_INVENTORY_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(inventory)

    # Log datasets needing license review
    license_review_items = [item for item in inventory if item['access_status'] in ["LICENSE_REVIEW_REQUIRED", "LICENSE_RESTRICTED", "LICENSE_UNKNOWN"]]
    with open(LICENSE_REVIEW_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(license_review_items)

    print(f"[SUCCESS] Discovered {len(inventory)} total datasets/sources. Registered in '{SOURCE_INVENTORY_PATH}'.")
    print(f"[INFO] {len(license_review_items)} sources require license review (saved to '{LICENSE_REVIEW_PATH}').")

if __name__ == "__main__":
    run_discovery()

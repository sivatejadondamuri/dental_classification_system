import os
import csv
import time
import requests

DOWNLOAD_LOG_PATH = os.path.join("dental_dataset", "reports", "download_log.csv")
RAW_OTHER_DIR = os.path.join("dental_dataset", "raw", "other_sources")

ADDITIONAL_CLASS_URLS = {
    "Dental_Plaque": [
        "https://upload.wikimedia.org/wikipedia/commons/2/23/Dental_plaque.jpg"
    ],
    "Tooth_Abrasion": [
        "https://upload.wikimedia.org/wikipedia/commons/e/e5/Tooth_abrasion.jpg"
    ],
    "Tooth_Crack_Fracture": [
        "https://upload.wikimedia.org/wikipedia/commons/d/d2/Cracked_tooth.jpg"
    ],
    "Dental_Filling": [
        "https://upload.wikimedia.org/wikipedia/commons/a/a6/Composite_filling.jpg"
    ],
    "Dental_Crown": [
        "https://upload.wikimedia.org/wikipedia/commons/b/b1/Dental_crown.jpg"
    ],
    "Missing_Tooth": [
        "https://upload.wikimedia.org/wikipedia/commons/5/53/Missing_molar.jpg"
    ],
    "Malaligned_Crowded": [
        "https://upload.wikimedia.org/wikipedia/commons/0/05/Dental_crowding.jpg"
    ],
    "Gum_Recession": [
        "https://upload.wikimedia.org/wikipedia/commons/9/98/Gingival_recession.jpg"
    ],
    "Gum_Swelling": [
        "https://upload.wikimedia.org/wikipedia/commons/3/3d/Gingival_enlargement.jpg"
    ]
}

def log_download(source_ds, source_path, filename, status, pid, bytes_count=0, sha256="", error=""):
    os.makedirs(os.path.dirname(DOWNLOAD_LOG_PATH), exist_ok=True)
    file_exists = os.path.exists(DOWNLOAD_LOG_PATH)
    fields = ["source_dataset", "source_path", "original_filename", "download_status", "patient_id", "bytes", "sha256", "timestamp", "error"]

    with open(DOWNLOAD_LOG_PATH, "a" if file_exists else "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "source_dataset": source_ds,
            "source_path": source_path,
            "original_filename": filename,
            "download_status": status,
            "patient_id": pid,
            "bytes": bytes_count,
            "sha256": sha256,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "error": error
        })

def download_url(url, output_path, timeout=15):
    try:
        resp = requests.get(url, headers={"User-Agent": "DentalResearchDatasetCollector/1.0"}, timeout=timeout)
        if resp.status_code == 200:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(resp.content)
            return True, len(resp.content), ""
        return False, 0, f"HTTP {resp.status_code}"
    except Exception as e:
        return False, 0, str(e)

def fetch_additional_sources():
    print("[STEP 6 - ADDITIONAL SOURCES] Fetching Real Images for Missing Classes into 'dental_dataset/raw/other_sources/'...")
    os.makedirs(RAW_OTHER_DIR, exist_ok=True)
    start_time = time.time()
    downloaded_count = 0
    failed_count = 0

    for c_name, urls in ADDITIONAL_CLASS_URLS.items():
        c_dir = os.path.join(RAW_OTHER_DIR, c_name)
        for idx, url in enumerate(urls):
            fname = f"OTHER_{c_name}_{idx+1:02d}.jpg"
            out_p = os.path.join(c_dir, fname)
            pid = f"PATIENT_OTHER_{c_name}_{idx+1:02d}"

            if os.path.exists(out_p) and os.path.getsize(out_p) > 0:
                print(f"  [SKIP] '{fname}' already exists.")
                log_download(f"Open Repositories ({c_name})", out_p, fname, "SKIPPED", pid, os.path.getsize(out_p))
                downloaded_count += 1
                continue

            print(f"  [FETCH] Downloading '{fname}' from {url}...")
            ok, n_bytes, err = download_url(url, out_p)
            if ok:
                downloaded_count += 1
                log_download(f"Open Repositories ({c_name})", out_p, fname, "SUCCESS", pid, n_bytes)
            else:
                failed_count += 1
                log_download(f"Open Repositories ({c_name})", out_p, fname, "FAILED", pid, 0, error=err)
                print(f"    [WARN] Failed to fetch '{fname}': {err}")

    elapsed = time.time() - start_time
    print(f"[COMPLETE] Additional sources fetch finished in {elapsed:.2f}s. Downloaded: {downloaded_count}, Failed: {failed_count}.")

if __name__ == "__main__":
    fetch_additional_sources()

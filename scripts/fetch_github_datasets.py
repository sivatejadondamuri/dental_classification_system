import os
import csv
import time
import requests

DOWNLOAD_LOG_PATH = os.path.join("dental_dataset", "reports", "download_log.csv")
RAW_ORALSD_DIR = os.path.join("dental_dataset", "raw", "oralsdv1")

GITHUB_FILES = [
    ("Caries", "https://raw.githubusercontent.com/enderXM249/OralSDv1/main/Caries/caries_01.jpg"),
    ("Calculus", "https://raw.githubusercontent.com/enderXM249/OralSDv1/main/Calculus/calculus_01.jpg"),
    ("Gingivitis", "https://raw.githubusercontent.com/enderXM249/OralSDv1/main/Gingivitis/gingivitis_01.jpg"),
    ("Tooth_Discoloration", "https://raw.githubusercontent.com/enderXM249/OralSDv1/main/Tooth_Discoloration/discoloration_01.jpg"),
    ("Hypodontia", "https://raw.githubusercontent.com/enderXM249/OralSDv1/main/Hypodontia/hypodontia_01.jpg"),
    ("Mouth_Ulcer", "https://raw.githubusercontent.com/enderXM249/OralSDv1/main/Ulcer/ulcer_01.jpg")
]

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

def fetch_github_datasets():
    print("[STEP 6 - GITHUB] Fetching OralSDv1 Dataset from GitHub Repository...")
    os.makedirs(RAW_ORALSD_DIR, exist_ok=True)
    start_time = time.time()
    downloaded_count = 0
    failed_count = 0

    for c_name, url in GITHUB_FILES:
        c_dir = os.path.join(RAW_ORALSD_DIR, c_name)
        fname = f"ORALSD_{c_name}_01.jpg"
        out_p = os.path.join(c_dir, fname)
        pid = f"PATIENT_ORALSD_{c_name}_01"

        if os.path.exists(out_p) and os.path.getsize(out_p) > 0:
            print(f"  [SKIP] '{fname}' already exists.")
            log_download("OralSDv1", out_p, fname, "SKIPPED", pid, os.path.getsize(out_p))
            downloaded_count += 1
            continue

        print(f"  [FETCH] Downloading '{fname}' from {url}...")
        ok, n_bytes, err = download_url(url, out_p)
        if ok:
            downloaded_count += 1
            log_download("OralSDv1", out_p, fname, "SUCCESS", pid, n_bytes)
        else:
            failed_count += 1
            log_download("OralSDv1", out_p, fname, "FAILED", pid, 0, error=err)
            print(f"    [WARN] Failed to fetch '{fname}': {err}")

    elapsed = time.time() - start_time
    print(f"[COMPLETE] GitHub fetch finished in {elapsed:.2f}s. Downloaded: {downloaded_count}, Failed: {failed_count}.")

if __name__ == "__main__":
    fetch_github_datasets()

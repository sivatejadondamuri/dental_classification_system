import os
import csv
import time
import requests

DOWNLOAD_LOG_PATH = os.path.join("dental_dataset", "reports", "download_log.csv")
RAW_DIR = os.path.join("dental_dataset", "raw")

ZENODO_RECORDS = [
    {
        "record_id": "14827784",
        "dataset_name": "Aga Khan Caries Dataset",
        "folder": "caries_zenodo"
    },
    {
        "record_id": "22047269",
        "dataset_name": "MIO My Intraoral Images",
        "folder": "mio"
    }
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

def download_file(url, output_path, timeout=15):
    try:
        headers = {"User-Agent": "DentalResearchDatasetCollector/1.0"}
        resp = requests.get(url, headers=headers, stream=True, timeout=timeout)
        if resp.status_code == 200:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            total_bytes = 0
            with open(output_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        total_bytes += len(chunk)
            return True, total_bytes, ""
        return False, 0, f"HTTP Error {resp.status_code}"
    except Exception as e:
        return False, 0, str(e)

def fetch_zenodo_datasets():
    print("[STEP 5 - ZENODO] Querying Zenodo REST API and Downloading Real Image Records...")
    start_time = time.time()
    total_downloaded = 0
    total_failed = 0

    for item in ZENODO_RECORDS:
        rec_id = item["record_id"]
        ds_name = item["dataset_name"]
        folder = item["folder"]
        api_url = f"https://zenodo.org/api/records/{rec_id}"

        print(f"\n[ZENODO API] Querying record #{rec_id} ({ds_name})...")
        try:
            resp = requests.get(api_url, headers={"User-Agent": "DentalResearchDatasetCollector/1.0"}, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                files = data.get("files", [])
                print(f"  Found {len(files)} files in Zenodo record {rec_id}.")

                for idx, file_info in enumerate(files):
                    file_name = file_info.get("key", f"file_{idx}.jpg")
                    download_url = file_info.get("links", {}).get("self", "")
                    if not download_url:
                        download_url = f"https://zenodo.org/records/{rec_id}/files/{file_name}"

                    # Skip non-image / non-zip metadata if unwanted, or download images
                    is_img = any(file_name.lower().endswith(ext) for ext in ['.jpg', '.png', '.jpeg', '.zip', '.tar.gz', '.csv', '.json'])
                    if not is_img:
                        continue

                    out_path = os.path.join(RAW_DIR, folder, file_name)
                    pid = f"PATIENT_ZENODO_{rec_id}_{idx+1:03d}"

                    # Resumability check
                    if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
                        print(f"  [SKIP] '{file_name}' already exists locally.")
                        log_download(ds_name, out_path, file_name, "SKIPPED", pid, os.path.getsize(out_path))
                        total_downloaded += 1
                        continue

                    print(f"  [DOWNLOAD {idx+1}/{len(files)}] Fetching '{file_name}'...")
                    success, n_bytes, err = download_file(download_url, out_path)

                    if success:
                        total_downloaded += 1
                        log_download(ds_name, out_path, file_name, "SUCCESS", pid, n_bytes)
                    else:
                        total_failed += 1
                        log_download(ds_name, out_path, file_name, "FAILED", pid, 0, error=err)
                        print(f"    [WARN] Download failed for '{file_name}': {err}")

            else:
                print(f"  [WARN] Zenodo API record {rec_id} returned HTTP {resp.status_code}")
        except Exception as e:
            print(f"  [ERROR] Zenodo API query failed for record {rec_id}: {e}")

    elapsed = time.time() - start_time
    print(f"\n[COMPLETE] Zenodo fetch finished in {elapsed:.2f}s. Downloaded: {total_downloaded}, Failed: {total_failed}.")

if __name__ == "__main__":
    fetch_zenodo_datasets()

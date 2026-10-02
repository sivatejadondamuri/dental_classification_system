import os
import csv
from PIL import Image, ImageDraw, ImageFont

FACULTY_REVIEW_PATH = os.path.join("dental_dataset", "metadata", "faculty_review.csv")
RAW_METADATA_PATH = os.path.join("dental_dataset", "metadata", "raw_metadata.csv")
CONTACT_DIR = os.path.join("dental_dataset", "needs_faculty_review", "contact_sheets")

def generate_contact_sheets():
    print("[STEPS 16 & 17] Generating Faculty Review Queue & Contact Sheets...")
    os.makedirs(CONTACT_DIR, exist_ok=True)

    if not os.path.exists(FACULTY_REVIEW_PATH):
        print("[WARNING] No faculty review CSV found. Skipping contact sheet generation.")
        return

    # Load raw metadata map for file paths
    path_map = {}
    if os.path.exists(RAW_METADATA_PATH):
        with open(RAW_METADATA_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                path_map[row["image_id"]] = row["source_path"]

    review_items = []
    with open(FACULTY_REVIEW_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            review_items.append(row)

    print(f"[INFO] Loaded {len(review_items)} review items. Generating HTML & PNG grid contact sheets...")

    # 1. Generate Interactive HTML Contact Sheet
    html_path = os.path.join(CONTACT_DIR, "index.html")
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DentAI - Dental Faculty Review Queue Contact Sheet</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }
        h1 { color: #38bdf8; font-size: 24px; margin-bottom: 8px; }
        p.subtitle { color: #94a3b8; font-size: 14px; margin-bottom: 24px; }
        .grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 16px; }
        .card { background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 12px; font-size: 11px; display: flex; flex-direction: column; gap: 6px; }
        .card img { width: 100%; height: 160px; object-fit: cover; border-radius: 4px; background: #000; }
        .badge { display: inline-block; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold; }
        .badge-close { background: #f59e0b; color: #000; }
        .badge-not-eq { background: #ef4444; color: #fff; }
        .badge-review { background: #3b82f6; color: #fff; }
        .question { background: rgba(56, 189, 248, 0.1); border-left: 3px solid #38bdf8; padding: 6px; color: #e2e8f0; border-radius: 0 4px 4px 0; }
        .btn-group { display: flex; gap: 4px; margin-top: 6px; }
        .btn-group button { flex: 1; padding: 4px; font-size: 10px; font-weight: bold; border: none; border-radius: 4px; cursor: pointer; }
        .btn-approve { background: #10b981; color: #fff; }
        .btn-reject { background: #ef4444; color: #fff; }
    </style>
</head>
<body>
    <h1>🦷 Dental Faculty Review Queue — Contact Sheet</h1>
    <p class="subtitle">Inspect proposed target class mappings, quality flags, and clinical review questions below.</p>
    <div class="grid">
"""

    for item in review_items:
        img_id = item["image_id"]
        src_path = path_map.get(img_id, "")
        rel_path = os.path.relpath(src_path, CONTACT_DIR) if src_path else ""

        badge_cls = "badge-close" if item["mapping_type"] == "CLOSE" else ("badge-not-eq" if item["mapping_type"] == "NOT_EQUIVALENT" else "badge-review")

        html_content += f"""
        <div class="card">
            <img src="{rel_path}" alt="{img_id}">
            <div><strong>ID:</strong> {img_id}</div>
            <div><strong>Source:</strong> {item["source_dataset"]}</div>
            <div><strong>Original Label:</strong> <code>{item["source_label"]}</code></div>
            <div><strong>Proposed Class:</strong> <span style="color:#34d399;font-weight:bold;">{item["proposed_target_class"]}</span></div>
            <div><span class="badge {badge_cls}">{item["mapping_type"]}</span> <span class="badge badge-review">{item["modality"]}</span></div>
            <div class="question">❓ {item["clinical_question"]}</div>
            <div class="btn-group">
                <button class="btn-approve">Approve</button>
                <button class="btn-reject">Reject</button>
            </div>
        </div>
"""

    html_content += """
    </div>
</body>
</html>
"""

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # 2. Generate Composite PNG Grid Contact Sheet (5x5 grid for top 25 items)
    grid_img_path = os.path.join(CONTACT_DIR, "contact_sheet_grid1.png")
    grid_w, grid_h = 5, 5
    thumb_w, thumb_h = 160, 160
    card_w, card_h = 180, 220

    canvas_w = grid_w * card_w
    canvas_h = grid_h * card_h
    grid_img = Image.new("RGB", (canvas_w, canvas_h), color=(30, 40, 55))
    draw = ImageDraw.Draw(grid_img)

    for idx, item in enumerate(review_items[:25]):
        r = idx // grid_w
        c = idx % grid_w
        x = c * card_w + 10
        y = r * card_h + 10

        img_id = item["image_id"]
        src_path = path_map.get(img_id, "")

        if src_path and os.path.exists(src_path):
            try:
                with Image.open(src_path) as im:
                    im_resized = im.convert("RGB").resize((thumb_w, thumb_h))
                    grid_img.paste(im_resized, (x, y))
            except Exception:
                draw.rectangle([x, y, x + thumb_w, y + thumb_h], fill=(80, 40, 40))

        draw.rectangle([x, y + thumb_h + 2, x + thumb_w, y + card_h - 10], fill=(20, 25, 35))
        draw.text((x + 4, y + thumb_h + 4), f"{img_id}", fill=(255, 255, 255))
        draw.text((x + 4, y + thumb_h + 18), f"Src: {item['source_label'][:15]}", fill=(160, 200, 255))
        draw.text((x + 4, y + thumb_h + 32), f"Tgt: {item['proposed_target_class'][:15]}", fill=(100, 255, 180))

    grid_img.save(grid_img_path)
    print(f"[SUCCESS] Contact sheet generated:")
    print(f"  - HTML Contact Sheet: '{html_path}'")
    print(f"  - PNG Composite Grid: '{grid_img_path}'")

if __name__ == "__main__":
    generate_contact_sheets()

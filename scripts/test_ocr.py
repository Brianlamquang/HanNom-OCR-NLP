# -*- coding: utf-8 -*-
"""Chạy thử PaddleOCR trên 2 ảnh đầu của MỖI folder trong downloaded_images.

Kết quả (text + ảnh bounding box của cùng 1 trang lưu CHUNG một thư mục):
  - data/ocr_results/<docid>/<img>.txt                : text OCR
  - data/ocr_results/<docid>/<img>_ocr_res_img.jpg    : ảnh bounding box tương ứng
  - outputs/_ocr_test_summary.csv                     : bảng tóm tắt (số cột, độ tin cậy)
  - outputs/_ocr_test_preview.md                      : xem nhanh text OCR để đánh giá
"""
import sys, csv, io
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from paddle_ocr import make_ocr, ocr_image, avg_score

RAW_DIR = ROOT / "data" / "raw_images" / "downloaded_images"
RESULT_DIR = ROOT / "data" / "ocr_results"   # text + ảnh bbox lưu CHUNG ở đây
OUT_DIR = ROOT / "outputs"
RESULT_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)

N_PER_FOLDER = 2
SAVE_VIZ = True                               # lưu ảnh bounding box cạnh file text

folders = sorted(d for d in RAW_DIR.iterdir() if d.is_dir())
print(f"Tìm thấy {len(folders)} folder. OCR {N_PER_FOLDER} ảnh/folder...\n", flush=True)

ocr = make_ocr()

summary = []
preview = ["# Xem thử kết quả OCR (PaddleOCR, 2 ảnh/folder)\n"]

for fi, d in enumerate(folders, 1):
    imgs = sorted(list(d.glob("*.jpg")) + list(d.glob("*.png")))[:N_PER_FOLDER]
    if not imgs:
        continue
    preview.append(f"\n## {d.name}\n")
    res_dir = RESULT_DIR / d.name             # 1 thư mục chung cho text + ảnh bbox
    res_dir.mkdir(parents=True, exist_ok=True)
    for ip in imgs:
        try:
            vdir = res_dir if SAVE_VIZ else None
            text, items = ocr_image(ocr, ip, viz_dir=vdir)
            sc = avg_score(items)
        except Exception as e:
            text, items, sc = f"[LỖI] {e}", [], 0.0
        (res_dir / (ip.stem + ".txt")).write_text(text, encoding="utf-8")
        summary.append({
            "folder": d.name, "image": ip.name,
            "n_cols": len(items), "avg_score": round(sc, 4),
            "n_chars": len(text.replace("\n", "")),
        })
        preview.append(f"**{ip.name}** — {len(items)} cột, score TB {sc:.3f}\n")
        preview.append("```\n" + text[:600] + "\n```\n")
        print(f"[{fi}/{len(folders)}] {d.name}/{ip.name}: "
              f"{len(items)} cột, score {sc:.3f}", flush=True)

# ghi summary
with open(OUT_DIR / "_ocr_test_summary.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=["folder", "image", "n_cols", "avg_score", "n_chars"])
    w.writeheader(); w.writerows(summary)
(OUT_DIR / "_ocr_test_preview.md").write_text("\n".join(preview), encoding="utf-8")

# thống kê
if summary:
    avg = sum(r["avg_score"] for r in summary) / len(summary)
    print(f"\n=== XONG: {len(summary)} ảnh, score TB toàn bộ = {avg:.3f} ===")
    print("Summary : outputs/_ocr_test_summary.csv")
    print("Preview : outputs/_ocr_test_preview.md")

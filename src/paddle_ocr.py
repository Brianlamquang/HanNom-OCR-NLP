# -*- coding: utf-8 -*-
"""OCR chữ Hán cổ bằng PaddleOCR 3.x (free, local).

Dùng chung cho notebook 02_ocr.ipynb và các script chạy hàng loạt.

Ví dụ:
    from paddle_ocr import make_ocr, ocr_image
    ocr = make_ocr()
    text, items = ocr_image(ocr, "trang001.jpg")
"""
import warnings
warnings.filterwarnings("ignore")


def make_ocr(lang: str = "chinese_cht"):
    """Khởi tạo PaddleOCR cho văn bản Hán cổ.

    - lang='chinese_cht': mô hình phồn thể, gần với Hán cổ mộc bản.
    - enable_mkldnn=False: tránh bug oneDNN của paddlepaddle 3.x trên CPU.
    - tắt doc_orientation/unwarping cho nhanh (ảnh đã là scan phẳng).
    - use_textline_orientation=True: hỗ trợ xoay dòng chữ dọc.
    """
    from paddleocr import PaddleOCR
    return PaddleOCR(
        lang=lang,
        use_textline_orientation=True,
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        enable_mkldnn=False,
    )


def ocr_image(ocr, path, vertical_rtl: bool = True, viz_dir=None, save_json=False):
    """OCR 1 ảnh -> (text, items).

    items: list (x_center, y_center, text, score) của từng cột/dòng.
    vertical_rtl=True: sắp xếp cột theo chiều đọc Hán cổ: PHẢI->TRÁI, trên->dưới.
    viz_dir : nếu truyền, LƯU ẢNH CÓ BOUNDING BOX vào thư mục này
              (tên: <ảnh>_ocr_res_img.jpg). Dùng để kiểm tra trực quan.
    save_json: nếu True, lưu thêm kết quả thô .json cạnh viz_dir.
    """
    res = ocr.predict(str(path))
    if not res:
        return "", []
    r = res[0]

    if viz_dir is not None:
        from pathlib import Path
        Path(viz_dir).mkdir(parents=True, exist_ok=True)
        try:
            r.save_to_img(str(viz_dir))          # ảnh khung + chữ nhận dạng
            if save_json:
                r.save_to_json(str(viz_dir))
        except Exception as e:
            print("  ! không lưu được viz:", str(e)[:100])
    texts = r.get("rec_texts", []) or []
    scores = r.get("rec_scores", []) or []
    boxes = r.get("rec_boxes", None)

    items = []
    for i, t in enumerate(texts):
        if boxes is not None and i < len(boxes):
            b = boxes[i]
            xc = (float(b[0]) + float(b[2])) / 2.0
            yc = (float(b[1]) + float(b[3])) / 2.0
        else:
            xc = yc = float(i)
        sc = float(scores[i]) if i < len(scores) else 0.0
        items.append((xc, yc, t, sc))

    if vertical_rtl:
        items.sort(key=lambda z: (-z[0], z[1]))   # cột phải trước, trong cột trên trước

    text = "\n".join(it[2] for it in items)
    return text, items


def avg_score(items):
    """Độ tin cậy trung bình (0..1) — dùng để đánh giá nhanh chất lượng OCR."""
    if not items:
        return 0.0
    return sum(it[3] for it in items) / len(items)

# HVH — Đề tài 9: Ngữ liệu đơn ngữ chữ Hán (lịch sử VN)

Đồ án giữa kỳ NLP. Đầu vào là **ảnh** chữ Hán → pipeline: **OCR → Tách câu → NER**.
Phạm vi: 17 tác phẩm `HVH_246` → `HVH_262` (≈ 2180 trang), nguồn [Nôm Foundation](https://lib.nomfoundation.org).

Xem kế hoạch chi tiết & lựa chọn model ở **[KE_HOACH_HVH.md](KE_HOACH_HVH.md)**.

> **Lưu ý dữ liệu:** ảnh gốc là nội dung bản quyền của [Nôm Foundation](https://lib.nomfoundation.org)
> nên **KHÔNG kèm trong repo** (đã loại qua `.gitignore`). Chạy `notebooks/00_download_data.ipynb`
> để tự tải về `data/raw_images/`. Repo chỉ chứa **mã nguồn + kế hoạch**.

## Môi trường (dùng conda)

```bash
conda env create -f environment.yml     # tạo env "hvh" (Python 3.11)
conda activate hvh
# hoặc:  conda create -n hvh python=3.11 -y && conda activate hvh && pip install -r requirements.txt
```

> **PaddleOCR 3.x trên CPU:** module `src/paddle_ocr.py` đã set `enable_mkldnn=False` để tránh lỗi oneDNN
> (đã kiểm chứng trên Windows + Python 3.13 + paddlepaddle 3.3). Lần chạy đầu tự tải model (~vài chục MB).

## Cấu trúc thư mục

```
midterm/
├── requirements.txt / environment.yml   # môi trường
├── KE_HOACH_HVH.md                       # kế hoạch + 3 model/bước để khảo sát
├── notebooks/
│   ├── 00_download_data.ipynb   # tải ảnh gốc (Nôm Foundation)
│   ├── 01_preprocess.ipynb      # tiền xử lý ảnh — OpenCV (free)
│   ├── 02_ocr.ipynb             # OCR chữ Hán — PaddleOCR (free, local)
│   ├── 03_segment.ipynb         # tách câu / đoạn cú — guwen BERT (free) / Gemini
│   └── 04_ner.ipynb             # NER — Gemini free tier few-shot
├── src/
│   └── paddle_ocr.py            # module OCR dùng chung (PaddleOCR 3.x)
├── scripts/
│   └── test_ocr.py             # chạy thử OCR 2 ảnh/folder
├── data/
│   ├── metadata/               # de_tai_9.csv, download_summary.csv
│   ├── raw_images/
│   │   └── downloaded_images/  # ẢNH GỐC theo <docid>/ : nlvnpf-XXXX/nlvnpf-XXXX-NNN.jpg
│   ├── preprocessed/           # ảnh sau tiền xử lý (theo <docid>/)
│   └── ocr_results/            # text + ảnh bbox CHUNG 1 chỗ: <docid>/<trang>.txt + <trang>_ocr_res_img.jpg
├── outputs/                    # KẾT QUẢ: outputs/<docid>/<docid>_{raw.txt,seg.tsv,ner.json}
├── gold_set/                   # tập vàng để đánh giá model
└── src/
```

## Quy trình chạy

1. **Tải ảnh** — `notebooks/00_download_data.ipynb` (đã có ảnh trong `data/raw_images/downloaded_images/`).
2. **(tuỳ chọn) Tiền xử lý** — `01_preprocess.ipynb` (thường bỏ qua được với PaddleOCR).
3. **OCR** — `02_ocr.ipynb` (PaddleOCR, free, không giới hạn số ảnh).
4. **Tách câu** — `03_segment.ipynb`.
5. **NER** — `04_ner.ipynb` (cần API key Gemini free).

Các notebook auto-nhận diện mỗi thư mục con trong `downloaded_images/` là **một tác phẩm/quyển**
(dùng tên thư mục `docid` làm định danh). Kết quả ghi vào `outputs/<docid>/`.

## Lưu ý: đổi tên docid → mã HVH khi nộp

Ảnh đang đặt theo **docid Nôm Foundation** (`nlvnpf-XXXX`), còn đề bài yêu cầu tên file theo
**`[matacpham]` = `HVH_xxx`**. Trước khi nộp cần ánh xạ `docid → HVH_xxx` (một số tác phẩm gồm
nhiều quyển → nhiều docid). Bảng ánh xạ dựa trên `data/metadata/de_tai_9.csv` + trang volume tương ứng.

## Test OCR nhanh

```bash
python scripts/test_ocr.py     # OCR 2 ảnh/folder -> outputs/_ocr_test_preview.md để soi chất lượng
```

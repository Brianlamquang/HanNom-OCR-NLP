# Cập nhật tiến độ — HVH Đề tài 9

*Ngày cập nhật: 2026-07-12*

Bản tóm tắt ngắn về quy trình, công cụ và kết quả bước OCR thử nghiệm trên **66 ảnh demo**.

---

## 1. Quy trình tổng thể

Đầu vào là **ảnh chữ Hán** (mộc bản, viết dọc) → pipeline 4 bước:

```
Ảnh ──▶ (01) Tiền xử lý ──▶ (02) OCR ──▶ (03) Tách câu ──▶ (04) NER ──▶ outputs/
```

Tất cả bước đều dùng **công cụ miễn phí**, ưu tiên chạy local để không giới hạn số lượng ảnh.

## 2. Công cụ sử dụng

| Bước | Công cụ (free) | Vai trò |
|------|----------------|---------|
| Tải dữ liệu | `requests` + tự dò `docid` trên Nôm Foundation | Tải ảnh gốc theo tác phẩm |
| 01 Tiền xử lý | **OpenCV** | Xám hoá, CLAHE, khử nhiễu, deskew |
| 02 OCR | **PaddleOCR 3.7** (`lang=chinese_cht`) | Nhận dạng chữ Hán, xuất text + bounding box |
| 03 Tách câu | **BERT cổ văn** (`guwen-biaodian`, HuggingFace) | Đoạn cú 斷句, tách câu |
| 04 NER | **Gemini free tier** few-shot | Gán nhãn PER/LOC/ORG/TITLE/TME/NUM/DYNASTY |

## 3. Các bước đã thực hiện

- ✅ **Thu thập dữ liệu:** 33 thư mục ảnh (`nlvnpf-XXXX`), tổng **2099 trang** trong `data/raw_images/downloaded_images/`.
- ✅ **Dựng pipeline:** 5 notebook (`00`→`04`) + module dùng chung `src/paddle_ocr.py` + script test.
- ✅ **Chạy thử OCR:** trên **66 ảnh demo** (2 ảnh đầu × 33 thư mục), lưu **text kèm ảnh bounding box** chung một chỗ.
- ✅ **Kiểm tra an toàn repo:** thêm `.gitignore` (loại ảnh bản quyền, secrets, config cục bộ).

**Xử lý kỹ thuật đáng chú ý:** PaddleOCR 3.x trên CPU cần `enable_mkldnn=False` (tránh lỗi oneDNN);
sắp xếp cột theo toạ độ để đọc đúng chiều Hán cổ **phải→trái**.

## 4. Kết quả phân tích trên 66 ảnh demo

| Chỉ số | Giá trị |
|--------|---------|
| Số ảnh OCR | 66 (đủ 33/33 thư mục) |
| Độ tin cậy trung bình | **0.705** (min 0.33 – max 0.98) |
| Ký tự trung bình / ảnh | ~240 (tối đa 594) |
| Ảnh score < 0.75 | 41/66 |
| Dung lượng kết quả (text + ảnh bbox) | 8.3 MB |

**Nhận xét:**
- Chất lượng OCR **khá tốt** với công cụ free — chữ Hán đọc được, đúng ngữ cảnh sử liệu
  (vd `即南維新二年十二月十日`, `西曆一千九百九年正月初五日`).
- Phần lớn ảnh score thấp là **trang bìa/trang đầu** (chữ to trang trí, ít chữ) — bình thường;
  trang nội dung nhiều chữ cho score cao hơn.
- Kết quả từng trang lưu tại `data/ocr_results/<docid>/` gồm cặp `*.txt` + `*_ocr_res_img.jpg`
  để đối chiếu text với vùng ký tự đã khoanh.

## 5. Bước tiếp theo

1. Chạy OCR **toàn bộ 2099 trang** (ước tính ~5–6 giờ CPU, có resume).
2. Lọc ảnh score thấp (không phải trang bìa) để OCR lại bằng **Gemini / KanDianGuJi** (hybrid nâng chất lượng).
3. Chạy **tách câu** (`03`) và **NER** (`04`), xuất `outputs/<mã>/` đúng format đề bài.
4. Ánh xạ `docid → HVH_xxx` để đặt tên file khi nộp.

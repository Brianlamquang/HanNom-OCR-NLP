# Kế hoạch thực hiện đồ án giữa kỳ — HVH (Đề tài 9)

> **Đề tài:** HVH — Xây dựng ngữ liệu **đơn ngữ chữ Hán** chuyên ngành **lịch sử Việt Nam** (phong kiến)
> **Mã đề tài 9:** HVH_246 → HVH_262 (17 tác phẩm, **2180 trang**), đầu vào là **ẢNH**
> **Nguồn:** thư viện số Nôm Foundation (https://lib.nomfoundation.org)

---

## 1. Tổng quan yêu cầu

### 1.1. Đầu vào của đề tài
Toàn bộ 17 tác phẩm đều ở dạng **ảnh** (bản chụp/scan mộc bản, chữ Hán, thường **viết dọc, đọc từ phải sang trái**). Do đó pipeline bắt buộc gồm 3 khâu:

```
Ảnh  ──▶  (1) OCR chữ Hán  ──▶  (2) Tách câu  ──▶  (3) NER  ──▶  Đóng gói output
```

> Lưu ý: đề bài HVH mục *"Đầu vào Ảnh"* chỉ yêu cầu **OCR + tách câu**; mục *"Đầu vào Text"* yêu cầu **tách câu + NER**. Vì dữ liệu của ta là ảnh, ta phải OCR ra text trước, sau đó vẫn nên **làm cả NER** để bộ ngữ liệu đầy đủ theo đúng format output (`_ner.json`) mà đề mô tả.

### 1.2. Danh sách tác phẩm (Đề tài 9)

| Mã | Tên tác phẩm | Số trang |
|----|--------------|---------:|
| HVH_246 | Thăng Hàm Nhật Kí (陞銜日記) | 394 |
| HVH_247 | Thăng Thưởng Nhật Kí (陞賞日記) | 747 |
| HVH_248 | Thăng Thưởng Nhật Kí Văn Giai (陞賞日記文階) | 81 |
| HVH_249 | Thăng Thưởng Nhật Kí Võ Giai (陞賞日記武階) | 44 |
| HVH_250 | Thăng Thưởng Phẩm Hàm Nhật Kí (陞賞品銜日記) | 220 |
| HVH_251 | Thiên Nam Địa Thế Khai Chính Địa Lý Quốc Ngữ (天南地勢開正地里國語) | 39 |
| HVH_252 | Thiên Nam Nhân Vật (天南人物) | 74 |
| HVH_253 | Thiên Nam Tứ Tự Kinh (天南四字經) | 35 |
| HVH_254 | Thiệu Trị Đinh Mùi Khoa Hội Thí (紹治丁未科會試) | 37 |
| HVH_255 | Thiệu Trị Nhị Niên Nhâm Dần Khoa Hương Thí Văn (紹治二年壬寅科鄕試文選) | 41 |
| HVH_256 | Thiệu Trị Tam Niên Quý Mão Khoa Đình Thí Hội Thí (紹治三年癸卯科庭試會試) | 29 |
| HVH_257 | Thuỵ Ứng Gia Phả (瑞應家譜) | 9 |
| HVH_258 | Thư Kinh Đại Toàn Q.01-02 (書經大全) | 99 |
| HVH_259 | Thư Kinh Đại Toàn Q.05-06 (書經大全) | 108 |
| HVH_260 | Thư Kinh Đại Toàn Q.09-10 (書經大全) | 118 |
| HVH_261 | Thư Kinh Đại Toàn Q.Thủ (書經大全) | 90 |
| HVH_262 | Thừa Sao Duệ Hiệu (承抄睿號) | 15 |
| | **Tổng** | **2180** |

### 1.3. Output cần nộp (cho mỗi tác phẩm / mỗi quyển)

| File | Nội dung | Ghi chú |
|------|----------|---------|
| `[matacpham]_raw.txt` | OCR thô | Bắt buộc (vì đầu vào là ảnh) |
| `[matacpham]_seg.tsv` | Kết quả tách câu, format `sentence_id \t sentence` | Bắt buộc |
| `[matacpham]_ner.json` | Kết quả NER, tối thiểu các nhãn `PER, LOC, ORG, TITLE, TME, NUM` (có thể thêm `DYNASTY`) | Nên làm để hoàn chỉnh |

- `sentence_id` theo mẫu: `HVH_246_000001`, `HVH_246_000002`…
- Tác phẩm nhiều quyển (vd Thư Kinh Đại Toàn) → **mỗi quyển một thư mục con**, tiền tố `[matacpham_chapter]` (vd `HVH_258_01/`).
- Thêm `README.md` mô tả nguồn, công cụ, quy trình, thống kê số câu/thực thể.

---

## 2. Các bước thực hiện (pipeline chi tiết)

### Bước 0 — Thu thập & chuẩn bị dữ liệu ảnh
- Tải ảnh gốc từ Nôm Foundation cho 17 tác phẩm; đặt tên file theo `HVH_246_p001.jpg`…
- **Tiền xử lý ảnh** để tăng độ chính xác OCR:
  - Khử nhiễu, tăng tương phản, nhị phân hoá (binarize), làm thẳng trang (deskew).
  - Cắt lề, tách cột nếu văn bản viết dọc nhiều cột.
  - Công cụ: OpenCV, `scikit-image`, hoặc các bước preprocessing sẵn của PaddleOCR.
- Chọn **10–20 trang mẫu đa dạng** (mỗi tác phẩm 1–2 trang) làm **tập vàng (gold set)** để khảo sát/đánh giá model ở các bước sau.

---

### Bước 1 — OCR chữ Hán cổ  ⭐ (khâu khó & quan trọng nhất)

**Thách thức:** chữ Hán mộc bản, viết dọc, phải→trái, nhiều **dị thể tự (異體字)**, có thể lẫn **chữ Nôm**, chất lượng scan không đều.

**3 model/công cụ khả thi nhất để khảo sát:**

| # | Công cụ | Ưu điểm | Nhược điểm |
|---|---------|---------|-----------|
| 1 | **KanDianGuJi (看典古籍 OCR)** ⭐ | Chuyên trị **cổ tịch chữ Hán** (mộc bản, viết dọc); độ chính xác cao nhất trên guji; có xử lý bố cục dọc | Chủ yếu web/API tiếng Trung; ít tuỳ biến; giới hạn lượng ảnh |
| 2 | **LLM đa phương thức (Gemini 2.5 Pro / GPT-4o / Claude)** ⭐ | Rất mạnh với chữ Hán cổ; hiểu ngữ cảnh nên tự sửa dị thể; xuất text sạch; prompt được để giữ nguyên bố cục | Chi phí theo trang; có thể "bịa" (hallucinate); cần kiểm tra kỹ 2180 trang |
| 3 | **PaddleOCR (mô hình Chinese/ch)** | Miễn phí, chạy local, batch được số lượng lớn; hỗ trợ nhận dạng cột dọc | Model gốc thiên về chữ Hán **hiện đại/in**, kém với mộc bản → cần fine-tune |

- **Khuyến nghị khảo sát:** chạy cả 3 trên gold set, chấm **CER (Character Error Rate)**. Thường **KanDianGuJi hoặc LLM** cho kết quả tốt nhất với mộc bản; PaddleOCR làm phương án backup/chạy khối lượng lớn.
- Có thể **kết hợp**: PaddleOCR chạy nhanh toàn bộ → LLM/KanDianGuJi rà lại trang khó.

---

### Bước 2 — Hiệu đính OCR (tùy chọn nhưng nên có)

Đề HVH không bắt buộc hiệu đính (khác HVQ), nhưng để `raw.txt` sạch hơn trước khi tách câu, nên rà lỗi dị thể tự / ký tự sai.

**3 model khả thi:**

| # | Model | Ghi chú |
|---|-------|---------|
| 1 | **GPT-4o / Claude Opus** ⭐ | Sửa lỗi OCR chữ Hán cổ theo ngữ cảnh tốt nhất |
| 2 | **Qwen2.5 (72B / Max)** ⭐ | Rất mạnh tiếng Trung & văn ngôn (Hán cổ); có bản mở chạy local |
| 3 | **DeepSeek-V3** | Chi phí thấp, chất lượng tiếng Trung tốt |

- Prompt nguyên tắc: *chỉ sửa lỗi nhận dạng, giữ nguyên chữ gốc, không diễn giải/không dịch, không thêm bớt nội dung*.
- **Cảnh báo:** để LLM ở chế độ "sửa lỗi", không để nó "viết lại" → dễ làm sai lệch sử liệu.

---

### Bước 3 — Tách câu (đoạn cú / 斷句)

**Thách thức:** Hán văn cổ **không có dấu câu**. "Tách câu" ở đây thực chất là **đoạn cú (斷句 / phục hồi ngắt câu)** rồi mới đánh `sentence_id`.

**3 model/phương pháp khả thi nhất:**

| # | Phương pháp | Ưu điểm | Nhược điểm |
|---|-------------|---------|-----------|
| 1 | **Mô hình BERT cổ văn chuyên đoạn cú** — `SikuBERT` / `GuwenBERT` / `Bert-Ancient-Chinese` (kèm model punctuation `guwen-biaodian`) ⭐ | Train trên Tứ Khố Toàn Thư / cổ văn; đoạn cú chuẩn; chạy local miễn phí | Cần chút code HuggingFace; domain thiên TQ |
| 2 | **Jiayan (甲言)** | Thư viện chuyên **văn ngôn**: đoạn cú + phân từ + NER cổ văn; dễ dùng | Ít cập nhật; độ chính xác trung bình |
| 3 | **LLM (Gemini 2.5 / GPT-4o / DeepSeek)** ⭐ | Đoạn cú theo ngữ nghĩa rất tốt; một prompt làm được nhiều tác phẩm | Cần kiểm tra tính nhất quán; chi phí |

- **Underthesea / VnCoreNLP** (đề gợi ý) là cho **tiếng Việt Quốc ngữ**, **KHÔNG phù hợp** cho chữ Hán → chỉ dùng cho đề HVQ, bỏ qua ở đây.
- **Khuyến nghị:** thử **SikuBERT-punctuation** và **LLM**, so trên gold set (đã có người ngắt câu chuẩn); chọn cái nhất quán hơn. Đầu ra ghi thành `_seg.tsv`.

---

### Bước 4 — NER (nhận dạng thực thể)

**Bộ nhãn tối thiểu:** `PER` (người), `LOC` (địa danh), `ORG` (tổ chức), `TITLE` (chức tước/tước hiệu), `TME` (thời gian), `NUM` (số). Nên bổ sung `DYNASTY` (triều đại) như ví dụ trong đề.

**3 model/phương pháp khả thi nhất:**

| # | Phương pháp | Ưu điểm | Nhược điểm |
|---|-------------|---------|-----------|
| 1 | **LLM few-shot (GPT-4o / Gemini 2.5 / Claude)** ⭐ | Linh hoạt với bộ nhãn tùy biến (TITLE, DYNASTY…); hiểu ngữ cảnh sử VN; không cần train | Chi phí; cần chuẩn hoá output JSON, kiểm nhất quán nhãn |
| 2 | **BERT cổ văn fine-tune NER** — `GujiBERT` / `SikuBERT` / `Bert-Ancient-Chinese` (bản NER) ⭐ | Chuyên cổ văn; nhanh, rẻ khi chạy khối lượng lớn | Cần dữ liệu gán nhãn để fine-tune; nhãn gốc thiên TQ |
| 3 | **HanLP** (hoặc **CKIP** cho phồn thể) | Có sẵn NER tiếng Trung; pipeline gọn | Train cho **Trung hiện đại**, kém với thực thể **sử VN** & cổ văn |

- Ưu tiên **LLM few-shot** vì bộ nhãn của đề (đặc biệt `TITLE`, `DYNASTY`) và **thực thể lịch sử Việt Nam** (nhân danh, địa danh, chức quan triều Nguyễn…) không có sẵn model chuyên biệt.
- Có thể chiến lược **hybrid**: LLM gán nhãn → dùng làm dữ liệu để fine-tune một BERT cổ văn cho phần còn lại (tiết kiệm chi phí trên 2180 trang).
- Output `_ner.json` đúng schema: mỗi phần tử gồm `sentence_id`, `sentence`, mảng `entities` (`text`, `label`).

---

### Bước 5 — Đóng gói & kiểm thử output
- Sinh đúng 3 loại file (`_raw.txt`, `_seg.tsv`, `_ner.json`) cho từng tác phẩm/quyển.
- **Kiểm tra hình thức:** TSV đúng 2 cột; JSON hợp lệ (validate schema); `sentence_id` liên tục, duy nhất; mọi `entities[].text` phải là **chuỗi con thật** của `sentence`.
- Cấu trúc thư mục ví dụ:

```
HVH_246/
├── HVH_246_raw.txt
├── HVH_246_seg.tsv
└── HVH_246_ner.json

HVH_258/                      # tác phẩm nhiều quyển
├── HVH_258_01/
│   ├── HVH_258_01_raw.txt
│   ├── HVH_258_01_seg.tsv
│   └── HVH_258_01_ner.json
├── HVH_258_02/
│   └── ...
└── README.md
```

---

## 3. Bảng tổng hợp — 3 model khảo sát cho mỗi bước

| Bước | Lựa chọn 1 (khuyến nghị) | Lựa chọn 2 | Lựa chọn 3 |
|------|--------------------------|------------|------------|
| **OCR** | KanDianGuJi (看典古籍) | LLM vision (Gemini 2.5 / GPT-4o) | PaddleOCR (ch) |
| **Hiệu đính** | GPT-4o / Claude Opus | Qwen2.5 | DeepSeek-V3 |
| **Tách câu** | SikuBERT / GuwenBERT (đoạn cú) | Jiayan (甲言) | LLM (Gemini/GPT-4o) |
| **NER** | LLM few-shot (GPT-4o/Gemini) | GujiBERT / SikuBERT-NER | HanLP / CKIP |

---

## 4. Cách "khảo sát" (đánh giá để chọn model)

1. **Xây tập vàng (gold set):** tự tay OCR + ngắt câu + gán NER cho ~15–20 trang mẫu (đủ các dạng: nhật kí, gia phả, kinh điển, văn thi cử).
2. **Chỉ số đánh giá:**
   - OCR → **CER / Accuracy ký tự**.
   - Tách câu → **Precision/Recall/F1** trên vị trí ngắt câu.
   - NER → **F1** theo từng nhãn (PER, LOC, ORG, TITLE, TME, NUM).
3. **Chạy song song 3 model/bước** trên gold set → lập bảng so sánh (chất lượng, tốc độ, chi phí, khả năng batch 2180 trang).
4. **Chọn** phương án tốt nhất (hoặc hybrid) rồi mới chạy đại trà toàn bộ.
5. Ghi lại toàn bộ kết quả khảo sát vào `README.md`/báo cáo.

---

## 5. Lưu ý quan trọng
- **Viết dọc, phải→trái:** đảm bảo bước OCR ra đúng thứ tự đọc trước khi tách câu.
- **Dị thể tự & chữ Nôm:** sử liệu VN có thể lẫn chữ Nôm; các model thuần Hán có thể sai → LLM/hiệu đính giúp giảm lỗi.
- **Thực thể sử Việt:** nhân danh/địa danh/chức quan triều Nguyễn → ưu tiên phương pháp LLM có thể "nhắc" ngữ cảnh lịch sử VN qua prompt.
- **Chi phí trên 2180 trang:** cân nhắc hybrid (model local chạy khối lượng lớn + LLM rà phần khó) để tối ưu tiền/thời gian.
- **Nhất quán nhãn:** thống nhất guideline gán nhãn (ranh giới thực thể, phân biệt TITLE vs PER…) trước khi chạy toàn bộ.
```

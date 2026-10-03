# Han-Nom OCR & NLP Pipeline

End-to-end pipeline for processing historical Han-character documents from Vietnamese collections, covering image preprocessing, OCR, classical Chinese sentence segmentation, and named entity recognition.

The project is designed for vertically written historical documents, where text is commonly read from right to left. It combines local OCR and NLP models with an optional LLM-based NER stage.

## Pipeline

```text
Historical scanned pages
        ↓
Image preprocessing
        ↓
PaddleOCR
        ↓
Reading-order reconstruction
        ↓
Classical Chinese sentence segmentation
        ↓
Named entity recognition
        ↓
Structured corpus outputs
```

## What is implemented

- **Image preprocessing:** grayscale conversion, CLAHE contrast enhancement, denoising, deskewing, and optional adaptive binarization with OpenCV.
- **OCR:** PaddleOCR with the Traditional Chinese model (`chinese_cht`).
- **Vertical reading order:** OCR regions are reordered from right to left and then top to bottom to better match historical Han-character documents.
- **Sentence segmentation:** local punctuation restoration using `raynardj/classical-chinese-punctuation-guwen-biaodian`.
- **NER:** Gemini-based few-shot extraction for `PER`, `LOC`, `ORG`, `TITLE`, `TME`, `NUM`, and `DYNASTY`.
- **Validation helpers:** generated entities are retained only when their text appears verbatim in the source sentence.
- **Reusable OCR module:** shared PaddleOCR logic is implemented in `src/paddle_ocr.py`.
- **OCR smoke testing:** `scripts/test_ocr.py` provides a lightweight way to inspect recognition quality before full processing.

## Project scope

The project was developed for a historical Han-character corpus covering 17 works, with an expected total of approximately 2,180 pages.

A working collection of 2,099 scanned pages across 33 source-volume folders was used during development. The original scans are not redistributed in this repository.

## OCR pilot results

A pilot OCR run was performed on 66 page images, using two pages from each of the 33 collected source folders.

| Metric | Result |
| --- | ---: |
| Pilot images | 66 |
| Source folders covered | 33 / 33 |
| Mean PaddleOCR confidence | 0.705 |
| Minimum confidence | 0.33 |
| Maximum confidence | 0.98 |
| Images below 0.75 confidence | 41 / 66 |
| Approx. characters per image | 240 |

`0.705` is the mean OCR model confidence reported by PaddleOCR. It is **not** a character-accuracy or CER score. A manually annotated gold set would be required for a proper OCR accuracy evaluation.

The pilot also showed that regular text pages were generally easier to recognize than title pages or decorative pages.

## Repository structure

```text
HanNom-OCR-NLP/
├── README.md
├── HanNom_OCR_NLP_Report.pdf
├── environment.yml
├── requirements.txt
├── notebooks/
│   ├── 01_preprocess.ipynb
│   ├── 02_ocr.ipynb
│   ├── 03_segment.ipynb
│   └── 04_ner.ipynb
├── src/
│   └── paddle_ocr.py
└── scripts/
    └── test_ocr.py
```

Large source images, generated OCR artifacts, local environments, model files, and secrets are excluded from Git.

## Input data

The original historical scans are not included in this repository.

Place source images under:

```text
data/raw_images/downloaded_images/<work_id>/
```

before running the pipeline.

## Environment

The recommended environment uses Python 3.11.

### Conda

```bash
conda env create -f environment.yml
conda activate hvh
```

### pip

```bash
python -m venv .venv
```

Windows:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Linux/macOS:

```bash
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Running the pipeline

The notebooks are intended to be run in order:

```text
01_preprocess.ipynb
        ↓
02_ocr.ipynb
        ↓
03_segment.ipynb
        ↓
04_ner.ipynb
```

### 1. Image preprocessing

`notebooks/01_preprocess.ipynb`

Applies grayscale conversion, CLAHE, deskewing, denoising, and optional adaptive binarization.

Processed images are written to:

```text
data/preprocessed/<work_id>/
```

Preprocessing is optional. PaddleOCR can also be run directly on the original scans.

### 2. OCR

`notebooks/02_ocr.ipynb`

The reusable OCR implementation is in:

```text
src/paddle_ocr.py
```

The OCR configuration uses:

```python
lang="chinese_cht"
use_textline_orientation=True
use_doc_orientation_classify=False
use_doc_unwarping=False
enable_mkldnn=False
```

`enable_mkldnn=False` is used to avoid oneDNN-related issues observed with PaddlePaddle 3.x on CPU.

OCR regions are sorted by x/y coordinates to reconstruct the traditional vertical reading order:

```text
right column → left column
top → bottom within each column
```

A quick OCR smoke test is available:

```bash
python scripts/test_ocr.py
```

### 3. Sentence segmentation

`notebooks/03_segment.ipynb`

The default local model is:

```text
raynardj/classical-chinese-punctuation-guwen-biaodian
```

The output format is:

```text
sentence_id<TAB>sentence
```

Example:

```text
HVH_246_000001	...
HVH_246_000002	...
```

### 4. Named entity recognition

`notebooks/04_ner.ipynb`

The NER stage uses Gemini few-shot prompting with the following entity schema:

```text
PER      person
LOC      location
ORG      organization
TITLE    title / official position
TME      time expression
NUM      number
DYNASTY  dynasty
```

API keys should be provided through environment variables and must not be stored in the repository.

PowerShell:

```powershell
$env:GOOGLE_API_KEY="your-key"
```

Linux/macOS:

```bash
export GOOGLE_API_KEY="your-key"
```

Generated entity text is validated against the original sentence before it is saved.

## Outputs

The pipeline can produce structured outputs such as:

```text
outputs/<work_id>/
├── <work_id>_raw.txt
├── <work_id>_seg.tsv
└── <work_id>_ner.json
```

Generated corpus files are not included in this repository. The repository focuses on the implementation and reproducible processing workflow.

## Data and copyright

The source scans used during development came from the [Nôm Foundation Digital Library](https://lib.nomfoundation.org).

The original page images are third-party materials and are **not redistributed in this repository**. Anyone reproducing the project should obtain the source material directly from the original provider and follow its terms of use.

## Limitations

- PaddleOCR is not specifically trained for every historical woodblock-print style or rare character variant.
- OCR confidence is not equivalent to OCR accuracy.
- Historical documents may contain rare glyphs, damaged print, mixed layouts, or non-standard forms.
- Sentence segmentation models trained mainly on classical Chinese corpora may not perfectly match Vietnamese historical material.
- LLM-based NER can produce inconsistent labels and should be evaluated against manually annotated data before being treated as ground truth.

## Report

The project report is available at:

[`HanNom_OCR_NLP_Report.pdf`](HanNom_OCR_NLP_Report.pdf)

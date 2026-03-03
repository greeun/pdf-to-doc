#!/usr/bin/env python3
"""
PDF text extractor using pdfplumber + optional OCR support.

Usage:
    python extract_pdf.py <pdf_path> [options]

Options:
    --json          Output raw JSON instead of Markdown
    --ocr           Enable OCR for scanned PDFs (requires tesseract, pymupdf)
    --lang LANG     OCR language (default: kor+eng)

Output:
    Default : Markdown text
    --json  : JSON {"pages": [...], "total_pages": N}

Dependencies:
    - pdfplumber         : pip install pdfplumber
    - pymupdf (OCR)      : pip install pymupdf
    - pytesseract (OCR)  : pip install pytesseract + brew install tesseract tesseract-lang
    - ocrmypdf (OCR)     : brew install ocrmypdf
"""

import sys
import json
import re
import tempfile
import os


# ── 반복 헤더/푸터 감지 ────────────────────────────────────────────────────────
def _detect_repeated_headers(pages: list) -> set:
    from collections import Counter
    line_counts = Counter()
    for page in pages:
        for line in page["text"].split("\n"):
            line = line.strip()
            if len(line) > 10:
                line_counts[line] += 1
    threshold = max(3, len(pages) * 0.3)
    return {line for line, cnt in line_counts.items() if cnt >= threshold}


# ── 텍스트 정제 ────────────────────────────────────────────────────────────────
def _clean_text(text: str, repeated: set) -> str:
    lines = []
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        if re.fullmatch(r"-\s*\d+\s*-", stripped):   # 페이지 번호
            continue
        if stripped in repeated:                       # 반복 헤더/푸터
            continue
        lines.append(stripped)
    return "\n".join(lines)


# ── 표 유효성 검사 ─────────────────────────────────────────────────────────────
def _is_valid_table(table: list) -> bool:
    if not table or len(table) < 2:
        return False
    flat = [cell for row in table for cell in row if cell and str(cell).strip()]
    return len(flat) >= 2


# ── 표 → Markdown ──────────────────────────────────────────────────────────────
def _table_to_markdown(table: list) -> str:
    header = table[0]
    rows = table[1:]
    md = "| " + " | ".join(str(c or "").strip() for c in header) + " |\n"
    md += "| " + " | ".join("---" for _ in header) + " |\n"
    for row in rows:
        md += "| " + " | ".join(str(c or "").strip() for c in row) + " |\n"
    return md


# ── 텍스트 → Markdown 헤딩 변환 ────────────────────────────────────────────────
def _text_to_markdown(text: str) -> str:
    lines = []
    for line in text.split("\n"):
        if re.match(r"^\d+\.\d+\.\d+\s+\S", line):
            lines.append(f"\n#### {line}")
        elif re.match(r"^\d+\.\d+\s+\S", line):
            lines.append(f"\n### {line}")
        elif re.match(r"^\d+\.\s+\S", line):
            lines.append(f"\n## {line}")
        else:
            lines.append(line)
    return "\n".join(lines)


# ── OCR: 스캔 PDF → 텍스트 PDF (ocrmypdf) ─────────────────────────────────────
def _ocr_preprocess(pdf_path: str, lang: str) -> str:
    """ocrmypdf로 스캔 PDF를 텍스트 레이어가 있는 PDF로 변환. 임시 파일 경로 반환."""
    import subprocess
    out_path = tempfile.mktemp(suffix="_ocr.pdf")
    result = subprocess.run(
        ["ocrmypdf", "--language", lang, "--skip-text", pdf_path, out_path],
        capture_output=True, text=True
    )
    if result.returncode not in (0, 6):  # 6 = already has text (skip)
        raise RuntimeError(f"ocrmypdf failed: {result.stderr.strip()}")
    # returncode 6이면 원본 그대로 사용
    return out_path if os.path.exists(out_path) and result.returncode == 0 else pdf_path


# ── OCR: 페이지 이미지 → 텍스트 (pymupdf + pytesseract) ───────────────────────
def _ocr_page_image(page_obj, lang: str) -> str:
    """pymupdf 페이지를 이미지로 렌더링 후 pytesseract로 OCR."""
    import fitz
    import pytesseract
    from PIL import Image
    import io

    mat = fitz.Matrix(2, 2)  # 2x 해상도로 렌더링 (OCR 정확도 향상)
    pix = page_obj.get_pixmap(matrix=mat)
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    return pytesseract.image_to_string(img, lang=lang)


# ── 이미지 추출 (pymupdf) ──────────────────────────────────────────────────────
def _extract_images(pdf_path: str) -> list:
    """PDF에서 이미지 파일 추출. [{page, index, ext, data}] 반환."""
    try:
        import fitz
    except ImportError:
        return []

    images = []
    with fitz.open(pdf_path) as doc:
        for page_num, page in enumerate(doc, 1):
            for img_index, img in enumerate(page.get_images(full=True)):
                xref = img[0]
                base_image = doc.extract_image(xref)
                images.append({
                    "page": page_num,
                    "index": img_index,
                    "ext": base_image["ext"],
                    "data": base_image["image"],
                })
    return images


# ── 핵심 추출 ──────────────────────────────────────────────────────────────────
def extract_pdf(pdf_path: str, ocr: bool = False, lang: str = "kor+eng") -> dict:
    try:
        import pdfplumber
    except ImportError:
        print(json.dumps({"error": "pdfplumber not installed. Run: pip install pdfplumber"}))
        sys.exit(1)

    target_path = pdf_path
    ocr_applied = False

    if ocr:
        try:
            target_path = _ocr_preprocess(pdf_path, lang)
            ocr_applied = target_path != pdf_path
        except Exception as e:
            sys.stderr.write(f"[OCR 전처리 실패, 원본으로 진행] {e}\n")

    raw_pages = []
    try:
        with pdfplumber.open(target_path) as pdf:
            total = len(pdf.pages)
            for i, page in enumerate(pdf.pages, 1):
                text = page.extract_text() or ""

                # 텍스트가 없는 페이지는 pytesseract로 OCR 시도
                if ocr and not text.strip():
                    try:
                        import fitz
                        with fitz.open(target_path) as doc:
                            text = _ocr_page_image(doc[i - 1], lang)
                    except Exception:
                        pass

                raw_pages.append({
                    "page": i,
                    "text": text,
                    "tables": page.extract_tables() or [],
                })
    except FileNotFoundError:
        print(json.dumps({"error": f"File not found: {pdf_path}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
    finally:
        if ocr_applied and os.path.exists(target_path):
            os.unlink(target_path)

    repeated = _detect_repeated_headers(raw_pages)
    pages = []
    for p in raw_pages:
        cleaned = _clean_text(p["text"], repeated)
        valid_tables = [t for t in p["tables"] if _is_valid_table(t)]
        pages.append({"page": p["page"], "text": cleaned, "tables": valid_tables})

    return {"pages": pages, "total_pages": total, "ocr_applied": ocr_applied}


# ── JSON → Markdown ────────────────────────────────────────────────────────────
def to_markdown(data: dict) -> str:
    sections = []
    for page in data["pages"]:
        text = page["text"].strip()
        tables = page["tables"]
        if not text and not tables:
            continue
        if text:
            sections.append(_text_to_markdown(text))
        for table in tables:
            sections.append("\n" + _table_to_markdown(table))
    return "\n\n".join(sections)


# ── CLI ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python extract_pdf.py <pdf_path> [--json] [--ocr] [--lang kor+eng]"}))
        sys.exit(1)

    pdf_path = sys.argv[1]
    as_json  = "--json" in sys.argv
    use_ocr  = "--ocr"  in sys.argv
    lang     = "kor+eng"
    if "--lang" in sys.argv:
        idx = sys.argv.index("--lang")
        if idx + 1 < len(sys.argv):
            lang = sys.argv[idx + 1]

    data = extract_pdf(pdf_path, ocr=use_ocr, lang=lang)

    if as_json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(to_markdown(data))

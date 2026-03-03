#!/usr/bin/env python3
"""
PDF text extractor using pdfplumber.
Extracts text and tables, cleans noise, and converts to structured Markdown.

Usage:
    python extract_pdf.py <pdf_path> [--json]

Output (stdout):
    Default : Markdown text
    --json  : JSON {"pages": [{"page": 1, "text": "...", "tables": [[...]]}], "total_pages": N}
"""

import sys
import json
import re


# ── 반복 헤더 감지 ─────────────────────────────────────────────────────────────
def _detect_repeated_headers(pages: list[dict]) -> set[str]:
    """3페이지 이상 반복되는 줄을 헤더/푸터로 판단."""
    from collections import Counter
    line_counts: Counter = Counter()
    for page in pages:
        for line in page["text"].split("\n"):
            line = line.strip()
            if len(line) > 10:
                line_counts[line] += 1
    threshold = max(3, len(pages) * 0.3)
    return {line for line, cnt in line_counts.items() if cnt >= threshold}


# ── 텍스트 정제 ────────────────────────────────────────────────────────────────
def _clean_text(text: str, repeated: set[str]) -> str:
    lines = []
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        # 페이지 번호 제거: "- 2 -", "- 12 -"
        if re.fullmatch(r"-\s*\d+\s*-", stripped):
            continue
        # 반복 헤더/푸터 제거
        if stripped in repeated:
            continue
        lines.append(stripped)
    return "\n".join(lines)


# ── 표 유효성 검사 ─────────────────────────────────────────────────────────────
def _is_valid_table(table: list) -> bool:
    """빈 셀만 있거나 1열짜리 의미없는 표 제외."""
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
        if re.match(r"^\d+\.\d+\.\d+\s+\S", line):   # 1.2.3 항목
            lines.append(f"\n#### {line}")
        elif re.match(r"^\d+\.\d+\s+\S", line):        # 1.2 항목
            lines.append(f"\n### {line}")
        elif re.match(r"^\d+\.\s+\S", line):            # 1. 항목
            lines.append(f"\n## {line}")
        else:
            lines.append(line)
    return "\n".join(lines)


# ── 핵심 추출 ──────────────────────────────────────────────────────────────────
def extract_pdf(pdf_path: str) -> dict:
    try:
        import pdfplumber
    except ImportError:
        print(json.dumps({"error": "pdfplumber not installed. Run: pip install pdfplumber"}))
        sys.exit(1)

    raw_pages = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            total = len(pdf.pages)
            for i, page in enumerate(pdf.pages, 1):
                raw_pages.append({
                    "page": i,
                    "text": page.extract_text() or "",
                    "tables": page.extract_tables() or [],
                })
    except FileNotFoundError:
        print(json.dumps({"error": f"File not found: {pdf_path}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

    repeated = _detect_repeated_headers(raw_pages)

    pages = []
    for p in raw_pages:
        cleaned = _clean_text(p["text"], repeated)
        valid_tables = [t for t in p["tables"] if _is_valid_table(t)]
        pages.append({"page": p["page"], "text": cleaned, "tables": valid_tables})

    return {"pages": pages, "total_pages": total}


# ── JSON → Markdown 변환 ───────────────────────────────────────────────────────
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
        print(json.dumps({"error": "Usage: python extract_pdf.py <pdf_path> [--json]"}))
        sys.exit(1)

    pdf_path = sys.argv[1]
    as_json = "--json" in sys.argv

    data = extract_pdf(pdf_path)

    if as_json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(to_markdown(data))

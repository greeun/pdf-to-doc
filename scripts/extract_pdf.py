#!/usr/bin/env python3
"""
PDF text extractor using pdfplumber.
Outputs structured JSON with page-by-page text content.

Usage:
    python extract_pdf.py <pdf_path>

Output (stdout):
    JSON: {"pages": [{"page": 1, "text": "...", "tables": [[...]]}], "total_pages": N}
"""

import sys
import json


def extract_pdf(pdf_path: str) -> dict:
    try:
        import pdfplumber
    except ImportError:
        print(json.dumps({"error": "pdfplumber not installed. Run: pip install pdfplumber"}))
        sys.exit(1)

    result = {"pages": [], "total_pages": 0}

    try:
        with pdfplumber.open(pdf_path) as pdf:
            result["total_pages"] = len(pdf.pages)
            for i, page in enumerate(pdf.pages, 1):
                page_data = {"page": i, "text": "", "tables": []}

                # Extract text
                text = page.extract_text()
                page_data["text"] = text or ""

                # Extract tables
                tables = page.extract_tables()
                if tables:
                    page_data["tables"] = tables

                result["pages"].append(page_data)

    except FileNotFoundError:
        print(json.dumps({"error": f"File not found: {pdf_path}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python extract_pdf.py <pdf_path>"}))
        sys.exit(1)

    data = extract_pdf(sys.argv[1])
    print(json.dumps(data, ensure_ascii=False, indent=2))

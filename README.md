# pdf-to-doc

A Claude Code skill that extracts and analyzes PDF content, converting it into structured Markdown or JSON documents.

Supports both text-based PDFs (via [pdfplumber](https://github.com/jsvine/pdfplumber)) and scanned/image-based PDFs (via OCR with [ocrmypdf](https://github.com/ocrmypdf/OCRmyPDF) + [pytesseract](https://github.com/madmaze/pytesseract)).

## Features

- **Two modes**: Extract raw content as-is, or Analyze with section summaries
- **Structure-aware**: Preserves document hierarchy (title → subtitle → body)
- **Multiple output formats**: Markdown (default) or JSON
- **OCR support**: Scanned/image-based PDFs via ocrmypdf + pytesseract
- **Auto cleanup**: Removes repeated headers/footers and page numbers
- **Table support**: Converts tables to Markdown format

## Requirements

### Basic (text-based PDFs)

```bash
pip install pdfplumber
```

### OCR (scanned/image-based PDFs)

```bash
brew install tesseract tesseract-lang ocrmypdf
pip install pymupdf pytesseract
```

## Usage

Trigger the skill with natural language:

```
"report.pdf 내용 추출해서 md로 만들어줘"
"paper.pdf 요약해줘"
"contract.pdf 그대로 추출해줘"
"스캔된 PDF인데 텍스트 추출해줘"
"extract content from report.pdf and save as markdown"
```

### Modes

| Mode | Keywords | Behavior |
|------|----------|----------|
| **Extract** | 그대로, 추출, 원문, extract, as-is | Raw content, structure only |
| **Analyze** | 요약, 분석, 정리, summarize, analyze | Section summaries + key points |

### Output

| Mode | Default filename | Format |
|------|-----------------|--------|
| Extract | `<name>_extracted.md` | Markdown |
| Analyze | `<name>_analyzed.md` | Markdown |
| JSON request | `<name>.json` | JSON |

## How It Works

```
PDF file
  ↓
[Text-based]                    [Scanned/Image-based]
extract_pdf.py (pdfplumber)     extract_pdf.py --ocr
  ↓                               ├── ocrmypdf (full PDF)
  ↓                               └── pymupdf + pytesseract (per page)
  ↓
Clean: remove headers, footers, page numbers
  ↓
Claude structures content (hierarchy detection)
  ↓
Extract mode: preserve as-is    Analyze mode: summarize sections
  ↓
Save as .md or .json
```

## Script Reference

```bash
# Text-based PDF → Markdown
python scripts/extract_pdf.py <pdf_path>

# Scanned PDF → OCR → Markdown
python scripts/extract_pdf.py <pdf_path> --ocr

# Language selection (default: kor+eng)
python scripts/extract_pdf.py <pdf_path> --ocr --lang kor+eng

# Raw JSON output
python scripts/extract_pdf.py <pdf_path> --json
```

## Skill Structure

```
pdf-to-doc/
├── SKILL.md              # Skill instructions for Claude
├── README.md             # This file
├── docs/
│   └── usage-guide.md   # Detailed usage guide
└── scripts/
    └── extract_pdf.py   # PDF extraction + OCR script
```

## Installation

Place the `pdf-to-doc/` folder in your Claude Code skills directory:

```bash
~/.claude/skills/pdf-to-doc/
```

## License

MIT

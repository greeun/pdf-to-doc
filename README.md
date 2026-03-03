# pdf-to-doc

A Claude Code skill that extracts and analyzes PDF content, converting it into structured Markdown or JSON documents using [pdfplumber](https://github.com/jsvine/pdfplumber).

## Features

- **Two modes**: Extract raw content as-is, or Analyze with section summaries
- **Structure-aware**: Preserves document hierarchy (title → subtitle → body)
- **Multiple output formats**: Markdown (default) or JSON
- **Python-powered extraction**: Uses pdfplumber for reliable text and table extraction

## Requirements

```bash
pip install pdfplumber
```

## Usage

Trigger the skill with natural language:

```
"report.pdf 내용 추출해서 md로 만들어줘"
"paper.pdf 요약해줘"
"contract.pdf 그대로 추출해줘"
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
extract_pdf.py (pdfplumber) → raw text + tables as JSON
  ↓
Claude structures content (hierarchy detection)
  ↓
Extract mode: preserve as-is    Analyze mode: summarize sections
  ↓
Save as .md or .json
```

## Skill Structure

```
pdf-to-doc/
├── SKILL.md              # Skill instructions for Claude
├── README.md             # This file
└── scripts/
    └── extract_pdf.py    # PDF extraction script (pdfplumber)
```

## Installation

Place the `pdf-to-doc/` folder in your Claude Code skills directory:

```bash
~/.claude/skills/pdf-to-doc/
```

## License

MIT

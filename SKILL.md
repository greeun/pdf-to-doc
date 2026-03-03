---
name: pdf-to-doc
description: Analyze PDF content following document flow, extract structured data (title → subtitle → content), and output as markdown or JSON. Supports OCR for scanned/image-based PDFs. Use when user says "PDF 읽어줘", "PDF 내용 추출", "md로 만들어줘", "스캔 PDF OCR", "이미지 PDF 텍스트 추출", or requests PDF analysis.
---

# pdf-to-doc

PDF 파일을 pdfplumber로 추출한 후 문서 흐름에 맞게 구조화하여 Markdown 또는 JSON으로 저장합니다.
스캔 PDF는 OCR(ocrmypdf + pytesseract)로 텍스트를 인식합니다.

## Quick Start

```
"report.pdf 내용 추출해서 md로 만들어줘"   → Extract 모드
"paper.pdf 요약해줘"                       → Analyze 모드
"contract.pdf 그대로 추출해줘"             → Extract 모드
"스캔된 PDF인데 텍스트 추출해줘"            → OCR 모드 (--ocr)
"이미지 기반 PDF라 텍스트가 없어"           → OCR 모드 (--ocr)
```

## Workflow

### Step 1: PDF 텍스트 추출

Bash 툴로 Python 스크립트 실행:

```bash
# 일반 PDF
python ~/.claude/skills/pdf-to-doc/scripts/extract_pdf.py <pdf_path>

# 스캔 PDF (이미지 기반) → OCR 적용
python ~/.claude/skills/pdf-to-doc/scripts/extract_pdf.py <pdf_path> --ocr

# 언어 지정 (기본: kor+eng)
python ~/.claude/skills/pdf-to-doc/scripts/extract_pdf.py <pdf_path> --ocr --lang kor+eng
```

기본 출력은 Markdown. `--json` 플래그로 원시 JSON 출력 가능.
OCR 의존성: `brew install tesseract tesseract-lang ocrmypdf` + `pip install pymupdf pytesseract`

### Step 2: 모드 선택

사용자 요청에서 모드 자동 감지. 불명확하면 반드시 먼저 질문:
> "원문 그대로 추출할까요, 아니면 요약/분석할까요?"

| 모드 | 트리거 키워드 | 동작 |
|------|-------------|------|
| **Extract** | 그대로, 추출, 원문, extract, as-is | 원문 유지, 구조만 정리 |
| **Analyze** | 요약, 분석, 정리, summarize, analyze | 섹션별 요약 + 핵심 포인트 |

### Step 3: 구조화

추출된 텍스트에서 계층 구조 파악 후 처리:

- **Extract 모드**: 원문 그대로 유지, Markdown 헤딩으로 계층 변환만 수행
- **Analyze 모드**: 각 섹션 1-3줄 요약 + 핵심 포인트 bullet 3-5개

표(table)는 Markdown 표 형식으로 변환.

### Step 4: 저장

Write 툴로 파일 저장 후 경로 안내.

| 모드 | 기본 파일명 | 포맷 |
|------|-----------|------|
| Extract | `<원본명>_extracted.md` | Markdown |
| Analyze | `<원본명>_analyzed.md` | Markdown |
| JSON 요청 시 | `<원본명>.json` | JSON |

## Guidelines

- 문서의 논리적 흐름 유지 (순서 변경 금지)
- 계층 구조 보존: H1 > H2 > H3
- Extract 모드: AI 해석 최소화, 원문 충실
- Analyze 모드: 섹션별 요약 + 핵심 bullet
- JSON 출력 구조: `{"title": "...", "sections": [{"heading": "...", "content": "...", "subsections": [...]}]}`

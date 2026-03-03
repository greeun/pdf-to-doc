# Usage Guide

## Overview

`pdf-to-doc`은 PDF 파일을 두 가지 모드로 처리합니다:

- **Extract 모드**: 원문 그대로 추출, 계층 구조만 정리
- **Analyze 모드**: 섹션별 요약 + 핵심 포인트 bullet

스캔된 PDF(이미지 기반)는 OCR을 통해 텍스트를 인식합니다.

---

## Installation

### 1. 스킬 설치

```bash
cp -r pdf-to-doc/ ~/.claude/skills/
```

### 2. 의존성 설치

**기본 (텍스트 PDF):**
```bash
pip install pdfplumber
```

**OCR 포함 (스캔 PDF):**
```bash
brew install tesseract tesseract-lang ocrmypdf
pip install pymupdf pytesseract
```

---

## Basic Usage

### Extract 모드 (원문 추출)

원문을 그대로 유지하면서 Markdown 계층 구조로 변환합니다.

**트리거 예시:**
```
"report.pdf 그대로 추출해줘"
"contract.pdf 원문 그대로 md로 만들어줘"
"extract content from paper.pdf as-is"
```

**출력 예시 (`report_extracted.md`):**
```markdown
# Annual Report 2024

## Executive Summary

Lorem ipsum dolor sit amet, consectetur adipiscing elit...

## Financial Results

### Revenue

Total revenue for fiscal year 2024 was $10.2 billion...

| Quarter | Revenue | Growth |
|---------|---------|--------|
| Q1      | $2.4B   | +12%   |
| Q2      | $2.6B   | +15%   |
```

---

### Analyze 모드 (요약/분석)

각 섹션을 1-3줄로 요약하고 핵심 포인트를 추출합니다.

**트리거 예시:**
```
"research_paper.pdf 요약해줘"
"이 PDF 분석해줘"
"summarize the key points in document.pdf"
```

**출력 예시 (`research_paper_analyzed.md`):**
```markdown
# Research Paper: AI in Healthcare (2024)

## Abstract

**요약**: 의료 분야에서 AI 활용 현황과 미래 전망을 다룬 연구.

**핵심 포인트:**
- AI 진단 정확도가 인간 의사 대비 평균 15% 향상
- 비용 절감 효과: 연간 $150B 예상
- 주요 적용 분야: 영상의학, 신약 개발, 환자 모니터링
```

---

## OCR Mode (스캔 PDF)

텍스트 레이어가 없는 스캔 PDF에 OCR을 적용합니다.

**트리거 예시:**
```
"스캔된 PDF인데 텍스트 추출해줘"
"이미지 기반 PDF라 텍스트가 없어"
"scan.pdf OCR 적용해서 md로 만들어줘"
```

**동작 방식:**
1. `ocrmypdf`로 PDF 전체에 텍스트 레이어 추가
2. 텍스트가 없는 개별 페이지는 `pymupdf + pytesseract`로 이미지 OCR

**언어 지정:**
```
"한국어 PDF야, OCR 해줘"           → --lang kor
"영문 스캔 문서 추출해줘"            → --lang eng
"한영 혼합 문서"                    → --lang kor+eng (기본값)
```

---

## JSON Output

JSON 형식으로 출력을 요청할 수 있습니다.

**트리거 예시:**
```
"document.pdf JSON으로 변환해줘"
"extract PDF as JSON"
```

**출력 구조 (`document.json`):**
```json
{
  "pages": [
    {
      "page": 1,
      "text": "...",
      "tables": [...]
    }
  ],
  "total_pages": 10,
  "ocr_applied": false
}
```

---

## Supported PDF Types

| PDF 유형 | Extract | Analyze | OCR | 비고 |
|---------|---------|---------|-----|------|
| 텍스트 기반 PDF | ✅ | ✅ | 불필요 | 최적 |
| 스캔 PDF (이미지) | ✅ | ✅ | 필요 (`--ocr`) | tesseract 설치 필요 |
| 표 포함 PDF | ✅ | ✅ | - | 표 → Markdown 표 변환 |
| 다국어 PDF | ✅ | ✅ | - | UTF-8 지원 |
| 암호화 PDF | ❌ | ❌ | - | 비밀번호 해제 후 사용 |

---

## How the Extraction Works

```
PDF 파일
    ↓
[텍스트 PDF]                      [스캔 PDF (--ocr)]
pdfplumber 텍스트 추출              ocrmypdf → 텍스트 레이어 추가
                                   텍스트 없는 페이지 → pytesseract OCR
    ↓
정제: 반복 헤더/푸터 제거, 페이지 번호 제거
    ↓
Claude 처리
    ├── Extract 모드: 계층 구조 감지 → Markdown 헤딩 변환
    └── Analyze 모드: 섹션 파악 → 요약 + 핵심 bullet 생성
    ↓
.md 또는 .json 파일로 저장
```

---

## Troubleshooting

### `pdfplumber not installed`
```bash
pip install pdfplumber
```

### `tesseract not found` (OCR 사용 시)
```bash
brew install tesseract tesseract-lang
```

### 한국어 OCR 인식률이 낮은 경우
해상도가 낮은 스캔본일 수 있습니다. 스캔 DPI를 300 이상으로 높여 재스캔하세요.
스크립트는 내부적으로 2배 해상도(Matrix 2x2)로 렌더링하여 정확도를 높입니다.

### 표가 깨지는 경우
복잡한 중첩 표는 pdfplumber가 완벽히 처리하지 못할 수 있습니다.
Extract 모드에서 수동으로 정리하는 것을 권장합니다.

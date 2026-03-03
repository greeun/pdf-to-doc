# Usage Guide

## Overview

`pdf-to-doc`은 PDF 파일을 두 가지 모드로 처리합니다:

- **Extract 모드**: 원문 그대로 추출, 계층 구조만 정리
- **Analyze 모드**: 섹션별 요약 + 핵심 포인트 bullet

---

## Installation

### 1. 스킬 설치

```bash
# Claude Code skills 디렉토리에 배치
cp -r pdf-to-doc/ ~/.claude/skills/
```

### 2. 의존성 설치

```bash
pip install pdfplumber
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

## Methodology

**요약**: 2019-2024년 50개 병원 데이터를 분석한 메타 연구.

**핵심 포인트:**
- 무작위 대조 임상시험(RCT) 방법론 사용
- 15만 명 환자 데이터 분석
- 3개 AI 모델 비교: GPT-4, Med-PaLM 2, BioGPT
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
  "title": "Document Title",
  "sections": [
    {
      "heading": "Section 1",
      "content": "Section content...",
      "subsections": [
        {
          "heading": "Subsection 1.1",
          "content": "Subsection content..."
        }
      ]
    }
  ]
}
```

---

## Supported PDF Types

| PDF 유형 | Extract | Analyze | 비고 |
|---------|---------|---------|------|
| 텍스트 기반 PDF | ✅ | ✅ | 최적 |
| 스캔 PDF (이미지) | ❌ | ❌ | OCR 필요 |
| 표 포함 PDF | ✅ | ✅ | 표 → Markdown 표 변환 |
| 다국어 PDF | ✅ | ✅ | UTF-8 지원 |
| 암호화 PDF | ❌ | ❌ | 비밀번호 해제 후 사용 |

---

## How the Extraction Works

```
PDF 파일
    ↓
extract_pdf.py (pdfplumber)
    ├── 페이지별 텍스트 추출
    └── 표(table) 감지 및 추출
    ↓
JSON 출력: { pages: [{page, text, tables}] }
    ↓
Claude 처리
    ├── Extract 모드: 계층 구조 감지 → Markdown 헤딩 변환
    └── Analyze 모드: 섹션 파악 → 요약 + 핵심 bullet 생성
    ↓
.md 또는 .json 파일로 저장
```

---

## Troubleshooting

### `pdfplumber not installed` 오류
```bash
pip install pdfplumber
```

### 텍스트가 제대로 추출되지 않는 경우
스캔된 PDF(이미지 기반)일 가능성이 높습니다. OCR 도구(예: `pytesseract`, `ocrmypdf`)로 사전 처리 후 사용하세요.

```bash
# ocrmypdf로 사전 처리
pip install ocrmypdf
ocrmypdf input.pdf input_ocr.pdf
```

### 표가 깨지는 경우
복잡한 중첩 표는 pdfplumber가 완벽히 처리하지 못할 수 있습니다. Extract 모드에서 수동으로 정리하는 것을 권장합니다.

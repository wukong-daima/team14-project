# 제안 발표 자료(Team14.zip) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (native, 사용자 승인됨). Steps use checkbox (`- [ ]`) syntax.

**Goal:** 승인된 12장 개요로 PPTX·PDF 를 만들고 `submission/Team14.zip` 으로 묶는다.
**Architecture:** `deck.json` 한 벌 → `build_pptx.js`(pptxgenjs) 와 `build_html.py`(HTML) → Playwright 인쇄 PDF → zip.
**Tech Stack:** Node 26 + pptxgenjs, Python 3 표준 라이브러리, Playwright MCP, zip.
**Spec:** docs/superpowers/specs/2026-11-14-proposal-deck-design.md

## Global Constraints
- 파일명 정확히 `Team14.zip`, 안에 `Team14.pptx`, `Team14.pdf`.
- 16:9. 한국어. 제목 문자열은 spec 그대로. mock 수치 금지.

## Review Focus
- 표지 제목이 두 줄로 잘리지 않는가 → PPTX 열어 확인(사용자), HTML 은 스크린샷.
- 한글 폰트 깨짐(PDF) → Playwright 렌더 확인.
- 이미지 경로가 PPTX 에 절대경로로 박히지 않는가 → zip 만 열어도 보이는지 확인.
- zip 안에 macOS 메타파일(`__MACOSX`, `.DS_Store`) 이 없는가 → `zip -X` + `unzip -l`.
- 12장 수와 순서가 승인 개요와 같은가 → deck.json 길이 검사.

### Task 1: 스크린샷 3장
- [ ] 로컬 서버 띄우고 라이트 테마로 `weeks/week02.html#play`, `weeks/week02.html?easy#c2`, `lab/index.html` 캡처 → `submission/img/{calc,easy,lab}.png`
- [ ] 파일 3개 존재 확인

### Task 2: deck.json
- [ ] 12장 작성(spec 개요). `python3 -c "import json;assert len(json.load(open('submission/deck.json'))['slides'])==12"`

### Task 3: PPTX
- [ ] `npm init -y && npm i pptxgenjs` (submission/ 안, node_modules 는 gitignore)
- [ ] `build_pptx.js` 작성: kind 별 렌더(title / bullets / table / two-col / image+bullets / diagram)
- [ ] `node build_pptx.js` → `Team14.pptx` 생성, 크기 > 50KB

### Task 4: HTML → PDF
- [ ] `build_html.py` 로 `deck.html` 생성(1280×720 섹션 12개, print CSS page size)
- [ ] Playwright 로 열어 콘솔 에러 0, 스크린샷 1장 확인 → `page.pdf` 로 `Team14.pdf`
- [ ] PDF 페이지 수 12 확인

### Task 5: zip + 커밋
- [ ] `cd submission && zip -X Team14.zip Team14.pptx Team14.pdf`; `unzip -l` 로 2개 파일만
- [ ] 커밋·PR·머지. README 에 제출물 위치 한 줄.

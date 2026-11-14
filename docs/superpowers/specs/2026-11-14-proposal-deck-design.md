# 제안 발표 자료(Team14.zip) 설계 — 2026-11-14

## 의도
11/15 23:55 LearnUS 제출: PPT + PDF 를 `Team14.zip` 하나로. 형식·제목·기한 위반 감점. 같은 시각 구글 시트에 제목 제출.

## 목표 / 비목표 / 반목표
- 목표: 12장 16:9 한국어 덱, 승인된 개요대로. PPTX 와 PDF 내용 동일. 저장소에 커밋.
- 비목표: 실제 라운드 수치(이 세션에서 실행 불가). 조원 이름(표지는 "14조", 이름은 사용자가 한 줄 추가).
- 반목표: mock 수치를 실측처럼 보이게 하는 것. 비공개 문항 내용 노출.

## 제약
- LibreOffice 없음 → PDF 는 HTML 덱을 Playwright 로 인쇄. 폰트는 Noto Sans KR(웹) / 맑은 고딕·Apple SD Gothic 대체.
- 제목: "자가 진화 LLM 하네스의 학습 효과 검증: 오버피팅인가, 진짜 개선인가".

## 접근 (승인: 방법 1)
1. (선택) 단일 데이터(`submission/deck.json`) → pptxgenjs PPTX + HTML 덱 → Playwright PDF. 내용 동일, 모양 유사.
2. PPTX 만 만들고 PDF 는 사용자가 내보내기. 수동 단계 남음.

## 결정
- 데이터: `submission/deck.json` (slides[]: {kind, title, bullets|table|two-col|image, note}).
- PPTX: `submission/build_pptx.js` (pptxgenjs, npm 로컬 설치, 16:9 LAYOUT_WIDE 13.33×7.5in).
- HTML/PDF: `submission/deck.html` 을 `build_html.py` 가 deck.json 으로 생성, Playwright 로 `Team14.pdf` 인쇄(1280×720 페이지).
- 스크린샷: 사이트 라이트 테마에서 2주차 계산기·쉬운 모드·실험실 3장을 `submission/img/` 에 저장.
- 산출: `submission/Team14.pptx`, `submission/Team14.pdf`, `submission/Team14.zip`.

## 빌더에게 맡기는 것
색·여백·아이콘. 단, 사이트 토큰(파랑 #2d5bff, 주황 #ff8a3d, 보라 #7b4dff) 사용.

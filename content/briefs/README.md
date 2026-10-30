# 주차별 콘텐츠 브리프

강의 PDF 원본(비공개, 저장소에 없음)과 수업 요약본을 대조해 만든 작업 지시서입니다.
주차 페이지를 만들 때 이 파일을 Claude Code에 그대로 넘기면 됩니다 (`CONTRIBUTING.md`의 권장 프롬프트 참고).

각 브리프의 구성: 강의 흐름 · 핵심 개념(전공/중학생 두 벌) · **요약본 정정** · 추천 인터랙션(대표 1 + 대안 2) ·
다이어그램 후보 · 모델 비교 포인트(확신도 표기) · 시험 포인트 + 예상 문제 · 출처.

| 파일 | 주차 | 원본 | 비고 |
|---|---|---|---|
| week01.md | 1주차 열린 문제와 에이전트 | week1_overview.pdf (32p) | 페이지 완성 (`weeks/week01.html`) |
| week02.md | 2주차 파운데이션 모델 아키텍처 | week2_fm.pdf (128p) | 페이지 완성 (`weeks/week02.html`). p.68~90 선호 튜닝은 4주차와 겹침 |
| week03.md | 3주차 KV 캐시 압축 (DeepSeek-V4.1-Flash) | week3_fm.pdf (27p, Week 3-1만) | 페이지 초안 완성. 3-2 자료(Mamba·GDN·Hybrid)는 미확보 |
| week04.md | 4주차 학습 방법론 | **week2_fm.pdf p.56~57, 68~90** + week4_agent.pdf p.84~93 | 페이지 초안 완성. 원본 슬라이드는 2주차 PDF 후반부, 2주차 개념 9·10의 심화 |
| week06.md | 6주차 에이전트 | **week4_agent.pdf (93p, "Week 4-1 AI Agent")** | 페이지 초안 완성. 파일명은 week4지만 내용은 6주차 요약과 1:1 대응 |
| week08.md | 8주차 하네스 엔지니어링 | week5_self_evolving_agent.pdf (92p, Week 5-1 Introduction) | 페이지 초안 완성. Reflexion·Voyager·R-Zero는 다음 수업 범위 |

## 작업 흐름

1. `weeks/_template.html` 복사 → `weeks/weekNN.html`
2. 브리프의 "핵심 개념"으로 개념 카드, "요약본 정정"으로 `callout fix` 박스, "추천 인터랙션 ★"으로 직접 해보기, "모델 비교 포인트"로 비교표, "시험 포인트"로 퀴즈.
3. `assets/js/weeks.js`에서 해당 주차 `status: "done"`.
4. 완성 예시: `weeks/week02.html` (인터랙션·도형·비교표·정정 박스 모두 포함).

# Team14 · 최신딥러닝 인터랙티브 랩

연세대학교 공학대학원 인공지능학과 **최신딥러닝이론및응용** 14조 조별과제.
주차별 강의 내용을 도형과 인터랙션으로 공부하고, 수업에서 다룬 모델(DeepSeek 등)과
Claude · GPT · 공개 모델의 동작을 **공개 자료 범위에서** 비교하는 정적 사이트입니다.

- **사이트: https://wukong-daima.github.io/team14-project/** (GitHub Pages, `main` 브랜치 루트에서 자동 배포)
- 발표 모드: `slides/index.html` (reveal.js)
- 계획: [PLAN.md](PLAN.md) · 작업 규칙: [CONTRIBUTING.md](CONTRIBUTING.md) · 주차별 콘텐츠 브리프: [content/briefs/](content/briefs/)

## 주차 작업 시작하기

```bash
git clone https://github.com/wukong-daima/team14-project.git && cd team14-project
scripts/new-week.sh 03          # 내 주차 번호. feat/week03 브랜치 + weeks/week03.html 준비
scripts/pr-week.sh 03           # 다 하면 커밋·푸시·PR 한 번에
```

| 담당 | 주차 | 명령 |
|---|---|---|
| 손 | 1, 2 (완성) · 공통 | `scripts/new-week.sh 01` / `02` |
| 조원 A | 3, 4 | `scripts/new-week.sh 03` / `04` |
| 조원 B | 6, 8 | `scripts/new-week.sh 06` / `08` |

## 로컬에서 보기

빌드 도구가 없습니다. 아무 정적 서버나 띄우면 됩니다.

```bash
python3 -m http.server 8080
# http://localhost:8080
```

## 구조

```
scripts/new-week.sh     주차 브랜치 만들기/이어하기 · scripts/pr-week.sh  커밋+푸시+PR
index.html              랜딩: 컨셉 · 주차 카드 · 팀/일정
weeks/weekNN.html       주차 페이지 (한 주차 = 한 파일, 인터랙션 스크립트 포함)
weeks/_template.html    새 주차를 만들 때 복사하는 템플릿
slides/index.html       발표용 슬라이드 (주차 페이지를 iframe 으로 시연)
assets/css/site.css     공통 스타일 (전공/쉬운 모드, 비교 패널, 퀴즈)
assets/js/site.js       공통 스크립트 (모드 토글, 내비게이션, 목차)
assets/js/weeks.js      주차 매니페스트 (제목·담당·상태) — 여기 한 줄이 카드/내비/슬라이드에 반영
content/briefs/         주차별 콘텐츠 브리프 (강의 원본 대조·개념·인터랙션 명세·비교 포인트·예상문제)
```

## 세 가지 기능

| 기능 | 어떻게 | 어디에 |
|---|---|---|
| 도형으로 이해 | 인라인 SVG 도형 + 주차당 대표 인터랙션 1개 (슬라이더/버튼) | 각 주차 `3. 직접 해보기` |
| 중학생 수준으로 이해하기 | 모든 설명을 `data-level="pro"` / `data-level="easy"` 두 벌로 작성, 헤더 버튼으로 전환 | 사이트 전체 |
| 최신 모델과 비교 | 정적 비교표. 공개 문서만, 출처 표기, 모르면 `비공개` 배지 | 각 주차 `4. 최신 모델과 비교하기` |

## 원칙

- 강의 자료 원본(PDF/이미지)은 저장소에 올리지 않습니다. 모든 설명과 도형은 팀이 재작성합니다.
- 요약본과 원본이 다르면 페이지에 **정정** 박스로 드러냅니다.
- 모델 비교는 추측으로 채우지 않습니다.

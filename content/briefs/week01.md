# 1주차: Orientation — '정의된 문제'를 넘어 '열린 문제(Open-Beginning)'로

> 한 줄 요약: 현재 AI는 "정의된 문제"를 푸는 데는 강력하지만, 과학·의료·비즈니스의 진짜 발견은 아직 아무도 문제라고 부르지 않은 **현상**에서 "다음에 무엇을 물을 것인가"를 알아보는 데서 시작된다. 이 수업은 그런 **자율적·자가진화·신뢰 가능한 에이전트**를 목표로 한다.

---

## 강의 흐름

| 섹션 | 페이지 | 내용 |
|---|---|---|
| 0. 강사·연구실 소개 | p.1–3 | MLAI Lab 소개, 연구 3축: Foundation & Generative Model / Agentic & Self-Evolving Systems / Trustworthy AI |
| 1. 예시 사례 ① Sid Sijbrandij | p.4–6 | GitLab 공동창업자가 자신의 골육종 치료를 Agentic AI 루프로 재설계 (FAP 표적 방사성 리간드 치료) |
| 2. 예시 사례 ② DNA 암 스크리닝 | p.7–15 | 30억 길이 DNA 시퀀스 → 전문가 feature(10만) → Option 1(기구축 feature) vs Option 2(Self-evolving Agentic AI가 코드로 feature 추출) |
| 3. Turing 1948 "Intelligent Machinery" | p.16 | "기계는 경험으로 배워야 한다", 보상·벌의 개념 |
| 4. Open-Beginningness | p.17–23 | 정의된 문제 vs 열린 문제, McClintock 사례, 병원/신종질병/신제품 사례, 기존 AI → 가설생성 AI → Open-Beginningness 3단계 |
| 5. Model Discovery Agent (MDA) | p.24 | LLM + Bayesian Inference + Value of Information |
| 6. 자가진화형 과학 발견 시스템 4단계 | p.25 | Knowledge Foundation → Mechanism Discovery → Knowledge Discovery → Open-Beginning & Self-Evolving Reasoning |
| 7. 수업 개요·평가·프로젝트 | p.26–32 | 수업 방향성 3문항, 15주 계획, 출석 10 / 기말 60 / 팀과제 30, 프로젝트 주제 5기준, 참고 강의 목록 |

---

## 핵심 개념

### 1. Agentic AI의 "권한" — 데이터를 읽는 게 아니라 코드를 짜게 한다 (p.7–15)
- **(a) 전공 설명**: DNA 시퀀스는 약 30억 길이라 GPT/Gemini의 컨텍스트(최대 약 100만 토큰)에 직접 넣을 수 없다. 전통적 접근(Option 1)은 전문가가 수십 년 지식으로 feature(예: A/C 동시 등장 개수)를 추출해 30억 → 10만으로 줄인 뒤 XGBoost·TabPFN 같은 모델에 넣는다. 그러나 이 방식은 성능 개선이 제한적이다. Option 2는 Self-evolving Agentic AI에게 DNA 파일에 **접근할 권한**을 주어, 파일을 통째로 읽는 것이 아니라 구조를 파악하고 유의미한 feature를 뽑는 **코드를 작성**하게 한다. 입력은 "기존 feature들과 각각의 성능 + DNA 파일", 사고과정은 "stage1 성능이 낮네 → A와 B의 장점을 결합한 C feature를 만들면?", 출력은 "C feature 추출 코드"(Any to Code, Code to Any)이며, 이 루프가 반복되면서 feature가 진화한다.
- **(b) 중학생 비유**: 30억 쪽짜리 책을 통째로 읽을 수 있는 사람은 없다. 대신 똑똑한 조수에게 "이 책에서 중요한 부분만 찾아내는 **검색 프로그램**을 직접 짜라"고 시키고, 결과가 별로면 "다시 짜봐"라고 하는 것. 조수는 책을 외우는 게 아니라 책을 뒤지는 도구를 만든다.
- **(c) 핵심 수치/고유명사**: 30억(DNA 길이) → 10만(전문가 feature), 컨텍스트 100만 토큰 한계, XGBoost, TabPFN, CRAM 파일, stage 1/2 조기 발견 시 사망률 크게 감소(췌장암 제외), "Any to Code, Code to Any"
- **(d) 슬라이드**: p.7–15

### 2. 개인 연구개발 루프로서의 Agentic AI — Sid Sijbrandij 사례 (p.5–6)
- **(a) 전공 설명**: 의료 비전문가가 스캔·혈액검사·조직 샘플·논문 정보를 모아 AI와 함께 분석하는 개인 R&D 루프(의료 Agentic AI)를 구축했다. 자연어 질문("지금 내 혈액/종양 데이터에서 무엇을 봐야 하나?") → AI가 논문을 찾고 볼 마커를 스스로 결정 → 분석 파이프라인 자동 구성 → 약 60만 개 단일세포 데이터 분석 → 결론·인터랙티브 플롯·Python 코드·분석 이력을 한 번에 산출. 의료진과 협업해 데이터 연결·변화 신호 조기 포착·새 치료 탐색(FAP 표적 방사성 리간드 치료)을 공격적으로 수행했다. 핵심은 "시간 투자를 전제로, 비전문가도 에이전트와 함께 전문가 수준 탐색이 가능하다"는 점이다.
- **(b) 중학생 비유**: 의사가 아닌 프로그래머가 자기 병을 고치려고 "AI 연구 조수"를 두고 매일 숙제를 시킨 것. 조수는 논문도 찾고, 그래프도 그리고, 코드도 짜서 "이번엔 이걸 확인해보자"를 반복했다.
- **(c) 고유명사**: Sid Sijbrandij(GitLab 공동창업자), T5 척추 약 6cm 종양·골육종, 2022 진단 → 2023 표준치료 → 2024 재발, FAP 표적 방사성 리간드 치료, 60만 단일세포 데이터
- **(d) 슬라이드**: p.5–6

### 3. "정의된 문제" vs "열린 문제(Open-Beginning Problem)" (p.18–20)
- **(a) 전공 설명**: 지도학습은 목표값·라벨이, 강화학습은 보상·환경이 주어졌다고 가정하고, Agentic AI도 미리 정해진 문제의 틀을 물려받는다. 즉 모두 주어진 문제 공간 안에서 명시된 목표를 최적화하며 과업 정의가 고정됐다고 가정한다. 반면 현실의 중요한 문제는 "찾으려던 것도 아니고 현재 문제 정의에 표현돼 있지도 않은 **현상(phenomenon)**"으로 등장한다. Open-Beginning Problem이란 "중요하다는 증거가 아직 없는 상황에서 어떤 현상에 지속적으로 관심을 기울여야 하는지, 그 현상으로 새 문제를 만들지 기존 문제를 재구성할지를 어떻게 판단하는가"이다. 어려운 이유: 해석 가치 판단 기준 부재, 맥락(변수·비교집단·시간범위) 부재, 약하고 분산된 증거, 문제 정의가 내생적·재귀적(정의가 다음 데이터를 바꿈), 즉시 평가할 정답 부재, "모든 것에 의미 부여 vs 아무것도 못 봄"의 선택 딜레마, 데이터/모델의 불확실성이 아니라 **문제 자체의 불확실성**.
- **(b) 중학생 비유**: 시험 문제를 잘 푸는 것과, 아무도 문제로 내지 않은 이상한 현상을 보고 "어? 이거 왜 이러지?"라고 질문을 만드는 것은 다르다. 지금 AI는 전자는 1등인데, 후자는 아직 서툴다.
- **(c) 핵심 용어**: phenomenon, Open-Beginningness, 내생적(endogenous)·재귀적 문제 정의, technical noise
- **(d) 슬라이드**: p.18–20

### 4. 열린 문제가 중요한 이유 — McClintock과 현실 사례 (p.19, 21–22)
- **(a) 전공 설명**: 유전자 교란 실험에서 목표(세포 성장)와 무관한 미묘한 형태(morphology) 변화가 관찰됐을 때, 이를 잡음으로 버릴지 연구를 재구성할지 결정하는 것이 핵심 판단이다. Barbara McClintock은 옥수수 색소 패턴 변화를 불규칙성으로 치부하지 않고 세대 간 유전을 추적해 **이동성 유전요소(mobile genetic elements)**를 추론했다(1951 발표 → 무시 → 1983 노벨 생리의학상 단독 수상). 결정적 행위는 현상의 "설명"이 아니라 "설명할 가치가 있음을 알아본 것". 같은 구조의 사례: 병원 환자 흐름 시스템이 추적 진료 누락 → 피할 수 있었던 응급실 입원 패턴을 발견(진료 연속성이 더 근본), 의사결정 지원 시스템이 기존 질병 범주에 맞지 않는 증상 조합 발견(신종 질병), 제품 채택 최적화 시스템이 설계 의도와 다른 기능 조합 사용 발견(신제품).
- **(b) 중학생 비유**: 옥수수 알갱이 색이 이상하게 얼룩진 걸 보고 "그냥 불량이네" 하고 넘긴 사람과, "왜 저럴까?" 하고 수십 년 추적해 노벨상을 받은 사람의 차이. 발견은 답이 아니라 **질문을 알아보는 눈**에서 시작한다.
- **(c) 고유명사/연도**: Barbara McClintock, 1951 → 1983 노벨 생리의학상, mobile genetic elements, morphology
- **(d) 슬라이드**: p.19, 21–22

### 5. AI의 3단계 진화: 기존 AI → 가설 생성 AI → Open-Beginningness (p.23)
- **(a) 전공 설명**: 기존 AI는 "문제 → 해답 탐색", 가설 생성 AI는 "문제 → 여러 가설 생성 → 검증", Open-Beginningness는 "수많은 현상 → 무엇이 중요한지 선택 → 질문/문제 자체를 생성 또는 재정의 → 탐구"이다. 단계가 올라갈수록 입력이 '문제'에서 '현상'으로 바뀌고, 출력이 '답'에서 '문제 정의'로 바뀐다. "진짜 발견은 정답을 잘 찾는 데서가 아니라, 아직 아무도 문제라고 부르지 않은 현상에서 '다음에 무엇을 물어야 하는가'를 알아보는 데서 시작된다."
- **(b) 중학생 비유**: 1단계는 "문제 주면 답 찾기", 2단계는 "문제 주면 답 후보 여러 개 내고 실험으로 고르기", 3단계는 "문제도 안 줬는데 세상을 보고 스스로 문제를 만들기".
- **(c) 핵심 구조**: 3단 사다리 (문제→답 / 문제→가설→검증 / 현상→선택→문제 생성→탐구)
- **(d) 슬라이드**: p.23

### 6. Model Discovery Agent (MDA) (p.24)
- **(a) 전공 설명**: Open-Beginningness 구현에 필요한 핵심 **inner loop**. 목표는 "지금 가능한 실험 중 어떤 실험을 하면 어떤 메커니즘이 맞는지 가장 많이 알 수 있을까?". 세 요소를 결합: (1) **LLM**이 가능한 새 mechanistic model(현실 현상을 설명하는 과학적·수학적 world model)을 제안, (2) **Bayesian Inference**로 어떤 모델이 현재 증거를 가장 잘 설명하는지 확률적으로 평가, (3) **Value of Information**으로 후보 모델들을 가장 잘 구분할 다음 실험을 선택. 출처: "Model Discovery Agent: LLM-assisted Bayesian experiment design for data-efficient discovery of mechanistic world models".
- **(b) 중학생 비유**: 탐정 놀이. AI가 "범인 후보(가설)"를 여러 명 내고, 지금까지 단서로 각 후보가 얼마나 그럴듯한지 점수를 매긴 뒤, "어떤 질문을 하면 후보가 가장 확 갈릴까?"를 골라 그 질문부터 한다.
- **(c) 핵심 용어**: mechanistic world model, Bayesian Inference, Value of Information(VoI), inner loop, data-efficient discovery
- **(d) 슬라이드**: p.24

### 7. 자가진화형 과학 발견 시스템 4단계와 수업 구조 (p.25, 27–29)
- **(a) 전공 설명**: Step 1 Knowledge Foundation(무엇을 알고 있는가) → Step 2 Mechanism Discovery(왜 그렇게 되는가) → Step 3 Knowledge Discovery(무엇을 새로 만들 것인가) → Step 4 Open-Beginning & Self-Evolving Scientific Reasoning(무엇을 다음에 검증할지, 현재 문제 정의가 맞는지, 새 개념·실험이 더 필요한지). AI가 기존 과학 지식을 구축·통합하고, 데이터·실험으로 새 기전과 법칙을 발견하며, 가설·해결책을 생성한 뒤 가장 가치 있는 후속 실험을 능동적으로 선택·검증해 **지식과 연구 전략을 함께 진화**시킨다. 수업 주제도 이 4단계에 대응: Knowledge Foundation(Agentic AI 입문, Multi-Agent) / Mechanism Discovery(실험 설계·인과 추론, 과학 법칙 발견) / Knowledge Discovery(수학·알고리즘 발견, 자율 과학 발견 시스템) / Open-Beginning & Self-Evolving(열린 과학 추론, 자가개선 에이전트, 신뢰·재현·자기교정 AI 과학).
- **(b) 중학생 비유**: 공부 → 원리 이해 → 새 발명 → "그런데 내가 풀던 문제가 맞는 문제였나?" 되묻기. 마지막 단계가 있어야 혼자서 계속 똑똑해진다.
- **(c) 핵심 구조**: 4 Step, 수업 방향성 3문항(현재 Agent 학습 원리 / Agent로 새 발견하는 법 / 앞으로 더 연구할 것), 15주 계획
- **(d) 슬라이드**: p.25, 27–29

### 8. Turing(1948) — 경험으로 배우는 기계 (p.16)
- **(a) 전공 설명**: "기계가 당신 대신 생각하게 할 수는 없다"는 통념에 의문을 제기한 1948년 논문 "Intelligent Machinery". 같은 실수를 반복하고 스스로 고치지 못하는 고정된 기계는 지능의 증거가 아니며, 결정적 단계는 **경험으로 배우는 것(learn by experience)**이고, 학습에는 심리적 보상·벌에 해당하는 "유리한/불리한 결과"의 개념이 필요하다. 이는 강화학습과 자가진화 에이전트의 사상적 뿌리다.
- **(b) 중학생 비유**: 80년 전 튜링이 이미 "진짜 똑똑한 기계는 혼나고 칭찬받으면서 스스로 고치는 기계"라고 말했다. 지금의 강화학습·자가진화 에이전트가 바로 그 아이디어다.
- **(c) 고유명사**: Alan Turing, "Intelligent Machinery"(1948), B. Jack Copeland(2004) 편집본 p.395
- **(d) 슬라이드**: p.16

---

## 요약본 정정

| 요약본 | 정정 (근거) |
|---|---|
| "AI 에이전트(GPT-4 기반)를 활용하여 1년간의 분석 끝에" | PDF에는 **모델명(GPT-4)과 '1년' 기간이 명시돼 있지 않음**. "AI와 함께 분석하는 개인 연구개발 루프(의료 Agentic AI)"로만 기술. 발언에서 나온 것일 수 있으니 사이트에는 "수업 구두 설명"으로 구분 표기 권장 (p.5–6) |
| "자신에게 맞는 치료법을 찾아낸 사례" | PDF는 구체적으로 **FAP 표적 방사성 리간드 치료**를 언급하고, "의료진과 협업"을 강조 (p.6) |
| "이동 유전체 현상 발견" | 정확한 용어는 **이동성 유전요소(mobile genetic elements)**, McClintock 옥수수 연구, 1951 발표 → 1983 노벨상 (p.21) |
| "커리큘럼: 에이전트, 멀티 에이전트, 능동적 데이터 수집, 정의된 문제 해결, 열린 문제 정의 및 자가 개선 에이전트 순" | PDF의 공식 15주 계획: Orientation → Introduction to Agentic AI → Multi-Agent Systems → Experimental Design and Causal Reasoning → AI for Scientific Law and Mechanism Discovery → AI for Mathematical and Algorithmic Discovery → Autonomous Scientific Discovery Systems → Open-Beginning Scientific Reasoning → Self-Improving and Self-Evolving Scientific Agents → Trustworthy, Reproducible, and Self-Correcting AI Science → 피드백 I/II → 발표 I/II → 기말 (p.29). "능동적 데이터 수집"은 "Experimental Design"에 해당 |
| "모델 디스커버리 에이전트" (설명 없음) | MDA = **LLM(모델 제안) + Bayesian Inference(증거 평가) + Value of Information(다음 실험 선택)**, Open-Beginningness의 inner loop (p.24) |
| "팀 과제 30%" | 팀 과제 30% = **피드백 + 프로젝트 발표 1회**; 기말 60%는 **전 범위 closed-book** (p.30) |
| 프로젝트 권장 기준 | PDF 원문은 5가지 중 **최소 한 가지** 만족: ① 도발적인 것 ② 새로운 관점 제시 ③ SoTA 성능(유명 리더보드) ④ 새로운 평가방법/지표/벤치마크/데이터셋 ⑤ 기업이 바로 가져다 쓰고 싶은 것. "도전적이라고 큰 계산자원이 필요한 건 아님" 강조 (p.31) |
| (누락) | Turing 1948 "Intelligent Machinery" 인용 슬라이드가 요약본에 없음 (p.16) |
| (누락) | Option 1 vs Option 2 구조(기구축 feature vs Agentic AI가 추출한 feature → XGBoost/TabPFN)가 요약본에 없음 (p.11–15) |

---

## 추천 인터랙션

### ★ 대표: "Self-evolving Feature Loop" 시뮬레이터 (DNA 암 스크리닝)
- **입력**: 사용자가 [루프 1회 실행] 버튼을 누르거나, [자동 실행] 토글. 추가로 "Option 1(전문가 feature 고정)" / "Option 2(에이전트가 feature 진화)" 라디오 전환.
- **출력**:
  - 왼쪽: 30억 길이를 상징하는 긴 띠(DNA)가 있고, 그 위에 현재 feature 추출 코드(의사코드 3줄, 예: `count(A,C adjacent)`)가 카드로 표시. 루프마다 카드가 "A+B 결합 → C feature"처럼 갱신(이전 카드는 흐리게 히스토리로 쌓임).
  - 오른쪽: stage별(1/2/3/4) 성능 막대 4개. Option 1은 몇 번 눌러도 막대가 거의 안 움직임(제한적 개선). Option 2는 루프마다 stage1 막대가 눈에 띄게 올라감(미리 정한 시나리오 수열, 랜덤 약간).
  - 하단: 에이전트 "사고과정" 말풍선이 타이핑 효과로 출력 ("stage1 성능이 낮네 → A와 B 장점을 결합한 C를 만들면?").
- **시각화**: SVG. 긴 가로 막대(DNA), 둥근 사각형 카드(코드), 세로 막대 차트(성능), 말풍선. 화살표로 "input(feature+성능+파일) → 사고 → output(code)" 순환 루프를 그려 현재 단계만 강조(색 변경).
- **난이도**: 중 (상태 머신 + 미리 정의된 시나리오 배열 6~8스텝, 애니메이션은 CSS transition)
- **교육 포인트**: "AI가 파일을 읽는 게 아니라 코드를 짠다", "루프가 반복되면 feature가 진화한다", "Option 1은 천장이 있다".

### 대안 1: "현상 → 문제" 판별 게임 (Open-Beginning)
- **입력**: 카드 덱(8장)에 '관찰된 현상'(옥수수 색소 얼룩 / 응급실 재입원 패턴 / 설계 의도와 다른 기능 조합 / 단순 센서 잡음 등)이 하나씩 나오고, 사용자가 [잡음으로 무시] / [기존 문제 재구성] / [새 문제 정의] 중 선택.
- **출력**: 선택 후 "실제 역사"가 공개(McClintock은 30년 뒤 노벨상 등)되고, 두 종류의 실패("모든 것에 의미 부여" vs "아무것도 못 봄") 카운터가 올라감. 마지막에 3단 사다리(기존 AI/가설 생성 AI/Open-Beginningness) 중 자신이 어디쯤인지 표시.
- **시각화**: HTML 카드 + 작은 SVG 사다리. 
- **난이도**: 하

### 대안 2: MDA "다음 실험 고르기" (Value of Information 체험)
- **입력**: 가설 3개(A/B/C)의 현재 확률 막대가 있고, 실험 후보 3개 버튼. 각 실험은 특정 가설 쌍만 구분할 수 있다고 미리 정의. 사용자가 실험을 고르면 결과가 나오고 베이즈 업데이트로 확률이 변함.
- **출력**: 확률 막대가 애니메이션으로 이동, "정보 가치(VoI)" 점수를 실험 버튼 위에 힌트로 표시(토글). 최소 횟수로 한 가설을 90% 이상 만들면 클리어.
- **시각화**: SVG 막대 3개 + 버튼. 
- **난이도**: 중 (간단한 이산 베이즈 업데이트 수식 하드코딩)

---

## 다이어그램 후보

### D1. Option 1 vs Option 2 (p.11–15)
- 상단 행: [기구축 feature (전문가 지식, 30억→10만)] → [AI Model (XGBoost, TabPFN)] → [결과] 위에 "성능 개선 제한적" 라벨.
- 하단 행: [DNA Sequence 파일] ← 접근 권한 ← [Self-evolving Agentic AI] → [추출된 feature(코드로 생성)] → [AI Model] → [결과]. 결과에서 Agentic AI로 되돌아가는 점선 화살표 "성능 피드백".
- 라벨: "Any to Code, Code to Any", "파일을 읽는 게 아니라 코드를 짠다".

### D2. AI의 3단 사다리 (p.23)
- 세 개의 가로 레인(아래→위): 
  - 기존 AI: [문제] → [해답 탐색]
  - 가설 생성 AI: [문제] → [가설 1,2,3] → [검증]
  - Open-Beginningness: [수많은 현상 ○○○○] → [무엇이 중요한지 선택] → [질문/문제 생성·재정의] → [탐구]
- 오른쪽에 위로 향하는 큰 화살표 "입력: 문제 → 현상 / 출력: 답 → 문제 정의".

### D3. 자가진화형 과학 발견 시스템 4 Step + MDA inner loop (p.24–25)
- 하단에 Step 1 [Knowledge Foundation: 무엇을 알고 있는가] → Step 2 [Mechanism Discovery: 왜 그렇게 되는가] → Step 3 [Knowledge Discovery: 무엇을 새로 만들 것인가] 가로 배치.
- 상단에 Step 4 [Open-Beginning & Self-Evolving Scientific Reasoning]이 세 Step을 덮는 호(arc) 화살표로 되돌아감.
- Step 2 안에 작은 원형 루프: [LLM: 모델 제안] → [Bayesian: 증거 평가] → [VoI: 다음 실험 선택] → (실험) → 다시 LLM. 라벨 "MDA inner loop".
- 좌측에 수업 주제 매핑(각 Step 옆에 해당 강의 제목 2~3개).

---

## 모델 비교 포인트

> 원칙: Claude/GPT/Gemini의 내부는 대부분 비공개. 아래는 **공개 문서·블로그·모델 카드 범위**에서만 쓰고, 확인 안 된 항목은 "확인 필요"로 둔다. 사이트 구현 전 각 출처 URL을 직접 확인할 것.

| 개념 | 수업에서 다룬 모델·방식 | Claude (공개 문서 범위) | 기타 모델 | 출처 후보 |
|---|---|---|---|---|
| 긴 컨텍스트 한계 (30억 DNA vs 100만 토큰) | "GPT/Gemini는 최대 약 100만 토큰"이라 직접 분석 불가 (p.9) | Claude는 표준 200K 토큰 컨텍스트, 일부 모델은 1M 토큰 컨텍스트 제공(베타/티어 조건은 확인 필요). 어느 쪽이든 30억에는 턱없이 부족 → 수업의 결론(코드로 feature 추출)은 Claude에도 동일하게 적용 | Gemini 1.5/2.x Pro: 1M 토큰(일부 2M, 확인 필요); GPT-4.1: 1M 토큰; Llama 4 Scout: 10M 토큰 주장(실효성 확인 필요) | Anthropic docs "Context windows", Google AI Gemini 모델 페이지, OpenAI GPT-4.1 발표문, Meta Llama 4 블로그 |
| "코드를 짜서 데이터에 접근"하는 에이전트 (Any to Code) | Self-evolving Agentic AI가 DNA 파일 접근 권한을 받아 feature 추출 코드 작성 (p.14–15) | Claude는 **tool use / code execution tool**, **Claude Code**(파일 시스템·셸 접근), **Agent SDK**로 동일 패턴 구현 가능. 수업의 "권한을 준다" = Claude에선 도구(tool) 정의로 접근 범위를 명시 | OpenAI: Code Interpreter / Responses API tools, Agents SDK; Gemini: code execution tool; 공개 모델: Qwen-Agent, Llama + 외부 프레임워크(LangGraph 등) | Anthropic docs "Tool use", "Code execution tool", Claude Code docs; OpenAI Agents SDK docs; Gemini API code execution docs |
| 성능 피드백으로 코드를 개선하는 루프 (Self-evolving) | feature 성능을 입력받아 새 feature 코드 생성 반복 (p.15) | Anthropic 블로그 "Building effective agents"(2024.12)의 evaluator-optimizer 패턴이 같은 구조. Claude 자체가 가중치를 바꾸는 게 아니라 **하네스(외부 루프)**가 진화시킴 — 8주차 하네스 주제와 연결 | AlphaEvolve(Google DeepMind, 2025): Gemini가 코드를 진화시켜 알고리즘 발견 — 수업의 Option 2와 가장 가까운 공개 사례; OpenAI: 공개된 동등 사례 확인 필요 | Anthropic "Building effective agents"; DeepMind AlphaEvolve 블로그/백서 |
| "경험으로 배우는 기계" (Turing 1948) → 보상 기반 학습 | 보상·벌 개념 = RL의 뿌리 (p.16) | Claude는 RLHF + **Constitutional AI(RLAIF)**로 학습됐다고 공개(세부 레시피는 비공개). 4주차 DPO/GRPO와 비교 포인트 | DeepSeek-R1: GRPO 공개; Llama/Qwen: DPO·RLHF 논문·모델카드 공개 | Anthropic "Constitutional AI" 논문(2022), Claude 모델 카드; DeepSeek-R1 논문 |
| 열린 문제(Open-Beginning) / 가설 생성 | 현재 AI는 정의된 문제만 강함 (p.18) | Anthropic은 "Claude for Science"·연구자 지원 프로그램 공개(확인 필요). Claude가 Open-Beginning 능력을 가진다는 공개 주장은 **없음** → "비공개/해당 없음" | Google "AI co-scientist"(2025, Gemini 기반 다중 에이전트 가설 생성) — 수업의 "가설 생성 AI" 2단계에 해당하는 공개 사례; Sakana AI "AI Scientist"(공개 모델/GPT 혼합) | Google Research "AI co-scientist" 블로그; Sakana AI Scientist 논문 |
| 모델 발견 에이전트(MDA): LLM + Bayesian + VoI | MDA 논문 (p.24) | Claude 관련 공개 사례 없음 → "해당 없음" | 논문이 어떤 LLM을 썼는지 **확인 필요** | MDA 논문 (arXiv, 제목으로 검색) |

**사이트에 넣을 '정직성 배지' 제안**: 각 셀에 `공개 문서` / `블로그·발표` / `비공개` / `확인 필요` 4종 배지를 색으로 구분.

---

## 시험 포인트

### 핵심 포인트
1. **정의된 문제 vs 열린 문제**: 지도학습(라벨 가정)·강화학습(보상·환경 가정)·Agentic AI(문제 틀 상속)는 모두 "문제 정의가 고정"을 가정. Open-Beginning Problem은 **문제 자체의 불확실성**을 다룸.
2. **Open-Beginning Problem의 정의**: 증거가 없는 상황에서 (i) 어떤 현상에 지속적 관심을 둘지, (ii) 새 문제를 만들지 vs 기존 문제를 재구성할지 판단하는 문제.
3. **어려운 점 7가지** 중 특히: 문제 정의가 내생적·재귀적, 즉시 평가할 정답 없음, 두 종류 실패의 딜레마.
4. **McClintock 사례**: 색소 패턴 → 이동성 유전요소, 1951 발표 → 1983 노벨상. 핵심 행위 = "설명할 가치가 있음을 알아본 것".
5. **DNA 사례의 논리**: 30억 길이 → 컨텍스트 한계 → Option 1(전문가 feature, 천장 있음) vs Option 2(Agentic AI에 **접근 권한** → 코드로 feature 추출 → 성능 피드백 루프). "파일을 읽는 게 아니라 코드를 짠다".
6. **MDA 3요소**: LLM(모델 제안) + Bayesian Inference(증거 평가) + Value of Information(실험 선택). Open-Beginningness의 inner loop.
7. **AI 3단계**: 문제→답 / 문제→가설→검증 / 현상→선택→문제 생성→탐구.
8. **4 Step 시스템**: Knowledge Foundation → Mechanism Discovery → Knowledge Discovery → Open-Beginning & Self-Evolving Reasoning.
9. **Turing 1948**: learn by experience, 보상·벌.

### 예상 문제
1. **(단답)** Model Discovery Agent(MDA)를 구성하는 세 가지 요소와 각각의 역할을 쓰시오.
   - **정답**: ① LLM — 가능한 새 mechanistic model(가설) 제안 ② Bayesian Inference — 어떤 모델이 현재 증거를 가장 잘 설명하는지 확률적 평가 ③ Value of Information — 후보 모델을 가장 잘 구분할 다음 실험 선택.
   - **해설**: MDA는 Open-Beginningness 구현의 inner loop이며, "어떤 실험을 하면 어떤 메커니즘이 맞는지 가장 많이 알 수 있을까"가 목표.

2. **(서술)** 지도학습·강화학습·Agentic AI가 공통으로 가정하는 것은 무엇이며, Open-Beginning Problem은 이와 어떻게 다른지 설명하시오.
   - **정답**: 셋 모두 문제가 이미 정의되어 있다고 가정한다(지도학습: 목표값·라벨, 강화학습: 보상·환경, Agentic AI: 미리 정해진 문제 틀). 즉 주어진 문제 공간 안에서 명시된 목표를 최적화한다. Open-Beginning Problem은 찾으려던 것도 아니고 현재 문제 정의에 없는 **현상**을 마주쳤을 때, 그 현상에 관심을 둘지와 새 문제를 만들지/기존 문제를 재구성할지를 판단하는 문제로, 데이터/모델의 불확실성이 아니라 **문제 자체의 불확실성**을 다룬다.

3. **(서술)** 30억 길이의 DNA 시퀀스로 암을 스크리닝할 때, LLM의 컨텍스트 한계에도 불구하고 Agentic AI가 기여할 수 있는 방식을 Option 1과 비교하여 설명하시오.
   - **정답**: Option 1은 전문가 지식으로 feature를 추출(30억→10만)해 XGBoost/TabPFN에 넣는 방식으로 성능 개선이 제한적이다. Option 2는 Agentic AI에 DNA 파일 **접근 권한**을 주되, 파일을 통째로 읽는 것이 아니라 파일 구조를 파악해 유의미한 feature를 추출하는 **코드를 작성**하게 한다. 입력은 기존 feature들과 성능, 출력은 새 feature 추출 코드이며, 성능 피드백을 받아 "A와 B를 결합한 C feature" 같은 개선을 반복하는 self-evolving 루프를 돈다(Any to Code, Code to Any).

4. **(단답)** Barbara McClintock의 옥수수 연구가 Open-Beginningness의 예시로 제시되는 이유를 한 문장으로 쓰시오.
   - **정답**: 불규칙성으로 치부될 수 있었던 색소 패턴 변화를 "설명할 가치가 있는 현상"으로 알아보고 세대 간 추적해 이동성 유전요소를 발견했기 때문(1951 발표, 1983 노벨 생리의학상).

5. **(단답/빈칸)** 자가진화형 과학 발견 시스템의 4단계를 순서대로 쓰고, Step 4가 던지는 질문 세 가지를 쓰시오.
   - **정답**: Knowledge Foundation(무엇을 알고 있는가) → Mechanism Discovery(왜 그렇게 되는가) → Knowledge Discovery(무엇을 새로 만들 것인가) → Open-Beginning & Self-Evolving Scientific Reasoning. Step 4의 질문: 무엇을 다음에 검증해야 하는가? 현재의 문제 정의가 맞는가? 더 필요한 새로운 개념 및 실험은 없는가?

6. **(보너스, 단답)** Turing(1948)이 "지능의 증거"로 본 결정적 단계는?
   - **정답**: 경험으로 배우는 것(learn by experience) — 같은 실수를 반복하고 고치지 못하는 고정된 기계는 지능의 증거가 아니며, 학습에는 보상·벌에 해당하는 유리/불리한 결과의 개념이 필요.

---

## 출처

- Sid Sijbrandij 사례: https://centuryofbio.com/p/sid (p.5–6)
- Turing, Alan. "Intelligent machinery (1948)." B. Jack Copeland (ed.), *The Essential Turing* (2004), p.395 (p.16)
- "From Phenomena to Problems: Open-Beginningness and the Next Frontier of AI" (p.18–23; 저자·연도 PDF에 미표기 → 확인 필요)
- "Model Discovery Agent: LLM-assisted Bayesian experiment design for data-efficient discovery of mechanistic world models" (p.24; arXiv 확인 필요)
- Nicholas Carlini, "How to win a best paper award" (2026): https://nicholas.carlini.com/writing/2026/how-to-win-a-best-paper-award.html (p.31)
- 참고 강의 (p.32): UW–Madison CS839 (AI Agents), UC Berkeley CDSS94, CMU 11-711 (Advanced NLP), Stanford CS224R (Deep RL), Stanford CS329A (Self-Improving AI Agents), UC Berkeley CS294/194-280 (Advanced LLM Agents), Boston University AI Methods for Science, AAAI 2026 Tutorial "Agentic AI for Scientific Discovery"
- 연구실: https://mlai.yonsei.ac.kr/ (p.1)

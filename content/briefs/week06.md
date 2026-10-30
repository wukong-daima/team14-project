# 6주차: AI 에이전트 — 정의, Reasoning · Memory · Planning, 제약과 과제, 롱 호라이즌

> **PDF 커버리지**: `week4_agent.pdf`(93p, 제목 "Week 4-1 AI Agent")가 이 주차의 강의 슬라이드다. 사용자의 6주차 요약(에이전트 정의, R/M/P, 학습 동향, 평가, 일정 공지)과 거의 1:1로 대응한다. 일정 공지(중간발표 11/16·11/23, 최종 11/30·12/7, 기말 12/14 19:10 클로즈북)는 PDF에 없고 요약본(구두 공지)에만 있다.

한 줄 요약: 에이전트는 "환경을 인식하고 행동하는 주체"이며, 언어 에이전트는 Reasoning(내부 행동)·Memory(읽기/쓰기 장기 기억)·Planning(행동 선택 알고리즘)으로 구성된다. 환경 조작 공격·일관성 부족·데이터 부족이라는 제약과, 수백 스텝 롱 호라이즌 과제를 위한 RL·하네스 설계를 다룬다.

## 강의 흐름
| 순서 | 섹션 | 페이지 |
|---|---|---|
| 1 | 에이전트 정의(Russell & Norvig), 도메인 예시: 게임·코딩(SWE-bench)·웹(WebArena)·컴퓨터 사용(OSWorld)·RAG/Agentic RAG·과학 발견(AI Scientist-v2) | p.3~13 |
| 2 | 부상과 논쟁(The rise, and the divide), Modern agent = LLM + 환경, LLM-first vs Agent-first, 언어 에이전트 | p.14~20 |
| 3 | 핵심 개념 3종: Reasoning / Memory / Planning, 고전 에이전트 관점과의 화해 | p.21~22 |
| 4 | Reasoning: 내부 행동, ReAct(Apple Remote 예시), CoT가 순차 문제를 푸는 이유, DeepSeek-R1 파이프라인, 증류, s1 budget forcing | p.23~42 |
| 5 | Memory: 장기 기억 읽기/쓰기, RAG는 read-only 기억, Generative Agents(episodic/semantic/procedural), Reflexion, Mem0/Zep | p.43~51 |
| 6 | Planning: 정의, 웹 에이전트(Mind2Web), 패러다임(반응형→트리 탐색→월드 모델), Tree Search(LATS), World model, WebDreamer | p.52~64 |
| 7 | 제약과 과제: 환경 조작(EIA, 팝업 공격), PrivacyLens, τ-bench pass^k, Sleeper Agent, 에이전트 데이터(시연/IDM/VPT), HLE, 신뢰성(GPT-5.5 시스템카드, ASPI), Anthropic 에이전트 Eval 8단계 | p.65~83 |
| 8 | 롱 호라이즌: T1(TITO/R3), Anthropic 하네스 설계(Sprint Contract), LongHorizon-Harness MEA | p.84~93 |

## 핵심 개념

### 1. 에이전트의 정의와 언어 에이전트
- (a) 전공: "센서로 환경을 인식하고 액추에이터로 환경에 행동하는 모든 것"(Russell & Norvig 2020). 도메인마다 환경/관측 공간/행동 공간이 다르다(게임: 스크린샷·인벤토리/조작, 코딩: 저장소·테스트 출력/코드 편집, 웹: DOM·스크린샷/클릭·입력, 컴퓨터 사용: 데스크톱 스크린샷·a11y 트리/키보드·마우스). LLM-first 관점은 "LLM을 에이전트로 만든다"(프롬프트·스캐폴딩 중심), Agent-first 관점은 "에이전트에 LLM을 통합한다"(인식·세계 모델·계획 과제가 그대로 남음). 언어를 추론·소통에 쓰는 현대 에이전트를 언어 에이전트라 부르며, LLM은 수단일 뿐이다.
- (b) 중학생: 로봇 청소기는 센서로 방을 보고 바퀴로 움직이는 에이전트다. 요즘 AI 에이전트는 "말"로 생각하고 "말"로 소통하면서 검색·코딩·클릭 같은 행동을 한다.
- (c) 고유명사: Russell & Norvig, SWE-bench(이슈 195단어, 코드베이스 평균 438,000줄), WebArena, OSWorld, MineDojo, Agentic RAG, AI Scientist-v2
- (d) p.3~20

### 2. Reasoning = 내부 행동(internal action)
- (a) 전공: 사람의 정신 과정에 해당하는 것이 LM의 중간 생성(intermediate generation)이고, 에이전트에게는 외부 환경을 바꾸지 않는 내부 행동이다. 추론은 내부 컨텍스트를 갱신해 이후 외부 행동을 바꾼다. 행동 공간이 클수록 용량은 커지지만 의사결정은 어려워지며, 추론/언어 공간은 무한하다. LLM은 인간의 추론 흔적을 모방해 reasoning prior를 학습한다. Self-reflection은 추론을 대상으로 다시 추론하는 메타 추론이다.
- (b) 중학생: "사과가 좋아"라고 속으로 생각하는 건 세상을 바꾸지 않지만, 나중에 마트에서 사과를 사게 만든다. 생각도 일종의 행동이다.
- (c) 핵심: internal action, inner monologue, reasoning prior, self-reflection(metacognition)
- (d) p.21~32

### 3. ReAct: 추론이 행동을 돕는 방식
- (a) 전공: Apple Remote 예시에서 행동만(Act→Obs 반복) 하면 "Front Row (software)" 검색 후 엉뚱하게 종료하고, 추론만 하면 iPhone/iPad라는 그럴듯한 오답을 낸다. Thought와 Act를 교차(Thought 1 → Act 1 → Obs 1 → … → Finish[keyboard function keys])하면 검색 결과를 해석해 올바른 답에 도달한다. 추론은 환경 상태 유추·과거 회고·재계획을 통해 더 나은 행동을 끌어내는 수단이다.
- (b) 중학생: 보물찾기에서 힌트를 읽기만 하거나(추론만) 아무 데나 파기만 하면(행동만) 못 찾는다. "힌트 읽기 → 파보기 → 결과 보고 다시 생각하기"를 반복해야 한다.
- (c) 핵심: Thought/Act/Obs 루프, Search[...], Finish[...]
- (d) p.28~30

### 4. CoT가 순차 문제를 푸는 이유와 추론 모델(DeepSeek-R1, s1)
- (a) 전공: 깊이가 고정된 트랜스포머도 충분히 긴 중간 추론 스텝을 생성하면 본질적으로 순차적인 문제를 풀 수 있고, 정답만 바로 내는 트랜스포머는 매우 깊은 네트워크가 필요하거나 못 푼다(Transformers는 병렬에 강하고 순차에 약함). DeepSeek-R1은 cold-start SFT(최소 추론 형식) → 정답이 명확한 수학·코딩에 reasoning-oriented RL → rejection sampling+SFT → 전 시나리오 RL 4단계로 학습했고, 강한 추론 모델(o3, R1)로부터 증류하면 Llama 같은 모델도 추론 능력을 얻는다. s1은 1,000개 고품질 문제(s1K)로 SFT한 뒤 budget forcing(토큰 상한에서 end-of-thinking 강제 삽입, 멈추려 하면 "Wait" 추가)으로 test-time scaling을 가장 단순하게 구현했다.
- (b) 중학생: 암산으로 한 번에 답을 내려면 머리가 엄청 좋아야 하지만, 종이에 한 줄씩 풀면 보통 머리로도 풀린다. "잠깐(Wait), 다시 볼까?"를 붙이면 스스로 실수를 고친다.
- (c) 핵심: CoT·순차 문제, cold-start, reasoning-oriented RL, rejection sampling, 증류, s1K(59,029→51,581→24,496→1,000), budget forcing("Wait")
- (d) p.38~42

### 5. Memory: 읽기/쓰기 가능한 장기 기억
- (a) 전공: 장기 기억은 경험·지식·기술을 저장하고 읽기/쓰기가 가능해야 한다. RAG의 검색 코퍼스는 타인(위키 편집자)이 쓴 read-only 기억이라 에이전트에게 최적이 아니므로 자율적 쓰기가 필요하다. Generative Agents는 컨텍스트 창에 모든 이벤트를 담을 수 없어 기억이 필요함을 보였고, 기억은 episodic(경험, append-only 이벤트 스트림), semantic(지식, LLM이 이벤트를 추론해 기록), procedural(기술, 코드 기반 skill)로 나뉜다. Reflexion은 RL 없이 보상을 자연어 요약으로 바꿔 기억에 저장하고 다음 시도의 컨텍스트로 써 시행착오 학습을 한다. 서비스로는 Mem0(선별 저장 semantic memory), Zep(시간 인식 지식 그래프)가 있다.
- (b) 중학생: 일기(있었던 일), 노트 정리(배운 것), 자전거 타기(몸이 기억하는 기술)가 각각 다른 기억이다. 틀린 뒤 "다음엔 이렇게 하자"를 적어두고 다시 도전하는 게 Reflexion이다.
- (c) 핵심: read/write, read-only retrieval, episodic/semantic/procedural, Reflexion(verbal reinforcement), Mem0, Zep
- (d) p.43~51

### 6. Planning: 반응형 → 트리 탐색 → 월드 모델
- (a) 전공: 언어 에이전트의 계획은 목표가 자연어로 표현되고 행동 공간이 열려 있으며 goal test가 어려워지는 방향으로 간다. 반응형(reactive) 계획은 빠르지만 근시안적이고, 실제 환경에서의 트리 탐색(LATS, Tree Search for LM Agents)은 체계적이지만 행동을 되돌릴 수 없고(비가역) 위험하며 느리다. 그래서 환경 전이 동역학 s_t, a_t → s_{t+1}을 모사하는 월드 모델이 필요하며, LLM은 상태 전이를 꽤 잘 예측한다. WebDreamer는 GPT-4o 또는 Dreamer-7B를 월드 모델로 써 실제 환경 접근 전에 후보 경로를 자연어로 시뮬레이션한다.
- (b) 중학생: 체스에서 아무 수나 두면(반응형) 지고, 실제로 말을 옮겨보며 탐색하면 무르기가 안 된다. 머릿속으로 "이렇게 두면 저렇게 되겠지"를 상상(월드 모델)하는 게 가장 안전하고 빠르다.
- (c) 핵심: branching/backtracking/exploration(v=0.5→0.45→0.68→1.0), 비가역 행동, world model, WebDreamer, Mind2Web
- (d) p.52~64

### 7. 제약과 과제: 환경 조작·프라이버시·일관성·백도어
- (a) 전공: EIA(Environmental Injection Attack)는 정상처럼 보이는 악성 콘텐츠로 웹 에이전트에 최대 70% 공격 성공률을 달성하고, 적대적 팝업은 OSWorld/VisualWebArena에서 에이전트 행동의 70~90%를 유도했다. PrivacyLens는 모호한 지시를 따르다 이직 정보를 이메일로 노출하는 등 문맥적 프라이버시 규범 위반을 평가한다. τ-bench의 pass^k는 k번 독립 시도가 모두 성공할 확률로 일관성을 측정한다(pass@k는 하나라도 성공). Sleeper Agents는 트리거가 있을 때만 악의적으로 행동하도록 학습된 모델이 SFT/RL/adversarial training을 거쳐도 백도어를 유지함을 보였다. ASPI는 "모호하면 질문하라"는 원칙이 오히려 프롬프트 인젝션 채널(사용자 답변, 도구 출력, ask_user 반환)을 늘림을 지적한다.
- (b) 중학생: 가짜 "확인" 버튼에 속아 눌러버리거나, 남의 비밀을 메일에 써버리거나, 10번 중 3번은 실수하는 로봇은 믿고 쓰기 어렵다.
- (c) 핵심: EIA 70% ASR, 팝업 70~90%, PrivacyLens, pass^k vs pass@k, Sleeper Agent 3단계, ASPI 3채널
- (d) p.66~70, 78~79

### 8. 에이전트 데이터 부족과 평가 설계
- (a) 전공: 에이전트 데이터(관측-행동 쌍 궤적)는 수집(과제 정의·인프라·시연·검증)과 공유(이질적 관측/행동 공간)가 어렵다. 통일안은 관측=스크린샷, 행동=범용 마우스·키보드. 인터넷 영상은 많지만 grounded trajectory가 없어 IDM(Inverse Dynamics Model, (o_t, o_{t+1}) → a_t)으로 행동을 복원하는 VPT가 제안됐다. Anthropic의 "Demystifying evals"는 평가를 마지막 시험이 아니라 개발 피드백 루프로 보고 8단계(20~50개 과제로 일찍 시작, 사람이 손으로 확인하던 것부터, 모호하지 않은 과제+정답 예시, positive/negative 균형, 깨끗한 환경, deterministic/LLM/human grader, 점수 대신 transcript 읽기, 포화 시 regression/capability eval 분리, 살아 있는 suite)를 제시한다.
- (b) 중학생: 유튜브에 요리 영상은 많지만 "어느 버튼을 눌렀는지"는 안 나온다. 그걸 추측해 주는 모델이 IDM이다. 시험은 끝에 한 번 보는 게 아니라 매일 작은 쪽지시험으로 뭘 못하는지 찾는 게 낫다.
- (c) 핵심: trajectory, IDM, VPT, "에이전트의 ImageNet", eval saturation, regression vs capability eval
- (d) p.71~77, 80~83

### 9. 롱 호라이즌 에이전트: T1, 하네스, MEA
- (a) 전공: T1은 리눅스 터미널에서 수백 번 명령을 실행하는 과제를 RL로 학습하되, sparse reward(전부 성공 1/아니면 0)를 verifier 부분 보상으로 바꾸고, 추론(SGLang)-학습(Megatron-Core+Transformer Engine) 불일치를 TITO(토큰 ID 재사용)와 R3(MoE 전문가 인덱스 재사용)로 해결했다. Anthropic 하네스 실험은 긴 작업에서 생기는 context anxiety와 자기 평가 과신 때문에 Planner→Generator→Evaluator를 분리하고 Sprint Contract(코딩 전 acceptance criteria 합의, contract.md/feedback.md 파일로 소통)를 도입해 20분→6시간짜리 완성도 높은 결과를 얻었고, Opus 등장 후 스프린트 구조를 제거했다. LongHorizon-Harness는 compounding error·context rot·task-state loss를 지적하며 MEA(Manager: task state 관리, Executor: 과거 컨텍스트 없이 한 subtask 수행, Auditor: read-only 검증)로 롱 호라이즌 실행을 "검증된 task-state 전이의 연속"으로 재정의한다.
- (b) 중학생: 긴 숙제는 계획 짜는 사람, 하는 사람, 검사하는 사람을 나누고, 검사에 통과한 것만 "끝남"으로 적는다. 하는 사람이 "다 했어요"라고 해도 그냥 믿지 않는다.
- (c) 핵심: T1, TITO, R3, context anxiety, Sprint Contract, MEA(Manage–Execute–Audit), compounding error, context rot
- (d) p.85~93

## 요약본 정정
- "딥식 아론 모델" → **DeepSeek-R1** (p.39~40)
- "GPT와 같은 고성능 모델을 이용한 지식 증류" → 슬라이드 예시는 **GPT-o3, DeepSeek-R1**을 교사로, Llama를 학생으로 (p.40)
- "T* 논문" → **T1: Terminal Agent Reinforcement Learning for Long-Horizon Tasks** [arXiv 2026] (p.85~88). 동기화 기법명은 **TITO**(토큰), **R3**(MoE 전문가 인덱스)
- "프레임워크(vLLM, Llama-factory 등) 간의 불일치" → 슬라이드는 롤아웃 **SGLang**, 학습 **Megatron-Core + Transformer Engine** (p.87). Llama-factory는 PDF에 없음
- "OpenAI/Anthropic 등은 자체 레드팀 데이터셋 구축 및 에이전트를 통한 자동 평가" → PDF 근거는 Anthropic "Demystifying evals for AI agents" 8단계(p.80~83)와 OpenAI GPT-5.5 System Card의 데이터 파괴 행동 평가(p.78). "레드팀 데이터셋"이라는 표현은 PDF에 없음(구두 설명 가능)
- "초기에는 풀이 과정 데이터로 SFT 후 정답만으로 RL" → R1은 **cold-start SFT → reasoning RL → rejection sampling & SFT → 전 시나리오 RL** 4단계 (p.39)
- "공간 지각 능력(Spatial Reasoning) 향상" → PDF에서 해당 슬라이드 없음 → 구두 설명으로 보임, 확인 필요
- "에이전트 평가 가이드라인 표준화 없음" → 맞음. 추가로 τ-bench **pass^k**(일관성 지표)가 PDF에 있음 (p.69)
- 발표·시험 일정은 PDF에 없음 → 요약본만 근거(강의 공지 재확인 권장)

## 추천 인터랙션

### 대표: ReAct 에이전트 루프 스텝 실행기 (난이도: 중)
- 입력: 질문 선택(기본: PDF의 Apple Remote 문제), 모드 토글 [행동만 / 추론만 / ReAct], [다음 스텝 ▶] 버튼, [자동 재생]
- 출력: 왼쪽에 Thought(연한 노랑)·Act(파랑)·Obs(회색) 카드가 한 스텝씩 쌓이고, 오른쪽에 "단기 메모리(컨텍스트 창)" 패널이 토큰 수 게이지와 함께 갱신. 하단에 환경 박스(가짜 위키 검색 결과 사전 정의). Finish 시 정답 비교: 행동만 → `Finish[yes]` (오답), 추론만 → `iPhone, iPad, iPod Touch` (오답), ReAct → `keyboard function keys` (정답)
- 시각화 포인트: Thought 카드는 환경 박스에 화살표가 가지 않고(내부 행동) 메모리 패널만 바꾸는 반면, Act 카드는 환경으로 화살표가 가고 Obs가 돌아온다. 세 모드를 나란히 재생해 "추론은 외부 행동을 바꾸는 수단"임을 보여줌
- 확장: 실패 후 [Reflexion] 버튼 → "다음엔 검색 결과를 해석하고 Front Row (software)로 재검색" 메모가 장기 메모리 패널에 추가되고 2회차 시도가 성공

### 대안 1: pass@k vs pass^k 계산기 (난이도: 하)
- 입력: 단일 시도 성공확률 p 슬라이더, k 슬라이더(1~10)
- 출력: 두 곡선 pass@k = 1−(1−p)^k (점선, 상승), pass^k = p^k (실선, 하락)을 같은 축에 그림. p=0.8, k=5에서 pass@k≈0.9997 vs pass^k≈0.33을 숫자로 강조. "벤치마크 점수는 높은데 실제로 믿기 어려운 이유"

### 대안 2: 트리 탐색 + backtracking 플레이어 (난이도: 중)
- 입력: PDF p.57의 트리(노드 ①~⑩, value 0.5/0.45/0.68/1.0 사전 정의), [탐색 한 스텝], [월드 모델 모드] 토글
- 출력: 현재 경로 하이라이트, 낮은 value에서 파란 점선 backtracking 애니메이션, terminal v=1.0 도달 시 성공. 월드 모델 모드에서는 실제 환경 박스가 회색(접근 없음)이 되고 "상상 속 시뮬레이션" 패널에서만 노드가 열림 → 비가역 행동·비용 문제를 피하는 이유 설명

## 다이어그램 후보 (정적 SVG)
1. **언어 에이전트 구조도**: 가운데 LLM(cognitive core), 왼쪽 Percepts 입력, 오른쪽 Action 출력. 내부 루프 화살표 "Reasoning → 단기 기억(컨텍스트 창) 갱신", 아래 장기 기억 박스(episodic/semantic/procedural)에 Read/Write 양방향 화살표, 위에 Planning(행동 선택 알고리즘) 배지. 외부 환경 박스에 게임/코드/웹/데스크톱 아이콘
2. **Planning 3패러다임 비교**: 세 열 — 반응형(한 줄 화살표, "빠름·근시안"), 실제 환경 트리 탐색(가지와 X표 비가역, "체계적·느림·위험"), 월드 모델 탐색(머릿속 구름 안의 트리, 실제 환경은 마지막 한 번만 접촉). 각 열 하단에 장단점 태그
3. **롱 호라이즌 하네스 MEA**: Manager(task state: requirements/artifacts/facts) → Executor(subtask 1개, 과거 컨텍스트 없음) → Auditor(read-only 검사) → "completed" 기록은 Auditor 통과 시에만(초록 체크). 옆에 단일 세션 방식의 문제(compounding error, context rot, task-state loss)를 빨간 경고로

## 모델 비교 포인트
| 개념 | 수업에서 다룬 모델·방식 | Claude (공개 문서 범위) | 기타 모델 | 출처 후보 |
|---|---|---|---|---|
| Reasoning 노출 방식 | DeepSeek-R1: 추론 과정(CoT)을 그대로 출력 | **extended thinking** 공개 기능(사고 블록 제공; 일부 버전은 요약된 thinking) | OpenAI o-시리즈: 추론 요약만 노출. Qwen3: thinking/non-thinking 모드 전환 | Anthropic docs(extended thinking), DeepSeek-R1 논문, OpenAI o1 system card |
| 추론 모델 학습 | R1 4단계(cold-start→RL→RS+SFT→RL), s1 budget forcing | 추론 학습 레시피 **비공개**; thinking budget(토큰 예산) 파라미터는 공개 API 기능 — s1의 max computation limit과 유사한 사용자 제어 | o1/o3: 비공개. Qwen3: 공개 보고서 | 확인 필요 |
| Memory | Generative Agents 3종 기억, Reflexion, Mem0/Zep | 제품 레벨 **memory 기능**(2025, 공개 발표), Claude Code의 CLAUDE.md·memory 파일(semantic/procedural 기억에 해당) — 내부 구현 세부 비공개 | ChatGPT memory(공개 발표), Mem0/Zep 서드파티 | Anthropic 발표 자료, OpenAI 발표 자료 (확인 필요) |
| Planning | 반응형/트리 탐색/월드 모델(WebDreamer) | Claude Code **plan mode**(공개 기능); Anthropic "Building effective agents"(2024.12)는 workflow vs agent 구분과 단순 구조 권장 | OpenAI Codex, Google ADK 등 | Anthropic 블로그 2024.12 |
| 컴퓨터 사용 | OSWorld 벤치마크, 팝업 공격 취약성 | **computer use** 공개 기능(2024.10 베타), OSWorld 점수 공개 | OpenAI Operator/CUA | Anthropic 발표, OSWorld |
| 안전·신뢰성 | Sleeper Agents, EIA, PrivacyLens, ASPI, pass^k | Sleeper Agents 논문은 **Anthropic 자체 연구**(Hubinger et al. 2024); 프롬프트 인젝션 대응은 system card에 공개(세부 확인 필요) | GPT-5.5 System Card: 데이터 파괴 행동 평가(p.78) | p.70, p.78~79 |
| 에이전트 평가 | 표준 가이드라인 부재, τ-bench | Anthropic "Demystifying evals for AI agents" 8단계 공개(p.80~83) | OpenAI evals | p.80~83 |
| 롱 호라이즌 하네스 | T1 RL, MEA | Anthropic 하네스 실험(Planner/Generator/Evaluator, Sprint Contract, Opus 후 제거) 공개; Claude Code subagent 등 | LongHorizon-Harness(Claude Code·Codex를 감싸는 하네스) | p.89~93 |

## 시험 포인트
1. 에이전트 정의(Russell & Norvig)와 도메인별 환경/관측/행동 공간 예시
2. Reasoning이 "내부 행동"인 이유, 추론 공간이 무한하다는 점, self-reflection = 메타 추론
3. ReAct 예시: 행동만/추론만/교차의 결과 차이 (Apple Remote → keyboard function keys)
4. CoT가 순차 문제를 푸는 이유(고정 깊이 트랜스포머 + 긴 중간 스텝), R1 4단계, s1 budget forcing
5. RAG는 read-only 기억 → 쓰기 가능한 기억 필요; episodic/semantic/procedural 구분; Reflexion
6. Planning 3패러다임의 장단점과 월드 모델의 정의(s_t, a_t → s_{t+1})
7. 제약: EIA/팝업 공격 수치, PrivacyLens, pass^k 정의, Sleeper Agent 3단계, 에이전트 데이터 수집/공유 어려움과 IDM
8. 롱 호라이즌: sparse reward 해결, TITO/R3, Generator/Evaluator 분리 이유, MEA에서 Auditor 역할

### 예상 문제
1. **Q.** 에이전트에게 Reasoning이 "내부 행동"으로 간주되는 이유를 설명하고, 외부 행동과의 차이를 예로 들라.
   **A.** 추론(토큰 생성)은 외부 환경 상태를 직접 바꾸지 않고 내부 컨텍스트(단기 기억)만 갱신하지만, 그 결과 이후 외부 행동(검색·클릭)의 선택이 달라진다. 예: "사과가 좋아"라는 생각은 환경을 바꾸지 않지만 마트에서 사과를 사게 만든다.
2. **Q.** Apple Remote 문제에서 행동만 하는 에이전트와 추론만 하는 에이전트가 각각 왜 실패했는지, ReAct는 왜 성공했는지 쓰라.
   **A.** 행동만: 검색 결과를 해석하지 않고 Front Row (software)에서 Finish[yes]로 엉뚱하게 종료. 추론만: 외부 정보 없이 Apple TV라는 그럴듯한 오답(iPhone/iPad/iPod Touch) 생성. ReAct: Thought로 "무엇을 검색해야 하는지" 정하고 Obs를 해석해 keyboard function keys라는 정답에 도달.
3. **Q.** Generative Agents가 제시한 세 가지 기억 유형과 각각의 쓰기 방식을 쓰고, 일반 RAG가 에이전트 기억으로 불충분한 이유를 설명하라.
   **A.** Episodic(경험, append-only 이벤트 스트림), Semantic(지식, LLM이 이벤트를 추론해 기록), Procedural(기술, 코드 기반 skill). RAG 코퍼스는 타인이 작성한 read-only 기억이라 에이전트 자신의 경험을 반영하지 못하므로 자율적 쓰기가 필요하다.
4. **Q.** 실제 환경에서의 트리 탐색 계획의 세 가지 문제와, 월드 모델이 이를 어떻게 해결하는지 WebDreamer를 예로 설명하라.
   **A.** 행동이 비가역적이라 backtracking 불가, 안전·프라이버시 위험, 추론 시점 탐색이 느리고 비쌈. 월드 모델은 s_t, a_t → s_{t+1}을 예측하는 모델로, WebDreamer는 GPT-4o/Dreamer-7B로 후보 상호작용을 자연어로 시뮬레이션해 실제 환경 접근 전에 각 경로의 성공 가능성을 평가한다.
5. **Q.** τ-bench의 pass^k를 정의하고 pass@k와의 차이를 쓰라. p=0.8, k=3일 때 각각의 값을 구하라.
   **A.** pass^k = 동일 과제를 k번 독립 시도해 모두 성공할 확률 = p^k (일관성·신뢰성 지표), pass@k = 하나라도 성공 = 1−(1−p)^k. p=0.8, k=3: pass^k = 0.512, pass@k = 0.992.
6. **Q.** Sleeper Agent 실험의 3단계를 쓰고, 오픈 웨이트 모델 도입 시 시사점을 설명하라.
   **A.** (1) 정상 프롬프트에선 정상, 트리거 포함 시 악의적으로 행동하도록 학습 (2) SFT/RL/adversarial training 등 표준 안전 기법 적용 (3) 테스트에선 안전해 보이지만 트리거 시 유해 행동 유지. 시사점: 표준 안전 학습으로 백도어를 제거했다고 보장할 수 없으므로 외부 오픈 웨이트 모델은 별도 검증이 필요하다.

## 출처
- Language Agent Tutorial: https://language-agent-tutorial.github.io/ (p.4~63 대부분)
- Berkeley LLM Agents course: https://rdi.berkeley.edu/llm-agents/f24 (p.33~37)
- SWE-bench: Can Language Models Resolve Real-World GitHub Issues? / MLE-bench (p.6)
- The AI Scientist-v2 (p.8); WebArena (p.9); OSWorld (p.11); MineDojo (p.5); IdeaBrowser (p.7)
- Chain of Thought Empowers Transformers to Solve Inherently Serial Problems (p.38)
- DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning; A Visual Guide to Reasoning LLMs (p.39~40)
- s1: Simple test-time scaling (p.41~42)
- Generative Agents: Interactive Simulacra of Human Behavior [UIST 23] (p.46~49)
- Reflexion: Language Agents with Verbal Reinforcement Learning [NeurIPS 2023] (p.50)
- Mem0 https://mem0.ai/ ; Zep https://www.getzep.com/ (p.51)
- Mind2Web [NeurIPS 2024] (p.54); Koh et al. "Tree Search for Language Model Agents" arXiv:2407.01476; Zhou et al. LATS ICML 2024 (p.57)
- Gu et al. "Is Your LLM Secretly a World Model of the Internet?" arXiv:2411.06559 (WebDreamer, p.64)
- EIA: Environmental injection attack arXiv:2409.11295 (p.66); Attacking Vision-Language Computer Agents via Pop-ups arXiv:2411.02391 (p.67)
- PrivacyLens arXiv:2409.00138 (p.68); τ-bench (p.69); Sleeper Agents arXiv:2401.05566 (p.70)
- Video PreTraining (VPT) (p.75); Humanity's Last Exam https://agi.safe.ai/ (p.77)
- GPT-5.5 System Card [OpenAI 2026] (p.78); ASPI [arXiv 2026] (p.79)
- Demystifying evals for AI agents [preprint 2026] (p.80~83)
- T1: Terminal Agent Reinforcement Learning for Long-Horizon Tasks [arXiv 2026] (p.85~88)
- Harness design for long-running application development [preprint 2026] (p.89~90)
- LongHorizon-Harness: Advancing LongHorizon Agents for Real-World Tasks [arXiv 2026] (p.91~93)

# 8주차: 하네스 엔지니어링과 자가 진화 에이전트 (Self-Evolving Agentic AI, Week 5-1)

**한 줄 요약:** 모델 가중치를 고정한 채 모델을 둘러싼 "하네스"(컨텍스트·워크플로우·메모리·서브에이전트·평가)를 설계하고 자동으로 진화시키는 방법을 배우고, 그 성능 향상이 정말 "똑똑해진 것"인지(일반화 G) 아니면 "벤치마크 암기"(오버피팅 O)·"돈을 더 쓴 것"(테스트타임 스케일링 T)인지 분해해서 검증하는 법을 익힌다.

> 파일명은 `week5_self_evolving_agent.pdf`(슬라이드 표지 "Week 5-1")이지만 사용자 기준 8주차 수업이다. 슬라이드 목차(p.7~8)에는 Reflexion, Voyager, A-MEM, GEPA, AlphaEvolve, R-Zero, Range-GRPO, Evo-Bench 등이 더 있지만, 이번 수업 본문(p.9~92)은 **"Introduction: Harness Engineering and the Foundations of Self-Improvement"** 파트만 다룬다. 나머지는 다음 주차(Week 5-2 이후) 범위로 추정.

---

## 강의 흐름

| 순서 | 섹션 | 페이지 | 출처 |
|---|---|---|---|
| 0 | 도입: Turing "Intelligent Machinery"(1948) — 경험으로 배우는 기계, 에이전트 정의(Russell & Norvig), Modern agent = LLM + 환경, 자가 진화 에이전트 정의, Reasoning/Memory/Planning | p.2~6 | language-agent-tutorial.github.io |
| 1 | 목차 (전체 커리큘럼) | p.7~8 | — |
| 2 | **하네스 엔지니어링 개론**: RSI 역사(Good 1965, Yudkowsky 2008), 하네스 정의, 디자인 패턴 3개(워크플로우 자동화·파일시스템 메모리·서브에이전트), 코딩 에이전트 사례(Claude Code 등), 하네스 vs 핵심 지능 | p.9~19 | "Harness Engineering for Self-Improvement" |
| 3 | **하네스 최적화 5갈래**: 컨텍스트 엔지니어링(ACE → MCE → Meta-Harness), 워크플로우 디자인(AI Scientist, ScientistOne, Autodata agent, ADAS, AFlow), 자기개선 하네스(STOP, Lin et al., Self-Harness, AHE), 진화 탐색(Promptbreeder, GEPA, AlphaEvolve, ThetaEvolve, DemoEvolve, ShinkaEvolve, DGM, Hyperagents), 가중치 공동 최적화(SIA, Continual Harness) | p.20~50 | 동일 |
| 4 | **미래 과제**: 자동 연구의 6가지 실패 모드(Trehan & Chopra 2026), RSI 병목 7가지 | p.51~53 | 동일 |
| 5 | **하네스 진화 성능 분해(HDA)**: O/T/G 정의, B·B_cc·E·E_neutral, 실험 결과(ALFWorld 98% 오버피팅 등), 시사점 | p.54~66 | "What Evolves When We Talk About Harness Evolution?" |
| 6 | **에이전트 평가 입문**: eval 구조(task/trial/grader/transcript/outcome/harness), Opus 4.5 τ²-bench 허점 사례, 3종 grader, capability vs regression eval, 코딩/대화/리서치/컴퓨터 사용 에이전트별 평가, 0→1 로드맵 8단계, Petri | p.67~92 | Anthropic 블로그 "Demystifying evals for AI agents" |

---

## 핵심 개념

### 1. 하네스(Harness)와 재귀적 자기개선(RSI)
- **(a) 전공:** 하네스는 베이스 모델을 둘러싸고 실행을 오케스트레이션하는 시스템으로, 모델이 *어떻게 생각·계획하고, 툴을 호출해 행동하고, 컨텍스트를 인지·관리하고, 산출물을 저장하고, 결과를 평가할지*를 결정한다(p.11). RSI는 I. J. Good(1965)의 "ultraintelligent machine"에서 시작해 Yudkowsky(2008)가 "AI가 자기 지능을 만드는 인지 기계장치를 자기 지능으로 개선하는 피드백 루프"로 정의했다(p.10). 현대적 해석에서 이 루프는 (1) 가중치 직접 수정, (2) 학습 파이프라인 개선, (3) **배포 시스템(deployment system)** 개선을 포함하며, 배포 시스템 = 하네스 + API/서빙 + 인프라 + 모니터링 + 보안이다(p.11). 초기 프레임워크의 `agent = LLM + memory + tools + planning + action`에 비해 하네스 엔지니어링은 워크플로우(루프) 설계·평가·권한 제어·영속 상태 관리까지 포함해 "프롬프트 템플릿"이 아닌 "런타임/소프트웨어 시스템 설계"에 가깝다(p.14).
- **(b) 중학생:** 모델이 "뇌"라면 하네스는 뇌에 붙은 손·눈·수첩·규칙집이다. 뇌는 그대로 두고, 수첩을 어떻게 쓰고 언제 손을 움직일지 규칙을 더 잘 짜면 같은 뇌로도 훨씬 일을 잘하게 된다. "스스로 더 좋아지는 AI"는 처음엔 뇌를 고치는 게 아니라 이 수첩과 규칙집을 스스로 고치는 것부터 시작한다.
- **(c) 키워드:** Good(1965), Yudkowsky(2008), deployment system, "Harness + API/Serving + Infra + Monitoring + Security"
- **(d) 페이지:** p.10~14, 19

### 2. 하네스 디자인 패턴 3가지
- **(a) 전공:** ① **워크플로우 자동화** — plan → execute → observe/test → improve → execute 의 목표 지향 루프를 모델이 돌 수 있게 정의. 모델이 자기 궤적(trajectory)과 실패 사례를 분석해 "agent runtime" 안에서 반복한다. Karpathy의 `autoresearch` 저장소가 깔끔한 예시(p.15). ② **파일시스템을 영속 메모리로** — 전체 워크플로우와 로그를 컨텍스트에 싣지 말고 파일에 durable state를 둔다. 실험 로그·코드 diff·에러 트레이스·과거 롤아웃은 학습된 컨텍스트 길이를 훨씬 넘기 때문이고, 파일 읽기/쓰기(bash)는 LLM의 기초 능력이라 모델이 좋아질수록 자연히 같이 좋아진다(p.16). ③ **서브에이전트와 백엔드 잡** — 여러 가설 탐색·동시 실험·격리된 하위작업 위임을 위해 병렬 서브에이전트를 띄우고, 부모 에이전트는 작은 프로세스 매니저(launch/inspect logs/cancel/merge) 역할을 한다. **핵심은 병렬성을 명시적이고 검사 가능하게 만드는 것**: 서브에이전트 출력이 휘발성 채팅 컨텍스트에만 있으면 금방 사라지므로 파일·로그·상태 레코드로 저장해야 중단 후 복구와 실행 이력 추론이 가능하다(p.17). 코딩 에이전트(Claude Code, Codex, OpenCode, Cursor류)의 핵심 인터페이스는 이 루프로 수렴했다(p.18).
- **(b) 중학생:** ① 숙제를 "풀고 → 채점하고 → 틀린 거 고치고 → 다시 풀기"를 자동으로 반복하는 규칙. ② 머릿속(컨텍스트)에 다 외우려 하지 말고 공책(파일)에 적어두기. ③ 친구 셋에게 다른 방법을 동시에 시켜보되, 각자 결과를 종이에 적어 내게 해야 나중에 누가 왜 틀렸는지 알 수 있다.
- **(c) 키워드:** plan-execute-observe-improve loop, `karpathy/autoresearch`, durable state in files, explicit & inspectable parallelism
- **(d) 페이지:** p.15~18

### 3. 하네스 최적화의 진행 방향과 5가지 축
- **(a) 전공:** 최적화 대상은 `instruction prompts → structured context → workflow → harness code → optimizer code` 순으로 깊어진다(p.20). 축은 ① **Context Engineering**(모델이 받는 정보의 내용·구조·관리), ② **Workflow Design**(계획·실행·협조 방식), ③ **Self-Improving Harness**(에이전트가 자기 실행 시스템을 반복 개선), ④ **Evolutionary Search**(후보 생성·평가·선택), ⑤ **Joint Optimization with Model Weights**(파라미터와 하네스 동시 최적화)이다. 하네스가 코드이므로 LLM이 코드를 최적화할 수 있으면 손으로 쓴 프롬프트보다 훨씬 큰 설계 공간에 접근한다(p.30).
- **(b) 중학생:** 처음엔 "질문을 잘 쓰는 법"만 고치다가, 다음엔 "참고 자료 정리법", 그다음엔 "일하는 순서", 그다음엔 "일하는 순서를 짜는 프로그램", 결국엔 "그 프로그램을 고치는 프로그램"까지 고치게 된다.
- **(c) 키워드:** 5 axes, "code is a universal language for defining programs and systems"
- **(d) 페이지:** p.12, 20, 30

### 4. ACE (Agentic Context Engineering, 2025)
- **(a) 전공:** 컨텍스트를 "점점 길어지는 프롬프트"가 아닌 **진화하는 플레이북(playbook)** 으로 다룬다. 플레이북은 식별자+설명이 달린 bullet point 모음이고, 세 구성요소가 유지한다: **Generator**(bullet을 참조해 과제 궤적 생성) → **Reflector**(성공/실패 궤적에서 통찰 증류) → **Curator**(증분적·항목화된 엔트리로 플레이북 갱신)(p.21). 이전 메모리 시스템의 두 한계 — **Context Collapse**(반복 재작성으로 과거 경험 정보가 유실·과단순화됨), **Brevity Bias**(LLM이 지나치게 간결한 지시를 선호해 세부를 빠뜨림) — 를 **Delta Update**(전체 재작성/요약 없이 필요한 변경분만 생성)로 해결한다(p.22). 다만 갱신 규칙과 전체 워크플로우는 여전히 수작업(handcrafted)이다(p.23).
- **(b) 중학생:** 오답노트를 매번 처음부터 다시 쓰면 예전에 적어둔 중요한 팁이 사라진다(붕괴). 그래서 ACE는 "오늘 새로 배운 것 한 줄만 추가"하는 방식으로 노트를 키운다. Git에서 파일 전체를 다시 올리지 않고 바뀐 줄만 커밋하는 것과 같다.
- **(c) 키워드:** Generator / Reflector / Curator, Context Collapse, Brevity Bias, Delta Updates
- **(d) 페이지:** p.21~23

### 5. MCE (Meta Context Engineering, Ye et al. 2026)와 Meta-Harness (Lee et al. 2026)
- **(a) 전공:** MCE는 **메커니즘(컨텍스트를 어떻게 관리할지)** 과 **산출물 내용(컨텍스트에 무엇이 들어갈지)** 을 분리한다. **Meta-Agent**가 "Agentic Crossover → Skill Generation"으로 컨텍스트 엔지니어링 방법 자체(학습 절차, 에러 분석 코드, 컨텍스트 템플릿, 검증 방법, 검색·필터링 같은 동적 연산자)를 자유 형식 **스킬**로 진화시키고, **Base-Agent**는 그 스킬을 실행해 과제별 컨텍스트를 생성·정제한다(Training Rollouts → Context Function). ACE와 달리 휴리스틱 규칙을 강제하지 않고 스킬과 스킬에 조건화된 컨텍스트를 공진화시킨다(p.23~24). **Meta-Harness**는 한 단계 더 내려가, "무엇을 저장·검색·제시할지 결정하고 최적화하는 코드" 자체를 최적화 대상으로 삼는 "하네스를 최적화하는 하네스"다. 제안자(proposer)는 코딩 에이전트이고, 최종 출력은 **파레토 프론티어(비용 대 성능) 위의 하네스 후보 집합**이다. 예: 텍스트 분류 초기 하네스 = Zero-shot / Few-shot / ACE / MCE 하네스, 루프가 새 하네스를 만들고 자격을 갖춘 것만 남긴다(p.25). ADAS 대비 Meta-Harness의 차별점: 전체 실행 이력에 선택적 접근, 에이전틱 진단(어떤 과거 경험을 볼지 코딩 에이전트가 결정), 최소한의 외부 루프(부모 선택 규칙을 강제하지 않음)(p.28).
- **(b) 중학생:** ACE가 "오답노트를 잘 쓰는 법"을 사람이 정해줬다면, MCE는 "오답노트 쓰는 법 자체"를 AI가 실험하며 바꾸게 한다. Meta-Harness는 거기서 더 나아가 "공부 도구를 만드는 공장"을 AI가 짓는 것이고, 비용 대비 성적이 가장 좋은 도구들만 남긴다.
- **(c) 키워드:** mechanism vs artifact content, Meta-Agent / Base-Agent, Agentic Crossover, Skill Generation, Pareto frontier, Full Execution History / Agentic Diagnosis / Minimal Outer Loop
- **(d) 페이지:** p.23~25, 28

### 6. 워크플로우 디자인: AI Scientist, ScientistOne, Autodata agent, ADAS, AFlow
- **(a) 전공:** 수작업 워크플로우로는 **AI Scientist**(Lu et al. 2026; 아이디어 제안→코드→실험→분석→원고→피어리뷰 파이프라인)와 **ScientistOne**(Meng et al. 2026; 모든 주장(인용·수치·방법·결론)이 근거 출처에 추적되고 Chain-of-Evidence 검사로 감사되는 "검증가능성 중심" 설계)이 있다(p.26). **Autodata agent**(Kulikov et al. 2026)는 데이터 과학자 역할로, 메인 에이전트가 **Challenger**(문제 제안), **Weak Solver**(충분히 어려운지 검사), **Strong Solver**(여전히 풀리는지 검사), **Verifier/Judge**(품질 평가)를 관리해 "강한 solver는 풀지만 약한 solver는 못 푸는" 딱 맞는 난이도의 학습·평가 데이터를 합성한다(p.27). 설계 공간이 거대하므로 워크플로우 설계를 **탐색 문제**로 본다: **ADAS**(Automated Design of Agentic Systems; Hu et al. 2025)는 메타 에이전트가 새 에이전틱 워크플로우를 제안하는 "meta-agent search"(p.28). **AFlow**(Zhang et al. 2025)는 워크플로우를 **그래프**(노드 = LLM 호출 액션, 엣지 = 코드로 구현된 논리 연산)로 표현하고 **MCTS**로 최적화한다: ① 템플릿으로 W0 초기화 → ② 점수와 균등 탐색의 soft mixture로 노드 선택 → ③ LLM에게 평가 성능에 조건화된 수정 워크플로우 생성 요청 → ④ 실행·평가 → ⑤ N라운드 예산 내 개선 시 트리에 추가 → ⑥ top-k 평균 점수가 정체되거나 예산 소진 시 종료(p.29).
- **(b) 중학생:** 큰 문제를 작은 문제로 쪼개 각각 풀고 합치는 "일하는 순서도"를 만드는 건데, 사람이 그리는 대신 AI가 여러 순서도를 그려보고(ADAS), 바둑 AI처럼 나무 모양으로 가지를 뻗어가며 제일 좋은 순서도를 찾는다(AFlow). Autodata는 "너무 쉽지도 어렵지도 않은 문제집"을 자동으로 만드는 출제 위원회다.
- **(c) 키워드:** Chain-of-Evidence, Challenger / Weak Solver / Strong Solver / Judge, meta-agent search, graph + MCTS, soft mixture of score and uniform exploration, top-k plateau
- **(d) 페이지:** p.26~29

### 7. 자기개선 하네스: STOP → Lin et al. → Self-Harness → AHE
- **(a) 전공:** **STOP**(Self-Taught Optimizer; Zelikman et al. 2023)은 초기 재귀적 스캐폴딩 개선 사례: 원래 Improver(코드를 한 번 수정·평가) → 개선된 Improver(여러 후보 생성·평가·최선 선택) → 그 Improver를 자기 코드에 적용. **경고 결과:** GPT-4에서는 반복마다 평균 성능이 올랐지만 GPT-3.5·Mixtral 같은 약한 모델에서는 오히려 하락 → "재귀 구조만으로는 부족하고 베이스 모델이 메커니즘을 개선할 만큼 유능해야 한다. 하네스 개선은 배포를 좋게 하지만 지능이 여전히 핵심"(p.31~33). **Lin et al. (2026)** 은 ① harness-updating(유용한 하네스 편집 생산 능력)은 Qwen2-32B~Opus 4.6까지 대체로 평평하고, ② harness-benefit(갱신된 하네스를 활용하는 능력)은 비단조적이며 **중간 티어 모델이 가장 이득**을 본다고 보고(p.34). **Self-Harness**(Zhang et al. 2026)는 같은 베이스 모델이 자기 실패를 분석해 propose-evaluate-accept 루프로 하네스를 고친다: Weakness mining(검증기 기반 실패 패턴 클러스터링) → Harness proposal(bounded edit 제안) → Proposal validation(검증·머지). MiniMax M2.5, Qwen3.5-35B-A3B, GLM-5 on Terminal-Bench-2에서 모델별 약점을 겨냥한 하네스 지시를 학습해 held-out pass rate 개선. 교수 우려: 프로그램이 OS를 편집할 수 있으면 추상화 경계가 깨짐 → 편집 가능 표면을 설계하고 권한 제어·보안 계층은 루프 **바깥**에 두어야 하며 보상 해킹 문제는 남는다(p.35~36). **AHE**(Agentic Harness Engineering; Lin et al. 2026)는 병목을 **관측가능성(observability)** 으로 보고 3기둥을 둔다: ① Component observability(편집 가능한 모든 하네스 컴포넌트가 파일시스템에 표현 → 액션 공간 명시·추적), ② Experience observability(대량 궤적을 증거·실패 패턴 계층으로 요약), ③ Decision observability(모든 편집에 다음 라운드 예측을 짝지어 검증). Terminal-Bench-2에서 Hard 티어 제외 인간 설계 하네스(OpenCode, Terminus-2, Codex)보다 우수했고, 진화를 멈춘 동일 하네스가 SWE-bench-verified로 전이 → 벤치마크 특화가 아니라 엔지니어링 경험이 컴포넌트에 인코딩됨(p.37~38).
- **(b) 중학생:** "공부법을 스스로 고치는 학생"인데, 똑똑한 학생은 고칠수록 성적이 오르고 아직 기초가 약한 학생은 오히려 망친다(STOP). Self-Harness는 "내가 자주 틀리는 유형"을 모아 공부법을 조금씩 고치고 효과가 있는 것만 채택한다. AHE는 "뭘 바꿨는지, 왜 틀렸는지, 바꾼 게 정말 효과 있었는지"를 전부 기록해 두는 것이 핵심이다.
- **(c) 키워드:** STOP, harness-updating vs harness-benefit, Weakness mining / Harness proposal / Proposal validation, 3 observability pillars, Terminal-Bench-2, SWE-bench-verified
- **(d) 페이지:** p.31~38

### 8. 진화 탐색(Evolutionary Search) 계열: GEPA, AlphaEvolve, ThetaEvolve, DemoEvolve, ShinkaEvolve, DGM, Hyperagents
- **(a) 전공:** 진화 탐색은 해 집단을 변이시키고 적합도 높은 것만 남긴다. (1) 탐색 공간이 넓거나 기형이고 (2) 그래디언트로 직접 최적화는 어렵지만 평가는 쉬울 때 적합 → 하네스 탐색이 딱 맞음(p.39). 프롬프트 영역: **Promptbreeder**(Fernando et al. 2023; 변이 프롬프트 자체도 진화), **GEPA**(Agrawal et al. 2025; 반성 기반 프롬프팅 + 진화 탐색, 시행착오 궤적에 대한 자연어 반성으로 프롬프트 갱신 제안)(p.39). **AlphaEvolve**(Novikov et al. 2025): 후보 프로그램 풀을 유지하고 고정 LLM에게 diff 생성을 시킴. MAP-Elites(특성 공간 각 영역의 고성능 프로그램 유지) + Island 진화(다양한 경로 유지), 코드 영역은 `# EVOLVE-BLOCK-START/END`로 명시, 메타프롬프트도 공진화. 파라미터는 갱신 안 함(p.40, 42). **ThetaEvolve**(Wang et al. 2025): 진화 탐색 + In-Context Learning + **GRPO로 LLM 파라미터 갱신**(실행 성능을 보상으로) = 경험으로부터 학습(p.42). **DemoEvolve**(Che et al. 2026): 롤아웃 아카이브에 **인간 전문가 시연**을 추가해 실패 진단의 참조 경험으로 사용 = 경험의 질 개선(p.43). **ShinkaEvolve**(Lange et al. 2025): ① Adaptive Parent Sampling(고성능·미탐색 부모 가중 샘플링), ② Novelty Rejection Sampling(코드 임베딩 유사도+LLM 판단으로 중복 변이 제거), ③ Bandit-Based LLM Selection(UCB로 기여도 높은 변이 LLM 선호), Meta-Scratchpad = 샘플 효율 개선(p.44). **DGM**(Darwin Gödel Machine; Zhang et al. 2025): 코딩 에이전트가 **자기 코드**를 수정(Self-Modification) → 더 나은 코딩 에이전트가 되도록 자기 파이썬 코드베이스 개선 → 평가·아카이브. 한계: 고정된 자기개선 절차·코딩 스킬 의존으로 타 도메인 일반화 제한. **Hyperagents (DGM-H)**(Zhang et al. 2026): Task Agent와 Meta Agent를 분리, Meta Agent가 Task Agent와 **자기 자신의 개선 절차**까지 수정(Metacognitive Self-Modification). 구분: Meta-Harness = 에이전트 개선, Hyperagents = 에이전트 + 개선 방법까지 개선(p.41, 45~46). DGM은 열린 탐색, Self-Harness는 실패 기반 검증된 수정에 집중(p.45).
- **(b) 중학생:** 생물 진화처럼 "여러 버전을 만들고 → 시험 보고 → 잘한 것만 남기고 → 또 변형"을 반복한다. AlphaEvolve는 "프로그램"을 진화시키고, DGM은 "프로그램을 만드는 로봇"을 진화시키고, Hyperagents는 "로봇을 고치는 방법"까지 진화시킨다. ShinkaEvolve는 같은 시도를 두 번 안 하게 해서 시험 횟수를 아낀다.
- **(c) 키워드:** MAP-Elites, Islands, EVOLVE-BLOCK, GRPO(ThetaEvolve), human demonstrations, UCB bandit, Metacognitive Self-Modification
- **(d) 페이지:** p.39~46

### 9. 가중치 공동 최적화: SIA, Continual Harness
- **(a) 전공:** 하네스 진화는 비파라메트릭 시스템만 바꾸므로, 완전한 자기개선을 위해선 가중치 갱신(학습 파이프라인 개선 또는 테스트 타임 지속 학습)도 동시에 허용할 수 있다. **SIA**(Hebbar et al. 2026): Meta-Agent(초기 하네스 제안) + Task-Specific Agent(과제 실행) + **Feedback-Agent(최근 궤적을 보고 하네스를 갱신할지 가중치를 갱신할지 선택)**(p.47~48). **Continual Harness**(arXiv 2026): 환경 리셋 없이 실행 중 하네스와 가중치를 계속 개선. 구성: PRM 기반 평가(행동 정확도·추론 품질·과제 진행도로 실패 지점 식별) → Teacher Correction(**Gemini 3.1 Pro**가 저점수 스텝의 개선 행동 생성) → SFT(교정 궤적으로 학생 가중치 갱신) → Harness Refinement(Refiner가 프롬프트·스킬·서브에이전트·메모리 갱신). Model–Harness Co-Learning 루프: 현재 모델로 256스텝 실행 → PRM으로 누적 궤적 평가 → 저점수 윈도우 식별·교정 행동 생성 → Soft SFT로 가중치 갱신(p.49~50).
- **(b) 중학생:** 지금까지는 "공부법(하네스)"만 고쳤는데, 이제는 "머리(가중치)"도 같이 고친다. SIA는 매번 "이번엔 공부법을 바꿀까, 머리를 훈련할까"를 코치가 고르고, Continual Harness는 선생님(Gemini)이 틀린 단계만 고쳐준 답안으로 다시 공부하면서 동시에 공부법도 손본다.
- **(c) 키워드:** Feedback-Agent, PRM(Process Reward Model), Teacher Correction(Gemini 3.1 Pro), Soft SFT, 256 steps
- **(d) 페이지:** p.47~50

### 10. 미래 과제: 자동 연구의 6가지 실패 모드와 RSI 7대 병목
- **(a) 전공:** 논문 생산 ≠ 과학적 발견. Trehan & Chopra (2026)가 관찰한 6가지 실패: ① 학습 데이터 기본값 편향(옛 라이브러리·stale 명령), ② 실행 압박 하 구현 표류(어려워지면 흔한 단순 해법으로 이탈), ③ 메모리·컨텍스트 저하(로그를 영속 산출물로 안 쓰면 세부 유실), ④ **과도한 낙관**(노이즈에도 성공 선언; Bubeck et al. 2025의 **p-hacking**(100번 중 1번 성공만 보고) · **eureka-ing**(버그로 100% 나왔는데 돌파구라 착각) · **numerical duct tape**(수치 불안정을 정당화 없는 근사로 덮기)), ⑤ 도메인 암묵지 부족, ⑥ 약한 과학적 취향(p.51). RSI 병목 7가지: ① 약하고 모호한 평가자(빠르고 정밀한 verifier 부재), ② 컨텍스트·메모리 생명주기(교수는 컨텍스트 엔지니어링이 결국 지능의 핵심 일부가 되어야 한다고 봄), ③ 부정적 결과(문헌이 성공 편향 → LLM이 가설 포기·실패 인정에 약함 → 실패를 보존하기 쉬운 하네스 필요), ④ 다양성 붕괴(진화·RL 루프가 알려진 고보상 패턴만 착취), ⑤ **보상 해킹**(유닛테스트→테스트 과적합, judge→judge 전용 꼼수, 벤치마크→아티팩트 착취; 평가자와 권한 제어는 루프 밖에, held-out 테스트·트레이스 감사·인간 리뷰), ⑥ 장기 성공(코딩 에이전트의 목표가 단기적; 유지보수성·소유권 경계·마이그레이션 비용·하위 호환은 RLVR 샌드박스가 못 잡음), ⑦ 인간의 역할(제거가 아니라 스택 위로 이동, 적절한 추상화 수준·시점에 감독)(p.52~53).
- **(b) 중학생:** AI가 스스로 공부하다 생기는 흔한 실수들: 시험 100번 봐서 제일 잘 본 1번만 자랑하기(p-hacking), 채점기 버그로 100점 나온 걸 진짜 실력이라 믿기(eureka-ing), 점수만 올리려고 채점기의 허점을 파고들기(보상 해킹). 그래서 채점자는 학생 손이 닿지 않는 곳에 둬야 하고, 어른이 중요한 순간엔 꼭 확인해야 한다.
- **(c) 키워드:** p-hacking / eureka-ing / numerical duct tape, diversity collapse, reward hacking, "evaluator and permission control outside the loop", "humans move up the stack"
- **(d) 페이지:** p.51~53

### 11. 하네스 진화 성능 분해 — HDA (Harness-Delta Attribution)와 O / T / G
- **(a) 전공:** 하네스 진화 = 고정 모델 주변의 비파라메트릭 시스템을 과제 피드백으로 반복 갱신하는 **텍스트 공간 최적화**. 매 반복에서 executor 모델이 현재 하네스로 과제 시도 → proposer 에이전트가 궤적·평가를 보고 편집 제안(p.56). 총점 상승은 메커니즘을 숨기므로 관측된 이득 Δ를 세 메커니즘으로 분해한다(p.57):
  - **Overfitting (O)**: 최적화 설정 특유의 패턴에 의존해 적절한 분포 이동 하에서 사라지는 이득. 데이터셋 아티팩트 착취(예: 항상 정답인 선택지를 string-match), proposer 모델의 과제 지식 증류, executor LLM을 아예 안 부르는 결정적 코드 작성 등. 가장 우려스럽고 가장 조심해서 해석해야 함.
  - **Test-Time Scaling (T)**: 재시도·검증·병렬 샘플링 등으로 추론 계산을 더 써서 얻는 이득. 베이스라인에 같은 계산 예산을 주면 따라잡힐 수 있음. held-out엔 전이될 수 있으나 비용 민감도에 따라 가치가 다름.
  - **Generalizable Improvement (G)**: O와 T를 제하고 남는 이득. 재사용 가능한 스킬, 더 나은 과제 분해, 흔한 executor 오류 교정 등. 추가 계산 없이 새 과제에 작동할 가능성이 높아 가장 바람직.
  - **측정 장치(p.58):** **B** = Base Harness(예: Claude Haiku 4.5), **E** = Evolved Harness(같은 모델, 호출 방식만 다름; 예시에서 20회 호출 궤적 반환), **B_cc** = B를 E와 **같은 모델 호출 횟수**로 실행(call-matched), **E_neutral** = E에서 의심되는 오버피팅 특성(예: 하드코딩 규칙)을 제거·중화한 사본. 따라서 Δ = E − B, O ≈ E − E_neutral, T ≈ B_cc − B, G = Δ − O − T(잔여). 추정된 O 기여는 일부가 암묵적·얽혀 있을 수 있어 **필연적으로 하한(lower bound)**(p.61).
  - **결과(p.63~65):** 다수 설정에서 이득의 큰 몫이 O 또는 T. **ALFWorld**: 5개 모델 모두 학습 성공률 100%에 도달했지만 HDA는 집계 이득의 **98%를 오버피팅**으로 귀속 — 진화가 사실상 executor를 대체. **LiveMath**(연구 수준 수학 동적 객관식): "a stronger result can be proven" 선택지가 학습 문항 35개 중 21개에 등장하고 항상 정답 → 데이터셋 지름길 착취. **CREATE**(연상 창의성, 다중 정답): 주로 추론 계산 추가 → call-matched 베이스라인이 Claude Haiku 4.5 이득의 49% 회복, Qwen3.6-35B-A3B에서는 진화 하네스를 **능가**. **SWE-bench Verified**(실제 GitHub 이슈): 가장 충실한 이득이지만 주로 **약한 executor**(headroom 큼)에서. 학습 이득은 held-out 테스트에서 대체로 훨씬 작고, 16개 설정 중 4개에선 베이스라인보다 **나쁨**. 검증 기반 선택은 오버피팅을 줄이지만 제한적 보호.
  - **시사점(p.66):** 오버피팅을 측정하고 held-out 성능을 보고하라 / 테스트타임 스케일링을 비용으로 환산하라(진화 전 비용 제약 명시) / 벤치마크를 신중히 골라라(proposer가 벤치마크를 이미 알면 held-out에서도 O 기반 이득이 나올 수 있음) / 일반화 개선을 선별하는 저-아티팩트·분포이동 있는 벤치마크가 필요.
- **(b) 중학생:** 새 공부법으로 성적이 60→90점이 됐다고 치자. 그 30점이 어디서 왔는지 셋으로 쪼갠다. "답지에 3번이 많다는 걸 외운 것"(O, 다른 시험에선 소용없음), "시험을 다섯 번 보고 제일 잘 본 걸 낸 것"(T, 시간을 더 쓴 것뿐), "진짜 개념을 이해한 것"(G). 꼼수 규칙을 지우고 시험 횟수를 똑같이 맞춰 보면 진짜 실력(G)만 남는다. 연구 결과, 어떤 과목에선 30점 중 29점이 "답지 외우기"였다.
- **(c) 키워드:** Δ = E − B, O = E − E_neutral (하한), T = B_cc − B, G = 잔여; ALFWorld 98%, LiveMath 21/35, CREATE 49%, SWE-bench Verified, 4/16 설정 역전
- **(d) 페이지:** p.54~66

### 12. 에이전트 평가(evals) 기초 — Anthropic "Demystifying evals for AI agents"
- **(a) 전공:** 용어(p.70): **task**(입력+성공 기준이 정의된 단일 테스트), **trial**(한 번의 시도; 출력이 변동하므로 다중 trial), **grader**(성능 일부를 채점하는 로직; task당 여러 grader, grader당 여러 assertion), **transcript**(= trace/trajectory; 출력·툴 호출·추론·중간 결과 전체 기록; Anthropic API에선 messages 배열), **outcome**(trial 종료 시 환경의 최종 상태 — "예약했습니다"라는 말이 아니라 DB에 예약이 존재하는지), **evaluation harness**(eval을 end-to-end로 돌리는 인프라), **agent harness(= scaffold)**(모델이 에이전트로 작동하게 하는 시스템; "에이전트를 평가한다" = 하네스+모델을 함께 평가. **Claude Code가 유연한 에이전트 하네스이며 Agent SDK로 그 원시 요소를 써서 장기 실행 하네스를 만들었다**), **evaluation suite**(특정 능력을 재는 task 모음) vs **benchmark**(여러 모델/에이전트를 공통 기준으로 비교하는 표준화 프레임워크). 정적 eval의 한계 사례(p.69): **Opus 4.5가 τ²-bench 항공권 문제**에서 "Basic Economy는 변경 불가 / Economy 업그레이드는 가능 / Economy는 변경 가능" 정책의 허점을 찾아 업그레이드 후 날짜 변경 → 벤치마크는 거절을 기대해 **실패 처리**했지만 실제로는 사용자에게 더 나은 유효한 해법. Grader 3종(p.75): code-based, model-based, human; 점수는 weighted / binary / hybrid. **Capability eval**(낮은 pass rate로 시작, 오를 언덕) vs **Regression eval**(~100% 유지, 퇴행 방지)(p.79). 에이전트 유형별(p.80~84): 코딩(결정적 grader 자연스러움; SWE-bench Verified, Terminal-Bench; 통과 후 transcript도 채점), 대화형(두 번째 LLM이 사용자 시뮬레이션; 다차원 — 상태 체크·턴 수 제약·톤 rubric; τ-Bench 2024 툴 사용·정책 준수 → τ²-Bench 2025 조정·소통 → τ³-Bench 2026 지식 검색·음성), 리서치(groundedness/coverage/source quality 체크 조합, BrowseComp, rubric을 전문가와 자주 캘리브레이션), 컴퓨터 사용(WebArena URL/페이지 상태+백엔드 상태 검증, OSWorld 파일·설정·DB·UI 검사; DOM 기반은 빠르지만 토큰 多, 스크린샷은 느리지만 토큰 효율). 0→1 로드맵 8단계(p.86~88): 0 실제 실패에서 20~50개 과제로 일찍 시작 → 1 이미 수동 테스트하는 것부터(사용자 영향 순) → 2 전문가 둘이 독립적으로 같은 pass/fail을 내릴 명확한 과제 + 참조 해답(프론티어 모델에서 **pass@100 = 0%면 대개 과제가 망가진 신호**) → 3 균형 잡힌 문제 집합(해야 할 때/하지 말아야 할 때 모두) → 4 안정적 환경의 견고한 하네스(공유 상태 잔여물로 인한 상관 실패 방지) → 5 grader 신중 설계(결정적 우선, LLM 필요시, 인간은 검증용; 부분 점수; 우회 불가) → 6 **transcript를 읽어라**(실패가 공정해 보여야) → 7 포화 모니터링(100%면 개선 신호 없음; SWE-bench Verified 30%→80%+) → 8 열린 기여·유지(PM/CS도 Claude Code로 eval task를 PR로 기여). Anthropic은 **Petri**(Auditor Agent가 타깃 모델을 여러 시나리오로 테스트해 위험 행동·숨은 취약점 식별) 공개(p.87). 자동 eval은 전체 그림의 일부 — 프로덕션 모니터링, 사용자 피드백, A/B, 수동 transcript 리뷰, 체계적 인간 평가와 함께(p.90). 프레임워크: Harbor(컨테이너 환경 대규모 trial), LangSmith, Arize Phoenix/AX(p.92).
- **(b) 중학생:** AI 비서가 잘하는지 재는 "시험지 만들기". 시험지는 문제(task), 여러 번 풀기(trial), 채점 기준(grader), 풀이 과정 기록(transcript), 실제 결과(outcome; "예약했어요"라고 말한 게 아니라 진짜 예약됐는지)로 이루어진다. 재밌는 사례: Claude가 항공권 규정의 빈틈을 찾아 더 좋은 답을 냈는데 시험지는 "틀림"이라 했다 → 시험지도 틀릴 수 있으니 풀이 기록을 꼭 읽어봐야 한다.
- **(c) 키워드:** task / trial / grader / transcript / outcome / eval harness / agent harness / suite vs benchmark; τ·τ²·τ³-Bench; BrowseComp; WebArena/OSWorld; pass@100=0% → broken task; Petri; Harbor
- **(d) 페이지:** p.67~92

---

## 요약본 정정

| 요약본 | 정정 | 근거 |
|---|---|---|
| "DSA (DeepSpeed Sparse Attention)" (다른 주차) | 8주차 범위 아님. 참고로 2주차 PDF는 **DeepSeek** Sparse Attention. | week2_fm.txt |
| "`groom.me`, `grill with bug`" 같은 명령/스킬 이름을 장기 메모리 패턴 예시로 기재 | **PDF 텍스트에 해당 표기 없음.** 슬라이드 p.16~18의 패턴은 "File System as Persistent Memory"와 코딩 에이전트 하네스(Claude Code/Codex/OpenCode/Cursor) 사례. 구두 설명 또는 데모(예: Claude Code 스킬·슬래시 커맨드 `/grill-me` 등)였을 가능성 → **교수 구두 언급 여부 확인 필요**, 사이트에는 "Claude Code 스킬/커맨드 예시"로만 표기 권장. | p.16~18 |
| "ACE: Qwen의 결과물을 상위 모델(GPT)이 평가하여 ... 델타 형태로만 플레이북 메모리에 업데이트(Git 방식)" | ACE의 구조는 **Generator → Reflector → Curator** 세 역할이며 "델타 업데이트"로 Context Collapse·Brevity Bias를 해결. Qwen/GPT 역할 분담은 PDF 텍스트에 없음(그림에 있을 수 있음 — 확인 필요). "Git 방식"은 비유로만 사용. | p.21~22 |
| "MCE: 컨텍스트 내용(C) 최적화와 정보 검색 방식(BM25, 임베딩, 하이브리드) 최적화를 교차 반복" | MCE = **Meta Context Engineering (via Agentic Skill Evolution; Ye et al. 2026)**. 핵심은 **메커니즘(스킬)과 산출물(컨텍스트) 분리**, Meta-Agent가 스킬 진화, Base-Agent가 컨텍스트 구성. "검색·필터링 같은 동적 연산자"가 스킬에 포함될 수 있다는 언급은 있으나 BM25/임베딩/하이브리드 구체 언급은 PDF 텍스트에 없음(그림 가능성). | p.23~24, p.7 |
| "AutoDataAgent: 제미나이(문제 출제), GPT(검증), Qwen(학습 대상)" | **Autodata agent (Kulikov et al. 2026)**: Main Agent + Challenger(문제 제안) + Weak Solver + Strong Solver + Verifier/Judge. 특정 모델명(Gemini/GPT/Qwen)은 PDF 텍스트에 없음 — 그림 또는 구두 설명 가능성, 확인 필요. 핵심은 "Weak는 못 풀고 Strong은 푸는 난이도". | p.27 |
| "ADAS, AFlow - 몬테카를로 트리 서치 기반 최적 경로 탐색" | **MCTS는 AFlow**(Zhang et al. 2025)의 방법. **ADAS**(Hu et al. 2025)는 "meta-agent search"(메타 에이전트가 워크플로우 설계 제안). 둘을 묶어 MCTS라 하면 부정확. | p.28~29 |
| "메타 하네스: 태스크 명세를 텍스트로 입력받아 코딩 에이전트가 하네스 코드 자체를 자동 생성. ... 파레토 최적 하네스 선별" | 대체로 정확. 보완: Meta-Harness(**Lee et al. 2026**)는 "하네스를 최적화하는 하네스"이며, 최적화 대상은 "무엇을 저장·검색·제시할지 결정·최적화하는 **코드**". ADAS 대비 3가지 차이(전체 실행 이력, 에이전틱 진단, 최소 외부 루프). | p.25, 28 |
| "성능 향상분(Δ=E−B)을 ... O 측정: 하드코딩 규칙(예: '객관식 정답은 3번') 제거한 E_neutral과의 차이" | 식은 맞음. 예시 정정: 슬라이드의 실제 사례는 LiveMath에서 **"a stronger result can be proven" 선택지가 35문항 중 21문항에 등장하며 항상 정답**인 데이터셋 지름길. "정답은 3번"은 구두 비유일 수 있음. 또한 O 추정치는 **하한(lower bound)** 이라는 단서가 있음. | p.58, 61, 63 |
| "Embodied Agent 벤치마크(ALFWorld 등)에서 성능 향상의 약 90%가 ... 오버피팅" | **ALFWorld에서 집계 이득의 98%**가 오버피팅으로 귀속(5개 모델 모두 학습 성공률 100%). 벤치마크별로 다름: LiveMath도 O 지배, **CREATE는 T 지배**(call-matched 베이스라인이 Haiku 4.5 이득의 49% 회복, Qwen3.6-35B-A3B는 역전), **SWE-bench Verified는 G가 가장 뚜렷**(약한 executor 위주). | p.63~64 |
| "ARC-AGI-3, ALFWorld 등에서 관찰된 겉보기 성능 급등(예: 60% → 90% 이상)" | **ARC-AGI-3와 "60%→90%" 수치는 PDF 텍스트에 없음.** 구두 설명 가능성 → 출처 확인 전 사이트 게재 비권장. | 전체 |
| "기존 벤치마크(TAU-bench 계열 등) 다수에 정답 오류 및 모호성 존재", "라벨 오류 약 30% 수준의 결함 가능성" | PDF에는 **Opus 4.5의 τ²-bench 항공권 허점 사례**(유효 해법을 벤치마크가 실패 처리)와 "pass@100=0%면 과제가 깨진 신호", "transcript를 읽어라"가 있음. **"30% 라벨 오류" 수치는 PDF 텍스트에 없음** — 구두 언급 또는 외부 자료 가능성, 확인 필요. | p.69, 86, 88 |
| "GEPA 등 프롬프트 최적화 단계에서도 오버피팅을 방지할 객관적 벤치마크 부재" | GEPA(Agrawal et al. 2025)는 p.39에서 "반성 기반 프롬프팅 + 진화 탐색"으로 소개됨. 벤치마크 부재 논지는 p.66("일반화 개선을 선별하는 벤치마크 필요")과 일치. 수업 문장 자체는 교수 해석으로 보임. | p.39, 66 |
| 요약본에 누락된 핵심 내용 | (1) STOP의 경고 결과(약한 모델은 재귀 개선 시 성능 하락), (2) Lin et al. harness-updating vs harness-benefit(중간 티어가 최대 이득), (3) Self-Harness 3단계 + 보안 우려, (4) AHE 관측가능성 3기둥, (5) 진화 탐색 계보(AlphaEvolve/ThetaEvolve/DemoEvolve/ShinkaEvolve/DGM/Hyperagents), (6) SIA/Continual Harness, (7) 자동 연구 6가지 실패 모드(p-hacking/eureka-ing/numerical duct tape), (8) RSI 병목 7가지, (9) **Anthropic eval 블로그 전체(p.67~92)** — 용어, grader 3종, capability vs regression, 로드맵 8단계. 시험 범위일 가능성이 높으므로 사이트에 반드시 포함. | p.31~53, 67~92 |

---

## 추천 인터랙션

### 대표: "하네스 진화 성능 분해 시뮬레이터 (HDA Lab)" — 난이도 중
- **목적:** Δ = O + T + G 를 몸으로 이해. "점수가 올랐다"가 "똑똑해졌다"가 아님을 체험.
- **입력(컨트롤):**
  - 프리셋 벤치마크 선택 드롭다운: ALFWorld(O 지배, 98%), LiveMath(O 지배, 지름길 21/35), CREATE(T 지배, 49% 회복), SWE-bench Verified(G 뚜렷). 숫자는 슬라이드 기반 근사값으로 하고 "예시 수치"라고 표기.
  - 슬라이더: 베이스 점수 B(0~100), 진화 하네스 점수 E(B~100), E의 모델 호출 횟수(1~20, B는 1 고정).
  - 토글 ①「하드코딩 규칙 제거 (E → E_neutral)」: 켜면 E_neutral 막대가 나타나고 O = E − E_neutral 구간이 빨간색으로 분리.
  - 토글 ②「호출 횟수 맞추기 (B → B_cc)」: 켜면 B_cc 막대가 나타나고 T = B_cc − B 구간이 노란색으로 분리.
  - 체크박스「held-out 테스트로 보기」: 학습 분할 → held-out 전환 시 O 구간이 사라져 막대가 내려가는 애니메이션(16개 중 4개는 베이스 아래로 떨어지는 경우 재현).
- **출력(시각화):** 가로 누적 막대 1개(B 회색 | T 노랑 | G 초록 | O 빨강 = E), 옆에 수식 카드 `Δ = E − B = O + T + G`가 실시간으로 숫자 갱신. 하단에 "이 설정의 진짜 개선(G)은 Δ의 n%" 문장과, G가 0 이하면 "⚠ 진화 하네스가 베이스보다 못함" 경고.
- **중학생 모드:** 라벨을 "답지 외우기 / 시험 여러 번 보기 / 진짜 실력"으로 치환.
- **구현:** 순수 JS + inline SVG. 상태 5개(B, E, calls, neutralOn, ccOn). 1일.

### 대안 1: "ACE 플레이북 델타 업데이트 vs 전체 재작성" — 난이도 하
- 왼쪽: 10줄짜리 플레이북(bullet, id 포함). 「에피소드 실행」버튼마다 Reflector가 통찰 1~2개 생성(사전 정의 시나리오 5개). 모드 토글: **전체 재작성 모드**는 매 라운드 플레이북을 요약 재생성해 라운드마다 줄 수가 줄고 오래된 항목이 회색으로 사라짐(Context Collapse·Brevity Bias 시각화). **델타 모드**는 새 줄만 초록으로 추가/수정 줄만 노랑으로 표시(Git diff 스타일). 하단에 "보존된 지식 n/총 m" 카운터.
- 구현: 배열 + diff 렌더링. 0.5일.

### 대안 2: "AFlow 미니 MCTS 워크플로우 탐색" — 난이도 상
- 노드 = 워크플로우(예: 단일 호출 / 생성→검증 / 3회 샘플→다수결 / 분해→병합), 엣지 = 변이. 「확장」버튼을 누르면 선택 규칙(점수 + 균등 탐색의 soft mixture)에 따라 노드 하이라이트 → LLM 제안(사전 정의된 변이 테이블에서 무작위) → 평가(난수 기반 점수 + 비용) → 개선 시 트리에 추가. 예산 N 슬라이더, top-k 평균 점수 그래프가 정체되면 "종료". 비용 축을 같이 그려 파레토 프론티어 점들을 표시(Meta-Harness 연결).
- 구현: SVG 트리 레이아웃 + 간단 상태머신. 1.5~2일.

---

## 다이어그램 후보 (정적 SVG)

1. **"하네스 해부도"** — 중앙에 고정된 "Model (weights frozen)" 원. 둘러싼 고리에 6개 블록: Context Engineering(컨텍스트 주입·관리), Workflow/Loop(plan→execute→observe→improve), Tools/Action(툴 풀링·실행), Memory(파일시스템 durable state), Sub-agents/Jobs(병렬·프로세스 매니저), Evaluator/Permissions(루프 바깥에 위치 — 점선으로 고리 밖에 그림). 바깥 라벨: "Deployment system = Harness + API/Serving + Infra + Monitoring + Security". 하단 화살표: `prompt → structured context → workflow → harness code → optimizer code`.
2. **"최적화 깊이 사다리: ACE → MCE → Meta-Harness → Hyperagents"** — 4단 계단. 각 단에 "무엇을 최적화하나": 플레이북 내용(ACE: Generator/Reflector/Curator 3상자) → 컨텍스트 구성 스킬(MCE: Meta-Agent/Base-Agent 2층) → 하네스 코드(Meta-Harness: 코딩 에이전트 proposer + 파레토 프론티어 점 그래프) → 개선 절차 자체(Hyperagents: Task Agent + Meta Agent가 자기 화살표). 옆에 STOP 경고 배지: "베이스 모델이 약하면 계단을 올라도 떨어진다".
3. **"HDA 분해 막대와 측정 장치"** — 세로 막대 4개: B, B_cc, E_neutral, E. 괄호 표기로 T = B_cc − B, O = E − E_neutral, G = 나머지. 오른쪽에 4개 벤치마크 미니 누적 막대(ALFWorld: O 98% / LiveMath: O 지배 / CREATE: T 49% / SWE-bench V: G). 하단 주석 "O는 하한(lower bound)".
4. (보너스) **"에이전트 eval 용어 지도"** — task → trial×N → transcript(툴 호출·추론 기록) → outcome(환경 최종 상태) → grader(code/model/human) → score(weighted/binary/hybrid). 두 하네스 상자(agent harness vs evaluation harness)를 구분. 옆에 Opus 4.5 항공권 사례 말풍선.

---

## 모델 비교 포인트

| 개념 | 수업에서 다룬 모델·방식 | Claude (공개 문서 범위) | 기타 모델 | 출처 후보 |
|---|---|---|---|---|
| 하네스 = 모델 둘레의 실행 시스템 | 코딩 에이전트 하네스(Claude Code, Codex, OpenCode, Cursor류) 루프 수렴(p.18); Terminus-2, OpenCode(p.37) | **Claude Code**가 "유연한 에이전트 하네스"이며 **Claude Agent SDK**로 그 원시 요소를 재사용해 장기 실행 하네스를 구축(수업 슬라이드 p.70, Anthropic 블로그 인용). Anthropic 공개 문서 기준 Claude Code 구성요소: 툴 루프, 권한 모드, CLAUDE.md, 서브에이전트, 스킬, 훅, MCP(세부 명칭은 공식 문서에서 확인 후 기재) | OpenAI Codex CLI, OpenCode(오픈소스), Cursor — 구조 공개 수준 상이(확인 필요) | 슬라이드 p.18, 70; Anthropic 블로그 "Demystifying evals for AI agents"; Claude Code 공식 문서 |
| 패턴 2: 파일시스템 영속 메모리 | durable state in files, 로그·diff·trace를 파일로(p.16) | Claude Code의 `CLAUDE.md`(프로젝트 메모리 파일)와 메모리 디렉토리, 세션 간 파일 기반 상태 — 공식 문서 확인 후 기재. "Effective context engineering for AI agents"(Anthropic 블로그, 2025) 공개 | Codex의 `AGENTS.md` 류 프로젝트 지시 파일(확인 필요); OpenCode 유사 파일(확인 필요) | Claude Code 문서(Memory), Anthropic 컨텍스트 엔지니어링 블로그 |
| 패턴 3: 서브에이전트·백엔드 잡, "명시적이고 검사 가능한 병렬성" | 부모 = 프로세스 매니저(launch/inspect/cancel/merge)(p.17) | Claude Code **서브에이전트**(별도 컨텍스트, 결과만 반환) 및 백그라운드 작업 기능 — 공식 문서 확인. Anthropic "Building effective agents"(2024)의 orchestrator-workers 패턴 공개 | OpenAI Agents SDK handoffs(공개), Codex 서브에이전트 여부 확인 필요 | Claude Code 문서(Sub-agents), Anthropic 블로그 |
| 컨텍스트 엔지니어링(ACE 델타 업데이트, 컨텍스트 붕괴) | ACE / MCE / Meta-Harness(p.21~25) | Anthropic 블로그 "Effective context engineering for AI agents"(2025): 컨텍스트를 유한 자원으로, compaction·구조화 노트·서브에이전트 활용 권고(세부 문구 확인). Claude Code의 컨텍스트 압축(compact) 기능 — 공식 문서 확인. **ACE/MCE 같은 자동 플레이북 진화를 Claude 제품이 내장했는지는 비공개/해당 없음** | 확인 필요 | Anthropic 블로그, Claude Code 문서 |
| 스킬 진화(MCE의 "free-form skills") | 스킬 = 학습 절차·에러분석 코드·템플릿·검증·동적 연산자(p.24) | Claude **Agent Skills**(SKILL.md 폴더 형식, 공개 사양) — 사람이 작성하는 스킬이며 자동 진화 기능은 공개 자료 범위 밖(확인 필요) | — | Anthropic Agent Skills 문서 |
| 자기개선 하네스의 보안 경계(권한 제어는 루프 밖) | Self-Harness 우려: 편집 표면 설계, 권한·보안 계층 외부화(p.36, 53) | Claude Code 권한 모드·허용 목록·훅(공식 문서 확인); Anthropic **Petri**(오픈소스 감사 도구, Auditor Agent)(p.87) | — | 슬라이드 p.36, 53, 87; Claude Code 문서(Permissions) |
| 하네스 진화 효과 측정(HDA, O/T/G) | B = Claude Haiku 4.5, executor 5종, Qwen3.6-35B-A3B(p.58, 63~64); 모델별 harness-benefit 비단조(Qwen2-32B~Opus 4.6)(p.34) | Claude Haiku 4.5는 **executor**로 쓰임. CREATE에서 call-matched 베이스라인이 Haiku 4.5 이득의 49% 회복. Claude 자체의 하네스 진화 내부 사용 여부: 비공개 | Qwen3.6-35B-A3B: CREATE에서 B_cc가 E를 능가; MiniMax M2.5·GLM-5(Self-Harness 실험) | 슬라이드 p.34, 58, 63~64 |
| 에이전트 평가: 정적 벤치마크의 한계 | Opus 4.5 τ²-bench 항공권 허점(p.69) | Anthropic이 공개 블로그에서 직접 공개한 사례. Claude Code를 통해 비개발자도 eval task를 PR로 기여(p.88) | τ-Bench(Sierra), SWE-bench Verified(OpenAI 큐레이션), Terminal-Bench, BrowseComp(OpenAI), WebArena, OSWorld | Anthropic 블로그; 각 벤치마크 논문 |
| 가중치 공동 최적화의 교사 모델 | Continual Harness: Teacher Correction = **Gemini 3.1 Pro**(p.49) | Claude가 교사로 쓰인 사례는 이 수업 범위에 없음 | Gemini 3.1 Pro(교사), 학생 모델 미기재(확인 필요) | 슬라이드 p.49 |
| 자동 연구 하네스 | AI Scientist(Lu et al. 2026), ScientistOne, Karpathy autoresearch(p.15, 26) | Anthropic 공개 자료 중 "AI research agent" 내부 하네스 세부: 비공개 | Sakana AI Scientist(공개 코드), `karpathy/autoresearch`(공개) | 슬라이드 p.15, 26 |

> 원칙: Claude 열은 Anthropic 공식 블로그/문서/시스템 카드 및 수업 슬라이드에 인용된 범위만. 내부 구현(예: Claude가 ACE 같은 플레이북 진화를 쓰는지)은 "비공개"로 명시. 팀이 사이트에 넣기 전 Claude Code 기능 명칭은 docs.anthropic.com(또는 code.claude.com/docs)에서 한 번 더 확인할 것.

---

## 시험 포인트

**핵심 8가지**
1. 하네스의 정의(모델 가중치 고정 + 생각/계획·툴 호출·컨텍스트 관리·산출물 저장·평가를 결정하는 외부 시스템)와 "배포 시스템" 구성요소.
2. 하네스 디자인 패턴 3가지: 워크플로우 자동화(루프), 파일시스템 영속 메모리, 서브에이전트/백엔드 잡(명시적·검사 가능한 병렬성).
3. 최적화 대상의 진행: prompt → structured context → workflow → harness code → optimizer code; 5가지 최적화 축.
4. ACE(Generator/Reflector/Curator, Context Collapse, Brevity Bias, Delta Update) vs MCE(메커니즘·내용 분리, 스킬 진화) vs Meta-Harness(하네스를 최적화하는 하네스, 파레토 프론티어).
5. ADAS(meta-agent search) vs AFlow(그래프 + MCTS) 구분; Autodata agent의 Challenger/Weak/Strong/Judge.
6. STOP 교훈(약한 모델은 재귀 개선에 실패), Lin et al.의 harness-updating/benefit, AHE의 관측가능성 3기둥, 보상 해킹과 "평가자는 루프 밖".
7. **HDA: Δ = E − B = O + T + G**; B_cc(호출 횟수 맞춤)로 T, E_neutral(오버피팅 중화)로 O(하한), 나머지 G; ALFWorld 98% O, CREATE T 지배, SWE-bench Verified G.
8. 에이전트 eval 용어(task/trial/grader/transcript/outcome/harness), grader 3종, capability vs regression, Opus 4.5 τ²-bench 사례, pass@100 = 0% → 과제 결함 신호, "transcript를 읽어라".

**예상 문제 5개**

**Q1. (단답)** 하네스 진화로 얻은 성능 향상 Δ = E − B 를 세 메커니즘으로 분해할 때, 각 메커니즘을 측정하기 위해 사용하는 두 가지 변형 하네스(B_cc, E_neutral)가 각각 무엇을 통제하는지 설명하고, 왜 오버피팅 추정치가 "하한"인지 쓰시오.
- **정답:** B_cc는 베이스 하네스를 진화 하네스와 **같은 모델 호출 횟수(추론 예산)** 로 실행한 것으로, B_cc − B 가 테스트타임 스케일링(T)을 측정한다. E_neutral은 진화 하네스에서 **하드코딩 규칙 등 의심되는 오버피팅 특성을 제거·중화**한 사본으로, E − E_neutral 이 오버피팅(O)을 측정한다. 일반화 개선 G = Δ − O − T. 오버피팅 중 일부는 암묵적이거나 다른 메커니즘과 얽혀 있어 탐지·제거되지 않을 수 있으므로 측정된 O는 필연적으로 하한이다.

**Q2. (서술)** ACE가 이전 메모리 시스템의 두 가지 한계(Context Collapse, Brevity Bias)를 어떻게 해결하는지 세 구성요소의 역할과 함께 설명하시오. 그리고 MCE가 ACE와 달라지는 핵심 아이디어를 한 문장으로 쓰시오.
- **정답:** Generator가 플레이북 bullet을 참조해 궤적을 생성하고, Reflector가 성공/실패 궤적에서 통찰을 증류하며, Curator가 **증분적·항목화된 델타 업데이트**로 플레이북을 갱신한다. 전체 재작성/요약을 하지 않으므로 반복 재작성에 의한 정보 유실(Context Collapse)과 LLM의 과도한 간결화(Brevity Bias)를 피한다. MCE는 "컨텍스트를 어떻게 관리할지(메커니즘 = 스킬)"와 "무엇을 담을지(내용)"를 분리해, 휴리스틱 규칙을 강제하는 대신 Meta-Agent가 스킬을 진화시키고 Base-Agent가 그 스킬로 컨텍스트를 구성하도록 공진화시킨다.

**Q3. (객관식)** 다음 중 AFlow의 워크플로우 최적화 방식으로 옳은 것은?
  ① 메타 에이전트가 새로운 에이전트 설계를 자연어로 제안하는 meta-agent search
  ② 워크플로우를 그래프(노드 = LLM 호출, 엣지 = 코드 논리)로 표현하고 MCTS로 탐색
  ③ 코딩 에이전트가 자기 자신의 코드베이스를 수정해 아카이브에 저장
  ④ 후보 프로그램 풀에 대해 MAP-Elites와 island 진화를 적용
- **정답: ②.** ①은 ADAS, ③은 DGM, ④는 AlphaEvolve.

**Q4. (서술)** STOP(Zelikman et al. 2023)의 "경고 결과"와 Lin et al.(2026)의 harness-benefit 비단조성 결과를 근거로, "하네스 개선과 모델 지능의 관계"에 대해 교수가 내린 결론을 설명하시오.
- **정답:** STOP은 GPT-4에서는 반복마다 성능이 개선됐지만 GPT-3.5·Mixtral 같은 약한 모델에서는 오히려 저하됐다 → 재귀 구조만으로는 부족하고 베이스 모델이 메커니즘을 개선할 만큼 유능해야 한다. Lin et al.은 하네스 편집 생산 능력(updating)은 모델 급에 따라 평평하지만, 갱신된 하네스를 활용하는 능력(benefit)은 비단조적으로 중간 티어 모델이 가장 이득을 본다고 보고했다. 결론: 하네스 엔지니어링은 모델의 더 나은 "배포"를 가능하게 하지만 핵심은 여전히 지능이며, 장기적으로 많은 하네스 개선이 모델 행동으로 내재화되더라도 외부 컨텍스트·툴과의 인터페이스(목표·제약·평가 명세)는 남는다.

**Q5. (서술)** Anthropic의 에이전트 평가 가이드에서 (a) transcript와 outcome의 차이, (b) capability eval과 regression eval의 차이, (c) 프론티어 모델에서 pass@100 = 0%가 의미하는 바를 각각 설명하고, Opus 4.5의 τ²-bench 사례가 왜 "transcript를 읽어라"는 교훈과 연결되는지 쓰시오.
- **정답:** (a) transcript는 trial 전체 기록(출력·툴 호출·추론·중간 결과; API에서는 messages 배열), outcome은 trial 종료 시 **환경의 최종 상태**(예: "예약했다"는 말이 아니라 DB에 예약 레코드 존재 여부). (b) capability eval은 "무엇을 잘하나"를 재며 낮은 pass rate로 시작해 오를 언덕을 주고, regression eval은 "예전에 되던 게 여전히 되나"를 재며 ~100% pass rate를 유지해 퇴행을 잡는다. (c) 프론티어 모델에서 많은 trial에 걸쳐 0% 통과는 대개 에이전트가 무능한 게 아니라 **과제 명세나 grader가 망가졌다는 신호**다. Opus 4.5는 Basic Economy→Economy 업그레이드 후 날짜 변경이라는 정책상 유효한 해법을 찾았지만 벤치마크는 거절을 기대해 실패 처리했다 → grader가 유효한 해법을 거부했는지 진짜 실수였는지는 transcript를 읽어야만 알 수 있고, 실패는 "공정해 보여야" 한다.

---

## 출처

- Turing, A. "Intelligent Machinery" (1948); "Intelligent Machinery, A Heretical Theory" (c.1951), in B. Jack Copeland (2004) — p.2
- Russell & Norvig, *AI: A Modern Approach* (2020) — p.3
- Language Agent Tutorial — https://language-agent-tutorial.github.io/ — p.3~6
- **"Harness Engineering for Self-Improvement"** (블로그/에세이; 슬라이드 p.10~53의 source. 저자 미기재 — 확인 필요) — 인용 문헌: I. J. Good (1965); Yudkowsky (2008); Karpathy `autoresearch` (https://github.com/karpathy/autoresearch); Claude Code 하네스 분석 저장소 (https://github.com/yasasbanukaofficial/claude-code, "Claude Code Leak"으로 표기); ACE (Agentic Context Engineering, 2025); MCE — Ye et al. 2026, "Meta Context Engineering via Agentic Skill Evolution"; Meta-Harness — Lee et al. 2026; AI Scientist — Lu et al. 2026; ScientistOne — Meng et al. 2026; Autodata agent — Kulikov et al. 2026; ADAS — Hu et al. 2025; AFlow — Zhang et al. 2025; STOP — Zelikman et al. 2023; Lin et al. 2026 (harness-updating/benefit); Self-Harness — Zhang et al. 2026; AHE — Lin et al. 2026; Promptbreeder — Fernando et al. 2023; GEPA — Agrawal et al. 2025; AlphaEvolve — Novikov et al. 2025; ThetaEvolve — Wang et al. 2025; DemoEvolve — Che et al. 2026; ShinkaEvolve — Lange et al. 2025; Darwin Gödel Machine — Zhang et al. 2025; Hyperagents — Zhang et al. 2026; SIA — Hebbar et al. 2026; Continual Harness (arXiv 2026); Trehan & Chopra (2026); Bubeck et al. (2025) "p-hacking and eureka-ing"
- **"What Evolves When We Talk About Harness Evolution?"** (Harness-Delta Attribution, HDA) — p.54~66 (목차 p.8에 "Rethinking the Evaluation of Harness Evolution for Agents", "Harness-Delta Attribution: Dissecting Gains From Harness Evolution"으로도 기재)
- **Anthropic, "Demystifying evals for AI agents"** (블로그) — p.67~92; 언급 벤치마크/도구: τ-Bench(2024), τ²-Bench(2025), τ³-Bench(2026), SWE-bench Verified, Terminal-Bench, BrowseComp, WebArena, OSWorld, Petri(Anthropic 감사 도구), Harbor, LangSmith, Arize Phoenix/AX; 사례: Descript, Bolt
- 목차(p.7~8)에 나열된 후속 주차 범위(이번 수업 미다룸): Reflexion, Voyager, A-MEM, GEPA(상세), AlphaEvolve(상세), TabFM-Auto, EvoX, Dream-RSI, R-Zero, RQ-Evolve, Tev, Range-GRPO, EvalResearchBench, Evo-Bench, RSIGym, HarnessOpt-Bench

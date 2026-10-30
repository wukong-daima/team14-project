# 4주차: LLM 학습 방법론 — RLHF · DPO · GRPO · OPD와 롱 호라이즌 에이전트 학습

> **PDF 커버리지 주의**: `week4_agent.pdf`는 실제로는 6주차(에이전트) 강의 슬라이드다. 4주차 요약의 선호 튜닝(RLHF/DPO/PPO/GRPO/OPD) 내용은 `week2_fm.pdf` pp.56~57, 68~90 (대부분 Stanford CME295 슬라이드 이미지라 추출 텍스트가 거의 없음)에, 롱 호라이즌/추론-학습 불일치 내용은 `week4_agent.pdf` pp.84~93 (T1, 하네스, MEA)에 있다. "Agentic Monte Carlo(블랙박스 모델 튜닝)"는 어느 PDF에서도 찾지 못했다 → 요약본(구두 설명) 기반.

한 줄 요약: 사전학습된 LLM을 "사람이 선호하는 답"과 "정답이 검증되는 추론"으로 끌어올리는 학습 레시피(SFT → 선호 튜닝 → 추론 RL → 증류)를 배우고, 수백 스텝짜리 에이전트 과제에서 보상 희소성과 추론-학습 불일치를 어떻게 푸는지 본다.

## 강의 흐름
| 순서 | 섹션 | 출처·페이지 |
|---|---|---|
| 1 | LLM 학습 단계: pt → cpt → SFT/IFT → PFT(선호) → RFT(강화) | week2_fm p.56~57 |
| 2 | (참고) PEFT: Adapter, LoRA, 통합 관점, In-context learning | week2_fm p.58~67 |
| 3 | Preference Tuning 개요 → RLHF(보상 모델, 온라인 RL) | week2_fm p.68~79 |
| 4 | DPO (오프라인 RL, 보상 모델 제거) / RLHF vs DPO | week2_fm p.80~82 |
| 5 | Reasoning을 위한 선호 튜닝 → PPO 구조·한계 | week2_fm p.83~84 |
| 6 | GRPO: 그룹 상대 어드밴티지, 클리핑, 가치 모델 제거 | week2_fm p.85~89 |
| 7 | On-Policy (Self-)Distillation | week2_fm p.90 |
| 8 | 롱 호라이즌 에이전트 RL: T1 (sparse reward, 추론-학습 불일치, TITO/R3) | week4_agent p.84~88 |
| 9 | 하네스 설계(Planner/Generator/Evaluator, Sprint Contract), LongHorizon-Harness MEA | week4_agent p.89~93 |
| 10 | 블랙박스 모델 튜닝 (Agentic Monte Carlo) | PDF 없음, 요약본 |

## 핵심 개념

### 1. LLM 학습 파이프라인 (pt → cpt → SFT → PFT → RFT)
- (a) 전공: 베이스 모델은 대규모 코퍼스로 사전학습(pt)하고 도메인 데이터로 계속 사전학습(cpt)한다. 그 위에 지시-응답 쌍으로 SFT/IFT를 하고, 사람 선호를 반영하는 Preference Fine-Tuning(RLHF/DPO), 마지막으로 검증 가능한 보상으로 Reinforcement Fine-Tuning(PPO/GRPO)을 한다. 각 단계는 반복될 수 있고, 강한 교사 모델이 있으면 증류(OPD)가 추가된다. Tulu 3, Nemotron Nano 2 등 공개 레시피가 이 순서를 따른다.
- (b) 중학생: 책을 엄청 많이 읽어 말을 배우고(사전학습) → 선생님이 문제-답 예시를 보여주고(SFT) → 두 답 중 사람들이 더 좋아하는 쪽을 배우고(선호 튜닝) → 수학 문제를 풀어 채점받으며 실력을 올린다(강화 학습).
- (c) 고유명사: pt, cpt, SFT/IFT, PFT, RFT, Tulu 3, Nemotron Nano 2
- (d) week2_fm p.56~57

### 2. RLHF (Reinforcement Learning from Human Feedback)
- (a) 전공: 사람이 매긴 응답 쌍 선호로 보상 모델(Reward Model)을 학습한 뒤, 정책 모델이 보상을 최대화하도록 PPO 등 온라인 RL로 학습한다. 레퍼런스 모델과의 KL 페널티로 분포 붕괴를 막는다. 정책·레퍼런스·보상·가치 모델까지 최대 4개 모델이 필요해 메모리와 불안정성이 크고, 보상 모델의 허점(예: 긴 답변 선호)을 정책이 파고드는 reward hacking에 취약하다.
- (b) 중학생: 심사위원 로봇(보상 모델)을 먼저 만들고, 학생 로봇이 심사위원 점수를 높이려 연습한다. 심사위원이 "길게 쓰면 점수 잘 줌" 같은 버릇이 있으면 학생이 그 버릇만 노린다(보상 해킹).
- (c) 핵심: 보상 모델, 온라인 RL, KL 규제, 4개 모델(policy/reference/reward/value), reward hacking
- (d) week2_fm p.72~79, p.84

### 3. DPO (Direct Preference Optimization)
- (a) 전공: RLHF의 보상 모델을 닫힌 형태로 정책 비율에 흡수해, 선호 응답 y_w의 로그확률은 올리고 비선호 y_l은 내리는 분류 손실 하나로 학습한다. 손실은 -log σ(β[log πθ(y_w|x)/π_ref(y_w|x) − log πθ(y_l|x)/π_ref(y_l|x)]) 형태로, β가 레퍼런스에서 얼마나 벗어나도 되는지를 조절한다. 롤아웃 없이 고정 데이터셋으로 학습하므로 오프라인 RL이며 정책+레퍼런스 2개 모델만 필요하다. 안정성과 구현 단순성 때문에 업계 표준이 됐다.
- (b) 중학생: 심사위원 로봇을 따로 만들지 않고, "이 답이 저 답보다 낫다"는 정답지를 보고 바로 공부한다. 준비물이 절반이라 빠르고 실수가 적다.
- (c) 핵심: 오프라인 RL, 선호 쌍 (y_w, y_l), β, 레퍼런스 모델, 2개 모델
- (d) week2_fm p.80~82

### 4. PPO와 가치 모델 (추론 RL의 출발점)
- (a) 전공: PPO는 확률비 r = πθ/π_old를 클리핑해 한 번의 업데이트가 과도하지 않게 하며, 가치 모델이 상태별 기대 리턴의 베이스라인을 제공하고 GAE로 어드밴티지 A를 계산한다. 정책·레퍼런스·보상·가치 4개 모델과 반복 롤아웃이 필요해 비용이 크고 하이퍼파라미터·보상 모델 오류에 민감하다.
- (b) 중학생: "지난번보다 얼마나 잘했나"를 재려면 기준점(가치 모델)이 필요하고, 한 번에 너무 크게 바꾸지 않도록 안전벨트(클리핑)를 맨다.
- (c) 핵심: 확률비 클리핑, value model, GAE, advantage
- (d) week2_fm p.84

### 5. GRPO (Group Relative Policy Optimization)
- (a) 전공: 같은 프롬프트에 대해 G개의 응답을 샘플링하고, 그룹 내 보상의 평균·표준편차로 정규화한 상대 어드밴티지 Â_i = (r_i − mean)/std를 사용해 PPO의 가치(critic) 모델을 없앤다. 확률비와 클리핑은 PPO와 같고, 수학·코딩처럼 정답 검증이 가능한 보상(RLVR)에 쓰인다. 그룹 정규화 덕분에 쉬운 문제(대부분 성공)보다 어려운 문제에서 드물게 성공한 샘플이 큰 가중치를 받는다. 한계: 그룹 전체가 성공 또는 전부 실패면 어드밴티지가 0이 되어 학습 신호가 없다.
- (b) 중학생: 같은 문제를 8번 풀어보고, 그중 평균보다 잘한 풀이는 더 자주 하도록, 못한 풀이는 덜 하도록 고친다. 8번 다 틀리면 비교할 게 없어서 아무것도 못 배운다.
- (c) 핵심: 그룹 크기 G, 그룹 정규화 어드밴티지, critic 제거, DeepSeekMath/DeepSeek-R1, "all-fail → 0 gradient"
- (d) week2_fm p.85~89; 요약본 정정 참조

### 6. OPD / OPSD (On-Policy (Self-)Distillation)
- (a) 전공: 학생 모델이 현재 정책으로 생성한 궤적의 각 prefix마다 교사(또는 더 강한 자기 버전)가 토큰 수준 감독을 제공한다. 고정된 교사 데이터로 하는 오프라인 증류의 train-inference 분포 불일치를 줄이면서, GRPO의 최종 정답 기반 희소 보상 대신 모든 토큰에 조밀한(dense) 신호를 준다. 단점은 강한 교사 모델에 의존한다는 점.
- (b) 중학생: 내가 푼 풀이를 한 줄 한 줄 선생님이 "여기선 이렇게 쓰는 게 맞아"라고 바로잡아 준다. 맨 끝 정답만 채점받는 것보다 어디서 틀렸는지 훨씬 잘 안다.
- (c) 핵심: on-policy, dense token-level supervision, teacher dependence
- (d) week2_fm p.90

### 7. 롱 호라이즌 RL의 문제 1 — 보상 희소성 (T1)
- (a) 전공: 300스텝짜리 터미널 과제에서 "전부 성공 1 / 아니면 0" 보상은 초반에 거의 항상 0이라, 거의 다 한 궤적과 아무것도 못 한 궤적이 동일 취급된다. T1은 verifier로 요구사항 몇 개를 만족했는지를 부분 보상으로 주고(dense reward), SFT/warm start로 긴 과제를 어느 정도 수행할 초기 능력을 만든다.
- (b) 중학생: 100문제 시험에서 "만점 아니면 0점"이면 아무도 늘지 않는다. 맞힌 개수만큼 점수를 주면 조금씩 나아진다.
- (c) 핵심: sparse reward, verifier, partial credit, warm start, T1
- (d) week4_agent p.85~88

### 8. 롱 호라이즌 RL의 문제 2 — 추론-학습 불일치 (TITO, R3)
- (a) 전공: 롤아웃은 SGLang 같은 고속 추론 엔진, 학습은 Megatron-Core + Transformer Engine으로 하므로 같은 모델이라도 선택되는 토큰과 MoE 전문가가 달라질 수 있다. 토큰을 텍스트로 디코딩했다가 재인코딩하면 encode(decode(ids)) ≠ ids가 생긴다(decode(encode(text)) = text는 항상 성립). T1의 TITO는 롤아웃의 토큰 ID 자체를 학습에 재사용하고, R3는 롤아웃 때의 MoE 전문가 인덱스를 저장해 학습 때 그대로 쓴다.
- (b) 중학생: 연습 때 쓴 공책을 복사기로 복사했다가 다시 베끼면 글자가 바뀔 수 있다. 원본 공책(토큰 ID)을 그대로 쓰면 안 바뀐다.
- (c) 핵심: inference-training discrepancy, SGLang vs Megatron-Core, TITO(token in token out), R3(expert index 재사용)
- (d) week4_agent p.87~88

### 9. 하네스 설계와 MEA
- (a) 전공: 모델 바깥에서 "어떻게 일을 나누고 검사하고 다시 고치게 할지"를 통제하는 시스템이 하네스다. Anthropic은 Planner → Generator → Evaluator 구조와 Sprint Contract(코딩 전 생성자-평가자가 acceptance criteria 합의, 파일로 소통)로 단일 에이전트 20분 → 풀 하네스 6시간의 완성도 높은 결과를 얻었고, 이후 Opus급 모델이 나오자 스프린트 구조를 제거했다. LongHorizon-Harness의 MEA(Manage–Execute–Audit)는 Executor의 "완료했다"를 믿지 않고 read-only Auditor가 환경을 검사해야만 task state에 completed를 기록한다.
- (b) 중학생: 혼자 숙제하면 "다 했다"고 착각하기 쉽다. 계획 짜는 사람, 하는 사람, 검사하는 사람을 나누고 검사 통과한 것만 "완료" 도장을 찍는다.
- (c) 핵심: context anxiety, Generator/Evaluator 분리, Sprint Contract, contract.md/feedback.md, MEA, compounding error, context rot
- (d) week4_agent p.89~93

### 10. 블랙박스 모델 튜닝 (Agentic Monte Carlo) — 요약본 기반
- (a) 전공: API로만 접근 가능한 모델(GPT, Claude)은 가중치를 바꿀 수 없다. 대신 생성 과정의 중간 상태를 평가하는 가치 모델을 두고, 가치가 높은 중간 상태에서 탐색을 분기해 재시도하면 처음부터 전부 다시 하는 것보다 효율적으로 성공률을 높인다. (6주차의 트리 탐색/backtracking과 같은 아이디어를 "학습 없는 튜닝"에 적용.)
- (b) 중학생: 미로에서 막히면 입구로 돌아가지 말고, "여기까진 잘 왔다"고 표시된 갈림길로 돌아가서 다른 길을 시도한다.
- (c) 핵심: value model on intermediate states, branching/backtracking, weight-free optimization. **정확한 논문명·슬라이드 확인 필요**
- (d) PDF 없음

## 요약본 정정
- "GRPO (Group-wise Reward-based Policy Optimization)" → **Group Relative Policy Optimization** (DeepSeekMath 2024 / DeepSeek-R1; week2_fm p.89 "Group-relative advantage")
- "OPD/OPG (On-Policy Distillation/Generation)" → 슬라이드 용어는 **On-Policy (Self-)Distillation, OPSD** (week2_fm p.90). "OPG"는 PDF에 없음 → 확인 필요
- "추론 엔진(vLLM, SGLang) vs 학습 프레임워크(Transformers)" → T1 기준 롤아웃 **SGLang**, 학습 **Megatron-Core + Transformer Engine** (week4_agent p.87). vLLM/Transformers는 일반론으로는 맞음
- "학습 파이프라인: Pre-training → SFT → DPO → GRPO → OPD" → 슬라이드는 **pt → cpt → SFT/IFT → PFT → RFT** (week2_fm p.57). DPO/GRPO/OPD 순서는 교수님 구두 설명으로 보이며 PDF에는 없음
- "RLHF는 최대 4개 모델" → PDF는 **PPO** 설명에서 policy/reference/reward/value 4개 (week2_fm p.84). 의미는 동일
- "토큰 ID와 MoE 전문가 인덱스를 저장" → 고유명사 **TITO**(토큰), **R3**(전문가 인덱스), 논문 **T1: Terminal Agent Reinforcement Learning for Long-Horizon Tasks** (week4_agent p.88)
- "GRPO는 롤아웃 전부 실패 시 학습 불가" → 정확히는 **전부 성공해도** 어드밴티지가 0 (그룹 내 분산 0). 양쪽 모두 명시 권장
- "Agentic Monte Carlo" → 어느 PDF에도 없음. 명칭·출처 확인 필요

## 추천 인터랙션

### 대표: GRPO 그룹 롤아웃 시뮬레이터 (난이도: 중)
- 입력: 문제 난이도 슬라이더(성공확률 p, 0.02~0.98), 그룹 크기 G(4/8/16), [롤아웃 실행] 버튼, [10번 반복] 버튼
- 출력: G개의 응답 카드가 순서대로 뒤집히며 성공(초록 1)/실패(회색 0) 표시 → 그룹 평균·표준편차 → 각 카드 위에 어드밴티지 Â_i = (r_i − μ)/σ 막대(양수 위로, 음수 아래로) → 하단에 "학습 신호 크기 Σ|Â|" 게이지
- 시각화 포인트: p=0.9(쉬움)일 때 성공 카드 어드밴티지가 작고, p=0.15(어려움)에서 드물게 성공한 카드가 매우 큰 양의 어드밴티지를 받는 것을 눈으로 확인. 전부 성공/전부 실패면 σ=0 → 게이지 0, "이 그룹에서는 배울 게 없음" 메시지
- 확장: [PPO 모드] 토글 시 critic 모델 박스가 추가로 그려지고, [GRPO 모드]에서 사라지는 비교 다이어그램

### 대안 1: DPO 선호 시소 (난이도: 하)
- 입력: 선호 응답/비선호 응답의 현재 로그확률 비율 슬라이더 2개, β 슬라이더
- 출력: 시소 그림이 기울어지며 손실값 −log σ(β·Δ)과 그래디언트 방향 화살표 표시. β가 크면 레퍼런스에서 조금만 벗어나도 손실이 급변하는 곡선

### 대안 2: TITO 토큰 왕복 데모 (난이도: 하)
- 입력: 텍스트 박스 + 가짜 서브워드 토크나이저(사전 정의 어휘). [텍스트→토큰→텍스트] vs [토큰→텍스트→토큰] 버튼
- 출력: 같은 문장이 두 경로에서 토큰 ID가 달라지는 사례(예: 공백·결합 규칙 모호한 단어)를 색으로 하이라이트. "decode(encode(text))=text 는 항상 참, encode(decode(ids))=ids 는 아님"

## 다이어그램 후보 (정적 SVG)
1. **학습 파이프라인 레일**: pt → cpt → SFT/IFT → PFT(RLHF/DPO) → RFT(PPO/GRPO) → OPD. 각 역에 "필요 모델 수"와 "데이터 종류(코퍼스/지시쌍/선호쌍/검증기)" 배지
2. **RLHF vs DPO vs GRPO 모델 구성도**: 세 열. RLHF/PPO: policy, reference, reward, value 4박스 + 롤아웃 화살표(온라인). DPO: policy, reference 2박스 + 데이터셋(오프라인). GRPO: policy, reference + verifier + 그룹 G 응답 묶음, critic 박스에 X
3. **롱 호라이즌 RL 루프와 불일치 지점**: SGLang 롤아웃 → (토큰 ID, 전문가 인덱스 저장) → Megatron 학습. 중간에 "텍스트 재인코딩" 우회로를 빨간 X로, TITO/R3 직결로를 초록으로. 옆에 sparse vs dense reward 타임라인(300스텝 중 verifier 체크포인트)

## 모델 비교 포인트
| 개념 | 수업에서 다룬 모델·방식 | Claude (공개 문서 범위) | 기타 모델 | 출처 후보 |
|---|---|---|---|---|
| 선호 튜닝 알고리즘 | RLHF(PPO) → DPO가 업계 표준 | 초기 Claude: RLHF + **Constitutional AI(RLAIF)** 공개 논문. 현재 세대의 구체 알고리즘(PPO/DPO/GRPO 여부)은 **비공개** | OpenAI InstructGPT: RLHF+PPO(2022). Llama 3: SFT→rejection sampling→DPO 반복(공개). Tulu 3: SFT→DPO→RLVR(공개) | Bai et al. "Constitutional AI" 2022; Ouyang et al. 2022; Llama 3 Herd 2024; Tulu 3 2024 |
| 추론 RL | DeepSeek-R1: cold-start SFT → GRPO(검증 보상) → rejection sampling+SFT → 전 도메인 RL | **extended thinking** 공개 기능. 추론 RL 레시피 **비공개** | DeepSeekMath/R1: GRPO 공개. Qwen3: 4단계(long-CoT cold start→reasoning RL→thinking fusion→general RL) 공개 보고서 | DeepSeek-R1 2025; Qwen3 Technical Report 2025 (확인 필요) |
| 보상 모델 / 보상 해킹 | RLHF 보상 모델의 길이 편향 등 | Constitutional AI에서 AI 피드백으로 사람 라벨 대체; 보상 해킹 관련 Anthropic 연구 공개(세부 **확인 필요**) | OpenAI "Learning to summarize from human feedback" 등 | Anthropic 블로그/논문 |
| 증류 | OPD(dense, on-policy) vs 오프라인 증류; R1→Llama/Qwen distill 모델 | Claude의 증류 여부·방식 **비공개**. 이용약관상 Claude 출력으로 경쟁 모델 학습 금지(공개 약관) | DeepSeek-R1-Distill-Qwen/Llama 공개 | DeepSeek-R1 논문 |
| 롱 호라이즌 RL | T1: dense verifier reward, TITO, R3 | Claude Code 등 장기 에이전트 제품은 공개, 학습 방식 **비공개** | OpenAI Codex, 기타 | T1 arXiv 2026 |
| 하네스 | Planner→Generator→Evaluator, Sprint Contract (Anthropic 실험) | **Anthropic 자체 공개 자료**: "Harness design for long-running application development"(26.03), "Demystifying evals for AI agents", "Building effective agents"(2024.12) | LongHorizon-Harness MEA (Claude Code·Codex를 감싸는 하네스) | week4_agent p.80~93 |
| 블랙박스 튜닝 | Agentic Monte Carlo(가치 모델로 중간 상태 분기) | Claude API는 가중치 접근 불가 → 이런 추론 시점 기법만 가능; prompt caching 등으로 분기 비용 절감 가능(공개 기능) | GPT API 동일 | 확인 필요 |

## 시험 포인트
1. 학습 단계 순서와 각 단계에 필요한 데이터/모델 (pt, cpt, SFT, PFT, RFT)
2. RLHF의 구성 요소 4개와 두 가지 약점(복잡성·불안정, reward hacking)
3. DPO가 RLHF와 다른 점: 보상 모델 제거, 오프라인, 2개 모델, β의 역할
4. PPO의 가치 모델 역할(베이스라인·GAE) vs GRPO의 그룹 정규화 어드밴티지 (critic 제거)
5. GRPO가 어려운 문제에 가중치를 더 주는 이유, 전부 성공/전부 실패 시 학습 신호 0
6. OPD가 GRPO의 희소 보상 문제를 어떻게 보완하는지(토큰 수준 dense 감독, on-policy), 교사 의존성
7. 추론-학습 불일치의 두 원인(토큰 재인코딩, MoE 전문가 선택)과 해결(TITO, R3)
8. 롱 호라이즌 보상 희소성 해결(verifier 부분 보상), 하네스에서 생성자-평가자 분리 이유(자기 평가 과신), MEA에서 Auditor의 역할

### 예상 문제
1. **Q.** DPO가 RLHF보다 안정적이라고 평가되는 이유를 필요한 모델 수와 학습 방식 관점에서 설명하라.
   **A.** RLHF는 보상 모델을 별도 학습하고 정책·레퍼런스·보상·가치 모델을 동시에 띄워 온라인 롤아웃으로 학습하므로 복잡하고 보상 모델 오류를 정책이 악용(reward hacking)할 수 있다. DPO는 보상 모델을 손실식에 흡수해 선호 쌍 데이터로 정책·레퍼런스 2개 모델만으로 오프라인 학습하므로 단순하고 안정적이다.
2. **Q.** GRPO에서 같은 프롬프트에 8개 응답을 샘플링했을 때 보상이 [1,0,0,0,0,0,0,0]인 경우와 [1,1,1,1,1,1,1,0]인 경우 각각 성공 응답의 어드밴티지는 어떻게 다른가? 전부 0이면?
   **A.** 어드밴티지는 (r−μ)/σ. 첫 경우 μ=0.125, σ≈0.33 → 성공 응답 ≈ +2.65(큰 양수), 둘째 경우 μ=0.875, σ≈0.33 → 성공 응답 ≈ +0.38(작은 양수). 어려운 문제의 드문 성공이 훨씬 강하게 강화된다. 전부 0이면 σ=0, 모든 어드밴티지 0 → 학습 신호 없음.
3. **Q.** OPD(On-Policy Distillation)가 해결하는 문제 두 가지와 그 한계 하나를 쓰라.
   **A.** (1) GRPO의 최종 정답 기반 희소 보상 → 교사의 토큰 수준 dense 감독, (2) 오프라인 증류의 train-inference 분포 불일치 → 학생이 실제 방문하는 상태에서 감독. 한계: 강한 교사 모델에 의존.
4. **Q.** 롤아웃 엔진과 학습 프레임워크가 달라서 생기는 불일치 두 가지와 T1의 해결책을 쓰라.
   **A.** (1) 토큰을 텍스트로 디코딩 후 재인코딩하면 encode(decode(ids))≠ids → TITO: 롤아웃 토큰 ID를 그대로 학습에 사용. (2) MoE 전문가 선택이 엔진마다 달라짐 → R3: 롤아웃 시 전문가 인덱스를 저장해 학습에 재사용.
5. **Q.** Anthropic 하네스 실험에서 Generator와 Evaluator를 분리한 이유와, LongHorizon-Harness MEA에서 "완료"가 기록되는 조건을 쓰라.
   **A.** 에이전트는 자기 결과를 과대평가하고 긴 컨텍스트에서 목표를 잊거나(context anxiety) 일찍 끝내려 하므로 만드는 역할과 평가 역할을 분리했다. MEA에서는 Executor가 완료했다고 말해도 인정하지 않고, read-only Auditor가 실제 환경을 검사해 확인해야만 task state에 completed가 기록된다.

## 출처
- Stanford CME295 Lecture 1 슬라이드 (week2_fm p.68~89 원출처): https://cme295.stanford.edu/slides/fall25-cme295-lecture1.pdf
- DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning (week4_agent p.39~40)
- DeepSeekMath (GRPO 원 논문) — 확인 필요
- s1: Simple test-time scaling (week4_agent p.41~42)
- T1: Terminal Agent Reinforcement Learning for Long-Horizon Tasks [arXiv 2026] (week4_agent p.85~88)
- Harness design for long-running application development [preprint 2026, Anthropic] (week4_agent p.89~90)
- LongHorizon-Harness: Advancing LongHorizon Agents for Real-World Tasks [arXiv 2026] (week4_agent p.91~93)
- Demystifying evals for AI agents [preprint 2026, Anthropic] (week4_agent p.80~83)
- Constitutional AI: Harmlessness from AI Feedback (Anthropic 2022) — 비교용
- Tulu 3 / Nemotron Nano 2 (week2_fm p.56)

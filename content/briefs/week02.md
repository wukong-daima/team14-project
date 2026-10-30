# 2주차: 파운데이션 모델 아키텍처 — 토크나이저부터 추론 최적화까지

> 한 줄 요약: 현대 LLM의 "사실상 표준" 부품(서브워드 토크나이저 · GQA/MLA/DSA · RoPE · Pre-Norm/RMSNorm · MoE)과 학습 레시피(SFT → 선호 튜닝 DPO/GRPO → On-Policy Distillation), 추론 가속(KV 캐시 · Speculative Decoding · MTP), 그리고 "AR vs Diffusion은 정말 다른가"라는 질문까지 한 번에 훑는 주차.

출처 PDF: `week2_fm.pdf` (128쪽, 송경우 교수, 연세대 MLAI Lab). 슬라이드 상당수가 그림 전용이라 텍스트 추출이 비어 있음(특히 p.10–19 Transformer 기본, p.68–88 Preference Tuning, p.91–95 KV Cache/Speculative Decoding). 아래 페이지 번호는 PDF 페이지.

---

## 강의 흐름

| 순서 | 섹션 | 페이지 | 내용 |
|---|---|---|---|
| 1 | Tokenizer & Transformer | 3–19 | word/char/subword 토크나이저, hidden state 용어, Transformer 기본 구조(Stanford CME295 슬라이드), Multi-head 예시(h=3) |
| 2 | Transformer Variants – Attention | 20–33 | MHA → MQA → GQA, MLA(DeepSeek-V2), 커널 관점(Implicit Kernel Attention), DeepSeek Sparse Attention(DSA), V4/V4.1·Qwen QSA |
| 3 | Transformer Variants – Positional Encoding | 34–41 | 사인 PE → 상대 PE(clipping) → RoPE(APE+RPE) |
| 4 | Transformer Variants – Normalization | 42–52 | Post-Norm vs Pre-Norm 그래디언트, LayerNorm → RMSNorm → pRMSNorm, DyT, BHyT(교수님 연구실, ICML 2026) |
| 5 | Transformer Variants – Architecture | 53–54 | MoE, DeepSeek MoE(shared/routed expert, auxiliary-loss-free) |
| 6 | Training | 55–67 | 학습 파이프라인(pt→cpt→SFT→PFT→RFT, Tulu 3/Nemotron Nano 2), Adapter/LoRA/Prefix tuning 통합 관점, ICL = gradient descent |
| 7 | Preference Tuning | 68–90 | RLHF(online) vs DPO(offline), PPO, GRPO 수식 해부, On-Policy Distillation(OPSD) |
| 8 | Inference | 91–96 | KV Cache, Speculative Decoding, MTP(independent→sequential, draft로 활용) |
| 9 | AR and Diffusion | 97–128 | AR vs Diffusion LM, 연속시간 masked diffusion == random-order AR, loss reweighting, 생성 순서 학습(insertion), Diffusion LM은 speculative draft로(DFlash/DSpark), Diffusion Forcing |

---

## 핵심 개념

### 1. 서브워드 토크나이저 (p.4–8)
- **(a) 전공 설명**: 토크나이저는 raw text → 정수 ID 시퀀스 변환기. Word-based는 어휘가 폭발하고(`malapropism → 170,000`) 미등록 단어(OOV)가 `[UNK]`로 손실됨. Character-based는 어휘가 작고 OOV가 없지만 시퀀스가 매우 길어지고 글자 단위 표현 학습이 어려움. Subword는 자주 쓰는 단어는 통째로(`dog`), 희귀 단어는 의미 단위로(`tokenization → [token, ##ization]`) 분절. BPE·WordPiece·Unigram·SentencePiece가 대표 알고리즘이며 현재 LLM의 표준.
- **(b) 중학생 비유**: 문장을 레고 블록으로 쪼개는 방법. 단어 하나를 블록 하나로 하면 블록 종류가 너무 많고 처음 보는 단어는 블록이 없음. 글자 하나를 블록 하나로 하면 종류는 적지만 블록을 너무 많이 꽂아야 함. 서브워드는 "자주 쓰는 덩어리"를 블록으로 삼는 절충안.
- **(c) 키워드/숫자**: OOV, `##` 접두(WordPiece), BPE, SentencePiece, Unigram. 파이프라인 `Raw text → Tokenizer → Input IDs → Model → Logits → Post-processing`.
- **(d) 슬라이드**: p.4–8.

### 2. Hidden state 용어 정리 (p.9)
- **(a)**: Embedding = 토큰 ID → 연속 벡터. Hidden state = 각 block/layer마다 존재하는 벡터. Layer = Attention/FFN 등 단위 연산, Block = Layer 묶음(Transformer Block). Penultimate layer = logit 직전(차원 축소 전 마지막) 벡터로 feature로 자주 사용. Logit = softmax 직전 벡터.
- **(b)**: 공장의 컨베이어 벨트. 원재료(토큰)가 들어와 각 작업대(layer)를 지날 때마다 반제품(hidden state)이 되고, 마지막 검수 직전 상태가 penultimate, 점수표가 logit.
- **(c)**: Embedding / Hidden state / Block / Penultimate / Logit.
- **(d)**: p.9.

### 3. MHA → MQA → GQA: KV 캐시 vs 성능 트레이드오프 (p.17, 22–27)
- **(a)**: MHA는 H개의 Q, K, V 헤드를 모두 가짐 → 추론 시 KV 캐시가 H에 비례. MQA(Shazeer 2019)는 K, V를 모든 헤드가 1개로 공유 → 메모리 1/H이지만 성능 저하. 기존 MHA 체크포인트를 MQA로 바꿀 때 K/V 투영 행렬을 mean pooling하여 단일 헤드로 만든 뒤 추가 학습(2-step: load → learn projection). GQA(Ainslie 2023)는 중간값: 쿼리 헤드를 g개 그룹으로 묶고 그룹마다 K/V 1개. **GQA-1 == MQA, GQA-H == MHA**, 논문 실험에서 GQA-8이 좋은 균형.
- **(b)**: 교실에 학생(쿼리) 32명이 있고 각자 교과서(K/V)를 한 권씩 가지면 사물함이 꽉 참(MHA). 교과서 1권을 반 전체가 돌려보면 사물함은 비지만 줄 서느라 공부가 안 됨(MQA). 4명당 1권씩 모둠으로 나누면 적당(GQA).
- **(c)**: KV 캐시 크기 ∝ `2 × n_kv_heads × d_head × n_layers × seq_len × bytes`. MHA: n_kv = H, GQA-g: n_kv = g, MQA: n_kv = 1. "GQA-8 performs better".
- **(d)**: p.17(h=3 예시), p.22–27.

### 4. MLA (Multi-head Latent Attention, DeepSeek-V2) (p.28)
- **(a)**: K와 V를 저장하는 대신 **저차원 잠재 벡터 c**로 공동 압축(low-rank joint compression)하여 캐시하고, 필요할 때 up-projection으로 K, V를 복원. down-scale/up-scale 파라미터 2개로 구성. KV 캐시를 헤드 수가 아니라 잠재 차원 d_c로 결정하므로 GQA보다 더 작게 만들면서 MHA급 성능을 노림.
- **(b)**: 교과서(K/V)를 통째로 사물함에 넣는 대신 "요약 노트(c)"만 넣어두고 필요할 때 노트를 보고 교과서 내용을 다시 펼치는 것.
- **(c)**: compressed latent vector c, down-/up-projection. (논문 수치: DeepSeek-V2에서 MLA 캐시 ≈ GQA 2.25 그룹 수준 — 슬라이드엔 없음, 논문 출처 표기 필요.)
- **(d)**: p.28.

### 5. DeepSeek Sparse Attention (DSA) 와 블록 단위 개선 (p.29–33)
- **(a)**: 어텐션은 RBF 커널로 볼 수 있고(Bochner 정리) `softmax(QKᵀ)V → φ(Q)φ(K)ᵀV`로 근사하면 효율화 가능(Implicit Kernel Attention, AAAI 21). DSA(DeepSeek-V3.2)는 **1) 가벼운 projection으로 index score를 계산해 top-K 토큰 선별 → 2) 각 쿼리가 선택된 K개 키에만 어텐션**. 복잡도 O(L²) → O(LK). DeepSeek V4/V4.1과 Qwen QSA는 **블록 단위 어텐션(key aggregation)** 으로 DSA를 개선.
- **(b)**: 책 1,000쪽을 다 읽는 대신 목차(가벼운 index)로 관련 있어 보이는 20쪽만 고른 뒤 그 20쪽만 정독하는 것. 블록 방식은 "장(章) 단위로 먼저 고르고 그 안에서 쪽을 고르는" 2단계.
- **(c)**: O(L²)→O(LK), index score, top-K, lightweight projection, block-level attention by key aggregation.
- **(d)**: p.29–33.

### 6. RoPE (Rotary Positional Embedding) (p.34–41)
- **(a)**: 원 Transformer는 사인/코사인 절대 위치 PE를 입력에 더함. 상대 PE(Shaw 2018, SHAPE)는 쿼리–키 간 상대 거리 정보를 어텐션에 주입하며 멀리 있는 거리는 clipping. RoPE(Su et al.)는 절대 위치 의존 **블록 대각 회전 행렬 R_i** 를 Q, K에 곱해 내적이 자동으로 상대 위치(i−j)에만 의존하도록 만듦 → APE + RPE 장점 결합. 현재 표준.
- **(b)**: 시계 바늘. 각 단어를 자기 자리만큼 시계 바늘처럼 돌려놓으면, 두 단어가 "얼마나 떨어져 있는지"는 두 바늘의 각도 차이로 바로 알 수 있음.
- **(c)**: APE, RPE, clipping, R_i = position-dependent block-diagonal rotation matrix.
- **(d)**: p.34–41.

### 7. Pre-Norm vs Post-Norm, RMSNorm/pRMSNorm, DyT, BHyT (p.42–52)
- **(a)**: Post-Norm은 잔차 합 뒤에 정규화 → 손실의 l번째 층 그래디언트가 곱 형태로 누적되어 폭발/소실. Pre-Norm은 서브층 전 정규화 → 그래디언트가 **덧셈(항등 경로)** 으로 전파되어 안정(Wang 2019). RMSNorm은 평균 빼기(re-centering)를 생략하고 RMS로만 스케일 → 연산 절감, pRMSNorm은 앞 p% 원소로 RMS 추정. DyT는 LN의 S자 입출력 관계를 `y = γ·tanh(αx) + β`로 대체(통계 계산 불필요)하나 실제론 성능 감소 관측. BHyT(교수님 연구실, ICML 2026)는 블록당 분산을 1번만 정확히 계산하고 나머지는 병렬 근사(κ=10, p=0.99).
- **(b)**: 계단을 내려갈 때 매 층마다 바닥을 평평하게(정규화) 해두고 내려가면(Pre-Norm) 안 넘어지지만, 내려간 뒤에 평평하게 하면(Post-Norm) 층이 깊어질수록 휘청거림. RMSNorm은 "평평하게 하기"를 더 싸게 하는 법.
- **(c)**: Pre-Norm, RMSNorm(re-centering 생략), pRMSNorm, DyT `γ·tanh(αx)+β`, BHyT κ=10.
- **(d)**: p.42–52.

### 8. MoE와 DeepSeek MoE (p.53–54)
- **(a)**: dense FFN을 여러 전문가 FFN으로 바꾸고 gate가 토큰마다 top-k 전문가를 선택. 총 파라미터는 크지만 활성 파라미터는 일부라 같은 compute로 모델/데이터 규모를 키움. 토큰별로 독립 동작. DeepSeek 변형: **shared expert(항상 활성) + routed expert**, 그리고 전문가 쏠림 방지용 auxiliary loss 대신 **bias로 라우팅을 조절하는 auxiliary-loss-free 전략**.
- **(b)**: 병원. 환자(토큰)가 오면 접수대(gate)가 증상에 맞는 전문의 몇 명만 배정. 의사가 100명 있어도 한 환자는 2명만 봄. shared expert는 모든 환자가 거치는 "내과 기본 진료".
- **(c)**: top-k gating, shared/routed expert, auxiliary-loss-free(bias), "same compute budget as dense".
- **(d)**: p.53–54.

### 9. 학습 파이프라인과 PEFT(Adapter/LoRA/Prefix) (p.56–65)
- **(a)**: Base I(pt) → Base II(cpt, continual pretrain) → SFT/IFT → PFT(preference) → RFT(reinforce). 단계는 반복 가능(Tulu 3, Nemotron Nano 2). PEFT: Adapter는 d→m→d 병목(2md+d+m 파라미터), LoRA는 `h = W₀x + BAx`, ΔW=BA 저랭크·초기 0, GPT-3 기준 학습 파라미터 1/10,000. "Unified View"(ICLR 2021)는 prefix tuning도 adapter의 변형(가중합만 다름)으로 통합.
- **(b)**: 이미 다 만들어진 로봇(사전학습 모델)에 작은 부품 몇 개(LoRA)만 끼워 새 일을 가르치는 것. 로봇 전체를 다시 만들 필요 없음.
- **(c)**: pt/cpt/SFT/PFT/RFT, Adapter 2md+d+m, LoRA ΔW=BA, 10,000×.
- **(d)**: p.56–65.

### 10. 선호 튜닝: RLHF(PPO) vs DPO vs GRPO (p.68–89)
- **(a)**: RLHF는 보상 모델을 학습 → PPO로 정책 최적화하는 **online RL**. PPO는 policy·reference·reward·value 4개 모델과 반복 롤아웃이 필요해 무겁고, 보상 모델 오류를 파고드는 reward hacking에 취약. value model + GAE로 advantage 계산. DPO는 보상 모델 없이 선호/비선호 쌍으로 정책을 직접 최적화하는 **offline RL**. GRPO 목적함수 3요소: **확률비**(새 정책/데이터 생성 정책) × **클리핑**(PPO와 동일한 안정화) × **그룹 상대 advantage**(같은 프롬프트의 다른 응답 대비 우열) — 이것이 PPO의 value/critic 모델을 대체.
- **(b)**: 글짓기 대회. RLHF는 심사위원 로봇을 따로 만들어 점수를 매기게 함(복잡). DPO는 "이 글이 저 글보다 좋다"는 쌍만 보고 바로 배움. GRPO는 같은 주제로 8편 쓰게 한 뒤 "그중에서 잘 쓴 편"을 칭찬 — 절대 점수표 없이 상대 평가.
- **(c)**: online vs offline, 4 models(PPO), reward hacking, GRPO = ratio × clip × group-relative advantage.
- **(d)**: p.68–89 (수식은 p.84, p.89 텍스트).

### 11. On-Policy Distillation / OPSD (p.90)
- **(a)**: 고정된 교사 생성 데이터(offline distillation) 대신 **학생이 현재 정책으로 생성한 궤적**에 대해 교사(또는 더 강한 자기 버전)가 **토큰 단위 감독**을 제공. 학생이 실제 추론에서 방문하는 상태에서 배우므로 train–inference 분포 불일치가 줄고, 매 토큰 dense supervision은 유지.
- **(b)**: 선생님이 모범답안을 외우게 하는 대신, 학생이 직접 푼 풀이를 옆에서 한 줄 한 줄 봐주면서 고쳐주는 것.
- **(c)**: on-policy, token-level supervision, dense, distribution mismatch 감소.
- **(d)**: p.90.

### 12. 추론 가속: KV Cache, Speculative Decoding, MTP (p.91–96)
- **(a)**: KV 캐시는 이전 토큰의 K, V를 저장해 재계산을 피함(메모리 ↔ 연산 교환). Speculative decoding은 작은 draft 모델이 여러 토큰 초안을 내고 큰 target 모델이 한 번의 forward로 병렬 검증 — 분포는 보존(이론상 무손실). MTP는 다음 1토큰이 아니라 **여러 미래 토큰**을 예측하도록 학습(Independent → Sequential MTP)하여 장기 의존 표현을 유도하고, 추론 시 MTP 모듈이 draft 역할을 해 speculative decoding과 결합.
- **(b)**: 받아쓰기. 빠른 후배(draft)가 다음 다섯 글자를 먼저 적으면, 느리지만 정확한 선배(target)가 한눈에 훑어 맞는 데까지만 승인. MTP는 선배가 아예 "다음 몇 글자"를 한 번에 떠올리도록 훈련하는 것.
- **(c)**: draft/target, verify in parallel, Independent→Sequential MTP, "MTP module as draft predictor".
- **(d)**: p.91–96.

### 13. AR vs Diffusion: 정말 다른 패러다임인가 (p.97–128)
- **(a)**: 연속시간 masked diffusion == **random-order AR**(N! 순열). 병렬 생성은 diffusion 고유 속성이 아니라 "이산화 스케줄"(한 스텝에 몇 토큰을 unmask하느냐)의 결과이며, 슬로우-투-패스트(코사인) 스케줄이 이산화 오차 ε_disc를 줄임. 연속 diffusion의 높은 지각 품질도 loss reweighting(log-SNR λ 기준) 덕분이 커서 MD4에도 적용 가능. 따라서 핵심 질문은 "어떤 변수를, 어떤 순서로, 언제 생성하느냐". 나아가 생성 순서를 학습(insertion 기반 정책)하면 SMILES처럼 구조 토큰을 먼저 만들고 원자를 채우는 전략을 스스로 발견. 현재 가장 실용적인 diffusion LM 용도는 AR의 **speculative draft**(DFlash, DSpark; SGLang/vLLM 지원). Diffusion Forcing = 토큰별 독립 연속 soft masking(AR 유연성 + diffusion guidance).
- **(b)**: 빈칸 채우기 문제지. 왼쪽부터 순서대로 채우면 AR, 아무 칸이나 골라 채우면 random-order AR, 여러 칸을 동시에 채우면 "병렬". diffusion LM은 사실 "아무 칸이나 여러 개 동시에" 채우는 방식일 뿐 마법이 아님.
- **(c)**: masked diffusion ≡ random-order AR, ε_disc, slow-to-fast schedule, loss reweighting(λ=log-SNR), insertion policy, DFlash/DSpark, Diffusion Forcing.
- **(d)**: p.97–128.

---

## 요약본 정정

| 요약본 | 정정 | 근거 |
|---|---|---|
| "DSA (DeepSpeed Sparse Attention)" | **DeepSeek Sparse Attention (DSA)**, 출처는 DeepSeek-V3.2 기술 보고서. DeepSpeed(MS 라이브러리)와 무관 | p.32–33 |
| "QSA (Qwen-Next): DSA를 개선, 토큰을 블록 단위로 묶어 계층적으로 비교" | 슬라이드 표기는 **"DeepSeek V4/V4.1 and Qwen QSA have improved DSA (e.g., block-level attention by key aggregation)"**. 즉 블록 단위 개선은 DeepSeek V4/V4.1과 Qwen QSA 공통이며, "Qwen-Next"라는 명칭은 슬라이드에 없음(Qwen3-Next 모델명과 혼동 가능 → 사이트에서는 "Qwen QSA"로 표기) | p.33 |
| "OPD (On-policy Preference Distillation)" | 슬라이드 제목은 **On-Policy Distillation**, 본문은 **On-policy self-distillation (OPSD)**. "Preference"라는 단어는 없음 | p.90 |
| "OPD: 최종 정답만 보는 GRPO의 희소 보상 문제를 해결" | 슬라이드의 근거는 "standard distillation의 train–inference distribution mismatch 감소 + dense token-level supervision 유지". GRPO 대비 희소보상 해결은 구두 설명으로 보임(4주차 요약과 일치) — 틀린 건 아니나 출처 구분 필요 | p.90 |
| 요약본에 MLA 없음 | **MLA(DeepSeek-V2)** 가 GQA 다음 슬라이드로 명시적으로 다뤄짐. KV 캐시 축소의 핵심 기법이므로 추가 필요 | p.28 |
| 요약본에 RMSNorm/DyT/BHyT 없음 | Pre-Norm 다음에 **RMSNorm → pRMSNorm → DyT → BHyT(교수님 연구실 ICML 2026)** 흐름이 있음. 시험 출제 가능성 높음 | p.46–52 |
| 요약본 MoE 설명에 DeepSeek 변형 없음 | **shared expert + routed expert, auxiliary-loss-free(bias)** 명시 | p.54 |
| 요약본에 PEFT·ICL·RLHF/DPO/PPO/GRPO 수식·AR vs Diffusion 전체 없음 | p.56–67, 68–89, 97–128 — 강의 후반부 약 60쪽이 요약본에 빠짐. 특히 **GRPO 3요소**(p.89)와 **"masked diffusion == random-order AR"**(p.101, 118)은 핵심 | 해당 페이지 |
| "Speculative Decoding: 2~3배, 평균 수락 4개" | 슬라이드(p.92–94)는 그림 전용으로 수치 없음. 구두 설명으로 추정 → "강의 중 언급" 표기 | p.92–94 |
| "트랜스포머 한계 O(n²)" | 슬라이드 표기는 **O(L²)→O(LK)** (L = 시퀀스 길이, K = 선택 토큰 수) | p.32 |

---

## 추천 인터랙션

### ★ 대표: "KV 캐시 계산기 — MHA / GQA / MQA / MLA 슬라이더" (난이도: 중)
- **입력**: 슬라이더 4개 — 쿼리 헤드 수 H(8~128), KV 그룹 수 g(1~H, GQA), 시퀀스 길이 L(1K~1M, 로그 스케일), 레이어 수(16~96). 토글: 정밀도(FP16/FP8), MLA 잠재 차원 d_c(예: 512).
- **출력**: (1) 헤드 다이어그램 — Q 헤드 H개가 원으로 늘어서고, 아래 K/V 박스가 g개만 남으며 선이 모임(g=1이면 MQA, g=H이면 MHA). (2) KV 캐시 메모리 막대 4개(MHA/GQA-g/MQA/MLA) 실시간 갱신, GB 단위 숫자. (3) "이 설정은 GPU 80GB 몇 장?" 한 줄.
- **시각화**: SVG — 원(Q 헤드), 사각형(K/V), 선(그룹 연결), 가로 막대(메모리). CSS transition으로 막대 길이 애니메이션.
- **공식**: `bytes = 2 × layers × n_kv × d_head × L × bytes_per_elem`, MLA는 `layers × d_c × L × bytes`.
- **왜 이것**: 2~3주차의 핵심 메시지("KV 캐시가 긴 컨텍스트의 병목")를 숫자로 체감. 3주차 페이지와 자연스럽게 연결.

### 대안 1: "MoE 라우터 시뮬레이션" (난이도: 중하)
- **입력**: 문장 입력(또는 샘플 문장 클릭), 전문가 수 E(4~16), top-k(1~4), "shared expert 켜기" 토글, "auxiliary-loss-free bias" 토글.
- **출력**: 토큰이 하나씩 흘러가며 gate가 전문가 박스 중 k개에 선을 긋고 불이 켜짐. 하단에 전문가별 사용 횟수 히스토그램 — bias 토글을 켜면 쏠림이 완화되는 모습(시뮬레이션용 가짜 score + bias 보정).
- **시각화**: SVG 박스(전문가) + 애니메이션 선, 막대 히스토그램.

### 대안 2: "Speculative Decoding 수락 애니메이션" (난이도: 중하)
- **입력**: "다음 블록 생성" 버튼, draft 길이 k(2~8), draft 정확도 슬라이더(0.3~0.95).
- **출력**: draft 모델이 k개 토큰을 빠르게 내놓고(작은 글자, 회색), target이 한 번에 검증해 앞에서부터 맞는 토큰은 초록, 첫 불일치 지점에서 빨강 후 target 토큰으로 교체. 누적 "평균 수락 토큰 수"와 "AR 대비 속도 향상 배수"를 표시 — 정확도 올려도 2~3배 근처에서 포화하는 걸 체감.
- **시각화**: 토큰 칩(사각형) 행 + 색상 전환, 작은 꺾은선(배수).

(보너스, 난이도 하: 토크나이저 비교 — 영어 문장을 입력하면 word/char/subword 가짜 분절(간단 규칙: 공백/글자/접미사 사전) 3줄로 보여주고 토큰 수 비교.)

---

## 다이어그램 후보 (정적 SVG)

1. **"MHA vs MQA vs GQA vs MLA" 4분할 비교도**
   - 각 칸: 위에 Q 헤드 원 8개, 아래 K/V 사각형(MHA 8개 / MQA 1개 / GQA 2개 / MLA: 작은 "c" 캡슐 1개 + up-projection 화살표로 K,V 복원).
   - 라벨: "KV cache ∝ 8 / 1 / 2 / d_c", 하단 캡션 "GQA-1 = MQA, GQA-H = MHA".
2. **"Pre-Norm vs Post-Norm 잔차 블록"**
   - 두 열. 각 열: 입력 → [Norm] → Attention → ⊕ → [Norm] → FFN → ⊕ 순서가 다름. 잔차 경로를 굵은 선으로, Post-Norm 쪽은 그래디언트 화살표가 Norm을 매번 통과(곱 기호), Pre-Norm 쪽은 항등 경로로 직행(덧셈 기호). 캡션 "Stable gradient".
3. **"LLM 학습 레시피 파이프라인 + 추론 가속"**
   - 가로 흐름: pt → cpt → SFT/IFT → PFT(DPO/RLHF) → RFT(GRPO) → OPD. 각 박스 아래 "필요 모델 수"(RLHF 4, DPO 2, GRPO 2+그룹 롤아웃). 오른쪽에 추론 박스: KV cache / Speculative(draft→target) / MTP(backbone 1회 + 헤드 n회).
   - (보조) **DSA 2단계도**: 쿼리 1개 → 가벼운 indexer → 전체 키 중 top-K 하이라이트 → 선택된 키에만 어텐션 선. 캡션 O(L²)→O(LK).

---

## 모델 비교 포인트

| 개념 | 수업에서 다룬 모델·방식 | Claude (공개 문서 범위) | 기타 모델 (공개 정보) | 출처 후보 |
|---|---|---|---|---|
| 토크나이저 | 서브워드(BPE/WordPiece/SentencePiece) 표준 | 토크나이저 종류·어휘 크기 **비공개**. 공개된 것은 API의 토큰 카운팅 엔드포인트와 "토큰 ≈ 3.5 영문자" 수준의 안내 | GPT: tiktoken(o200k 등) 공개. Llama 3: 128K 어휘 BPE. Qwen/DeepSeek: 공개 토크나이저 | Anthropic docs(token counting), tiktoken repo, Llama 3 보고서 |
| 어텐션(MHA/GQA/MLA/DSA) | GQA 표준, DeepSeek MLA·DSA | **비공개** | Llama 2/3·Qwen·Gemma·gpt-oss: GQA(공개). DeepSeek-V2/V3: MLA, V3.2: DSA. Gemma 3·gpt-oss: local/global(sliding window) 교대 | GQA 논문, DeepSeek-V2/V3/V3.2 보고서, gpt-oss 모델 카드, Gemma 3 보고서 |
| 위치 인코딩 | RoPE 표준 | **비공개** | Llama·Qwen·Gemma·DeepSeek·gpt-oss: RoPE(공개). 긴 컨텍스트용 YaRN 등 확장 사용 사례 | RoFormer, YaRN |
| 정규화 | Pre-Norm, RMSNorm | **비공개** | Llama·Qwen·DeepSeek: Pre-Norm + RMSNorm(공개). Gemma 2/3: pre+post RMSNorm 병용 | 각 기술 보고서 |
| MoE | DeepSeek MoE(shared/routed, aux-loss-free) | **비공개** (Claude가 MoE인지 dense인지 공식 문서 없음) | Gemini 1.5: MoE 명시. Llama 4·Qwen3-MoE·DeepSeek-V3·gpt-oss: MoE 공개. GPT-4: 비공개(루머만, 인용 금지) | Gemini 1.5 보고서, Llama 4 블로그, gpt-oss 카드 |
| 컨텍스트 길이 | KV 캐시 병목 | 공개: 모델별 컨텍스트 창(예: 200K, 일부 모델 1M 베타) — **정확한 수치는 작성 시점에 docs에서 확인 필요** | Gemini: 1M~2M 공개. GPT-4.1: 1M 공개. Llama 4 Scout: 10M 주장 | 각 사 docs/모델 카드 |
| 선호 튜닝 | RLHF(PPO)/DPO/GRPO | 공개: RLHF + **Constitutional AI(RLAIF)** 논문(2022). 세부 알고리즘(PPO/DPO 여부)·GRPO 사용 여부 **비공개** | DeepSeek-R1: GRPO 공개. Llama 3: SFT+RS+DPO 공개. Tulu 3: SFT→DPO→RLVR 공개. OpenAI: RLHF(InstructGPT) 공개, 이후 비공개 | Constitutional AI 논문, DeepSeek-R1, Llama 3, Tulu 3 |
| On-policy distillation | OPD/OPSD | 공개 정보 없음 — **비공개** | DeepSeek-R1 distill 모델: offline SFT distillation(공개). Qwen3: 강→약 distillation 언급(공개) | DeepSeek-R1, Qwen3 보고서 |
| Speculative decoding / MTP | draft-target, MTP | 서빙 내부 기법 **비공개** | DeepSeek-V3: MTP 모듈 공개(speculative draft 활용). OpenAI API: "Predicted Outputs" 기능 공개(speculative 계열). vLLM/SGLang: 오픈소스 지원 | DeepSeek-V3, OpenAI docs, vLLM docs |
| 확장 추론(reasoning) | GRPO로 추론 강화(R1 계열) | 공개: **extended thinking** 기능(사고 토큰 예산 지정, API 파라미터) — 학습 방식은 비공개 | OpenAI o-시리즈: RL 기반 추론 학습 공개(세부 비공개). DeepSeek-R1: 전 과정 공개 | Anthropic docs(extended thinking), DeepSeek-R1 |
| AR vs Diffusion | AR 표준, diffusion LM은 draft 용도 | Claude: AR로 알려져 있으나 공식 아키텍처 문서 없음 → **비공개** | Gemini Diffusion(실험 모델) 공개 발표. Inception Mercury, LLaDA: diffusion LM 공개 | Google I/O 발표, LLaDA 논문 |

> 작성 원칙: "비공개"는 추측으로 채우지 않는다. "확인 필요"는 사이트 작성 시점에 공식 docs 링크를 확인해 수치를 넣는다.
> 비교의 교육적 메시지: 수업에서 배운 부품(GQA/RoPE/Pre-Norm/MoE)은 **공개 모델에서는 사실상 표준으로 확인**되고, Claude/GPT는 **학습 철학(Constitutional AI, RLHF)과 제품 기능(extended thinking, 컨텍스트 창)** 수준에서만 비교 가능하다.

---

## 시험 포인트 (클로즈북 12/14 대비)

1. 토크나이저 3종의 장단점과 서브워드가 표준인 이유(OOV ↔ 시퀀스 길이 트레이드오프).
2. MHA/MQA/GQA의 KV 캐시 크기 관계와 성능 순서, **GQA-1 = MQA, GQA-H = MHA**. MLA는 "저차원 잠재 c로 K,V 공동 압축".
3. DSA 2단계(index score로 top-K 선별 → 선택 키에만 어텐션), O(L²)→O(LK). 블록 단위 개선(V4/V4.1, Qwen QSA).
4. RoPE가 왜 APE+RPE인지(회전 행렬 곱 → 내적이 상대 위치 함수).
5. Pre-Norm이 안정적인 이유(그래디언트가 덧셈/항등 경로로 전파), RMSNorm이 싼 이유(re-centering 생략).
6. MoE의 compute 이점(총 파라미터 ≠ 활성 파라미터), DeepSeek의 shared/routed expert, auxiliary-loss-free.
7. RLHF(online, 4개 모델, reward hacking) vs DPO(offline, 보상 모델 없음) vs GRPO(그룹 상대 advantage가 value 모델 대체, 확률비·클리핑).
8. Speculative decoding(무손실 병렬 검증)·MTP(여러 미래 토큰 예측, draft로 활용), 그리고 "masked diffusion = random-order AR, 병렬성은 스케줄의 산물".

### 예상 문제

**Q1.** 쿼리 헤드 32개, d_head 128, 레이어 32, 시퀀스 길이 128K, FP16인 모델에서 MHA 대비 GQA-8, MQA의 KV 캐시 크기 비율을 쓰고, GQA-8의 KV 캐시 용량(GB)을 계산하라.
> **A.** 비율 = 32 : 8 : 1 → GQA-8은 MHA의 1/4, MQA는 1/32. GQA-8 용량 = 2(K,V) × 32 layers × 8 heads × 128 × 131,072 tokens × 2 bytes ≈ 17.2 GB (MHA는 ≈ 68.7 GB).

**Q2.** Post-Norm보다 Pre-Norm이 깊은 Transformer 학습에 안정적인 이유를 그래디언트 전파 관점에서 설명하라.
> **A.** Pre-Norm은 잔차 경로가 정규화를 거치지 않는 항등 경로이므로 손실의 l층 그래디언트가 상위층 그래디언트의 **합** 형태로 전달된다. Post-Norm은 매 층 Norm을 통과하며 야코비안이 **곱**으로 누적되어 층이 깊어질수록 폭발/소실한다.

**Q3.** GRPO 목적함수의 세 구성 요소를 쓰고, 각각이 PPO의 어떤 부분을 대체/계승하는지 설명하라. GRPO가 학습 불가능한 상황도 한 가지 제시하라.
> **A.** (1) 확률비 r = π_new/π_old — PPO의 importance ratio 계승. (2) 클리핑 — PPO의 정책 급변 방지 계승. (3) 그룹 상대 advantage — 같은 프롬프트의 G개 응답 간 정규화된 보상으로 PPO의 value/critic 모델을 대체. 한 프롬프트의 롤아웃이 전부 실패(또는 전부 성공)하면 advantage가 0이 되어 학습 신호가 없다.

**Q4.** DeepSeek Sparse Attention(DSA)의 동작 2단계와 복잡도 변화를 쓰고, 이것이 KV 캐시 메모리 자체를 줄이는지 여부를 논하라.
> **A.** 1) 가벼운 projection으로 각 쿼리–키 index score를 구해 top-K 키를 선택, 2) 선택된 K개 키에만 어텐션. 연산 O(L²)→O(LK). 단, 모든 키의 KV는 여전히 캐시에 있어야 하므로 **연산량**을 줄이는 것이지 KV 캐시 **저장 메모리**를 직접 줄이는 것은 아니다(메모리 축소는 GQA/MLA/슬라이딩 윈도우의 역할).

**Q5.** "Diffusion 언어 모델은 병렬 생성이 가능해 AR보다 본질적으로 빠르다"는 주장을 강의 내용에 근거해 비판하라.
> **A.** 연속시간 masked diffusion은 random-order AR과 동치이므로 병렬성은 diffusion 고유 속성이 아니라 이산화 스케줄(한 스텝에 몇 토큰을 unmask하는가)에서 나온다. 병렬로 많이 뽑을수록 이산화 오차 ε_disc가 커지며, 슬로우-투-패스트 스케줄이 필요하다. 실제로 현재 가장 실용적인 쓰임은 diffusion LM을 AR 모델의 speculative draft(DFlash 등)로 쓰는 것이다.

(보너스) **Q6.** OPD/OPSD가 standard distillation과 다른 점 두 가지. → on-policy(학생이 생성한 궤적에서 학습 → 분포 불일치 감소), token-level dense supervision 유지.

---

## 출처

- HuggingFace tokenizer summary: https://huggingface.co/docs/transformers/tokenizer_summary (p.4–7)
- Stanford CME295 Lecture 1 slides: https://cme295.stanford.edu/slides/fall25-cme295-lecture1.pdf (p.10–19, 68–89)
- Shazeer, "Fast transformer decoding: One write-head is all you need", arXiv:1911.02150 (MQA, p.22–25)
- Ainslie et al., "GQA: Training generalized multi-query transformer models from multi-head checkpoints", arXiv:2305.13245 (p.17, 26–27)
- DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model (MLA, p.28)
- Implicit Kernel Attention [AAAI 21] (p.29–31)
- DeepSeek-V3.2: Pushing the Frontier of Open Large Language Models (DSA, p.32–33)
- Positional encoding 설명: https://aiml.com/explain-the-need-for-positional-encoding-in-transformer-models/ (p.34–35)
- Kiyono et al., "SHAPE: Shifted absolute position embedding", arXiv:2109.05644; Shaw et al., "Self-attention with relative position representations", arXiv:1803.02155 (p.36–39)
- Su et al., "RoFormer: Enhanced transformer with rotary position embedding", Neurocomputing 568 (2024) (p.40–41)
- Wang et al., "Learning deep transformer models for machine translation", arXiv:1906.01787 (Pre/Post-Norm, p.42–45)
- Zhang & Sennrich, "Root mean square layer normalization", NeurIPS 2019 (p.47–50)
- Zhu et al., "Transformers without Normalization", arXiv 2025 (DyT, p.51)
- "Bounded Hyperbolic Tangent: A Stable and Efficient Alternative to Pre-Layer Normalization in LLMs", ICML 2026 (BHyT, MLAI Lab, p.52)
- DeepSeek-V3 Technical Report; https://huggingface.co/blog/moe (p.53–54)
- Houlsby et al., "Parameter-Efficient Transfer Learning for NLP", ICML 2019 (Adapter, p.58)
- Hu et al., "LoRA: Low-Rank Adaptation of Large Language Models", ICLR 2022 (p.59)
- He et al., "Towards a Unified View of Parameter-Efficient Transfer Learning", ICLR 2021 (p.60–64)
- "The Expressive Power of Low-Rank Adaptation", ICLR 2024 (p.65)
- von Oswald et al., "Transformers learn in-context by gradient descent", ICML 2023 (p.67)
- Hidden state 용어: https://wikidocs.net/blog/@jaehong/18261/ (p.9)
- AR vs Diffusion 개관: https://arxiv.org/pdf/2505.15045 (p.98–99, 127–128)
- Jiaxin Shi, Simons Institute talk: https://jiaxins.io/talks/simons_talk.pdf (p.100–126); D3PM "Structured denoising diffusion models in discrete state-spaces", arXiv 2021 (p.102)
- 학습 레시피 예시: Tulu 3, Nemotron Nano 2 (p.56)

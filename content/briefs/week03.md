# 3주차: Foundation Models II — KV 캐시 압축의 끝까지 (DeepSeek-V4.1-Flash) 와 Perceiver

> 한 줄 요약: 긴 컨텍스트 시대의 병목은 KV 캐시다. DeepSeek-V4.1-Flash는 "더 작게 저장(FP4) · 덜 저장(CSA2 압축) · 레이어 간 공유(CSA2 cross-layer reuse) · 오래 들고 있지 않기(Bounded Replay) · 디코더 prefill 생략(CED)"의 다섯 가지를 한 아키텍처에 묶어 100만 토큰 글로벌 KV를 약 0.89GB로 줄였고, Perceiver는 입력 길이 M과 무관한 고정 크기 latent N으로 모달리티 불문 O(MN) 처리를 제안했다.

> 주의: 이 PDF는 "Week 3-1"이며 27페이지다. 목차(2p)에 있는 Mamba(Mamba-2/3), Gated Delta Networks(DeltaNet, GDN, KDA, GDN-2), Hybrid(Kimi Linear, Qwen3.8-Flash-Next, Nvidia Nemotron)는 이 파일에 **없다**(3-2 자료로 추정). 사용자 요약본도 이 부분은 다루지 않는다. 이 브리프는 PDF에 실제로 있는 내용만 다룬다.

---

## 강의 흐름

| 순서 | 섹션 | 페이지 |
|---|---|---|
| 0 | 표지·목차 (Transformers / Perceiver / Mamba / GDN / Hybrid) | 1–2 |
| 1 | Transformers: DeepSeek-V4.1-Flash 개요 — KV 캐시 압축 4대 전략 | 3–4 |
| 2 | V4.1-Flash 구조 수치 (40 레이어, 552B+196B, 8B/16B 활성, SWA 128, 희소 선택 512) | 5 |
| 3 | Engram (학습된 거대 사전, 레이어 1·14에 배치) | 6 |
| 4 | Single-Pass mHC (Manifold-Constrained Hyper-Connections) | 7–8 |
| 5 | CED (Causal Encoder-Decoder): 디코더 글로벌 KV를 인코더 hidden state에서 생성, prefill 비용 절반 | 9–10 |
| 6 | CSA2: KV 압축(m=2) + 레이어 간 공유 (Full → Reuse → Reuse → Reuse → Reindex) | 11 |
| 7 | FP4 글로벌 KV (SWA KV는 FP8), 890 bytes/token | 12 |
| 8 | Bounded Replay: 마지막 128 토큰만 디코더 재생으로 SWA 상태 초기화 | 13 |
| 9 | Perceiver: 모달리티 통합, byte array M vs latent array N, O(MN) | 14–22 |
| 10 | Perceiver IO: 출력 쿼리 M으로 구조화된 출력(분할 등) | 23–26 |
| 11 | Graph Perceiver IO: 그래프(관계) 정보 결합 | 27 |

---

## 핵심 개념

### 1. KV 캐시 압축의 4대 전략 (V4.1-Flash 설계 원칙)
- (a) 전공: 긴 컨텍스트 추론에서 메모리는 모델 가중치가 아니라 KV 캐시가 지배한다. V4.1-Flash는 KV 캐시를 네 축으로 공략한다. ① 각 엔트리를 더 작게 저장(FP4), ② 저장할 시퀀스 엔트리 수를 줄임(CSA2 compression), ③ 레이어마다 별도 KV 캐시를 두지 않음(CSA2 cross-layer reuse), ④ SWA KV를 오래 보관하지 않음(Bounded Replay). 여기에 CED가 prefill 연산 자체를 절반으로 줄인다.
- (b) 중학생: 책상 위에 메모지를 쌓아둔다고 생각하자. 메모지를 더 작은 글씨로 쓰고(FP4), 두 장을 한 장으로 합치고(압축), 같은 메모를 여러 서랍에 복사하지 않고(공유), 최근 메모 몇 장만 남기고 버리는(Bounded Replay) 네 가지 정리법이다.
- (c) 키워드: FP4, CSA2 compression, CSA2 cross-layer reuse, Bounded Replay, prefill.
- (d) 페이지: 4.

### 2. V4.1-Flash 구조 수치
- (a) 전공: 40개 causal Transformer 레이어 = 20 Causal Encoder + 20 Causal Decoder. 백본 파라미터 552B, 별도 Engram 파라미터 196B. 토큰당 활성 파라미터는 prefill 시 8B(인코더만), decoding 시 16B(인코더+디코더). 첫 두 레이어는 SWA만(윈도우 128), 나머지는 CSA2+SWA. 희소 어텐션 선택 토큰 수 512. 프롬프트는 인코더로만 처리(prefill), 생성 토큰은 인코더→디코더 파이프라인을 다시 통과.
- (b) 중학생: 40층 건물인데 아래 20층은 "읽기 전담(인코더)", 위 20층은 "쓰기 전담(디코더)"이다. 긴 질문을 읽을 땐 아래 20층만 돌고, 답을 한 글자씩 쓸 때만 40층을 다 돈다.
- (c) 숫자: 40 = 20+20 레이어, 552B 백본, 196B Engram, 8B(prefill)/16B(decode) 활성, SWA window 128, Top-512 희소 토큰.
- (d) 페이지: 5.

### 3. Engram
- (a) 전공: 짧은 국소 어휘 패턴(short local lexical pattern) 자체를 메모리 주소로 쓰는 거대한 학습된 사전(dictionary). Transformer가 여러 레이어 연산을 거쳐 재구성해야 할 패턴을 빠른 조회(lookup)로 가져온다. V4.1-Flash에서는 레이어 1과 14(0-indexed)에 Engram 모듈이 배치된다. 파라미터는 백본과 별도로 196B.
- (b) 중학생: 자주 쓰는 숙어는 머리로 매번 계산하지 않고 "숙어 사전"에서 바로 찾아보는 것. 본체(Transformer)는 어려운 긴 문맥 이해에만 집중할 수 있다.
- (c) 키워드: learned dictionary, lexical pattern = memory address, layers 1 & 14, 196B.
- (d) 페이지: 6. (요약본의 "바이그램/트라이그램 해시, O(1) 조회"는 PDF 문구에 없고 강의 구두 설명으로 보임 — 사이트에 쓸 땐 "강의 설명" 표시.)

### 4. mHC (Manifold-Constrained Hyper-Connections) / Single-Pass mHC
- (a) 전공: Residual connection은 1차선 고속도로. Hyper-Connections(HC)는 n개의 residual stream을 병렬로 유지하고, 각 블록(attention/MoE) 입력 전에 관련 stream을 섞는다. mHC는 이 섞는 매핑을 무제한으로 두지 않고 doubly stochastic matrix(행·열 합이 1)로 제약해 변환이 안정 범위에 머물게 한다. Single-Pass mHC는 이 변환을 한 번의 패스로 효율적으로 구현한 것.
- (b) 중학생: 고속도로를 1차선에서 여러 차선으로 넓히되, 차선 변경 규칙을 정해서(한 차선이 다 빨려 들어가거나 텅 비지 않게) 교통이 꼬이지 않게 만든 것.
- (c) 키워드: residual stream n개, doubly stochastic matrix, 학습 안정성, single-pass.
- (d) 페이지: 7–8.

### 5. CED (Causal Encoder-Decoder)
- (a) 전공: prefill 단계에서 "모든 입력 토큰을 모든 상위 레이어에 통과시켜야만 글로벌 KV를 만들 수 있는가?"에 대한 답. CED는 각 디코더 레이어의 글로벌 K, V를 그 레이어의 hidden state가 아니라 **인코더 최종 hidden state로부터** 생성한다(인코더의 K,V를 그대로 재사용하는 게 아니라 hidden state를 재료로 씀). 긴 입력은 대부분 20개 인코더 레이어만 통과하면 되므로 prefill 연산이 N≫n_win일 때 대략 절반. 디코더의 SWA(로컬) KV는 여전히 디코더 각 레이어 hidden state에서 만들어야 하므로 Bounded Replay로 보완. CSA2 cross-layer sharing과 결합하면 인코더 유래 글로벌 KV를 여러 디코더 레이어가 공유.
- (b) 중학생: 긴 책을 읽을 때 "읽기 담당(인코더)"이 요약 노트를 만들면, "쓰기 담당(디코더)"은 책을 처음부터 다시 읽지 않고 그 노트만 보고 글을 쓴다. 다만 마지막 몇 줄은 직접 읽어야 문맥이 이어진다(Bounded Replay).
- (c) 수식/숫자: prefill 연산 ≈ 1/2 (N≫n_win), decode 시 16B 활성.
- (d) 페이지: 9–10.

### 6. CSA2 — 압축(Compression) + 레이어 간 공유(Full/Reuse/Reindex)
- (a) 전공: 압축: 보통 토큰당 KV 엔트리 1개인데 m=2면 두 토큰당 1개(차원별 가중 결합). 공유: KV 공유는 메모리를, 희소 선택 위치(sparse position) 공유는 검색 연산을 줄이며 둘은 반드시 결합될 필요 없음. 레이어 패턴 Full → Reuse → Reuse → Reuse → Reindex. Full: 글로벌 KV/Indexer K 새로 생성, Top-K 새로 선택. Reuse: 앞 Full 레이어 KV와 선택 결과 모두 재사용. Reindex: KV는 재사용하되 표현이 많이 바뀌었으므로 Top-K 선택만 현재 레이어에서 재계산. 모든 모드에서 Main Q, SWA KV는 현 레이어에서 따로 계산(Full/Reindex는 indexer Q도).
- (b) 중학생: 반 전체 사진을 층마다 다시 찍지 않고 한 번 찍은 사진을 여러 층에서 돌려 쓰되, 몇 층 지나면 "누구를 볼지(Top-K)"만 다시 고르는 것.
- (c) 키워드: m=2, Full/Reuse/Reindex, Top-K=512, indexer K/Q. (CSA2의 풀네임은 슬라이드에 없음 — 논문 확인 필요.)
- (d) 페이지: 11.

### 7. FP4 글로벌 KV
- (a) 전공: CSA2가 "몇 개를 저장할지"를 줄인다면 FP4는 "엔트리당 몇 비트"를 줄인다. 글로벌 KV는 FP4, post-training 단계에서 quantization-aware training 적용. 양자화에 민감한 SWA KV는 FP8 유지. 글로벌 KV 890 bytes/token → 1M 토큰에 약 0.89GB.
- (b) 중학생: 메모를 깨알 글씨(4비트)로 쓰되, 틀리면 안 되는 최근 메모(SWA)는 조금 큰 글씨(8비트)로 쓴다.
- (c) 숫자: 890 B/token, 1,000,000 tokens ≈ 0.89 GB, FP4 vs FP8.
- (d) 페이지: 12.

### 8. Bounded Replay
- (a) 전공: CED로 글로벌 KV는 인코더에서 만들지만 디코더 SWA KV는 디코더 각 레이어 hidden state에 의존한다. SWA 윈도우 128이라도 깊은 레이어의 정확한 SWA 상태 복원에는 레이어 수만큼 의존 범위가 누적되어 약 20×128 토큰이 필요하다. Bounded Replay는 복원을 마지막 128 프롬프트 토큰만 디코더에 재생하는 것으로 제한해 근사 로컬 상태를 만든다(정확 복원 대신 bounded recomputation).
- (b) 중학생: 대화를 이어가려고 지난 대화 전체를 다시 읽는 대신 "마지막 몇 문장"만 다시 읽고 시작하는 것. 완벽하진 않지만 충분히 자연스럽다.
- (c) 숫자: 128 토큰 replay, 이론적 의존 범위 ≈ 20×128 = 2,560 토큰.
- (d) 페이지: 10, 13.

### 9. Perceiver — byte array M vs latent array N
- (a) 전공: 이미지·텍스트·3D 포인트클라우드를 한 구조로 다루려는 통합 모델. 입력(byte array)은 M개 인덱스 × C 채널(ImageNet 224×224×3이면 M=50,176, C=3). 입력에 PE를 더한 뒤, 하이퍼파라미터 크기 N×D의 **latent array**가 입력을 cross-attention으로 읽고(O(MN)), latent끼리 self-attention(O(N²))을 반복한다. 입력에 self-attention을 걸면 O(M²)라 불가능한 것을 latent로 우회. 마지막 latent를 pooling해 분류.
- (b) 중학생: 5만 장짜리 사진 뭉치를 전부 서로 비교하면 끝이 없으니, "메모장 N칸"이 사진 뭉치를 훑어 필요한 정보만 적고(cross-attention), 메모장끼리만 정리(self-attention)한다. 사진이 아무리 많아도 메모장 크기는 그대로다.
- (c) 수식: self-attn(byte) O(M²), self-attn(latent) O(N²), cross-attn O(MN). Query N, Key M → 출력 N.
- (d) 페이지: 15–22.

### 10. Perceiver IO / Graph Perceiver IO
- (a) 전공: Perceiver는 분류처럼 출력이 작을 때만 쓸 수 있다. Perceiver IO는 **출력 쿼리 배열(크기 M)**로 latent(N)를 cross-attention해(Query M, Key N → 출력 M) 분할(segmentation)처럼 입력 크기의 구조화된 출력을 만든다. 그러나 노드 간 관계(그래프)는 다루지 못해, Graph Perceiver IO가 관계 정보를 결합한다.
- (b) 중학생: 메모장(N)만 보고 "사진 한 장 전체 크기의 답(M)"을 다시 그려내려면, "질문 카드"를 사진 픽셀 수만큼 만들어 메모장에 물어보는 식이다.
- (c) 키워드: output query array, Query M/Key N/Attention ⇒ M, segmentation, graph relational information.
- (d) 페이지: 23–27.

---

## 요약본 정정

| 요약본 | 정정 | 근거 |
|---|---|---|
| "DeepSeek-V2 (Flash)" | **DeepSeek-V4.1-Flash** (논문: "DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression", arXiv 2026) | 2, 4–13p |
| "CID (Causal Encoder-Decoder)" | **CED** (Causal Encoder-Decoder) | 9–10p |
| "Single-Pass MHC" | **Single-Pass mHC** (Manifold-Constrained Hyper-Connections, 소문자 m) | 7–8p |
| "CID: 프롬프트는 인코더만 통과시켜 KV 캐시를 절반으로 줄임" | CED가 절반으로 줄이는 것은 **prefill 연산량**(N≫n_win일 때). 디코더 글로벌 KV를 인코더 hidden state에서 생성하는 구조. KV 캐시 크기 자체는 CSA2·FP4가 줄임 | 9–10p |
| "Engram: 바이그램·트라이그램 해시 외부 메모리, O(1) 조회" | PDF 표현은 "short local lexical patterns 자체를 memory address로 쓰는 massive learned dictionary". 해시/O(1)/N-gram 표현은 PDF에 없음(구두 설명 가능성) → 사이트에서는 "강의 설명" 표기 | 6p |
| "Engram: 별도 외부 메모리" | Engram 모듈은 레이어 1, 14(0-indexed)에 배치, 파라미터 196B(백본 552B와 별도) | 5–6p |
| "DSA (DeepSpeed Sparse Attention)" (2주차 맥락) | **DeepSeek Sparse Attention** (2주차 PDF 기준). 3주차 PDF에서는 DSA 용어 대신 CSA2(희소 선택 512 토큰) 사용 | 2주차 PDF, 5·11p |
| "여러 레이어에 걸쳐 KV 캐시 재사용(Reuse)·재인덱스(Re-index)" | 정확한 패턴: **Full → Reuse → Reuse → Reuse → Reindex**. Reindex는 KV 재사용 + Top-K 선택만 재계산 | 11p |
| "최근 128개 토큰 풀 어텐션 + 오래된 토큰은 압축/재사용 KV" | SWA 윈도우 128(첫 2개 레이어는 SWA만, 나머지는 CSA2+SWA). "최근 128만 full attention"이 아니라 **SWA(128) + 글로벌 희소 어텐션(Top-512) 병행** | 5p |
| (누락) | **FP4** 글로벌 KV(SWA KV는 FP8), 890 B/token, 1M 토큰 ≈ 0.89GB | 12p |
| (누락) | **Bounded Replay**: 마지막 128 토큰만 디코더 재생, 이론적 의존 범위 ≈ 20×128 | 10, 13p |
| (누락) | 구조 수치: 40 레이어(20E+20D), 8B/16B 활성 파라미터 | 5p |
| (누락) | **Perceiver / Perceiver IO / Graph Perceiver IO** 섹션 전체(14–27p) | 14–27p |
| "GPT-4, Claude 3 Opus 대등 벤치마크" | PDF에 벤치마크 표 없음. 사이트에 쓰려면 논문 확인 필요 | — |
| (요약본에만 있음) 벤치마크 vs 실사용, 오픈 웨이트 백도어, GPU 자원 논의 | PDF에 없음(토론 내용). "수업 토론" 섹션으로 분리 표기 권장 | — |

---

## 추천 인터랙션

### ★ 대표: "100만 토큰 KV 캐시 다이어트" 슬라이더
- 입력: 컨텍스트 길이 슬라이더(1K ~ 1M 토큰, 로그 스케일), 토글 5개를 순서대로 켜기 — ① FP16→FP4 ② CSA2 압축(m=2) ③ CSA2 cross-layer reuse(Full/Reuse/Reindex 패턴, 공유 그룹 5) ④ SWA 128 + Bounded Replay(SWA KV는 윈도우만 보관) ⑤ (비교용) GQA, MHA 기준선.
- 출력: 가로 막대 차트 — MHA 기준선 대비 각 단계의 글로벌 KV 메모리(GB). 최종 막대는 "890 B/token × N" 공식으로 계산해 1M에서 ≈0.89GB가 나오도록 캘리브레이션(기준선 수치는 가정값이라고 화면에 명시).
- 시각화: 막대가 토글마다 애니메이션으로 줄어듦. 막대 옆에 "노트북 메모리 16GB / GPU 80GB" 기준선 점선.
- 난이도: 중. 순수 JS로 계산식 + CSS transition이면 충분.
- 계산 가이드(단순 모델, 화면에 "교육용 근사"라고 표시): bytes/token = 2(K,V) × L_layers × H_kv × d_head × bits/8. 토글별로 bits 16→4, 엔트리 수 N→N/2, 레이어 수 L→L/5(공유 그룹), SWA는 min(N,128)만 FP8로 가산.

### 대안 A: CED prefill 시뮬레이터
- 입력: 프롬프트 길이 N 슬라이더, "CED 켜기" 토글.
- 출력: 40층 건물 그림. 끄면 N개 토큰이 40층 전부를 통과(연산 N×40), 켜면 20층만 통과 + 마지막 128 토큰만 디코더 20층 재생(Bounded Replay). 연산량 수식과 비율(→ 약 1/2) 표시.
- 난이도: 중. SVG rect 40개 + 토큰 점 이동 애니메이션.

### 대안 B: CSA2 레이어 모드 클릭 탐색기
- 입력: 5개 레이어 카드(Full, Reuse, Reuse, Reuse, Reindex) 클릭.
- 출력: 각 카드에서 "글로벌 KV: 새로 생성/재사용", "Top-K 선택: 새로/재사용/재계산", "현 레이어 계산: Main Q, SWA KV, (indexer Q)"가 색깔로 켜짐(11p 표 그대로).
- 난이도: 하. 표 데이터만 있으면 됨.

### 대안 C: Perceiver 복잡도 계산기
- 입력: M(입력 크기, 예: 224×224=50,176), N(latent 크기 슬라이더 128~1024).
- 출력: O(M²) vs O(MN)+O(N²) 숫자와 막대. M을 키워도 latent 비용이 거의 안 늘어나는 것을 체감.
- 난이도: 하.

---

## 다이어그램 후보

### D1. DeepSeek-V4.1-Flash 전체 구조 (5p 재구성)
- 세로 스택: 하단 "Encoder ×20" 박스, 상단 "Decoder ×20" 박스. 각 블록 내부에 "SWA(128)" + "CSA2 global(Top-512)" 두 어텐션 칩. 첫 2개 레이어 칩은 "SWA only"로 다른 색.
- 좌측 입력 화살표 "Prompt(prefill)" → Encoder만 통과 → "8B 활성". 우측 "Generated token" → Encoder → Decoder → "16B 활성".
- Encoder 최종 hidden state에서 Decoder 블록으로 가는 굵은 화살표 라벨 "CED: global K,V 생성 재료".
- 레이어 1, 14 옆에 "Engram(196B)" 사이드 박스. 하단 범례: 백본 552B.

### D2. KV 캐시 4대 압축 전략 맵 (4p)
- 가운데 "KV Cache" 큰 박스. 네 방향 화살표: ① "엔트리 크기 ↓ → FP4" ② "엔트리 수 ↓ → CSA2 compression (m=2)" ③ "레이어별 중복 ↓ → cross-layer reuse (Full/Reuse/Reindex)" ④ "보관 기간 ↓ → Bounded Replay(128)". 각 화살표 끝에 결과 수치 칩 "890 B/token, 1M → 0.89GB".

### D3. Perceiver vs Perceiver IO 흐름 (19p, 24p)
- 좌: "Byte array M×C"(큰 직사각형) → cross-attention(O(MN)) → "Latent array N×D"(작은 직사각형) → self-attention(O(N²)) ×L → pooling → "classification".
- 우(Perceiver IO): latent → cross-attention(Query M, Key N) ← "Output query array M" → "Output array M (segmentation)". 하단 주석: "self-attn on byte array = O(M²) ✗".

---

## 모델 비교 포인트

| 개념 | 수업에서 다룬 모델·방식 | Claude (공개 문서 범위) | 기타 모델 | 출처 후보 |
|---|---|---|---|---|
| 컨텍스트 길이 | V4.1-Flash: 1M 토큰 KV를 0.89GB로 (논문 수치) | Claude 모델은 200K 컨텍스트가 기본, 일부 모델에서 1M 컨텍스트 제공(Anthropic 공식 문서 기준). 내부 KV 캐시 기법은 **비공개** | Gemini: 1M+ 컨텍스트 공개 (확인 필요: 최신 모델별 수치) | Anthropic docs "Models overview", Google Gemini 문서 |
| prefix/prompt 재사용 | CED(인코더 hidden state 재사용), CSA2 cross-layer reuse | Anthropic API의 **Prompt Caching**(동일 prefix의 처리 결과를 캐시해 비용·지연 절감)은 공개 기능. 캐시 내부 표현(KV인지 여부)은 비공개 | OpenAI, Gemini도 prompt/context caching 제공 (확인 필요) | Anthropic docs "Prompt caching" |
| KV 양자화(FP4/FP8) | 글로벌 KV FP4, SWA KV FP8, QAT | 비공개 | 오픈 모델 추론 엔진(vLLM 등)의 FP8 KV cache 옵션은 공개 (확인 필요: 지원 범위) | vLLM 문서 |
| 어텐션 구조(SWA + 희소 글로벌) | SWA 128 + Top-512 희소, 첫 2레이어 SWA만 | 비공개 | Gemma 2/3: 로컬 SWA 레이어와 글로벌 레이어 교차 배치(공개), Mistral 7B: SWA 4096(공개) (확인 필요: 각 윈도우 크기) | Gemma/Mistral 논문·모델카드 |
| 인코더-디코더 분리(CED) | 20 causal encoder + 20 causal decoder | 비공개 | 대부분의 공개 LLM은 decoder-only. T5 계열은 전통적 encoder-decoder(비인과 인코더)로 CED와 다름 | T5 논문 |
| 외부 메모리/사전(Engram) | 196B 학습 사전, 레이어 1·14 | 비공개 | (확인 필요) | — |
| Residual 확장(mHC) | n개 residual stream, doubly stochastic 제약 | 비공개 | (확인 필요: Hyper-Connections 원논문 모델) | HC/mHC 논문 |
| 모달리티 통합 (Perceiver) | latent array로 O(MN) | Claude는 이미지·PDF 입력을 지원(공개). 내부 비전 인코더 구조 **비공개** | Perceiver/Perceiver IO는 DeepMind(Google) 공개 연구; Flamingo의 Perceiver Resampler가 유사 아이디어 (확인 필요) | Jaegle et al. 2021 |
| 수업 토론: 벤치마크 vs 실사용, 오픈 웨이트 백도어 | DeepSeek 오픈 웨이트 | Claude는 closed weights(API 제공). Anthropic은 system card·safety 평가 공개 | Llama/Qwen/DeepSeek 오픈 웨이트 | Anthropic system cards |

> 원칙: Claude·GPT 열은 공식 문서/시스템 카드/논문에 있는 것만 적고, 아키텍처 내부는 전부 "비공개"로 둔다. "확인 필요" 항목은 페이지 작성 시 출처 링크를 달아야 공개한다.

---

## 시험 포인트

1. V4.1-Flash의 KV 캐시 압축 4대 전략과 각 담당 기술(FP4 / CSA2 compression / CSA2 cross-layer reuse / Bounded Replay)을 매칭할 수 있어야 한다.
2. 구조 수치: 40=20E+20D, 552B 백본 + 196B Engram, 8B(prefill)/16B(decode) 활성, SWA 128, Top-512.
3. CED의 핵심: 디코더 글로벌 K,V를 **인코더 최종 hidden state**에서 생성(인코더 K,V 직접 재사용 아님) → 긴 입력의 prefill은 인코더 20층만 → 연산 ≈ 1/2.
4. CED가 못 없애는 것: 디코더 SWA KV → Bounded Replay(마지막 128 토큰만 재생, 이론 의존 범위 20×128).
5. CSA2 레이어 패턴 Full → Reuse×3 → Reindex, 각 모드에서 무엇을 새로 만들고 무엇을 재사용하는지(11p 표).
6. FP4는 글로벌 KV만, SWA KV는 FP8(양자화 민감). 890 B/token → 1M ≈ 0.89GB.
7. mHC: 다중 residual stream + doubly stochastic 제약으로 안정성.
8. Perceiver: byte M vs latent N, O(M²)→O(MN)+O(N²); Perceiver IO는 출력 쿼리 M으로 구조화 출력; Graph Perceiver IO는 관계 정보.

### 예상 문제
1. **(단답)** DeepSeek-V4.1-Flash에서 글로벌 KV 캐시 엔트리 수를 줄이는 기술과 엔트리당 비트 수를 줄이는 기술을 각각 쓰시오.
   정답: 엔트리 수 ↓ = CSA2 compression(m=2), 비트 수 ↓ = FP4 양자화(QAT). 해설: 4p의 ①②, 11–12p.
2. **(서술)** CED(Causal Encoder-Decoder)가 prefill 연산을 절반으로 줄이는 원리를 설명하고, 그럼에도 Bounded Replay가 필요한 이유를 쓰시오.
   정답: 디코더 각 레이어의 글로벌 K,V를 인코더 최종 hidden state로부터 생성하므로 긴 입력은 인코더 20층만 통과하면 된다(N≫n_win일 때 ≈1/2). 그러나 디코더의 SWA(로컬) KV는 디코더 레이어별 hidden state에 의존하므로, 마지막 128 토큰만 디코더에 재생해 근사 로컬 상태를 만든다.
3. **(계산)** 글로벌 KV 캐시가 토큰당 890바이트일 때 1,000,000 토큰의 글로벌 KV 캐시 크기는? SWA KV가 FP8로 남는 이유도 쓰시오.
   정답: ≈ 0.89GB. SWA KV는 양자화에 더 민감하므로 FP8 유지.
4. **(객관식)** CSA2 레이어 패턴에서 "Reindex" 레이어가 하는 일로 옳은 것은?
   ① 글로벌 KV와 Top-K 선택을 모두 새로 계산 ② 글로벌 KV는 앞 Full 레이어 것을 재사용하고 Top-K 선택만 현재 레이어에서 재계산 ③ 모두 재사용 ④ SWA KV만 재사용
   정답: ②. 해설: ①은 Full, ③은 Reuse.
5. **(서술)** Perceiver가 224×224×3 이미지(M=50,176)에 self-attention을 직접 적용하지 않는 이유와, latent array(N)를 도입했을 때의 복잡도를 쓰시오. Perceiver IO는 무엇을 추가했는가?
   정답: 직접 self-attention은 O(M²)로 과도. latent N을 두어 cross-attention O(MN) + latent self-attention O(N²)로 줄임(M이 커져도 latent 비용 불변). Perceiver IO는 출력 쿼리 배열(크기 M)로 latent를 cross-attention(Query M, Key N → 출력 M)해 분할 같은 구조화된 출력을 가능하게 함.

---

## 출처
- DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression [arXiv 2026] (4–13p 전체 source 라인)
- Jaegle, Andrew, et al. "Perceiver: General perception with iterative attention." ICML 2021 (PMLR). (15–22p)
- Jaegle, Andrew, et al. "Perceiver IO: A general architecture for structured inputs & outputs." arXiv:2107.14795 (2021). (23–26p)
- Bae, Seyun, et al. "Graph Perceiver IO: A general architecture for graph structured data." arXiv:2209.06418 (2022). (27p)
- 강의: 최신딥러닝이론및응용 Week 3-1 "Foundation Models II", Kyungwoo Song (송경우), Yonsei University, https://mlai.yonsei.ac.kr/
- 목차에만 있고 이 PDF에 없는 항목(3-2 추정): Mamba/Mamba-2/Mamba-3, DeltaNet/GDN/KDA/GDN-2, Kimi Linear, Qwen3.8-Flash-Next, Nvidia Nemotron, PuRo-2B.

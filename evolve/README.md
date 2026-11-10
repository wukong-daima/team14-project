# evolve — EvoLecture 자가 진화 루프

설계는 `PLAN.md` 3절. 여기는 실행법.

```
evolve/common.py       문제 은행 로드 · 페이지 텍스트(예상 문제 제거) · Claude 래퍼(비용 상한, mock)
evolve/solve.py        풀이자 실행 (조건 none/brief/page, k 반복, effort)
evolve/diagnose.py     오답 몰린 개념 · 미검증 주장 · 패치 대상 카드
evolve/propose.py      보강 설명 제안(전공/쉬운 두 벌 + 출처) → 카드에 삽입
evolve/verify.py       유출(문제 문장 베끼기) 검사 · HTML 짝 검사 · R 계산
evolve/round.py        한 라운드 오케스트레이션 → evolve/reports/round-NN.json (→ PR)
evolve/experiments.py  행동 실험 E1(effort) · E2(pass@k) · E3(하네스 효과)
```

## 준비

```bash
python3 -m venv .venv && .venv/bin/pip install anthropic
export ANTHROPIC_API_KEY=...            # 또는 ant auth login
# 비공개 세트(선택): git clone https://github.com/wukong-daima/team14-heldout.git _heldout
export HELDOUT_DIR=$PWD/_heldout/heldout
```

## 실행

```bash
# API 없이 파이프라인만 확인 (가짜 풀이자, 정답률은 의미 없음)
.venv/bin/python evolve/round.py --weeks week09 --mock

# 실제 1라운드 (풀이자 haiku, 제안자 opus, 상한 $5)
.venv/bin/python evolve/round.py --weeks week02,week04,week08

# 통과한 패치를 브랜치 + PR 로
.venv/bin/python evolve/round.py --weeks week02,week04,week08 --pr

# 행동 실험
.venv/bin/python evolve/experiments.py e3 --weeks week02,week04,week08
.venv/bin/python evolve/experiments.py e2 --weeks week09 --k 10
.venv/bin/python evolve/experiments.py e1 --weeks week04
```

환경 변수: `EVOLVE_WEAK_MODEL`(기본 claude-haiku-5-5), `EVOLVE_STRONG_MODEL`(기본 claude-opus-5-5), `EVOLVE_MAX_USD`(기본 5).

## 보상과 분해

- `R = 0.6 · Acc_public + 0.4 · SourcePass` (verify.py). `SourcePass` 는 비교표 배지 집계(`src` 통과 / `check` 미판정)로 근사.
- 라운드 리포트의 `decomposition`: `Δ공개`, `Δ비공개`, `O = Δ공개 − Δ비공개`, `T`(이 설계에서는 호출 수 동일 → 0; 호출 수 효과는 E1·E2 로 별도 측정), `G = Δ − O − T`.
- 비공개 세트가 없으면 O·G 는 `null` 로 남는다. **비공개 세트 없이는 "개선"을 주장하지 않는다.**

## 유출 방지 (리워드 해킹 차단)

1. 풀이자에게 주는 페이지 텍스트에서 `section.exam`, `details.quiz` 를 제거한다.
2. 제안자는 문제를 보지 않는다. 약한 **개념 이름**과 브리프·페이지 본문만 본다.
3. 패치 문장이 공개 문제 문장·보기와 25자 이상(또는 60%) 겹치면 라운드를 기각한다.
4. 비공개 세트 점수가 공개 세트만큼 오르지 않으면 O 로 드러난다.

## GitHub Actions

`.github/workflows/evolve.yml` — 매주 일요일 18:00 UTC(월 03:00 KST) + 수동 실행. 시크릿: `ANTHROPIC_API_KEY`(필수), `HELDOUT_TOKEN`(비공개 저장소 읽기용 PAT, 선택). 결과는 `evolve/round-NN` 브랜치의 PR 로만 올라간다.

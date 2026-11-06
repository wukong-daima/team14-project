---
name: quiz-forge
description: "주차 강의 자료(content/briefs/weekNN.md 등)로 퀴즈 문제 은행(assets/data/quiz/weekNN-agent.json)을 만들고 검증한다. '문제 만들어줘', '퀴즈 출제', 'N주차 문제 은행', '출제 에이전트 돌려줘', '문제 다시 검증', '떨어진 문제만 다시', '출제 결과 개선' 같은 요청에 사용한다. 주차 페이지(weeks/weekNN.html) 자체를 만드는 작업이나 퀴즈 페이지 UI 수정에는 쓰지 않는다."
---

# quiz-forge — 수업 자료로 검증된 퀴즈 문제 만들기

9주차 수업 내용을 그대로 설계에 옮긴 출제 하네스다. 만든 문제를 믿을 수 있게 하는 장치가 핵심이다.

| 수업 내용 | 이 하네스의 장치 |
|---|---|
| Autodata agent: Challenger · Weak/Strong Solver · Judge (8주차 p.27) | 출제자 · 약한/강한 풀이자 · 검증자 |
| 다양성 붕괴 → MAP-Elites로 칸을 나눠 생성 (9주차) | 개념 × 유형 × 난이도 격자를 코드로 먼저 정함 |
| pass@k가 낮으면 문제가 망가진 것 (9주차) | 강한 풀이자 k번 중 정답 수로 결함 판정 |
| 기계 채점 가능한 문제 우선 (9주차) | 객관식·숫자 문제 위주, 숫자는 계산식을 코드로 재계산 |
| 실패 사례 20~50개부터 모아라 (9주차) | `references/failure-cases.md`가 검증 기준 |
| 리워드 해킹: 항상 같은 번호가 정답 (8주차) | 정답 위치를 코드로 고르게 재배치, 보기 길이 편향 검사 |
| 실제 사용자가 검증 (9주차) | 마지막은 사람이 검토하고 PR |

## 실행 모드

- **서브에이전트 위임 + 스크립트.** 단계 순서와 반복 조건은 이 문서가 정하고, 결정적 작업(격자 계획, 채점, 정답 위치 재배치, 중복·계산 검사, 조립)은 `scripts/forge.py`가 한다. 판단이 필요한 일만 에이전트에 맡긴다.
- `Workflow` 도구는 사용자가 명시적으로 요청할 때만 쓴다. 단계는 같다.
- 사용자 정의 에이전트(`.claude/agents/quiz-*.md`)는 이 저장소를 연 세션에서 `subagent_type`으로 부른다. 다른 폴더의 세션이면 `general-purpose`에 `model`을 지정하고 프롬프트 첫 줄에 "`.claude/agents/quiz-XXX.md`를 읽고 그 역할로 일하라"를 넣는다.

## 데이터 전달

모든 중간 산출물은 `_workspace/quiz/weekNN/`에 파일로 둔다(저장소에 커밋하지 않음). 이름 규칙은 `{단계}_{역할}_{내용}.json`.

| 단계 | 파일 | 만든 쪽 |
|---|---|---|
| 1 | `01_mapper_concepts.json` | quiz-mapper |
| 2 | `02_plan.json` | forge.py plan |
| 3 | `03_writer_batchN.json` → `03_candidates.json` | quiz-writer (병렬) → forge.py merge |
| 4 | `04_check.json`, `04_pack.json`(정답 뺀 문제지) | forge.py check / pack |
| 5 | `05_weak_runN.json`, `05_strong_runN.json` | quiz-solver-weak / quiz-solver-strong (병렬) |
| 6 | `06_scores.json` | forge.py score |
| 7 | `07_verifier_batchN.json` | quiz-verifier (병렬) |
| 8 | `08_writer_repair.json` | quiz-writer (떨어진 문제만) |
| 9 | `assets/data/quiz/weekNN-agent.json`, `assets/data/quiz/reports/weekNN-agent.report.json` | forge.py assemble |

JSON 형식은 `references/schemas.md`를 따른다.

## 절차

### 0단계: 상태 확인
- `_workspace/quiz/weekNN/`이 없으면 처음부터 한다.
- 있고 "떨어진 문제만 다시" 같은 요청이면 6~9단계만 다시 한다.
- 새 자료로 다시 만들면 기존 폴더를 `weekNN_YYYYMMDD-HHMM`으로 옮긴다.

### 1단계: 개념 지도 (quiz-mapper, sonnet)
입력: `content/briefs/weekNN.md`(주 자료)와 브리프가 가리키는 다른 브리프의 해당 절. 강의 PDF 텍스트가 `_workspace/quiz/sources/`에 있으면 함께 읽는다. 출력: 개념 10~15개, 개념마다 근거 문장 인용과 출처 위치, 출제 가능한 유형.

### 2단계: 출제 격자 (스크립트)
```bash
python .claude/skills/quiz-forge/scripts/forge.py plan --week weekNN --target 30
```
개념마다 유형(mc/num/self)과 난이도(1~3)를 배정한다. 목표 비율은 객관식 50%, 숫자 20%(숫자로 물을 수 있는 개념만), 서술형 30%. 한 개념에 칸이 몰리지 않게 한다.

### 3단계: 출제 (quiz-writer, opus, 칸을 3묶음으로 나눠 병렬)
각 칸에 문제 하나. 규칙은 `references/question-rules.md`. 끝나면:
```bash
python .claude/skills/quiz-forge/scripts/forge.py merge --week weekNN
```

### 4단계: 기계 검사 (스크립트)
```bash
python .claude/skills/quiz-forge/scripts/forge.py check --week weekNN
python .claude/skills/quiz-forge/scripts/forge.py pack --week weekNN
```
형식, 숫자 재계산, 정답 위치 재배치, 보기 길이 편향, 문제 속 정답 노출, 기존 문제와의 중복을 본다. `pack`은 정답을 뺀 문제지를 만든다.

### 5단계: 풀이 시험 (k = 3, 6개 호출을 한 메시지에서 병렬)
- quiz-solver-weak(haiku) × 3: **자료 없이** 문제지만 보고 푼다.
- quiz-solver-strong(sonnet) × 3: 문제지와 1단계 근거 자료를 보고 푼다.
- 서술형은 풀이 시험에서 빠진다(기계 채점이 안 되므로 7단계 검증자가 판정).
```bash
python .claude/skills/quiz-forge/scripts/forge.py score --week weekNN
```
판정: 강한 풀이자 3번 중 0번 정답 → `broken`(문제 결함), 1번 → `shaky`, 2번 이상 → 통과. 약한 풀이자 3번 모두 정답 → `too_easy`(난이도 1이면 허용).
`too_easy`는 1라운드에서는 수정 대상이다. 수정 라운드 뒤에도 `too_easy`이면 검증자가 원인을 가른다: 소거·흘림(F20~F22)이면 버리고, 일반 ML 지식으로 풀리지만 결함이 없으면 **기초 문제**(난이도 1, `basic: true`)로 남긴다. 약한 풀이자(haiku)는 일반 ML 지식이 있어 강의를 안 들은 사람보다 강하기 때문이다(9주차 시범 운영에서 정함).

### 6단계: 검증 (quiz-verifier, opus, 2묶음 병렬)
모든 문제를 `references/failure-cases.md` 기준으로 본다. 6단계 점수를 함께 넘긴다. 판정은 `pass` / `fix`(무엇을 고칠지) / `drop`.

### 7단계: 수정 (quiz-writer, 떨어진 문제만 한 번)
```bash
python .claude/skills/quiz-forge/scripts/forge.py repairs --week weekNN   # → r2/08_repair_request.json
```
수정본은 `r2/08_writer_repairN.json`. 이후 `merge/check/pack/score --round 2`, 검증 결과는 `r2/07_verifier_batchN.json`. 2라운드 검증자는 `fix` 없이 `pass`/`drop`만 쓴다.
`fix`와 `broken`, `shaky` 문제를 사유와 함께 넘겨 고친다. 고친 문제는 4~6단계를 한 번 더 거친다. 두 번째도 떨어지면 버린다. 수정 루프는 최대 1회(비용 상한).

### 8단계: 조립 (스크립트)
```bash
python .claude/skills/quiz-forge/scripts/forge.py assemble --week weekNN
```
통과한 문제만 `assets/data/quiz/weekNN-agent.json`에 쓰고 `index.json`에 등록한다. 보고서에는 생성 수, 통과 수, 버린 이유, 격자 커버리지, 정답 위치 분포를 남긴다.

### 9단계: 사람 검토
보고서와 문제를 사람이 원본과 대조한다. 고친 내용과 버린 문제는 `references/failure-cases.md`에 사례로 추가한다(다음 실행의 기준이 된다). PR은 사람이 올린다.

## 오류 처리
- 에이전트 호출이 실패하면 한 번 다시 한다. 또 실패하면 그 묶음 없이 진행하고 보고서의 `missing`에 적는다.
- 사용량 한도·인증 오류는 다시 시도하지 않는다. 어디까지 됐는지 `_workspace`를 확인해 보고한다.
- 에이전트가 형식에 안 맞는 JSON을 내면 `forge.py`가 그 문제를 `format_error`로 떨어뜨린다. 오케스트레이터가 대신 고쳐 쓰지 않는다.

## 테스트 시나리오
- **정상:** "9주차 문제 만들어줘" → 1~8단계 → `week09-agent.json`에 20개 안팎, 보고서 생성.
- **오류:** 강한 풀이자 3번 모두 틀린 문제 → `broken` → 7단계 수정 → 다시 실패하면 `drop`, 보고서에 사유.
- **후속:** "떨어진 문제만 다시" → 0단계에서 기존 폴더 확인 → 7~8단계만.

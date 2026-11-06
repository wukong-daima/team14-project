# quiz-forge 중간 산출물 형식

모든 파일은 UTF-8 JSON. 문자열 안의 줄바꿈은 `\n`.

## 01_mapper_concepts.json
```json
{
  "week": "week09",
  "sources": ["content/briefs/week09.md", "content/briefs/week08.md#개념 12"],
  "concepts": [
    {
      "key": "pass-at-k",
      "name": "pass@k와 pass^k",
      "summary": "두세 문장 요약",
      "evidence": [{"quote": "원문 그대로 인용 (40~200자)", "where": "week09.md 개념 12 / p.86"}],
      "types": ["mc", "num", "self"],
      "numeric_ok": true,
      "weight": 2
    }
  ]
}
```
- `types`: 이 개념으로 낼 수 있는 유형. `num`은 정답이 숫자 하나로 떨어지는 계산이 원문에 있을 때만.
- `weight`: 1~3. 시험 포인트에 직접 나오면 3.

## 02_plan.json (forge.py plan)
```json
{"week": "week09", "cells": [{"cell": "c01", "concept": "pass-at-k", "type": "num", "difficulty": 2}]}
```

## 03_writer_batchN.json (quiz-writer)
```json
{"questions": [
  {
    "cell": "c01", "concept": "pass-at-k", "type": "mc", "difficulty": 2,
    "q": "문제 문장",
    "options": ["보기1", "보기2", "보기3", "보기4"],
    "answer": 1,
    "calc": null,
    "explanation": "해설",
    "rubric": null,
    "evidence": [{"quote": "근거 원문", "where": "week09.md 개념 12"}]
  }
]}
```
- `mc`: `options` 4개, `answer`는 0부터 센 번호.
- `num`: `answer`는 숫자, `calc`는 파이썬 산술식 문자열(예: `"1-(1-0.1)**10"`), `tol` 선택.
- `self`: `answer`는 모범 답안, `rubric`은 채점 핵심어 2~4개 배열.

## 04_pack.json (forge.py pack) — 풀이자에게 주는 문제지
```json
{"questions": [{"id": "w09a-c01", "type": "mc", "q": "...", "options": ["..."]}]}
```

## 05_*_runN.json (quiz-solver-*)
```json
{"run": "strong-1", "answers": [{"id": "w09a-c01", "choice": 2}, {"id": "w09a-c05", "value": 0.651}]}
```
`choice`는 0부터 센 번호. 모르겠으면 그래도 하나를 고른다(빈칸 금지).

## 07_verifier_batchN.json (quiz-verifier)
```json
{"reviews": [
  {"id": "w09a-c01", "verdict": "pass", "grounded": true, "issues": [], "note": "", "fix": ""}
]}
```
- `verdict`: `pass` · `fix` · `drop`
- `issues`: `references/failure-cases.md`의 코드(F01 등)
- `fix`: `fix`일 때 무엇을 어떻게 고칠지 한두 문장

## 08_writer_repair.json (quiz-writer)
03과 같은 형식. 각 문제에 원래 `cell`을 그대로 쓴다.

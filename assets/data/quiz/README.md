# 퀴즈 문제 은행

`quiz/index.html`은 문제를 두 곳에서 모읍니다.

1. **주차 페이지의 예상 문제**: `weeks/weekNN.html`의 `<details class="quiz">`. 페이지를 고치면 자동으로 반영됩니다.
   - 문제에 `(객관식)`이 있고 보기가 `① … ② …` 형식이며 정답이 `②.`처럼 원문자로 시작하면 자동 채점됩니다.
   - 나머지는 서술형으로 보고 정답을 보여준 뒤 스스로 채점합니다.
2. **이 폴더의 문제 은행 JSON**: 페이지에 넣기 전의 추가 문제, 문제 출제 에이전트가 만든 문제를 넣는 곳입니다.
   `index.json`의 `banks`에 파일 이름을 적어야 불러옵니다.

## JSON 형식

```json
{
  "week": "week09",
  "source": "brief",
  "generated": "2026-11-06",
  "questions": [
    {
      "id": "w09-passk-01",
      "type": "num",
      "q": "한 번 성공 확률 p = 0.1일 때 pass@10은? (소수 셋째 자리까지)",
      "answer": 0.651,
      "tol": 0.002,
      "explanation": "pass@k = 1 − (1 − p)^k = 1 − 0.9^10 ≈ 0.651",
      "concept": "pass@k",
      "refs": ["week5_self_evolving_agent.pdf p.86", "노션 #09 Q&A"]
    }
  ]
}
```

| 필드 | 필수 | 설명 |
|---|---|---|
| `week` | 예 | `assets/js/weeks.js`의 주차 id |
| `source` | 아니오 | `brief`, `agent`, `manual` 등 출처 |
| `questions[].id` | 아니오 | 고정 id. 없으면 문제 문장으로 만듭니다. **문장을 고치면 기록이 끊기므로** 에이전트 출력에는 넣는 것을 권장 |
| `questions[].type` | 예 | `mc`(객관식) · `num`(숫자 답) · `self`(서술형, 스스로 채점) |
| `questions[].q` | 예 | 문제 문장 (일반 텍스트, HTML 쓰지 않음) |
| `questions[].options` | `mc`만 | 보기 문자열 배열 (2~6개) |
| `questions[].answer` | 예 | `mc`: 정답 보기의 0부터 센 번호 · `num`: 숫자 · `self`: 모범 답안 문자열 |
| `questions[].tol` | 아니오 | `num`의 허용 오차. 없으면 정답의 1% |
| `questions[].unit` | 아니오 | `num`의 단위 표시 |
| `questions[].explanation` | 아니오 | 해설 (`mc`, `num`에서 채점 뒤 표시) |
| `questions[].concept`, `refs` | 아니오 | 개념 이름, 근거(PDF 페이지·노션) |

같은 id의 문제가 여러 곳에 있으면 먼저 불러온 하나만 씁니다. 문제 문장은 HTML이 아닌 텍스트로 표시합니다.

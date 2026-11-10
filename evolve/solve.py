"""풀이자 실행: 조건(none/brief/page)별로 문제 은행을 풀고 정답률을 잰다.

사용:
  python evolve/solve.py --weeks week02,week04 --condition page --k 1 --out evolve/runs/base.json
  python evolve/solve.py --bank heldout --condition page            # HELDOUT_DIR 필요
  python evolve/solve.py --mock ...                                  # API 없이 파이프라인 검증
행동 실험:
  E3 하네스 효과  : --condition none / brief / page 를 각각 실행
  E2 pass@k      : --k 10
  E1 테스트타임  : --effort low / medium / high / xhigh
"""
from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path

from common import LLM, RUN_DIR, WEAK_MODEL, context_for, jdump, load_bank, log

SYSTEM = (
    "당신은 '최신딥러닝이론및응용' 수업 시험을 보는 수강생입니다. "
    "주어진 참고 자료가 있으면 그것을 근거로, 없으면 아는 대로 답하세요. "
    "반드시 마지막 줄에 'ANSWER: <값>' 형식으로만 최종 답을 쓰세요. "
    "객관식은 보기 번호(1부터), 숫자 문제는 숫자만 씁니다. 모르면 그래도 하나를 고릅니다."
)


def fmt_question(q: dict) -> str:
    s = q["q"].strip()
    if q["type"] == "mc":
        s += "\n" + "\n".join(f"{i+1}. {o}" for i, o in enumerate(q["options"]))
        s += "\n(객관식: 보기 번호로 답)"
    else:
        s += "\n(숫자로 답)"
    return s


ANS_RE = re.compile(r"ANSWER\s*[:：]\s*([-+]?\d+(?:[.,]\d+)?)", re.I)


def parse_answer(text: str, q: dict):
    m = ANS_RE.findall(text or "")
    if not m:
        return None
    raw = m[-1].replace(",", "")
    try:
        v = float(raw)
    except ValueError:
        return None
    return int(v) - 1 if q["type"] == "mc" else v


def is_correct(q: dict, pred) -> bool:
    if pred is None:
        return False
    if q["type"] == "mc":
        return int(pred) == int(q["answer"])
    tol = float(q.get("tol", 0) or 0)
    ans = float(q["answer"])
    tol = max(tol, abs(ans) * 0.01)  # 기본 1% 허용
    return abs(float(pred) - ans) <= tol


def run(args, llm: LLM | None = None, html_override: dict | None = None, patched: bool = False) -> dict:
    weeks = args.weeks.split(",") if args.weeks else None
    bank = load_bank(args.bank, weeks)
    if args.limit:
        bank = bank[: args.limit]
    if not bank:
        raise SystemExit(f"문제가 없습니다: bank={args.bank} weeks={weeks} (HELDOUT_DIR 확인)")
    llm = llm or LLM(mock=args.mock)
    ctx_cache: dict[str, str] = {}
    results = []
    t0 = time.time()
    for q in bank:
        wk = q["week"]
        if wk not in ctx_cache:
            ctx_cache[wk] = context_for(wk, args.condition, (html_override or {}).get(wk))
        ctx = ctx_cache[wk]
        user = (f"[참고 자료: {wk}]\n{ctx}\n\n" if ctx else "") + "[문제]\n" + fmt_question(q)
        attempts = []
        for i in range(args.k):
            text = llm.ask(args.model, SYSTEM, user, effort=args.effort,
                           mock_hint={"kind": "solve", "condition": args.condition, "q": q, "patched": patched})
            pred = parse_answer(text, q)
            attempts.append({"pred": pred, "correct": is_correct(q, pred)})
        n_ok = sum(a["correct"] for a in attempts)
        results.append({
            "id": q["id"], "week": wk, "type": q["type"], "concept": q.get("concept", ""),
            "attempts": attempts, "n_correct": n_ok, "k": args.k,
            "pass_at_k": n_ok > 0, "pass_hat_k": n_ok == args.k, "acc": n_ok / args.k,
        })
        log(f"  {q['id']:>14} {q['type']} {'✓' if n_ok == args.k else ('~' if n_ok else '✗')} {n_ok}/{args.k}")
    n = len(results)
    summary = {
        "bank": args.bank, "condition": args.condition, "model": args.model, "effort": args.effort, "k": args.k,
        "weeks": sorted({r["week"] for r in results}), "n": n,
        "acc": round(sum(r["acc"] for r in results) / n, 4),
        "pass_at_k": round(sum(r["pass_at_k"] for r in results) / n, 4),
        "pass_hat_k": round(sum(r["pass_hat_k"] for r in results) / n, 4),
        "by_week": {w: round(sum(r["acc"] for r in results if r["week"] == w) / max(1, sum(1 for r in results if r["week"] == w)), 4) for w in sorted({r["week"] for r in results})},
        "mock": args.mock, "elapsed_s": round(time.time() - t0, 1), "usage": llm.usage.to_dict(),
    }
    out = {"summary": summary, "results": results}
    if args.out:
        jdump(out, Path(args.out))
        log(f"→ {args.out}")
    log(f"acc={summary['acc']} pass@{args.k}={summary['pass_at_k']} pass^{args.k}={summary['pass_hat_k']} n={n} ${summary['usage']['usd']}")
    return out


def build_parser():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bank", default="public", choices=["public", "heldout"])
    ap.add_argument("--weeks", default="", help="week02,week04 (비우면 전체)")
    ap.add_argument("--condition", default="page", choices=["none", "brief", "page"])
    ap.add_argument("--k", type=int, default=1)
    ap.add_argument("--model", default=WEAK_MODEL)
    ap.add_argument("--effort", default="low", choices=["low", "medium", "high", "xhigh", "max"])
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", default="")
    ap.add_argument("--mock", action="store_true")
    return ap


if __name__ == "__main__":
    run(build_parser().parse_args())

"""행동 실험 E1·E2·E3 (PLAN.md 3.4). 결과는 evolve/reports/exp-*.json.

  python evolve/experiments.py e3 --weeks week02,week04,week08      # 자료 없음/브리프/페이지
  python evolve/experiments.py e2 --weeks week09 --k 10              # pass@k vs pass^k
  python evolve/experiments.py e1 --weeks week04                     # effort low→xhigh (테스트타임 스케일링)
  --mock 으로 API 없이 형식 확인
"""
from __future__ import annotations

import argparse
import time
from types import SimpleNamespace

from common import BACKEND, CLI_ISOLATION, LLM, REPORT_DIR, WEAK_MODEL, jdump, log, update_report_index
from solve import run as solve_run


def ns(**kw):
    base = dict(bank="public", weeks="", condition="page", k=1, model=WEAK_MODEL, effort="low", limit=0, out="", mock=False)
    base.update(kw)
    return SimpleNamespace(**base)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("exp", choices=["e1", "e2", "e3"])
    ap.add_argument("--weeks", required=True)
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--model", default=WEAK_MODEL)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()
    llm = LLM(mock=a.mock)
    out = {"exp": a.exp, "weeks": a.weeks, "model": a.model, "mock": a.mock, "date": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "backend": "mock" if a.mock else BACKEND, "cli_isolation": " ".join(CLI_ISOLATION) if BACKEND == "claude-cli" and not a.mock else None, "runs": []}
    if a.exp == "e3":
        for cond in ("none", "brief", "page"):
            r = solve_run(ns(weeks=a.weeks, condition=cond, model=a.model, limit=a.limit, mock=a.mock), llm)
            out["runs"].append({"condition": cond, **r["summary"]})
    elif a.exp == "e2":
        r = solve_run(ns(weeks=a.weeks, k=a.k, model=a.model, limit=a.limit, mock=a.mock), llm)
        out["runs"].append(r["summary"])
        out["suspect_broken"] = [x["id"] for x in r["results"] if x["n_correct"] == 0]
        out["too_easy"] = [x["id"] for x in r["results"] if x["n_correct"] == a.k]
    else:
        for eff in ("low", "medium", "high", "xhigh"):
            r = solve_run(ns(weeks=a.weeks, effort=eff, model=a.model, limit=a.limit, mock=a.mock), llm)
            out["runs"].append({"effort": eff, **r["summary"]})
    out["usage"] = llm.usage.to_dict()
    p = REPORT_DIR / f"exp-{a.exp}-{a.weeks.replace(',', '_')}{'-mock' if a.mock else ''}.json"
    jdump(out, p)
    update_report_index()
    log(f"→ {p}")


if __name__ == "__main__":
    main()

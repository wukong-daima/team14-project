"""진단: 풀이 결과에서 오답이 몰린 개념과, 페이지의 미검증 주장(확인 필요 배지)을 뽑는다.

  python evolve/diagnose.py --run evolve/runs/base.json --out evolve/runs/diag.json
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

from common import WEEK_DIR, jdump, log


def concept_table(run: dict) -> list[dict]:
    agg = defaultdict(lambda: {"n": 0, "correct": 0.0, "ids": []})
    for r in run["results"]:
        key = (r["week"], r.get("concept") or "(미분류)")
        a = agg[key]
        a["n"] += 1
        a["correct"] += r["acc"]
        a["ids"].append(r["id"])
    rows = []
    for (wk, c), a in agg.items():
        rows.append({"week": wk, "concept": c, "n": a["n"], "acc": round(a["correct"] / a["n"], 3), "ids": a["ids"]})
    rows.sort(key=lambda x: (x["acc"], -x["n"]))
    return rows


def unverified_claims(week: str) -> list[dict]:
    """'확인 필요' 배지가 붙은 표 행과, 정정 박스가 없는 '요약본' 언급을 찾는다."""
    p = WEEK_DIR / f"{week}.html"
    if not p.exists():
        return []
    src = p.read_text(encoding="utf-8")
    out = []
    for m in re.finditer(r"<tr>(.*?)</tr>", src, re.S):
        row = m.group(1)
        if 'badge check' in row:
            cells = re.findall(r"<td>(.*?)</td>", row, re.S)
            name = re.sub(r"<[^>]+>", "", cells[0]).strip() if cells else "?"
            out.append({"week": week, "kind": "확인 필요", "where": "비교표", "concept": name})
    return out


def card_ids(week: str) -> list[dict]:
    """개념 카드 id 와 제목 목록 (패치 대상 선택용)."""
    p = WEEK_DIR / f"{week}.html"
    src = p.read_text(encoding="utf-8")
    cards = []
    for m in re.finditer(r'<section class="concept" id="([^"]+)">.*?<h3>(.*?)</h3>', src, re.S):
        cards.append({"id": m.group(1), "title": re.sub(r"<[^>]+>", "", m.group(2)).strip()})
    return cards


def diagnose(run: dict, top: int = 3) -> dict:
    rows = concept_table(run)
    weeks = run["summary"]["weeks"]
    weak = [r for r in rows if r["acc"] < 1.0][:top]
    return {
        "based_on": run["summary"],
        "weak_concepts": weak,
        "all_concepts": rows,
        "unverified": [c for w in weeks for c in unverified_claims(w)],
        "cards": {w: card_ids(w) for w in weeks},
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", default="")
    ap.add_argument("--top", type=int, default=3)
    a = ap.parse_args()
    d = diagnose(json.loads(Path(a.run).read_text(encoding="utf-8")), a.top)
    if a.out:
        jdump(d, Path(a.out))
    for r in d["weak_concepts"]:
        log(f"약한 개념 {r['week']} · {r['concept']} acc={r['acc']} (n={r['n']})")
    log(f"미검증 주장 {len(d['unverified'])}건")

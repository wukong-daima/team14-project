"""한 라운드: 진단 → 제안 → 검증 → 리포트 (→ PR).

  python evolve/round.py --weeks week02,week04,week08 --mock          # API 없이 파이프라인 검증
  python evolve/round.py --weeks week02,week04,week08                 # 실제 실행 (ANTHROPIC_API_KEY)
  python evolve/round.py --weeks week02 --pr                          # 통과한 패치를 브랜치+PR 로

출력: evolve/reports/round-NN.json, 패치 적용본은 --apply 또는 --pr 일 때만 weeks/*.html 에 기록.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
from pathlib import Path
from types import SimpleNamespace

from common import LLM, REPORT_DIR, ROOT, RUN_DIR, WEAK_MODEL, WEEK_DIR, jdump, load_bank, log, update_report_index
from diagnose import diagnose
from propose import apply_patches, propose
from solve import run as solve_run
from verify import reward, source_pass, verify_patches


def next_round_no() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    nums = [int(p.stem.split("-")[1]) for p in REPORT_DIR.glob("round-*.json") if p.stem.split("-")[1].isdigit()]
    return (max(nums) + 1) if nums else 1


def solve_args(weeks: str, bank: str, k: int, model: str, mock: bool, effort: str = "low"):
    return SimpleNamespace(bank=bank, weeks=weeks, condition="page", k=k, model=model, effort=effort, limit=0, out="", mock=mock)


def git(*a, check=True):
    return subprocess.run(["git", *a], cwd=ROOT, check=check, capture_output=True, text=True).stdout.strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--weeks", required=True, help="week02,week04 — 이번 라운드 대상 주차")
    ap.add_argument("--k", type=int, default=1)
    ap.add_argument("--max-patches", type=int, default=3)
    ap.add_argument("--model", default=WEAK_MODEL)
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--apply", action="store_true", help="통과한 패치를 weeks/*.html 에 기록")
    ap.add_argument("--pr", action="store_true", help="--apply + 브랜치 생성 + 커밋 + 푸시 + PR")
    ap.add_argument("--reward", default="full", choices=["full", "acc-only"], help="보상 변형 (ablation). acc-only 는 출처 항 없이 정답률만")
    a = ap.parse_args()

    no = next_round_no()
    tag = f"round-{no:02d}"
    log(f"=== EvoLecture {tag} · weeks={a.weeks} · mock={a.mock}")
    llm = LLM(mock=a.mock)
    has_heldout = bool(load_bank("heldout"))

    # 1. 베이스라인
    log("[1/5] 베이스라인 (공개 세트, page 조건)")
    base_pub = solve_run(solve_args(a.weeks, "public", a.k, a.model, a.mock), llm)
    base_hid = solve_run(solve_args(a.weeks, "heldout", a.k, a.model, a.mock), llm) if has_heldout else None
    log("[1/5] 베이스라인 (none 조건, T 계산용 B)")
    base_none = solve_run(SimpleNamespace(**{**vars(solve_args(a.weeks, "public", a.k, a.model, a.mock)), "condition": "none"}), llm)

    # 2. 진단
    log("[2/5] 진단")
    diag = diagnose(base_pub, top=a.max_patches)
    jdump(diag, RUN_DIR / f"{tag}-diag.json")

    # 3. 제안
    log("[3/5] 제안")
    prop = propose(diag, llm, a.max_patches)
    patches = prop["patches"]
    patched = apply_patches(patches)
    jdump(prop, RUN_DIR / f"{tag}-patches.json")

    # 4. 검증
    log("[4/5] 검증")
    checks = verify_patches(patches, patched)
    after_pub = solve_run(solve_args(a.weeks, "public", a.k, a.model, a.mock), llm, html_override=patched, patched=True) if patches else base_pub
    after_hid = (solve_run(solve_args(a.weeks, "heldout", a.k, a.model, a.mock), llm, html_override=patched, patched=True) if (patches and has_heldout) else base_hid)

    weeks = a.weeks.split(",")
    sp_before = {w: source_pass(w) for w in weeks}
    sp_after = {w: source_pass(w, patched.get(w)) for w in weeks}
    def mean_rate(d):
        v = [x["rate"] for x in d.values() if x["rate"] is not None]
        return round(sum(v) / len(v), 3) if v else None
    R_before = reward(base_pub["summary"]["acc"], mean_rate(sp_before), a.reward)
    R_after = reward(after_pub["summary"]["acc"], mean_rate(sp_after), a.reward)
    # 신뢰구간이 겹치면 '유의한 개선'이라 부르지 않는다 (채택 여부와는 별개로 리포트에 남김)
    ci_b, ci_a = base_pub["summary"]["acc_ci95"], after_pub["summary"]["acc_ci95"]
    ci_overlap = not (ci_a[0] > ci_b[1] or ci_b[0] > ci_a[1])

    # O·T·G (한 라운드 근사). T 는 호출 수를 늘린 비교가 없으면 0 으로 두고 표기.
    d_pub = round(after_pub["summary"]["acc"] - base_pub["summary"]["acc"], 4)
    d_hid = round(after_hid["summary"]["acc"] - base_hid["summary"]["acc"], 4) if base_hid else None
    O = round(d_pub - d_hid, 4) if d_hid is not None else None
    T = 0.0  # k 동일, 호출 수 동일 → 이번 설계에서는 T=0. (E1/호출 수 실험은 experiments 로)
    G = round(d_pub - (O or 0) - T, 4) if O is not None else None

    accepted = checks["ok"] and R_after > R_before
    report = {
        "round": no, "date": dt.date.today().isoformat(), "weeks": weeks, "mock": a.mock, "model": a.model, "k": a.k,
        "reward_variant": a.reward, "n_public": base_pub["summary"]["n"], "n_heldout": base_hid["summary"]["n"] if base_hid else 0,
        "ci95": {"public_before": ci_b, "public_after": ci_a, "overlap": ci_overlap,
                 "heldout_before": base_hid["summary"]["acc_ci95"] if base_hid else None, "heldout_after": after_hid["summary"]["acc_ci95"] if after_hid else None},
        "baseline": {"acc_public": base_pub["summary"]["acc"], "acc_heldout": base_hid["summary"]["acc"] if base_hid else None,
                     "acc_none": base_none["summary"]["acc"], "source_pass": sp_before, "R": R_before},
        "after": {"acc_public": after_pub["summary"]["acc"], "acc_heldout": after_hid["summary"]["acc"] if after_hid else None,
                  "source_pass": sp_after, "R": R_after},
        "decomposition": {"delta_public": d_pub, "delta_heldout": d_hid, "O": O, "T": T, "G": G,
                          "note": "O = Δ공개 − Δ비공개 (비공개 세트 없으면 계산 불가). T 는 호출 수 동일 설계라 0."},
        "weak_concepts": diag["weak_concepts"], "patches": patches, "checks": checks, "accepted": accepted,
        "usage": llm.usage.to_dict(),
    }
    jdump(report, REPORT_DIR / f"{tag}.json")
    update_report_index()
    log(f"[5/5] 리포트 → evolve/reports/{tag}.json")
    log(f"  CI95 공개 {ci_b} → {ci_a} {'(겹침: 유의하지 않음)' if ci_overlap else '(분리: 유의)'}")
    log(f"  R {R_before} → {R_after}  Δ공개={d_pub} Δ비공개={d_hid} O={O} G={G}  패치 {len(patches)}개  accepted={accepted}  ${report['usage']['usd']}")

    if accepted and (a.apply or a.pr):
        for w, h in patched.items():
            (WEEK_DIR / f"{w}.html").write_text(h, encoding="utf-8")
        log(f"  적용: {', '.join(patched)}")
    if accepted and a.pr:
        br = f"evolve/{tag}"
        git("checkout", "-B", br)
        git("add", "-A", "weeks", "evolve/reports")
        git("commit", "-m", f"evolve {tag}: 패치 {len(patches)}개 (R {R_before}→{R_after}, Δ공개 {d_pub}, O {O}, G {G}, reward={a.reward})")
        git("push", "-u", "origin", br, "--force")
        body = (f"자가 진화 루프 {tag} 결과. 사람이 검토 후 머지합니다.\n\n"
                f"| 지표 | 전 | 후 |\n|---|---|---|\n| Acc 공개 | {report['baseline']['acc_public']} | {report['after']['acc_public']} |\n"
                f"| Acc 비공개 | {report['baseline']['acc_heldout']} | {report['after']['acc_heldout']} |\n| R | {R_before} | {R_after} |\n\n"
                f"분해: Δ공개 {d_pub} · O {O} · T {T} · G {G} · 보상 변형 {a.reward} · CI95 공개 {ci_b}→{ci_a} ({'겹침' if ci_overlap else '분리'})\n\n패치: " + ", ".join(f"{p['week']}#{p['card_id']} ({p['concept']})" for p in patches)
                + f"\n\n비용 ${report['usage']['usd']} · mock={a.mock}\n\n리포트: `evolve/reports/{tag}.json`")
        subprocess.run(["gh", "pr", "create", "--base", "main", "--head", br, "--title", f"evolve {tag}: 콘텐츠 보강 제안", "--body", body], cwd=ROOT, check=False)
    elif not accepted:
        log("  채택 안 됨 (검증 실패 또는 R 미상승). 리포트만 남김.")


if __name__ == "__main__":
    main()

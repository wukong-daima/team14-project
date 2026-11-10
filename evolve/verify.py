"""검증: 패치 적용본으로 다시 풀고 R 변화를 계산한다. 유출(리워드 해킹)·HTML 깨짐도 검사.

R = alpha * Acc_public + beta * SourcePass
"""
from __future__ import annotations

import difflib
import re
from html.parser import HTMLParser

from common import WEEK_DIR, load_bank, log

ALPHA, BETA = 0.6, 0.4


class _Balance(HTMLParser):
    VOID = {"br", "img", "input", "meta", "link", "hr", "source"}

    def __init__(self):
        super().__init__()
        self.stack = []
        self.errors = 0

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        elif tag in self.stack:
            while self.stack and self.stack[-1] != tag:
                self.stack.pop(); self.errors += 1
            self.stack.pop()
        else:
            self.errors += 1


def html_ok(html: str) -> tuple[bool, int]:
    p = _Balance(); p.feed(html)
    return (p.errors == 0 and len(p.stack) == 0), p.errors + len(p.stack)


def leakage(patches: list[dict], bank: list[dict]) -> list[dict]:
    """패치 문장이 공개 문제 문장·보기·정답과 지나치게 겹치면 유출로 본다."""
    hits = []
    for p in patches:
        text = " ".join(str(p.get(k, "")) for k in ("title", "pro", "easy"))
        for q in bank:
            if q["week"] != p["week"]:
                continue
            probes = [q["q"]] + (q.get("options") or [])
            for s in probes:
                s = re.sub(r"\s+", " ", str(s)).strip()
                if len(s) < 15:
                    continue
                r = difflib.SequenceMatcher(None, s, text).find_longest_match(0, len(s), 0, len(text))
                if r.size >= max(25, int(len(s) * 0.6)):
                    hits.append({"patch": p.get("card_id"), "week": p["week"], "qid": q["id"], "overlap": s[r.a:r.a + r.size]})
                    break
    return hits


def source_pass(week: str, html: str | None = None) -> dict:
    """출처 검증 통과율의 대리 지표: 비교표 셀 배지 집계 (src=통과, check=미판정, private=미판정)."""
    src = html if html is not None else (WEEK_DIR / f"{week}.html").read_text(encoding="utf-8")
    n_src = len(re.findall(r'badge src', src))
    n_chk = len(re.findall(r'badge check', src))
    n_prv = len(re.findall(r'badge private', src))
    judged = n_src + n_chk
    return {"src": n_src, "check": n_chk, "private": n_prv, "rate": round(n_src / judged, 3) if judged else None}


def reward(acc_public: float, sp_rate: float | None) -> float:
    return round(ALPHA * acc_public + BETA * (sp_rate if sp_rate is not None else 0.5), 4)


def verify_patches(patches: list[dict], patched_html: dict[str, str]) -> dict:
    bank = load_bank("public")
    leaks = leakage(patches, bank)
    html_report = {}
    for w, h in patched_html.items():
        ok, errs = html_ok(h)
        html_report[w] = {"ok": ok, "errors": errs}
    ok = not leaks and all(v["ok"] for v in html_report.values())
    if leaks:
        log(f"  유출 의심 {len(leaks)}건: " + ", ".join(f"{l['week']}#{l['patch']}~{l['qid']}" for l in leaks))
    return {"ok": ok, "leaks": leaks, "html": html_report}

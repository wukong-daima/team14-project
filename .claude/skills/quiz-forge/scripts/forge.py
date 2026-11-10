"""quiz-forge 결정적 단계 (격자 계획 · 병합 · 기계 검사 · 문제지 · 채점 · 수정 요청 · 조립)

    python .claude/skills/quiz-forge/scripts/forge.py plan     --week week09 [--target 30]
    python .claude/skills/quiz-forge/scripts/forge.py merge    --week week09 [--round 2]
    python .claude/skills/quiz-forge/scripts/forge.py check    --week week09 [--round 2]
    python .claude/skills/quiz-forge/scripts/forge.py pack     --week week09 [--round 2]
    python .claude/skills/quiz-forge/scripts/forge.py score    --week week09 [--round 2]
    python .claude/skills/quiz-forge/scripts/forge.py repairs  --week week09        # 1라운드 탈락 → r2/08_repair_request.json
    python .claude/skills/quiz-forge/scripts/forge.py assemble --week week09

1라운드 파일은 _workspace/quiz/<week>/, 수정 라운드는 그 아래 r2/ 에 둔다. 형식은 references/schemas.md.
표준 라이브러리만 쓴다.
"""
import argparse
import glob
import html
import json
import math
import os
import re
import sys
from datetime import date

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
QUIZ_DATA = os.path.join(ROOT, "assets", "data", "quiz")
TYPE_RATIO = {"mc": 0.5, "num": 0.2, "self": 0.3}
DIFF_CYCLE = [2, 3, 1, 2]
HARD = {"format_error", "calc_mismatch"}          # 이 문제는 풀이 시험에도 안 보낸다


def ws(week, rnd=1):
    d = os.path.join(ROOT, "_workspace", "quiz", week)
    return d if rnd == 1 else os.path.join(d, "r%d" % rnd)


def load(path, default=None):
    if not os.path.exists(path):
        if default is not None:
            return default
        sys.exit("없음: " + os.path.relpath(path, ROOT))
    with open(path, encoding="utf-8-sig") as f:
        return json.load(f)


def save(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("  →", os.path.relpath(path, ROOT))


def short(week):                                  # week09 → w09a (a = agent)
    return "w" + re.sub(r"\D", "", week).zfill(2) + "a"


# ---------------------------------------------------------------- plan
def cmd_plan(a):
    cons = load(os.path.join(ws(a.week), "01_mapper_concepts.json"))["concepts"]
    cons = sorted(cons, key=lambda c: -int(c.get("weight", 1)))
    total_w = sum(int(c.get("weight", 1)) for c in cons) or 1
    # 개념별 칸 수: 가중치 비례, 최소 1 · 최대 4 (한 개념에 몰리지 않게)
    slots = {c["key"]: max(1, min(4, round(a.target * int(c.get("weight", 1)) / total_w))) for c in cons}
    n = sum(slots.values())
    quota = {t: TYPE_RATIO[t] * n for t in TYPE_RATIO}
    cells, k = [], 0
    for c in cons:
        allowed = [t for t in c.get("types", ["mc", "self"]) if t in TYPE_RATIO]
        if not c.get("numeric_ok"):
            allowed = [t for t in allowed if t != "num"]
        allowed = allowed or ["mc"]
        used = []
        for i in range(slots[c["key"]]):
            # 남은 할당량이 큰 유형부터, 같은 개념 안에서는 아직 안 쓴 유형 우선
            t = max(allowed, key=lambda t: (t not in used, quota[t]))
            quota[t] -= 1
            used.append(t)
            k += 1
            cells.append({"cell": "c%02d" % k, "concept": c["key"], "concept_name": c.get("name", c["key"]),
                          "type": t, "difficulty": DIFF_CYCLE[i % len(DIFF_CYCLE)]})
    save(os.path.join(ws(a.week), "02_plan.json"), {"week": a.week, "cells": cells})
    cnt = {t: sum(1 for x in cells if x["type"] == t) for t in TYPE_RATIO}
    print("칸 %d개 · 개념 %d개 · %s" % (len(cells), len(cons), cnt))


# ---------------------------------------------------------------- merge
def cmd_merge(a):
    d = ws(a.week, a.round)
    pattern = "03_writer_batch*.json" if a.round == 1 else "08_writer_repair*.json"
    files = sorted(glob.glob(os.path.join(d, pattern)))
    if not files:
        sys.exit("출제 결과 파일이 없습니다: " + pattern)
    out, seen = [], set()
    for f in files:
        for q in load(f).get("questions", []):
            cell = q.get("cell")
            if not cell or cell in seen:
                continue
            seen.add(cell)
            q["id"] = short(a.week) + "-" + cell
            q["round"] = a.round
            out.append(q)
    save(os.path.join(d, "03_candidates.json"), {"week": a.week, "questions": out})
    print("후보 %d개 (%d개 파일)" % (len(out), len(files)))


# ---------------------------------------------------------------- check
SAFE_CALC = re.compile(r"^[0-9\s.+\-*/()e]+$")


def calc(expr):
    expr = str(expr).replace("^", "**")
    if not SAFE_CALC.match(expr.replace("**", "*")):
        raise ValueError("허용되지 않은 문자")
    return eval(expr, {"__builtins__": {}}, {})  # 숫자·연산자만 통과한 식


def grams(s, n=3):
    s = re.sub(r"\s+", "", s)
    return {s[i:i + n] for i in range(max(0, len(s) - n + 1))}


def jacc(a, b):
    return len(a & b) / len(a | b) if a and b else 0.0


def existing_questions(week):
    """주차 페이지의 예상 문제와 다른 문제 은행(에이전트 은행 제외) — 중복 검사용"""
    out = []
    for p in glob.glob(os.path.join(ROOT, "weeks", "week*.html")):
        txt = open(p, encoding="utf-8").read()
        for m in re.finditer(r'<details class="quiz"><summary>(.*?)</summary>', txt, re.S):
            s = html.unescape(re.sub(r"<[^>]+>", "", m.group(1)))
            if s.strip() and not s.strip().endswith("문제"):
                out.append((os.path.basename(p), s))
    for p in glob.glob(os.path.join(QUIZ_DATA, "*.json")):
        if p.endswith("-agent.json") or p.endswith("index.json"):
            continue
        for q in load(p).get("questions", []):
            out.append((os.path.basename(p), q.get("q", "")))
    return out


def check_one(q):
    issues = []
    t = q.get("type")
    if not q.get("q") or t not in TYPE_RATIO:
        return ["format_error"]
    if not q.get("evidence"):
        issues.append("no_evidence")
    if t == "mc":
        opts, ans = q.get("options"), q.get("answer")
        if not isinstance(opts, list) or len(opts) != 4 or not isinstance(ans, int) or not 0 <= ans < 4:
            return issues + ["format_error"]
        if len(set(o.strip() for o in opts)) < 4:
            issues.append("format_error")
        right = opts[ans].strip()
        if len(right) >= 6 and right in q["q"]:
            issues.append("F20_answer_in_question")
        others = [len(o) for i, o in enumerate(opts) if i != ans]
        if len(right) > 1.6 * (sum(others) / 3) and len(right) - max(others) > 8:
            issues.append("F21_long_answer")
        if any(re.search(r"모두 (옳|맞)|정답 없음|해당 없음", o) for o in opts):
            issues.append("F40_all_none")
        if sum(bool(re.match(r"\s*(\(?[A-Da-d][).:]|[①-④]|(과제|모델|사례|방법) ?[A-D])", o)) for o in opts) >= 2:
            issues.append("F43_option_labels")
        if re.search(r"[①-④]|[1-4]번(째)? ?보기|(첫|두|세|네) ?번째 보기|보기 ?[1-4]", q.get("explanation", "")):
            issues.append("F44_explanation_by_number")
    elif t == "num":
        ans = q.get("answer")
        if not isinstance(ans, (int, float)):
            return issues + ["format_error"]
        tol = q.get("tol")
        if not isinstance(tol, (int, float)):
            tol = q["tol"] = abs(ans) * 0.01 or 0.001
        try:
            v = calc(q.get("calc", ""))
            if not math.isclose(v, ans, abs_tol=tol):
                issues.append("calc_mismatch")
                q["calc_value"] = v
        except Exception as e:
            issues.append("calc_mismatch")
            q["calc_value"] = "계산 실패: %s" % e
    elif t == "self":
        if not isinstance(q.get("answer"), str) or not q.get("answer").strip():
            return issues + ["format_error"]
        if not isinstance(q.get("rubric"), list) or len(q["rubric"]) < 2:
            issues.append("F14_no_rubric")
    return issues


def rebalance(questions):
    """객관식 정답 위치를 0~3에 고르게 (리워드 해킹 방지). 정답 보기를 목표 칸과 맞바꾼다."""
    mcs = sorted([q for q in questions if q.get("type") == "mc" and isinstance(q.get("options"), list)
                  and len(q["options"]) == 4 and isinstance(q.get("answer"), int)], key=lambda q: q["id"])
    for i, q in enumerate(mcs):
        target, cur = (i * 3 + 1) % 4, q["answer"]   # 1,0,3,2,… 순서로 퍼뜨림
        if target != cur:
            o = q["options"]
            o[target], o[cur] = o[cur], o[target]
            q["answer"] = target
    return {k: sum(1 for q in mcs if q["answer"] == k) for k in range(4)}


def cmd_check(a):
    d = ws(a.week, a.round)
    cand = load(os.path.join(d, "03_candidates.json"))
    qs = cand["questions"]
    pos = rebalance(qs)
    prior = existing_questions(a.week)
    res = {}
    for q in qs:
        iss = check_one(q)
        g = grams(q.get("q", ""))
        for src, s in prior:
            if jacc(g, grams(s)) >= 0.5:
                iss.append("F32_dup:" + src)
                break
        for o in qs:
            if o is not q and o["id"] < q["id"] and jacc(g, grams(o.get("q", ""))) >= 0.6:
                iss.append("F32_dup:" + o["id"])
        res[q["id"]] = {"issues": iss, "hard": any(i in HARD for i in iss)}
    save(os.path.join(d, "03_candidates.json"), cand)        # 정답 위치 재배치 반영
    save(os.path.join(d, "04_check.json"), {"week": a.week, "answer_positions": pos, "results": res})
    bad = {k: v["issues"] for k, v in res.items() if v["issues"]}
    print("검사 %d개 · 문제 있음 %d개 · 정답 위치 %s" % (len(qs), len(bad), pos))
    for k, v in bad.items():
        print("   ", k, v)


# ---------------------------------------------------------------- pack
def cmd_pack(a):
    d = ws(a.week, a.round)
    qs = load(os.path.join(d, "03_candidates.json"))["questions"]
    chk = load(os.path.join(d, "04_check.json"))["results"]
    out = []
    for q in qs:
        if chk.get(q["id"], {}).get("hard") or q["type"] == "self":
            continue
        item = {"id": q["id"], "type": q["type"], "q": q["q"]}
        if q["type"] == "mc":
            item["options"] = q["options"]
        out.append(item)
    save(os.path.join(d, "04_pack.json"), {"week": a.week, "questions": out})
    print("문제지 %d문제 (서술형·형식 오류 제외)" % len(out))


# ---------------------------------------------------------------- score
def correct(q, ans):
    if ans is None:
        return False
    if q["type"] == "mc":
        return ans.get("choice") == q["answer"]
    try:
        return math.isclose(float(ans.get("value")), q["answer"], abs_tol=q.get("tol") or abs(q["answer"]) * 0.01)
    except (TypeError, ValueError):
        return False


def cmd_score(a):
    d = ws(a.week, a.round)
    qs = {q["id"]: q for q in load(os.path.join(d, "03_candidates.json"))["questions"]}
    pack = [x["id"] for x in load(os.path.join(d, "04_pack.json"))["questions"]]
    runs = {}
    for kind in ("weak", "strong"):
        runs[kind] = [{x["id"]: x for x in load(f).get("answers", [])}
                      for f in sorted(glob.glob(os.path.join(d, "05_%s_run*.json" % kind)))]
    out = {}
    for qid in pack:
        q = qs[qid]
        w = sum(correct(q, r.get(qid)) for r in runs["weak"])
        s = sum(correct(q, r.get(qid)) for r in runs["strong"])
        kw, ks = len(runs["weak"]), len(runs["strong"])
        if ks and s == 0:
            status = "broken"
        elif ks and s == 1 and ks >= 3:
            status = "shaky"
        elif kw and w == kw and q.get("difficulty", 2) > 1:
            status = "too_easy"
        else:
            status = "ok"
        wrong = [r.get(qid, {}).get("choice") for r in runs["strong"] if not correct(q, r.get(qid))]
        out[qid] = {"weak": "%d/%d" % (w, kw), "strong": "%d/%d" % (s, ks), "status": status,
                    "strong_wrong_choices": wrong if q["type"] == "mc" else None}
    tally = {}
    for v in out.values():
        tally[v["status"]] = tally.get(v["status"], 0) + 1
    def p1(kind):
        rs = runs[kind]
        if not rs or not pack:
            return None
        return round(sum(correct(qs[i], r.get(i)) for r in rs for i in pack) / (len(rs) * len(pack)), 3)
    save(os.path.join(d, "06_scores.json"), {"week": a.week, "k": {"weak": len(runs["weak"]), "strong": len(runs["strong"])},
                                             "pass1": {"weak": p1("weak"), "strong": p1("strong")},
                                             "tally": tally, "scores": out})
    print("채점 %d문제 · %s · pass@1 약함 %s / 강함 %s" % (len(out), tally, p1("weak"), p1("strong")))


# ---------------------------------------------------------------- repairs / assemble
def verdicts(d):
    rv = {}
    for f in sorted(glob.glob(os.path.join(d, "07_verifier_batch*.json"))):
        for r in load(f).get("reviews", []):
            rv[r["id"]] = r
    return rv


def judge(q, chk, sc, rv, final=False):
    """(통과 여부, 탈락 사유 목록). final=True(마지막 라운드)면 too_easy 이면서 검증자가 pass 한 문제는
    '기초 문제'로 남긴다(난이도 1로 낮춤). 약한 모델은 일반 ML 지식이 있어 강의를 안 들은 사람보다 강하기 때문."""
    why = []
    c = chk.get(q["id"], {"issues": [], "hard": False})
    if c["hard"]:
        why += c["issues"]
    s = (sc.get(q["id"]) or {}).get("status")
    if s in ("broken", "shaky") or (s == "too_easy" and not final):
        why.append("score:" + s)
    r = rv.get(q["id"])
    if not r:
        why.append("no_review")
    elif r.get("verdict") != "pass":
        why.append("verifier:" + r.get("verdict", "?"))
    return not why, why


def round_state(week, rnd):
    d = ws(week, rnd)
    qs = load(os.path.join(d, "03_candidates.json"))["questions"]
    chk = load(os.path.join(d, "04_check.json"))["results"]
    sc = load(os.path.join(d, "06_scores.json"), {"scores": {}})["scores"]
    return qs, chk, sc, verdicts(d)


def cmd_repairs(a):
    qs, chk, sc, rv = round_state(a.week, 1)
    req = []
    for q in qs:
        ok, why = judge(q, chk, sc, rv)
        r = rv.get(q["id"], {})
        if ok or r.get("verdict") == "drop":
            continue
        req.append({"cell": q["cell"], "original": {k: v for k, v in q.items() if k not in ("round",)},
                    "reasons": why, "check_issues": chk.get(q["id"], {}).get("issues", []),
                    "score": sc.get(q["id"]), "verifier": r})
    save(os.path.join(ws(a.week, 2), "08_repair_request.json"), {"week": a.week, "items": req})
    print("수정 요청 %d개 (verifier drop 은 제외)" % len(req))


def cmd_assemble(a):
    kept, dropped, coverage = [], [], {}
    plan = load(os.path.join(ws(a.week), "02_plan.json"))["cells"]
    final = {}
    for rnd in (1, 2):
        if not os.path.exists(os.path.join(ws(a.week, rnd), "03_candidates.json")):
            continue
        qs, chk, sc, rv = round_state(a.week, rnd)
        for q in qs:
            ok, why = judge(q, chk, sc, rv, final=(rnd == 2))
            if ok and (sc.get(q["id"]) or {}).get("status") == "too_easy":
                q["difficulty"], q["basic"] = 1, True
            final[q["cell"]] = (q, ok, why, sc.get(q["id"]))   # 2라운드가 1라운드를 덮어씀
    for cell, (q, ok, why, s) in sorted(final.items()):
        (kept if ok else dropped).append((q, why, s))
    bank = []
    for q, _, s in kept:
        b = {"id": q["id"], "type": q["type"], "q": q["q"], "answer": q["answer"],
             "explanation": q.get("explanation", ""), "concept": q.get("concept_name") or q.get("concept", ""),
             "difficulty": q.get("difficulty"), "refs": [e.get("where", "") for e in q.get("evidence", [])]}
        if q["type"] == "mc":
            b["options"] = q["options"]
        if q["type"] == "num":
            b["tol"] = q.get("tol")
            if q.get("unit"):
                b["unit"] = q["unit"]
        if q["type"] == "self":
            b["answer"] = q["answer"] + ("\n\n채점 핵심어: " + " · ".join(q.get("rubric") or []) if q.get("rubric") else "")
        if s:
            b["verified"] = {"strong": s["strong"], "weak": s["weak"]}
        if q.get("basic"):
            b["basic"] = True
        bank.append(b)
        coverage[q.get("concept")] = coverage.get(q.get("concept"), 0) + 1
    concepts = sorted({c["concept"] for c in plan})
    s1 = load(os.path.join(ws(a.week), "06_scores.json"), {})
    report = {"week": a.week, "generated": date.today().isoformat(), "planned": len(plan),
              "candidates": len(final), "kept": len(kept), "dropped": len(dropped),
              "by_type": {t: sum(1 for b in bank if b["type"] == t) for t in TYPE_RATIO},
              "basic_kept": sum(1 for b in bank if b.get("basic")),
              "answer_positions": {k: sum(1 for b in bank if b["type"] == "mc" and b["answer"] == k) for k in range(4)},
              "concept_coverage": {c: coverage.get(c, 0) for c in concepts},
              "round1_pass1": s1.get("pass1"),
              "round2_pass1": load(os.path.join(ws(a.week, 2), "06_scores.json"), {}).get("pass1"),
              "drop_reasons": [{"id": q["id"], "cell": q["cell"], "q": q["q"][:60], "why": why} for q, why, _ in dropped]}
    name = a.week + "-agent.json"
    save(os.path.join(QUIZ_DATA, name), {"week": a.week, "source": "agent", "generated": report["generated"],
                                         "note": "quiz-forge 하네스 출력. 사람 검토 전에는 PR 하지 않는다.",
                                         "questions": bank})
    save(os.path.join(QUIZ_DATA, "reports", a.week + "-agent.report.json"), report)
    idx_p = os.path.join(QUIZ_DATA, "index.json")
    idx = load(idx_p, {"banks": []})
    if name not in idx["banks"]:
        idx["banks"].append(name)
        save(idx_p, idx)
    print("통과 %d / 후보 %d (계획 %d) · 유형 %s · 정답 위치 %s" % (len(kept), len(final), len(plan),
          report["by_type"], report["answer_positions"]))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("cmd", choices=["plan", "merge", "check", "pack", "score", "repairs", "assemble"])
    p.add_argument("--week", required=True)
    p.add_argument("--round", type=int, default=1)
    p.add_argument("--target", type=int, default=30)
    a = p.parse_args()
    globals()["cmd_" + a.cmd](a)


if __name__ == "__main__":
    main()

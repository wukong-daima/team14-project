"""제안: 약한 개념에 대해 근거를 인용한 보강 설명(전공/쉬운 두 벌)을 만들고 페이지에 패치한다.

규칙 (리워드 해킹 방지):
  - 공개 문제의 문장·정답을 패치에 그대로 적지 않는다 (verify 가 검사)
  - 제안자는 문제 자체를 보지 않는다. 약한 '개념 이름'과 브리프·페이지 원문만 본다
  - 출처 없는 주장은 넣지 않는다 (sources 필수)
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from common import LLM, STRONG_MODEL, WEEK_DIR, brief_text, jdump, log, page_text

SYSTEM = (
    "당신은 대학원 '최신딥러닝이론및응용' 강의 노트를 보강하는 편집자입니다. "
    "주어진 강의 브리프(원본 대조본)와 현재 페이지 본문만 근거로 씁니다. 모르는 것은 쓰지 않습니다. "
    "출력은 JSON 하나만: {\"patches\": [{\"card_id\", \"title\", \"pro\", \"easy\", \"sources\", \"reason\"}]}. "
    "pro 는 전공 수준 3~5문장(정의→왜→어떻게→대가), easy 는 중학생 비유 2~3문장. "
    "sources 는 브리프의 절 이름이나 논문명 배열. 설명문 외에 문제·정답·보기 형태의 문장은 쓰지 않습니다."
)


def propose(diag: dict, llm: LLM, max_patches: int = 3) -> dict:
    patches = []
    for w in diag["weak_concepts"][:max_patches]:
        week, concept = w["week"], w["concept"]
        cards = diag["cards"].get(week, [])
        card_list = "\n".join(f"- {c['id']}: {c['title']}" for c in cards)
        user = (
            f"[주차] {week}\n[약한 개념] {concept}  (풀이자 정답률 {w['acc']})\n"
            f"[이 주차의 개념 카드 목록 — card_id 는 이 중 하나]\n{card_list}\n\n"
            f"[강의 브리프]\n{brief_text(week)[:12000]}\n\n"
            f"[현재 페이지 본문 (예상 문제 제외)]\n{page_text(week)[:12000]}\n\n"
            "약한 개념에 대해 현재 페이지에 빠졌거나 모호한 점을 보강하는 패치 1개를 JSON 으로 주세요."
        )
        text = llm.ask(STRONG_MODEL, SYSTEM, user, effort="high", max_tokens=6000,
                       mock_hint={"kind": "propose", "week": week, "card_id": cards[0]["id"] if cards else "c1"})
        m = re.search(r"\{.*\}", text, re.S)
        if not m:
            log(f"  제안 파싱 실패: {week}/{concept}")
            continue
        try:
            obj = json.loads(m.group(0))
        except json.JSONDecodeError:
            log(f"  제안 JSON 오류: {week}/{concept}")
            continue
        for p in obj.get("patches", []):
            p["week"] = week
            p["concept"] = concept
            if p.get("card_id") in {c["id"] for c in cards} and p.get("pro") and p.get("sources"):
                patches.append(p)
    return {"patches": patches, "usage": llm.usage.to_dict()}


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_patch(p: dict) -> str:
    src = "".join(f"<li>{esc(s)}</li>" for s in p.get("sources", []))
    return (
        f'\n            <div class="evolve-patch" data-concept="{esc(p.get("concept",""))}">'
        f'\n              <div class="callout"><b>🧬 자가 진화 보강 · {esc(p.get("title",""))}</b>'
        f'\n                <div data-level="pro"><p>{esc(p["pro"])}</p></div>'
        f'\n                <div data-level="easy"><p>{esc(p.get("easy",""))}</p></div>'
        f'\n                <details class="small"><summary>근거 · 이유</summary><ul>{src}</ul><p class="muted">{esc(p.get("reason",""))}</p></details>'
        f'\n              </div>\n            </div>\n'
    )


def apply_patches(patches: list[dict]) -> dict[str, str]:
    """주차별 패치 적용본 HTML 을 반환 (파일은 건드리지 않음)."""
    out: dict[str, str] = {}
    for p in patches:
        week = p["week"]
        html = out.get(week) or (WEEK_DIR / f"{week}.html").read_text(encoding="utf-8")
        # 해당 카드(section.concept#id)의 첫 <figure 또는 </div></section> 앞에 삽입
        m = re.search(rf'(<section class="concept" id="{re.escape(p["card_id"])}">.*?)(\n\s*<figure class="figure">|\n\s*</div>\s*</section>)', html, re.S)
        if not m:
            log(f"  카드 못 찾음: {week}#{p['card_id']}")
            continue
        html = html[: m.end(1)] + render_patch(p) + html[m.end(1):]
        out[week] = html
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--diag", required=True)
    ap.add_argument("--out", default="evolve/runs/patches.json")
    ap.add_argument("--max", type=int, default=3)
    ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()
    d = json.loads(Path(a.diag).read_text(encoding="utf-8"))
    r = propose(d, LLM(mock=a.mock), a.max)
    jdump(r, Path(a.out))
    log(f"패치 {len(r['patches'])}개 → {a.out}")

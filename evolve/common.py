"""EvoLecture evolve 루프 공통 모듈.

- 문제 은행 로드 (공개: assets/data/quiz, 비공개: HELDOUT_DIR)
- 주차 페이지 텍스트 추출 (예상 문제·퀴즈·스크립트 제거 → 유출 방지)
- Claude 호출 래퍼 (비용 집계, mock 모드)
"""
from __future__ import annotations

import hashlib
import html
import json
import os
import random
import re
import sys
import time
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_BANK_DIR = ROOT / "assets" / "data" / "quiz"
BRIEF_DIR = ROOT / "content" / "briefs"
WEEK_DIR = ROOT / "weeks"
RUN_DIR = ROOT / "evolve" / "runs"
REPORT_DIR = ROOT / "evolve" / "reports"

# USD per 1M tokens (입력, 출력). 2026-10 기준 공개 가격. 리포트 추정용.
PRICE = {
    "claude-haiku-5-5": (0.10, 0.50),
    "claude-sonnet-5-5": (2.00, 10.00),
    "claude-opus-5-5": (4.00, 20.00),
}
WEAK_MODEL = os.environ.get("EVOLVE_WEAK_MODEL", "claude-haiku-5-5")
STRONG_MODEL = os.environ.get("EVOLVE_STRONG_MODEL", "claude-opus-5-5")
MAX_USD = float(os.environ.get("EVOLVE_MAX_USD", "5"))
# 백엔드: "api" = Anthropic SDK(API 키 과금) · "claude-cli" = 구독 로그인된 Claude Code 헤드리스(claude -p)
BACKEND = os.environ.get("EVOLVE_BACKEND", "claude-cli" if not os.environ.get("ANTHROPIC_API_KEY") else "api")
CLAUDE_BIN = os.environ.get("CLAUDE_BIN", "claude")


# ---------------------------------------------------------------- 문제 은행
def load_bank(kind: str = "public", weeks: list[str] | None = None) -> list[dict]:
    """kind: public | heldout. 자동 채점 가능한 mc/num 문항만 반환."""
    if kind == "public":
        base = PUBLIC_BANK_DIR
    else:
        hd = os.environ.get("HELDOUT_DIR") or str(ROOT / "_heldout" / "heldout")
        base = Path(hd)
    idx = base / "index.json"
    if not idx.exists():
        return []
    banks = json.loads(idx.read_text(encoding="utf-8")).get("banks", [])
    out = []
    for f in banks:
        p = base / f
        if not p.exists():
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        wk = d.get("week")
        if weeks and wk not in weeks:
            continue
        for q in d.get("questions", []):
            if q.get("type") not in ("mc", "num"):
                continue
            qq = dict(q)
            qq["week"] = wk
            qq["bank"] = kind
            qq.setdefault("id", "q-" + hashlib.sha1(q["q"].encode()).hexdigest()[:8])
            out.append(qq)
    return out


# ---------------------------------------------------------------- 페이지 텍스트
class _Text(HTMLParser):
    """시험 포인트(section.exam), 퀴즈(details.quiz), script/style 를 제외한 본문 텍스트."""

    SKIP_TAGS = {"script", "style", "nav", "header", "footer"}

    def __init__(self):
        super().__init__()
        self.out: list[str] = []
        self.skip_depth = 0
        self.stack: list[tuple[str, bool]] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = (a.get("class") or "").split()
        skip = tag in self.SKIP_TAGS or ("exam" in cls and tag == "section") or ("quiz" in cls and tag == "details") or a.get("id") == "week-nav"
        self.stack.append((tag, skip))
        if skip:
            self.skip_depth += 1
        elif tag in ("p", "li", "h1", "h2", "h3", "tr", "figcaption", "div", "section", "summary", "text"):
            self.out.append("\n")
        if tag == "div" and a.get("data-level") == "easy" and not skip:
            self.out.append("\n[쉬운 설명] ")

    def handle_endtag(self, tag):
        # 가장 가까운 같은 태그를 닫는다
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                _, skip = self.stack.pop(i)
                if skip:
                    self.skip_depth -= 1
                break

    def handle_data(self, data):
        if self.skip_depth == 0:
            self.out.append(data)


def page_text(week: str, html_override: str | None = None) -> str:
    src = html_override if html_override is not None else (WEEK_DIR / f"{week}.html").read_text(encoding="utf-8")
    p = _Text()
    p.feed(src)
    txt = html.unescape("".join(p.out))
    txt = re.sub(r"[ \t]+", " ", txt)
    txt = re.sub(r"\n\s*\n+", "\n", txt)
    return txt.strip()


def brief_text(week: str) -> str:
    p = BRIEF_DIR / f"{week}.md"
    if not p.exists():
        return ""
    t = p.read_text(encoding="utf-8")
    # 브리프의 예상 문제 절은 제외 (유출 방지)
    t = re.split(r"\n### 예상 문제|\n## 시험 포인트", t)[0]
    return t


def context_for(week: str, condition: str, html_override: str | None = None) -> str:
    """condition: none | brief | page"""
    if condition == "none":
        return ""
    if condition == "brief":
        return brief_text(week)
    if condition == "page":
        return page_text(week, html_override)
    raise ValueError(condition)


# ---------------------------------------------------------------- 모델 호출
@dataclass
class Usage:
    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    usd: float = 0.0
    by_model: dict = field(default_factory=dict)

    def add(self, model: str, inp: int, out: int):
        pi, po = PRICE.get(model, (5.0, 25.0))
        cost = inp / 1e6 * pi + out / 1e6 * po
        self.calls += 1
        self.input_tokens += inp
        self.output_tokens += out
        self.usd += cost
        m = self.by_model.setdefault(model, {"calls": 0, "usd": 0.0})
        m["calls"] += 1
        m["usd"] += cost
        if self.usd > MAX_USD:
            raise RuntimeError(f"비용 상한 초과: ${self.usd:.2f} > ${MAX_USD:.2f} (EVOLVE_MAX_USD)")

    def to_dict(self):
        return {"calls": self.calls, "input_tokens": self.input_tokens, "output_tokens": self.output_tokens,
                "usd": round(self.usd, 4), "by_model": {k: {"calls": v["calls"], "usd": round(v["usd"], 4)} for k, v in self.by_model.items()}}


class LLM:
    """Claude 호출 래퍼. mock=True 면 API 없이 결정적 가짜 응답(파이프라인 검증용)."""

    def __init__(self, mock: bool = False, usage: Usage | None = None, seed: int = 14):
        self.mock = mock
        self.usage = usage or Usage()
        self.rng = random.Random(seed)
        self._client = None
        self.backend = BACKEND
        if not mock and self.backend == "api":
            import anthropic  # 지연 import: mock/cli 모드는 SDK 없이도 동작
            self._client = anthropic.Anthropic()

    def ask(self, model: str, system: str, user: str, effort: str = "low", max_tokens: int = 4000, mock_hint: dict | None = None) -> str:
        if self.mock:
            self.usage.add(model, len(system + user) // 3, 40)
            return self._mock_answer(mock_hint or {})
        if self.backend == "claude-cli":
            return self._ask_cli(model, system, user, effort)
        import anthropic
        for attempt in range(3):
            try:
                r = self._client.messages.create(
                    model=model, max_tokens=max_tokens, system=system,
                    output_config={"effort": effort},
                    messages=[{"role": "user", "content": user}],
                )
                break
            except anthropic.RateLimitError as e:
                wait = int(e.response.headers.get("retry-after", "20"))
                time.sleep(min(wait, 60))
            except anthropic.APIStatusError as e:
                if e.status_code >= 500 and attempt < 2:
                    time.sleep(5 * (attempt + 1))
                    continue
                raise
        else:
            raise RuntimeError("API 재시도 실패")
        self.usage.add(model, r.usage.input_tokens, r.usage.output_tokens)
        if r.stop_reason == "refusal":
            return ""
        return "".join(b.text for b in r.content if b.type == "text")

    def _ask_cli(self, model: str, system: str, user: str, effort: str) -> str:
        """구독 로그인된 Claude Code 를 헤드리스로 호출. 도구 없음, 세션 저장 없음, 1턴."""
        import subprocess
        cmd = [CLAUDE_BIN, "-p", user, "--system-prompt", system, "--model", model, "--effort", effort,
               "--output-format", "json", "--bare", "--strict-mcp-config", "--tools", "", "--no-session-persistence"]
        for attempt in range(3):
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            try:
                j = json.loads(r.stdout.strip().splitlines()[-1]) if r.stdout.strip() else {}
            except json.JSONDecodeError:
                j = {}
            if j and not j.get("is_error"):
                u = j.get("usage") or {}
                self.usage.add(model, int(u.get("input_tokens", 0)) + int(u.get("cache_read_input_tokens", 0)) + int(u.get("cache_creation_input_tokens", 0)), int(u.get("output_tokens", 0)))
                return j.get("result", "") or ""
            msg = (j.get("result") if j else "") or r.stderr.strip()[-300:] or r.stdout.strip()[-300:]
            if "Not logged in" in msg:
                raise RuntimeError("Claude Code 가 로그인돼 있지 않습니다. 터미널에서 `claude` 실행 후 /login (구독 계정), CI 는 `claude setup-token` 으로 만든 CLAUDE_CODE_OAUTH_TOKEN.")
            if "rate" in msg.lower() or "limit" in msg.lower() or "overloaded" in msg.lower():
                time.sleep(60 * (attempt + 1))
                continue
            if attempt == 2:
                raise RuntimeError(f"claude -p 실패: {msg}")
            time.sleep(5)
        return ""

    def _mock_answer(self, hint: dict) -> str:
        """mock: condition 에 따라 정답률이 달라지는 가짜 풀이자 / 가짜 제안자."""
        kind = hint.get("kind")
        if kind == "solve":
            p = {"none": 0.35, "brief": 0.55, "page": 0.62}.get(hint.get("condition"), 0.5)
            if hint.get("patched"):
                p += 0.08
            q = hint["q"]
            if self.rng.random() < p:
                ans = q["answer"]
            else:
                if q["type"] == "mc":
                    ans = self.rng.choice([i for i in range(len(q["options"])) if i != q["answer"]])
                else:
                    ans = float(q["answer"]) * self.rng.choice([0.5, 1.7, 2.0])
            return f"(mock) 풀이 생략\nANSWER: {ans if q['type']=='num' else ans + 1}"
        if kind == "propose":
            return json.dumps({"patches": [{
                "card_id": hint.get("card_id", "c1"),
                "title": "보강 설명 (mock)",
                "pro": "mock 모드에서 생성된 자리표시 설명입니다. 실제 실행에서는 근거를 인용한 보강 설명이 들어갑니다.",
                "easy": "mock 모드의 쉬운 설명 자리표시입니다.",
                "sources": ["content/briefs/" + hint.get("week", "weekNN") + ".md"],
                "reason": "오답률이 높은 개념"}]}, ensure_ascii=False)
        return "(mock)"


# ---------------------------------------------------------------- 유틸
def jdump(obj, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


def log(*a):
    print(*a, file=sys.stderr, flush=True)

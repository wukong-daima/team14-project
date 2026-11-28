"""quiz-forge 의 추가 세트(--set b): 이미 있는 은행(weekNN-agent.json)을 덮어쓰지 않고 문항을 더한다.
기존 문항 id(w09a-*)는 전이 사다리 2단 문항과 1:1 짝이라 바뀌면 안 된다."""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _forge():
    spec = importlib.util.spec_from_file_location("forge", ROOT / ".claude/skills/quiz-forge/scripts/forge.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_default_names_unchanged():
    f = _forge()
    assert f.short("week09") == "w09a"
    assert f.ws("week09").replace("\\", "/").endswith("_workspace/quiz/week09")
    assert f.bank_name("week09") == "week09-agent.json"
    assert f.report_name("week09") == "week09-agent.report.json"


def test_set_gets_its_own_ids_workspace_and_files():
    f = _forge()
    f.SET = "b"
    assert f.short("week09") == "w09b"
    assert f.ws("week09").replace("\\", "/").endswith("_workspace/quiz/week09-b")
    assert f.ws("week09", 2).replace("\\", "/").endswith("_workspace/quiz/week09-b/r2")
    assert f.bank_name("week09") == "week09-agent-b.json"
    assert f.report_name("week09") == "week09-agent-b.report.json"


def test_set_checks_duplicates_against_first_agent_bank():
    f = _forge()
    assert "week09-agent.json" not in {src for src, _ in f.existing_questions("week09")}
    f.SET = "b"
    srcs = {src for src, _ in f.existing_questions("week09")}
    assert "week09-agent.json" in srcs            # 같은 주차의 먼저 만든 은행과는 겹치면 안 된다
    assert "week09-agent-b.json" not in srcs      # 자기 자신과는 비교하지 않는다
    assert "week10-agent.json" not in srcs        # 다른 주차 에이전트 은행은 예전처럼 뺀다
    assert os.path.basename(f.bank_name("week09")) not in srcs

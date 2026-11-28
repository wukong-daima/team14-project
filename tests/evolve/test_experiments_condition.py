"""행동 실험 E1·E2 를 자료 조건(none/brief/page)을 골라 돌릴 수 있어야 한다.
페이지 조건은 9주차에서 94~100% 라 효과가 보일 여지가 없다. 자료 없음 조건에서 따로 잰다."""
from __future__ import annotations

import json
import sys

import experiments


def _run(monkeypatch, tmp_path, *argv):
    monkeypatch.setattr(experiments, "REPORT_DIR", tmp_path)
    monkeypatch.setattr(experiments, "update_report_index", lambda: None)
    monkeypatch.setattr(sys, "argv", ["experiments.py", *argv])
    experiments.main()
    return {p.name: json.loads(p.read_text(encoding="utf-8")) for p in tmp_path.glob("exp-*.json")}


def test_e1_runs_under_chosen_condition_with_repeats(monkeypatch, tmp_path):
    out = _run(monkeypatch, tmp_path, "e1", "--weeks", "week09", "--condition", "none", "--reps", "2", "--limit", "3", "--mock")
    r = out["exp-e1-week09-none-mock.json"]
    assert r["condition"] == "none"
    assert [x["effort"] for x in r["runs"]] == ["low", "medium", "high", "xhigh"]
    assert all(x["condition"] == "none" and x["k"] == 2 for x in r["runs"])


def test_e2_runs_under_chosen_condition(monkeypatch, tmp_path):
    out = _run(monkeypatch, tmp_path, "e2", "--weeks", "week09", "--condition", "none", "--k", "4", "--limit", "3", "--mock")
    r = out["exp-e2-week09-none-mock.json"]
    assert r["runs"][0]["condition"] == "none" and r["runs"][0]["k"] == 4


def test_default_condition_keeps_old_report_name(monkeypatch, tmp_path):
    out = _run(monkeypatch, tmp_path, "e2", "--weeks", "week09", "--k", "2", "--limit", "2", "--mock")
    assert list(out) == ["exp-e2-week09-mock.json"]
    assert out["exp-e2-week09-mock.json"]["runs"][0]["condition"] == "page"

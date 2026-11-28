from __future__ import annotations

import pytest

from conftest import raw_question
from livelab import core


def test_bank_week09_has_25_questions_without_answers():
    b = core.bank("week09")
    assert b["set"] == "week09" and b["weeks"] == ["week09"]
    assert len(b["questions"]) == 25
    for q in b["questions"]:
        assert set(q) == {"id", "week", "type", "q", "options", "concept"}


def test_bank_seed_has_39_questions():
    b = core.bank("seed")
    assert b["weeks"] == ["week02", "week04", "week08"] and len(b["questions"]) == 39


def test_bank_num_question_has_no_options():
    nums = [q for q in core.bank("week09")["questions"] if q["type"] == "num"]
    assert nums and all(q["options"] is None for q in nums)


def test_bank_unknown_set_is_400():
    with pytest.raises(core.LiveError) as e:
        core.bank("week99")
    assert e.value.status == 400


@pytest.mark.parametrize("qid,cond", [("w09a-c03", "everything"), ("nope", "none"), ("", "none")])
def test_solve_rejects_unknown_inputs(qid, cond):
    with pytest.raises(core.LiveError) as e:
        core.solve(qid, cond)
    assert e.value.status == 400


def test_solve_grades_correct_answer(fake_llm_factory):
    q = raw_question("w09a-c03")
    r = core.solve("w09a-c03", "none", llm=fake_llm_factory(f"풀이\nANSWER: {q['answer'] + 1}"))
    assert r["qid"] == "w09a-c03" and r["condition"] == "none"
    assert r["correct"] is True and r["pred"] == q["answer"]
    assert r["input_tokens"] == 120 and r["output_tokens"] == 30 and r["ms"] >= 0


def test_solve_grades_wrong_answer(fake_llm_factory):
    q = raw_question("w09a-c03")
    wrong = (q["answer"] + 1) % len(q["options"])
    r = core.solve("w09a-c03", "none", llm=fake_llm_factory(f"ANSWER: {wrong + 1}"))
    assert r["correct"] is False and r["pred"] == wrong


def test_solve_unparseable_answer_is_wrong_not_error(fake_llm_factory):
    r = core.solve("w09a-c03", "page", llm=fake_llm_factory("모르겠습니다"))
    assert r["pred"] is None and r["correct"] is False


def test_solve_prompt_has_context_only_when_condition_gives_one(fake_llm_factory):
    llm = fake_llm_factory("ANSWER: 1")
    core.solve("w09a-c03", "none", llm=llm)
    assert "[참고 자료" not in llm.last_user and llm.last_user.startswith("[문제]\n")
    assert llm.last_model == "claude-haiku-5-5" and llm.last_effort == "low"
    llm = fake_llm_factory("ANSWER: 1")
    core.solve("w09a-c03", "page", llm=llm)
    assert llm.last_user.startswith("[참고 자료: week09]\n") and "\n\n[문제]\n" in llm.last_user


def test_solve_never_sends_the_answer_key_to_the_solver(fake_llm_factory):
    q = raw_question("w09a-c03")
    llm = fake_llm_factory("ANSWER: 1")
    core.solve("w09a-c03", "none", llm=llm)
    assert q["explanation"][:40] not in llm.last_user


def test_solve_is_503_when_disabled(monkeypatch):
    monkeypatch.setenv("LIVE_DISABLED", "1")
    with pytest.raises(core.LiveError) as e:
        core.solve("w09a-c03", "none")
    assert e.value.status == 503


def test_solve_with_mock_env_returns_a_graded_result():
    r = core.solve("w09a-c03", "brief")
    assert isinstance(r["correct"], bool) and isinstance(r["input_tokens"], int)


@pytest.mark.parametrize("env,expected", [
    ({}, False),
    ({"ANTHROPIC_API_KEY": ""}, False),
    ({"ANTHROPIC_API_KEY": "x"}, True),
    ({"ANTHROPIC_API_KEY": "x", "LIVE_DISABLED": "1"}, False),
    ({"ANTHROPIC_API_KEY": "x", "LIVE_DISABLED": "true"}, False),
    ({"LIVE_MOCK": "1"}, True),
    ({"LIVE_MOCK": "1", "LIVE_DISABLED": "1"}, False),
])
def test_is_live(env, expected):
    assert core.is_live(env) is expected


def test_llm_retry_exhaustion_maps_to_429_without_leaking_detail(raising_llm_factory):
    with pytest.raises(core.LiveError) as e:
        core.solve("w09a-c03", "none", llm=raising_llm_factory(RuntimeError("API 재시도 실패")))
    assert e.value.status == 429 and "재시도 실패" not in e.value.message


def test_llm_api_error_maps_to_502(raising_llm_factory):
    import anthropic
    import httpx

    exc = anthropic.APIConnectionError(request=httpx.Request("POST", "https://api.anthropic.com/v1/messages"))
    with pytest.raises(core.LiveError) as e:
        core.solve("w09a-c03", "none", llm=raising_llm_factory(exc))
    assert e.value.status == 502


def test_health_lists_sets_with_counts():
    h = core.health()
    assert h["live"] is True and h["model"] == "claude-haiku-5-5"
    assert {(s["name"], s["n"]) for s in h["sets"]} == {("week09", 25), ("seed", 39)}


def test_reports_include_recorded_week09_run():
    r = next(x for x in core.reports() if x["weeks"] == "week09")
    assert [(run["condition"], run["acc"]) for run in r["runs"]] == [("none", 0.6667), ("brief", 1.0), ("page", 0.9444)]
    assert r["runs"][0]["n"] == 18 and len(r["runs"][0]["acc_ci95"]) == 2


def test_mock_solver_varies_by_cell_and_is_repeatable():
    """가짜 풀이자는 칸마다 다른 결과를 내야 화면의 오답·정답 표시를 확인할 수 있다."""
    ids = [q["id"] for q in core.bank("week09")["questions"]]
    first = [core.solve(i, "none")["correct"] for i in ids]
    assert True in first and False in first
    assert first == [core.solve(i, "none")["correct"] for i in ids]


def test_health_reports_whether_materials_are_readable():
    """배포 번들에 브리프·주차 페이지가 빠지면 자료 조건이 '자료 없음'과 같아진다. health 로 드러낸다."""
    m = core.health()["materials"]
    assert set(m) == {"week02", "week04", "week08", "week09"}
    assert all(v == {"brief": True, "page": True} for v in m.values())


def test_solve_is_502_when_material_is_missing(monkeypatch, fake_llm_factory):
    monkeypatch.setattr(core.ev_common, "context_for", lambda week, condition, *a: "")
    with pytest.raises(core.LiveError) as e:
        core.solve("w09a-c03", "page", llm=fake_llm_factory("ANSWER: 1"))
    assert e.value.status == 502
    core.solve("w09a-c03", "none", llm=fake_llm_factory("ANSWER: 1"))  # 자료 없음 조건은 빈 자료가 정상


class _RaisingMessages:
    def __init__(self, exc):
        self.exc, self.calls = exc, 0

    def create(self, **kw):
        self.calls += 1
        raise self.exc


def _rate_limit_error():
    import anthropic
    import httpx

    req = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
    return anthropic.RateLimitError("rate limited", response=httpx.Response(429, request=req), body=None)


def test_real_backend_rate_limit_fails_fast_as_429(monkeypatch):
    """실제 API 경로: 한도 초과면 서버 함수 안에서 재시도·대기하지 않고 바로 429 를 돌려준다
    (evolve 의 LLM.ask 는 최대 60초씩 잠들어 서버 함수 시간 제한 60초를 넘긴다)."""
    monkeypatch.delenv("LIVE_MOCK", raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-not-real")
    msgs = _RaisingMessages(_rate_limit_error())
    monkeypatch.setattr(core, "_anthropic_client", lambda: type("C", (), {"messages": msgs})())
    monkeypatch.setattr(core.time, "sleep", lambda s: (_ for _ in ()).throw(AssertionError(f"slept {s}s")))
    with pytest.raises(core.LiveError) as e:
        core.solve("w09a-c03", "none")
    assert e.value.status == 429 and msgs.calls == 1


def test_real_backend_server_error_fails_fast_as_502(monkeypatch):
    import anthropic
    import httpx

    monkeypatch.delenv("LIVE_MOCK", raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-not-real")
    req = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
    msgs = _RaisingMessages(anthropic.InternalServerError("boom", response=httpx.Response(529, request=req), body=None))
    monkeypatch.setattr(core, "_anthropic_client", lambda: type("C", (), {"messages": msgs})())
    monkeypatch.setattr(core.time, "sleep", lambda s: (_ for _ in ()).throw(AssertionError(f"slept {s}s")))
    with pytest.raises(core.LiveError) as e:
        core.solve("w09a-c03", "none")
    assert e.value.status == 502 and msgs.calls == 1


def test_real_backend_client_has_no_sdk_retries_and_a_short_timeout(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-not-real")
    c = core._anthropic_client()
    assert c.max_retries == 0 and float(c.timeout) <= 30


def test_rounds_list_what_each_round_changed():
    """진화 기록 화면: 라운드마다 언제, 어느 주차의 어떤 카드를 왜 고쳤는지와 전후 정답률."""
    r = next(x for x in core.rounds() if x["round"] == 1)
    assert (r["date"], r["weeks"], r["accepted"]) == ("2026-11-23", ["week09"], True)
    assert (r["acc_before"], r["acc_after"], r["n_public"], r["ci_overlap"]) == (0.9444, 1.0, 18, True)
    assert r["weak_concepts"] == [{"week": "week09", "concept": "workflow-design-adas-aflow", "ids": ["w09a-c28"]}]
    p = r["patches"][0]
    assert (p["week"], p["card_id"]) == ("week09", "c4")
    assert p["title"].startswith("워크플로우 디자인") and p["reason"] and p["easy"]


def test_rounds_skip_mock_and_sort_newest_first(tmp_path, monkeypatch):
    import json as _json
    for n, mock in ((1, False), (2, True), (3, False)):
        (tmp_path / f"round-{n:02d}.json").write_text(_json.dumps({"round": n, "mock": mock}), encoding="utf-8")
    (tmp_path / "round-04.json").write_text("{broken", encoding="utf-8")
    monkeypatch.setattr(core.ev_common, "REPORT_DIR", tmp_path)
    assert [x["round"] for x in core.rounds()] == [3, 1]

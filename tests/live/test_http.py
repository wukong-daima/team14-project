from __future__ import annotations

import json

import pytest

from livelab import core, http


def test_health_ok():
    s, b = http.handle("GET", "/api/health", {}, b"")
    assert s == 200 and b["live"] is True


def test_bank_default_set_is_week09():
    s, b = http.handle("GET", "/api/bank", {}, b"")
    assert s == 200 and b["set"] == "week09" and len(b["questions"]) == 25


def test_bank_seed_set():
    s, b = http.handle("GET", "/api/bank", {"set": "seed"}, b"")
    assert s == 200 and len(b["questions"]) == 39


def test_bank_unknown_set_is_400_with_error_text():
    s, b = http.handle("GET", "/api/bank", {"set": "x"}, b"")
    assert s == 400 and isinstance(b["error"], str) and b["error"]


def test_solve_roundtrip():
    body = json.dumps({"qid": "w09a-c03", "condition": "none"}).encode()
    s, b = http.handle("POST", "/api/solve", {}, body)
    assert s == 200 and b["qid"] == "w09a-c03" and isinstance(b["correct"], bool)


@pytest.mark.parametrize("body", [
    b"", b"not json", b"[]", b"null", b'{"qid": 3, "condition": "none"}',
    b'{"qid": "w09a-c03"}', b'{"qid": "w09a-c03", "condition": ["none"]}', b"\xff\xfe",
])
def test_solve_bad_body_is_400(body):
    s, b = http.handle("POST", "/api/solve", {}, body)
    assert s == 400 and "error" in b


def test_solve_disabled_is_503(monkeypatch):
    monkeypatch.setenv("LIVE_DISABLED", "1")
    body = json.dumps({"qid": "w09a-c03", "condition": "none"}).encode()
    s, b = http.handle("POST", "/api/solve", {}, body)
    assert s == 503 and "error" in b


def test_reports_ok():
    s, b = http.handle("GET", "/api/reports", {}, b"")
    assert s == 200 and any(r["weeks"] == "week09" for r in b["reports"])


def test_wrong_method_is_405():
    assert http.handle("GET", "/api/solve", {}, b"")[0] == 405
    assert http.handle("POST", "/api/health", {}, b"")[0] == 405


def test_unknown_path_is_404():
    assert http.handle("GET", "/api/nope", {}, b"")[0] == 404


def test_trailing_slash_and_query_free_path_match():
    assert http.handle("GET", "/api/health/", {}, b"")[0] == 200


def test_unexpected_exception_is_500_without_detail(monkeypatch):
    def boom():
        raise ValueError("secret detail")

    monkeypatch.setattr(core, "health", boom)
    s, b = http.handle("GET", "/api/health", {}, b"")
    assert s == 500 and b == {"error": "서버 오류"}


def test_deeply_nested_body_is_400_not_500():
    s, b = http.handle("POST", "/api/solve", {}, b"[" * 4096)
    assert s == 400 and "error" in b


def test_reports_include_rounds():
    s, b = http.handle("GET", "/api/reports", {}, b"")
    assert s == 200 and any(r["round"] == 1 for r in b["rounds"])

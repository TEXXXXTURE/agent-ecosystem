"""终止条件与两档分流单测（AutoGen 式 TerminationCondition 脱离 LLM 单测）。"""
import pytest

from orchestrator.termination import Termination, classify_failure


@pytest.mark.parametrize(
    "failure,expected",
    [
        ({"category": "mechanical", "code": "test_failed"}, "mechanical"),
        ({"code": "schema_invalid"}, "mechanical"),
        ({"code": "exit_nonzero"}, "mechanical"),
        ({"code": "param_missing"}, "mechanical"),
        ({"code": "requirement_ambiguous"}, "directional"),  # 非机器可判 → 升级 owner
        ({"code": "scope_change"}, "directional"),
        ({"category": "directional"}, "directional"),
        ({"code": "unknown_code"}, "directional"),  # 安全默认
        ({}, "directional"),
    ],
)
def test_classify_failure(failure: dict, expected: str) -> None:
    assert classify_failure(failure) == expected


def test_termination_schema_passed() -> None:
    t = Termination("schema_passed")
    assert t.should_stop({"schema_ok": True})
    assert not t.should_stop({"schema_ok": False})


def test_termination_needs_owner() -> None:
    t = Termination("needs_owner")
    assert t.should_stop({"verdict": "needs_owner"})
    assert not t.should_stop({"verdict": "mechanical"})


def test_termination_max_retry() -> None:
    t = Termination("max_retry")
    assert t.should_stop({"retries": 3, "max_retries": 3})
    assert not t.should_stop({"retries": 2, "max_retries": 3})

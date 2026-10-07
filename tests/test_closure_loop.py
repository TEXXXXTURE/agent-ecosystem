"""6 步闭环状态机测试：终态断言 + 两档分流断言（Anthropic 终态评估方法论）。

只查两个终态：
1. owner 拍板后产出物过没过 schema
2. 失败有没有带原因正确回流（⑤→③ / ④ 两档）
"""
import pytest

from orchestrator.closure import ClosureLoop, State
from orchestrator.gates import OwnerGate
from tests.test_schemas import VALID_EXEC_DIFF, VALID_PM_PLAN

APPROVE = {"decision": "采纳", "options": [{"name": "方案A", "consequence": "快"}],
           "rationale": "owner 拍板", "owner": "A"}
REDIRECT = {"decision": "改走 B", "options": [{"name": "B", "consequence": "稳"}],
            "rationale": "owner 定夺", "owner": "A"}


def _pm_ok(task: str) -> dict:
    plan = dict(VALID_PM_PLAN)
    plan["title"] = task[:20] or plan["title"]
    return plan


def _exec_ok(plan: dict, prior_failure: dict | None) -> dict:
    diff = dict(VALID_EXEC_DIFF)
    diff["plan_id"] = plan.get("id")
    return diff


def test_happy_path_reaches_done() -> None:
    """happy path：PM 产出 → owner 拍板 → 执行 done → 校验过 → DONE。"""
    loop = ClosureLoop(pm_handler=_pm_ok, exec_handler=_exec_ok)
    result = loop.run("做一个素材索引功能", owner_decisions=[APPROVE])
    assert result.succeeded
    assert result.state == State.DONE
    # 终态断言 1：owner 拍板后产出物过 schema（未产生 schema 失败）
    assert not [f for f in result.failures if f["code"] == "schema_invalid"]
    # 终态断言 2：无未回流失败
    assert result.failures == []
    # trace 覆盖关键节点
    trace = result.trace
    assert "owner_gate" in trace and "verify" in trace


def test_mechanical_failure_self_heals_without_owner() -> None:
    """机械问题（执行异常）→ 自解 + 机器兜底，不升级 owner，最终 DONE。"""
    calls = {"exec": 0}

    def exec_mech_then_ok(plan, prior_failure):
        calls["exec"] += 1
        if calls["exec"] == 1:
            raise RuntimeError("TypeError: NoneType is not iterable")  # 机械型异常
        return _exec_ok(plan, prior_failure)

    loop = ClosureLoop(pm_handler=_pm_ok, exec_handler=exec_mech_then_ok)
    result = loop.run("任务", owner_decisions=[APPROVE])  # 只有方案拍板一次
    assert result.succeeded
    # 机械失败已回流并自解：无第二次 owner 升级
    assert len(result.decision_records) == 1
    mech = [f for f in result.failures if f["code"] == "other_directional"]
    assert not mech


def test_directional_failure_escalates_to_owner() -> None:
    """方向问题 → 升级 owner 一句话定夺（不经过编码互审循环），继续执行到 DONE。"""
    calls = {"exec": 0}

    def exec_blocked_then_ok(plan, prior_failure):
        calls["exec"] += 1
        if calls["exec"] == 1:
            return {
                "schema_version": "exec_diff@0.1", "plan_id": plan.get("id"),
                "leaf": "video-cut-agent", "changes": [{"file": "x", "action": "create"}],
                "status": "blocked",
                "blocker": {"category": "directional", "summary": "需求歧义：索引范围未定"},
            }
        return _exec_ok(plan, prior_failure)

    loop = ClosureLoop(pm_handler=_pm_ok, exec_handler=exec_blocked_then_ok)
    result = loop.run("任务", owner_decisions=[APPROVE, REDIRECT])  # 方案拍板 + 方向升级
    assert result.succeeded
    # 终态断言：方向问题正确回流（升级 owner 一次）
    assert len(result.decision_records) == 2
    assert result.decision_records[1]["decision"] == "改走 B"


def test_max_retry_fails_when_pm_plan_never_passes_schema() -> None:
    """PM 方案反复不过 schema → 机械兜底重试到上限 → FAILED（防循环空转）。"""

    def pm_bad(task: str) -> dict:
        return {"schema_version": "pm_plan@0.1", "title": "缺字段"}  # 缺 required

    loop = ClosureLoop(pm_handler=pm_bad, exec_handler=_exec_ok, max_retries=2)
    result = loop.run("任务")
    assert result.state == State.FAILED
    assert all(f["category"] == "mechanical" for f in result.failures)
    assert len(result.failures) >= 2  # 重试上限

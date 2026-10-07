"""6 步协作闭环显式状态机（PRD FR-03 / NFR-03）。

形态：闭环 = 显式状态机（图），不写进编排 Agent 的 prompt 让它自觉。
- 节点：PM 产出 → schema 校验 → owner_gate → 执行 → 两档分流 → 校验回环。
- 与 LLM 解耦：PM / 执行通过 handler 注入（生产接 openai-agents 或模型 API，测试注入假 handler）。
- 强制只落在：schema 校验（contracts/validators）、两档分流（termination.py）、owner_gate（gates.py）。

用法（CLI）:
    python -m orchestrator.closure "任务描述"
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # 允许直接以模块运行

from contracts.validators.schema_validator import validate_against_schema
from orchestrator.gates import OwnerGate
from orchestrator.termination import Termination, classify_failure


class State(Enum):
    IDLE = "idle"
    PLANNING = "planning"        # ① PM 产出方案
    SCHEMA_CHECK = "schema_check"  # ① 机器校验
    OWNER_GATE = "owner_gate"    # ② ④ owner 拍板（人环，0 token）
    EXECUTING = "executing"      # ③ 编码执行
    DIAGNOSIS = "diagnosis"      # ④ 两档分流
    VERIFY = "verify"            # ⑤ 机器校验
    DONE = "done"                # 交付
    FAILED = "failed"            # 终止（MaxRetry）


@dataclass
class LoopResult:
    state: State
    pm_plan: dict | None = None
    exec_diff: dict | None = None
    decision_records: list[dict] = field(default_factory=list)
    trace: list[str] = field(default_factory=list)
    failures: list[dict] = field(default_factory=list)

    @property
    def succeeded(self) -> bool:
        return self.state == State.DONE


class ClosureLoop:
    """6 步闭环状态机。handlers 可注入（测试用假实现，生产接真实叶片）。"""

    def __init__(
        self,
        pm_handler: Callable[[str], dict],
        exec_handler: Callable[[dict, dict | None], dict],
        owner_gate: OwnerGate | None = None,
        max_retries: int = 3,
        schema_checker: Callable[[dict, str], list[str]] = validate_against_schema,
    ) -> None:
        self.pm_handler = pm_handler
        self.exec_handler = exec_handler
        self.owner_gate = owner_gate or OwnerGate()
        self.max_retries = max_retries
        self.schema_checker = schema_checker

    # ---- 状态迁移 ----

    def run(self, task: str, owner_decisions: list[dict] | None = None) -> LoopResult:
        """驱动闭环。owner_decisions 供测试注入拍板；生产由外部 resume() 提供。"""
        result = LoopResult(state=State.IDLE)
        decisions = list(owner_decisions or [])
        retries = 0
        state = State.PLANNING
        pm_plan: dict | None = None
        exec_diff: dict | None = None
        prior_failure: dict | None = None

        while True:
            result.trace.append(state.value)
            # 终止条件（AutoGen 式对象）
            if Termination("max_retry", "超过最大重试").should_stop({"retries": retries, "max_retries": self.max_retries}):
                state = State.FAILED
                break

            if state == State.PLANNING:
                pm_plan = self.pm_handler(task)
                state = State.SCHEMA_CHECK

            elif state == State.SCHEMA_CHECK:
                errors = self.schema_checker(pm_plan or {}, "pm_plan")
                if errors:
                    failure = {
                        "category": "mechanical",
                        "code": "schema_invalid",
                        "summary": "PM 方案未通过 pm_plan schema",
                        "evidence": errors,
                        "retryable": True,
                    }
                    result.failures.append(failure)
                    retries += 1
                    state = State.PLANNING  # PM 自修（机械兜底）
                else:
                    state = State.OWNER_GATE

            elif state == State.OWNER_GATE:
                question = f"方案「{(pm_plan or {}).get('title', '?')}」请拍板（方向对不对，一句话）"
                if decisions:
                    decision = decisions.pop(0)
                else:
                    decision = self.owner_gate.wait(question)
                decision.setdefault("related_plan_id", (pm_plan or {}).get("id"))
                result.decision_records.append(decision)
                state = State.EXECUTING

            elif state == State.EXECUTING:
                try:
                    exec_diff = self.exec_handler(pm_plan or {}, prior_failure)
                except Exception as e:  # 执行异常 = 机器可检测信号（等价 exit code 非零）→ 机械自解
                    failure = {"category": "mechanical", "code": "exit_nonzero",
                               "summary": f"执行异常（机器可检测）: {e}", "evidence": [str(e)], "retryable": True}
                    result.failures.append(failure)
                    prior_failure = failure
                    state = State.DIAGNOSIS
                    continue
                if exec_diff.get("status") == "blocked":
                    failure = exec_diff.get("blocker") or {
                        "category": "directional", "code": "other_directional",
                        "summary": "执行阻塞（无结构化 blocker）", "evidence": [], "retryable": True}
                    failure.setdefault("retryable", True)
                    result.failures.append(failure)
                    prior_failure = failure
                    state = State.DIAGNOSIS
                else:
                    prior_failure = None
                    state = State.VERIFY

            elif state == State.DIAGNOSIS:
                category = classify_failure(prior_failure or {})
                if category == "mechanical":
                    # 机械问题 → 自解 + 机器兜底（不升级）
                    retries += 1
                    state = State.EXECUTING
                else:
                    # 方向问题 → 直接升级 owner（0 token，不做编码互审循环）
                    question = f"方向问题请定夺: {(prior_failure or {}).get('summary', '?')}"
                    if decisions:
                        decision = decisions.pop(0)
                    else:
                        decision = self.owner_gate.wait(question)
                    decision.setdefault("related_plan_id", (pm_plan or {}).get("id"))
                    result.decision_records.append(decision)
                    state = State.EXECUTING

            elif state == State.VERIFY:
                errors = self.schema_checker(exec_diff or {}, "exec_diff")
                if errors:
                    failure = {"category": "mechanical", "code": "schema_invalid",
                               "summary": "执行 diff 未通过 exec_diff schema",
                               "evidence": errors, "retryable": True}
                    result.failures.append(failure)
                    prior_failure = failure
                    retries += 1
                    state = State.EXECUTING  # 失败带原因回流（⑤→③）
                else:
                    state = State.DONE

            if state == State.DONE or state == State.FAILED:
                break

        result.state = state
        result.pm_plan = pm_plan
        result.exec_diff = exec_diff
        return result


def _cli(task: str) -> None:
    """生产入口（最小）：提示接入真实 PM/执行 handler 与 owner 通知。"""
    print(f"[closure] 任务: {task}")
    print("[closure] 请先接入真实 handler（pm_handler / exec_handler）与 owner 通知通道，再驱动闭环。")
    print("[closure] 当前为骨架，可用 tests/test_closure_loop.py 的假 handler 验证状态机。")
    sys.exit(2)


if __name__ == "__main__":
    _cli(" ".join(sys.argv[1:]))

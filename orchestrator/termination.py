"""两档分流与终止条件对象（AutoGen 式可组合）。

核心规则：方向问题升级 owner、机械问题机器兜底。
- 机器可检测（测试红 / schema 错 / exit code 非零 / 参数缺失）→ mechanical（自解 + 机器兜底）
- 其余一律 → directional（升级 owner，0 token 兜底）
"""
from __future__ import annotations

from dataclasses import dataclass, field

# 机器可判定的错误码（failure_reason.code 的机械档全集）
MECHANICAL_CODES = {
    "test_failed",
    "schema_invalid",
    "exit_nonzero",
    "param_missing",
}


@dataclass(frozen=True)
class Termination:
    """终止条件对象：命中即 stop/升级，可组合（| = OR，& = AND 语义见组合函数）。"""

    kind: str  # "schema_passed" | "needs_owner" | "max_retry"
    reason: str = ""
    payload: dict = field(default_factory=dict)

    def should_stop(self, ctx: dict) -> bool:
        """喂上下文断言是否命中。"""
        if self.kind == "schema_passed":
            return bool(ctx.get("schema_ok"))
        if self.kind == "needs_owner":
            return ctx.get("verdict") == "needs_owner"
        if self.kind == "max_retry":
            return int(ctx.get("retries", 0)) >= int(ctx.get("max_retries", 3))
        return False


def classify_failure(failure: dict) -> str:
    """两档分流（程序判定，不消耗 LLM）。

    返回 "mechanical" 或 "directional"。
    """
    category = failure.get("category")
    if category == "mechanical":
        return "mechanical"
    if category == "directional":
        return "directional"
    code = failure.get("code")
    if code in MECHANICAL_CODES:
        return "mechanical"
    # 安全默认：无法机器判定的 → 升级 owner（方向问题升级 owner）
    return "directional"


def combine_or(*terms: Termination) -> Termination:
    """组合终止条件（任一命中即终止）。"""
    kinds = [t.kind for t in terms]
    return Termination(kind="|".join(kinds), reason=" OR ".join(t.reason for t in terms))


def combine_and(*terms: Termination) -> Termination:
    """组合终止条件（全部命中才终止）。"""
    kinds = [t.kind for t in terms]
    return Termination(kind="&".join(kinds), reason=" AND ".join(t.reason for t in terms))

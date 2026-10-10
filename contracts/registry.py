"""契约注册表 —— 集成层规则本体（R2 / FR-01 / FR-02）。

registry.json 声明每个产出物的 producer / consumer 与合法 handoff 边。
本模块负责：
  1. 加载并校验注册表自身结构；
  2. 与 leaves/*.md 的输入/输出契约做一致性对账（防止叶片声明与注册表漂移）；
  3. handoff 断言：任何产出物流转必须能在注册表找到一条合法边，否则显式报错。

硬规则不靠 Agent 自觉：无契约可依时，assert_handoff 抛 ContractNotFoundError。

用法:
    from contracts.registry import load_registry, assert_handoff, validate_with_leaves
    reg = load_registry()
    assert_handoff(reg, "pm_plan", "project-pm-tracker", "owner_gate")
"""
from __future__ import annotations

import json
from pathlib import Path

REGISTRY_PATH = Path(__file__).resolve().parent / "registry.json"


class RegistryError(Exception):
    """注册表结构非法。"""


class ContractNotFoundError(Exception):
    """产出物无契约可依（未登记产出物 / producer / consumer / handoff 边）。"""


def load_registry(path: Path = REGISTRY_PATH) -> dict:
    """加载 registry.json 并做最小结构校验。"""
    if not path.exists():
        raise RegistryError(f"契约注册表不存在: {path}")
    try:
        reg = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise RegistryError(f"契约注册表不是合法 JSON: {e}") from e
    for key in ("registry_version", "artifacts", "handoffs"):
        if key not in reg:
            raise RegistryError(f"契约注册表缺少必需字段: {key}")
    if not isinstance(reg["artifacts"], dict):
        raise RegistryError("artifacts 必须是映射")
    if not isinstance(reg["handoffs"], list):
        raise RegistryError("handoffs 必须是数组")
    return reg


def producers_of(reg: dict, artifact: str) -> list[str]:
    spec = reg["artifacts"].get(artifact)
    if spec is None:
        raise ContractNotFoundError(
            f"未登记的产出物类型: {artifact}（registry artifacts 中不存在）"
        )
    return list(spec.get("produced_by", []))


def consumers_of(reg: dict, artifact: str) -> list[str]:
    spec = reg["artifacts"].get(artifact)
    if spec is None:
        raise ContractNotFoundError(
            f"未登记的产出物类型: {artifact}（registry artifacts 中不存在）"
        )
    return list(spec.get("consumed_by", []))


def assert_handoff(reg: dict, artifact: str, producer: str, consumer: str) -> None:
    """断言一次产出物传递合法：产出物已登记、producer/consumer 匹配、存在 handoff 边。

    任一不满足 → ContractNotFoundError（显式报错，不静默流转）。
    """
    if artifact not in reg["artifacts"]:
        raise ContractNotFoundError(
            f"产出物 {artifact} 无契约可依：未在 registry 登记"
        )
    if producer not in producers_of(reg, artifact):
        raise ContractNotFoundError(
            f"产出物 {artifact} 不允许由 {producer} 产出"
            f"（合法 producer: {producers_of(reg, artifact)}）"
        )
    if consumer not in consumers_of(reg, artifact):
        raise ContractNotFoundError(
            f"产出物 {artifact} 不允许交付给 {consumer}"
            f"（合法 consumer: {consumers_of(reg, artifact)}）"
        )
    for edge in reg["handoffs"]:
        if (
            edge.get("artifact") == artifact
            and edge.get("from") == producer
            and edge.get("to") == consumer
        ):
            return
    raise ContractNotFoundError(
        f"无 handoff 边: {producer} → {consumer}（artifact={artifact}）"
    )


def validate_with_leaves(reg: dict, leaves: list) -> list[str]:
    """注册表与叶片声明一致性对账，返回错误列表（空 = 一致）。

    只做反向核对：每个实际存在的叶片所声明的 output/input contract，
    必须在注册表把该叶片登记为对应 producer / consumer。
    注册表引用尚未建立的叶片（如 executor/verify）不报缺失。
    """
    errors: list[str] = []
    for leaf in leaves:
        for artifact in leaf.output_contract:
            if artifact not in reg["artifacts"]:
                errors.append(
                    f"叶片 {leaf.name} 声明产出 {artifact}，但 registry 未登记该产出物"
                )
                continue
            if leaf.name not in producers_of(reg, artifact):
                errors.append(
                    f"叶片 {leaf.name} 声明产出 {artifact}，"
                    f"但 registry 的 produced_by={producers_of(reg, artifact)} 不含它"
                )
        for artifact in leaf.input_contract:
            # 外部原始材料（未登记为系统产出物）放行：只对已登记的产出物核对 consumer。
            if artifact not in reg["artifacts"]:
                continue
            if leaf.name not in consumers_of(reg, artifact):
                errors.append(
                    f"叶片 {leaf.name} 声明消费 {artifact}，"
                    f"但 registry 的 consumed_by={consumers_of(reg, artifact)} 不含它"
                )
    return errors

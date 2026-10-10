"""契约注册表测试（R2 验收：无契约可依时显式报错；注册表与叶片一致）。"""
from __future__ import annotations

import copy

import pytest

from contracts.registry import (
    ContractNotFoundError,
    RegistryError,
    assert_handoff,
    load_registry,
    producers_of,
    consumers_of,
    validate_with_leaves,
)
from orchestrator.router import discover_leaves


@pytest.fixture(scope="module")
def reg():
    return load_registry()


# ---- 注册表自身 ----

def test_registry_loads_with_four_artifacts(reg):
    assert {"pm_plan", "decision_record", "exec_diff", "failure_reason"} <= set(
        reg["artifacts"]
    )
    assert isinstance(reg["handoffs"], list) and reg["handoffs"]


def test_load_registry_missing_file(tmp_path):
    with pytest.raises(RegistryError):
        load_registry(tmp_path / "nope.json")


def test_load_registry_bad_json(tmp_path):
    p = tmp_path / "registry.json"
    p.write_text("{ not json", encoding="utf-8")
    with pytest.raises(RegistryError):
        load_registry(p)


# ---- 合法 handoff ----

@pytest.mark.parametrize(
    "artifact,producer,consumer",
    [
        ("pm_plan", "project-pm-tracker", "owner_gate"),
        ("decision_record", "owner_gate", "executor"),
        ("exec_diff", "executor", "verify"),
        ("failure_reason", "verify", "executor"),
        ("failure_reason", "executor", "executor"),
    ],
)
def test_legal_handoffs_pass(reg, artifact, producer, consumer):
    assert_handoff(reg, artifact, producer, consumer)


# ---- 无契约 / 非法传递 → 显式报错 ----

def test_unknown_artifact_raises(reg):
    with pytest.raises(ContractNotFoundError):
        assert_handoff(reg, "mystery_thing", "x", "y")


def test_wrong_producer_raises(reg):
    with pytest.raises(ContractNotFoundError):
        assert_handoff(reg, "pm_plan", "executor", "owner_gate")


def test_wrong_consumer_raises(reg):
    with pytest.raises(ContractNotFoundError):
        assert_handoff(reg, "pm_plan", "project-pm-tracker", "executor")


def test_missing_handoff_edge_raises(reg):
    """producer/consumer 各自合法，但二者之间没有登记 handoff 边 → 报错。"""
    hacked = copy.deepcopy(reg)
    # pm_plan 的合法 producer=project-pm-tracker，合法 consumer=owner_gate。
    # 临时把 consumer 列表加入 executor（但不补 handoff 边）。
    hacked["artifacts"]["pm_plan"]["consumed_by"].append("executor")
    with pytest.raises(ContractNotFoundError):
        assert_handoff(hacked, "pm_plan", "project-pm-tracker", "executor")


def test_producers_consumers_lookup(reg):
    assert "project-pm-tracker" in producers_of(reg, "pm_plan")
    assert "owner_gate" in consumers_of(reg, "pm_plan")
    with pytest.raises(ContractNotFoundError):
        producers_of(reg, "not_an_artifact")


# ---- 与真实叶片一致性 ----

def test_registry_consistent_with_real_leaves(reg):
    leaves = discover_leaves()
    assert leaves, "应至少发现 project-pm-tracker 叶片"
    errors = validate_with_leaves(reg, leaves)
    assert errors == [], f"注册表与叶片漂移: {errors}"


class _FakeLeaf:
    def __init__(self, name, outputs=(), inputs=()):
        self.name = name
        self.output_contract = list(outputs)
        self.input_contract = list(inputs)


def test_drift_detected_when_leaf_claims_unregistered_output(reg):
    errors = validate_with_leaves(reg, [_FakeLeaf("rogue-leaf", outputs=["nope"])])
    assert any("rogue-leaf" in e and "nope" in e for e in errors)


def test_drift_detected_when_producer_not_listed(reg):
    errors = validate_with_leaves(reg, [_FakeLeaf("impostor", outputs=["pm_plan"])])
    assert any("impostor" in e for e in errors)


def test_external_raw_input_material_is_allowed(reg):
    """未登记为产出物的原始输入材料（project_context 等）不判缺失。"""
    errors = validate_with_leaves(
        reg, [_FakeLeaf("x", inputs=["project_context", "requirement_material"])]
    )
    assert errors == []

"""schema 校验器 golden cases（第一档确定性测试，进 CI）。"""
import json
from pathlib import Path

import pytest

from contracts.validators.schema_validator import validate_against_schema

SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "contracts" / "schemas"

VALID_PM_PLAN = {
    "schema_version": "pm_plan@0.1",
    "id": "pplan-20261008-001",
    "title": "视频素材管理功能选型",
    "problem": {
        "statement": "素材散落难以检索",
        "impact": "剪辑效率低",
        "constraints": ["不引入新数据库"],
    },
    "decision": {
        "recommendation": "用文件系统 + 索引 JSON",
        "alternatives": [{"name": "SQLite", "tradeoff": "重，需迁移"}],
    },
    "rationale": "轻量、零迁移",
    "acceptance_criteria": ["可按标签检索", "扫描耗时 < 1s"],
    "owner": "A",
    "created_at": "2026-10-08T10:00:00+08:00",
}

VALID_EXEC_DIFF = {
    "schema_version": "exec_diff@0.1",
    "plan_id": "pplan-20261008-001",
    "leaf": "video-cut-agent",
    "changes": [{"file": "src/indexer.py", "action": "create", "summary": "索引器"}],
    "status": "done",
    "completed_at": "2026-10-08T11:00:00+08:00",
}

VALID_FAILURE = {
    "schema_version": "failure_reason@0.1",
    "category": "mechanical",
    "code": "test_failed",
    "summary": "单测失败",
    "evidence": ["test_indexer.py::test_scan FAILED"],
    "retryable": True,
}


@pytest.mark.parametrize(
    "schema_name,doc",
    [
        ("pm_plan", VALID_PM_PLAN),
        ("exec_diff", VALID_EXEC_DIFF),
        ("failure_reason", VALID_FAILURE),
    ],
)
def test_valid_doc_passes(schema_name: str, doc: dict) -> None:
    assert validate_against_schema(doc, schema_name) == []


def test_pm_plan_missing_required_field() -> None:
    bad = dict(VALID_PM_PLAN)
    del bad["decision"]
    errors = validate_against_schema(bad, "pm_plan")
    assert any("decision" in e for e in errors)


def test_pm_plan_wrong_type() -> None:
    bad = dict(VALID_PM_PLAN)
    bad["acceptance_criteria"] = "必须可测"  # 应为数组
    errors = validate_against_schema(bad, "pm_plan")
    assert errors


def test_schema_version_pinned() -> None:
    bad = dict(VALID_PM_PLAN)
    bad["schema_version"] = "pm_plan@0.9"
    errors = validate_against_schema(bad, "pm_plan")
    assert any("schema_version" in e for e in errors)


def test_failure_reason_category_enum() -> None:
    bad = dict(VALID_FAILURE)
    bad["category"] = "unknown"  # 非法枚举
    errors = validate_against_schema(bad, "failure_reason")
    assert any("category" in e for e in errors)


def test_all_schema_files_are_valid_json_and_compile() -> None:
    import jsonschema

    for path in SCHEMAS_DIR.glob("*.schema.json"):
        schema = json.loads(path.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)  # 编译失败会抛异常

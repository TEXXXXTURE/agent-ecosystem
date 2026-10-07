"""契约校验器 —— 全系统唯一强制点（NFR-02）。

所有产出物在流转前必须通过对应 schema 校验；校验是纯机器行为，不消耗 LLM 调用。
校验失败抛 SchemaValidationError，由编排层捕获后按两档分流处置（机械型）。

用法:
    from contracts.validators.schema_validator import assert_valid
    assert_valid(pm_plan_doc, "pm_plan")
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "schemas"

_schema_cache: dict[str, dict] = {}


class SchemaValidationError(Exception):
    """产出物未通过契约校验。"""


def _load_schema(name: str) -> dict:
    if name not in _schema_cache:
        path = SCHEMAS_DIR / f"{name}.schema.json"
        if not path.exists():
            raise SchemaValidationError(f"未知 schema: {name}（{path} 不存在）")
        _schema_cache[name] = json.loads(path.read_text(encoding="utf-8"))
    return _schema_cache[name]


def validate_against_schema(doc: dict, schema_name: str) -> list[str]:
    """校验产出物，返回错误列表；空列表 = 通过。"""
    try:
        schema = _load_schema(schema_name)
    except SchemaValidationError as e:
        return [str(e)]
    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(doc), key=lambda e: list(e.path))
    return [
        f"{'/'.join(str(p) for p in e.path) or '<root>'}: {e.message}"
        for e in errors
    ]


def assert_valid(doc: dict, schema_name: str) -> None:
    """校验不通过直接抛 SchemaValidationError（用于流转断点）。"""
    errors = validate_against_schema(doc, schema_name)
    if errors:
        raise SchemaValidationError(f"{schema_name} 校验未通过: {errors}")

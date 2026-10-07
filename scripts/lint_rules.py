"""规则文件 lint（衔接验证：NL 层与程序层的引用断裂检查）。

检查项：
1. AGENTS.md 存在且非空；字节预算 < 32KiB（Codex 32KiB 截断教训）
2. AGENTS.md / docs/soul.md 引用的相对路径真实存在（引用断裂）
3. docs/soul.md 存在
4. leaves/*.md frontmatter 合法（加载期闸门，仿 claude plugin validate）
5. contracts/schemas/*.json 合法 JSON 且可被 Draft202012 编译

用法: python scripts/lint_rules.py  （退出码 0 = 通过）
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import jsonschema
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
BYTE_BUDGET = 32 * 1024  # AGENTS.md 字节预算（Codex project_doc_max_bytes 教训）


def _check(ok: bool, msg: str, errors: list[str]) -> None:
    if not ok:
        errors.append(msg)


def lint_rules(root: Path = REPO_ROOT) -> list[str]:
    """返回错误列表；空列表 = 通过。"""
    errors: list[str] = []

    # 1. AGENTS.md 存在 / 非空 / 字节预算
    agents_md = root / "AGENTS.md"
    _check(agents_md.exists(), "AGENTS.md 缺失", errors)
    if agents_md.exists():
        size = agents_md.stat().st_size
        _check(size > 0, "AGENTS.md 为空", errors)
        _check(size <= BYTE_BUDGET, f"AGENTS.md 超出字节预算 {BYTE_BUDGET}（当前 {size}）", errors)

    # 2. AGENTS.md / soul.md 的 markdown 相对引用存在
    for md in [root / "AGENTS.md", root / "docs" / "soul.md"]:
        if not md.exists():
            continue
        text = md.read_text(encoding="utf-8")
        for ref in re.findall(r"\[[^\]]*\]\(([^)#]+)(?:#[^)]*)?\)", text):
            if ref.startswith(("http://", "https://", "#")):
                continue
            target = (md.parent / ref).resolve()
            _check(target.exists(), f"{md.relative_to(root)} 引用断裂: {ref}", errors)

    # 3. soul.md 存在
    soul = root / "docs" / "soul.md"
    _check(soul.exists(), "docs/soul.md 缺失", errors)

    # 4. leaves/*.md frontmatter 合法（跳过 README）
    leaves_dir = root / "leaves"
    if leaves_dir.exists():
        for path in sorted(leaves_dir.glob("*.md")):
            if path.name.upper() == "README.MD":
                continue
            text = path.read_text(encoding="utf-8")
            meta, err = _parse_frontmatter(text)
            _check(meta is not None, f"leaves/{path.name} frontmatter: {err}", errors)
            if meta is not None:
                for k in ("name", "type", "kind", "description"):
                    _check(k in meta, f"leaves/{path.name} frontmatter 缺 {k}", errors)

    # 5. schemas/*.json 合法 + 编译
    schemas_dir = root / "contracts" / "schemas"
    if schemas_dir.exists():
        for path in sorted(schemas_dir.glob("*.schema.json")):
            try:
                schema = json.loads(path.read_text(encoding="utf-8"))
                jsonschema.Draft202012Validator.check_schema(schema)
            except Exception as e:
                _check(False, f"contracts/schemas/{path.name} 无效: {e}", errors)

    return errors


def _parse_frontmatter(text: str) -> tuple[dict | None, str]:
    if not text.startswith("---"):
        return None, "frontmatter 缺失"
    lines = text.splitlines()
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return None, "frontmatter 未闭合"
    try:
        meta = yaml.safe_load("\n".join(lines[1:end]))
    except yaml.YAMLError as e:
        return None, f"YAML 解析失败: {e}"
    if not isinstance(meta, dict):
        return None, "frontmatter 必须是映射"
    return meta, ""


def main() -> int:
    errors = lint_rules()
    if errors:
        print("[lint_rules] FAIL")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("[lint_rules] OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())

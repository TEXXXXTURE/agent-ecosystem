"""规则文件有效性测试（CI 断言）：调用 scripts/lint_rules 的检查逻辑。"""
from scripts.lint_rules import lint_rules


def test_lint_rules_passes() -> None:
    errors = lint_rules()
    assert errors == [], f"规则文件 lint 未通过: {errors}"

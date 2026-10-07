"""叶片 frontmatter 发现与意图路由（FR-02 / FR-03 / NFR-03）。

- 叶片声明 = leaves/*.md：frontmatter 结构化元数据 + 正文 NL。
- frontmatter 解析失败 → 拒载并记日志（加载期闸门）。
- 路由 = 程序判定（关键词/描述匹配），不消耗 LLM（固定路径程序化，零幻觉）。
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

import yaml

logger = logging.getLogger("agent-ecosystem.router")

LEAVES_DIR = Path(__file__).resolve().parent.parent / "leaves"


@dataclass
class Leaf:
    name: str
    kind: str
    description: str
    input_contract: list[str] = field(default_factory=list)
    output_contract: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    pointer: str = ""
    body: str = ""

    def route_hint(self) -> str:
        """路由提示：description 中的"何时选我 / 何时别选我"。"""
        return self.description


def _parse_frontmatter(text: str) -> tuple[dict | None, str]:
    """解析 frontmatter（--- 围栏）。失败返回 (None, 错误)。"""
    if not text.startswith("---"):
        return None, "frontmatter 缺失（必须以 --- 开头）"
    lines = text.splitlines()
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return None, "frontmatter 未闭合（缺少结束 ---）"
    try:
        meta = yaml.safe_load("\n".join(lines[1:end]))
    except yaml.YAMLError as e:
        return None, f"frontmatter YAML 解析失败: {e}"
    if not isinstance(meta, dict):
        return None, "frontmatter 必须是一个映射（键值对）"
    return meta, ""


def load_leaf(path: Path) -> Leaf | None:
    """加载一个叶片声明。解析失败 → 拒载并记日志，返回 None。"""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        logger.error("拒载 %s: 读取失败 %s", path.name, e)
        return None
    meta, err = _parse_frontmatter(text)
    if meta is None:
        logger.error("拒载 %s: %s", path.name, err)
        return None
    required = ("name", "type", "kind", "description")
    missing = [k for k in required if k not in meta]
    if missing:
        logger.error("拒载 %s: 缺少必需字段 %s", path.name, missing)
        return None
    body = "\n".join(text.splitlines()[meta_end(text):])
    return Leaf(
        name=str(meta["name"]),
        kind=str(meta["kind"]),
        description=str(meta["description"]),
        input_contract=[str(x) for x in meta.get("input_contract", [])],
        output_contract=[str(x) for x in meta.get("output_contract", [])],
        tools=[str(x) for x in meta.get("tools", [])],
        pointer=str(meta.get("pointer", "")),
        body=body,
    )


def meta_end(text: str) -> int:
    """返回 frontmatter 结束 --- 之后的第一行索引（正文起点）。"""
    lines = text.splitlines()
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return i + 1
    return len(lines)


def discover_leaves(directory: Path = LEAVES_DIR) -> list[Leaf]:
    """发现目录下全部叶片（*.md，跳过 README）。"""
    leaves: list[Leaf] = []
    if not directory.exists():
        return leaves
    for path in sorted(directory.glob("*.md")):
        if path.name.upper() == "README.MD":
            continue
        leaf = load_leaf(path)
        if leaf is not None:
            leaves.append(leaf)
    return leaves


def route(intent: str, leaves: list[Leaf]) -> Leaf | None:
    """意图路由（程序判定）：在 description 中找"何时选我"关键词。

    第一版为确定性关键词匹配（零幻觉）；后续可升级为 LLM 路由（动态路径）。
    """
    intent_lower = intent.casefold()
    best: Leaf | None = None
    best_score = 0
    for leaf in leaves:
        hint = leaf.route_hint().casefold()
        score = 0
        for token in ("何时选我", "产品决策", "方案", "prd", "评审", "需求", "优先级"):
            if token in hint:
                score += 1
        if intent_lower and any(k in intent_lower for k in ("方案", "prd", "评审", "需求", "取舍", "roadmap", "plan")):
            if "产品决策" in hint or "方案" in hint:
                score += 2
        if score > best_score:
            best, best_score = leaf, score
    return best

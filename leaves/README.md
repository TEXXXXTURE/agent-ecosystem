# 工具叶片（leaves/）

> 挂载层：所有能力单元以"引用"（产品仓指针）挂在本架构下方，不镜像内容。
> 叶片声明形态（2026-10-08 定稿）：**每个叶片一个 Markdown，frontmatter 写结构化元数据 + 正文写"怎么干活"的自然语言**（参照 Claude Code subagents 混合文件）。

## 声明格式

```markdown
---
name: <叶片标识>
type: leaf
kind: <累积型|产出型|处理型|展示型|规则维护型>
description: "<路由描述：我擅长什么；何时选我；何时别选我。程序按此路由。>"
input_contract: ["<输入契约>", ...]
output_contract: ["<输出契约，产出物 schema 名>", ...]
tools: ["<工具白名单，可选>"]
pointer: "<产品仓指针>"
---

# 正文：怎么干活（自然语言，接契约即开工）
```

- 程序按 frontmatter 发现、路由（读 `description`）、注入正文与工具白名单。
- **frontmatter 解析失败 → 拒载并记日志**（加载期闸门，仿 Claude subagents 加载校验）。
- 叶片只声明"我吃什么、我产什么"，能力细节留在产品仓。

## 叶片清单（指针）

完整登记表见 `../docs/工具叶片清单.md`。本目录放每叶片的声明文件（新增叶片 = 新增一个 md，不动既有叶片与编排代码，FR-04 验收）。

## 已有叶片声明

- [project-pm-tracker.md](project-pm-tracker.md) —— 产品决策叶片（6 步闭环①的执行者）

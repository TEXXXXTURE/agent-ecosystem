# 契约注册表（contracts/）

> 契约注册表 = 集成层的规则本体（PRD FR-01 落点）。产出物通过契约交流，不互相依赖、不融合程序。

## 目录

| 路径 | 内容 |
|---|---|
| `registry.json` | **产出物契约注册表（规则本体）**：每个产出物的 producer/consumer + 合法 handoff 边；交接只传压缩结论+指针 |
| `registry.py` | 注册表加载、与叶片一致性对账、handoff 断言（无契约可依时抛 `ContractNotFoundError`） |
| `schemas/` | 产出物 schema（JSON Schema，语言中立、可跨工具、可进 CI lint） |
| `validators/` | 校验器实现（`schema_validator.py`）——**全系统唯一强制点**（NFR-02） |
| 叶片声明 | 见 `../leaves/`（frontmatter Markdown，FR-02 落点） |

## 首批 schema（v0.1）

| schema | 产出物 | 流转节点 |
|---|---|---|
| `pm_plan` | PM 方案 | 6 步①→②（过校验才进 owner_gate） |
| `exec_diff` | 执行 diff | 6 步③→⑤（交付前校验） |
| `failure_reason` | 失败原因（结构化，带回流） | 6 步⑤→③ |
| `decision_record` | 决策记录（owner 拍板留痕） | 6 步② |
| `info_stream` | **外部信息流交付物**（黑洞工作流 → 工作台内编排 Agent） | 入 6 步① 之前的输入侧（loop_step 0） |

## 校验断点（怎么用）

```python
from contracts.validators.schema_validator import assert_valid

assert_valid(pm_plan_doc, "pm_plan")   # 不过就抛 SchemaValidationError
```

## 契约变更流程（NFR-01）

1. 契约变更 = 一次决策：先在 project-vault 记 ADR（备选 / 影响范围 / 兼容期）；
2. ADR 通过后：改 `schemas/` 对应文件 + 升 `schema_version`（如 `pm_plan@0.1` → `0.2`）；
3. 同步更新：校验器测试（golden cases）、本 README、叶片 frontmatter 的 input/output_contract；
4. 旧契约兼容期明确后，过期版本删除（保留在 git 历史）。

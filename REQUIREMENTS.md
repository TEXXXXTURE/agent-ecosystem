# REQUIREMENTS.md — 需求与任务清单（新会话接任入口）

> 本文件是本仓**当前待办需求**的唯一权威清单。新会话/新 Agent 接任本仓任务时，**先读本文件**，再读 [docs/soul.md](docs/soul.md)（编排 Agent 人设与 6 步闭环细则）与 [docs/PRD.md](docs/PRD.md)（产品需求）。
> 状态图例：✅ 已有可用 ｜ 🔧 制作/测试中 ｜ ❌ 未落地 ｜ 🎯 待办

## 0. 项目一句话

**agent-ecosystem**：Agent 生态集成层——把平级能力单元（工具/Agent/项目）组织为可组合总系统的集群规则 + 产出物契约 + 6 步协作闭环。核心规则：**方向问题升级 owner、机械问题机器兜底**。规则形态：混合三明治（判断留给自然语言，兜底留给程序）。

## 1. 现状快照（2026-10-09）

| 环节 | 状态 | 说明 |
|---|---|---|
| ① AI PM / 产品 Agent | ✅ | project-pm-tracker 叶片；方案产出物 schema（`contracts/schemas/pm_plan.schema.json`）已有 |
| ② 原型规划（Figma API） | 🔧 | **新增环节**（见 R1）：Figma API 插件 → CLI 端原型规划 → 截图回传确认 |
| ③ 契约注册表 | ✅ | 2026-10-09 定稿：`registry.json`（producer/consumer+handoff 边）+ `registry.py`（对账+断言），17 项测试覆盖，见 R2 |
| ④ 编码 / 执行 Agent | ✅ | PI / dsh / Codex / Hermes 等 CLI Agent 已在用 |
| ⑤ 互审 Agent | ❌ | 只有一次性外部评审规则雏形，无常驻循环角色（见 R3） |
| ⑥ 修订 → 复核 | ❌ | 处置追踪列 + 修订即重审未落地（见 R4） |
| ⑦ NFR-02 校验器 | 🔧 | 校验器实现已有雏形，需按 R5 完善并接入闭环 |
| ⑧ 终止条件三件套 | 🔧 | `orchestrator/termination.py` 已有雏形，需验证接入（见 R6） |
| ⑨ owner 人工审核 | ✅ | 人在环拍板已有；中断点机制随 R6 落地 |

**已建基础设施**（骨架完整，见 README 目录结构）：`contracts/`（schemas + validators + registry）、`orchestrator/`（closure.py / gates.py / router.py / termination.py）、`leaves/`、`scripts/lint_rules.py`、`tests/`（确定性测试 4 组）、`.github/workflows/`（CI，未提交）。

## 2. 待办需求清单

### R1 · 原型环节（新增，用户自制工具对接）
- **目标**：在 ① PM 方案 与 ③ 编码 之间插入原型规划环节——Agent 在 CLI 端通过 **Figma API 插件**完成原型规划，产出的原型图以**手动截图回传**（当前）或 **API 直读形状/内容**（后期）作为通信方式确认形态，确认后才进入契约与编码。
- **现状**：用户正在制作 Figma API 插件（调到 CLI 端操作）；闭环链路与契约位**尚未预留**。
- **待办**：① 在 6 步闭环中正式登记"原型产出物"环节与契约；② 定义原型产出物 schema（文件指针 + 截图 + 确认状态）；③ 明确"方案 → 原型 → 契约 → 编码"的传递路径。
- **验收**：闭环设计图与 soul.md 中出现原型环节；原型产出物有 schema 可校验。
- **关联**：`docs/soul.md`、`contracts/schemas/`、闭环设计图。

### R2 · 契约注册表定稿 ✅（2026-10-09 完成）
- **交付**：`contracts/registry.json`（规则本体：4 类产出物的 producer/consumer + 5 条 handoff 边；handoff_rule=只传压缩结论+指针）+ `contracts/registry.py`（加载/结构校验、与 leaves 一致性对账 `validate_with_leaves`、handoff 断言 `assert_handoff`）。
- **验收实测**：新增 `tests/test_registry.py` 17 例，全仓 **42 passed**；合法 handoff 通过，未登记产出物/错误 producer/consumer/缺边均抛 `ContractNotFoundError`；注册表与真实叶片对账零漂移；外部原始材料放行。lint OK。
- **语义约定**：系统内产出物必须登记；外部原始输入材料（project_context 等）不作为产出物登记。
- **后续**：新增执行叶片后，经 `validate_with_leaves` 自动纳入对账。

### R3 · 互审 Agent 实体（常驻循环角色）
- **目标**：把互审从"一次性外部评审"升级为闭环内**常驻循环角色**——独立、无记忆、新眼睛，事件驱动唤醒。
- **现状**：三段式意见规则（一句话结论 + 看到了什么/担心什么/为什么/建议怎么改）已有雏形；无常驻实体。
- **待办**：① 定义互审产出物 schema（意见 + 严重度：必须改/建议改）；② 明确唤醒条件（编码出问题/失败信号）；③ 互审独立于编排者（防 GOD 自裁式反例）。
- **验收**：闭环运行中互审角色可按事件被触发并产出结构化意见。
- **关联**：`contracts/schemas/`、`orchestrator/closure.py`、`docs/soul.md`。

### R4 · 修订 → 复核（处置追踪 + 修订即重审）
- **目标**：意见回填处置追踪列；**修订后旧意见自动作废**（stale dismissal 式重审），防旧意见罩新产物。
- **现状**：未落地。
- **待办**：① 处置追踪列落地（意见 → 处置 → 状态）；② 修订事件触发旧意见失效 + 新意见重审；③ 最大轮数内完成（超限升级 owner）。
- **验收**：产物修订后，旧意见在追踪列中标记作废；重审只针对新改动（增量审）。
- **关联**：`orchestrator/closure.py`、`orchestrator/gates.py`。

### R5 · NFR-02 校验器完善（唯一强制点）
- **目标**：校验器是全系统**唯一强制点**——schema / 来源锚定 / 测试；过 → 流转交付，不过 → 带失败原因回炉。
- **现状**：`contracts/validators/schema_validator.py` 与 schema 已有雏形。
- **待办**：① 校验器接入闭环状态机（closure 终态断言）；② 失败原因结构化回流（`failure_reason.schema.json` 已建，需接线）；③ 校验器结果写入交付记录。
- **验收**：`pytest tests/` 全绿；校验不过时产出物带原因正确回炉（≤ 最大轮数）。
- **关联**：`orchestrator/closure.py`、`contracts/validators/`、`tests/test_closure_loop.py`。

### R6 · 终止条件三件套验证接入
- **目标**：通过信号 / 最大轮数 / owner 中断点（+ hops cap）——防空转。
- **现状**：`orchestrator/termination.py` 已有雏形。
- **待办**：① 三件套在 closure 主循环中实际生效；② owner 中断点以程序原语实现（interrupt 式挂起，owner 一句话 resume）；③ hops cap 超限升级 owner。
- **验收**：终止条件单测覆盖三件套；超轮数/超跳数正确升级而非空转。
- **关联**：`orchestrator/termination.py`、`tests/test_termination.py`。

### R7 · 真实闭环测试用例（进行中）
- **目标**：用真实项目验证 6 步闭环跑通。
- **现状**：**进行中**——测试用例为 wiki 项目前端重置（Manus 手绘涂鸦风，`D:\AIGC术语库`，MkDocs+Material），范围 A：内容零改动，只补背景质感装饰层（frontend-aesthetic-skill 第⑤维：禁纯色平铺）。已按"一写一审"委派 CLI Agent：PI（DeepSeek V4 Flash via Ark Plan 火山额度）写 → dsh 互审补漏。
- **待办**：① PI 产出回收验证（mkdocs build 通过 + 双主题截图）；② dsh 互审；③ 结论回填本仓（哪些环节暴露缺口）。
- **验收**：闭环全链路跑通一次；暴露的问题登记为后续需求。
- **关联**：`D:\AIGC术语库\TASK-background-texture.md`（任务交接文档）、frontend-aesthetic-skill。

### R8 · CI 推送（待提交）
- **目标**：`.github/workflows/`（跑全部确定性测试 + 规则 lint）随本需求清单一起提交推送。
- **现状**：工作流文件已建，未 git 提交。
- **待办**：提交并确认 GitHub Actions 跑绿。

## 3. 新会话接任顺序（必读）

1. `REQUIREMENTS.md`（本文件）→ 明确待办需求
2. `docs/soul.md` → 编排 Agent 人设与 6 步闭环细则
3. `docs/PRD.md` → 产品需求 FR/NFR
4. `README.md` → 部署形态与命令
5. 待办需求逐项推进，每项完成走"契约 → 实现 → 测试 → CI"闭环

## 4. 管理边界

- 本仓是**产品本体**（公开）；项目管理跟踪（ADR/评审/状态/跟进日志）留在本地 project-vault（STANDARDS §11）。
- 契约变更走 ADR 后同步 `contracts/README.md`（NFR-01）。

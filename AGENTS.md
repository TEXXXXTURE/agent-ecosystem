# AGENTS.md

> 本仓库是 **agent-ecosystem**（Agent 生态集成层）的产品本体：编排 Agent 的集群规则 + 产出物契约 + 6 步协作闭环。
> 本文件是给所有 Agent（与人类）看的通用门面（薄）。深度人设与执行细则见 [docs/soul.md](docs/soul.md)。

## 这个仓库是什么

把**平级的能力单元**（工具 / Agent / 项目）组织为可组合总系统的**集成层**：编排 Agent 按契约路由传递，契约注册表是规则本体。核心是**产出物契约驱动**——能力单元只通过产出物交流（输入契约 → 输出契约），不互相依赖、不融合程序。

## 协作闭环（6 步，一句话版）

```
① PM 产出方案 + 机器 schema 校验（免费）
② owner 审方案拍板（人在环，一句话定方向，0 token）——替代"方案互审循环"
③ 编码执行（N 次调用）
④ 出问题分两档：机械问题 → 自解 + 机器校验兜底；方向问题 → 直接升级 owner 一句话定夺（0 token）——替代"编码互审循环"
⑤ 机器校验（测试/schema）过 → 交付；失败 → 带原因回③
⑥ 可选：关键产出物一次互审 + 落痕（0-1 次调用）
```

**核心规则一句话：方向问题升级 owner、机械问题机器兜底。**

- 凡是"过不过 / 停不停 / 升级不升级"的判断，全部指向程序实体（`contracts/` 的 schema 与校验器、`orchestrator/` 的图、门、终止条件对象）——不靠 Agent 自觉。
- 硬执行不进指令文件：本文件与 soul.md 只塑造行为与判断，机器强制在 `contracts/validators` 与 `orchestrator/`。
- 判断留给自然语言，兜底留给程序（混合三明治形态，依据见 [docs/调研/规则形态调研与仓库结构草案.md](docs/调研/规则形态调研与仓库结构草案.md)）。

## 常用命令

```bash
# 安装编排层依赖
pip install -r requirements.txt

# 跑全部确定性测试（schema 校验器 / 6 步状态机 / 两档分流 / 终止条件 / 规则文件 lint）
pytest tests/ -v

# 规则文件 lint（单独跑）
python scripts/lint_rules.py

# 以 CLI 驱动一次闭环（示例）
python -m orchestrator.closure "任务描述"
```

## 目录导览

| 路径 | 内容 |
|---|---|
| `docs/soul.md` | 编排 Agent 深度人设与 6 步闭环执行细则（接任先读） |
| `docs/PRD.md` | 产品需求文档（FR / NFR） |
| `contracts/` | 契约注册表：产出物 schema + 校验器（全系统唯一强制点） |
| `orchestrator/` | 6 步闭环显式状态机 / 图 + 两档分流 + owner_gate + 路由 |
| `leaves/` | 工具叶片指针清单（引用不镜像） |
| `scripts/` | 规则 lint 与小样本 eval |
| `tests/` | 确定性测试（进 CI） |

## 约定

- 规则正文中文；命令与代码块英文。
- 契约变更走 ADR（管理跟踪在 project-vault，本仓只登记 origin 指针）。
- 产出物必须过对应 schema 校验才可流转（NFR-02）。

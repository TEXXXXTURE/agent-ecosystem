# agent-ecosystem

**Agent 生态集成层**：把平级的能力单元（工具 / Agent / 项目）组织为可组合总系统的集群规则 + 产出物契约 + 6 步协作闭环。

- 核心规则：**方向问题升级 owner、机械问题机器兜底**。
- 规则形态：混合三明治——判断留给自然语言（`AGENTS.md` / `soul.md`），兜底留给程序（`contracts/` 契约校验 + `orchestrator/` 显式状态机）。
- 为单人 owner 设计，token 敏感：方向判断由人在环免费接管，机器校验零 token 兜底，互审循环按需可选。

## 📌 当前任务（新会话先读）

**待办需求唯一权威清单：[REQUIREMENTS.md](REQUIREMENTS.md)** —— 含现状快照与 R1–R8 需求清单（原型环节 / 契约注册表 / 互审 Agent / 修订复核 / 校验器 / 终止条件 / 真实测试用例 / CI 推送）。接任本仓任务请先读它。

## 快速开始（三档部署形态）

### 档位一 · 只用规则（零安装）

```bash
git clone https://github.com/TEXXXXTURE/agent-ecosystem.git
cd agent-ecosystem
# 用支持 AGENTS.md 的 Agent 工具打开（Codex / Claude Code / Cursor / Cline）
# AGENTS.md 会被自动加载，6 步闭环规则即刻生效
```

### 档位二 · 要跑闭环自动化

```bash
git clone https://github.com/TEXXXXTURE/agent-ecosystem.git
cd agent-ecosystem
pip install -r requirements.txt

# 配置模型 API key（编排层调用 LLM 的入口）
# Windows: setx ARK_API_KEY_PI "<key>"
# macOS/Linux: export ARK_API_KEY_PI="<key>"

# CLI 驱动一次闭环
python -m orchestrator.closure "任务描述"
```

### 档位三 · 接入宿主集群

宿主 Agent（豆包 / Munder+Hermes / DeepSeek Harness / Claude Code / Codex / CrewAI 等，任选，不绑定任何特定实现）读取 `AGENTS.md` + `docs/soul.md` 获得人设与规则，契约校验走 `contracts/`（机器强制），叶片按 `leaves/` 指针挂载。详见 [docs/soul.md](docs/soul.md)。

## 目录结构

```
├── AGENTS.md              # 通用规则门面（薄）——所有 Agent 自动读
├── README.md
├── LICENSE                # MIT
├── docs/
│   ├── soul.md            # 编排 Agent 深度人设 + 6 步闭环执行细则
│   ├── PRD.md             # 产品需求（FR / NFR）
│   ├── 工具叶片清单.md      # 挂载层清单（引用不镜像）
│   ├── 过程记录.md          # 立项推演与关键决策
│   └── 调研/               # 两轮范式调研报告原件
├── contracts/             # 契约注册表（程序约束层核心）
│   ├── schemas/           # 产出物 schema（JSON Schema）
│   ├── validators/        # 校验器实现（唯一强制点）
│   └── registry.json      # 叶片能力声明（输入/输出契约 + handoff_description）
├── orchestrator/          # 6 步闭环状态机 + 两档分流 + owner_gate + 路由
├── leaves/                # 工具叶片指针
├── scripts/               # 规则 lint / 小样本 eval
├── tests/                 # 确定性测试（进 CI）
└── .github/workflows/     # CI：跑全部确定性测试 + 规则 lint
```

## 环境变量

| 变量 | 用途 |
|---|---|
| `ARK_API_KEY_PI` | 编排层 LLM 调用密钥（火山 ARK Plan 额度，模型如 deepseek-v4-flash） |

## 测试

```bash
pip install -r requirements.txt
pytest tests/ -v
python scripts/lint_rules.py
```

覆盖：schema 校验器 golden cases、6 步闭环状态机终态断言（owner 拍板后产出物过没过 schema / 失败有没有带原因正确回流）、两档分流断言、终止条件单测、规则文件 lint（存在性 / 引用断裂 / frontmatter / 字节预算）。

## 管理边界

- 产品本体（本仓）与项目管理跟踪分离：ADR、评审、状态、跟进日志留在本地 project-vault（STANDARDS §11），本仓只登记 origin 指针。
- 契约变更走 ADR 后同步 `contracts/README.md`（NFR-01）。

## License

[MIT](LICENSE)

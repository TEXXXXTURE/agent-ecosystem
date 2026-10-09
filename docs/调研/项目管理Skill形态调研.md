# Agent 生态 · 项目管理类 Skill 形态调研（第三轮）

> 承接前两轮（①督促-互审-闭环调研；②规则形态调研与仓库结构草案）。本轮回答：**项目管理类能力/规则在业界以什么形态存在？"项目规则本身就是一个 Skill"成立吗？交接文档处到底该放 Skill 指针、Skill 本体、还是继续 AGENTS.md 入口 + 程序约束？**
> 已拍板硬约束：6 步闭环 + GitHub 独立仓库。本轮只调研，不实现。
> 日期：2026-10-09 ｜ 调研方式：三路并行（Skill 形态本体与生态 / 指令文件与 MCP 对照 / 触发机制与"规则即 Skill"案例），来源实际打开核验，标注「已查证 / 一方称」。

---

## 一、一页结论

1. **"项目管理即 Skill"是行业主流做法，不是异想**。OpenAI 官方仓库 `openai/skills` 的 `.curated/linear/SKILL.md` 就是把"Sprint Planning / Bug Triage / Release Planning"等项目管理流程规则封装成 Skill 的官方样板；社区还有 `maul-team`（19 个 skill 覆盖完整 Scrum 生命周期）、`@ethansmc/pm-skills`（12 个 skill 的 PM 流水线）。官方边界表（Claude Code features-overview）明确：**跨项目可复用、按需触发的流程 → Skill；项目专属、每次都要遵守的约定 → 指令文件；外部工具/数据 → MCP；每次必须发生的强制 → Hook/程序**。

2. **回答你的质疑"业界是不是直接写进 AGENTS.md / CLAUDE.md，而不是做成独立 Skill？"**——**两者都对，分界线是官方明示的 always-on vs on-demand**：项目专属且每次要遵守的（用 pnpm、PR 目标分支、提交前跑 lint）确实直接写进根 AGENTS.md/CLAUDE.md（真实案例：`github/awesome-copilot` 的根 AGENTS.md 写了整套 PR Guidelines + Code Review Checklist，并配 `npm run skill:validate` 脚本机器校验）；**跨项目复用的流程（sprint 怎么开、issue 怎么分诊、PR 怎么审）做成 Skill**。Anthropic 原话："If you find yourself copying the same instructions across multiple Projects, that's a signal to create a skill instead"；"Projects say what you need to know; Skills say **how to do things**"。

3. **触发机制决定一切，且"放置位置≠会被加载"**。Claude 的 Skill 采用渐进披露：启动只把 name+description（约 100 token/skill）注入 system prompt，模型按 description 语义匹配才读全文；显式 `/name` 是第二通道。**"放在交接文档旁"不会让模型因此自动加载它**——放置只决定可发现性，不决定触发。业界触发可信度排序：**程序驱动（Munder 消息+Stop hook、maul 的 scrum-start.sh）> 约定式自动（Copilot 目录就近、Cline paths）> 语义自觉（Claude description 匹配）**。你设想的主 Agent"识别场景→自觉加载"属最弱档，必须配显式入口或前置指针兜底。

4. **推荐：交接文档处放「Skill 指针 + 触发声明」，不放 Skill 本体**。三件事分开——① 仓库根 `AGENTS.md`（薄门面，跨工具自动加载）：一行"项目管理场景 → 调用 project-pm-tracker Skill"；② 项目交接文档（STANDARDS §16 第一入口）：写"何时调、调哪个 + 本项目五段式上下文"，**指针指向 Skill 本体**；③ Skill 本体（project-pm-tracker）留在全局 `.user_skills`（跨项目复用，已是如此），承载"怎么盯项目、怎么做产品决策"的复用流程。理由：交接文档是"每项目一变"的内容，Skill 是"跨项目不变"的逻辑，混放会导致规则版本化困难；业界成熟项目无一例外是"薄门面 + 指针 + Skill 本体 + 程序约束"四层。

5. **纯 NL 的项目管理 Skill 无成熟先例——成熟实例全部叠加程序约束**。maul-team 带 hooks（DoD 质量门、stall-watchdog 卡死看门狗）、pm-skills 带 `test_*.py` 与证据门控。这印证前两轮"混合三明治"结论：**Skill 承载 NL 流程引导，机器强制仍在 contracts/orchestrator**；Skill 本身要可测（官方已有 `claude plugin validate` + `claude plugin eval` 的 `tool_used: Skill` grader，pm-skills 自带 pytest）。

---

## 二、调研范围与语境

- **用户设想**：主 Agent（A）识别"需要项目管理"场景 → 识别并加载本地 Skill → Skill 执行仓库内项目管理规则（"项目规则本身就是一个 Skill"）；计划在项目交接文档处放置该 Agent/Skill。
- **本地先例**：`project-pm-tracker` Skill（.user_skills 目录，双模式：盯项目对接 project-vault + 产品决策 PRD/优先级/评审；通用纪律：先读总仓再下结论、事实与判断分离、停顿点、改动前先展示、落痕；集群角色约定：收到子任务先声明职能、写改删先回传计划）。
- **前两轮结论（推荐依据）**：混合三明治 = NL 引导 + 程序约束；仓库根 AGENTS.md = 薄门面（跨工具自动加载）；soul.md = 编排 Agent 深人设；contracts/orchestrator = 程序约束层；判断留给 NL、兜底留给程序。

---

## 三、形态分布总览（项目管理类能力）

| 形态 | 典型代表 | 承载什么 | 加载方式 | 是否机器强制 | 适用 |
|---|---|---|---|---|---|
| **独立 Skill**（SKILL.md） | Claude Agent Skills、openai/skills linear、maul-team、pm-skills | 跨项目可复用的流程 SOP（sprint 怎么开、PRD 怎么写、issue 怎么分诊） | 按 description 语义匹配 + `/name` 显式；渐进披露省 context | 仅 frontmatter（name/description）可校验，正文纯 NL；可带 scripts/hooks | 通用、可复用、按需 |
| **指令文件**（AGENTS.md/CLAUDE.md/.cursorrules） | github/awesome-copilot 根 AGENTS.md、各开源仓库 | 项目专属、每次都要遵守的约定（命令、分支、风格、Review Checklist） | 启动即自动读（全量注入，常驻 context） | 基本无（可配脚本校验如 npm run validate） | 项目专属、启动即需知 |
| **MCP / 插件** | GitHub MCP Server、Linear MCP、Notion/Jira MCP | 工具与数据访问（读/改 issue、建 cycle），**不含规则** | 客户端连接后工具常驻可调用 | 参数 schema + OAuth，校验"调用对不对" | 外部系统连接 |
| **混合** | Claude Code 官方扩展层（CLAUDE.md+Skill+Subagent+Tool+MCP+Hook） | 每层各管一段：常驻约定 / 按需流程 / 隔离执行 / 工具 / 强制兜底 | 各按自身机制 | 判断留 NL、强制留 Hook/校验器 | 完整工程系统 |

**官方边界判据（Claude Code features-overview 的"Build your setup over time"触发表，已查证）**：

| 触发信号 | 官方建议放哪 |
|---|---|
| Claude 把某条约定/命令做错两次 | 写进 CLAUDE.md |
| 反复手打同一个 prompt 开头 | 存成可调用 Skill |
| 同一份 playbook/多步流程第三次粘贴进对话 | 固化为 Skill |
| 不断从 Claude 看不见的浏览器 tab 抄数据 | 接 MCP server |
| 想让某事每次自动发生、不用问 | 写 Hook（程序强制） |

配套原文：CLAUDE.md 硬上限 **<200 行**，涨了就拆给 skill / `.claude/rules/`；"MCP gives tools and data access；Skills give knowledge about how to use those tools"；"never edit .env 写在 CLAUDE.md 里只是请求（request），不是保证（guarantee）——要每次成立就做成 Hook"。

---

## 四、每案例拆解

### 4.1 Skill 形态本体与生态（第三轮-A）

**Anthropic Agent Skills 官方形态**【已查证：anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills + code.claude.com/docs/en/skills】——Skill = 一个目录里的 `SKILL.md`（YAML frontmatter 仅 `name`+`description` 必填 + Markdown 正文步骤/规范/示例）+ 可外挂 `scripts/`、`references/`、`assets/`。官方定位：正文是"给新员工的 onboarding guide"，主文件精简、细节外挂（如 PDF skill 把冷门"填表"拆到 forms.md）。**渐进披露三级**：① 启动只把 name+description 塞进 system prompt（约 100 token/个）；② 模型判断相关后用 Bash 读入完整 SKILL.md；③ 按需读 bundled 引用文件。官方明确警告："description 模糊或互相重叠，模型会误触发/漏触发"——**触发准不准 90% 取决于 description 写得是否精准、互不重叠**。

**开放规范 agentskills.io**【已查证：agentskills.io/specification】——frontmatter 机器可校验字段（权威枚举）：`name` 必填（≤64 字符、仅小写字母/数字/连字符、不能首尾连字符、**必须与父目录同名**）、`description` 必填（≤1024 字符、写清"做什么+何时用+关键词"）、可选 `license`/`compatibility`/`metadata`/`allowed-tools`（实验性）。**存在官方校验工具 `skills-ref validate ./my-skill`**（校验 frontmatter 合法性与命名规范，已查证）。正文无格式限制，建议主 SKILL.md <500 行 / <5000 token。

**anthropics/skills 官方示例仓库**【已查证】——含 docx/pdf/pptx/xlsx 生产级 skill、`template/` 起步模板（frontmatter 后正文分 `## Examples` + `## Guidelines` 两段式）。**官方没有项目管理类 skill**——PM 形态来自社区。

**skills vs subagents vs tools vs memory 官方边界**【已查证：code.claude.com/docs/en/features-overview】——CLAUDE.md（=memory）：**每次会话永远全量加载**，放"总是要遵守"的项目约定，官方建议 ≤200 行；Skill：**按需加载**的可复用知识/工作流，可显式 `/<name>` 也可模型按 description 匹配；Subagent：**独立上下文的隔离 worker**，跑完只回摘要，可 `skills:` 字段预载；Tool/MCP：可执行函数/外部连接；Hook：**确定性触发**（每次编辑后跑 lint），"绝不能违反"的护栏应放 Hook——"prompt 只是请求，hook 才是强制"。**与你们"三明治"分层完全同构。**

**社区生态 + 真实 PM 类 skill 实例**——聚合站 agskills.dev / skillmd.ai / LobeHub（一方称，未逐一深核）；可核验实例：`OthmanAdi/planning-with-files`（Snyk 榜单称全生态最热门 PM 类 skill，13.4k stars，核心=把 volatile context 持久化成磁盘三文件 task_plan/findings/progress，强制五条落盘纪律——**与 project-pm-tracker 的"落痕"纪律同一思路**；注意：细节经 Snyk 榜单转述，一方称，存在性已交叉核对）；编号交付 pipeline（001-624 编号 skill 集，职责正交：task-executor 不评审不写测试）；`aidankinzett/claude-git-pr-skill`（把 PR 评审封成严格流程，含"告警信号"清单明令禁止模型偷懒借口）。

### 4.2 指令文件 vs MCP vs 混合（第三轮-B）

**规则直接写指令文件的真实案例**【已查证：raw.githubusercontent.com/github/awesome-copilot/refs/heads/main/AGENTS.md】——GitHub 官方 awesome-copilot 仓库根 AGENTS.md 写了整套 `## Pull Request Guidelines`（"All PRs should target **main**, not staged"）+ `### Pre-commit Checklist` + `### Code Review Checklist`（对 instructions.md/agent.md/skills 分别列 checkbox），并配可执行校验命令 `npm run skill:validate` / `npm run plugin:validate`。**结论：业界确实把项目专属协作流程直接写根 AGENTS.md，但同时用脚本把它机器可校验化**——不是纯 NL 裸奔。

**MCP 形态**【已查证：github.com/github/github-mcp-server（33.5k star）+ linear.app/docs/mcp 工具清单经 openai/skills curated 目录交叉核验】——MCP server 暴露的是 **tool definitions + resources**（list_issues/get_issue/create_issue/create_cycle…），官方定位"connects AI tools directly to GitHub"、"USB-C for LLMs"。**它回答"能不能读/改 issue"，不回答"按什么节奏做 sprint"——规则不在这一层**。

**混合形态样板**【已查证：github.com/openai/skills 的 `.curated/linear/SKILL.md`】——OpenAI 官方把 Linear MCP 的工具包进 Skill 的流程里：frontmatter + `Required Workflow` Step0-4（先澄清 scope → 先 list/get 读上下文 → 再 create/update 批量 → 总结 gap 与 next actions）+ `Practical Workflows`（Sprint Planning / Bug Triage / Documentation Audit / Workload Balance / Release Planning…）+ `Prerequisites` 强制"Linear MCP 必须已 OAuth 连接"。**这就是用户设想的形态落地：MCP 给工具、Skill 给流程。**

### 4.3 触发机制与"规则即 Skill"案例（第三轮-C）

**Claude skill 触发细节**【已查证：code.claude.com/docs/en/skills + platform.claude.com/docs】——渐进披露三级（同上）；两种触发模式：自动（description 语义匹配）+ 显式（`/skill-name`）；frontmatter 可锁档：`disable-model-invocation: true`（只许手动，用于有副作用流程）、`user-invocable: false`（只许模型用）、`paths: glob`（仅处理匹配文件时自动加载）；description+when_to_use 合计超 1536 字符被截断；官方验证：`claude plugin validate <dir>`（frontmatter 可解析）+ `claude plugin eval` 配 `tool_used: Skill` grader 评测触发命中率。

**触发机制对比表**：

| 工具 | 触发源 | 触发时机 | 加载方式 | 是否需模型自觉 |
|---|---|---|---|---|
| Claude Code skills | description 语义匹配 + `/name` + `paths` glob | 每轮请求时模型对照 description | 启动只载 name+desc；命中才 cat 正文 | 是（可 disable-model-invocation 关） |
| Cursor rules（前轮核验） | globs / alwaysApply / description 四档 | alwaysApply 始终注入；globs 文件打开时 | 命中即注入 | 半自动 |
| Cline 规则（前轮核验） | `paths` 条件 | 打开匹配文件时激活 | 文件系统驱动 | 否 |
| GitHub Copilot 指令（前轮核验） | 目录树约定 | 启动/就近编辑 | 就近优先叠加 | 否 |
| Munder HIVE（本地核验） | outbox 消息 + Stop hook + registry | 消息到达/回合结束 | router 投递 inbox；hook block 续跑 | 否（程序驱动） |
| maul-team | `scrum-start.sh` + SM delegate + hooks | 启动脚本拉起；事件驱动 | 19 skill 按 Sprint 阶段派发 | 混合 |

**"规则即 Skill"现存案例**：
- `@ethansmc/pm-skills`【已查证：npmjs.com/package/@ethansmc/pm-skills】——12 个 skill 的 PM 流水线（pm-workflow 主编排 + pm-knowledge/prd-reconcile/write-prd/pm-tdd/pm-verification/pm-branch-management…），阶段化 SOP（消歧→需求探索→写 PRD→原型验证），明确"事实性自动写、分析性草稿待审"分流；自带 `conftest.py`/`test_*.py` 与验证步骤。**主入口是显式 `/pm-workflow` 而非纯自动**。
- `sohei56/maul-team`【一方称：skillget.dev + github.com/sohei56/maul-team，early access】——与用户设想**最接近的成熟形态**：19 个 skill 覆盖完整 Scrum 生命周期 + hooks（status-gate、DoD 质量门、stall-watchdog 卡死看门狗、completion-gate）+ `.scrum/` 落盘状态 + "把想要的行为变成机制（turning behaviors into mechanisms）"；**入口是 `scrum-start.sh` 程序拉起，不是模型自觉**。
- `github-project-management`【一方称：claudskills.com 社区草稿】——GitHub Projects v2 自动化 skill（star 拓扑 + 三条 SOP），重依赖外部 MCP、缺自测，草稿级。
- **猎寻结论（如实）**：项目管理类成熟 skill 存在（maul-team、pm-skills），但**无一纯 NL**——全部叠加 scripts/hooks/测试；**未找到**"仅把协作规则写成纯 SKILL.md、靠模型自动识别就跑得稳"的实例。

---

## 五、用户设想对照

| 你的设想 | 业界事实 | 异同判断 |
|---|---|---|
| "项目规则本身就是一个 Skill" | 官方（OpenAI linear skill、Claude skills 生态）+ 社区（maul/pm-skills）都把可复用流程规则包成 Skill | **成立且主流**；但成熟实例均叠加程序约束，纯 NL 无先例 |
| "主 Agent 识别项目管理场景 → 自觉加载 Skill" | 触发可信度：程序驱动 > 约定式自动 > 语义自觉；Claude 靠 description 语义匹配（最弱档） | **可行但要兜底**：description 必须精准 + 配显式入口/指针；编排 Agent 的"意图路由"职责正好补这个兜底 |
| "在项目交接文档处放置 Skill" | Skill 官方落点 = 全局 `~/.claude/skills` 或项目 `.claude/skills`；**放置位置只决定可发现性，不决定触发** | **放指针而非本体**：交接文档写"何时调、调哪个"，本体放全局复用 |
| "Skill 执行仓库内项目管理规则" | 规则应拆两层：通用流程纪律（Skill）+ 项目专属上下文（交接文档/AGENTS.md）+ 机器强制（程序层） | **一致**：与"薄门面 + 指针 + Skill + 程序约束"四层同构 |

**关键机制点**：交接文档（STANDARDS §16 是"新会话恢复上下文的第一入口"）若想让新会话拿到 PM Skill，正确姿势是——AGENTS.md（自动加载的门面）写触发声明 → 交接文档作为第一入口被读取 → 交接文档显式指向/声明调用 Skill（description 触发词）→ Skill 执行规则。**而不是指望"放旁边就生效"**。

---

## 六、推荐：交接文档处到底放什么

### 三方案代价与边界对比

| 方案 | 放什么 | 优点 | 代价/边界 |
|---|---|---|---|
| A. Skill 本体 | 把 SKILL.md 复制进每个项目交接文档目录 | 就近、自包含 | **规则版本化灾难**：每项目一份副本，改规则要全量同步；违背"引用不镜像"（PRD 决策准则 5）；Skill 本体含 references 目录，交接文档会膨胀 |
| B. Skill 指针（推荐） | 交接文档写一行触发声明 + 指向全局 Skill（如"项目管理场景 → 加载 project-pm-tracker（.user_skills），触发词：进度/PRD/评审"） | 单源维护、跨项目复用、符合官方放置约定；指针可带触发词提升 description 匹配率 | 依赖加载机制正确（需配 AGENTS.md 门面声明 + 编排 Agent 路由兜底）；指针失效时需 lint 检查 |
| C. 纯 AGENTS.md 入口 + 程序约束 | 不引入 Skill 概念，全部规则写 AGENTS.md/交接文档 + contracts/orchestrator | 最简、自动加载 | 启动即全量注入、context 贵；跨项目规则无法复用；CLAUDE.md <200 行硬上限会迅速触顶；纯 NL 不可强制 |

### 推荐落地（四层，与三路调研证据一一对应）

1. **仓库根 `AGENTS.md`（薄门面，跨工具自动加载）**：加一行触发声明——"涉及项目管理/进度/待办/PRD/评审/复盘 → 调用 `project-pm-tracker` Skill（.user_skills 全局）"。依据：AGENTS.md 是 Codex/Claude/Cursor/Cline 共同自动加载的入口（前两轮已证），一行即可让"识别场景"从最外层发生。
2. **项目交接文档（STANDARDS §16 第一入口）**：五段式现有内容不变，加一节「能力接入」：声明"本项目由 project-pm-tracker 承担盯项目/产品决策，触发词：xxx；本项目专属约定：xxx"。**放指针，不放本体**——交接文档=每项目一变，Skill=跨项目不变，单源维护。
3. **Skill 本体（project-pm-tracker，全局 .user_skills）**：承载"怎么盯项目、怎么做产品决策"的复用流程（现状已如此，无需搬动）；若落地强化，加：① description 精修（做什么+何时用+关键词，对照 agentskills.io 规范 ≤1024 字符）；② 触发测试（`claude plugin eval` 式 tool_used: Skill grader，或 pm-skills 式 pytest——验证"该触发时触发、不该触发时不触发"）。
4. **程序约束层（contracts/orchestrator，前两轮已定）**：6 步闭环图、schema 校验器、owner_gate 不变——Skill 里的"先读总仓、事实判断分离、停顿点、落痕"是 NL 引导，机器强制仍在程序层（"prompt 只是请求，hook 才是强制"）。

**一句话**：交接文档处放**指针**（何时调、调哪个、本项目专属约定），Skill 本体留全局，AGENTS.md 做触发门面，程序约束管强制——四层各司其职，与官方边界表（CLAUDE.md/Skill/Subagent/Tool/Hook）和社区成熟实践（maul/pm-skills 的"薄门面+指针+本体+程序"）完全同构。

---

## 七、待拍板问题清单

1. **交接文档加「能力接入」节**（指针形态，见第六节）是否采纳？
2. **触发兜底**：除 AGENTS.md 声明 + description 匹配外，是否让编排 Agent 的意图路由把"项目管理场景"识别作为显式入口（程序驱动档）？——建议采纳，属编排 Agent 本职（意图路由），可测。
3. **project-pm-tracker description 精修**：按 agentskills.io 规范（≤1024 字符、写清做什么+何时用+关键词、与 soul/其他 Skill 边界不重叠）改写，是否现在做？
4. **Skill 测试投入**：是否引入 `claude plugin eval`（tool_used: Skill grader）或 pm-skills 式 pytest 验证触发命中率？（第三轮结论：纯 NL 无先例，成熟实例都有测试——建议至少做触发命中率小样本）
5. **MCP 是否纳入**：项目协作类工具（GitHub/Linear）后续走 MCP 还是继续纯文件/CLI？（本轮结论：MCP 给工具、Skill 给流程，规则不进 MCP——是否接 MCP 待定，不影响本轮 Skill 形态决策）
6. **落档**：本报告与前三轮报告统一归档（建议 GitHub 仓 `docs/调研/`，上一轮草案已含）是否确认？

---

## 八、来源清单

**Skill 形态本体（第三轮-A）**：
- anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills（已查证，2025-10-16；文末注记 2025-12-18 已作为开放标准发布）
- agentskills.io/specification（已查证；含 `skills-ref validate` 官方校验器）
- code.claude.com/docs/en/features-overview（已查证；扩展层边界表 + "Build your setup over time"触发表）
- code.claude.com/docs/en/skills（已查证；触发机制与锁档字段）
- platform.claude.com/docs/en/agents-and-tools/agent-skills/overview（已查证）
- github.com/anthropics/skills（已查证；官方示例仓库与 template）
- OthmanAdi/planning-with-files、编号交付 pipeline、aidankinzett/claude-git-pr-skill（存在性交叉核对；细节经 Snyk 榜单/社区转述，一方称）
- 聚合站 agskills.dev / skillmd.ai / LobeHub（一方称）

**指令文件与 MCP 对照（第三轮-B）**：
- github.com/github/awesome-copilot 根 AGENTS.md（raw 全文已查证；PR Guidelines/Review Checklist/validate 脚本）
- github.com/github/github-mcp-server（已查证，33.5k star）
- linear.app/docs/mcp（工具清单经 openai/skills curated 目录交叉核验）
- github.com/openai/skills `.curated/linear/SKILL.md`（raw 全文已查证；MCP 工具 + 流程规则混合样板）
- claude.com/blog/skills-explained（已查证；"跨项目复制同一段指令 → 做成 skill"）
- anthropic.com/news/building-effective-agents（前轮已查证；gate 程序校验）

**触发机制与"规则即 Skill"案例（第三轮-C）**：
- code.claude.com/docs/en/skills + platform.claude.com/docs（已查证；渐进披露/锁档/validate/eval）
- Munder HIVE.md 本地核验（`C:\Users\A\Doubao\chats\2026-10-06\new-chat\_agent_ui_shots\HIVE.md`，已查证；消息+Stop hook+registry 程序驱动）
- npmjs.com/package/@ethansmc/pm-skills（已查证；12 skill + 测试）
- skillget.dev/listings/sohei56-claude-scrum-team + github.com/sohei56/maul-team（一方称；19 skill + hooks）
- claudskills.com/skills/when-managing-github-projects-use-github-project-management（一方称，社区草稿）
- Cursor rules / Cline paths / GitHub Copilot 目录就近（前轮已核验，本轮引用）

---

*调研执行：三路并行（Skill 形态本体与生态 / 指令文件与 MCP 对照 / 触发机制与"规则即 Skill"案例）；本报告整合定稿 2026-10-09。*

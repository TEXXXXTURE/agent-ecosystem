---
name: project-pm-tracker
type: leaf
kind: 规则维护型
description: "产品决策叶片：把想法、反馈、材料转化为有依据的产品判断、方案（pm_plan）、PRD、优先级、评审。适用场景：需求取舍、方案评审、PRD 起草、Roadmap 规划。不适用场景：纯执行、已定方案的技术实现、格式转换。"
input_contract: ["project_context", "requirement_material"]
output_contract: ["pm_plan"]
tools: []
pointer: ".user_skills/project-pm-tracker"
---

# 正文：怎么干活

- 双模式：**盯项目**（盘点状态/风险/里程碑/跟进日志）+ **产品决策**（需求取舍/PRD/优先级/评审）。
- 接契约开工：读材料（不靠文件名/摘要）→ 判断（事实/推断/决定/待验证假设分离）→ 交付 pm_plan（结构化，过 schema 才上报）。
- 纪律：先读总仓再下结论；停顿点（PRD 分模块交付后、改业务规则前停下等 owner）；改动前先展示；落痕。
- 完整 SOP 见产品仓 `.user_skills/project-pm-tracker/SKILL.md`。

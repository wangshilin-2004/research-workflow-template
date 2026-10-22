# Research Workflow Template

面向长期科研和不同 AI 交替接手的通用模板。独立于学科、模型、AI 产品和具体论文。不把聊天记录当作唯一记忆。

## 核心原则

研究问题先于工具；证据决定去留；官方基线与自写探针分开；保留负结果及其适用范围；事实、假设、决策、计划分开。保存可公开核查的决策依据，不要求 AI 提供内部推理过程。

## 开始使用

1. 阅读 [WORKFLOW.md](WORKFLOW.md)。
2. 把 research 模板初始化到项目（只创建不存在的文件；有冲突则整体停止，不覆盖）：

```bash
python3 tools/init_project.py --project /path/to/project
```

3. 填写 `research/BRIEF.md`、`research/PREFERENCES.md` 和 `research/STATUS.md`。在项目原有 AGENTS.md 或其他 AI 入口中加入“先阅读 research/START_HERE.md”；不要覆盖原有规则。
4. 每轮工作更新状态、证据和决策；用实验模板记录验证。不要一开始强制填满所有文件。
5. 换 AI 时让它读 `research/START_HERE.md`。无法访问文件的 AI，可接收单文件交接包：

```bash
python3 tools/export_handoff.py --project /path/to/project --output /path/to/handoff.md
```

导出只包含明确列出的研究记录和文件哈希，不自动包含原始数据、凭据、代码或整段聊天。发送到其他平台前由使用者核查内容；具体项目的隐私级别不会因为采用通用模板而降低。

## 接手消息

> 请先阅读 research/START_HERE.md 及其要求的文件。先用简短文字复述研究目标、已验证事实、当前任务和不能声称的结论，核查代码与结果是否存在，再继续 STATUS.md 的下一项工作。不要把历史计划当作当前任务，不要重跑已完成实验。若没有文件访问能力，请列出准确缺少的文件，不猜测。

## 文件职责

- BRIEF：研究问题与范围。
- PREFERENCES：经用户确认的协作习惯。
- STATUS：唯一当前任务入口，会覆盖更新。
- IDEAS：假设及其证据状态。
- EVIDENCE：有来源的结果索引。
- DECISIONS：追加式决策演变。
- ENVIRONMENT：可复现环境、路径和运行方式，不存秘密。
- DELIVERIES：每轮AI交付与接手核查；使用DELIVERY_TEMPLATE统一交付。
- HANDOFF_CHECKLIST：接手/交出时核查事项。

这是项目记忆协议，不会自动在不同平台之间同步、授予工具权限或启动 AI。接手方仍需仓库权限、必要结果文件及用户授权。模板变更不自动覆盖已经实例化的项目。

## 验证工具

```bash
python3 -m unittest discover -s tests -v
```

## 阶段复盘与方法积累（模板 v2）

新项目包含 RESEARCH_REVIEW（全局目的与下一项决策）和 LESSONS（有证据与边界的经验）。已有项目只补充缺失文件并审查规则，不覆盖其事实记录。导出器兼容没有这两个文件的 v1 项目；存在时纳入交接包。通用流程明确区分探针、筛选和确认，包含机制对照、异步计时、负结果边界与纠错纪律。

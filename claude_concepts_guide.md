# Claude Code 概念总览

这个文件用于把仓库里最容易混淆的几个核心概念放在一起解释。

## 1. Slash Commands（快捷命令）

用户主动输入的快捷命令，适合显式触发某个动作。

## 2. Memory（记忆）

长期自动加载的上下文，适合放项目规则和个人偏好。

## 3. Skills（技能）

可复用、可自动触发的能力，适合沉淀稳定工作流。

`v2.1.176` 这轮同步后，特别值得关注这些 bundled skills、plugin 和排障入口：

- `/run`：启动当前项目，确认改动能真实运行
- `/verify`：构建、运行并观察应用，确认修复不是只停留在测试通过
- `/run-skill-generator`：为项目生成专属 run / verify skill
- `/code-review [effort]`：审查当前 diff 的正确性缺陷
- `/simplify`：清理型审查，关注复用、简化、效率和抽象层级，并应用修复
- `/reload-skills`：重新扫描 skill 目录，不需要重启当前 session
- `disableBundledSkills` / `CLAUDE_CODE_DISABLE_BUNDLED_SKILLS=1`：隐藏内置 skills、workflows 和 commands
- `claude plugin init <name>`：在 `.claude/skills` 中脚手架本地 plugin，放在该目录的 plugin 会自动加载
- `/plugin list --enabled` / `--disabled`：按启用状态查看 installed plugins

## 4. Subagents（子代理）

用于复杂任务拆分和专业分工的子代理。

从 `v2.1.172+` 起，subagent 可以再 spawn 子 subagent，最多嵌套 5 层；如果要限制可 spawn 的对象，保留 `Agent(agent_type)` 语法，不要翻译成中文字段。

## 5. MCP（外部工具协议）

让 Claude 连接外部工具和实时数据的协议。

## 6. Hooks（钩子）

在特定事件上自动执行动作的机制。

从 `v2.1.172+` 起，hook handler 可以加 `if` 条件，用 `Edit(src/**)`、`Read(.env)`、`Bash(git push *)` 这类 permission-rule 语法按工具参数继续收窄匹配。

这轮同步移除了上一版里关于 `Stop` / `SubagentStop` 可读取 `background_tasks`、`session_crons` 的说明；当前官方 hooks reference 没有列出这两个字段，写 hook 时不要依赖它们。

## 7. Plugins（插件）

把 commands、skills、MCP、hooks、subagents 打包成整套方案。

## 8. Checkpoints（检查点）

用于安全试错和回退。

## 9. CLI（命令行）

Claude Code 的核心使用入口，也是自动化、脚本化和 CI/CD 的关键接口。

`claude agents --json` 可以把 Agent View 列表输出为机器可读 JSON，适合接状态栏、脚本巡检或自定义 session picker。

在 `claude agents` 视图里，`Ctrl+T` 可以固定后台 session。已固定的 session 空闲时会被优先保留，升级 Claude Code 时也会在原位重启，只有内存压力较大时才会在未固定 session 之后被清理。

`/usage` 的成本页现在会按 skills、subagents、plugins、MCP server 等类别拆分，排查“钱花在哪里”会更直观。

`v2.1.174+` 的 VSCode Account & usage 视图还会显示 cache miss、long-context cost、subagents，以及 per-skill / per-agent / per-plugin / per-MCP 归因。

`/workflows` 可以查看 dynamic workflows 的运行记录，适合大规模审查、迁移、全仓扫描这类需要多代理编排的任务。

`v2.1.160` 起，dynamic workflows 的触发关键词是 `ultracode`；裸词 `workflow` 不再触发运行。

`/model` 的默认行为也要注意：`v2.1.153+` 起选择模型会保存为后续 session 默认值；如果只想作用于当前 session，选中后按 `s`。

`--safe-mode` / `CLAUDE_CODE_SAFE_MODE=1` 适合排查自定义配置问题；`fallbackModel` 适合给主模型不可用时准备有序 fallback。

`wheelScrollAccelerationEnabled`、`footerLinksRegexes`、`language` 是 settings.json 里的 key，说明文字可以中文化，但 key 本身不要翻译。

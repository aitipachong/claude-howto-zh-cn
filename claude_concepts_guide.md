# Claude Code 概念总览

这个文件用于把仓库里最容易混淆的几个核心概念放在一起解释。

## 1. Slash Commands（快捷命令）

用户主动输入的快捷命令，适合显式触发某个动作。

## 2. Memory（记忆）

长期自动加载的上下文，适合放项目规则和个人偏好。

## 3. Skills（技能）

可复用、可自动触发的能力，适合沉淀稳定工作流。

`v2.1.145+` 后特别值得关注三个 bundled skills：

- `/run`：启动当前项目，确认改动能真实运行
- `/verify`：构建、运行并观察应用，确认修复不是只停留在测试通过
- `/run-skill-generator`：为项目生成专属 run / verify skill

## 4. Subagents（子代理）

用于复杂任务拆分和专业分工的子代理。

## 5. MCP（外部工具协议）

让 Claude 连接外部工具和实时数据的协议。

## 6. Hooks（钩子）

在特定事件上自动执行动作的机制。

`Stop` / `SubagentStop` 现在可以读取 `background_tasks` 和 `session_crons`，适合在 session 结束前确认后台任务或 `/schedule` 任务没有被遗漏。

## 7. Plugins（插件）

把 commands、skills、MCP、hooks、subagents 打包成整套方案。

## 8. Checkpoints（检查点）

用于安全试错和回退。

## 9. CLI（命令行）

Claude Code 的核心使用入口，也是自动化、脚本化和 CI/CD 的关键接口。

`claude agents --json` 可以把 Agent View 列表输出为机器可读 JSON，适合接状态栏、脚本巡检或自定义 session picker。

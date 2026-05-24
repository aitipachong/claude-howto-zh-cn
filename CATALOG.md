<picture>
  <source media="(prefers-color-scheme: dark)" srcset="resources/logos/claude-howto-logo-dark.svg">
  <img alt="Claude How To" src="resources/logos/claude-howto-logo.svg">
</picture>

# Claude Code 功能总表（Feature Catalog）

> 适合“先建立全局地图，再进入某个模块”的读者。

**快速导航**：  
[Slash Commands](#slash-commands快捷命令) | [Permission Modes](#permission-modes权限模式) | [Subagents](#subagents子代理) | [Skills](#skills技能) | [Plugins](#plugins插件) | [MCP](#mcp外部工具协议) | [Hooks](#hooks钩子) | [Memory](#memory记忆) | [新功能提示](#新功能提示)

---

## 总览

| 类别 | 内建能力 | 仓库示例 | 适合先学吗 | 入口 |
|------|----------|----------|------------|------|
| Slash Commands | 60+ | 8 | 非常适合 | [01-slash-commands/](01-slash-commands/) |
| Memory | 7 类 | 3 | 非常适合 | [02-memory/](02-memory/) |
| Skills | 9 个 bundled skills + 示例 | 多个 | 适合进阶 | [03-skills/](03-skills/) |
| Subagents | 6 个内建 | 多个 | 适合进阶 | [04-subagents/](04-subagents/) |
| MCP | 1 个内建生态入口 + 示例 | 多个 | 适合集成场景 | [05-mcp/](05-mcp/) |
| Hooks | 29 个事件 | 9 | 适合自动化 | [06-hooks/](06-hooks/) |
| Plugins | - | 3 | 适合团队级方案 | [07-plugins/](07-plugins/) |
| Checkpoints | 内建 | 示例文档 | 新手必学 | [08-checkpoints/](08-checkpoints/) |
| Advanced Features | 多项 | 示例文档 | 高阶再学 | [09-advanced-features/](09-advanced-features/) |
| CLI | 内建 | 参考文档 | 全阶段都用得到 | [10-cli/](10-cli/) |

---

## Slash Commands（快捷命令）

slash commands 是用户在 Claude Code 里主动输入的快捷操作，例如 `/help`、`/model`、`/rewind`。这也是新手最容易立刻感受到收益的能力。

### 常见内建命令

| 命令 | 用途 |
|------|------|
| `/help` | 查看帮助 |
| `/clear` | 清空当前对话 |
| `/config` | 查看或编辑配置 |
| `/agents` | 查看可用 agents |
| `/skills` | 查看可用 skills |
| `/hooks` | 查看 hooks |
| `/mcp` | 查看或管理 MCP servers |
| `/plugin` | 管理 plugins |
| `/plan` | 进入 planning mode |
| `/proactive` | `/loop` 的别名 |
| `/recap` | 返回旧 session 时快速回顾上下文 |
| `/rewind` | 回退到 checkpoint |
| `/resume` | 恢复之前的 session |
| `/team-onboarding` | 根据当前项目配置生成新人上手说明 |
| `/tui` | 切换全屏 TUI 模式 |
| `/focus` | 切换 focus view |
| `/undo` | `/rewind` 的别名 |
| `/ultraplan` | 把计划起草交给浏览器里的云端会话 |
| `/ultrareview` | 云端多代理代码审查 |
| `/less-permission-prompts` | 分析调用记录并建议 allowlist |
| `/usage-credits` | 配置额外用量额度；`/extra-usage` 仍可作为 alias 使用 |
| `/branch` | 从当前对话分叉（某些版本中 `/fork` 仍可能可用） |

### 仓库里的示例命令

| 命令 | 文件 | 典型用途 |
|------|------|----------|
| `/optimize` | `01-slash-commands/optimize.md` | 性能分析 |
| `/pr` | `01-slash-commands/pr.md` | PR 准备流程 |
| `/generate-api-docs` | `01-slash-commands/generate-api-docs.md` | API 文档生成 |
| `/commit` | `01-slash-commands/commit.md` | 带上下文的提交说明 |
| `/push-all` | `01-slash-commands/push-all.md` | stage + commit + push |
| `/doc-refactor` | `01-slash-commands/doc-refactor.md` | 文档重构 |
| `/setup-ci-cd` | `01-slash-commands/setup-ci-cd.md` | CI/CD 初始化 |
| `/unit-test-expand` | `01-slash-commands/unit-test-expand.md` | 测试补全 |

**适合先学的原因**：复制文件就能用，反馈快，挫败感低。

---

## Permission Modes（权限模式）

permission modes 决定 Claude Code 在使用工具时需要多大授权。

| 模式 | 说明 | 适合什么时候 |
|------|------|--------------|
| `default` | 大多数风险操作前询问 | 日常交互 |
| `acceptEdits` | 自动接受文件编辑，其他操作仍可能询问 | 较信任的本地编辑 |
| `plan` | 只读分析，不做修改 | 方案设计、代码阅读 |
| `dontAsk` | 跳过需要额外授权的动作 | 非交互脚本 |
| `bypassPermissions` | 跳过权限检查 | 可信、受控的自动化环境 |
| `auto` | 根据分类器自动决定 | 高自动化流程（需要谨慎） |

中国用户在刚上手时，优先理解 `default`、`acceptEdits`、`plan`、`dontAsk` 这四个就足够了。

---

## Subagents（子代理）

subagents 是专门负责某类任务的子代理。它们适合复杂任务拆分，比如“一个做代码审查，一个做测试，一个做文档”。

### 常见内建 subagents

| 名称 | 典型用途 |
|------|----------|
| `general-purpose` | 通用复杂任务 |
| `Plan` | 方案设计 |
| `Explore` | 快速搜索与理解代码 |
| `Bash` | 终端命令执行 |

### 仓库里的示例 subagents

| 名称 | 文件 | 用途 |
|------|------|------|
| `code-reviewer` | `04-subagents/code-reviewer.md` | 代码质量审查 |
| `test-engineer` | `04-subagents/test-engineer.md` | 测试策略 |
| `documentation-writer` | `04-subagents/documentation-writer.md` | 文档撰写 |
| `secure-reviewer` | `04-subagents/secure-reviewer.md` | 安全审查 |
| `implementation-agent` | `04-subagents/implementation-agent.md` | 实现任务 |
| `debugger` | `04-subagents/debugger.md` | 根因分析 |
| `data-scientist` | `04-subagents/data-scientist.md` | 数据与 SQL 分析 |
| `performance-optimizer` | `04-subagents/performance-optimizer.md` | Profiling 与性能优化 |

---

## Skills（技能）

skills 是 Claude Code 会根据描述自动触发的复用能力。它们往往比单个 slash command 更适合长期维护的工作流。

### 仓库里的示例 skills

| 名称 | 文件夹 | 典型用途 |
|------|--------|----------|
| `code-review` | `03-skills/code-review/` | 代码审查 |
| `brand-voice` | `03-skills/brand-voice/` | 文案语气统一 |
| `doc-generator` | `03-skills/doc-generator/` | 文档生成 |
| `refactor` | `03-skills/refactor/` | 结构化重构 |

### Claude Code 自带 bundled skills

这些是 Claude Code 自带的 skills，不需要从本仓库复制安装：

| 名称 | 典型用途 |
|------|----------|
| `/batch` | 跨大量文件批量执行同一类修改 |
| `/claude-api` | 加载 Claude API / SDK 参考 |
| `/debug` | 读取 debug log 并排查当前 session 问题 |
| `/fewer-permission-prompts` | 扫描调用记录并建议更合理的 allowlist |
| `/loop` | 按间隔重复执行 prompt |
| `/run` | 启动当前项目，实际看改动是否跑起来 |
| `/run-skill-generator` | 为项目生成 `/run` / `/verify` 所需的运行技能 |
| `/simplify` | 从复用性、质量和效率角度审查改动 |
| `/verify` | 构建、运行并观察应用，确认修复真的有效 |

### skill 结构

```text
.claude/skills/skill-name/
├── SKILL.md
├── scripts/
└── templates/
```

### 高风险提醒

`SKILL.md` 里的 frontmatter 是可执行配置的一部分，不要翻译这些字段：

- `name`
- `description`
- `effort`
- `shell`

---

## Plugins（插件）

plugins 适合“把整套方案打包给团队用”。它们通常会组合多个能力：

- slash commands
- skills
- subagents
- MCP
- hooks

### 仓库里的示例 plugins

| 名称 | 位置 | 用途 |
|------|------|------|
| `pr-review` | `07-plugins/pr-review/` | PR 审查工作流 |
| `documentation` | `07-plugins/documentation/` | 文档生成与同步 |
| `devops-automation` | `07-plugins/devops-automation/` | 部署、监控与事故处理 |

### plugin 结构

```text
plugin-name/
├── .claude-plugin/plugin.json
├── commands/
├── agents/
├── hooks/
├── mcp/
└── scripts/
```

`.claude-plugin/plugin.json` 是 manifest，`name`、`version`、`description`、`license` 这些 key 不要翻。

---

## MCP（外部工具协议）

MCP（Model Context Protocol）用于让 Claude Code 连接外部工具、服务和实时数据。

### 仓库里的典型 MCP 配置

| 文件 | 用途 |
|------|------|
| `05-mcp/github-mcp.json` | GitHub 集成 |
| `05-mcp/database-mcp.json` | 数据库访问 |
| `05-mcp/filesystem-mcp.json` | 文件系统访问 |
| `05-mcp/multi-mcp.json` | 多服务组合 |

### 中国用户常见卡点

- `npx` 首次安装 MCP server 时很慢
- GitHub Token 没权限或没导出
- Windows / WSL 环境下 shell 和路径行为不同

### 高风险提醒

以下内容不要翻：

- `mcpServers`
- server 名称，例如 `github`
- 环境变量名，例如 `GITHUB_TOKEN`
- 路径占位符和命令字段

---

## Hooks（钩子）

hooks 是事件驱动的自动化动作。适合这些场景：

- 调工具前做风险拦截
- 提交前跑测试
- 改完代码后自动格式化
- 结束前记录上下文

### 仓库里的示例 hooks

| 文件 | 用途 |
|------|------|
| `06-hooks/pre-commit.sh` | 提交前跑测试 |
| `06-hooks/format-code.sh` | 自动格式化 |
| `06-hooks/security-scan.sh` | 安全检查 |
| `06-hooks/pre-tool-check.sh` | Bash 高风险命令预检查 |
| `06-hooks/validate-prompt.sh` | prompt 校验 |
| `06-hooks/log-bash.sh` | Bash 日志记录 |
| `06-hooks/dependency-check.sh` | 依赖清单变更后的漏洞扫描 |

### hook 类型

- `command`
- `http`
- `mcp_tool`
- `prompt`
- `agent`

这些类型名同样不要翻成中文字段。

---

## Memory（记忆）

memory 是 Claude Code 用来长期加载规则和上下文的机制。

### 本仓库里的 memory 示例

| 文件 | 用途 |
|------|------|
| `02-memory/project-CLAUDE.md` | 项目规则 |
| `02-memory/personal-CLAUDE.md` | 个人偏好 |
| `02-memory/directory-api-CLAUDE.md` | 目录级规则示例 |

### 新手最重要的理解

- `CLAUDE.md` 不是随便写笔记的地方，它更像项目规范和上下文入口。
- 项目级和个人级 memory 适合放不同内容。
- memory 很强，但它不替代 skills、hooks 和 slash commands。
- 旧教程里常见的 `# ...` 快捷写 memory 已经停用；现在请用 `/memory` 或自然语言更新。

---

## 新功能提示

这个仓库同步的是 Claude Code 较新的能力集，因此你会在文档里频繁看到这些内容：

- Auto Mode
- Monitor Tool
- `/tui`
- `/focus`
- `/recap`
- `/undo`
- `/proactive`
- `/ultrareview`
- `/less-permission-prompts`
- `/usage-credits`
- `/team-onboarding`
- `/ultraplan`
- `/goal`
- `/scroll-speed`
- `/run`
- `/verify`
- `/run-skill-generator`
- `claude agents --json`
- Stop / SubagentStop hook 的 `background_tasks` 和 `session_crons`
- Voice Dictation
- Channels
- background tasks
- scheduled tasks
- worktrees
- web sessions
- remote control

如果你是初学者，不需要先掌握这些。按 [LEARNING-ROADMAP.md](LEARNING-ROADMAP.md) 的顺序往下学即可。

---

## 推荐阅读顺序

1. [README.md](README.md)
2. [LEARNING-ROADMAP.md](LEARNING-ROADMAP.md)
3. [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
4. [01-slash-commands/](01-slash-commands/)
5. [02-memory/](02-memory/)
6. [10-cli/](10-cli/)

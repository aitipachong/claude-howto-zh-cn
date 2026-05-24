<picture>
  <source media="(prefers-color-scheme: dark)" srcset="resources/logos/claude-howto-logo-dark.svg">
  <img alt="Claude How To" src="resources/logos/claude-howto-logo.svg">
</picture>

# Claude Code 速查卡（Quick Reference）

这份速查卡适合两种场景：

- 你已经知道大概原理，现在只想快速复制命令
- 你正在本土化或二次改写仓库，想快速确认哪些路径和标识不能动

---

## 🚀 安装命令速查

### Slash Commands（快捷命令）

```bash
# 安装全部示例 slash commands
cp 01-slash-commands/*.md .claude/commands/

# 安装单个命令
cp 01-slash-commands/optimize.md .claude/commands/
```

### Memory（记忆）

```bash
# 项目级 memory
cp 02-memory/project-CLAUDE.md ./CLAUDE.md

# 个人级 memory
cp 02-memory/personal-CLAUDE.md ~/.claude/CLAUDE.md
```

### Skills（技能）

```bash
# 个人 skills
cp -r 03-skills/code-review ~/.claude/skills/

# 项目 skills
cp -r 03-skills/code-review .claude/skills/
```

### Subagents（子代理）

```bash
# 安装全部 subagents
cp 04-subagents/*.md .claude/agents/

# 安装单个 subagent
cp 04-subagents/code-reviewer.md .claude/agents/
```

### MCP（外部工具协议）

```bash
# 先准备凭证
export GITHUB_TOKEN="your_token"
export DATABASE_URL="postgresql://..."

# 项目级 MCP 配置
cp 05-mcp/github-mcp.json .mcp.json

# 或者写进用户级配置 ~/.claude.json
```

### Hooks（钩子）

```bash
mkdir -p ~/.claude/hooks
cp 06-hooks/*.sh ~/.claude/hooks/
chmod +x ~/.claude/hooks/*.sh
```

### Plugins（插件）

```bash
/plugin install pr-review
/plugin install devops-automation
/plugin install documentation
```

### Checkpoints（检查点）

```bash
# checkpoints 默认自动创建
/rewind
```

### Advanced Features（高级功能）

```bash
# 进入规划模式
/plan Task description

# 把复杂规划交给云端会话起草
/ultraplan Task description

# 为新同事生成项目 onboarding guide
/team-onboarding

# 额外用量配置
/usage-credits       # `/extra-usage` 仍可作为兼容 alias

# 常见 permission mode
claude --permission-mode default
claude --permission-mode acceptEdits
claude --permission-mode plan
claude --permission-mode dontAsk
claude --permission-mode bypassPermissions

# session 常用命令
/resume
/rename "session-name"
/branch                # 某些版本中 `/fork` 仍可作为兼容别名
claude -c
claude -r "session-name"
claude agents --json   # 机器可读的 Agent View 列表
```

---

## 📋 功能速查表

| 能力 | 安装 / 所在位置 | 典型用法 | 备注 |
|------|------------------|----------|------|
| Slash Commands | `.claude/commands/*.md` | `/command-name` | 用户主动触发 |
| Memory | `./CLAUDE.md` / `~/.claude/CLAUDE.md` | 自动加载 | 长期规则和偏好 |
| Skills | `.claude/skills/*/SKILL.md` | 自动触发 | 可复用工作流 |
| Subagents | `.claude/agents/*.md` | 自动委派 / 显式调用 | 分工执行 |
| MCP | `.mcp.json` / `~/.claude.json` | `/mcp`、工具调用 | 实时外部能力 |
| Hooks | `~/.claude/hooks/*.sh` 等 | 事件触发 | 自动检查和自动化 |
| Plugins | `/plugin install` | 一次安装多能力 | 团队分发 |
| Checkpoints | 内建 | `Esc+Esc`、`/rewind` | 安全试错 |
| Planning Mode | 内建 | `/plan <task>` | 复杂任务规划 |
| Ultraplan | 内建 | `/ultraplan <task>` | 云端起草复杂计划 |
| Monitor Tool | 内建 | 监控后台命令 stdout 事件流 | 适合替代轮询 |
| Print Mode | 内建 | `claude -p` | 脚本 / CI/CD |
| Run / Verify Skills | bundled skills | `/run`、`/verify`、`/run-skill-generator` | 启动项目并确认改动真实可用 |

---

## 🧠 哪些标识不能翻

这部分最容易踩坑，单独列出来：

- `/optimize`、`/pr`、`/review-pr`
- `skills`、`hooks`、`MCP`、`CLI`
- `allowed-tools`、`tools`、`model`、`env`
- `GITHUB_TOKEN`、`DATABASE_URL`
- `.mcp.json`
- `claude -p`

想继续中文化仓库时，先看：

- [LOCALIZATION-STYLE.md](LOCALIZATION-STYLE.md)
- [UPSTREAM.md](UPSTREAM.md)

---

## 🎯 常见场景速查

### 代码审查

```bash
# 方法 1：slash command
cp 01-slash-commands/optimize.md .claude/commands/
# 使用：/optimize

# 方法 2：subagent
cp 04-subagents/code-reviewer.md .claude/agents/

# 方法 3：skill
cp -r 03-skills/code-review ~/.claude/skills/

# 方法 4：plugin
/plugin install pr-review
```

### 文档生成

```bash
cp 01-slash-commands/generate-api-docs.md .claude/commands/
cp 04-subagents/documentation-writer.md .claude/agents/
cp -r 03-skills/doc-generator ~/.claude/skills/
/plugin install documentation
```

### DevOps（运维自动化）

```bash
/plugin install devops-automation
# 常见命令：/deploy /rollback /status /incident
```

### 团队规范

```bash
cp 02-memory/project-CLAUDE.md ./CLAUDE.md
```

### 自动化与 Hooks

```bash
mkdir -p ~/.claude/hooks
cp 06-hooks/*.sh ~/.claude/hooks/
chmod +x ~/.claude/hooks/*.sh

# 常见例子
# - pre-commit.sh
# - format-code.sh
# - security-scan.sh
```

### 安全试错

```bash
# 修改前后都记得 checkpoint 可回退
/rewind
```

### CI/CD

```bash
claude -p "Run all tests and generate report"
claude -p "Run tests" --permission-mode dontAsk
```

---

## 🇨🇳 中国用户特别注意

### GitHub 访问和 Token

- 很多 MCP 示例、plugin 示例默认依赖 GitHub。
- 开始之前先确认你能访问 GitHub，并且 `GITHUB_TOKEN` 具备需要的 scope。

### `npm` / `npx` / `uv` 使用提醒

- 很多示例会用到 `npx` 安装 MCP server。
- Python 相关脚本和测试通常依赖 `uv`。
- 如果第一次安装很慢，优先检查网络、代理、包管理镜像和证书环境。

### Windows / WSL 使用提醒

- 如果你在 Windows 上，优先明确自己是在 PowerShell、Git Bash，还是 WSL 里操作。
- 部分 shell 脚本和路径写法默认更偏 Unix / macOS / Linux 风格。

### 翻译不要碰的地方

- frontmatter 字段名
- JSON key
- shell 命令
- 环境变量
- slash command / skill / plugin / subagent 的名称
- hook 输入字段，例如 `background_tasks`、`session_crons`

---

## 🔗 常用入口

- [README.md](README.md)
- [LEARNING-ROADMAP.md](LEARNING-ROADMAP.md)
- [CATALOG.md](CATALOG.md)
- [01-slash-commands/](01-slash-commands/)
- [02-memory/](02-memory/)
- [03-skills/](03-skills/)
- [04-subagents/](04-subagents/)
- [05-mcp/](05-mcp/)
- [06-hooks/](06-hooks/)
- [07-plugins/](07-plugins/)
- [09-advanced-features/](09-advanced-features/)
- [10-cli/](10-cli/)

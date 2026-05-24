<picture>
  <source media="(prefers-color-scheme: dark)" srcset="resources/logos/claude-howto-logo-dark.svg">
  <img alt="Claude How To" src="resources/logos/claude-howto-logo.svg">
</picture>

[![Source Project](https://img.shields.io/badge/source-luongnv89%2Fclaude--howto-24292f)](https://github.com/luongnv89/claude-howto)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Localization](https://img.shields.io/badge/localization-zh--CN-brightgreen)](LOCALIZATION-STYLE.md)
[![Claude Code](https://img.shields.io/badge/Claude_Code-2.1+-purple)](https://code.claude.com)

# Claude Code 中文全面上手指南

从会输入 `claude`，到真正会组合使用 slash commands、memory、skills、hooks、MCP、subagents 和 plugins。

这是一个基于上游项目 [`luongnv89/claude-howto`](https://github.com/luongnv89/claude-howto) 的 **非官方中文本土化 fork**。它不是生硬逐句翻译，而是面向中国小白用户重写表达方式、补齐学习路径、保留所有关键可执行标识，并加入翻译后兼容性校验。

**[15 分钟快速开始](#-15-分钟快速开始)** | **[先判断你适合从哪开始](#-不知道从哪里开始)** | **[浏览功能总表](CATALOG.md)** | **[查看来源与同步说明](UPSTREAM.md)**

---

## 最近同步

- **最近同步日期**：2026-05-23
- **本轮参考范围**：`7e369ee` -> `46941a3`
- **本次同步内容**：
  - 同步 Claude Code `v2.1.145` 相关口径：`/usage-credits`、`/model` session-only 默认行为、`claude agents --json`
  - 补充 `/run`、`/verify`、`/run-skill-generator` 三个 bundled skills，以及 Stop / SubagentStop hook 新字段
  - 记录 Bash 裸环境变量 allowlist 自动批准漏洞已修复，避免中文用户继续按旧权限规则配置
  - 审阅上游多语言目录 root-level logo 路径修正；本 fork 不维护额外多语言目录树，因此不引入对应子目录改动

---

## Table of Contents

- [最近同步](#最近同步)
- [这是什么项目](#这是什么项目)
- [本项目做了哪些调整](#本项目做了哪些调整)
- [哪些内容为了兼容性不会翻译](#哪些内容为了兼容性不会翻译)
- [为什么这份指南更适合中国小白](#为什么这份指南更适合中国小白)
- [怎么使用这份指南](#怎么使用这份指南)
- [不知道从哪里开始](#-不知道从哪里开始)
- [15 分钟快速开始](#-15-分钟快速开始)
- [你能用它搭什么](#你能用它搭什么)
- [常见问题](#常见问题)
- [参与贡献](#contributing)
- [许可证](#license)

---

## 这是什么项目

如果你已经装好了 Claude Code，但只会简单对话，很容易卡在这几个地方：

- 官方文档告诉你“有什么功能”，却不会告诉你“这些功能怎么组合起来真正在项目里省时间”。
- 你知道 `CLAUDE.md`、hooks、MCP、skills、subagents 这些词，但不知道先学哪个、后学哪个。
- 你能看懂一些简单例子，但还不会把它们变成自己的 code review、文档生成、自动化流程。

这个仓库的目标，就是把这些碎片能力整理成一条可落地的学习路径，让你知道：

- 先学什么最有效
- 每个功能什么时候用
- 哪些示例可以直接复制
- 哪些看起来像普通文本、其实不能乱翻

---

## 本项目做了哪些调整

和上游英文项目相比，这个中文版做了这些本土化处理：

- 把首页、学习路线、速查卡、功能目录等核心入口文档改成中文主线表达。
- 用中国小白更容易理解的方式重写“是什么 / 什么时候用 / 怎么装 / 怎么跑 / 常见坑”。
- 保留所有会影响运行的关键标识，避免为了翻译把示例翻坏。
- 补充中国用户常见障碍说明，比如 GitHub Token、`npm` / `npx` / `uv` / Python 环境、网络与代理、macOS / Windows / WSL 差异。
- 增加来源声明、同步策略和本地化风格规范，方便后续持续跟进上游版本。
- 增加本地化校验脚本，自动检查 frontmatter、JSON/YAML、shell 脚本、关键命令名和受保护标识是否仍然可用。

详细规则见：

- [UPSTREAM.md](UPSTREAM.md)
- [LOCALIZATION-STYLE.md](LOCALIZATION-STYLE.md)

---

## 哪些内容为了兼容性不会翻译

为了确保示例仍然能直接复制运行，下列内容默认 **保留英文，不做中文化改名**：

- 目录名、文件名
- slash command 名称
- skill / subagent / plugin 名称
- YAML frontmatter key
- JSON / YAML key
- CLI flags、环境变量名、路径占位符、MCP server 名
- 代码块里的可执行命令、配置片段、协议字段

举例来说，`skills`、`CLI`、`hooks`、`MCP`、`subagents` 这些术语在正文里通常会保留英文，并在首次出现时补充中文解释；但不会粗暴改成一个中文词后再让读者回头猜原始命令是什么。

---

## 为什么这份指南更适合中国小白

这个中文版本不是“翻译腔”文档，而是按学习体验重新组织表达：

- 先讲清楚“这是什么”和“什么时候用”，再给你命令和配置。
- 尽量把容易混淆的概念放在一起对比，比如 slash commands、skills、memory、hooks、plugins 的职责边界。
- 对中国开发者常见的安装、访问和权限问题，直接给出前置提醒，不让你跑到一半才踩坑。
- 对高风险示例明确提醒哪些行不能翻、哪些字段不能改。

---

## 怎么使用这份指南

### 1. 先找自己的起点

直接看 [LEARNING-ROADMAP.md](LEARNING-ROADMAP.md)，先做自测，再按 beginner / intermediate / advanced 路线学。

### 2. 再按模块逐步上手

仓库里的 10 个模块按推荐顺序排列：

1. [Slash Commands](01-slash-commands/)
2. [Memory](02-memory/)
3. [Checkpoints](08-checkpoints/)
4. [CLI Basics](10-cli/)
5. [Skills](03-skills/)
6. [Hooks](06-hooks/)
7. [MCP](05-mcp/)
8. [Subagents](04-subagents/)
9. [Advanced Features](09-advanced-features/)
10. [Plugins](07-plugins/)

### 3. 边学边复制模板

这个仓库不是纯阅读材料。很多文件都可以直接复制到你的项目里，例如：

- `01-slash-commands/*.md`
- `02-memory/project-CLAUDE.md`
- `03-skills/*/SKILL.md`
- `04-subagents/*.md`
- `05-mcp/*.json`
- `06-hooks/*.sh`
- `07-plugins/*`
- `local-progress/index.html`

### 4. 每改一处示例都先确认兼容性

如果你继续 fork 并深度本地化，建议每次改完都跑：

```bash
uv run python scripts/validate_localization.py
```

它会帮你检查：

- Markdown 相对链接
- YAML frontmatter
- JSON / YAML 解析
- shell 脚本语法
- 关键可执行标识是否被误改

---

## 🌱 不知道从哪里开始

如果你还不确定自己算什么水平，可以直接用下面这套简版判断：

| 你目前的情况 | 建议起点 | 预计时间 |
|--------------|----------|----------|
| 只会打开 Claude Code 聊天 | [01-slash-commands](01-slash-commands/) | 约 2.5 小时 |
| 已经用过 `CLAUDE.md` 和一些命令 | [03-skills](03-skills/) | 约 3.5 小时 |
| 已经开始碰 hooks、MCP、subagents | [09-advanced-features](09-advanced-features/) | 约 5 小时 |

完整路线见 [LEARNING-ROADMAP.md](LEARNING-ROADMAP.md)。

---

## 🚀 15 分钟快速开始

如果你只是想先跑起来，不想马上看完整教程，可以先做这一套：

```bash
# 1. 准备项目目录
mkdir -p /path/to/your-project/.claude/commands

# 2. 复制第一个 slash command
cp 01-slash-commands/optimize.md /path/to/your-project/.claude/commands/

# 3. 在 Claude Code 里试用
# /optimize

# 4. 加上项目级 memory
cp 02-memory/project-CLAUDE.md /path/to/your-project/CLAUDE.md

# 5. 安装一个 skill
mkdir -p ~/.claude/skills
cp -r 03-skills/code-review ~/.claude/skills/
```

如果你想在 1 小时内完成最小可用配置，可以继续：

```bash
# Slash commands（快捷命令）
cp 01-slash-commands/*.md .claude/commands/

# Project memory（项目记忆）
cp 02-memory/project-CLAUDE.md ./CLAUDE.md

# A reusable skill（可复用 skill）
cp -r 03-skills/code-review ~/.claude/skills/

# 周末目标：继续加 hooks、MCP、subagents、plugins
```

---

## 你能用它搭什么

| 场景 | 你会组合哪些能力 |
|------|------------------|
| 自动化代码审查 | Slash Commands + Subagents + Memory + MCP |
| 团队 onboarding | Memory + Slash Commands + Plugins |
| 文档自动生成 | Skills + Subagents + Plugins |
| CI/CD 自动化 | CLI + Hooks + Background Tasks |
| 安全审计 | Skills + Hooks + Subagents |
| DevOps 流程 | Plugins + MCP + Hooks |
| 大型重构 | Checkpoints + Planning Mode + Hooks |

---

## 常见问题

**这是官方项目吗？**  
不是。这是基于上游社区项目做的中文本土化 fork，来源与同步策略见 [UPSTREAM.md](UPSTREAM.md)。

**我能直接复制里面的命令和配置吗？**  
大多数可以，但前提是你不要改坏关键标识。像 frontmatter key、JSON key、CLI flags、环境变量名这些不能为了中文化而改掉。

**为什么有些术语不翻译？**  
因为很多术语一旦翻译，会让你在真实使用 Claude Code、搜索官方文档、复制命令时更容易混淆。这个项目遵循“术语保真，解释中文化”的原则。

**中国用户最容易卡在哪？**  
常见是：GitHub 访问、Token 权限、`npm` / `npx` / `uv` / Python 环境、Windows 和 WSL 差异、以及把示例里可执行字段误翻译。

**能离线看吗？**  
可以。运行：

```bash
uv run scripts/build_epub.py
```

会生成 EPUB 电子书。脚本说明见 [scripts/README.md](scripts/README.md)。

**之后怎么跟上游同步？**  
请先看 [UPSTREAM.md](UPSTREAM.md)。本仓库默认按“持续同步上游、中文侧增量跟进”的方式维护。

---

<details>
<summary>快速导航：所有核心能力</summary>

| 能力 | 说明 | 入口 |
|------|------|------|
| 功能总表 | 一眼看全所有功能、安装方式、适用场景 | [CATALOG.md](CATALOG.md) |
| 学习路线 | 从新手到进阶的推荐学习顺序 | [LEARNING-ROADMAP.md](LEARNING-ROADMAP.md) |
| Quick Reference | 安装命令、路径、常用场景速查 | [QUICK_REFERENCE.md](QUICK_REFERENCE.md) |
| Slash Commands | 用户主动触发的快捷操作 | [01-slash-commands/](01-slash-commands/) |
| Memory | 持久上下文与规则 | [02-memory/](02-memory/) |
| Skills | 自动触发的复用能力 | [03-skills/](03-skills/) |
| Subagents | 分工明确的 AI 助手 | [04-subagents/](04-subagents/) |
| MCP | 外部工具与实时数据接入 | [05-mcp/](05-mcp/) |
| Hooks | 事件驱动自动化 | [06-hooks/](06-hooks/) |
| Plugins | 多能力打包分发 | [07-plugins/](07-plugins/) |
| Checkpoints | 安全试错与回退 | [08-checkpoints/](08-checkpoints/) |
| Advanced Features | plan、auto mode、background tasks 等高级能力 | [09-advanced-features/](09-advanced-features/) |
| CLI | `claude` / `claude -p` / session / automation 参考 | [10-cli/](10-cli/) |

</details>

<details>
<summary>核心能力对照</summary>

| 能力 | 触发方式 | 持久性 | 最适合什么 |
|------|----------|--------|------------|
| Slash Commands | 手动输入 `/cmd` | 当前会话 | 高频快捷操作 |
| Memory | 自动加载 | 跨会话 | 长期规则与偏好 |
| Skills | 自动触发 | 文件系统级 | 可复用工作流 |
| Subagents | 自动委派或显式调用 | 独立上下文 | 任务拆分 |
| MCP | 自动查询 | 实时 | 外部系统接入 |
| Hooks | 事件触发 | 配置级 | 自动检查和拦截 |
| Plugins | 一次安装 | 组合能力 | 团队级打包方案 |
| Checkpoints | 内建 | 会话级 | 安全试错 |
| Planning Mode | 手动或自动进入 | 计划阶段 | 复杂实现 |
| CLI | 终端命令 | 脚本 / 会话 | 自动化与 CI/CD |

</details>

---

## Contributing

欢迎继续把这个中文 fork 做得更适合中文用户，但请遵循两个底线：

- 先看 [LOCALIZATION-STYLE.md](LOCALIZATION-STYLE.md)，不要把可执行标识翻坏。
- 先看 [UPSTREAM.md](UPSTREAM.md)，不要在没有记录映射关系的情况下随意偏离上游结构。

如果你要贡献翻译或重写内容，建议至少本地跑一次：

```bash
uv run python scripts/validate_localization.py
```

---

## License

本仓库沿用上游项目的 [MIT License](LICENSE)。

来源项目、上游 commit、同步策略和本地化边界见 [UPSTREAM.md](UPSTREAM.md)。

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="resources/logos/claude-howto-logo-dark.svg">
  <img alt="Claude How To" src="resources/logos/claude-howto-logo.svg">
</picture>

[![Source Project](https://img.shields.io/badge/source-luongnv89%2Fclaude--howto-24292f)](https://github.com/luongnv89/claude-howto)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Localization](https://img.shields.io/badge/localization-zh--CN-brightgreen)](docs/contributing/LOCALIZATION-STYLE.md)
[![Claude Code](https://img.shields.io/badge/Claude_Code-2.1+-purple)](https://code.claude.com)

# Claude Code 中文全面上手指南

从会输入 `claude`，到真正会组合使用 slash commands、memory、skills、hooks、MCP、subagents 和 plugins。

这是一个基于上游项目 [`luongnv89/claude-howto`](https://github.com/luongnv89/claude-howto) 的 **非官方中文本土化 fork**。它不是生硬逐句翻译，而是面向中国小白用户重写表达方式、补齐学习路径、保留所有关键可执行标识，并加入翻译后兼容性校验。

**[15 分钟快速开始](#-15-分钟快速开始)** | **[先判断你适合从哪开始](#-不知道从哪里开始)** | **[浏览功能总表](CATALOG.md)** | **[查看来源与同步说明](docs/project/UPSTREAM.md)**

---

> **最近同步**：2026-05-23（`7e369ee` → `46941a3`）。完整记录见 [CHANGELOG.md](docs/project/CHANGELOG.md)。

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

## 关于这个中文版

和上游英文项目相比，这个中文版做了以下本土化处理：

- 把学习路径、速查卡、功能目录等核心入口改成中文主线表达
- 保留所有影响运行的关键标识（命令名、frontmatter key、JSON key、CLI flags 等），确保复制就能跑
- 补充中国用户常见障碍说明（GitHub Token、网络代理、Windows/WSL 差异等）
- 增加本地化校验脚本，防止翻译把示例改坏

详细规则见 [docs/project/UPSTREAM.md](docs/project/UPSTREAM.md) 和 [docs/contributing/LOCALIZATION-STYLE.md](docs/contributing/LOCALIZATION-STYLE.md)。

---

## 怎么使用

1. **找起点**：看 [LEARNING-ROADMAP.md](LEARNING-ROADMAP.md) 做自测，按路线学
2. **按模块上手**：10 个模块按推荐顺序排列——[01](01-slash-commands/) → [02](02-memory/) → [08](08-checkpoints/) → [10](10-cli/) → [03](03-skills/) → [06](06-hooks/) → [05](05-mcp/) → [04](04-subagents/) → [09](09-advanced-features/) → [07](07-plugins/)
3. **边学边复制**：很多文件可直接复制到你的项目里（slash commands、CLAUDE.md、skills、subagents、hooks 等）
4. **改完跑校验**：
   ```bash
   uv run python scripts/validate_localization.py
   ```

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
不是。这是基于上游社区项目做的中文本土化 fork，来源与同步策略见 [docs/project/UPSTREAM.md](docs/project/UPSTREAM.md)。

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
请先看 [docs/project/UPSTREAM.md](docs/project/UPSTREAM.md)。本仓库默认按“持续同步上游、中文侧增量跟进”的方式维护。

---

## 核心能力速览

| 能力 | 触发方式 | 最适合什么 | 入口 |
|------|----------|------------|------|
| Slash Commands | 手动输入 `/cmd` | 高频快捷操作 | [01](01-slash-commands/) |
| Memory | 自动加载 | 长期规则与偏好 | [02](02-memory/) |
| Skills | 自动触发 | 可复用工作流 | [03](03-skills/) |
| Subagents | 自动委派 | 任务拆分 | [04](04-subagents/) |
| MCP | 自动查询 | 外部系统接入 | [05](05-mcp/) |
| Hooks | 事件触发 | 自动检查和拦截 | [06](06-hooks/) |
| Plugins | 一次安装 | 团队级打包方案 | [07](07-plugins/) |
| Checkpoints | 内建 | 安全试错 | [08](08-checkpoints/) |
| Advanced Features | 手动/自动 | 复杂实现 | [09](09-advanced-features/) |
| CLI | 终端命令 | 自动化与 CI/CD | [10](10-cli/) |

完整功能目录见 [CATALOG.md](CATALOG.md)。

---

## Contributing

欢迎继续把这个中文 fork 做得更适合中文用户，但请遵循两个底线：

- 先看 [docs/contributing/LOCALIZATION-STYLE.md](docs/contributing/LOCALIZATION-STYLE.md)，不要把可执行标识翻坏。
- 先看 [docs/project/UPSTREAM.md](docs/project/UPSTREAM.md)，不要在没有记录映射关系的情况下随意偏离上游结构。

如果你要贡献翻译或重写内容，建议至少本地跑一次：

```bash
uv run python scripts/validate_localization.py
```

---

## License

本仓库沿用上游项目的 [MIT License](LICENSE)。

来源项目、上游 commit、同步策略和本地化边界见 [docs/project/UPSTREAM.md](docs/project/UPSTREAM.md)。

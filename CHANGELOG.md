# 更新日志

> 本文件保留上游版本信息的时间顺序，但用中文补充阅读说明，方便中文用户快速判断“这个仓库最近同步了什么”。

## 中文版同步 — 2026-05-23

### 上游审阅

- 核对上游范围：`7e369ee` → `46941a3`
- 上游这轮重点：
  - 修正多语言 root-level README 的 logo 相对路径
  - 同步 Claude Code `v2.1.145`
  - `/extra-usage` 主名称改为 `/usage-credits`，旧命令仍作为 alias 保留
  - `/model` 默认只影响当前 session，选择模型后按 `d` 才写入后续 session 默认值
  - 新增 bundled skills：`/run`、`/verify`、`/run-skill-generator`
  - Stop / SubagentStop hook 输入新增 `background_tasks` 和 `session_crons`
  - `claude agents` 新增 `--json`
  - 修复 Bash 裸环境变量 allowlist 自动批准漏洞

### 中文 fork 处理

- 将会影响实际使用、安全边界和自动化脚本的变化改写成中文说明
- 保留所有 slash command、CLI flag、JSON key、环境变量和权限规则标识原文
- 补充根级 `pyproject.toml` 的 `jinja2` 依赖，确保固定的自动化测试命令无需额外 `--with jinja2` 也能覆盖网站构建测试
- 不引入上游 `uk/`、`vi/`、`zh/` 等额外多语言目录改动，继续保持根目录中文主线结构
- 更新 `README.md` 和 `UPSTREAM.md` 的最近同步记录

## 中文版同步 — 2026-05-20（补充）

### 上游审阅

- 核对上游范围：`30d5ad5` → `7e369ee`
- 上游这轮重点：
  - 修正 `ja/`、`uk/`、`vi/`、`zh/` 多语言模块 README 的 logo 相对路径

### 中文 fork 处理

- 本中文 fork 的根目录中文主线与模块 README 路径原本正确，因此无需正文改动
- 不引入上游其他语言子目录改动，继续保持当前中文主线结构
- 更新 `README.md` 和 `UPSTREAM.md` 的最近同步记录

## 中文版同步 — 2026-05-20

### 上游审阅

- 核对上游范围：`3557d79` → `30d5ad5`
- 上游这轮重点：
  - 同步 Claude Code `v2.1.143`
  - 新增 `/goal`、`/scroll-speed`、Agent View、`claude plugin details`
  - hooks 增加 `args`、`continueOnBlock`、`terminalSequence`、Stop hook safety cap
  - MCP stdio server 自动带 `CLAUDE_PROJECT_DIR`
  - Fast Mode 默认切到 Opus 4.7，API key 会静默禁用 Remote Control / `/schedule` / claude.ai connectors

### 中文 fork 处理

- 将会影响自动化、安全边界和命令行为的变化改写成适合中文用户理解的说明
- 保留所有 CLI flags、JSON key、环境变量和命令名原样
- 更新 hooks 事件数和版本脚注，避免中文仓库继续引用旧口径
- 保持根目录中文默认入口，不引入上游英文 README 或其他语言目录改动
- 更新 `README.md` 和 `UPSTREAM.md` 的最近同步记录

## 中文版同步 — 2026-05-16

### 上游审阅

- 核对上游范围：`553a319` → `3557d79`
- 上游这轮重点：
  - 新增 `scripts/build_website.py`
  - 新增 `scripts/vendor_assets.py`
  - 新增 `scripts/website_templates/` 页面模板与样式
  - 新增 `scripts/tests/test_build_website.py`
  - 新增 `.github/workflows/pages.yml`

### 中文 fork 处理

- 将静态网站生成器、依赖、模板、测试和 GitHub Pages workflow 同步进中文仓库
- 用中文补充 `scripts/README.md` 的网站构建、预览和 Pages 部署说明
- 实际跑通网站构建测试、Markdown 渲染校验、本地化校验、交叉引用检查和整套脚本测试
- 保持根目录中文默认入口，不引入上游其他语言目录改动
- 更新 `README.md` 和 `UPSTREAM.md` 的最近同步记录

## 中文版同步 — 2026-05-12

### 上游审阅

- 核对上游范围：`b3571e8` → `553a319`
- 上游这轮重点：
  - 新增 `scripts/check_markdown_rendering.py`
  - 新增 `scripts/tests/test_check_markdown_rendering.py`
  - `.pre-commit-config.yaml` 增加 `markdown-rendering` 钩子
  - 修正文档里 `` !`command` `` 相关 Markdown 渲染转义

### 中文 fork 处理

- 将新的 Markdown 渲染校验脚本、测试和 pre-commit 配置同步进中文仓库
- 实际运行渲染校验器，确认当前中文 README 集合通过检查
- 保持根目录中文默认入口，不引入上游其他语言目录改动
- 更新 `README.md` 和 `UPSTREAM.md` 的最近同步记录

## 中文版同步 — 2026-05-10

### 上游审阅

- 核对上游范围：`d4b5cf5` → `b3571e8`
- 上游这轮重点：
  - 同步 Claude Code `v2.1.138`
  - hooks 事件数更新到 29，并新增 `Setup` 事件、`effort.level`
  - 新增 `worktree.baseRef`、`autoMode.hard_deny`、plan mode 无条件阻止写入
  - MCP 修复 `/clear` 后 server 丢失与 OAuth refresh token 并发刷新
  - plugin 支持空格调用，subagent 共享主 skill catalog，CLI 增补新的环境变量与 resume 权限模式修复

### 中文 fork 处理

- 将会影响自动化、安全边界和命令行为的变化改写成适合中文用户理解的说明
- 保留所有 CLI flags、JSON key、环境变量和命令名原样
- 同步 hooks 事件数、目录计数和版本脚注，避免中文仓库继续引用旧统计
- 保持根目录中文默认入口，不引入上游英文 README 或其他语言目录改动
- 更新 `README.md` 和 `UPSTREAM.md` 的最近同步记录

## 中文版同步 — 2026-05-07

### 上游审阅

- 核对上游范围：`9701bb7` → `d4b5cf5`
- 上游这轮重点：
  - 同步 Claude Code `v2.1.131`
  - 新增 `skillOverrides`、plugin `.zip` / `--plugin-url`、`disableRemoteControl`
  - `/mcp` 增加工具数量显示和 `0 tools` 提示
  - gateway model discovery 改成显式 opt-in，需要 `CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY=1`
  - `/context` 不再把 ASCII 可视化写进对话上下文，`Ctrl+R` 默认搜索所有项目 prompts，`--channels` 支持 API key

### 中文 fork 处理

- 将新增命令、设置项和行为变化改写成适合中文用户理解的说明
- 保留所有 CLI flags、JSON key、环境变量和命令名原样
- 修正上次关于 gateway model discovery 的口径，避免误导用户只设置 `ANTHROPIC_BASE_URL` 就能自动发现模型
- 保持根目录中文默认入口，不引入上游英文 README 或其他语言目录改动
- 更新 `README.md` 和 `UPSTREAM.md` 的最近同步记录

## 中文版同步 — 2026-05-03

### 上游审阅

- 核对上游范围：`f393805` → `9701bb7`
- 上游这轮重点：
  - 同步 Claude Code `v2.1.126`
  - 新增 `claude project purge`、`claude plugin prune`、headless `claude ultrareview`
  - 补充 MCP `alwaysLoad`、hooks `updatedToolOutput` 全工具适用范围、`${CLAUDE_EFFORT}` 等说明
  - 修正 memory 题库中已停用的 `# your rule` 写法
  - 修正 extended thinking 相关示例与题目，避免误写 `/think`

### 中文 fork 处理

- 将新增命令和配置说明改写为中文用户可理解、可复制的版本
- 保留所有 CLI flags、JSON key、环境变量和命令名原样
- 更新 lesson quiz 的出题规则：每轮即时反馈，并要求打乱选项顺序
- 不引入上游其他语言目录变化，继续保持根目录中文默认入口
- 更新 `README.md` 和 `UPSTREAM.md` 的最近同步记录

## 中文版同步 — 2026-05-01

### 上游审阅

- 核对上游范围：`3221229` → `f393805`
- 上游这轮重点：
  - 新增完整 `ja/` 日文翻译目录
  - 英文 README 去掉硬编码 star / fork 数字
  - 日文目录配套补充 pre-commit 和 EPUB 构建支持

### 中文 fork 处理

- 不引入 `ja/` 目录，继续保持根目录中文主线
- 中文首页没有使用上游硬编码 star / fork 指标，因此无需正文改动
- 不同步日文专项构建配置，避免为未维护目录增加无效检查
- 更新 `README.md` 和 `UPSTREAM.md` 的最近同步记录

## 中文版同步 — 2026-04-28

### 上游审阅

- 核对上游范围：`a7a0ea2` → `3221229`
- 上游这轮重点：
  - 新增 `SessionEnd` 学习进度记录 hook
  - 新增本地浏览器进度面板 `local-progress/index.html`
  - 修正 agent 优先级为 CLI → Project → User
  - 修正 lesson quiz 里几个过时题目
  - 配置示例继续更新到 Opus 4.7 / Sonnet 4.6

### 中文 fork 处理

- 新增中文化的 `06-hooks/session-end.sh`
- 新增中文化的 `local-progress/index.html`
- 更新 hooks、subagents、CLI、advanced features 和 lesson quiz 相关说明
- 继续保留中文根目录主线，不采用上游英文 README 或多语言目录结构
- 保留本仓库自有 `RELEASE_NOTES.md`，不跟随上游删除该文件

## 中文版同步 — 2026-04-22

### 上游审阅

- 核对上游范围：`9c224ff` → `cf92e8e`
- 上游这轮重点：
  - 同步 Claude Code `v2.1.110` / `v2.1.112`
  - 新增 `/tui`、`/focus`、`/recap`、`/undo`、`/proactive`、`/ultrareview`、`/less-permission-prompts`
  - `09-advanced-features` 补充 TUI、session recap、push notifications、Auto Mode 新访问方式
  - CLI / docs 切到 Opus 4.7，并引入 `xhigh` effort
  - plugins 文档新增 background monitors 说明

### 中文 fork 处理

- 把这轮新增能力同步到中文根目录主线文档
- 更新 `README.md` 和 `UPSTREAM.md` 的最近同步记录
- 保留中文默认入口，不采用上游英文 README 和多语言目录结构
- 增强本地化校验，拦截明显未翻译的英文标题和英文模板段落

## 中文版同步 — 2026-04-08

### 上游审阅

- 核对上游范围：`0ca8c37` → `561c6cb`
- 上游这轮重点：
  - 发布 `v2.3.0`
  - 新增 `CLAUDE.md`
  - 新增 `performance-optimizer` subagent
  - 新增 `pre-tool-check.sh` 与 `dependency-check.sh`
  - hooks shell 示例统一到 stdin JSON 协议，并补 Windows Git Bash 兼容性
  - 文档更新覆盖 `/ultraplan`、`MCP Apps`、Agent Teams、Channels、`cleanupPeriodDays` 等主题
  - 上游新增 `zh/` / `vi/` 多语言目录

### 中文 fork 处理

- 新增根目录 [CLAUDE.md](CLAUDE.md)，写明本仓库的协作与校验约定
- 新增 `04-subagents/performance-optimizer.md`
- 新增 `06-hooks/pre-tool-check.sh` 与 `06-hooks/dependency-check.sh`
- 将 `format-code.sh`、`log-bash.sh`、`security-scan.sh`、`validate-prompt.sh` 同步到新版协议写法
- 更新 `README.md` 的最近同步说明，以及 `01`、`02`、`03`、`04`、`05`、`06`、`08`、`09`、`10` 模块的中文说明
- 未采用上游的多语言目录拆分与 README 星标 / fork 指标，继续保留当前中文主线仓库结构
## 中文版同步 — 2026-04-01

### 上游同步

- 同步上游范围：`d41b335` → `0ca8c37`
- 核心变化：
  - hooks 不再推荐旧的 `auto-adapt-mode` 动态学习方案
  - 新增一次性权限种子脚本 `09-advanced-features/setup-auto-mode-permissions.py`
  - auto-mode 权限基线改为更保守的默认集合，并支持按需开启 edits、tests、git writes、packages、GitHub writes
  - 上游 `README` 新增 Trending 徽章

### 中文 fork 处理

- 删除本仓库中的旧 `06-hooks/auto-adapt-mode.py`
- 在 `06-hooks/README.md` 和 `09-advanced-features/README.md` 中补上新的中文说明
- 在 `README.md` 中加入最近同步日期与更新内容说明
- 未直接照搬上游 Trending 徽章，以避免误导为当前中文 fork 的真实热度状态

## v2.2.0 — 2026-03-26

### 文档

- 将全部教程和参考文档同步到 Claude Code `v2.1.84`
  - slash commands 更新为 55+ 个内建命令 + 5 个 bundled skills，并标记 3 个已废弃项
  - hooks 事件从 18 个扩展到 25 个，并新增 `agent` hook type
  - advanced features 新增 Auto Mode、Channels、Voice Dictation
  - `SKILL.md` frontmatter 新增 `effort`、`shell`
  - subagent 字段新增 `initialPrompt`、`disallowedTools`
  - MCP 新增 WebSocket transport、elicitation、2KB tool cap 等说明
  - plugins 新增 LSP、`userConfig`、`${CLAUDE_PLUGIN_DATA}` 相关支持
  - 更新 `CATALOG`、`QUICK_REFERENCE`、`LEARNING-ROADMAP`、`INDEX`
- README 改写为更像 landing page 的结构

### 问题修复

- 为 CI 补充缺失的 cSpell 词条和 README 章节
- 在 cSpell 词典中加入 `Sandboxing`

**Full Changelog**: https://github.com/luongnv89/claude-howto/compare/v2.1.1...v2.2.0

---

## v2.1.1 — 2026-03-13

### 问题修复

- 删除导致链接检查失败的无效 marketplace 链接
- 在 cSpell 词典中补充 `sandboxed` 和 `pycache`

**Full Changelog**: https://github.com/luongnv89/claude-howto/compare/v2.1.0...v2.1.1

---

## v2.1.0 — 2026-03-13

### 功能

- 新增自适应学习路径、自测和课后测验相关 skills
  - `/self-assessment`：对 10 个能力域做交互式自测并给出个性化学习路径
  - `/lesson-quiz [lesson]`：针对单个模块做 8-10 题知识检查

### 问题修复

- 更新失效 URL、已废弃写法和过时引用
- 修复资源文档和自测 skill 里的坏链
- 将概念指南中的嵌套代码块改为波浪线 fence
- 增补 cSpell 词典缺失词条

### 文档

- 修正文档里的术语、URL 和一致性问题
- 完成缺失能力覆盖与参考文档补齐
- 在 MCP 章节加入 MCPorter 运行时说明
- 补充缺失命令、设置项和特性说明
- 新增风格指南
- 将自测和 lesson-quiz 引入 README 与路线图

### 新贡献者

- `@VikalpP` 首次贡献

**Full Changelog**: https://github.com/luongnv89/claude-howto/compare/v2.0.0...v2.1.0

---

## v2.0.0 — 2026-02-01

### 功能

- 将文档整体同步到 2026 年 2 月的 Claude Code 能力集
  - 新增 Auto Memory
  - 新增 Remote Control、Web Sessions、Desktop App
  - 新增 Agent Teams（实验性）
  - 新增 MCP OAuth 2.0、Tool Search、Claude.ai Connectors
  - 新增 subagents 的 persistent memory 与 worktree isolation
  - 新增 background subagents、task list、prompt suggestions
  - 新增 sandboxing 与 managed settings
  - 新增 HTTP hooks 和 7 个新事件
  - 新增 plugin settings、LSP、marketplace 相关说明
  - 补充 checkpoints 的 summarize from checkpoint
  - 补充 17 个新 slash commands
  - 补充一批新 CLI flags 和环境变量

### 设计

- 重做 logo，改为更简洁的视觉设计

### 问题修复 / 纠正

- 更新模型名：Sonnet 4.5 → Sonnet 4.6，Opus 4.5 → Opus 4.6
- 修正 permission mode 名称
- 修正 hooks 事件名
- 修正 CLI 写法：`claude-code --headless` → `claude -p`
- 修正 checkpoint 命令示例
- 修正 session 管理命令
- 修正 plugin manifest：`plugin.yaml` → `.claude-plugin/plugin.json`
- 修正 MCP 配置路径
- 修正文档 URL，并删除虚构地址
- 移除多个虚构配置字段

**Full Changelog**: https://github.com/luongnv89/claude-howto/compare/20779db...v2.0.0

# 上游与 Fork 说明

## 上游来源

- 上游仓库：[`luongnv89/claude-howto`](https://github.com/luongnv89/claude-howto)
- 上游分支：`main`
- 本地化基线 commit：`0ca8c37c81918458e063739425c4740ca92c2db2`
- 最近检查到的上游 commit：`46941a38fc9a6beeca02b755a29110465de87059`
- 上游许可证：[MIT License](LICENSE)

## 本仓库性质

本仓库是一个 **非官方中文本土化 fork**，目标是面向中国小白用户重写 Claude Code 学习材料，同时尽量保持与上游结构、示例和运行行为兼容。

它不是：

- 官方 Anthropic 文档
- 上游仓库的逐字逐句翻译镜像
- 为中国平台完全重构后的独立产品

## 本仓库做了哪些调整

- 把首页、学习路线、Quick Reference、Catalog 等核心入口文档改成中文主线。
- 用“先讲用途，再讲安装，再讲示例和常见坑”的方式重写表达。
- 保留目录结构、文件路径、命令名、frontmatter key、JSON/YAML key、环境变量、CLI flags 等关键兼容元素。
- 增加中国用户常见障碍说明，例如 GitHub Token、`npm` / `npx` / `uv` / Python 环境、网络与代理、Windows / WSL 差异。
- 增加本地化校验脚本与 CI 护栏，避免翻译把示例和配置改坏。

## 本地化原则

1. **兼容性优先**  
   任何会影响 Claude Code 运行、加载或复制执行的标识，默认不翻。

2. **中文表达优先**  
   给人看的说明文字、学习路径、FAQ、对比表、导语等内容，以中文重写为主。

3. **术语保真**  
   `skills`、`CLI`、`hooks`、`MCP`、`subagents` 这类高频术语保留英文，首次出现补中文解释。

4. **持续同步**  
   本仓库默认采用“跟进上游版本 -> 判定受影响文件 -> 更新中文内容 -> 记录处理结果”的维护方式。

## 推荐同步流程

1. 获取上游新版本或新 commit。
2. 列出上游变更的文件范围。
3. 判断哪些文件影响本仓库的中文文档、示例或校验脚本。
4. 优先同步以下类型的变化：
   - 命令名、字段名、协议名、路径约定
   - 新增或废弃功能
   - 影响复制可运行性的示例变更
5. 更新中文文档后，运行：

```bash
uv run python scripts/validate_localization.py
```

6. 在提交说明或更新日志中记录：
   - 上游变更点
   - 本仓库采取了什么处理
   - 哪些内容暂时未同步

## 最近一次同步记录

### 上游同步 — 2026-05-23

- Reviewed upstream range: `7e369ee` → `46941a3`
- 重点上游变化：
  - 上游先修正 `uk/`、`vi/`、`zh/` 等多语言 root-level README 的 logo 相对路径
  - Claude Code 教程覆盖更新到 `v2.1.145`
  - `/extra-usage` 主名称改为 `/usage-credits`，旧名继续作为 alias 可用
  - `/model` 选择默认只影响当前 session；选择后按 `d` 才会设置成后续 session 默认模型
  - 新增 bundled skills：`/run`、`/verify`、`/run-skill-generator`
  - Stop / SubagentStop hook 输入新增 `background_tasks` 和 `session_crons`
  - `claude agents` 增加 `--json`，方便脚本、状态栏和 session picker 读取
  - 修复 Bash 裸环境变量 allowlist 自动批准问题，`FOO=bar somecommand` 这类命令现在需要覆盖完整命令的 `Bash(...)` 权限规则
- Chinese fork actions:
  - 将影响真实使用、安全边界和自动化脚本的变化同步进中文主线文档
  - 保留 `/usage-credits`、`/run`、`/verify`、`background_tasks`、`session_crons`、`Bash(...)` 等可执行标识原文
  - 补充根级 `pyproject.toml` 的 `jinja2` 依赖，确保固定自动化测试命令能覆盖网站构建测试
  - 不引入上游 `uk/`、`vi/`、`zh/` 等额外多语言目录改动，继续维护根目录中文默认入口
  - 更新 `README.md`、`UPSTREAM.md` 和 `CHANGELOG.md` 的最近同步记录

### 上游同步 — 2026-05-20（补充）

- Reviewed upstream range: `30d5ad5` → `7e369ee`
- 重点上游变化：
  - 修正 `ja/`、`uk/`、`vi/`、`zh/` 多语言模块 README 的 logo 相对路径
  - 变更集中在多语言子目录，不涉及英文根主线文档内容
- Chinese fork actions:
  - 审阅后确认本中文 fork 采用根目录中文主线，现有根目录与模块 README 路径本身正确
  - 不引入上游其他语言子目录改动，避免在本 fork 中维护额外多语言树
  - 仅更新 `README.md`、`UPSTREAM.md` 和 `CHANGELOG.md` 的同步记录

### 上游同步 — 2026-05-20

- Reviewed upstream range: `3557d79` → `30d5ad5`
- 重点上游变化：
  - Claude Code 教程覆盖更新到 `v2.1.143`
  - 新增 `/goal`、`/scroll-speed`、`claude agents` Agent View、`claude plugin details`
  - hooks 增加 `args` exec 形式、`continueOnBlock`、`terminalSequence`、Stop hook block safety cap
  - plugins、Remote Control、`/schedule`、Windows PowerShell tool、Fast Mode 默认模型出现多项行为更新
  - MCP stdio server 现在自动带 `CLAUDE_PROJECT_DIR`
- Chinese fork actions:
  - 将会影响真实使用和自动化行为的变化同步到中文主线文档
  - 保留 `/goal`、`claude agents`、`continueOnBlock`、`CLAUDE_PROJECT_DIR`、`CLAUDE_CODE_OPUS_4_6_FAST_MODE_OVERRIDE` 等可执行标识原文
  - 不引入上游英文根 README 或其他语言目录改动，继续维护 `lhfer/claude-howto-zh-cn` 的中文默认入口
  - 更新 `README.md`、`UPSTREAM.md` 和 `CHANGELOG.md` 的最近同步记录

### 上游同步 — 2026-05-16

- Reviewed upstream range: `553a319` → `3557d79`
- 重点上游变化：
  - 新增 `scripts/build_website.py`，可从 Markdown 生成静态网站
  - 新增 `scripts/vendor_assets.py` 与 `scripts/website_templates/`，用于自托管 Tailwind、Mermaid、字体和页面模板
  - 新增 `scripts/tests/test_build_website.py`
  - 新增 `.github/workflows/pages.yml`，支持 GitHub Pages 自动构建与发布
  - `scripts/requirements.txt` / `scripts/pyproject.toml` 增加 `jinja2` 依赖，`.gitignore` 增加 `site/` 与 `scripts/.vendor-cache/`
- Chinese fork actions:
  - 将静态网站生成器、依赖、模板、测试和 Pages workflow 同步到中文仓库
  - 用中文补充 `scripts/README.md` 的网站构建与部署说明，保留 CLI、路径和模板文件名等可执行标识原文
  - 实际运行新加的网站构建测试，并在整套脚本测试中确认通过
  - 更新 `README.md`、`UPSTREAM.md` 和 `CHANGELOG.md` 的最近同步记录

### 上游同步 — 2026-05-12

- Reviewed upstream range: `b3571e8` → `553a319`
- 重点上游变化：
  - 新增 `scripts/check_markdown_rendering.py`，用于校验 Markdown 渲染正确性
  - 新增 `scripts/tests/test_check_markdown_rendering.py`
  - `.pre-commit-config.yaml` 增加 `markdown-rendering` 钩子
  - 文档侧修正 `` !`command` `` 相关渲染转义，避免 inline code 被错误解析
- Chinese fork actions:
  - 将 Markdown 渲染校验脚本、测试和 pre-commit 钩子同步到中文仓库
  - 保持中文文档主线不变，不引入上游 `ja/`、`vi/`、`zh/` 目录里的非根主线改动
  - 通过实际运行新校验器，确认当前中文 README 集合渲染检查通过
  - 更新 `README.md`、`UPSTREAM.md` 和 `CHANGELOG.md` 的最近同步记录

### 上游同步 — 2026-05-10

- Reviewed upstream range: `d4b5cf5` → `b3571e8`
- 重点上游变化：
  - Claude Code 教程覆盖更新到 `v2.1.138`
  - hooks 文档更新为 29 个事件，新增 `Setup` 事件，并把 `effort.level` / `CLAUDE_EFFORT` / `CLAUDE_CODE_SESSION_ID` 暴露给 hooks / Bash 子进程
  - advanced features 增补 `worktree.baseRef`、`autoMode.hard_deny`、plan mode 无条件阻止写入、`sandbox.bwrapPath` / `sandbox.socatPath`
  - MCP 修复 `/clear` 后 server 丢失与 OAuth refresh token 并发刷新问题
  - plugin command 现在支持 `/myplugin review` 这种空格写法，`plugin.json` 里的 `skills` 条目与默认 `skills/` 目录会合并发现
- Chinese fork actions:
  - 将会影响命令执行、权限理解或自动化行为的变化同步到中文主线文档
  - 保留 `Setup`、`worktree.baseRef`、`autoMode.hard_deny`、`CLAUDE_CODE_SESSION_ID`、`CLAUDE_CODE_DISABLE_ALTERNATE_SCREEN` 等可执行标识原文
  - 不引入上游英文根 README 或其他语言目录改动，继续维护 `lhfer/claude-howto-zh-cn` 的中文默认入口
  - 更新 `README.md`、`UPSTREAM.md` 和 `CHANGELOG.md` 的最近同步记录

### 上游同步 — 2026-05-07

- Reviewed upstream range: `9701bb7` → `d4b5cf5`
- 重点上游变化：
  - Claude Code 教程覆盖更新到 `v2.1.131`
  - 新增 `skillOverrides` 的更细粒度取值、`--plugin-url`、plugin `.zip` 加载、`disableRemoteControl`
  - `/mcp` 会显示每个 server 的工具数并标记 `0 tools`
  - gateway `/v1/models` 发现从默认开启改为显式 opt-in，需要 `CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY=1`
  - `/context` 不再把 ASCII 可视化写进对话上下文，`Ctrl+R` 默认搜索范围扩大到所有项目，`--channels` 支持 API key 认证
- Chinese fork actions:
  - 将会影响复制执行或配置理解的变更同步到中文主线文档
  - 保留 `skillOverrides`、`/mcp`、`--plugin-url`、`disableRemoteControl`、`CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY` 等可执行标识原文
  - 不引入上游英文根 README 或其他语言目录改动，继续维护 `lhfer/claude-howto-zh-cn` 的中文默认入口
  - 更新 `README.md`、`UPSTREAM.md` 和 `CHANGELOG.md` 的最近同步记录

### 上游同步 — 2026-05-03

- Reviewed upstream range: `f393805` → `9701bb7`
- 重点上游变化：
  - Claude Code 教程覆盖更新到 `v2.1.126`
  - 新增或补充 `claude project purge`、`claude plugin prune`、headless `claude ultrareview`、MCP `alwaysLoad`、hooks `updatedToolOutput`
  - 修正 memory 题库中已停用的 `# your rule` 快捷写法
  - 修正 extended thinking 题库和示例，避免把 `/think` 当成有效命令，并明确 `ultrathink` 与 `/effort` 的区别
  - 上游 `uk/`、`vi/` 本地化目录同步了 advanced features 说明
- Chinese fork actions:
  - 将会影响中文用户复制使用的命令、配置和题库说明同步到根目录中文主线
  - 保留 `project purge`、`plugin prune`、`alwaysLoad`、`updatedToolOutput`、`ultrathink`、`/effort` 等可执行标识原文
  - 不引入上游其他语言目录改动，继续维护 `lhfer/claude-howto-zh-cn` 的中文默认入口
  - 更新 `README.md`、`UPSTREAM.md` 和 `CHANGELOG.md` 的最近同步记录

### 上游同步 — 2026-05-01

- Reviewed upstream range: `3221229` → `f393805`
- 重点上游变化：
  - 新增完整 `ja/` 日文翻译目录
  - 英文 README 去掉硬编码 star / fork 数字，改成更稳妥的动态信任表述
  - 上游为日文目录补充对应 pre-commit / EPUB 构建支持
- Chinese fork actions:
  - 不引入 `ja/` 多语言目录，继续保持根目录中文主线
  - 中文 README 原本未使用上游硬编码 star / fork 指标，因此只更新同步记录
  - 不同步日文 EPUB / pre-commit 专项配置，避免为未维护目录增加无效检查
  - 保持中文默认入口和核心教程内容不变

### 上游同步 — 2026-04-28

- Reviewed upstream range: `a7a0ea2` → `3221229`
- 重点上游变化：
  - 新增 `06-hooks/session-end.sh`，用于在 `SessionEnd` 时记录学习进度
  - 新增 `local-progress/index.html`，提供浏览器本地学习进度面板
  - 修正 agent 定义优先级为 CLI → Project → User
  - 修正 lesson quiz 题库里的 skill metadata 预算、agent 优先级和 hooks 类型口径
  - 配置示例继续收敛到 Opus 4.7 / Sonnet 4.6
- Chinese fork actions:
  - 将新增 hook 和本地进度页面改写为中文用户可直接理解的版本
  - 保留 `SessionEnd`、`CLAUDE_PROJECT_DIR`、`localStorage`、CLI flags 等可执行标识
  - 更新中文 hooks、subagents、CLI、advanced features 与题库说明
  - 保留本仓库自有 `RELEASE_NOTES.md`，不照搬上游删除动作

### 上游同步 — 2026-04-26

- Reviewed upstream range: `eff5bd2` → `a7a0ea2`
- 重点上游变化：
  - skills 文档把加载流程图的命名讲得更清楚
  - plugins 文档新增 marketplace update / plugin update 区分，以及 auto-update 说明
  - advanced features 修正 effort level 的模型支持范围，明确 `xhigh` 仅属于 Opus 4.7
- Chinese fork actions:
  - 只同步会影响中文用户理解和使用的说明性变化
  - 在中文文档里补上 marketplace 更新与 plugin 更新的区别
  - 修正 effort level 支持范围的中文表述，避免误导
  - 保持中文根目录主线，不引入上游多语言目录结构

### 上游同步 — 2026-04-25

- Reviewed upstream range: `d17d515` → `eff5bd2`
- 重点上游变化：
  - 修复 `security-reviewer` agent 中无效的 `diff` 工具配置，改为 `bash`
  - 新增 `scripts/check_cross_references.py` 的 repo-root 边界处理
  - 新增 `scripts/tests/test_check_cross_references.py` 覆盖该脚本边界场景
  - 将 `scripts/requirements.txt` 固定到已验证版本
- Chinese fork actions:
  - 把 agent 工具修正同步到中文仓库
  - 引入交叉引用检查脚本和测试，并修正中文仓库现有断锚，确保脚本能本地通过
  - 固定脚本依赖版本，减少环境差异导致的校验波动
  - 保持中文根目录主线，不引入上游多语言目录结构

### 上游同步 — 2026-04-24

- Reviewed upstream range: `cf92e8e` → `d17d515`
- 重点上游变化：
  - 上游同步到 Claude Code `v2.1.119`
  - slash commands 补充 `/cost` / `/stats` / `/usage` 的新关系，以及 `/doctor`、`/theme`、`/btw` 的新版说明
  - hooks 补充 `mcp_tool`、28 个事件、`duration_ms`、PowerShell auto-approve
  - CLI / advanced features 补充 native binary、docs host 迁移、Opus 4.7 细节、Auto Mode 与 settings 新行为
  - skills / memory / subagents / checkpoints / plugins 文档补充一批配置与行为说明
- Chinese fork actions:
  - 只把影响中文用户理解和实际使用的变化同步到中文根目录主线
  - 保持中文默认入口，不采用上游英文 README 和多语言目录结构
  - 对新增配置和命令做中文解释，同时保留可执行标识原样
  - 本地化校验与测试通过后再推送到 origin/main

### 上游同步 — 2026-04-22

- Reviewed upstream range: `9c224ff` → `cf92e8e`
- 重点上游变化：
  - 上游同步到 Claude Code `v2.1.110` / `v2.1.112`
  - 新增或明确 `/tui`、`/focus`、`/recap`、`/undo`、`/proactive`、`/ultrareview`、`/less-permission-prompts`
  - advanced features 补充了 TUI、session recap、push notifications、Auto Mode 新访问方式
  - CLI / docs 切到 Opus 4.7，并引入 `xhigh` effort
  - plugins 章节新增 background monitors 说明
- Chinese fork actions:
  - 把本轮新增能力同步到中文根目录主线文档
  - 保留中文默认入口，不采用上游英文 README 和 `uk/` / `zh/` 目录结构
  - 更新本地化校验，拦截明显未翻译的英文标题和英文模板段落

### 上游同步 — 2026-04-14

- Reviewed upstream range: `561c6cb` → `9c224ff`
- 重点上游变化：
  - 上游把 `# ...` inline memory 快捷写法标记为 discontinued，推荐改用 `/memory` 或自然语言记忆请求
  - `05-mcp/README.md` 不再继续强调 `WebSocket transport`
  - 新增 `/team-onboarding` 命令说明，并扩充了 `/ultraplan` 的云端起草细节
  - `Monitor Tool` 被明确写进 advanced features，用于替代低效轮询
  - `06-hooks/pre-tool-check.sh` 修复了 block reason 输出和 `rm -rf /tmp/...` 误拦截问题
  - README 补充了乌克兰语入口，但这属于上游多语言分发层变化
- Chinese fork actions:
  - 更新中文 `memory` 文档，移除对 `# ...` 快捷写法的继续推荐
  - 删除中文 `MCP` 文档里已经过时的 `WebSocket transport` 说明
  - 在中文命令目录、Catalog、Quick Reference 中补上 `/team-onboarding`、`/ultraplan` 与 `Monitor Tool`
  - 同步 `pre-tool-check.sh` 的上游修复，并新增回归测试覆盖 block/warn 行为
  - 保持根目录中文主线结构，不引入上游 `uk/` 目录和 README 语言切换入口

### 上游同步 — 2026-04-08

- Reviewed upstream range: `0ca8c37` → `561c6cb`
- 重点上游变化：
  - 上游在 2026 年 4 月完成一轮更大的文档同步，并发布 `v2.3.0`
  - 新增 `CLAUDE.md`
  - 新增 `04-subagents/performance-optimizer.md`
  - 新增 `06-hooks/pre-tool-check.sh` 与 `06-hooks/dependency-check.sh`
  - 一批 hooks 脚本改为读取 stdin JSON，并补齐 Windows Git Bash 兼容性
  - 文档层面新增 / 修正了 `MCP Apps`、`/ultraplan`、Agent Teams、Channels、`cleanupPeriodDays` 等说明
  - 上游新增 `zh/`、`vi/` 多语言目录，并重构了部分 CI / release 流程
- Chinese fork actions:
  - 将与中文主线直接相关的新增能力和示例同步到根目录中文文档
  - 新增中文 `CLAUDE.md`，适配本仓库自己的校验和本地化工作流
  - 新增 `performance-optimizer` subagent，并更新 `CATALOG.md`
  - 同步高价值 hooks 脚本与新版协议行为
  - 在 `README.md` 中更新最近同步日期与本轮更新说明
  - 未采用上游 `zh/` / `vi/` 目录结构与 README 指标徽章，继续保持“中文主线在根目录”的 fork 结构
### 上游同步 — 2026-04-01

- Upstream range: `d41b335` → `0ca8c37`
- Affected files:
  - `06-hooks/README.md`
  - `06-hooks/auto-adapt-mode.py`
  - `09-advanced-features/README.md`
  - `09-advanced-features/setup-auto-mode-permissions.py`
  - `README.md`
- Chinese fork actions:
  - 删除旧的 `auto-adapt-mode` hook 文件，不再继续维护“动态记忆批准”方案
  - 新增 `09-advanced-features/setup-auto-mode-permissions.py`，同步上游的一次性权限种子脚本
  - 在中文 `Advanced Features` 和 `Hooks` 文档中补上新的使用方式、适用场景和安全边界
  - 在项目介绍中写明最近同步日期与本次上游更新内容
  - 上游新增的 Trending 徽章未直接照搬，因为它描述的是上游仓库状态，而不是当前中文 fork 的状态

## 建议记录模板

```md
## 上游同步 - YYYY-MM-DD

- Upstream range: <old>...<new>
- Affected files:
  - README.md
  - 05-mcp/README.md
- Chinese fork actions:
  - 同步了 MCP 章节新增字段说明
  - 保留了命令名与 JSON key 不变
  - 补充了中国用户的安装注意事项
```

## 额外说明

- 如果你未来将本仓库发布到自己的 GitHub 账号下，建议仓库名使用 `claude-howto-zh-cn`。
- 如果需要替换徽章、封面图、仓库 URL，请在保留来源声明的前提下调整。
- 如果某处翻译和可执行性冲突，**优先保留原始标识**，并在正文中补中文解释。

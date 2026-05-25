# 本地化风格指南（Localization Style Guide）

## 目标

这份规范用于约束 `claude-howto-zh-cn` 的中文本土化方式，确保两件事同时成立：

- 中文用户更容易读懂、学会、照着做
- 文档里的命令、配置、模板、frontmatter、JSON/YAML 片段仍然可运行

## 核心原则

### 1. 术语保真，解释中文化

优先保留英文术语，并在首次出现时补充中文解释。例如：

- `skills`：可复用、可自动触发的能力
- `CLI`：命令行界面
- `hooks`：事件触发的自动化动作
- `MCP`：用于连接外部工具和数据的协议
- `subagents`：用于分工协作的子代理

不建议把这些词统一硬翻成一个中文词后全文替换。

### 2. 运行相关标识禁止翻译

以下内容默认视为 **protected tokens**：

- 目录名、文件名、扩展名
- slash command 名称
- skill / subagent / plugin 名称
- YAML frontmatter key
- JSON / YAML key
- CLI 命令和 flags
- 环境变量名
- MCP server 名
- 路径占位符
- 代码块中的可执行命令

示例：

- `allowed-tools`
- `tools`
- `model`
- `env`
- `GITHUB_TOKEN`
- `.mcp.json`
- `/optimize`
- `claude -p`

这些内容可以解释，但不要改名。

### 3. 面向中国小白重写表达

正文尽量遵循这个顺序：

1. 这是什么
2. 什么时候用
3. 需要提前准备什么
4. 怎么安装 / 配置 / 执行
5. 常见坑和排错建议

不要一上来就给一大段术语、字段表或抽象定义。

## 建议保留英文的高频术语

- Claude Code
- slash commands
- memory
- skills
- subagents
- hooks
- plugins
- MCP
- CLI
- print mode
- planning mode
- Auto Mode
- checkpoints
- session
- worktree

## 中文写法建议

- 第一次出现术语时写成：`skills`（可复用能力）这样的格式。
- 解释型内容多用短句，少用生硬长句。
- 能直接帮助用户操作的提醒，优先写在命令前面。
- 对中国用户常见障碍，尽量提前提示，不要等到“故障排查”章节再说。

## 允许改写的内容

- 标题
- 导语
- 对比表
- FAQ
- 学习路线描述
- 注释和说明型输出
- Mermaid 图中的说明性文字

## 默认不要改的内容

- frontmatter 字段名
- JSON / YAML key
- shell 命令
- 路径和目录名
- 环境变量名
- 插件/skill/subagent/command 的真实标识

## 风险等级

### 低风险

- 普通 `README.md`
- 学习路线、FAQ、导读、对比表

可以做完整中文重写。

### 中风险

- `SKILL.md`
- subagent `.md`
- slash command `.md`

只翻译人类可读说明，保留协议格式、字段名、命令、标识符。

### 高风险

- `.json`
- `.yml` / `.yaml`
- `.py`
- `.sh`
- GitHub Actions

除非明确知道不会影响行为，否则不要做功能性改写；如需中文化，只改注释或用户可见文案。

## 提交前检查

提交前至少执行一次：

```bash
uv run python scripts/validate_localization.py
```

它会检查：

- Markdown 相对链接
- YAML frontmatter
- JSON / YAML 语法
- shell 脚本语法
- 关键 protected tokens 是否仍存在

## 常见反例

错误做法：

- 把 `skills` 全文改成“技能系统”，却不保留原英文
- 把 `allowed-tools` 翻成 `允许工具`
- 把 `/optimize` 改成 `/优化`
- 把 `GITHUB_TOKEN` 改成 `GitHub令牌`
- 把 `.mcp.json` 改成中文文件名

推荐做法：

- 保留 `/optimize`，正文里解释“这是一个用于性能分析的 slash command”
- 保留 `GITHUB_TOKEN`，正文里补充“需要先在 GitHub 创建 token 并导出到环境变量”

# 发布说明

## 推荐 commit message

### 单行版本

```text
docs: ship the first polished zh-cn Claude Code guide release
```

### 带正文版本

```text
docs: ship the first polished zh-cn Claude Code guide release

- 将所有已跟踪的 Markdown 文档整理为中文优先指南
- 恢复 self-assessment / lesson-quiz 的完整交互流程
- 增加本地化校验护栏、测试和 CI 验证
- 提升面向中文初学者的发布完成度
```

## 推荐仓库描述（GitHub About）

```text
Claude Code 中文全面上手指南。基于 luongnv89/claude-howto 本土化重写，面向中国小白用户，保留命令与配置兼容性，并附学习路径与本地化校验护栏。
```

## 推荐 GitHub 首页摘要

```text
这是一个基于 luongnv89/claude-howto 的非官方中文本土化 fork，目标不是逐句翻译，而是做成适合中国小白长期学习的 Claude Code 全面上手指南。

你可以从 README、学习路线图和速查卡开始，再逐步进入 slash commands、memory、skills、MCP、hooks、subagents、plugins、CLI 等模块。仓库同时保留了关键可执行标识，并提供本地化校验脚本，尽量避免“中文化后示例不可用”的问题。
```

## 推荐首版 Release 标题

```text
v1.0.0 — 首个中文本土化发布
```

## 推荐首版 Release 摘要

```text
首个正式中文本土化版本，面向中国小白用户重写 Claude Code 学习主线，并保留关键命令、配置和 frontmatter 兼容性。

本版完成了中文首页、学习路线、速查卡、功能总表、主要模块 README，以及高频执行型 Markdown 的中文化收口；同时恢复了 self-assessment / lesson-quiz 的完整交互结构，并加入本地化校验脚本、测试与 CI 护栏。
```

## 发布前建议核对

- 仓库默认分支是否正确
- `UPSTREAM.md` 中的来源说明是否保留
- GitHub 仓库 About 文案是否与 README 首段一致
- Release 标题、tag 和 `RELEASE_NOTES.md` 是否统一

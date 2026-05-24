# 资源总览

仓库里的 `resources/` 目录主要存放：

- logo
- icon
- favicon
- 设计系统说明
- 快速使用说明
- 供文档引用的配套资源索引

如果你要把这个中文 fork 发布成独立仓库，也可以在保留来源说明的前提下替换这些资源。

## 2026 年 5 月需要关注的新能力

这轮同步后，中文读者如果只看资源索引，至少要知道这些新入口：

| 能力 | 说明 | 入口 |
|------|------|------|
| `/usage-credits` | 配置额外用量额度；`/extra-usage` 仍可作为 alias | [Slash Commands](01-slash-commands/) |
| `/run` / `/verify` | bundled skills，用于启动项目并确认改动真实可用 | [Skills Guide](03-skills/) |
| `/run-skill-generator` | 为项目生成专属 run / verify skill | [Skills Guide](03-skills/) |
| `claude agents --json` | 输出机器可读的 Agent View 列表 | [CLI Guide](10-cli/) |
| `background_tasks` / `session_crons` | Stop / SubagentStop hook 输入新增字段 | [Hooks Guide](06-hooks/) |

这些名称都是可执行标识或协议字段，不要翻译成中文 key。

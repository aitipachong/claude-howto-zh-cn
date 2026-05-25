# 发布说明

## v1.0.0 — 首个中文本土化发布

这是 `claude-howto-zh-cn` 的首个正式发布版本。

本次发布的目标不是做“逐句翻译镜像”，而是把上游项目重构成一个 **更适合中国小白长期学习、同时保留真实可用性的 Claude Code 中文全面上手指南**。

## 本版重点

### 1. 中文主线入口完成

- `README`
- `LEARNING-ROADMAP`
- `QUICK_REFERENCE`
- `CATALOG`
- 核心模块 `README`

这些入口文档现在已经统一成中文主线表达，学习路径、安装方式、使用场景和常见坑更贴近中文用户阅读习惯。

### 2. 执行型文档完成兼容性收口

- 保留命令名、frontmatter key、JSON/YAML key、CLI flags、环境变量等关键标识
- 修复了不应被中文化的显示标识
- 自动触发类 descriptions 补回英文触发短语

目标是避免“看起来翻译对了，但复制就跑不起来”的问题。

### 3. 互动学习能力补回完整结构

- `self-assessment` 恢复为完整自测流程
- `lesson-quiz` 恢复为完整 lesson 测验流程
- 题库恢复为结构化格式，并统一评分口径

### 4. 发布前护栏已落地

- 本地化校验脚本：`scripts/validate_localization.py`
- 对应测试已补齐
- CI / docs-check 工作流已扩展

## 自动验证

本版发布前已通过：

```bash
uv run python scripts/validate_localization.py
uv run pytest scripts/tests/ -q
```

## 适合谁

- 想系统学 Claude Code 的中文用户
- 想把上游项目改成中文团队教材的人
- 想保留真实命令和配置兼容性的本土化维护者

## 说明

- 本项目为 **非官方中文本土化 fork**
- 来源与同步策略见 [UPSTREAM.md](UPSTREAM.md)
- 本地化边界与术语规则见 [LOCALIZATION-STYLE.md](../contributing/LOCALIZATION-STYLE.md)

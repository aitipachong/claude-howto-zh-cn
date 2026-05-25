<picture>
  <source media="(prefers-color-scheme: dark)" srcset="resources/logos/claude-howto-logo-dark.svg">
  <img alt="Claude How To" src="resources/logos/claude-howto-logo.svg">
</picture>

# 参与贡献

欢迎为这个中文本土化仓库继续贡献内容。

## 贡献方向

- 改进中文表达
- 补充中国用户常见坑
- 修复无效链接和错误示例
- 补全教程、模板、skills、plugins 示例
- 同步上游更新

## 提交前请先看

- [UPSTREAM.md](docs/project/UPSTREAM.md)
- [LOCALIZATION-STYLE.md](docs/contributing/LOCALIZATION-STYLE.md)

## 本地验证

```bash
uv venv
uv pip install -r scripts/requirements-dev.txt
uv run python scripts/validate_localization.py
uv run pytest scripts/tests/ -q
```

## 贡献原则

- 不要把可执行标识翻坏
- 不要随意改目录结构和文件名
- 修改时尽量保持和上游映射关系清楚

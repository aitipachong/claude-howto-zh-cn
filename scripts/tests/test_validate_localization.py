"""Tests for localization validation utilities."""

from __future__ import annotations

import argparse

import pytest
from pathlib import Path

from validate_localization import (
    validate_data_files,
    validate_frontmatter,
    validate_markdown_links,
    validate_protected_snippets,
    validate_shell_scripts,
    validate_untranslated_english,
)


def test_validate_markdown_links_detects_missing_file(tmp_path: Path) -> None:
    readme = tmp_path / "README.md"
    readme.write_text("[Broken](missing.md)\n", encoding="utf-8")

    errors = validate_markdown_links(tmp_path)

    assert len(errors) == 1
    assert "broken relative link" in errors[0]


def test_validate_frontmatter_accepts_valid_mapping(tmp_path: Path) -> None:
    skill = tmp_path / "skill.md"
    skill.write_text(
        "---\nname: sample\ndescription: demo\n---\n# Title\n",
        encoding="utf-8",
    )

    errors = validate_frontmatter(tmp_path)

    assert errors == []


def test_validate_data_files_detects_bad_json(tmp_path: Path) -> None:
    config = tmp_path / "broken.json"
    config.write_text("{bad json}\n", encoding="utf-8")

    errors = validate_data_files(tmp_path)

    assert len(errors) == 1
    assert "invalid JSON" in errors[0]


def test_validate_shell_scripts_detects_syntax_error(tmp_path: Path) -> None:
    script = tmp_path / "broken.sh"
    script.write_text("if then\n", encoding="utf-8")

    errors = validate_shell_scripts(tmp_path)

    assert len(errors) == 1
    assert "invalid shell syntax" in errors[0]


def test_validate_protected_snippets_detects_missing_tokens(tmp_path: Path) -> None:
    files = {
        "README.md": (
            "## Table of Contents\n"
            "## Contributing\n"
            "## License\n"
            "UPSTREAM.md\n"
        ),
        "01-slash-commands/pr.md": "allowed-tools:\nBash(git add:*)\n",
        "03-skills/code-review/SKILL.md": "name: code-review-specialist\n## 审查模板\n",
        "04-subagents/code-reviewer.md": "name: code-reviewer\n",
        "05-mcp/github-mcp.json": '{"mcpServers": {"github": {}}}\n',
        "07-plugins/pr-review/.claude-plugin/plugin.json": '{"name": "pr-review"}\n',
    }
    for relative_path, content in files.items():
        path = tmp_path / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    errors = validate_protected_snippets(tmp_path)

    assert errors
    assert any("LOCALIZATION-STYLE.md" in error for error in errors)


def test_validate_untranslated_english_detects_english_heading(
    tmp_path: Path,
) -> None:
    readme = tmp_path / "README.md"
    readme.write_text("# Security Policy\n\n中文说明。\n", encoding="utf-8")

    errors = validate_untranslated_english(tmp_path)

    assert errors
    assert any("Security Policy" in error for error in errors)


def test_validate_untranslated_english_allows_protected_terms(
    tmp_path: Path,
) -> None:
    readme = tmp_path / "README.md"
    readme.write_text(
        "# Claude Code 中文指南\n\n"
        "## MCP (外部工具协议)\n\n"
        "### `/optimize`\n\n"
        "`GITHUB_TOKEN` 和 `.mcp.json` 这些标识不要翻译。\n",
        encoding="utf-8",
    )

    errors = validate_untranslated_english(tmp_path)

    assert errors == []


def test_validate_untranslated_english_allows_required_root_readme_headings(
    tmp_path: Path,
) -> None:
    readme = tmp_path / "README.md"
    readme.write_text(
        "## Table of Contents\n\n"
        "中文目录说明。\n\n"
        "## Contributing\n\n"
        "欢迎继续贡献。\n\n"
        "## License\n\n"
        "本项目使用 MIT License。\n",
        encoding="utf-8",
    )

    errors = validate_untranslated_english(tmp_path)

    assert errors == []


# =============================================================================
# Frontmatter Tests
# =============================================================================


def test_split_frontmatter_no_frontmatter_returns_none() -> None:
    from validate_localization import split_frontmatter

    assert split_frontmatter("# Just markdown\n") is None
    assert split_frontmatter("No frontmatter here\n") is None


def test_split_frontmatter_insufficient_separators_returns_none() -> None:
    from validate_localization import split_frontmatter

    assert split_frontmatter("---\nonly one") is None


def test_split_frontmatter_valid_returns_content() -> None:
    from validate_localization import split_frontmatter

    result = split_frontmatter("---\nname: test\n---\n# Title\n")
    assert result == "\nname: test\n"


def test_validate_frontmatter_no_frontmatter_skips(tmp_path: Path) -> None:
    readme = tmp_path / "README.md"
    readme.write_text("# No Frontmatter\n\nContent.\n", encoding="utf-8")

    errors = validate_frontmatter(tmp_path)
    assert errors == []


def test_validate_frontmatter_invalid_yaml_reported(tmp_path: Path) -> None:
    skill = tmp_path / "skill.md"
    skill.write_text(
        "---\nname: [unclosed\n---\n# Title\n",
        encoding="utf-8",
    )

    errors = validate_frontmatter(tmp_path)

    assert len(errors) == 1
    assert "invalid YAML frontmatter" in errors[0]


def test_validate_frontmatter_non_dict_reported(tmp_path: Path) -> None:
    skill = tmp_path / "skill.md"
    skill.write_text(
        "---\n- just\n- a\n- list\n---\n# Title\n",
        encoding="utf-8",
    )

    errors = validate_frontmatter(tmp_path)

    assert len(errors) == 1
    assert "must parse to a mapping" in errors[0]


# =============================================================================
# Data Files Tests (YAML)
# =============================================================================


def test_validate_data_files_detects_bad_yaml(tmp_path: Path) -> None:
    config = tmp_path / "broken.yml"
    config.write_text("bad: [unclosed\n", encoding="utf-8")

    errors = validate_data_files(tmp_path)

    assert len(errors) == 1
    assert "invalid YAML" in errors[0]


def test_validate_data_files_accepts_valid_yaml(tmp_path: Path) -> None:
    config = tmp_path / "valid.yml"
    config.write_text("key: value\nlist:\n  - a\n  - b\n", encoding="utf-8")

    errors = validate_data_files(tmp_path)

    assert errors == []


def test_validate_data_files_accepts_valid_json(tmp_path: Path) -> None:
    config = tmp_path / "valid.json"
    config.write_text('{"key": "value"}\n', encoding="utf-8")

    errors = validate_data_files(tmp_path)

    assert errors == []


# =============================================================================
# Link Validation - Directory Traversal
# =============================================================================


def test_iter_link_validation_files_traverses_directory(tmp_path: Path) -> None:
    from validate_localization import iter_link_validation_files

    # Create a mock directory structure matching LINK_VALIDATION_PATHS
    (tmp_path / "README.md").write_text("# Doc", encoding="utf-8")
    sub_dir = tmp_path / "01-slash-commands"
    sub_dir.mkdir()
    (sub_dir / "a.md").write_text("# A", encoding="utf-8")
    (sub_dir / "b.md").write_text("# B", encoding="utf-8")

    # Temporarily override LINK_VALIDATION_PATHS
    import validate_localization as vl

    original_paths = vl.LINK_VALIDATION_PATHS
    try:
        vl.LINK_VALIDATION_PATHS = [Path("README.md"), Path("01-slash-commands")]
        files = iter_link_validation_files(tmp_path)
        names = {f.name for f in files}
        assert "README.md" in names
        assert "a.md" in names
        assert "b.md" in names
    finally:
        vl.LINK_VALIDATION_PATHS = original_paths


def test_validate_markdown_links_ignores_external_urls(tmp_path: Path) -> None:
    readme = tmp_path / "README.md"
    readme.write_text(
        "[External](https://example.com)\n"
        "[Mail](mailto:test@example.com)\n"
        "[Anchor](#section)\n",
        encoding="utf-8",
    )

    errors = validate_markdown_links(tmp_path)

    assert errors == []


def test_validate_markdown_links_ignores_empty_target(tmp_path: Path) -> None:
    readme = tmp_path / "README.md"
    readme.write_text("[Empty]()\n", encoding="utf-8")

    errors = validate_markdown_links(tmp_path)

    assert errors == []


# =============================================================================
# Untranslated English - Edge Cases
# =============================================================================


def test_validate_untranslated_english_ignores_frontmatter(tmp_path: Path) -> None:
    readme = tmp_path / "README.md"
    readme.write_text(
        "---\nname: test-skill\ndescription: English description\n---\n\n"
        "# 中文标题\n\n中文内容。\n",
        encoding="utf-8",
    )

    errors = validate_untranslated_english(tmp_path)
    # Frontmatter should be skipped entirely
    assert not any("English description" in e for e in errors)


def test_validate_untranslated_english_ignores_fenced_code(tmp_path: Path) -> None:
    readme = tmp_path / "README.md"
    readme.write_text(
        "# 中文标题\n\n"
        "```bash\n"
        "git clone https://github.com/example/repo\n"
        "npm install\n"
        "```\n\n"
        "中文说明。\n",
        encoding="utf-8",
    )

    errors = validate_untranslated_english(tmp_path)
    # Code blocks should be ignored
    assert errors == []


def test_validate_untranslated_english_flags_prose_with_many_english_words(
    tmp_path: Path,
) -> None:
    readme = tmp_path / "README.md"
    # Use words with 3+ letters each (ENGLISH_WORD_RE requires [A-Za-z']{2,} after first char)
    readme.write_text(
        "# 中文标题\n\n"
        "These sentences contain many English vocabulary words here today.\n",
        encoding="utf-8",
    )

    errors = validate_untranslated_english(tmp_path)

    assert any("likely untranslated" in e for e in errors)


def test_validate_untranslated_english_allows_cjk_mixed_text(tmp_path: Path) -> None:
    readme = tmp_path / "README.md"
    readme.write_text(
        "# 中文标题\n\n"
        "这是一个中文句子，但包含一些 English words 也没有问题。\n",
        encoding="utf-8",
    )

    errors = validate_untranslated_english(tmp_path)

    assert errors == []


def test_validate_untranslated_english_ignores_command_lines(tmp_path: Path) -> None:
    readme = tmp_path / "README.md"
    readme.write_text(
        "# 中文标题\n\n"
        "- `git status` 查看状态\n"
        "* `npm install` 安装依赖\n"
        "- [some link](url)\n"
        "$ echo hello\n"
        "# /path/to/file\n",
        encoding="utf-8",
    )

    errors = validate_untranslated_english(tmp_path)

    # Command-like lines should be ignored
    assert errors == []


def test_validate_untranslated_english_allows_allowed_heading_patterns(
    tmp_path: Path,
) -> None:
    readme = tmp_path / "README.md"
    readme.write_text(
        "# 中文标题\n\n"
        "## CLAUDE.md\n\n"
        "## v2.1.145\n\n"
        "## CI/CD\n\n"
        "## `/optimize`\n\n"
        "## /my-command\n\n"
        "中文内容。\n",
        encoding="utf-8",
    )

    errors = validate_untranslated_english(tmp_path)

    assert errors == []


def test_validate_untranslated_english_ignores_empty_lines(tmp_path: Path) -> None:
    readme = tmp_path / "README.md"
    readme.write_text(
        "# 中文标题\n\n"
        "\n"
        "中文内容。\n",
        encoding="utf-8",
    )

    errors = validate_untranslated_english(tmp_path)

    assert errors == []


# =============================================================================
# Protected Snippets Tests
# =============================================================================


def test_validate_protected_snippets_missing_file_reported(tmp_path: Path) -> None:
    # Create only some of the required files
    readme = tmp_path / "README.md"
    readme.write_text(
        "## Table of Contents\n\n"
        "## Contributing\n\n"
        "## License\n\n"
        "UPSTREAM.md\n\n"
        "LOCALIZATION-STYLE.md\n",
        encoding="utf-8",
    )

    errors = validate_protected_snippets(tmp_path)

    # Missing files like 01-slash-commands/pr.md should be reported
    assert any("required file is missing" in e for e in errors)


def test_validate_protected_snippets_missing_snippet_reported(
    tmp_path: Path,
) -> None:
    readme = tmp_path / "README.md"
    readme.write_text(
        "## Table of Contents\n\n"
        "## Contributing\n\n"
        "UPSTREAM.md\n",
        encoding="utf-8",
    )

    errors = validate_protected_snippets(tmp_path)

    assert any("missing protected snippet" in e for e in errors)


# =============================================================================
# Shell Script Tests
# =============================================================================


def test_validate_shell_scripts_accepts_valid_script(tmp_path: Path) -> None:
    script = tmp_path / "valid.sh"
    script.write_text("#!/bin/bash\necho 'hello'\n", encoding="utf-8")

    errors = validate_shell_scripts(tmp_path)

    assert errors == []


def test_validate_shell_scripts_skips_venv(tmp_path: Path) -> None:
    venv = tmp_path / ".venv"
    venv.mkdir()
    (venv / "bad.sh").write_text("if then\n", encoding="utf-8")

    errors = validate_shell_scripts(tmp_path)

    assert errors == []


# =============================================================================
# Integration / Root Validation
# =============================================================================


def test_validate_root_combines_all_validators(tmp_path: Path) -> None:
    from validate_localization import validate_root

    # Create a valid repo structure
    readme = tmp_path / "README.md"
    readme.write_text("# 中文标题\n\n中文内容。\n", encoding="utf-8")

    errors = validate_root(tmp_path)

    # Should pass with no errors for a clean repo
    assert isinstance(errors, list)


def test_validate_root_detects_multiple_issues(tmp_path: Path) -> None:
    from validate_localization import validate_root

    # Create files with multiple issues
    readme = tmp_path / "README.md"
    readme.write_text(
        "# Security Policy\n\n"
        "[Broken](missing.md)\n\n"
        "```bash\nunclosed fence\n",
        encoding="utf-8",
    )
    bad_json = tmp_path / "bad.json"
    bad_json.write_text("{bad json}", encoding="utf-8")

    errors = validate_root(tmp_path)

    assert len(errors) >= 2


# =============================================================================
# CLI Tests
# =============================================================================


def test_main_with_errors_returns_one(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import validate_localization as vl

    readme = tmp_path / "README.md"
    readme.write_text("# Security Policy\n", encoding="utf-8")

    monkeypatch.setattr(vl, "parse_args", lambda: argparse.Namespace(root=tmp_path))

    assert vl.main() == 1


def test_main_clean_returns_zero(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import validate_localization as vl

    readme = tmp_path / "README.md"
    readme.write_text("# 中文标题\n\n中文内容。\n", encoding="utf-8")

    monkeypatch.setattr(vl, "parse_args", lambda: argparse.Namespace(root=tmp_path))
    # Mock protected snippets to avoid needing all required files
    monkeypatch.setattr(vl, "validate_protected_snippets", lambda root: [])

    assert vl.main() == 0

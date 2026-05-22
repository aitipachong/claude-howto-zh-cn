#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["pyyaml"]
# ///
"""Validate localization-sensitive files in the repository."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess  # nosec B404
import sys
from pathlib import Path

import yaml

MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
CJK_RE = re.compile(r"[\u4e00-\u9fff]")
ENGLISH_WORD_RE = re.compile(r"\b[A-Za-z][A-Za-z']{2,}\b")

MARKDOWN_IGNORE_PARTS = {
    ".git",
    ".pytest_cache",
    ".venv",
    "node_modules",
    "zh",
    "vi",
    "uk",
}

ALLOWED_ENGLISH_HEADING_RE = [
    re.compile(pattern)
    for pattern in [
        r"^#{1,6}\s+CLAUDE\.md$",
        r"^#{1,6}\s+v\d+\.\d+\.\d+\b.*$",
        r"^#{1,6}\s+CI/CD$",
        r"^#{1,6}\s+`[^`]+`$",
        r"^#{1,6}\s+/[A-Za-z0-9_-]+$",
    ]
]

ALLOWED_ENGLISH_HEADINGS_BY_PATH = {
    Path("README.md"): {
        "## Table of Contents",
        "## Contributing",
        "## License",
    }
}

FORBIDDEN_UNTRANSLATED_SNIPPETS = [
    "## Table of Contents",
    "## Contributing",
    "## License",
    "# Security Policy",
    "# Testing Guide",
    "# Publishing Notes",
    "## Review Template",
    "## Project Information",
    "## Executive Summary",
    "## Pre-Refactoring Checklist",
    "## Identified Code Smells",
    "## Refactoring Phases",
    "| Area | Status |",
    "| Feature Area | Score | Mastery | Status |",
    "This is a TypeScript web application.",
    "Run tests before commit.",
    "Keep API changes documented.",
]
LINK_VALIDATION_PATHS = [
    Path("README.md"),
    Path("UPSTREAM.md"),
    Path("LOCALIZATION-STYLE.md"),
    Path("LEARNING-ROADMAP.md"),
    Path("QUICK_REFERENCE.md"),
    Path("CATALOG.md"),
    Path("CHANGELOG.md"),
    Path("02-memory/README.md"),
    Path("03-skills/README.md"),
    Path("05-mcp/README.md"),
    Path("06-hooks/README.md"),
    Path("07-plugins/README.md"),
    Path("08-checkpoints/README.md"),
    Path("09-advanced-features/README.md"),
    Path("10-cli/README.md"),
    Path("scripts/README.md"),
    Path("01-slash-commands"),
    Path("03-skills/code-review/SKILL.md"),
    Path("04-subagents"),
]

PROTECTED_SNIPPETS = {
    Path("README.md"): [
        "## Table of Contents",
        "## Contributing",
        "## License",
        "UPSTREAM.md",
        "LOCALIZATION-STYLE.md",
    ],
    Path("01-slash-commands/pr.md"): [
        "allowed-tools:",
        "Bash(git add:*)",
        "Bash(git status:*)",
        "Bash(git diff:*)",
    ],
    Path("03-skills/code-review/SKILL.md"): [
        "name: code-review-specialist",
        "## 审查模板",
    ],
    Path("04-subagents/code-reviewer.md"): [
        "name: code-reviewer",
        "tools: Read, Grep, Glob, Bash",
        "model: inherit",
    ],
    Path("05-mcp/github-mcp.json"): [
        '"mcpServers"',
        '"github"',
        '"GITHUB_TOKEN"',
    ],
    Path("07-plugins/pr-review/.claude-plugin/plugin.json"): [
        '"name": "pr-review"',
        '"version"',
        '"license": "MIT"',
    ],
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def iter_link_validation_files(root: Path) -> list[Path]:
    files: set[Path] = set()
    for relative_path in LINK_VALIDATION_PATHS:
        path = root / relative_path
        if not path.exists():
            continue
        if path.is_file():
            files.add(path)
            continue
        files.update(child for child in path.rglob("*.md") if child.is_file())
    return sorted(files)


def validate_markdown_links(root: Path) -> list[str]:
    errors: list[str] = []
    for path in iter_link_validation_files(root):
        content = read_text(path)
        for raw_target in MARKDOWN_LINK_RE.findall(content):
            target = raw_target.strip()
            if not target or target.startswith("#"):
                continue
            if "://" in target or target.startswith(("mailto:", "javascript:")):
                continue
            target_path = target.split("#", 1)[0]
            resolved = (path.parent / target_path).resolve()
            if not resolved.exists():
                errors.append(f"{path}: broken relative link '{target}'")
    return errors


def split_frontmatter(content: str) -> str | None:
    if not content.startswith("---\n"):
        return None
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None
    return parts[1]


def validate_frontmatter(root: Path) -> list[str]:
    errors: list[str] = []
    for path in root.rglob("*.md"):
        if ".venv" in path.parts or "node_modules" in path.parts:
            continue
        frontmatter = split_frontmatter(read_text(path))
        if frontmatter is None:
            continue
        try:
            loaded = yaml.safe_load(frontmatter)
        except yaml.YAMLError as exc:
            errors.append(f"{path}: invalid YAML frontmatter - {exc}")
            continue
        if loaded is not None and not isinstance(loaded, dict):
            errors.append(f"{path}: YAML frontmatter must parse to a mapping")
    return errors


def validate_data_files(root: Path) -> list[str]:
    errors: list[str] = []
    for path in root.rglob("*.json"):
        if ".venv" in path.parts or "node_modules" in path.parts:
            continue
        try:
            json.loads(read_text(path))
        except json.JSONDecodeError as exc:
            errors.append(f"{path}: invalid JSON - {exc}")
    for suffix in ("*.yml", "*.yaml"):
        for path in root.rglob(suffix):
            if ".venv" in path.parts or "node_modules" in path.parts:
                continue
            try:
                yaml.safe_load(read_text(path))
            except yaml.YAMLError as exc:
                errors.append(f"{path}: invalid YAML - {exc}")
    return errors


def validate_shell_scripts(root: Path) -> list[str]:
    bash_path = shutil.which("bash")
    if bash_path is None:
        # Fallback to common Git for Windows paths.
        for candidate in (
            r"C:\Program Files\Git\bin\bash.exe",
            r"C:\Program Files\Git\usr\bin\bash.exe",
            r"C:\Program Files (x86)\Git\bin\bash.exe",
        ):
            if Path(candidate).exists():
                bash_path = candidate
                break

    if bash_path is None:
        print("Warning: bash not found, skipping shell script validation.")
        return []

    errors: list[str] = []
    for path in root.rglob("*.sh"):
        if ".venv" in path.parts or "node_modules" in path.parts:
            continue
        # Validate repo-local shell files with `bash -n`.
        result = subprocess.run(  # nosec B603
            [bash_path, "-n", str(path)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            details = result.stderr.strip() or "bash -n failed"
            errors.append(f"{path}: invalid shell syntax - {details}")
    return errors


def iter_markdown_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*.md")
        if not any(part in MARKDOWN_IGNORE_PARTS for part in path.parts)
    )


def is_allowed_english_heading(line: str) -> bool:
    return any(pattern.match(line) for pattern in ALLOWED_ENGLISH_HEADING_RE)


def strip_inline_code(line: str) -> str:
    return re.sub(r"`[^`]*`", "", line)


def looks_like_command_or_path(line: str) -> bool:
    stripped = line.strip()
    if stripped.startswith(("[![", "<", "|", "$", "# /", "# -", "- `", "* `")):
        return True
    command_prefixes = (
        "git ",
        "npm ",
        "npx ",
        "uv ",
        "python ",
        "python3 ",
        "bash ",
        "claude ",
        "curl ",
        "docker ",
        "kubectl ",
        "bq ",
        "cp ",
        "mkdir ",
    )
    return stripped.startswith(command_prefixes)


def validate_untranslated_english(root: Path) -> list[str]:
    errors: list[str] = []

    for path in iter_markdown_files(root):
        relative_path = path.relative_to(root)
        allowed_headings = ALLOWED_ENGLISH_HEADINGS_BY_PATH.get(relative_path, set())
        content = read_text(path)
        for snippet in FORBIDDEN_UNTRANSLATED_SNIPPETS:
            if snippet in content and snippet not in allowed_headings:
                errors.append(f"{path}: untranslated protected text '{snippet}'")

        in_fence = False
        in_frontmatter = False
        first_line = True
        for line_number, raw_line in enumerate(content.splitlines(), 1):
            line = raw_line.strip()
            if first_line and line == "---":
                in_frontmatter = True
                first_line = False
                continue
            first_line = False
            if in_frontmatter:
                if line == "---":
                    in_frontmatter = False
                continue
            if line.startswith(("```", "~~~")):
                in_fence = not in_fence
                continue
            if in_fence or not line or looks_like_command_or_path(line):
                continue

            if line.startswith("#") and not CJK_RE.search(line):
                if line in allowed_headings:
                    continue
                if ENGLISH_WORD_RE.search(line) and not is_allowed_english_heading(
                    line
                ):
                    errors.append(
                        f"{path}:{line_number}: untranslated heading '{line}'"
                    )
                continue

            text = strip_inline_code(line)
            if CJK_RE.search(text):
                continue
            if len(ENGLISH_WORD_RE.findall(text)) >= 9:
                errors.append(
                    f"{path}:{line_number}: likely untranslated text '{line}'"
                )

    return errors


def validate_protected_snippets(root: Path) -> list[str]:
    errors: list[str] = []
    for relative_path, snippets in PROTECTED_SNIPPETS.items():
        path = root / relative_path
        if not path.exists():
            errors.append(f"{relative_path}: required file is missing")
            continue
        content = read_text(path)
        errors.extend(
            f"{relative_path}: missing protected snippet '{snippet}'"
            for snippet in snippets
            if snippet not in content
        )
    return errors


def validate_root(root: Path) -> list[str]:
    errors: list[str] = []
    errors.extend(validate_markdown_links(root))
    errors.extend(validate_frontmatter(root))
    errors.extend(validate_data_files(root))
    errors.extend(validate_shell_scripts(root))
    errors.extend(validate_untranslated_english(root))
    errors.extend(validate_protected_snippets(root))
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate localization-sensitive content in the repository."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Repository root to validate.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    errors = validate_root(root)
    if errors:
        print("Localization validation failed:\n")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Localization validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

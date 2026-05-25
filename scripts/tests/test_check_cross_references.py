"""Tests for check_cross_references.py - focus on repo-root boundary."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

import check_cross_references


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_links_escaping_repo_root_are_skipped(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    outside = repo.parent / "outside.md"
    outside.write_text("# Outside")

    rel = os.path.relpath(outside, repo)
    (repo / "README.md").write_text(f"# Doc\n\n[escape]({rel})\n")

    assert check_cross_references.main() == 0
    assert "broken cross-reference" not in capsys.readouterr().out


def test_broken_in_repo_link_is_reported(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (repo / "README.md").write_text("# Doc\n\n[missing](does-not-exist.md)\n")

    assert check_cross_references.main() == 1
    assert "broken cross-reference" in capsys.readouterr().out


def test_valid_in_repo_link_passes(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (repo / "other.md").write_text("# Other")
    (repo / "README.md").write_text("# Doc\n\n[ok](other.md)\n")

    assert check_cross_references.main() == 0
    assert "All cross-references valid" in capsys.readouterr().out


def test_numbered_lesson_dir_missing_readme_is_reported(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (repo / "README.md").write_text("# Doc")
    (repo / "01-intro").mkdir()

    assert check_cross_references.main() == 1
    assert "01-intro: missing README.md" in capsys.readouterr().out


class TestHeadingToAnchor:
    def test_simple_heading(self) -> None:
        assert check_cross_references.heading_to_anchor("Hello World") == "hello-world"

    def test_punctuation_removed(self) -> None:
        assert check_cross_references.heading_to_anchor("What's Next?") == "whats-next"

    def test_unicode_preserved(self) -> None:
        assert check_cross_references.heading_to_anchor("Hướng dẫn") == "hướng-dẫn"

    def test_emoji_stripped(self) -> None:
        assert check_cross_references.heading_to_anchor("🔥 Trending") == "-trending"

    def test_empty_after_processing(self) -> None:
        assert check_cross_references.heading_to_anchor("!!!") == ""

    def test_trailing_hyphens_stripped(self) -> None:
        assert check_cross_references.heading_to_anchor("Hello-") == "hello"

    def test_emoji_removed_no_leading_hyphen(self) -> None:
        # 🔥 is removed, no space before Fire, so no leading hyphen
        assert check_cross_references.heading_to_anchor("🔥Fire") == "fire"


class TestStripCodeBlocks:
    def test_removes_fenced_blocks(self) -> None:
        content = "Before\n```python\nprint('hi')\n```\nAfter"
        result = check_cross_references.strip_code_blocks(content)
        assert "Before" in result
        assert "After" in result
        assert "print" not in result

    def test_removes_inline_code(self) -> None:
        content = "Use `print()` for output"
        result = check_cross_references.strip_code_blocks(content)
        assert "Use" in result
        assert "print" not in result


class TestAnchorValidation:
    def test_valid_anchor_passes(
        self, repo: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        (repo / "README.md").write_text(
            "# Doc\n\n## Section\n\n[link](#section)\n"
        )
        assert check_cross_references.main() == 0

    def test_broken_anchor_reported(
        self, repo: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        (repo / "README.md").write_text(
            "# Doc\n\n## Section\n\n[link](#missing-section)\n"
        )
        assert check_cross_references.main() == 1
        assert "broken anchor" in capsys.readouterr().out

    def test_anchor_with_emoji_heading(
        self, repo: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        (repo / "README.md").write_text(
            "# Doc\n\n## 🚀 Getting Started\n\n[link](#-getting-started)\n"
        )
        assert check_cross_references.main() == 0


class TestCodeFenceValidation:
    def test_unmatched_fences_reported(
        self, repo: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        (repo / "README.md").write_text("# Doc\n\n```python\ncode\n")
        assert check_cross_references.main() == 1
        assert "unmatched code fences" in capsys.readouterr().out

    def test_matched_fences_pass(
        self, repo: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        (repo / "README.md").write_text("# Doc\n\n```python\ncode\n```\n")
        assert check_cross_references.main() == 0


class TestIgnoreDirsAndFiles:
    def test_ignored_dirs_skipped(
        self, repo: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        (repo / "README.md").write_text("# Doc")
        venv = repo / ".venv"
        venv.mkdir()
        (venv / "bad.md").write_text("[broken](missing.md)\n")
        assert check_cross_references.main() == 0

    def test_ignored_files_skipped(
        self, repo: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        (repo / "README.md").write_text("# Doc")
        (repo / "README.backup.md").write_text("[broken](missing.md)\n")
        assert check_cross_references.main() == 0

    def test_code_block_links_ignored(
        self, repo: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        (repo / "README.md").write_text(
            "# Doc\n\n```\n[example](missing.md)\n```\n"
        )
        assert check_cross_references.main() == 0


class TestLessonDirBoundary:
    def test_dirs_above_range_not_checked(
        self, repo: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        (repo / "README.md").write_text("# Doc")
        (repo / "12-future").mkdir()
        assert check_cross_references.main() == 0

    def test_dirs_below_range_not_checked(
        self, repo: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        (repo / "README.md").write_text("# Doc")
        (repo / "00-intro").mkdir()
        assert check_cross_references.main() == 0

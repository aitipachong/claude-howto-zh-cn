"""Tests for the EPUB builder module."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from unittest.mock import patch

import httpx
import pytest
from ebooklib import epub

# Fixtures are imported from conftest.py automatically by pytest
# Import from parent directory (handled by conftest.py sys.path)
from build_epub import (
    BuildState,
    ChapterCollector,
    EPUBConfig,
    MermaidRenderer,
    ValidationError,
    _attr_str,
    collect_folder_files,
    convert_internal_links,
    create_chapter_html,
    create_cover_image,
    create_stylesheet,
    extract_all_mermaid_blocks,
    extract_markdown_h1,
    get_chapter_order,
    handle_svg_image,
    load_font,
    md_to_html,
    prepare_root_readme_for_epub,
    process_mermaid_blocks,
    sanitize_mermaid,
    setup_logging,
    validate_inputs,
)

# =============================================================================
# BuildState Tests
# =============================================================================


class TestBuildState:
    """Tests for BuildState dataclass."""

    def test_initial_state(self, state: BuildState) -> None:
        """Test that initial state is empty."""
        assert state.mermaid_counter == 0
        assert len(state.mermaid_cache) == 0
        assert len(state.mermaid_added_to_book) == 0
        assert len(state.embedded_assets) == 0
        assert len(state.path_to_chapter) == 0

    def test_state_modification(self, state: BuildState) -> None:
        """Test that state can be modified."""
        state.mermaid_counter = 5
        state.mermaid_cache["key"] = (b"data", "file.png")
        state.mermaid_added_to_book.add("file.png")
        state.embedded_assets.add("logo.png")
        state.path_to_chapter["README.md"] = "chap_01.xhtml"

        assert state.mermaid_counter == 5
        assert state.mermaid_cache["key"] == (b"data", "file.png")
        assert "file.png" in state.mermaid_added_to_book
        assert "logo.png" in state.embedded_assets
        assert state.path_to_chapter["README.md"] == "chap_01.xhtml"

    def test_reset(self, state: BuildState) -> None:
        """Test that reset clears all state."""
        state.mermaid_counter = 5
        state.mermaid_cache["key"] = (b"data", "file.png")
        state.mermaid_added_to_book.add("file.png")
        state.embedded_assets.add("logo.png")
        state.path_to_chapter["README.md"] = "chap_01.xhtml"

        state.reset()

        assert state.mermaid_counter == 0
        assert len(state.mermaid_cache) == 0
        assert len(state.mermaid_added_to_book) == 0
        assert len(state.embedded_assets) == 0
        assert len(state.path_to_chapter) == 0


# =============================================================================
# EPUBConfig Tests
# =============================================================================


class TestEPUBConfig:
    """Tests for EPUBConfig dataclass."""

    def test_required_fields(self, tmp_path: Path) -> None:
        """Test that required fields must be provided."""
        config = EPUBConfig(
            root_path=tmp_path,
            output_path=tmp_path / "out.epub",
        )
        assert config.root_path == tmp_path
        assert config.output_path == tmp_path / "out.epub"

    def test_default_values(self, tmp_path: Path) -> None:
        """Test that default values are set correctly."""
        config = EPUBConfig(
            root_path=tmp_path,
            output_path=tmp_path / "out.epub",
        )
        assert config.identifier == "claude-howto-zh-cn-guide"
        assert config.title == "Claude Code 中文全面上手指南"
        assert config.language == "zh"
        assert config.author == "claude-howto-zh-cn contributors"
        assert config.request_timeout == 30.0
        assert config.max_concurrent_requests == 10
        assert config.max_retries == 3

    def test_custom_values(self, tmp_path: Path) -> None:
        """Test that custom values override defaults."""
        config = EPUBConfig(
            root_path=tmp_path,
            output_path=tmp_path / "out.epub",
            title="Custom Title",
            request_timeout=60.0,
            max_concurrent_requests=5,
        )
        assert config.title == "Custom Title"
        assert config.request_timeout == 60.0
        assert config.max_concurrent_requests == 5


# =============================================================================
# Validation Tests
# =============================================================================


class TestValidation:
    """Tests for input validation."""

    def test_valid_inputs(self, config: EPUBConfig, logger: logging.Logger) -> None:
        """Test that valid inputs pass validation."""
        # Should not raise
        validate_inputs(config, logger)

    def test_missing_root_path(self, tmp_path: Path, logger: logging.Logger) -> None:
        """Test that missing root path raises ValidationError."""
        config = EPUBConfig(
            root_path=tmp_path / "nonexistent",
            output_path=tmp_path / "out.epub",
        )
        with pytest.raises(ValidationError, match="Root path does not exist"):
            validate_inputs(config, logger)

    def test_root_path_is_file(self, tmp_path: Path, logger: logging.Logger) -> None:
        """Test that file as root path raises ValidationError."""
        file_path = tmp_path / "file.txt"
        file_path.write_text("content")
        config = EPUBConfig(
            root_path=file_path,
            output_path=tmp_path / "out.epub",
        )
        with pytest.raises(ValidationError, match="Root path is not a directory"):
            validate_inputs(config, logger)

    def test_no_markdown_files(self, tmp_path: Path, logger: logging.Logger) -> None:
        """Test that directory with no markdown files raises ValidationError."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        config = EPUBConfig(
            root_path=empty_dir,
            output_path=tmp_path / "out.epub",
        )
        with pytest.raises(ValidationError, match="No markdown files found"):
            validate_inputs(config, logger)

    def test_missing_output_directory(
        self, tmp_project: Path, logger: logging.Logger
    ) -> None:
        """Test that missing output directory raises ValidationError."""
        config = EPUBConfig(
            root_path=tmp_project,
            output_path=tmp_project / "nonexistent" / "out.epub",
        )
        with pytest.raises(ValidationError, match="Output directory does not exist"):
            validate_inputs(config, logger)


class TestCoverGeneration:
    """Tests for cover image generation."""

    def test_create_cover_image_from_prebuilt_cover(
        self, tmp_path: Path, logger: logging.Logger
    ) -> None:
        cover_path = tmp_path / "cover.png"
        from PIL import Image as PILImage

        PILImage.new("RGB", (1200, 1800), color=(240, 240, 240)).save(cover_path, "PNG")

        config = EPUBConfig(
            root_path=tmp_path,
            output_path=tmp_path / "out.epub",
            cover_image_path=cover_path,
        )

        cover_bytes = create_cover_image(config, logger)

        assert len(cover_bytes) > 0


# =============================================================================
# Mermaid Processing Tests
# =============================================================================


class TestMermaidProcessing:
    """Tests for Mermaid diagram processing."""

    def test_sanitize_mermaid_numbered_list(self) -> None:
        """Test that numbered lists in brackets are escaped."""
        input_code = 'A["1. First item"] --> B["2. Second item"]'
        expected = 'A["1\\. First item"] --> B["2\\. Second item"]'
        assert sanitize_mermaid(input_code) == expected

    def test_sanitize_mermaid_no_change(self) -> None:
        """Test that code without numbered lists is unchanged."""
        input_code = "A --> B --> C"
        assert sanitize_mermaid(input_code) == input_code

    def test_extract_mermaid_blocks(
        self, tmp_path: Path, logger: logging.Logger
    ) -> None:
        """Test extraction of Mermaid blocks from files."""
        # Create test file with mermaid blocks
        md_file = tmp_path / "test.md"
        md_file.write_text(
            """# Test

```mermaid
graph TD
    A --> B
```

Some text

```mermaid
graph LR
    C --> D
```
"""
        )

        diagrams, _ = extract_all_mermaid_blocks([(md_file, "Test")], logger)

        assert len(diagrams) == 2
        assert diagrams[0][0] == 1  # First diagram index
        assert diagrams[1][0] == 2  # Second diagram index
        assert "A --> B" in diagrams[0][1]
        assert "C --> D" in diagrams[1][1]

    def test_extract_mermaid_blocks_deduplication(
        self, tmp_path: Path, logger: logging.Logger
    ) -> None:
        """Test that duplicate Mermaid blocks are deduplicated."""
        md_file1 = tmp_path / "test1.md"
        md_file2 = tmp_path / "test2.md"

        same_diagram = """```mermaid
graph TD
    A --> B
```"""

        md_file1.write_text(f"# File 1\n\n{same_diagram}")
        md_file2.write_text(f"# File 2\n\n{same_diagram}")

        diagrams, _ = extract_all_mermaid_blocks(
            [(md_file1, "Test1"), (md_file2, "Test2")], logger
        )

        # Should only have one diagram since they're identical
        assert len(diagrams) == 1

    @pytest.mark.asyncio
    async def test_mermaid_render_timeout_keeps_build_going(
        self, config: EPUBConfig, state: BuildState, logger: logging.Logger
    ) -> None:
        """A Kroki timeout should not fail the whole EPUB build."""
        renderer = MermaidRenderer(config, state, logger)

        with patch.object(
            renderer,
            "_fetch_with_retry",
            side_effect=httpx.ReadTimeout("timed out"),
        ):
            rendered = await renderer.render_all([(1, "graph TD\n    A --> B")])

        assert rendered == {}
        assert state.mermaid_cache == {}

    def test_unrendered_mermaid_block_falls_back_to_source(
        self, state: BuildState, logger: logging.Logger
    ) -> None:
        """Unrendered Mermaid should remain readable instead of raising."""
        content = """# Diagram

```mermaid
graph TD
    A --> B
```
"""

        processed = process_mermaid_blocks(content, epub.EpubBook(), state, logger)

        assert "```mermaid" in processed
        assert "A --> B" in processed


# =============================================================================
# Chapter Collection Tests
# =============================================================================


class TestChapterCollector:
    """Tests for ChapterCollector class."""

    def test_collect_single_file(self, tmp_path: Path, state: BuildState) -> None:
        """Test collecting a single markdown file."""
        readme = tmp_path / "README.md"
        readme.write_text("# Test")

        collector = ChapterCollector(tmp_path, state)
        chapters = collector.collect_all_chapters([("README.md", "Introduction")])

        assert len(chapters) == 1
        assert chapters[0].file_path == readme
        assert chapters[0].display_name == "Test"
        assert chapters[0].chapter_filename == "chap_01.xhtml"
        assert state.path_to_chapter["README.md"] == "chap_01.xhtml"

    def test_collect_folder(self, tmp_project: Path, state: BuildState) -> None:
        """Test collecting a folder with multiple files."""
        collector = ChapterCollector(tmp_project, state)
        chapters = collector.collect_all_chapters([("01-test-chapter", "Test Chapter")])

        assert len(chapters) == 2  # README.md and section.md
        assert chapters[0].is_folder_overview is True
        assert chapters[0].folder_name == "Chapter Overview"
        assert chapters[0].file_title == "概览"
        assert chapters[1].is_folder_overview is False

    def test_path_mapping(self, tmp_project: Path, state: BuildState) -> None:
        """Test that path mapping is built correctly."""
        collector = ChapterCollector(tmp_project, state)
        collector.collect_all_chapters(
            [
                ("README.md", "Introduction"),
                ("01-test-chapter", "Test Chapter"),
            ]
        )

        assert "README.md" in state.path_to_chapter
        assert "01-test-chapter" in state.path_to_chapter
        # Use Path to handle Windows/Unix path separator differences
        readme_key = str(Path("01-test-chapter") / "README.md")
        assert readme_key in state.path_to_chapter


# =============================================================================
# HTML Generation Tests
# =============================================================================


class TestHTMLGeneration:
    """Tests for HTML generation."""

    def test_create_chapter_html_overview(self) -> None:
        """Test creating HTML for an overview chapter."""
        html = create_chapter_html(
            display_name="Introduction",
            file_title="Introduction",
            html_content="<h1>Introduction</h1><h2>Table of Contents</h2><p>Content</p>",
            is_overview=True,
        )

        assert "<!DOCTYPE html>" in html
        assert '<html xmlns="http://www.w3.org/1999/xhtml"' in html
        assert 'lang="zh"' in html
        assert html.count("<h1>Introduction</h1>") == 1
        assert "<h2>目录</h2>" in html
        assert "<p>Content</p>" in html

    def test_create_chapter_html_section(self) -> None:
        """Test creating HTML for a section chapter."""
        html = create_chapter_html(
            display_name="Chapter",
            file_title="Section",
            html_content="<h1>Section</h1><h2>Best Practices</h2><p>Content</p>",
            is_overview=False,
        )

        assert "<h2>Section</h2>" in html
        assert "<h1>Section</h1>" not in html
        assert "<h2>最佳实践</h2>" in html


class TestMarkdownPreprocessing:
    """Tests for markdown preprocessing helpers."""

    def test_prepare_root_readme_for_epub_replaces_hero_block(self) -> None:
        content = """<picture>old</picture>

[![Badge](https://example.com/badge.svg)](https://example.com)

# Claude Code 中文全面上手指南

导语内容

---

## 目录

正文内容
"""

        processed = prepare_root_readme_for_epub(content)

        assert "<picture>" not in processed
        assert "follow-qr.jpg" in processed
        assert "luongnv89/claude-howto" in processed
        assert processed.startswith("# Claude Code 中文全面上手指南")
        assert "导语内容" not in processed
        assert "## 目录" in processed

    def test_html_escaping(self) -> None:
        """Test that HTML special characters are escaped."""
        html = create_chapter_html(
            display_name="<script>alert('xss')</script>",
            file_title="Test & Title",
            html_content="<p>Content</p>",
            is_overview=True,
        )

        assert "&lt;script&gt;" in html
        # Note: Python's html.escape uses &#x27; for single quotes
        assert "<script>alert" not in html


# =============================================================================
# Chapter Order Tests
# =============================================================================


class TestChapterOrder:
    """Tests for chapter ordering."""

    def test_get_chapter_order(self) -> None:
        """Test that chapter order is defined correctly."""
        order = get_chapter_order()

        assert len(order) > 0
        assert order[0] == ("README.md", "首页")

        # Check that all expected chapters are present
        chapter_names = [name for name, _ in order]
        assert "01-slash-commands" in chapter_names
        assert "02-memory" in chapter_names
        assert "10-cli" in chapter_names
        assert "resources.md" in chapter_names


class TestMarkdownTitleExtraction:
    """Tests for extracting markdown H1 titles."""

    def test_extract_markdown_h1(self, tmp_path: Path) -> None:
        md = tmp_path / "sample.md"
        md.write_text("# 中文标题\n\n正文\n", encoding="utf-8")

        assert extract_markdown_h1(md) == "中文标题"

    def test_extract_markdown_h1_ignores_code_blocks(self, tmp_path: Path) -> None:
        md = tmp_path / "sample.md"
        md.write_text(
            "```md\n# fake\n```\n\n# Real Title\n",
            encoding="utf-8",
        )

        assert extract_markdown_h1(md) == "Real Title"


# =============================================================================
# Logging Tests
# =============================================================================


class TestLogging:
    """Tests for logging setup."""

    def test_setup_logging_default(self) -> None:
        """Test default logging setup."""
        logger = setup_logging(verbose=False)
        assert logger.name == "epub_builder"

    def test_setup_logging_verbose(self) -> None:
        """Test verbose logging setup."""
        logger = setup_logging(verbose=True)
        assert logger.name == "epub_builder"


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for the full build process."""

    @pytest.mark.asyncio
    async def test_build_without_mermaid(
        self, tmp_project: Path, logger: logging.Logger
    ) -> None:
        """Test building an EPUB without Mermaid diagrams."""
        from build_epub import build_epub_async

        config = EPUBConfig(
            root_path=tmp_project,
            output_path=tmp_project / "test.epub",
        )

        # Override chapter order for minimal test
        with patch("build_epub.get_chapter_order") as mock_order:
            mock_order.return_value = [("README.md", "Introduction")]

            result = await build_epub_async(config, logger)

            assert result.exists()
            assert result.suffix == ".epub"


# =============================================================================
# Critical Issue 1: BeautifulSoup 重复解析
# =============================================================================


class TestSinglePassParsing:
    """Tests for Critical Issue 1: BeautifulSoup should parse only once per file."""

    def test_convert_internal_links_accepts_soup_object(self, tmp_path: Path) -> None:
        """convert_internal_links 应该接收 BeautifulSoup 对象并返回 soup 对象。"""
        from bs4 import BeautifulSoup

        state = BuildState()
        state.path_to_chapter["README.md"] = "chap_01.xhtml"

        # Use absolute paths like real code does
        root_path = tmp_path.resolve()
        current_file = root_path / "test.md"
        current_file.write_text("test")

        html = '<p><a href="README.md">Link</a></p>'
        soup = BeautifulSoup(html, "html.parser")

        result = convert_internal_links(soup, current_file, root_path, state)

        assert isinstance(result, BeautifulSoup)
        a_tag = result.find("a")
        assert a_tag is not None
        assert a_tag["href"] == "chap_01.xhtml"

    def test_md_to_html_parses_soup_only_once(
        self, tmp_path: Path, state: BuildState, logger: logging.Logger
    ) -> None:
        """md_to_html 中 BeautifulSoup 构造函数应该只被调用一次。"""
        from unittest.mock import patch

        from bs4 import BeautifulSoup

        md_content = "# Test\n\n[Link](README.md)\n"
        current_file = tmp_path / "test.md"
        current_file.write_text(md_content)
        root_path = tmp_path
        book = epub.EpubBook()
        state.path_to_chapter["README.md"] = "chap_01.xhtml"

        with patch("build_epub.BeautifulSoup") as mock_bs:
            mock_bs.side_effect = BeautifulSoup

            md_to_html(md_content, current_file, root_path, book, state, logger)

            assert mock_bs.call_count == 1, (
                f"BeautifulSoup was called {mock_bs.call_count} times, expected 1"
            )


# =============================================================================
# Critical Issue 2: 文件内容重复读取
# =============================================================================


class TestFileContentCaching:
    """Tests for Critical Issue 2: File contents should be cached to avoid duplicate reads."""

    def test_extract_mermaid_returns_content_cache(
        self, tmp_path: Path, logger: logging.Logger
    ) -> None:
        """extract_all_mermaid_blocks 应该返回文件内容缓存字典。"""
        md_file = tmp_path / "test.md"
        content = "# Title\n\n```mermaid\ngraph TD\n    A --> B\n```\n"
        md_file.write_text(content)

        result = extract_all_mermaid_blocks([(md_file, "Test")], logger)

        # 新返回格式: (diagrams, file_contents)
        assert isinstance(result, tuple)
        assert len(result) == 2

        _, file_contents = result
        assert isinstance(file_contents, dict)
        assert md_file in file_contents
        assert file_contents[md_file] == content


# =============================================================================
# Critical Issue 3: mermaid_counter 竞态条件
# =============================================================================


class TestMermaidCounterThreadSafety:
    """Tests for Critical Issue 3: mermaid_counter must be thread-safe under concurrency."""

    def test_renderer_has_counter_lock(
        self, config: EPUBConfig, state: BuildState, logger: logging.Logger
    ) -> None:
        """MermaidRenderer 应该有一个 asyncio.Lock 来保护 counter。"""
        import asyncio

        renderer = MermaidRenderer(config, state, logger)
        assert hasattr(renderer, "_counter_lock")
        assert isinstance(renderer._counter_lock, asyncio.Lock)

    @pytest.mark.asyncio
    async def test_concurrent_render_produces_unique_names(
        self, config: EPUBConfig, state: BuildState, logger: logging.Logger
    ) -> None:
        """并发渲染多个 diagram 时, 图片名应该是唯一的 (无重复)。"""
        import asyncio
        from unittest.mock import AsyncMock, MagicMock, patch

        renderer = MermaidRenderer(config, state, logger)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake_png_data"

        async def mock_get(*args, **kwargs):
            await asyncio.sleep(0)  # yield control to create race condition window
            return mock_response

        mock_client = MagicMock()
        mock_client.get = mock_get
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("httpx.AsyncClient", return_value=mock_client):
            diagrams = [(i, f"graph TD\n    A{i} --> B{i}") for i in range(20)]
            await renderer.render_all(diagrams)

        img_names = [name for _, name in state.mermaid_cache.values()]
        assert len(img_names) == len(set(img_names)), (
            f"发现重复图片名: {len(img_names)} total, {len(set(img_names))} unique"
        )
        assert state.mermaid_counter == 20


# =============================================================================
# Critical Issue 4: collect_folder_files 显式栈（非递归）
# =============================================================================


class TestCollectFolderFiles:
    """Tests for collect_folder_files with explicit stack approach."""

    def test_deeply_nested_folders_no_recursion_error(
        self, tmp_path: Path
    ) -> None:
        """深层嵌套目录不应抛出 RecursionError。"""
        deep = tmp_path
        for i in range(10):
            deep = deep / f"level{i}"
            deep.mkdir()
        (deep / "deep.md").write_text("# Deep Content")

        result = collect_folder_files(tmp_path)

        titles = [title for _, title in result]
        assert any("Deep Content" in t for t in titles)

    def test_subfolder_prefix_format(self, tmp_path: Path) -> None:
        """子目录中的文件应有正确的前缀格式。"""
        sub = tmp_path / "sub-folder"
        sub.mkdir()
        (sub / "file.md").write_text("# Sub File")

        result = collect_folder_files(tmp_path)

        titles = [title for _, title in result]
        assert any(t == "Sub Folder: Sub File" for t in titles)

    def test_nested_subfolder_prefix_stack(self, tmp_path: Path) -> None:
        """多层嵌套子目录应累积正确的前缀。"""
        level0 = tmp_path / "level0"
        level0.mkdir()
        level1 = level0 / "level1"
        level1.mkdir()
        (level1 / "nested.md").write_text("# Nested")

        result = collect_folder_files(tmp_path)

        titles = [title for _, title in result]
        assert any("Level0: Level1: Nested" in t for t in titles)

    def test_readme_first_in_subfolder(self, tmp_path: Path) -> None:
        """子目录中的 README.md 应排在其他文件之前。"""
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "other.md").write_text("# Other")
        (sub / "README.md").write_text("# Readme")

        result = collect_folder_files(tmp_path)

        paths = [str(f) for f, _ in result]
        readme_idx = next(
            (i for i, p in enumerate(paths) if "README" in p), None
        )
        other_idx = next(
            (i for i, p in enumerate(paths) if "other" in p), None
        )
        assert readme_idx is not None
        assert other_idx is not None
        assert readme_idx < other_idx


# =============================================================================
# Critical Issue 5: _attr_str 新增辅助函数
# =============================================================================


class TestAttrStr:
    """Tests for _attr_str helper function."""

    def test_existing_string_attr(self) -> None:
        """正常获取字符串属性值。"""
        from bs4 import BeautifulSoup

        soup = BeautifulSoup('<img src="test.png" alt="Test">', "html.parser")
        assert _attr_str(soup.find("img"), "src") == "test.png"
        assert _attr_str(soup.find("img"), "alt") == "Test"

    def test_missing_attr_returns_default(self) -> None:
        """缺失的属性返回默认值。"""
        from bs4 import BeautifulSoup

        soup = BeautifulSoup('<img src="test.png">', "html.parser")
        assert _attr_str(soup.find("img"), "alt") == ""
        assert _attr_str(soup.find("img"), "alt", "fallback") == "fallback"

    def test_list_value_returns_first(self) -> None:
        """属性值为列表时返回第一个元素。"""
        from bs4 import BeautifulSoup

        soup = BeautifulSoup("<div></div>", "html.parser")
        tag = soup.find("div")
        tag.attrs["data-list"] = ["a", "b", "c"]  # type: ignore[assignment]
        assert _attr_str(tag, "data-list") == "a"

    def test_empty_list_returns_default(self) -> None:
        """空列表返回默认值。"""
        from bs4 import BeautifulSoup

        soup = BeautifulSoup("<div></div>", "html.parser")
        tag = soup.find("div")
        tag.attrs["data-list"] = []  # type: ignore[assignment]
        assert _attr_str(tag, "data-list", "default") == "default"


# =============================================================================
# Critical Issue 6: load_font 增加 @lru_cache
# =============================================================================


class TestLoadFontCache:
    """Tests for load_font with @lru_cache."""

    def test_caches_same_args(self, logger: logging.Logger) -> None:
        """相同参数应返回缓存的同一对象。"""
        load_font.cache_clear()
        font_paths = ("nonexistent.ttf",)

        result1 = load_font(font_paths, 12, logger)
        result2 = load_font(font_paths, 12, logger)

        assert result1 is result2

    def test_different_size_bypasses_cache(self, logger: logging.Logger) -> None:
        """不同字号应返回不同对象。"""
        load_font.cache_clear()
        font_paths = ("nonexistent.ttf",)

        result1 = load_font(font_paths, 12, logger)
        result2 = load_font(font_paths, 24, logger)

        assert result1 is not result2


# =============================================================================
# Critical Issue 7: extract_markdown_h1 逐行读取与异常处理
# =============================================================================


class TestMarkdownH1LineByLine:
    """Tests for extract_markdown_h1 with line-by-line reading."""

    def test_extract_markdown_h1_unicode_decode_error(
        self, tmp_path: Path
    ) -> None:
        """非 UTF-8 文件应返回 None 而不是抛出异常。"""
        md = tmp_path / "bad.md"
        md.write_bytes(b"\xff\xfe# Title\n")

        assert extract_markdown_h1(md) is None

    def test_extract_markdown_h1_large_file(self, tmp_path: Path) -> None:
        """大文件逐行读取应正确找到 H1。"""
        md = tmp_path / "large.md"
        lines = ["paragraph line"] * 1000
        lines[500] = "# The Real Title"
        md.write_text("\n".join(lines), encoding="utf-8")

        assert extract_markdown_h1(md) == "The Real Title"

    def test_extract_markdown_h1_no_h1(self, tmp_path: Path) -> None:
        """没有 H1 的文件应返回 None。"""
        md = tmp_path / "no_h1.md"
        md.write_text("## H2\n\nSome text\n", encoding="utf-8")

        assert extract_markdown_h1(md) is None


# =============================================================================
# Critical Issue 8: build_epub_async 使用 file_content_cache
# =============================================================================


class TestFileContentCacheIntegration:
    """Integration tests for file_content_cache in build_epub_async."""

    @pytest.mark.asyncio
    async def test_build_uses_cached_content_with_mermaid(
        self, tmp_path: Path, logger: logging.Logger
    ) -> None:
        """有 Mermaid 块时，build_epub_async 应正确使用 file_content_cache。"""
        from build_epub import build_epub_async
        from PIL import Image as PILImage
        from unittest.mock import patch

        readme = tmp_path / "README.md"
        readme.write_text(
            "# Test\n\n```mermaid\ngraph TD\n    A --> B\n```\n"
        )
        logo = tmp_path / "claude-howto-logo.png"
        PILImage.new("RGB", (100, 100)).save(logo, "PNG")

        config = EPUBConfig(
            root_path=tmp_path,
            output_path=tmp_path / "test.epub",
        )

        with patch("build_epub.MermaidRenderer.render_all") as mock_render:
            mock_render.return_value = {}

            with patch("build_epub.get_chapter_order") as mock_order:
                mock_order.return_value = [("README.md", "Introduction")]

                result = await build_epub_async(config, logger)

                assert result.exists()
                assert result.suffix == ".epub"


# =============================================================================
# Additional Coverage Tests
# =============================================================================


class TestSanitizeMermaidEdgeCases:
    """Additional tests for sanitize_mermaid edge cases."""

    def test_no_numbered_list_no_change(self) -> None:
        input_code = "A --> B --> C --> D"
        assert sanitize_mermaid(input_code) == input_code

    def test_single_quoted_number(self) -> None:
        input_code = "A['1. Item'] --> B"
        assert sanitize_mermaid(input_code) == "A['1\\. Item'] --> B"

    def test_double_quoted_number(self) -> None:
        input_code = 'A["1. Item"] --> B'
        assert sanitize_mermaid(input_code) == 'A["1\\. Item"] --> B'

    def test_no_change_for_non_list_patterns(self) -> None:
        input_code = "A[2024-01-01] --> B[v1.2.3]"
        assert sanitize_mermaid(input_code) == input_code


class TestExtractMermaidBlocksEdgeCases:
    """Tests for extract_all_mermaid_blocks edge cases."""

    def test_unicode_decode_error_handled(
        self, tmp_path: Path, logger: logging.Logger
    ) -> None:
        bad_file = tmp_path / "bad.md"
        bad_file.write_bytes(b"\xff\xfe")

        diagrams, file_contents = extract_all_mermaid_blocks(
            [(bad_file, "Test")], logger
        )

        assert diagrams == []
        assert bad_file not in file_contents


class TestChapterOrder:
    """Tests for get_chapter_order."""

    def test_returns_ordered_list(self) -> None:
        order = get_chapter_order()
        assert isinstance(order, list)
        assert len(order) > 0
        assert order[0][0] == "README.md"

    def test_all_items_are_tuples(self) -> None:
        order = get_chapter_order()
        for item in order:
            assert isinstance(item, tuple)
            assert len(item) == 2


class TestHumanizeSegment:
    """Tests for humanize_segment."""

    def test_known_folder_label(self) -> None:
        from build_epub import humanize_segment

        assert humanize_segment("code-review") == "代码审查"
        assert humanize_segment("pr-review") == "PR 审查"

    def test_unknown_segment_title_case(self) -> None:
        from build_epub import humanize_segment

        assert humanize_segment("my-folder") == "My Folder"
        assert humanize_segment("my_file") == "My File"


class TestInferMarkdownLabel:
    """Tests for infer_markdown_label."""

    def test_prefers_h1(self, tmp_path: Path) -> None:
        from build_epub import infer_markdown_label

        md = tmp_path / "test.md"
        md.write_text("# Real Title\n\nBody\n", encoding="utf-8")
        assert infer_markdown_label(md, "Fallback") == "Real Title"

    def test_falls_back_when_no_h1(self, tmp_path: Path) -> None:
        from build_epub import infer_markdown_label

        md = tmp_path / "test.md"
        md.write_text("## H2\n\nBody\n", encoding="utf-8")
        assert infer_markdown_label(md, "Fallback") == "Fallback"


class TestPrepareRootReadmeEdgeCases:
    """Tests for prepare_root_readme_for_epub edge cases."""

    def test_no_h1_returns_unchanged(self) -> None:
        content = "Some text without heading\n"
        result = prepare_root_readme_for_epub(content)
        assert result == content

    def test_no_rule_after_h1_returns_unchanged(self) -> None:
        content = "# Title\n\nSome content\n\nMore content\n"
        result = prepare_root_readme_for_epub(content)
        assert result == content


class TestChapterCollectorEdgeCases:
    """Tests for ChapterCollector edge cases."""

    def test_empty_folder_returns_empty(self, tmp_project: Path, state: BuildState) -> None:
        empty_dir = tmp_project / "empty-chapter"
        empty_dir.mkdir()
        collector = ChapterCollector(tmp_project, state)
        chapters = collector.collect_all_chapters([("empty-chapter", "Empty")])
        assert chapters == []

    def test_nonexistent_file_skipped(self, tmp_project: Path, state: BuildState) -> None:
        collector = ChapterCollector(tmp_project, state)
        chapters = collector.collect_all_chapters([("nonexistent.md", "Missing")])
        assert chapters == []


class TestCoverGenerationFallbacks:
    """Tests for cover image generation fallback paths."""

    def test_generated_cover_without_logo(self, tmp_path: Path, logger: logging.Logger) -> None:
        """Should generate a text-only cover when no logo exists."""
        config = EPUBConfig(
            root_path=tmp_path,
            output_path=tmp_path / "out.epub",
        )
        cover_bytes = create_cover_image(
            config, logger, title="Test\nGuide", subtitle="A Subtitle"
        )
        assert len(cover_bytes) > 0

    def test_generated_cover_with_logo(self, tmp_path: Path, logger: logging.Logger) -> None:
        """Should generate cover with logo when logo exists."""
        from PIL import Image as PILImage

        logo = tmp_path / "claude-howto-logo.png"
        PILImage.new("RGBA", (100, 100), (255, 255, 255, 255)).save(logo, "PNG")

        config = EPUBConfig(
            root_path=tmp_path,
            output_path=tmp_path / "out.epub",
        )
        cover_bytes = create_cover_image(config, logger)
        assert len(cover_bytes) > 0

    def test_logo_non_rgba_mode(self, tmp_path: Path, logger: logging.Logger) -> None:
        """Should handle logo in non-RGBA mode."""
        from PIL import Image as PILImage

        logo = tmp_path / "claude-howto-logo.png"
        # Create a P-mode (palette) image
        PILImage.new("P", (100, 100)).save(logo, "PNG")

        config = EPUBConfig(
            root_path=tmp_path,
            output_path=tmp_path / "out.epub",
        )
        cover_bytes = create_cover_image(config, logger)
        assert len(cover_bytes) > 0


class TestHandleSvgImage:
    """Tests for SVG image handling."""

    def test_returns_placeholder(self, logger: logging.Logger) -> None:
        result = handle_svg_image("path/to/diagram.svg", "My Diagram", logger)
        assert "svg-placeholder" in result
        assert "My Diagram" in result
        assert "path/to/diagram.svg" in result

    def test_escapes_alt_text(self, logger: logging.Logger) -> None:
        result = handle_svg_image("file.svg", "<script>alert('xss')</script>", logger)
        assert "<script>" not in result
        assert "&lt;script&gt;" in result


class TestConvertInternalLinksEdgeCases:
    """Tests for convert_internal_links edge cases."""

    def test_external_links_unchanged(self, tmp_path: Path) -> None:
        from bs4 import BeautifulSoup

        state = BuildState()
        html = '<p><a href="https://example.com">External</a></p>'
        soup = BeautifulSoup(html, "html.parser")
        result = convert_internal_links(soup, tmp_path / "test.md", tmp_path, state)
        a = result.find("a")
        assert a["href"] == "https://example.com"

    def test_mailto_links_unchanged(self, tmp_path: Path) -> None:
        from bs4 import BeautifulSoup

        state = BuildState()
        html = '<p><a href="mailto:test@example.com">Email</a></p>'
        soup = BeautifulSoup(html, "html.parser")
        result = convert_internal_links(soup, tmp_path / "test.md", tmp_path, state)
        a = result.find("a")
        assert a["href"] == "mailto:test@example.com"

    def test_hash_only_unchanged(self, tmp_path: Path) -> None:
        from bs4 import BeautifulSoup

        state = BuildState()
        html = '<p><a href="#section">Anchor</a></p>'
        soup = BeautifulSoup(html, "html.parser")
        result = convert_internal_links(soup, tmp_path / "test.md", tmp_path, state)
        a = result.find("a")
        assert a["href"] == "#section"

    def test_empty_href_unchanged(self, tmp_path: Path) -> None:
        from bs4 import BeautifulSoup

        state = BuildState()
        html = '<p><a href="">Empty</a></p>'
        soup = BeautifulSoup(html, "html.parser")
        result = convert_internal_links(soup, tmp_path / "test.md", tmp_path, state)
        a = result.find("a")
        assert a["href"] == ""

    def test_link_outside_repo_skipped(self, tmp_path: Path) -> None:
        from bs4 import BeautifulSoup

        state = BuildState()
        html = '<p><a href="../../outside.md">Outside</a></p>'
        soup = BeautifulSoup(html, "html.parser")
        result = convert_internal_links(soup, tmp_path / "a" / "b" / "test.md", tmp_path, state)
        a = result.find("a")
        assert a["href"] == "../../outside.md"

    def test_directory_link_with_readme(self, tmp_path: Path) -> None:
        from bs4 import BeautifulSoup

        state = BuildState()
        state.path_to_chapter["sub/README.md"] = "chap_01_00.xhtml"

        subdir = tmp_path / "sub"
        subdir.mkdir()
        (subdir / "README.md").write_text("# Sub")

        html = '<p><a href="sub/">Directory</a></p>'
        soup = BeautifulSoup(html, "html.parser")
        result = convert_internal_links(soup, tmp_path / "test.md", tmp_path, state)
        a = result.find("a")
        assert a["href"] == "chap_01_00.xhtml"


class TestProcessMermaidBlocks:
    """Tests for process_mermaid_blocks."""

    def test_no_mermaid_returns_unchanged(self, state: BuildState, logger: logging.Logger) -> None:
        content = "# Title\n\nNo diagrams here.\n"
        result = process_mermaid_blocks(content, epub.EpubBook(), state, logger)
        assert result == content

    def test_mermaid_replaced_when_cached(
        self, state: BuildState, logger: logging.Logger
    ) -> None:
        content = "# Title\n\n```mermaid\ngraph TD\n    A --> B\n```\n"
        state.mermaid_cache["graph TD\n    A --> B"] = (b"fake_png", "mermaid_1.png")

        result = process_mermaid_blocks(content, epub.EpubBook(), state, logger)

        assert "mermaid_1.png" in result
        assert "```mermaid" not in result


class TestCreateStylesheet:
    """Tests for create_stylesheet."""

    def test_returns_epub_item(self) -> None:
        from build_epub import create_stylesheet

        item = create_stylesheet()
        assert item.file_name == "style/nav.css"
        assert item.media_type == "text/css"
        assert "font-family: Georgia" in item.content


class TestMermaidRendererCacheHit:
    """Tests for MermaidRenderer cache hit scenarios."""

    @pytest.mark.asyncio
    async def test_fetch_single_cache_hit(
        self, config: EPUBConfig, state: BuildState, logger: logging.Logger
    ) -> None:
        """Cache hit should return cached data without network call."""
        renderer = MermaidRenderer(config, state, logger)
        renderer._semaphore = asyncio.Semaphore(1)

        # Pre-populate cache
        state.mermaid_cache["cached diagram"] = (b"cached_data", "mermaid_1.png")

        result = await renderer._fetch_single(
            None, "cached diagram", 1  # type: ignore[arg-type]
        )

        assert result is not None
        assert result[0] == "cached diagram"
        assert result[1] == (b"cached_data", "mermaid_1.png")


class TestCreateEpubWrapper:
    """Tests for create_epub synchronous wrapper."""

    def test_module_has_create_epub(self) -> None:
        from build_epub import create_epub

        assert callable(create_epub)


class TestBuildEpubAsyncEdgeCases:
    """Tests for build_epub_async edge cases."""

    @pytest.mark.asyncio
    async def test_build_with_empty_chapter_list(
        self, tmp_path: Path, logger: logging.Logger
    ) -> None:
        """Empty chapter order should still produce valid EPUB."""
        from build_epub import build_epub_async
        from PIL import Image as PILImage
        from unittest.mock import patch

        readme = tmp_path / "README.md"
        readme.write_text("# Test\n")
        logo = tmp_path / "claude-howto-logo.png"
        PILImage.new("RGB", (100, 100)).save(logo, "PNG")

        config = EPUBConfig(
            root_path=tmp_path,
            output_path=tmp_path / "test.epub",
        )

        with patch("build_epub.get_chapter_order") as mock_order:
            mock_order.return_value = []

            result = await build_epub_async(config, logger)
            assert result.exists()


# =============================================================================
# Run tests
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

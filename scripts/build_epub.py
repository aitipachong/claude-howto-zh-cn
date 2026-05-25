#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#     "ebooklib", "markdown", "beautifulsoup4", "httpx", "pillow", "tenacity",
# ]
# ///
"""
Build an EPUB from the Claude How-To markdown files.

Usage:
    Run from the repository root directory:
        ./scripts/build_epub.py

    Or run directly with Python/uv:
        uv run scripts/build_epub.py
        python scripts/build_epub.py

    Command-line options:
        --root, -r      Root directory containing markdown files (default: repo root)
        --output, -o    Output EPUB file path (default: <root>/claude-howto-guide.epub)
        --verbose, -v   Enable verbose logging
        --timeout       Timeout for API requests in seconds (default: 30)
        --max-concurrent Maximum concurrent API requests (default: 10)

    The script uses inline script dependencies (PEP 723), so uv will
    automatically install required packages in an isolated environment.

Output:
    Creates 'claude-howto-guide.epub' in the repository root directory.

Features:
    - Organizes chapters by folder structure (01-slash-commands, etc.)
    - Renders Mermaid diagrams as PNG images via Kroki.io API (async concurrent)
    - Generates a cover image from the project logo
    - Converts internal markdown links to EPUB chapter references
    - Handles SVG images by replacing with styled placeholders
    - Falls back to readable Mermaid source blocks if remote rendering fails

Requirements:
    - uv (recommended) or Python 3.10+ with dependencies installed
    - Internet connection for Mermaid diagram rendering (optional fallback included)
    - Repository structure with markdown files and claude-howto-logo.png
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import html
import itertools
import logging
import os
import re
import sys
import zlib
from dataclasses import dataclass, field
from functools import lru_cache
from io import BytesIO
from pathlib import Path

import httpx
import markdown
from bs4 import BeautifulSoup
from ebooklib import epub
from PIL import Image, ImageDraw, ImageFont, ImageOps
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

# =============================================================================
# Custom Exceptions
# =============================================================================


class EPUBBuildError(Exception):
    """Base exception for EPUB build errors."""

    pass


class MermaidRenderError(EPUBBuildError):
    """Error rendering Mermaid diagram."""

    pass


class ValidationError(EPUBBuildError):
    """Error validating input or output."""

    pass


class CoverGenerationError(EPUBBuildError):
    """Error generating cover image."""

    pass


# =============================================================================
# Module-level Constants (avoid repeated object creation)
# =============================================================================

# Pre-compiled regex patterns
_MERMAID_PATTERN = re.compile(r"```mermaid\n(.*?)```", flags=re.DOTALL)
_SANITIZE_NUMBERED_LIST_RE = re.compile(r'\[(["\']?)(\d+)\.(\s)')

# Hero template for README-to-EPUB transformation
HERO_TEMPLATE = (
    "![Claude How To 中文版 Logo](claude-howto-logo.png)\n\n"
    "> 本书由 **一起 Vibe** 基于上游仓库 "
    "[`luongnv89/claude-howto`](https://github.com/luongnv89/claude-howto) "
    "翻译与本土化整理。\n\n"
    "![一起 Vibe 小红书二维码](assets/cover/follow-qr.jpg)\n"
)

# Heading translation map for EPUB HTML generation
HEADING_MAP = {
    "Table of Contents": "目录",
    "Contributing": "参与贡献",
    "License": "许可证",
    "Troubleshooting": "故障排查",
    "Best Practices": "最佳实践",
    "Features": "功能特性",
    "Installation": "安装方式",
    "What's Included": "包含内容",
    "Requirements": "使用前提",
    "Usage": "使用方式",
    "Examples": "示例",
    "Overview": "概览",
    "Quick Start": "快速开始",
    "Output Requirements": "输出要求",
    "Summary": "总结",
}

# Media type mapping for embedded raster images
_MEDIA_TYPE_MAP = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}

# EPUB stylesheet CSS
_EPUB_CSS = """
body { font-family: Georgia, serif; line-height: 1.6; padding: 1em; }
h1 { color: #333; border-bottom: 2px solid #e67e22; padding-bottom: 0.3em; }
h2 { color: #444; margin-top: 1.5em; }
h3 { color: #555; }
code {
    background: #f4f4f4; padding: 0.2em 0.4em;
    border-radius: 3px; font-family: monospace;
}
pre { background: #f4f4f4; padding: 1em; overflow-x: auto; border-radius: 5px; }
pre code { background: none; padding: 0; }
table { border-collapse: collapse; width: 100%; margin: 1em 0; }
th, td { border: 1px solid #ddd; padding: 0.5em; text-align: left; }
th { background: #f4f4f4; }
blockquote {
    border-left: 4px solid #e67e22;
    margin: 1em 0; padding-left: 1em; color: #666;
}
a { color: #e67e22; }
img { max-width: 100%; height: auto; display: block; margin: 1em auto; }
.diagram { text-align: center; margin: 1.5em 0; }
.svg-placeholder {
    border: 1px dashed #ccc; padding: 1em;
    text-align: center; background: #f9f9f9;
    border-radius: 4px; margin: 1em 0;
}
"""


# =============================================================================
# Configuration and State
# =============================================================================


@dataclass
class EPUBConfig:
    """Configuration for EPUB generation."""

    # Paths
    root_path: Path
    output_path: Path
    cover_image_path: Path | None = None
    logo_path: Path | None = None

    # EPUB Metadata
    identifier: str = "claude-howto-zh-cn-guide"
    title: str = "Claude Code 中文全面上手指南"
    language: str = "zh"
    author: str = "claude-howto-zh-cn contributors"

    # Cover Settings
    cover_width: int = 600
    cover_height: int = 900
    cover_bg_color: tuple[int, int, int] = (26, 26, 46)
    cover_title_color: tuple[int, int, int] = (78, 205, 196)
    cover_subtitle_color: tuple[int, int, int] = (168, 178, 209)

    # Network Settings
    kroki_base_url: str = "https://kroki.io"
    request_timeout: float = 30.0
    max_retries: int = 3
    max_concurrent_requests: int = 10

    # Font paths (platform-specific)
    title_font_paths: list[str] = field(
        default_factory=lambda: [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
            "C:\\Windows\\Fonts\\arialbd.ttf",  # Windows
        ]
    )
    subtitle_font_paths: list[str] = field(
        default_factory=lambda: [
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
            "C:\\Windows\\Fonts\\arial.ttf",  # Windows
        ]
    )


@dataclass
class BuildState:
    """Mutable state for the build process."""

    mermaid_cache: dict[str, tuple[bytes, str]] = field(default_factory=dict)
    mermaid_counter: int = 0
    mermaid_added_to_book: set[str] = field(default_factory=set)
    embedded_assets: set[str] = field(default_factory=set)
    path_to_chapter: dict[str, str] = field(default_factory=dict)

    def reset(self) -> None:
        """Reset all state for a fresh build."""
        self.mermaid_cache.clear()
        self.mermaid_counter = 0
        self.mermaid_added_to_book.clear()
        self.embedded_assets.clear()
        self.path_to_chapter.clear()


@dataclass
class ChapterInfo:
    """Information about a chapter for processing."""

    file_path: Path
    display_name: str
    file_title: str
    chapter_filename: str
    is_folder_overview: bool = False
    folder_name: str | None = None


# =============================================================================
# Logging Setup
# =============================================================================


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Configure logging for the build process."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
    )
    return logging.getLogger("epub_builder")


# =============================================================================
# Input Validation
# =============================================================================


def validate_inputs(config: EPUBConfig, logger: logging.Logger) -> None:
    """Validate all inputs before starting the build."""
    errors = []

    # Check root path exists
    if not config.root_path.exists():
        errors.append(f"Root path does not exist: {config.root_path}")
    elif not config.root_path.is_dir():
        errors.append(f"Root path is not a directory: {config.root_path}")

    # Check output path is writable
    output_dir = config.output_path.parent
    if not output_dir.exists():
        errors.append(f"Output directory does not exist: {output_dir}")
    elif not os.access(output_dir, os.W_OK):
        errors.append(f"Output directory is not writable: {output_dir}")

    # Check cover image / logo if specified
    cover_image_path = config.cover_image_path or (
        config.root_path / "assets/cover/epub-cover-official.png"
    )
    logo_path = config.logo_path or (config.root_path / "claude-howto-logo.png")
    if not cover_image_path.exists() and not logo_path.exists():
        logger.warning(
            f"Cover image not found: {cover_image_path}, "
            f"and logo not found: {logo_path}. "
            f"Cover will be generated without branding assets."
        )

    # Verify at least some markdown files exist
    md_files = list(config.root_path.glob("**/*.md"))
    if not md_files:
        errors.append(f"No markdown files found in {config.root_path}")

    if errors:
        for error in errors:
            logger.error(error)
        raise ValidationError("\n".join(errors))


# =============================================================================
# Mermaid Rendering (Async with Retry)
# =============================================================================


def sanitize_mermaid(mermaid_code: str) -> str:
    """Sanitize mermaid code to avoid markdown parsing issues.

    Mermaid's markdown-in-nodes feature incorrectly interprets numbered
    lists (e.g., "1. Item") inside node labels. This escapes the period
    to prevent that.
    """
    return _SANITIZE_NUMBERED_LIST_RE.sub(r"[\1\2\\.\3", mermaid_code)


class MermaidRenderer:
    """Async renderer for Mermaid diagrams via Kroki.io API."""

    def __init__(
        self, config: EPUBConfig, state: BuildState, logger: logging.Logger
    ) -> None:
        self.config = config
        self.state = state
        self.logger = logger
        self._semaphore: asyncio.Semaphore | None = None
        self._counter_lock = asyncio.Lock()

    async def _fetch_single(
        self, client: httpx.AsyncClient, mermaid_code: str, index: int
    ) -> tuple[str, tuple[bytes, str]] | None:
        """Fetch a single Mermaid diagram with retry logic."""
        cache_key = mermaid_code.strip()

        # Check cache first
        if cache_key in self.state.mermaid_cache:
            self.logger.debug(f"Cache hit for diagram {index}")
            return cache_key, self.state.mermaid_cache[cache_key]

        # Rate limit with semaphore
        assert self._semaphore is not None
        async with self._semaphore:
            try:
                result = await self._fetch_with_retry(client, mermaid_code, index)
            except (httpx.HTTPError, MermaidRenderError) as e:
                self.logger.warning(
                    f"Skipping rendered image for Mermaid diagram {index}: "
                    f"{type(e).__name__}: {e}. Keeping source block in EPUB."
                )
                return None
            if result is None:
                self.logger.warning(
                    f"Skipping rendered image for Mermaid diagram {index} after "
                    f"{self.config.max_retries} attempts. Keeping source block in EPUB."
                )
                return None
            return cache_key, result

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        reraise=True,
    )
    async def _fetch_with_retry(
        self, client: httpx.AsyncClient, mermaid_code: str, index: int
    ) -> tuple[bytes, str] | None:
        """Fetch diagram with retry logic."""
        try:
            compressed = zlib.compress(mermaid_code.encode("utf-8"), level=9)
            encoded = base64.urlsafe_b64encode(compressed).decode("ascii")
            url = f"{self.config.kroki_base_url}/mermaid/png/{encoded}"

            self.logger.debug(f"Fetching diagram {index}...")
            response = await client.get(url, timeout=self.config.request_timeout)

            if response.status_code == 200:
                async with self._counter_lock:
                    self.state.mermaid_counter += 1
                    img_name = f"mermaid_{self.state.mermaid_counter}.png"
                result = (response.content, img_name)
                cache_key = mermaid_code.strip()
                self.state.mermaid_cache[cache_key] = result
                self.logger.info(f"Rendered diagram {index} -> {img_name}")
                return result
            else:
                self.logger.warning(
                    f"Kroki API returned {response.status_code} for diagram {index}"
                )
                raise MermaidRenderError(
                    f"Kroki API returned {response.status_code} for diagram {index}"
                )

        except httpx.TimeoutException:
            self.logger.warning(f"Timeout fetching diagram {index}, will retry...")
            raise
        except httpx.NetworkError as e:
            self.logger.warning(
                f"Network error for diagram {index}: {e}, will retry..."
            )
            raise

    async def render_all(
        self, diagrams: list[tuple[int, str]]
    ) -> dict[str, tuple[bytes, str]]:
        """Render all Mermaid diagrams concurrently."""
        self._semaphore = asyncio.Semaphore(self.config.max_concurrent_requests)
        results: dict[str, tuple[bytes, str]] = {}

        async with httpx.AsyncClient(
            follow_redirects=True,
            limits=httpx.Limits(max_connections=self.config.max_concurrent_requests),
            timeout=httpx.Timeout(self.config.request_timeout),
        ) as client:
            tasks = [
                self._fetch_single(client, sanitize_mermaid(code), idx)
                for idx, code in diagrams
            ]

            self.logger.info(
                f"Fetching {len(tasks)} Mermaid diagrams concurrently..."
            )

            # Remote rendering is best-effort;
            # unavailable diagrams remain as code blocks.
            completed = await asyncio.gather(*tasks)

            for item in completed:
                if item is None:
                    continue
                cache_key, data = item
                results[cache_key] = data

        success_count = len(results)
        self.logger.info(
            f"Successfully rendered {success_count}/{len(diagrams)} diagrams"
        )
        return results


def extract_all_mermaid_blocks(
    md_files: list[tuple[Path, str]], logger: logging.Logger
) -> tuple[list[tuple[int, str]], dict[Path, str]]:
    """Extract all unique Mermaid code blocks from markdown files.

    Returns:
        A tuple of (diagrams, file_content_cache).
        file_content_cache maps file Path to file content string,
        avoiding duplicate reads during chapter processing.
    """
    seen: set[str] = set()
    diagrams: list[tuple[int, str]] = []
    file_contents: dict[Path, str] = {}
    counter = 0

    for file_path, _ in md_files:
        try:
            content = file_path.read_text(encoding="utf-8")
            file_contents[file_path] = content
            for match in _MERMAID_PATTERN.finditer(content):
                code = match.group(1).strip()
                if code not in seen:
                    seen.add(code)
                    counter += 1
                    diagrams.append((counter, code))
        except UnicodeDecodeError as e:
            logger.warning(f"Failed to read {file_path}: {e}")

    logger.info(f"Found {len(diagrams)} unique Mermaid diagrams")
    return diagrams, file_contents


# =============================================================================
# Chapter Collection (Single-Pass)
# =============================================================================


def get_chapter_order() -> list[tuple[str, str]]:
    """Define the order of chapters based on folder structure."""
    return [
        ("README.md", "首页"),
        ("LEARNING-ROADMAP.md", "学习路线图"),
        ("QUICK_REFERENCE.md", "速查卡"),
        ("claude_concepts_guide.md", "概念总览"),
        ("01-slash-commands", "Slash Commands"),
        ("02-memory", "Memory"),
        ("03-skills", "Skills"),
        ("04-subagents", "Subagents"),
        ("05-mcp", "MCP"),
        ("06-hooks", "Hooks"),
        ("07-plugins", "Plugins"),
        ("08-checkpoints", "Checkpoints"),
        ("09-advanced-features", "Advanced Features"),
        ("10-cli", "CLI"),
        ("resources.md", "资源"),
    ]


FOLDER_LABELS = {
    "blog-draft": "博客草稿",
    "brand-voice": "品牌语气",
    "claude-md": "CLAUDE.md",
    "code-review": "代码审查",
    "doc-generator": "文档生成",
    "refactor": "重构",
    "pr-review": "PR 审查",
    "documentation": "文档插件",
    "devops-automation": "DevOps 自动化",
    "agents": "子代理",
    "commands": "命令",
    "templates": "模板",
    "references": "参考资料",
    "scripts": "脚本",
    "docs": "文档",
    "skills": "技能",
    "hooks": "Hooks",
}


def extract_markdown_h1(file_path: Path) -> str | None:
    """Extract the first H1 outside fenced code blocks."""
    try:
        with file_path.open(encoding="utf-8") as f:
            in_fence = False
            for raw_line in f:
                line = raw_line.strip()
                if line.startswith("```") or line.startswith("~~~"):
                    in_fence = not in_fence
                    continue
                if in_fence:
                    continue
                if line.startswith("# "):
                    return line[2:].strip()
    except UnicodeDecodeError:
        return None
    return None


def humanize_segment(segment: str) -> str:
    """Convert a file or folder segment into a readable label."""
    if segment in FOLDER_LABELS:
        return FOLDER_LABELS[segment]
    return segment.replace("-", " ").replace("_", " ").title()


def infer_markdown_label(file_path: Path, fallback: str) -> str:
    """Prefer the markdown H1, otherwise use the fallback label."""
    return extract_markdown_h1(file_path) or fallback


def prepare_root_readme_for_epub(md_content: str) -> str:
    """Replace the README hero block with EPUB-friendly branding."""
    lines = md_content.splitlines()
    h1_index = next((i for i, line in enumerate(lines) if line.startswith("# ")), None)
    if h1_index is None:
        return md_content
    first_rule_after_h1 = next(
        (
            i
            for i, line in enumerate(lines[h1_index + 1 :], start=h1_index + 1)
            if line.strip() == "---"
        ),
        None,
    )
    if first_rule_after_h1 is None:
        return md_content

    heading = lines[h1_index]
    remainder = "\n".join(lines[first_rule_after_h1:]).lstrip()
    return f"{heading}\n\n{HERO_TEMPLATE}\n\n{remainder}"


def collect_folder_files(folder_path: Path) -> list[tuple[Path, str]]:
    """Collect all markdown files from a folder, README first.

    Uses an explicit stack instead of recursion to avoid RecursionError
    on deeply nested directory structures.
    """
    files: list[tuple[Path, str]] = []
    # Stack of (directory_to_process, accumulated_prefix)
    stack: list[tuple[Path, str]] = [(folder_path, "")]

    while stack:
        current_path, prefix = stack.pop()

        # Get README first if it exists
        readme = current_path / "README.md"
        if readme.exists():
            label = infer_markdown_label(readme, "概览")
            files.append((readme, f"{prefix}{label}" if prefix else label))

        # Get all other markdown files
        for md_file in sorted(current_path.glob("*.md")):
            if md_file.name != "README.md":
                title = infer_markdown_label(md_file, humanize_segment(md_file.stem))
                files.append((md_file, f"{prefix}{title}" if prefix else title))

        # Queue subfolders (reverse to maintain sorted order with LIFO stack)
        subfolders = [
            subfolder
            for subfolder in sorted(current_path.iterdir(), reverse=True)
            if subfolder.is_dir() and not subfolder.name.startswith(".")
        ]
        for subfolder in subfolders:
            segment = humanize_segment(subfolder.name)
            new_prefix = f"{prefix}{segment}: " if prefix else f"{segment}: "
            stack.append((subfolder, new_prefix))

    return files


class ChapterCollector:
    """Collects and organizes chapter information in a single pass."""

    def __init__(self, root_path: Path, state: BuildState) -> None:
        self.root_path = root_path
        self.state = state

    def collect_all_chapters(
        self, chapter_order: list[tuple[str, str]]
    ) -> list[ChapterInfo]:
        """Collect all chapters and build path mapping in one pass."""
        chapters: list[ChapterInfo] = []
        chapter_num = 0

        for item, display_name in chapter_order:
            item_path = self.root_path / item

            if item_path.is_file() and item_path.suffix == ".md":
                resolved_title = infer_markdown_label(item_path, display_name)
                chapter_num += 1
                chapter_filename = f"chap_{chapter_num:02d}.xhtml"
                self.state.path_to_chapter[item] = chapter_filename

                chapters.append(
                    ChapterInfo(
                        file_path=item_path,
                        display_name=resolved_title,
                        file_title=resolved_title,
                        chapter_filename=chapter_filename,
                    )
                )

            elif item_path.is_dir():
                folder_readme = item_path / "README.md"
                resolved_display_name = (
                    infer_markdown_label(folder_readme, display_name)
                    if folder_readme.exists()
                    else display_name
                )
                folder_chapters = self._collect_folder(
                    item_path, item, resolved_display_name, chapter_num
                )
                if folder_chapters:
                    chapter_num += 1
                    chapters.extend(folder_chapters)

        return chapters

    def _collect_folder(
        self, folder_path: Path, item: str, display_name: str, base_chapter_num: int
    ) -> list[ChapterInfo]:
        """Collect chapters from a folder."""
        folder_files = collect_folder_files(folder_path)
        if not folder_files:
            return []

        chapter_num = base_chapter_num + 1
        chapters: list[ChapterInfo] = []

        # Map folder itself
        first_filename = f"chap_{chapter_num:02d}_00.xhtml"
        self.state.path_to_chapter[item] = first_filename
        self.state.path_to_chapter[item.rstrip("/")] = first_filename

        for i, (file_path, file_title) in enumerate(folder_files):
            chapter_filename = f"chap_{chapter_num:02d}_{i:02d}.xhtml"
            rel_path = str(file_path.relative_to(self.root_path))
            self.state.path_to_chapter[rel_path] = chapter_filename

            chapters.append(
                ChapterInfo(
                    file_path=file_path,
                    display_name=display_name if i == 0 else file_title,
                    file_title="概览" if i == 0 else file_title,
                    chapter_filename=chapter_filename,
                    is_folder_overview=(i == 0),
                    folder_name=display_name,
                )
            )

        return chapters


# =============================================================================
# Cover Image Generation
# =============================================================================


@lru_cache(maxsize=8)
def load_font(
    font_paths: tuple[str, ...], size: int, logger: logging.Logger
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load a font from a list of paths, with fallback to default."""
    for font_path in font_paths:
        try:
            font = ImageFont.truetype(font_path, size)
            logger.debug(f"Loaded font: {font_path}")
            return font
        except OSError:
            continue

    logger.warning("No custom fonts found, using default font")
    return ImageFont.load_default()


def _add_logo_to_cover(
    cover: Image.Image, logo_path: Path, config: EPUBConfig, logger: logging.Logger
) -> None:
    """Add logo to cover image."""
    with Image.open(logo_path) as logo:
        target_width = config.cover_width - 60
        scale_factor = target_width / logo.width
        new_height = int(logo.height * scale_factor)
        logo_scaled = logo.resize((target_width, new_height), Image.Resampling.LANCZOS)

        if logo_scaled.mode == "RGBA":
            logo_bg = Image.new("RGB", logo_scaled.size, config.cover_bg_color)
            logo_bg.paste(logo_scaled, mask=logo_scaled.split()[3])
            logo_scaled = logo_bg
        elif logo_scaled.mode != "RGB":
            logo_scaled = logo_scaled.convert("RGB")

        logo_x = (config.cover_width - logo_scaled.width) // 2
        logo_y = config.cover_height - logo_scaled.height - 80
        cover.paste(logo_scaled, (logo_x, logo_y))
        logger.debug(f"Added logo from {logo_path}")


def _draw_text_centered(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    color: tuple[int, int, int],
    canvas_width: int,
    y_start: int,
    line_spacing: int,
) -> int:
    """Draw centered multi-line text, return final y position."""
    y_offset = y_start
    for line in text.split("\n"):
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (canvas_width - text_width) // 2
        draw.text((x, y_offset), line, font=font, fill=color)
        y_offset += line_spacing
    return y_offset


def create_cover_image(
    config: EPUBConfig,
    logger: logging.Logger,
    title: str = "Claude Code\nHow-To Guide",
    subtitle: str = "Complete Guide to Claude Code Features",
) -> bytes:
    """Create a cover image with proper error handling."""
    try:
        cover_image_path = config.cover_image_path or (
            config.root_path / "assets/cover/epub-cover-official.png"
        )
        if cover_image_path.exists():
            with Image.open(cover_image_path) as cover_image:
                fitted = ImageOps.fit(
                    cover_image.convert("RGB"),
                    (config.cover_width, config.cover_height),
                    method=Image.Resampling.LANCZOS,
                )
                buffer = BytesIO()
                fitted.save(buffer, format="PNG", optimize=True)
                logger.info(f"Using prebuilt cover image: {cover_image_path}")
                return buffer.getvalue()

        cover = Image.new(
            "RGB", (config.cover_width, config.cover_height), config.cover_bg_color
        )
        draw = ImageDraw.Draw(cover)

        # Load fonts once
        title_font = load_font(tuple(config.title_font_paths), 72, logger)
        subtitle_font = load_font(tuple(config.subtitle_font_paths), 24, logger)

        # Add logo if available
        logo_path = config.logo_path or (config.root_path / "claude-howto-logo.png")
        if logo_path.exists():
            _add_logo_to_cover(cover, logo_path, config, logger)
        else:
            logger.warning("Logo not found, creating text-only cover")

        # Draw title
        y_after_title = _draw_text_centered(
            draw,
            title,
            title_font,
            config.cover_title_color,
            config.cover_width,
            y_start=120,
            line_spacing=90,
        )

        # Draw subtitle
        _draw_text_centered(
            draw,
            subtitle,
            subtitle_font,
            config.cover_subtitle_color,
            config.cover_width,
            y_start=y_after_title + 20,
            line_spacing=30,
        )

        buffer = BytesIO()
        cover.save(buffer, format="PNG", optimize=True)
        logger.info("Cover image generated successfully")
        return buffer.getvalue()

    except Exception as e:
        logger.error(f"Failed to create cover image: {e}")
        raise CoverGenerationError(f"Cover generation failed: {e}") from e


# =============================================================================
# HTML Generation
# =============================================================================


def create_chapter_html(
    display_name: str, file_title: str, html_content: str, is_overview: bool = False
) -> str:
    """Create chapter HTML with proper escaping."""
    soup = BeautifulSoup(html_content, "html.parser")
    first_h1 = soup.find("h1")
    if first_h1 is not None:
        first_h1.decompose()

    for heading in soup.find_all(["h2", "h3", "h4"]):
        text = heading.get_text(" ", strip=True)
        if text in HEADING_MAP:
            heading.clear()
            heading.append(HEADING_MAP[text])

    html_content = str(soup)
    safe_display = html.escape(display_name)
    safe_title = html.escape(file_title)

    if is_overview:
        return f"""<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="zh" xml:lang="zh">
<head>
    <meta charset="utf-8"/>
    <title>{safe_display}</title>
</head>
<body>
    <h1>{safe_display}</h1>
    {html_content}
</body>
</html>"""
    else:
        return f"""<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="zh" xml:lang="zh">
<head>
    <meta charset="utf-8"/>
    <title>{safe_title}</title>
</head>
<body>
    <h2>{safe_title}</h2>
    {html_content}
</body>
</html>"""


def handle_svg_image(src: str, alt: str, logger: logging.Logger) -> str:
    """Handle SVG images with a styled placeholder."""
    placeholder = f"""
    <div class="svg-placeholder" style="
        border: 1px dashed #ccc;
        padding: 1em;
        text-align: center;
        background: #f9f9f9;
        border-radius: 4px;
        margin: 1em 0;
    ">
        <p><em>[SVG Image: {html.escape(alt)}]</em></p>
        <p style="font-size: 0.8em; color: #666;">
            Original: {html.escape(src)}
        </p>
    </div>
    """
    logger.debug(f"Replaced SVG image: {src}")
    return placeholder


def _attr_str(tag, attr: str, default: str = "") -> str:
    """Safely get a string attribute from a BeautifulSoup tag."""
    val = tag.get(attr, default)
    if isinstance(val, list):
        return str(val[0]) if val else default
    return str(val) if val is not None else default


def embed_local_raster_images(
    soup: BeautifulSoup,
    current_file: Path,
    root_path: Path,
    book: epub.EpubBook,
    state: BuildState,
    logger: logging.Logger,
) -> None:
    """Embed local PNG/JPG images into the EPUB and rewrite their src."""
    for img in soup.find_all("img"):
        src = _attr_str(img, "src")
        if not src or src.startswith(("http://", "https://", "data:")):
            continue
        if src.endswith(".svg"):
            continue

        source_path = (current_file.parent / src).resolve()
        try:
            rel_path = source_path.relative_to(root_path)
        except ValueError:
            continue
        if not source_path.exists():
            logger.warning(f"Local image not found: {source_path}")
            continue

        asset_key = str(rel_path)
        asset_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", asset_key)
        epub_path = f"images/{asset_name}"
        if asset_key not in state.embedded_assets:
            media_type = _MEDIA_TYPE_MAP.get(source_path.suffix.lower())
            if media_type is None:
                continue
            item = epub.EpubItem(
                uid=asset_name.replace(".", "_"),
                file_name=epub_path,
                media_type=media_type,
                content=source_path.read_bytes(),
            )
            book.add_item(item)
            state.embedded_assets.add(asset_key)
            logger.debug(f"Embedded local image: {source_path}")

        img["src"] = epub_path


# =============================================================================
# Markdown Processing
# =============================================================================


def _replace_mermaid_block(
    match: re.Match[str],
    book: epub.EpubBook,
    state: BuildState,
    logger: logging.Logger,
) -> str:
    """Replace a single mermaid code block with its rendered image."""
    mermaid_code = sanitize_mermaid(match.group(1))
    cache_key = mermaid_code.strip()

    if cache_key in state.mermaid_cache:
        img_data, img_name = state.mermaid_cache[cache_key]
        # Only add image to book if not already added
        if img_name not in state.mermaid_added_to_book:
            img_item = epub.EpubItem(
                uid=img_name.replace(".", "_"),
                file_name=f"images/{img_name}",
                media_type="image/png",
                content=img_data,
            )
            book.add_item(img_item)
            state.mermaid_added_to_book.add(img_name)
        return f"\n![Diagram](images/{img_name})\n"
    else:
        logger.warning(
            "Mermaid diagram was not rendered; keeping source block in EPUB."
        )
        return match.group(0)


def process_mermaid_blocks(
    md_content: str, book: epub.EpubBook, state: BuildState, logger: logging.Logger
) -> str:
    """Find mermaid code blocks and replace with image references."""
    return _MERMAID_PATTERN.sub(
        lambda m: _replace_mermaid_block(m, book, state, logger), md_content
    )


def convert_internal_links(
    soup: BeautifulSoup, current_file: Path, root_path: Path, state: BuildState
) -> BeautifulSoup:
    """Convert markdown links to internal EPUB chapter links."""
    for link in soup.find_all("a"):
        href = _attr_str(link, "href")
        if not href or href.startswith(("http://", "https://", "mailto:", "#")):
            continue

        # Remove anchor part for path resolution
        anchor = ""
        if "#" in href:
            href, anchor = href.split("#", 1)
            anchor = "#" + anchor

        # Resolve relative path from current file's directory
        if href:
            resolved = (current_file.parent / href).resolve()
            try:
                rel_to_root = resolved.relative_to(root_path)
            except ValueError:
                # Link points outside the repo
                continue

            # Normalize the path for lookup
            lookup_path = str(rel_to_root)

            # Try various path forms for matching
            for path in (
                lookup_path,
                lookup_path.rstrip("/"),
                lookup_path + "/README.md"
                if not lookup_path.endswith(".md")
                else lookup_path,
            ):
                if path in state.path_to_chapter:
                    link["href"] = state.path_to_chapter[path] + anchor
                    break

    return soup


def md_to_html(
    md_content: str,
    current_file: Path,
    root_path: Path,
    book: epub.EpubBook,
    state: BuildState,
    logger: logging.Logger,
) -> str:
    """Convert markdown to HTML with proper styling.

    Handles:
    - Mermaid diagrams (rendered as PNG images)
    - SVG images (replaced with styled placeholders)
    - Internal links (converted to EPUB chapter references)
    - Standard markdown features
    """
    # Process mermaid blocks first (before markdown conversion)
    if current_file == root_path / "README.md":
        md_content = prepare_root_readme_for_epub(md_content)

    md_content = process_mermaid_blocks(md_content, book, state, logger)

    # Convert markdown to HTML
    html_content = markdown.markdown(
        md_content,
        extensions=[
            "tables",
            "fenced_code",
            "codehilite",
            "toc",
        ],
    )

    # Single BeautifulSoup parse for all DOM operations
    soup = BeautifulSoup(html_content, "html.parser")

    # Clean up any SVG references (they won't work in EPUB)
    for img in soup.find_all("img"):
        src = _attr_str(img, "src")
        if src.endswith(".svg"):
            alt = _attr_str(img, "alt", "Image")
            placeholder = handle_svg_image(src, alt, logger)
            img.replace_with(BeautifulSoup(placeholder, "html.parser"))

    embed_local_raster_images(soup, current_file, root_path, book, state, logger)

    # Convert internal links to EPUB chapter references (operates on same soup)
    soup = convert_internal_links(soup, current_file, root_path, state)

    return str(soup)


# =============================================================================
# EPUB Generation
# =============================================================================


def create_stylesheet() -> epub.EpubItem:
    """Create the EPUB stylesheet."""
    return epub.EpubItem(
        uid="style_nav",
        file_name="style/nav.css",
        media_type="text/css",
        content=_EPUB_CSS,
    )


async def build_epub_async(
    config: EPUBConfig,
    logger: logging.Logger,
    state: BuildState | None = None,
) -> Path:
    """Build EPUB asynchronously with concurrent diagram fetching."""
    state = state or BuildState()
    state.reset()  # Ensure clean state

    # Validate inputs
    validate_inputs(config, logger)

    # Initialize book
    book = epub.EpubBook()
    book.set_identifier(config.identifier)
    book.set_title(config.title)
    book.set_language(config.language)
    book.add_author(config.author)

    # Add cover
    logger.info("Generating cover image...")
    cover_data = create_cover_image(config, logger)
    book.set_cover("cover.png", cover_data)

    # Add CSS
    nav_css = create_stylesheet()
    book.add_item(nav_css)

    # Collect all chapters in single pass
    logger.info("Collecting chapters...")
    collector = ChapterCollector(config.root_path, state)
    chapter_infos = collector.collect_all_chapters(get_chapter_order())

    # Extract and pre-fetch all Mermaid diagrams
    logger.info("Extracting Mermaid diagrams...")
    md_files = [(ch.file_path, ch.file_title) for ch in chapter_infos]
    all_diagrams, file_content_cache = extract_all_mermaid_blocks(md_files, logger)

    if all_diagrams:
        renderer = MermaidRenderer(config, state, logger)
        await renderer.render_all(all_diagrams)

    # Process chapters
    logger.info("Processing chapters...")
    chapters: list[epub.EpubHtml] = []
    chapter_entries: list[tuple[epub.EpubHtml, str | None]] = []

    for chapter_info in chapter_infos:
        content = file_content_cache.get(chapter_info.file_path)
        if content is None:
            try:
                content = chapter_info.file_path.read_text(encoding="utf-8")
            except UnicodeDecodeError as e:
                logger.error(f"Failed to read {chapter_info.file_path}: {e}")
                raise ValidationError(
                    f"Failed to read {chapter_info.file_path}: {e}"
                ) from e

        logger.debug(
            f"Processing: {chapter_info.file_path.relative_to(config.root_path)}"
        )
        html_content = md_to_html(
            content, chapter_info.file_path, config.root_path, book, state, logger
        )

        chapter = epub.EpubHtml(
            title=chapter_info.file_title,
            file_name=chapter_info.chapter_filename,
            lang=config.language,
        )

        chapter.content = create_chapter_html(
            chapter_info.display_name,
            chapter_info.file_title,
            html_content,
            is_overview=chapter_info.is_folder_overview
            or chapter_info.folder_name is None,
        )
        chapter.add_item(nav_css)
        book.add_item(chapter)
        chapters.append(chapter)
        chapter_entries.append((chapter, chapter_info.folder_name))

    # Build TOC structure using groupby
    toc: list[epub.EpubHtml | tuple[epub.Section, list[epub.EpubHtml]]] = []
    for folder_name, group in itertools.groupby(
        chapter_entries, key=lambda entry: entry[1]
    ):
        group_chapters = [entry[0] for entry in group]
        if folder_name is None:
            toc.extend(group_chapters)
        else:
            toc.append((epub.Section(folder_name), group_chapters))

    # Set table of contents
    book.toc = toc

    # Add navigation files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Set spine
    book.spine = ["nav"] + chapters

    # Write EPUB
    logger.info(f"Writing EPUB to {config.output_path}...")
    epub.write_epub(str(config.output_path), book, {})

    logger.info(f"EPUB created successfully: {config.output_path}")
    return config.output_path


def create_epub(root_path: Path, output_path: Path, verbose: bool = False) -> Path:
    """Synchronous wrapper for backward compatibility."""
    logger = setup_logging(verbose)
    config = EPUBConfig(root_path=root_path, output_path=output_path)
    return asyncio.run(build_epub_async(config, logger))


# =============================================================================
# CLI
# =============================================================================


def main() -> int:
    """Main entry point with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description="Build an EPUB from Claude How-To markdown files."
    )
    parser.add_argument(
        "--root",
        "-r",
        type=Path,
        default=None,
        help="Root directory containing markdown files (default: repo root)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Output EPUB file path (default: <root>/claude-howto-guide.epub)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Timeout for API requests in seconds (default: 30)",
    )
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=10,
        help="Maximum concurrent API requests (default: 10)",
    )

    args = parser.parse_args()

    # Determine root path
    root = args.root
    if root is None:
        # Default to parent of scripts directory (repo root)
        root = Path(__file__).parent.parent

    root = root.resolve()
    output = args.output or (root / "claude-howto-guide.epub")
    output = output.resolve()

    logger = setup_logging(args.verbose)
    config = EPUBConfig(
        root_path=root,
        output_path=output,
        request_timeout=args.timeout,
        max_concurrent_requests=args.max_concurrent,
    )

    try:
        result = asyncio.run(build_epub_async(config, logger))
        print(f"Successfully created: {result}")
        return 0
    except EPUBBuildError as e:
        logger.error(f"Build failed: {e}")
        return 1
    except KeyboardInterrupt:
        logger.warning("Build interrupted by user")
        return 130


if __name__ == "__main__":
    sys.exit(main())

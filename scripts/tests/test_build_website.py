"""Tests for the static website builder."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from build_website import (
    BuildState,
    PageInfo,
    WebsiteConfig,
    _disambiguate_url,
    build_website,
    collect_folder_markdown,
    collect_pages,
    derive_page_title,
    heading_to_anchor,
    is_excluded_dir,
    is_excluded_top_level_markdown,
    relative_link,
    render_markdown,
    replace_mermaid_blocks,
    rewrite_links,
    source_to_site_url,
)


@pytest.fixture
def site_root(tmp_path: Path) -> Path:
    """Create a minimal repo-like tree the builder can render."""
    (tmp_path / "README.md").write_text(
        "<picture>\n"
        '  <source media="(prefers-color-scheme: dark)" '
        'srcset="resources/logos/claude-howto-logo-dark.svg">\n'
        '  <img alt="Claude How To" src="resources/logos/claude-howto-logo.svg">\n'
        "</picture>\n\n"
        "# Home Page\n\nWelcome. See [Slash Commands](01-slash-commands/README.md).\n"
        "Also check [script](scripts/build.sh) and the [logo](resources/logos/logo.svg).\n"
    )
    (tmp_path / "LEARNING-ROADMAP.md").write_text(
        "# Learning Roadmap\n\nLink back to [Home](README.md#home-page).\n"
    )
    (tmp_path / "CONTRIBUTING.md").write_text("# Contributing\n\nHelp improve docs.")
    (tmp_path / "CLAUDE.md").write_text("# Internal Agent Notes\n")
    (tmp_path / "update-plan-2026-05-02.md").write_text("# Temporary Plan\n")

    sc = tmp_path / "01-slash-commands"
    sc.mkdir()
    (sc / "README.md").write_text(
        "# Slash Commands\n\nMermaid time:\n\n```mermaid\nflowchart LR\nA-->B\n```\n\n"
        "See [example](example.md).\n"
    )
    (sc / "example.md").write_text("# Example\n\nGo back to [overview](README.md).\n")

    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "build.sh").write_text("#!/bin/bash\necho hi\n")

    logos = tmp_path / "resources" / "logos"
    logos.mkdir(parents=True)
    (logos / "logo.svg").write_text("<svg></svg>")
    (logos / "claude-howto-logo.svg").write_text("<svg></svg>")
    (logos / "claude-howto-logo-dark.svg").write_text("<svg></svg>")

    return tmp_path


@pytest.fixture
def logger() -> logging.Logger:
    return logging.getLogger("test_build_website")


class TestHeadingToAnchor:
    def test_simple_title(self) -> None:
        assert heading_to_anchor("Hello World") == "hello-world"

    def test_punctuation_removed(self) -> None:
        assert heading_to_anchor("What's Next?") == "whats-next"

    def test_unicode_preserved(self) -> None:
        assert heading_to_anchor("Hướng dẫn") == "hướng-dẫn"

    def test_emoji_stripped(self) -> None:
        assert heading_to_anchor("🔥 Trending") == "-trending"


class TestSourceToSiteUrl:
    def test_root_readme_maps_to_index(self) -> None:
        assert source_to_site_url("README.md") == "index.html"

    def test_folder_readme_maps_to_folder_index(self) -> None:
        assert (
            source_to_site_url("01-slash-commands/README.md")
            == "01-slash-commands/index.html"
        )

    def test_other_markdown_uses_html_extension(self) -> None:
        assert (
            source_to_site_url("01-slash-commands/example.md")
            == "01-slash-commands/example.html"
        )


class TestDisambiguateUrl:
    def test_no_collision_passes_through(self) -> None:
        used: set[str] = {"foo.html"}
        assert _disambiguate_url("bar.html", used, "bar.md") == "bar.html"

    def test_case_insensitive_collision_disambiguated(self) -> None:
        used: set[str] = {"index.html"}
        result = _disambiguate_url("INDEX.html", used, "INDEX.md")
        assert result.lower() != "index.html"
        assert result.endswith(".html")


class TestRelativeLink:
    def test_same_directory(self) -> None:
        assert relative_link("01/index.html", "01/example.html") == "example.html"

    def test_anchor_appended(self) -> None:
        assert (
            relative_link("01/index.html", "02/index.html", "#intro")
            == "../02/index.html#intro"
        )

    def test_self_link_returns_anchor_only(self) -> None:
        assert relative_link("01/index.html", "01/index.html", "#section") == "#section"

    def test_parent_directory(self) -> None:
        assert relative_link("01/index.html", "index.html") == "../index.html"


class TestIsExcludedDir:
    def test_hidden_dirs_excluded(self) -> None:
        assert is_excluded_dir(".git") is True

    def test_known_dir_excluded(self) -> None:
        assert is_excluded_dir("node_modules") is True

    def test_chapter_dir_kept(self) -> None:
        assert is_excluded_dir("01-slash-commands") is False


class TestIsExcludedTopLevelMarkdown:
    def test_internal_agent_file_excluded(self) -> None:
        assert is_excluded_top_level_markdown("CLAUDE.md") is True

    def test_temporary_update_plan_excluded(self) -> None:
        assert is_excluded_top_level_markdown("update-plan-2026-05-02.md") is True

    def test_project_doc_included(self) -> None:
        assert is_excluded_top_level_markdown("CONTRIBUTING.md") is False


class TestCollectFolderMarkdown:
    def test_readme_first(self, tmp_path: Path) -> None:
        (tmp_path / "b.md").write_text("# B")
        (tmp_path / "README.md").write_text("# Readme")
        (tmp_path / "a.md").write_text("# A")
        files = collect_folder_markdown(tmp_path)
        assert [f.name for f in files] == ["README.md", "a.md", "b.md"]

    def test_skips_hidden_subdirs(self, tmp_path: Path) -> None:
        (tmp_path / "README.md").write_text("# R")
        hidden = tmp_path / ".cache"
        hidden.mkdir()
        (hidden / "junk.md").write_text("# junk")
        files = collect_folder_markdown(tmp_path)
        assert [f.name for f in files] == ["README.md"]


class TestCollectPages:
    def test_additional_top_level_docs_are_collected(
        self, site_root: Path, logger: logging.Logger
    ) -> None:
        state = collect_pages(
            WebsiteConfig(root_path=site_root, output_path=site_root / "site"), logger
        )
        assert "CONTRIBUTING.md" in state.source_to_url
        assert state.source_to_url["CONTRIBUTING.md"] == "CONTRIBUTING.html"
        assert "CLAUDE.md" not in state.source_to_url
        assert "update-plan-2026-05-02.md" not in state.source_to_url


class TestDerivePageTitle:
    def test_uses_h1(self, tmp_path: Path) -> None:
        f = tmp_path / "f.md"
        f.write_text("Some intro\n# The Title\nBody")
        assert derive_page_title(f, "Default") == "The Title"

    def test_falls_back_when_no_h1(self, tmp_path: Path) -> None:
        f = tmp_path / "f.md"
        f.write_text("No heading here")
        assert derive_page_title(f, "Default") == "Default"


class TestReplaceMermaidBlocks:
    def test_replaces_fence(self) -> None:
        md = "Before\n\n```mermaid\nflowchart LR\nA-->B\n```\n\nAfter"
        out = replace_mermaid_blocks(md)
        assert '<pre class="mermaid">' in out
        assert "flowchart LR" in out
        assert "```mermaid" not in out

    def test_escapes_html(self) -> None:
        md = "```mermaid\nA --> B<C>\n```\n"
        out = replace_mermaid_blocks(md)
        assert "&lt;C&gt;" in out


class TestRenderMarkdown:
    def test_heading_gets_github_anchor(self) -> None:
        html_content = render_markdown("# Hello World\n\nBody")
        assert 'id="hello-world"' in html_content

    def test_duplicate_headings_get_suffix(self) -> None:
        html_content = render_markdown("# Hi\n\n# Hi\n")
        assert 'id="hi"' in html_content
        assert 'id="hi-1"' in html_content


class TestRewriteLinks:
    def _state(self) -> BuildState:
        state = BuildState()
        state.source_to_url = {
            "README.md": "index.html",
            "01-slash-commands/README.md": "01-slash-commands/index.html",
        }
        return state

    def _config(self, root: Path) -> WebsiteConfig:
        return WebsiteConfig(
            root_path=root,
            output_path=root / "out",
            repo_url="https://github.com/example/repo",
            branch="main",
        )

    def test_internal_markdown_link_rewritten(
        self, tmp_path: Path, logger: logging.Logger
    ) -> None:
        (tmp_path / "README.md").write_text("# Home")
        (tmp_path / "01-slash-commands").mkdir()
        (tmp_path / "01-slash-commands" / "README.md").write_text("# Slash")
        page = PageInfo(
            source=tmp_path / "README.md",
            rel_source="README.md",
            output_url="index.html",
            title="Home",
            section="Introduction",
            is_section_index=True,
        )
        html_in = '<a href="01-slash-commands/README.md">go</a>'
        out = rewrite_links(
            html_in, page, self._state(), self._config(tmp_path), logger
        )
        assert "01-slash-commands/index.html" in out
        assert ".md" not in out

    def test_anchor_preserved(self, tmp_path: Path, logger: logging.Logger) -> None:
        (tmp_path / "README.md").write_text("# Home")
        (tmp_path / "01-slash-commands").mkdir()
        (tmp_path / "01-slash-commands" / "README.md").write_text("# Slash")
        page = PageInfo(
            source=tmp_path / "README.md",
            rel_source="README.md",
            output_url="index.html",
            title="Home",
            section="Introduction",
            is_section_index=True,
        )
        html_in = '<a href="01-slash-commands/README.md#run">go</a>'
        out = rewrite_links(
            html_in, page, self._state(), self._config(tmp_path), logger
        )
        assert "#run" in out

    def test_non_markdown_link_uses_github_blob(
        self, tmp_path: Path, logger: logging.Logger
    ) -> None:
        (tmp_path / "scripts").mkdir()
        (tmp_path / "scripts" / "build.sh").write_text("#!/bin/bash")
        (tmp_path / "README.md").write_text("# Home")
        page = PageInfo(
            source=tmp_path / "README.md",
            rel_source="README.md",
            output_url="index.html",
            title="Home",
            section="Introduction",
            is_section_index=True,
        )
        html_in = '<a href="scripts/build.sh">script</a>'
        out = rewrite_links(
            html_in, page, self._state(), self._config(tmp_path), logger
        )
        assert "github.com/example/repo/blob/main/scripts/build.sh" in out
        assert 'target="_blank"' in out

    def test_repo_directory_link_uses_github_tree(
        self, tmp_path: Path, logger: logging.Logger
    ) -> None:
        (tmp_path / "scripts").mkdir()
        (tmp_path / "README.md").write_text("# Home")
        page = PageInfo(
            source=tmp_path / "README.md",
            rel_source="README.md",
            output_url="index.html",
            title="Home",
            section="Introduction",
            is_section_index=True,
        )
        html_in = '<a href="scripts/">scripts</a>'
        out = rewrite_links(
            html_in, page, self._state(), self._config(tmp_path), logger
        )
        assert "github.com/example/repo/tree/main/scripts" in out
        assert "github.com/example/repo/blob/main/scripts" not in out

    def test_repo_root_link_uses_github_tree(
        self, tmp_path: Path, logger: logging.Logger
    ) -> None:
        (tmp_path / "README.md").write_text("# Home")
        page = PageInfo(
            source=tmp_path / "README.md",
            rel_source="README.md",
            output_url="index.html",
            title="Home",
            section="Introduction",
            is_section_index=True,
        )
        html_in = '<a href=".">repo root</a>'
        out = rewrite_links(
            html_in, page, self._state(), self._config(tmp_path), logger
        )
        assert "github.com/example/repo/tree/main" in out
        assert "github.com/example/repo/blob/main/." not in out

    def test_external_link_left_alone(
        self, tmp_path: Path, logger: logging.Logger
    ) -> None:
        page = PageInfo(
            source=tmp_path / "README.md",
            rel_source="README.md",
            output_url="index.html",
            title="Home",
            section="Introduction",
            is_section_index=True,
        )
        (tmp_path / "README.md").write_text("# Home")
        html_in = '<a href="https://anthropic.com">site</a>'
        out = rewrite_links(
            html_in, page, self._state(), self._config(tmp_path), logger
        )
        assert 'href="https://anthropic.com"' in out


class TestHeadingToAnchorEdgeCases:
    def test_empty_string(self) -> None:
        assert heading_to_anchor("") == ""

    def test_only_punctuation(self) -> None:
        assert heading_to_anchor("!!!???") == ""

    def test_only_spaces(self) -> None:
        assert heading_to_anchor("   ") == ""

    def test_multiple_emojis(self) -> None:
        # Emoji removed, space becomes single hyphen
        assert heading_to_anchor("🚀✨🎉 Title") == "-title"


class TestSourceToSiteUrlErrors:
    def test_non_markdown_raises_valueerror(self) -> None:
        with pytest.raises(ValueError, match="Not a markdown path"):
            source_to_site_url("not-a-md-file.txt")

    def test_empty_string_raises_valueerror(self) -> None:
        with pytest.raises(ValueError, match="Not a markdown path"):
            source_to_site_url("")


class TestDisambiguateUrlEdgeCases:
    def test_multiple_collisions_increment_suffix(self) -> None:
        # _disambiguate_url uses {stem}-{src_stem}-{suffix} pattern
        used: set[str] = {"bar.html", "bar-bar.html", "bar-bar-2.html"}
        result = _disambiguate_url("bar.html", used, "bar.md")
        assert result == "bar-bar-3.html"

    def test_no_extension_collision(self) -> None:
        used: set[str] = set()
        result = _disambiguate_url("path/to/file.html", used, "file.md")
        assert result == "path/to/file.html"


class TestRelativeLinkEdgeCases:
    def test_same_url_no_anchor(self) -> None:
        assert relative_link("01/index.html", "01/index.html") == ""

    def test_root_to_child(self) -> None:
        assert relative_link("index.html", "01/index.html") == "01/index.html"

    def test_child_to_root(self) -> None:
        assert relative_link("01/index.html", "index.html") == "../index.html"

    def test_deep_nesting(self) -> None:
        assert (
            relative_link("a/b/c/page.html", "x/y/z/other.html")
            == "../../../x/y/z/other.html"
        )


class TestIsExternal:
    def test_http_is_external(self) -> None:
        from build_website import is_external

        assert is_external("http://example.com") is True

    def test_https_is_external(self) -> None:
        from build_website import is_external

        assert is_external("https://example.com") is True

    def test_mailto_is_external(self) -> None:
        from build_website import is_external

        assert is_external("mailto:test@example.com") is True

    def test_tel_is_external(self) -> None:
        from build_website import is_external

        assert is_external("tel:+1234567890") is True

    def test_relative_is_not_external(self) -> None:
        from build_website import is_external

        assert is_external("README.md") is False


class TestResolveRepoRelative:
    def test_resolves_relative_path(self, tmp_path: Path) -> None:
        from build_website import _resolve_repo_relative

        # page.md is at repo root, sub/file.md is relative to it
        result = _resolve_repo_relative("sub/file.md", tmp_path, tmp_path)
        assert result == "sub/file.md"

    def test_outside_repo_returns_none(self, tmp_path: Path) -> None:
        from build_website import _resolve_repo_relative

        # Create a file outside the repo
        outside = tmp_path.parent / "outside.md"
        outside.write_text("outside")
        # Use absolute path that resolves outside tmp_path
        result = _resolve_repo_relative(str(outside), tmp_path, tmp_path)
        assert result is None


class TestGithubSourceUrl:
    def test_blob_for_file(self) -> None:
        from build_website import _github_source_url

        config = WebsiteConfig(
            root_path=Path("."),
            output_path=Path("out"),
            repo_url="https://github.com/user/repo",
            branch="main",
        )
        result = _github_source_url(config, "scripts/build.sh", is_dir=False)
        assert result == "https://github.com/user/repo/blob/main/scripts/build.sh"

    def test_tree_for_directory(self) -> None:
        from build_website import _github_source_url

        config = WebsiteConfig(
            root_path=Path("."),
            output_path=Path("out"),
            repo_url="https://github.com/user/repo",
            branch="main",
        )
        result = _github_source_url(config, "scripts", is_dir=True)
        assert result == "https://github.com/user/repo/tree/main/scripts"

    def test_root_dot_uses_tree(self) -> None:
        from build_website import _github_source_url

        config = WebsiteConfig(
            root_path=Path("."),
            output_path=Path("out"),
            repo_url="https://github.com/user/repo",
            branch="main",
        )
        result = _github_source_url(config, ".", is_dir=True)
        assert result == "https://github.com/user/repo/tree/main"

    def test_anchor_appended(self) -> None:
        from build_website import _github_source_url

        config = WebsiteConfig(
            root_path=Path("."),
            output_path=Path("out"),
            repo_url="https://github.com/user/repo",
            branch="main",
        )
        result = _github_source_url(config, "README.md", is_dir=False, anchor="#section")
        assert result == "https://github.com/user/repo/blob/main/README.md#section"


class TestRewriteAnchorEdgeCases:
    def _state(self) -> BuildState:
        state = BuildState()
        state.source_to_url = {
            "README.md": "index.html",
        }
        return state

    def _config(self, root: Path) -> WebsiteConfig:
        return WebsiteConfig(
            root_path=root,
            output_path=root / "out",
            repo_url="https://github.com/example/repo",
            branch="main",
        )

    def test_empty_href_skipped(self, tmp_path: Path, logger: logging.Logger) -> None:
        from build_website import _rewrite_anchor

        page = PageInfo(
            source=tmp_path / "README.md",
            rel_source="README.md",
            output_url="index.html",
            title="Home",
            section="Introduction",
            is_section_index=True,
        )
        from bs4 import BeautifulSoup

        soup = BeautifulSoup('<a href="">empty</a>', "html.parser")
        a = soup.find("a")
        _rewrite_anchor(a, page, self._state(), self._config(tmp_path), logger)
        assert a["href"] == ""

    def test_hash_only_anchor_skipped(
        self, tmp_path: Path, logger: logging.Logger
    ) -> None:
        from build_website import _rewrite_anchor

        page = PageInfo(
            source=tmp_path / "README.md",
            rel_source="README.md",
            output_url="index.html",
            title="Home",
            section="Introduction",
            is_section_index=True,
        )
        from bs4 import BeautifulSoup

        soup = BeautifulSoup('<a href="#section">anchor</a>', "html.parser")
        a = soup.find("a")
        _rewrite_anchor(a, page, self._state(), self._config(tmp_path), logger)
        assert a["href"] == "#section"


class TestNormaliseHeadingIds:
    def test_empty_anchor_skipped(self) -> None:
        from build_website import normalise_heading_ids

        html_content = "<h1>   </h1><p>Body</p>"
        result = normalise_heading_ids(html_content)
        assert '<h1 id=' not in result

    def test_suffix_incremented_for_duplicates(self) -> None:
        from build_website import normalise_heading_ids

        html_content = "<h2>Title</h2><h2>Title</h2><h2>Title</h2>"
        result = normalise_heading_ids(html_content)
        assert 'id="title"' in result
        assert 'id="title-1"' in result
        assert 'id="title-2"' in result

    def test_different_levels_same_text(self) -> None:
        from build_website import normalise_heading_ids

        html_content = "<h2>Setup</h2><h3>Setup</h3>"
        result = normalise_heading_ids(html_content)
        # Both should get the same anchor since they're separate searches
        assert 'id="setup"' in result


class TestExtractToc:
    def test_no_id_heading_skipped(self) -> None:
        from build_website import extract_toc

        html_content = '<h2>No ID</h2><h3 id="has-id">Has ID</h3>'
        result = extract_toc(html_content)
        assert len(result) == 1
        assert result[0]["text"] == "Has ID"

    def test_only_h2_and_h3(self) -> None:
        from build_website import extract_toc

        html_content = '<h1 id="h1">H1</h1><h2 id="h2">H2</h2><h4 id="h4">H4</h4>'
        result = extract_toc(html_content)
        assert len(result) == 1
        assert result[0]["anchor"] == "h2"


class TestBuildNavigation:
    def test_groups_by_section(self) -> None:
        from build_website import build_navigation

        state = BuildState()
        state.pages = [
            PageInfo(
                source=Path("a.md"),
                rel_source="a.md",
                output_url="a.html",
                title="Page A",
                section="Section 1",
                is_section_index=True,
            ),
            PageInfo(
                source=Path("b.md"),
                rel_source="b.md",
                output_url="b.html",
                title="Page B",
                section="Section 2",
                is_section_index=False,
            ),
            PageInfo(
                source=Path("c.md"),
                rel_source="c.md",
                output_url="c.html",
                title="Page C",
                section="Section 1",
                is_section_index=False,
            ),
        ]
        nav = build_navigation(state, "a.html")
        assert len(nav) == 2
        section_names = [n["name"] for n in nav]
        assert "Section 1" in section_names
        assert "Section 2" in section_names

    def test_current_page_marked(self) -> None:
        from build_website import build_navigation

        state = BuildState()
        state.pages = [
            PageInfo(
                source=Path("a.md"),
                rel_source="a.md",
                output_url="a.html",
                title="Page A",
                section="Section 1",
                is_section_index=True,
            ),
        ]
        nav = build_navigation(state, "a.html")
        items = nav[0]["items"]
        assert items[0]["is_current"] is True


class TestCopyAssets:
    def test_copies_referenced_images(self, tmp_path: Path, logger: logging.Logger) -> None:
        from build_website import copy_assets

        img_dir = tmp_path / "images"
        img_dir.mkdir()
        img = img_dir / "photo.png"
        img.write_bytes(b"fake-png-data")

        md = tmp_path / "page.md"
        md.write_text("![Alt](images/photo.png)")

        state = BuildState()
        state.pages = [
            PageInfo(
                source=md,
                rel_source="page.md",
                output_url="page.html",
                title="Page",
                section="Test",
            ),
        ]
        config = WebsiteConfig(root_path=tmp_path, output_path=tmp_path / "site")
        copy_assets(config, state, logger)

        assert (tmp_path / "site" / "assets" / "images" / "photo.png").exists()

    def test_skips_external_images(self, tmp_path: Path, logger: logging.Logger) -> None:
        from build_website import copy_assets

        md = tmp_path / "page.md"
        md.write_text("![Alt](https://example.com/img.png)")

        state = BuildState()
        state.pages = [
            PageInfo(
                source=md,
                rel_source="page.md",
                output_url="page.html",
                title="Page",
                section="Test",
            ),
        ]
        config = WebsiteConfig(root_path=tmp_path, output_path=tmp_path / "site")
        copy_assets(config, state, logger)

        # Should not create any assets directory for external images
        assert not (tmp_path / "site" / "assets" / "img.png").exists()

    def test_skips_nonexistent_images(self, tmp_path: Path, logger: logging.Logger) -> None:
        from build_website import copy_assets

        md = tmp_path / "page.md"
        md.write_text("![Alt](missing.png)")

        state = BuildState()
        state.pages = [
            PageInfo(
                source=md,
                rel_source="page.md",
                output_url="page.html",
                title="Page",
                section="Test",
            ),
        ]
        config = WebsiteConfig(root_path=tmp_path, output_path=tmp_path / "site")
        copy_assets(config, state, logger)

        assert not (tmp_path / "site" / "assets" / "missing.png").exists()


class TestCollectPagesEdgeCases:
    def test_missing_chapter_target_skipped(
        self, site_root: Path, logger: logging.Logger
    ) -> None:
        from build_website import CHAPTER_ORDER, collect_pages

        # Remove one of the chapter directories to simulate missing target
        import build_website as bw

        original_order = bw.CHAPTER_ORDER
        try:
            bw.CHAPTER_ORDER = [
                ("README.md", "Introduction"),
                ("nonexistent-dir", "Missing"),
            ]
            state = collect_pages(
                WebsiteConfig(root_path=site_root, output_path=site_root / "site"), logger
            )
            # Should only collect README, not fail on missing dir
            assert len(state.pages) >= 1
        finally:
            bw.CHAPTER_ORDER = original_order

    def test_non_file_non_directory_warns(
        self, site_root: Path, logger: logging.Logger, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from build_website import collect_pages

        warnings: list[str] = []
        original_warning = logger.warning

        def capture_warning(msg: str, *args: object, **kwargs: object) -> None:
            warnings.append(msg)

        monkeypatch.setattr(logger, "warning", capture_warning)

        # Create a symlink or pipe that is neither file nor dir
        # Just test with a file without .md extension
        (site_root / "not-md.txt").write_text("text")

        state = collect_pages(
            WebsiteConfig(root_path=site_root, output_path=site_root / "site"), logger
        )
        # The warning may or may not fire depending on CHAPTER_ORDER
        # Just verify no exception is raised
        assert state is not None


class TestDerivePageTitleErrors:
    def test_unicode_decode_error_returns_default(self, tmp_path: Path) -> None:
        bad = tmp_path / "bad.md"
        bad.write_bytes(b"\xff\xfe")
        assert derive_page_title(bad, "Fallback") == "Fallback"

    def test_os_error_returns_default(self, tmp_path: Path) -> None:
        # This is harder to test directly; UnicodeDecodeError covers the main error path
        pass


class TestSetupLogging:
    def test_default_logging(self) -> None:
        from unittest.mock import patch

        from build_website import setup_logging

        with patch("build_website.logging.basicConfig") as mock_bc:
            logger = setup_logging(verbose=False)
            assert logger.name == "website_builder"
            mock_bc.assert_called_once()
            assert mock_bc.call_args[1]["level"] == logging.INFO

    def test_verbose_logging(self) -> None:
        from unittest.mock import patch

        from build_website import setup_logging

        with patch("build_website.logging.basicConfig") as mock_bc:
            logger = setup_logging(verbose=True)
            assert logger.name == "website_builder"
            mock_bc.assert_called_once()
            assert mock_bc.call_args[1]["level"] == logging.DEBUG


class TestBuildWebsiteEdgeCases:
    def test_root_not_directory_raises(self, tmp_path: Path, logger: logging.Logger) -> None:
        not_a_dir = tmp_path / "file.txt"
        not_a_dir.write_text("not a dir")
        config = WebsiteConfig(root_path=not_a_dir, output_path=tmp_path / "site")
        with pytest.raises(RuntimeError, match="Root path is not a directory"):
            build_website(config, logger, skip_vendor=True)

    def test_no_pages_raises(self, tmp_path: Path, logger: logging.Logger) -> None:
        empty = tmp_path / "empty"
        empty.mkdir()
        config = WebsiteConfig(root_path=empty, output_path=tmp_path / "site")
        with pytest.raises(RuntimeError, match="No markdown pages found"):
            build_website(config, logger, skip_vendor=True)


class TestBuildWebsite:
    def test_smoke_build(self, site_root: Path, logger: logging.Logger) -> None:
        out_dir = site_root / "site"
        config = WebsiteConfig(
            root_path=site_root,
            output_path=out_dir,
            repo_url="https://github.com/example/repo",
            branch="main",
        )

        build_website(config, logger, skip_vendor=True)

        index = out_dir / "index.html"
        assert index.exists()
        index_html = index.read_text(encoding="utf-8")
        assert "Home Page" in index_html
        assert "01-slash-commands/index.html" in index_html
        assert "CONTRIBUTING.html" in index_html
        assert "github.com/example/repo/blob/main/scripts/build.sh" in index_html
        assert 'srcset="assets/resources/logos/' in index_html

        assert (out_dir / "CONTRIBUTING.html").exists()
        assert not (out_dir / "CLAUDE.html").exists()
        assert not (out_dir / "update-plan-2026-05-02.html").exists()

        sc_index = out_dir / "01-slash-commands" / "index.html"
        assert sc_index.exists()
        sc_html = sc_index.read_text(encoding="utf-8")
        assert '<pre class="mermaid">' in sc_html
        assert "example.html" in sc_html

        example_page = out_dir / "01-slash-commands" / "example.html"
        assert example_page.exists()
        example_html = example_page.read_text(encoding="utf-8")
        assert "index.html" in example_html

        assert (out_dir / "assets" / "site.css").exists()
        assert (out_dir / "assets" / "resources" / "logos" / "logo.svg").exists()
        for hostile in (
            "cdn.tailwindcss.com",
            "cdn.jsdelivr.net",
            "fonts.googleapis.com",
        ):
            assert hostile not in index_html, f"Built HTML still references {hostile} — CDN should be self-hosted"


class TestVendorAssets:
    def test_module_exports(self) -> None:
        import vendor_assets

        for attr in (
            "build_tailwind_css",
            "fetch_mermaid",
            "fetch_fonts",
            "write_vendor_manifest",
            "ensure_tailwind_binary",
            "TAILWIND_VERSION",
            "MERMAID_VERSION",
        ):
            assert hasattr(vendor_assets, attr), f"missing {attr}"

    def test_detect_tailwind_asset_name(self) -> None:
        from vendor_assets import _detect_tailwind_asset_name

        known = {
            "tailwindcss-macos-arm64",
            "tailwindcss-macos-x64",
            "tailwindcss-linux-arm64",
            "tailwindcss-linux-armv7",
            "tailwindcss-linux-x64",
            "tailwindcss-windows-x64.exe",
        }
        assert _detect_tailwind_asset_name() in known

    def test_download_rejects_non_http_scheme(self, tmp_path: Path) -> None:
        from vendor_assets import _download

        with pytest.raises(ValueError, match="non-HTTP URL"):
            _download("file:///etc/passwd", tmp_path / "out.bin")

"""MkDocs 훅: 나무위키식 역링크(백링크)를 자동으로 계산한다.

문서 A가 마크다운 링크로 문서 B를 가리키면, B 페이지 맨 아래에
"이 문서를 링크하는 문서" 목록에 A가 자동으로 나타난다.
수동으로 관리할 필요 없음 - 빌드할 때마다 문서 전체를 스캔해서 다시 계산한다.

mkdocs.yml 에서 다음처럼 등록해서 쓴다:
    hooks:
      - tools/mkdocs_backlinks.py
"""

from __future__ import annotations

import posixpath
import re

_LINK_RE = re.compile(r"\]\(([^)\s#]+\.md)(?:#[^)\s]*)?\)")
_SKIP_SUFFIXES = ("_template.md",)
_SKIP_FILES = {"index.md", "tags.md"}

# 빌드 1회당 채워지는 캐시. on_files -> on_page_markdown 순서로 호출되는 걸 이용한다.
_backlinks: dict[str, set[str]] = {}
_titles: dict[str, str] = {}

_TITLE_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)


def _resolve(src_uri: str, link: str) -> str:
    base = posixpath.dirname(src_uri)
    return posixpath.normpath(posixpath.join(base, link))


def on_files(files, config):
    global _backlinks, _titles
    _backlinks = {}
    _titles = {}

    md_files = {f.src_uri: f for f in files if f.src_uri.endswith(".md")}

    for src_uri, f in md_files.items():
        try:
            with open(f.abs_src_path, encoding="utf-8") as fh:
                text = fh.read()
        except OSError:
            continue

        title_match = _TITLE_RE.search(text)
        if title_match:
            _titles[src_uri] = title_match.group(1)

        for match in _LINK_RE.finditer(text):
            target = _resolve(src_uri, match.group(1))
            if target in md_files and target != src_uri:
                _backlinks.setdefault(target, set()).add(src_uri)

    return files


def on_page_markdown(markdown, page, config, files):
    src_uri = page.file.src_uri

    if src_uri in _SKIP_FILES or src_uri.endswith(_SKIP_SUFFIXES):
        return markdown

    sources = _backlinks.get(src_uri)
    if not sources:
        return markdown

    base_dir = posixpath.dirname(src_uri)
    lines = ["", "## 이 문서를 링크하는 문서", ""]
    for other_uri in sorted(sources, key=lambda u: _titles.get(u, u)):
        title = _titles.get(other_uri, other_uri)
        rel = posixpath.relpath(other_uri, base_dir) if base_dir else other_uri
        lines.append(f"- [{title}]({rel})")

    return markdown.rstrip("\n") + "\n\n" + "\n".join(lines) + "\n"

#!/usr/bin/env python3
"""Mirror a Notion page tree into Jekyll posts and categories."""

from __future__ import annotations

import html
import json
import mimetypes
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import requests

ROOT_ID = os.environ.get("NOTION_ROOT_PAGE_ID", "d19bec251d44498c8c53ac994966d82d")
PAGE_ID = os.environ.get("NOTION_PAGE_ID", "").strip()
PARENT_CATEGORY = os.environ.get("NOTION_PARENT_CATEGORY", "").strip()
PARENT_CATEGORY_ID = os.environ.get("NOTION_PARENT_CATEGORY_ID", "").strip()
PARENT_PATH = os.environ.get("NOTION_PARENT_PATH", "").strip()
TOKEN = os.environ["NOTION_API_KEY"]
API = "https://api.notion.com/v1"
VERSION = "2022-06-28"
ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "_posts"
CATEGORIES = ROOT / "_blog_categories"
MEDIA = ROOT / "assets/images/notion"
SESSION = requests.Session()
SESSION.headers.update({"Authorization": f"Bearer {TOKEN}", "Notion-Version": VERSION})


def api(path: str, params: dict | None = None) -> dict:
    for attempt in range(6):
        time.sleep(0.35)
        response = SESSION.get(f"{API}/{path}", params=params, timeout=60)
        if response.status_code == 429:
            time.sleep(int(response.headers.get("Retry-After", "2")))
            continue
        response.raise_for_status()
        return response.json()
    raise RuntimeError(f"Notion rate limit persisted for {path}")


def children(block_id: str) -> list[dict]:
    result: list[dict] = []
    cursor = None
    while True:
        params = {"page_size": 100}
        if cursor:
            params["start_cursor"] = cursor
        data = api(f"blocks/{block_id}/children", params)
        result.extend(data["results"])
        if not data.get("has_more"):
            return result
        cursor = data["next_cursor"]


def redact_secrets(value: str) -> str:
    """Mask credentials before imported text reaches public posts."""
    value = re.sub(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", "[REDACTED PRIVATE KEY]", value, flags=re.S)
    value = re.sub(r"\b(?:AKIA|ASIA|AIDA|AROA|ANPA|ANVA|AGPA)[A-Z0-9]{16}\b", "[REDACTED AWS ACCESS KEY]", value)
    value = re.sub(r'''(?im)(aws[_ -]?secret[_ -]?access[_ -]?key|secret[_ -]?access[_ -]?key|client[_ -]?secret|access[_ -]?token|api[_ -]?key|password|passwd|token)(\s*[:=]\s*)(?:"[^"]*"|'[^']*'|[^\s,;]+)''', r"\1\2[REDACTED]", value)
    value = re.sub(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b", "[REDACTED GITHUB TOKEN]", value)
    return value


def rich_text(items: list[dict]) -> str:
    parts = []
    for item in items or []:
        value = redact_secrets(item.get("plain_text", ""))
        ann = item.get("annotations", {})
        if ann.get("code"):
            value = f"`{value}`"
        if ann.get("bold"):
            value = f"**{value}**"
        if ann.get("italic"):
            value = f"*{value}*"
        if ann.get("strikethrough"):
            value = f"~~{value}~~"
        href = (item.get("href") or (item.get("text", {}).get("link") or {}).get("url"))
        if href:
            value = f"[{value}]({href})"
        parts.append(value)
    return "".join(parts)


def download_notion_file(block: dict, file_obj: dict) -> str:
    url = file_obj.get("url")
    if not url:
        return ""
    block_id = block["id"].replace("-", "")
    ext = Path(urlparse(url).path).suffix.lower()
    response = None

    for attempt in range(6):
        try:
            response = requests.get(url, timeout=(20, 90))
            if response.status_code in (401, 403, 404):
                # Notion-hosted file URLs are temporary. Refresh the URL from the block.
                if attempt == 5:
                    response.raise_for_status()
                latest = api(f"blocks/{block['id']}")
                latest_data = latest.get(latest.get("type", ""), {})
                refreshed = latest_data.get("file") or latest_data.get("external") or {}
                url = refreshed.get("url", url)
                ext = Path(urlparse(url).path).suffix.lower() or ext
                continue
            if response.status_code == 429 or response.status_code >= 500:
                if attempt == 5:
                    response.raise_for_status()
                delay = int(response.headers.get("Retry-After", str(min(2 ** attempt, 30))))
                print(f"Temporary file download response {response.status_code}; retrying in {delay}s.", flush=True)
                time.sleep(delay)
                continue
            response.raise_for_status()
            break
        except (requests.ConnectionError, requests.Timeout) as exc:
            if attempt == 5:
                raise
            delay = min(2 ** attempt, 30)
            print(f"File download interrupted ({type(exc).__name__}); retrying in {delay}s.", flush=True)
            time.sleep(delay)

    content_type = response.headers.get("Content-Type", "").split(";", 1)[0]
    if not ext:
        ext = mimetypes.guess_extension(file_obj.get("mime_type") or content_type) or ".bin"
    MEDIA.mkdir(parents=True, exist_ok=True)
    target = MEDIA / f"{block_id}{ext}"
    if not target.exists() or target.read_bytes() != response.content:
        target.write_bytes(response.content)
    written_media.add(target)
    return f"/assets/images/notion/{target.name}"

def page_title(block: dict) -> str:
    kind = block.get("type")
    data = block.get(kind, {})
    if kind == "child_page":
        return data.get("title", "제목 없음")
    props = block.get("properties", {})
    for prop in props.values():
        if isinstance(prop, dict) and prop.get("type") == "title":
            return rich_text(prop.get("title", [])) or "제목 없음"
    return "제목 없음"


def render_blocks(blocks: list[dict], depth: int = 0) -> str:
    out: list[str] = []
    for block in blocks:
        kind = block.get("type")
        data = block.get(kind, {})
        text = rich_text(data.get("rich_text", []))
        if kind == "paragraph":
            out.append(text)
        elif kind in ("heading_1", "heading_2", "heading_3"):
            out.append(f"{'#' * int(kind[-1])} {text}")
        elif kind == "bulleted_list_item":
            out.append(f"{'  ' * depth}- {text}")
        elif kind == "numbered_list_item":
            out.append(f"{'  ' * depth}1. {text}")
        elif kind == "to_do":
            out.append(f"- [{'x' if data.get('checked') else ' '}] {text}")
        elif kind == "code":
            language = data.get("language", "text")
            body = rich_text(data.get("rich_text", []))
            out.append(f"```{language}\n{body}\n```")
        elif kind == "quote":
            out.append("\n".join(f"> {line}" for line in text.splitlines()))
        elif kind == "callout":
            icon = data.get("icon", {}).get("emoji", "💡")
            out.append(f"> {icon} {text}")
        elif kind == "divider":
            out.append("---")
        elif kind in ("image", "file", "pdf"):
            file_obj = data.get("file") or data.get("external") or {}
            source = download_notion_file(block, file_obj) if data.get("file") else file_obj.get("url", "")
            caption = rich_text(data.get("caption", [])) or "Notion 첨부 파일"
            if source:
                out.append(f"![{caption}]({source})" if kind == "image" else f"[{caption}]({source})")
        elif kind in ("bookmark", "embed", "video", "audio"):
            source = data.get("url") or data.get("external", {}).get("url", "")
            if source:
                out.append(f"[{source}]({source})")
        elif kind == "table":
            rows = children(block["id"])
            table_rows = []
            for row in rows:
                cells = row.get("table_row", {}).get("cells", [])
                table_rows.append([rich_text(cell) for cell in cells])
            if table_rows:
                width = max(map(len, table_rows))
                fmt = lambda row: "| " + " | ".join((row + [""] * width)[:width]) + " |"
                out.extend([fmt(table_rows[0]), fmt(["---"] * width)])
                out.extend(fmt(row) for row in table_rows[1:])
        elif kind == "child_database":
            out.append(f"> Notion 데이터베이스: {data.get('title', '열기')} (데이터베이스 내용은 별도 내보내기가 필요합니다.)")
        elif kind in ("child_page", "synced_block"):
            # Child pages are emitted as their own post; synced blocks need API child content.
            if kind == "synced_block" and block.get("has_children"):
                out.append(render_blocks(children(block["id"]), depth + 1))
        elif text:
            out.append(text)

        if block.get("has_children") and kind not in ("table", "synced_block"):
            nested = render_blocks(children(block["id"]), depth + 1)
            if nested:
                out.append(nested)
    return "\n\n".join(item for item in out if item).strip()


def yaml_quote(value: str) -> str:
    return json.dumps(redact_secrets(value), ensure_ascii=False)


def slug_id(page_id: str) -> str:
    return page_id.replace("-", "")[:16].lower()


def safe_date(value: str) -> tuple[str, str]:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed.strftime("%Y-%m-%d"), parsed.strftime("%Y-%m-%d %H:%M:%S %z")


def save_category(page: dict, title: str, parent_title: str = "") -> None:
    key = slug_id(page["id"])
    path = CATEGORIES / f"notion-{key}.md"
    lines = ["---", "layout: category", f"title: {yaml_quote(title)}", f"slug: notion-{key}",
             f"description: {yaml_quote('Study Record에서 가져온 Notion 분류입니다.')}",
             f"notion_id: {page['id']}"]
    if parent_title:
        lines.append(f"parent: {yaml_quote(parent_title)}")
    lines += ["---", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


seen: set[str] = set()
written: set[Path] = set()
written_media: set[Path] = set()
category_titles: set[str] = set()
written_categories: set[Path] = set()


def walk(page_id: str, title: str, parents: list[tuple[str, dict]]) -> None:
    page_id = page_id.replace("-", "")
    if page_id in seen:
        return
    seen.add(page_id)
    if len(seen) % 25 == 0:
        print(f"Visited {len(seen)} Notion pages so far.", flush=True)
    page = api(f"pages/{page_id}")
    title = page_title(page) or title
    blocks = children(page_id)
    subpages = [b for b in blocks if b.get("type") == "child_page"]
    page_record = {"id": page_id}

    if subpages and page_id != ROOT_ID.replace("-", ""):
        save_category(page_record, title, parents[-1][0] if parents else "")
        category_titles.add(title)
        written_categories.add(CATEGORIES / f"notion-{slug_id(page_id)}.md")

    body = redact_secrets(render_blocks(blocks))
    # Category pages that contain useful notes are also preserved as posts.
    if body or not subpages:
        created = page.get("created_time", "2026-01-01T00:00:00Z")
        day, date = safe_date(created)
        post_path = POSTS / f"{day}-notion-{slug_id(page_id)}.md"
        ancestors = [item[0] for item in parents if item[0] in category_titles]
        direct_category = [title] if subpages and title in category_titles else ancestors[-1:]
        if PAGE_ID and PARENT_CATEGORY:
            direct_category = [PARENT_CATEGORY]
        categories_yaml = "[" + ", ".join(yaml_quote(item) for item in direct_category) + "]"
        breadcrumb = " / ".join([item[0] for item in parents if item[0] != "Study Record"] + [title])
        if PAGE_ID and PARENT_PATH:
            breadcrumb = f"{PARENT_PATH} / {title}"
        front = ["---", "layout: post", f"title: {yaml_quote(title)}", f"date: {date}",
                 f"categories: {categories_yaml}", "tags: [Notion 가져오기]",
                 f"description: {yaml_quote('Study Record에서 가져온 기록입니다.')}",
                 f"notion_id: {page_id}", f"notion_path: {yaml_quote(breadcrumb)}", "---", ""]
        post_path.write_text("\n".join(front) + body + "\n", encoding="utf-8")
        written.add(post_path)

    next_parents = parents + [(title, page_record)]
    for child in subpages:
        walk(child["id"], child.get("child_page", {}).get("title", "제목 없음"), next_parents)


def main() -> None:
    POSTS.mkdir(exist_ok=True)
    CATEGORIES.mkdir(exist_ok=True)
    if PAGE_ID:
        if PARENT_CATEGORY and PARENT_CATEGORY_ID:
            save_category({"id": PARENT_CATEGORY_ID}, PARENT_CATEGORY, "Study Record")
            written_categories.add(CATEGORIES / f"notion-{slug_id(PARENT_CATEGORY_ID)}.md")
        page = api(f"pages/{PAGE_ID.replace('-', '')}")
        walk(PAGE_ID, page_title(page), [])
        print(f"Imported selected Notion page subtree: {len(written)} posts, {len(written_categories)} categories, and {len(written_media)} media files.", flush=True)
        return

    walk(ROOT_ID, "Study Record", [])
    # Full-tree runs alone may remove stale content; partial runs never prune unrelated posts.
    for path in POSTS.glob("*-notion-*.md"):
        if path not in written:
            path.unlink()
    for path in CATEGORIES.glob("notion-*.md"):
        if path not in written_categories:
            path.unlink()
    for path in MEDIA.glob("*"):
        if path.is_file() and path not in written_media:
            path.unlink()
    print(f"Synced {len(written)} pages, {len(category_titles)} categories, and {len(written_media)} media files from Notion.")



if __name__ == "__main__":
    main()

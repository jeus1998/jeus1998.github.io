#!/usr/bin/env python3
"""Mirror a Notion page tree into Jekyll posts and categories."""

from __future__ import annotations

import json
import mimetypes
import os
import re
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import requests

ROOT_ID = os.environ.get("NOTION_ROOT_PAGE_ID", "d19bec251d44498c8c53ac994966d82d")
PAGE_ID = os.environ.get("NOTION_PAGE_ID", "").strip()
PAGE_IDS = os.environ.get("NOTION_PAGE_IDS", "").strip()
SELECTED_PAGE_IDS = list(dict.fromkeys(
    [value.replace("-", "") for value in re.split(r"[\s,;]+", PAGE_IDS) if value]
    + ([PAGE_ID.replace("-", "")] if PAGE_ID else [])
))
TOKEN = os.environ["NOTION_API_KEY"]
API = "https://api.notion.com/v1"
VERSION = "2022-06-28"
ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "_posts"
CATEGORIES = ROOT / "_blog_categories"
MEDIA = ROOT / "assets/images/notion"
STATE_FILE = ROOT / "_data/notion_sync_state.json"
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


def search_pages() -> list[dict]:
    """Read the lightweight page index without downloading page block bodies."""
    result: list[dict] = []
    cursor = None
    while True:
        payload: dict = {"query": "", "filter": {"property": "object", "value": "page"}, "page_size": 100}
        if cursor:
            payload["start_cursor"] = cursor
        for attempt in range(6):
            time.sleep(0.35)
            response = SESSION.post(f"{API}/search", json=payload, timeout=60)
            if response.status_code == 429 or response.status_code >= 500:
                if attempt == 5:
                    response.raise_for_status()
                time.sleep(int(response.headers.get("Retry-After", str(min(2 ** attempt, 30)))))
                continue
            response.raise_for_status()
            data = response.json()
            break
        if data.get("request_status", {}).get("incomplete_reason"):
            raise RuntimeError(f"Notion returned an incomplete page index ({data['request_status']['incomplete_reason']}); refusing sync and deletion.")
        result.extend(data.get("results", []))
        if not data.get("has_more"):
            return result
        cursor = data.get("next_cursor")


def page_parent_id(page: dict) -> str:
    parent = page.get("parent", {})
    for key in ("page_id", "database_id", "data_source_id"):
        if parent.get(key):
            return parent[key].replace("-", "")
    return ""


def build_page_index() -> dict[str, dict]:
    pages = {page["id"].replace("-", ""): page for page in search_pages()}
    root_id = ROOT_ID.replace("-", "")
    if root_id not in pages:
        raise RuntimeError("Study Record root is missing from the Notion integration's page index; refusing to sync or delete posts.")

    children_by_parent: dict[str, list[str]] = {}
    for page_id, page in pages.items():
        parent_id = page_parent_id(page)
        if parent_id:
            children_by_parent.setdefault(parent_id, []).append(page_id)

    included = {root_id}
    changed = True
    while changed:
        changed = False
        for parent_id, child_ids in children_by_parent.items():
            if parent_id in included:
                before = len(included)
                included.update(child_ids)
                changed |= len(included) != before

    index: dict[str, dict] = {}
    for page_id in included:
        page = pages[page_id]
        parent_id = page_parent_id(page)
        index[page_id] = {
            "title": page_title(page),
            "parent_id": parent_id,
            "children": sorted(children_by_parent.get(page_id, [])),
            "last_edited_time": page.get("last_edited_time", ""),
        }
    for page_id, item in index.items():
        item["path"] = " / ".join([title for title, _ in page_ancestors(page_id, index)] + [item["title"]])
    return index


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {"pages": {}}
    return json.loads(STATE_FILE.read_text(encoding="utf-8"))


def save_state(index: dict[str, dict]) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps({"pages": index}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def page_ancestors(page_id: str, index: dict[str, dict]) -> list[tuple[str, dict]]:
    result = []
    parent_id = index[page_id]["parent_id"]
    while parent_id and parent_id in index:
        parent = index[parent_id]
        result.append((parent["title"], {"id": parent_id}))
        parent_id = parent["parent_id"]
    result.reverse()
    return result


def remove_post_for_page(page_id: str) -> None:
    for path in POSTS.glob("*-notion-*.md"):
        content = path.read_text(encoding="utf-8")
        match = re.search(r"^notion_id:\s*[\"']?([0-9a-f-]+)", content, flags=re.M)
        if match and match.group(1).replace("-", "") == page_id:
            path.unlink()


def remove_deleted_pages(old_pages: dict[str, dict], index: dict[str, dict]) -> None:
    missing = [page_id for page_id, item in old_pages.items() if item.get("imported") and page_id not in index]
    imported = [page_id for page_id, item in old_pages.items() if item.get("imported")]
    if len(old_pages) > 10 and len(index) < len(old_pages) // 2:
        raise RuntimeError(f"Notion page index shrank from {len(old_pages)} to {len(index)} pages; refusing deletion until integration access is checked.")
    if imported and len(missing) > max(5, len(imported) // 2):
        raise RuntimeError(f"Notion index lost {len(missing)} of {len(imported)} imported pages; refusing a mass deletion. Check integration access.")
    for page_id in missing:
        remove_post_for_page(page_id)
        (CATEGORIES / f"notion-{slug_id(page_id)}.md").unlink(missing_ok=True)


def cleanup_orphan_media() -> None:
    if not MEDIA.exists():
        return
    referenced = set()
    for post in POSTS.glob("*-notion-*.md"):
        referenced.update(re.findall(r"\]\((/assets/images/notion/[^)]+)\)", post.read_text(encoding="utf-8")))
    for path in MEDIA.iterdir():
        if path.is_file() and f"/assets/images/notion/{path.name}" not in referenced:
            path.unlink()


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
            value = markdown_wrap(value, "**")
        if ann.get("italic"):
            value = markdown_wrap(value, "*")
        if ann.get("strikethrough"):
            value = markdown_wrap(value, "~~")
        href = (item.get("href") or (item.get("text", {}).get("link") or {}).get("url"))
        if href:
            value = f"[{value}]({href})"
        parts.append(value)
    return "".join(parts)


def markdown_wrap(value: str, marker: str) -> str:
    """Keep whitespace outside Markdown emphasis delimiters."""
    leading = value[: len(value) - len(value.lstrip())]
    trailing = value[len(value.rstrip()):]
    content = value.strip()
    return f"{leading}{marker}{content}{marker}{trailing}" if content else value


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
    out: list[tuple[str, bool]] = []
    for block in blocks:
        kind = block.get("type")
        data = block.get(kind, {})
        text = rich_text(data.get("rich_text", []))
        is_list = kind in ("bulleted_list_item", "numbered_list_item", "to_do")
        if kind == "paragraph":
            rendered = text
        elif kind in ("heading_1", "heading_2", "heading_3"):
            rendered = f"{'#' * int(kind[-1])} {text}"
        elif kind == "bulleted_list_item":
            rendered = f"{'  ' * depth}- {text}"
        elif kind == "numbered_list_item":
            rendered = f"{'  ' * depth}1. {text}"
        elif kind == "to_do":
            rendered = f"{'  ' * depth}- [{'x' if data.get('checked') else ' '}] {text}"
        elif kind == "code":
            language = data.get("language", "text")
            body = rich_text(data.get("rich_text", []))
            rendered = f"```{language}\n{body}\n```"
        elif kind == "quote":
            rendered = "\n".join(f"> {line}" for line in text.splitlines())
        elif kind == "callout":
            icon = data.get("icon", {}).get("emoji", "💡")
            rendered = f"> {icon} {text}"
        elif kind == "divider":
            rendered = "---"
        elif kind in ("image", "file", "pdf"):
            file_obj = data.get("file") or data.get("external") or {}
            source = download_notion_file(block, file_obj) if data.get("file") else file_obj.get("url", "")
            caption = rich_text(data.get("caption", [])) or "Notion 첨부 파일"
            if source:
                rendered = f"![{caption}]({source})" if kind == "image" else f"[{caption}]({source})"
            else:
                rendered = ""
        elif kind in ("bookmark", "embed", "video", "audio"):
            source = data.get("url") or data.get("external", {}).get("url", "")
            rendered = f"[{source}]({source})" if source else ""
        elif kind == "table":
            rows = children(block["id"])
            table_rows = []
            for row in rows:
                cells = row.get("table_row", {}).get("cells", [])
                table_rows.append([rich_text(cell) for cell in cells])
            if table_rows:
                width = max(map(len, table_rows))
                fmt = lambda row: "| " + " | ".join(escape_table_cell(cell) for cell in (row + [""] * width)[:width]) + " |"
                rows = [fmt(table_rows[0]), fmt(["---"] * width)]
                rows.extend(fmt(row) for row in table_rows[1:])
                rendered = "\n".join(rows)
            else:
                rendered = ""
        elif kind == "child_database":
            rendered = f"> Notion 데이터베이스: {data.get('title', '열기')} (데이터베이스 내용은 별도 내보내기가 필요합니다.)"
        elif kind in ("child_page", "synced_block"):
            # Keep the original child-page content in the parent rendering too.
            if kind == "synced_block" and block.get("has_children"):
                rendered = render_blocks(children(block["id"]), depth + 1)
            else:
                rendered = ""
        elif text:
            rendered = text
        else:
            rendered = ""

        if block.get("has_children") and kind not in ("table", "synced_block"):
            nested = render_blocks(children(block["id"]), depth + 1)
            if nested:
                rendered = f"{rendered}\n{nested}" if is_list and rendered else "\n\n".join(part for part in (rendered, nested) if part)
        if rendered:
            out.append((rendered, is_list))
    parts: list[str] = []
    previous_was_list = False
    for rendered, is_list in out:
        parts.append(("\n" if previous_was_list and is_list else "\n\n") + rendered if parts else rendered)
        previous_was_list = is_list
    return "".join(parts).strip()


def escape_table_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\r\n", "<br>").replace("\n", "<br>").replace("\r", "<br>")


def yaml_quote(value: str) -> str:
    return json.dumps(redact_secrets(value), ensure_ascii=False)


def slug_id(page_id: str) -> str:
    return page_id.replace("-", "")[:16].lower()


def safe_date(value: str) -> tuple[str, str]:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed.strftime("%Y-%m-%d"), parsed.strftime("%Y-%m-%d %H:%M:%S %z")


def save_category(page: dict, title: str, parent_id: str = "") -> None:
    key = slug_id(page["id"])
    path = CATEGORIES / f"notion-{key}.md"
    lines = ["---", "layout: category", f"title: {yaml_quote(title)}", f"slug: notion-{key}",
             f"description: {yaml_quote('Study Record에서 가져온 Notion 분류입니다.')}",
             f"notion_id: {page['id']}"]
    if parent_id:
        lines.append(f"parent_notion_id: {yaml_quote(parent_id.replace('-', ''))}")
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
        save_category(page_record, title, parents[-1][1]["id"] if parents else "")
        category_titles.add(title)
        written_categories.add(CATEGORIES / f"notion-{slug_id(page_id)}.md")

    body = redact_secrets(render_blocks(blocks))
    # Category pages that contain useful notes are also preserved as posts.
    if body or not subpages:
        created = page.get("created_time", "2026-01-01T00:00:00Z")
        day, date = safe_date(created)
        post_path = POSTS / f"{day}-notion-{slug_id(page_id)}.md"
        ancestors = [item for item in parents if item[0] in category_titles]
        # Keep the top-level category in Jekyll's permalink for URL stability.
        direct_category = [ancestors[1][0] if len(ancestors) > 1 else (ancestors[0][0] if ancestors else title)]
        notion_category_ids = [item[1]["id"] for item in parents if item[0] in category_titles]
        if subpages and title in category_titles:
            notion_category_ids.append(page_id)
        categories_yaml = "[" + ", ".join(yaml_quote(item) for item in direct_category) + "]"
        breadcrumb = " / ".join([item[0] for item in parents] + [title])
        category_ids_yaml = "[" + ", ".join(yaml_quote(item) for item in notion_category_ids) + "]"
        front = ["---", "layout: post", f"title: {yaml_quote(title)}", f"date: {date}",
                 f"categories: {categories_yaml}", "tags: [Notion 가져오기]",
                 f"description: {yaml_quote('Study Record에서 가져온 기록입니다.')}",
                 f"notion_id: {page_id}", f"notion_path: {yaml_quote(breadcrumb)}",
                 f"notion_category_ids: {category_ids_yaml}", "---", "", "{% raw %}"]
        # Notion content is user-authored Markdown, so Liquid-like examples
        # (for example GitHub Actions `${{ secrets.NAME }}` or Java array braces)
        # must remain literal instead of being parsed as Jekyll template syntax.
        post_path.write_text("\n".join(front) + body + "\n{% endraw %}\n", encoding="utf-8")
        written.add(post_path)
    elif subpages:
        remove_post_for_page(page_id)

    next_parents = parents + [(title, page_record)]
    for child in subpages:
        walk(child["id"], child.get("child_page", {}).get("title", "제목 없음"), next_parents)


def main() -> None:
    POSTS.mkdir(exist_ok=True)
    CATEGORIES.mkdir(exist_ok=True)
    old_state = load_state()
    old_pages = old_state.get("pages", {})
    index = build_page_index()
    remove_deleted_pages(old_pages, index)

    # Every manual or scheduled run updates the parent-child index. A first
    # manual run establishes a baseline without importing the whole workspace.
    missing_selected = [page_id for page_id in SELECTED_PAGE_IDS if page_id not in index]
    if missing_selected:
        raise RuntimeError(f"Selected Notion pages are outside the Study Record tree or unavailable: {', '.join(missing_selected)}")
    if not old_pages and not SELECTED_PAGE_IDS:
        # A scheduled run before the first manual import records a safe baseline
        # without publishing the entire existing Study Record tree.
        save_state(index)
        print(f"Saved initial Notion index for {len(index)} pages; existing pages remain staged for manual import.", flush=True)
        return

    if ROOT_ID.replace("-", "") in SELECTED_PAGE_IDS:
        root_id = ROOT_ID.replace("-", "")
        root = index[root_id]
        save_category({"id": root_id}, root["title"])
        category_titles.add(root["title"])
        written_categories.add(CATEGORIES / f"notion-{slug_id(root_id)}.md")

    candidates = set()
    for selected_id in SELECTED_PAGE_IDS:
        candidates.add(selected_id)
        candidates.update(page_id for page_id in index if selected_id in {a[1]["id"] for a in page_ancestors(page_id, index)})
    if old_pages:
        for page_id, item in index.items():
            previous = old_pages.get(page_id)
            if previous is None or (previous.get("imported") and any(previous.get(key) != item.get(key) for key in ("title", "parent_id", "children", "last_edited_time", "path"))):
                candidates.add(page_id)
                # Child page bodies are also rendered inside their parent page,
                # so refresh imported ancestors when a descendant changes.
                for ancestor_title, ancestor in page_ancestors(page_id, index):
                    ancestor_id = ancestor["id"]
                    if old_pages.get(ancestor_id, {}).get("imported"):
                        candidates.add(ancestor_id)

    # Import only the topmost candidate in each changed subtree. New pages
    # are discovered automatically; existing unimported pages stay staged.
    roots = [page_id for page_id in candidates if not any(ancestor[1]["id"] in candidates for ancestor in page_ancestors(page_id, index))]
    for page_id in roots:
        ancestors = page_ancestors(page_id, index)
        for i, (ancestor_title, ancestor) in enumerate(ancestors):
            ancestor_id = ancestor["id"]
            if index[ancestor_id]["children"] or ancestor_id == ROOT_ID.replace("-", ""):
                parent_id = ancestors[i - 1][1]["id"] if i else ""
                save_category(ancestor, ancestor_title, parent_id)
                category_titles.add(ancestor_title)
                written_categories.add(CATEGORIES / f"notion-{slug_id(ancestor_id)}.md")
        page = api(f"pages/{page_id}")
        walk(page_id, page_title(page), ancestors)

    # Save the complete inventory, preserving the staged-import flag.
    for page_id, item in index.items():
        item["imported"] = bool(old_pages.get(page_id, {}).get("imported")) or any(page_id == root or root in {a[1]["id"] for a in page_ancestors(page_id, index)} for root in roots)
    for category_file in CATEGORIES.glob("notion-*.md"):
        category_id = category_file.stem.removeprefix("notion-")
        if category_id in index and not index[category_id]["children"] and category_id != ROOT_ID.replace("-", ""):
            category_file.unlink()
    save_state(index)
    cleanup_orphan_media()
    print(f"Synced {len(roots)} changed page groups: {len(written)} posts, {len(written_categories)} categories, and {len(written_media)} media files.", flush=True)



if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generate content/content.js from the markdown tree in content/docs.

The site (learn.html) renders markdown client-side; embedding the page text
in a JS file lets it work from file:// and GitHub Pages alike, with no
server or build framework needed.

The same file also carries a media index (media.html) — every image, GIF,
PDF and embedded video the docs reference, plus the asset files on disk that
nothing references yet.

Run from the repo root whenever content/docs changes:

    python tools/build_content.py
"""

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "content"
DOCS_DIR = CONTENT_DIR / "docs"
ASSETS_DIR = DOCS_DIR / "assets"
OUT_FILE = CONTENT_DIR / "content.js"

MEDIA_TYPES = {
    "gif": "gif",
    "png": "image", "jpg": "image", "jpeg": "image",
    "webp": "image", "avif": "image", "bmp": "image",
    "svg": "vector",
    "pdf": "pdf",
    "mp4": "video", "webm": "video", "mov": "video",
}

# Tolerates a missing trailing newline after the closing --- and front matter
# wrapped in an HTML comment (both occur in some imported source files).
FRONT_MATTER_RE = re.compile(
    r"\A(?:<!--\s*)?---\s*\n(.*?)\n---\s*(?:-->)?[ \t]*(?:\n|\Z)", re.DOTALL
)


def parse_front_matter(text):
    """Return (meta dict, body) for a markdown file."""
    meta = {}
    m = FRONT_MATTER_RE.match(text)
    if not m:
        return meta, text
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        value = value.strip().strip('"').strip("'")
        meta[key.strip()] = value
    return meta, text[m.end():]


# --------------------------------------------------------------------------
# media index
# --------------------------------------------------------------------------

FENCE_RE = re.compile(r"^```.*?^```", re.DOTALL | re.MULTILINE)
MD_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
HTML_SRC_RE = re.compile(
    r"<(?:img|embed|iframe|video|source|a)\b[^>]*?\b(?:src|href)\s*=\s*[\"']([^\"']+)[\"']",
    re.IGNORECASE,
)
MD_LINK_RE = re.compile(
    r"(?<!!)\[([^\]]*)\]\(\s*<?([^)\s>]+\.(?:%s))\b[^)]*\)" % "|".join(MEDIA_TYPES),
    re.IGNORECASE,
)
YOUTUBE_RE = re.compile(
    r"(?:youtube(?:-nocookie)?\.com/(?:embed/|watch\?v=)|youtu\.be/)([A-Za-z0-9_-]{6,})"
)


def resolve(page_rel, src):
    """Resolve a doc-relative src against the page's folder, content/-relative."""
    parts = Path(page_rel).parent.as_posix().split("/") + src.split("/")
    stack = []
    for part in parts:
        if part in ("", "."):
            continue
        if part == "..":
            if stack:
                stack.pop()
        else:
            stack.append(part)
    return "/".join(stack)


def media_type(src):
    ext = src.rsplit(".", 1)[-1].lower() if "." in src.rsplit("/", 1)[-1] else ""
    return MEDIA_TYPES.get(ext, ""), ext


def scan_media(page_rel, body):
    """Yield (key, entry-seed, use) for every media reference on a page."""
    text = FENCE_RE.sub(" ", body)
    refs = []
    for m in MD_IMAGE_RE.finditer(text):
        refs.append((m.group(2).strip(), m.group(1).strip()))
    for m in MD_LINK_RE.finditer(text):
        refs.append((m.group(2).strip(), m.group(1).strip()))
    for m in HTML_SRC_RE.finditer(text):
        refs.append((m.group(1).strip(), ""))

    for src, alt in refs:
        if not src or src.startswith(("#", "data:", "mailto:")):
            continue

        video = YOUTUBE_RE.search(src)
        if video:
            vid = video.group(1)
            yield ("yt:" + vid, {
                "src": "https://www.youtube.com/watch?v=" + vid,
                "name": vid,
                "type": "video",
                "ext": "youtube",
                "local": False,
                "thumb": "https://i.ytimg.com/vi/%s/hqdefault.jpg" % vid,
            }, alt)
            continue

        kind, ext = media_type(src.split("?")[0].split("#")[0])
        if not kind:
            continue

        remote = bool(re.match(r"^[a-z]+:", src, re.IGNORECASE)) or src.startswith("//")
        if remote:
            yield (src, {
                "src": src,
                "name": src.split("?")[0].rstrip("/").rsplit("/", 1)[-1],
                "type": kind,
                "ext": ext,
                "local": False,
                "thumb": src,
            }, alt)
        else:
            rel = resolve(page_rel, src.split("?")[0].split("#")[0])
            yield (rel, {
                "src": rel,
                "name": rel.rsplit("/", 1)[-1],
                "type": kind,
                "ext": ext,
                "local": True,
                "thumb": rel,
            }, alt)


def nearest_section(page_rel, pages):
    """Title of the closest index.md above a page (its section heading)."""
    parts = Path(page_rel).parent.as_posix().split("/")
    while parts and parts != ["."]:
        candidate = "/".join(parts) + "/index.md"
        if candidate in pages and candidate != page_rel:
            return pages[candidate]["title"]
        parts.pop()
    # a top-level index page is its own section
    return pages[page_rel]["parent"] or pages[page_rel]["title"]


def build_media(pages):
    items = {}

    def seed(key, entry):
        if key not in items:
            entry = dict(entry)
            entry["uses"] = []
            items[key] = entry
        return items[key]

    for page_rel in sorted(pages):
        page = pages[page_rel]
        for key, entry, alt in scan_media(page_rel, page["body"]):
            item = seed(key, entry)
            if any(u["page"] == page_rel for u in item["uses"]):
                if alt and not item["uses"][-1].get("alt"):
                    item["uses"][-1]["alt"] = alt
                continue
            item["uses"].append({
                "page": page_rel,
                "title": page["title"],
                "section": nearest_section(page_rel, pages),
                "alt": alt,
            })

    # every asset on disk, so files nothing references still show up
    if ASSETS_DIR.exists():
        for path in sorted(ASSETS_DIR.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(CONTENT_DIR).as_posix()
            kind, ext = media_type(rel)
            if not kind:
                continue
            seed(rel, {
                "src": rel, "name": path.name, "type": kind,
                "ext": ext, "local": True, "thumb": rel,
            })

    for key, item in items.items():
        if item["local"]:
            path = CONTENT_DIR / item["src"]
            item["missing"] = not path.is_file()
            item["bytes"] = path.stat().st_size if not item["missing"] else 0

    order = {"image": 0, "gif": 1, "vector": 2, "video": 3, "pdf": 4}
    return sorted(
        items.values(),
        key=lambda i: (order.get(i["type"], 9), i["name"].lower()),
    )


def main():
    pages = {}
    for path in sorted(DOCS_DIR.rglob("*.md")):
        rel = path.relative_to(CONTENT_DIR).as_posix()
        text = path.read_text(encoding="utf-8")
        meta, body = parse_front_matter(text)

        if meta.get("draft", "").lower() in {"true", "yes", "1"}:
            continue

        try:
            order = int(meta.get("nav_order", "999"))
        except ValueError:
            order = 999

        pages[rel] = {
            "title": meta.get("title") or path.stem,
            "parent": meta.get("parent") or None,
            "order": order,
            "body": body.strip(),
        }

    media = build_media(pages)

    payload = json.dumps({"pages": pages}, ensure_ascii=False, indent=None)
    media_payload = json.dumps({"items": media}, ensure_ascii=False, indent=None)
    OUT_FILE.write_text(
        "// GENERATED by tools/build_content.py — do not edit by hand.\n"
        "// Edit the markdown in content/docs/ and rerun the script.\n"
        f"window.SITE_CONTENT = {payload};\n"
        f"window.SITE_MEDIA = {media_payload};\n",
        encoding="utf-8",
    )

    unused = sum(1 for m in media if m["local"] and not m["uses"])
    broken = [m for m in media if m.get("missing")]
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)} with {len(pages)} pages "
          f"and {len(media)} media items ({unused} unused).")
    for m in broken:
        pages_using = ", ".join(u["page"] for u in m["uses"])
        print(f"  ! missing file: {m['src']}  (referenced by {pages_using})")


if __name__ == "__main__":
    main()

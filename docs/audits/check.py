#!/usr/bin/env python3
"""Validate the docs/ tree: relative links, front matter, markers, house style.

Run from the repository root:

    python docs/audits/check.py

Exit code 1 if anything fails. Add checks here rather than eyeballing the tree.
"""

import re
import sys
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent
FM_FIELDS = ["id", "title", "section", "priority", "audience", "status"]
STATUSES = {"draft", "review", "ready", "blocked"}
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
MARKER_RE = re.compile(r"\[(DECISION|INFO) REQUIRED:([^\]]*)\]")

problems = []
markers = []
pages = sorted(DOCS.rglob("*.md"))

for page in pages:
    rel = page.relative_to(DOCS).as_posix()
    raw = page.read_text(encoding="utf-8")
    # Fenced blocks hold examples and diagram source, not real prose or links.
    text = re.sub(r"^```.*?^```", "", raw, flags=re.S | re.M)

    if "—" in text:
        problems.append(f"{rel}: em dash present")

    if page.parent.name == "competitor" and page.name != "index.md":
        if not raw.startswith("---\n"):
            problems.append(f"{rel}: missing front matter")
        else:
            block = raw.split("---", 2)[1]
            keys = [ln.split(":", 1)[0].strip() for ln in block.strip().splitlines()]
            if keys != FM_FIELDS:
                problems.append(f"{rel}: front matter keys {keys} != {FM_FIELDS}")
            status = re.search(r"^status:\s*(\S+)", block, re.M)
            if status and status.group(1) not in STATUSES:
                problems.append(f"{rel}: bad status {status.group(1)}")

    for kind, body in MARKER_RE.findall(text):
        markers.append((rel, kind, " ".join(body.split())))

    for href in LINK_RE.findall(text):
        if href.startswith(("http://", "https://", "#", "mailto:")):
            continue
        target = (page.parent / href.split("#", 1)[0]).resolve()
        if not target.exists():
            problems.append(f"{rel}: broken link -> {href}")

print(f"pages checked: {len(pages)}")
print(f"markers found: {len(markers)}")
for rel, kind, body in markers:
    print(f"  {rel} [{kind}] {body[:100]}")

if problems:
    print(f"\nFAIL ({len(problems)})")
    for p in problems:
        print(f"  {p}")
    sys.exit(1)

print("\nOK")

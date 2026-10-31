"""Offline structural checks; no automated check establishes copyright status."""
import datetime
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote, urlsplit
from catalogue import CATEGORIES, RIGHTS, START, END, render, slug

ROOT = Path(__file__).resolve().parents[1]
FIELDS = {"id", "title", "creator", "year", "category", "description", "institution",
          "item_url", "rights_status", "rights_url", "rights_evidence", "formats",
          "region", "tags", "date_verified"}
REQUIRED_FILES = [
    "README.md", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md", "LICENSE",
    "COPYRIGHT_AND_RIGHTS.md", "EDITORIAL_GUIDELINES.md", "CHANGELOG.md", ".gitignore",
    ".github/ISSUE_TEMPLATE/suggest-a-treasure.yml",
    ".github/ISSUE_TEMPLATE/report-a-broken-link.yml",
    ".github/PULL_REQUEST_TEMPLATE.md", ".github/workflows/validate.yml",
    "data/treasures.json", "data/schema.json", "scripts/validate.py", "assets/banner.svg",
]


def valid_url(value):
    if not isinstance(value, str) or re.search(r"[\s<>]", value):
        return False
    try:
        p = urlsplit(value)
        return p.scheme == "https" and bool(p.hostname) and not p.username and not p.password and p.port in (None, 443)
    except ValueError:
        return False


def validate_entries(entries):
    errors, ids, urls = [], set(), set()
    if not isinstance(entries, list) or not entries:
        return ["Catalogue must be a nonempty JSON array"]
    for i, e in enumerate(entries):
        label = f"Entry {i + 1}"
        if not isinstance(e, dict):
            errors.append(label + ": expected object")
            continue
        if set(e) != FIELDS:
            errors.append(label + f": unexpected/missing fields: {sorted(set(e) ^ FIELDS)}")
        for field in FIELDS - {"creator", "year", "formats", "tags"}:
            if not isinstance(e.get(field), str) or not e[field].strip():
                errors.append(label + ": empty/invalid " + field)
        for field in ("creator", "year"):
            if e.get(field) is not None and (not isinstance(e[field], str) or not e[field].strip()):
                errors.append(label + ": invalid " + field)
        for field in ("formats", "tags"):
            a = e.get(field)
            if not isinstance(a, list) or any(not isinstance(v, str) or not v.strip() for v in a):
                errors.append(label + ": invalid " + field)
            elif len(set(a)) != len(a):
                errors.append(label + ": repeated " + field)
            elif field == "tags" and any(re.search(r"[-_]|^\s|\s$", v) for v in a):
                errors.append(label + ": tags use spaces, not hyphens or underscores")
        ident = e.get("id")
        if not isinstance(ident, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", ident):
            errors.append(label + ": invalid id")
        elif ident in ids:
            errors.append(label + ": duplicate id")
        else:
            ids.add(ident)
        for field in ("item_url", "rights_url"):
            if not valid_url(e.get(field)):
                errors.append(label + ": invalid " + field)
        url = e.get("item_url")
        if isinstance(url, str):
            normalized = url.split("#")[0].rstrip("/")
            if normalized in urls:
                errors.append(label + ": duplicate item URL")
            urls.add(normalized)
        if e.get("category") not in CATEGORIES:
            errors.append(label + ": unrecognized category")
        if e.get("rights_status") not in RIGHTS:
            errors.append(label + ": unrecognized rights label")
        try:
            date = datetime.date.fromisoformat(e.get("date_verified", ""))
            if date > datetime.date.today():
                errors.append(label + ": future verification date")
        except (TypeError, ValueError):
            errors.append(label + ": invalid verification date")
    present = {e["category"] for e in entries
               if isinstance(e, dict) and isinstance(e.get("category"), str)}
    missing = set(CATEGORIES) - present
    if missing:
        errors.append("Categories without entries: " + ", ".join(sorted(missing)))
    return errors


def check_headline_counts(readme, entries):
    match = re.search(r"\*\*(\d+) individually researched treasures in (\d+) categories\*\*", readme)
    if not match:
        return ["README headline count sentence not found"]
    if (int(match[1]), int(match[2])) != (len(entries), len(CATEGORIES)):
        return [f"README headline says {match[1]} treasures in {match[2]} categories; data has {len(entries)} in {len(CATEGORIES)}"]
    return []


def anchors(text):
    result = set(re.findall(r'<a id="([^"]+)"', text))
    counts = {}
    for heading in re.findall(r"^#{1,6} (.+?)\s*$", text, re.M):
        base = slug(heading)
        n = counts.get(base, 0)
        result.add(base + (f"-{n}" if n else ""))
        counts[base] = n + 1
    return result


def check_links(root):
    errors = []
    for path in root.rglob("*.md"):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^\s)]+)\)", text):
            if urlsplit(target).scheme:
                continue
            name, _, fragment = target.partition("#")
            dest = (path.parent / unquote(name)).resolve() if name else path.resolve()
            if not dest.is_relative_to(root.resolve()):
                errors.append(f"{path.name}: link escapes repository: {target}")
            elif not dest.exists():
                errors.append(f"{path.name}: missing link: {target}")
            elif fragment and dest.suffix == ".md" and unquote(fragment) not in anchors(dest.read_text(encoding="utf-8")):
                errors.append(f"{path.name}: missing anchor: {target}")
    return errors


def main():
    errors = [f"Missing or empty required file: {name}" for name in REQUIRED_FILES
              if not (ROOT / name).is_file() or not (ROOT / name).stat().st_size]
    try:
        entries = json.loads((ROOT / "data/treasures.json").read_text(encoding="utf-8"))
        schema = json.loads((ROOT / "data/schema.json").read_text(encoding="utf-8"))
        errors += validate_entries(entries)
        if schema["items"]["properties"]["category"]["enum"] != CATEGORIES or schema["items"]["properties"]["rights_status"]["enum"] != RIGHTS:
            errors.append("Schema enums differ from validator")
        if set(schema["items"]["required"]) != FIELDS:
            errors.append("Schema required fields differ from validator")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        if readme.count(START) != 1 or readme.count(END) != 1:
            errors.append("README catalogue markers missing or repeated")
        else:
            errors += check_headline_counts(readme, entries)
        if readme.count(START) == 1 and readme.count(END) == 1 and not errors and readme.split(START, 1)[1].split(END, 1)[0] != render(entries).split(START, 1)[1].split(END, 1)[0]:
            errors.append("README differs from data: run python scripts/build_readme.py")
        errors += check_links(ROOT)
        svg = ET.parse(ROOT / "assets/banner.svg")
        if svg.getroot().tag != "{http://www.w3.org/2000/svg}svg":
            errors.append("Banner is not an SVG")
    except (OSError, ValueError, KeyError, ET.ParseError) as exc:
        errors.append(str(exc))
    if errors:
        print("Validation failed:\n" + "\n".join("- " + e for e in errors))
        return 1
    print(f"PASS: {len(entries)} entries; all 12 categories; fields, rights evidence, dates, duplicates, README parity, local links, anchors and SVG XML checked.")
    print("External reachability and copyright conclusions require separate review.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

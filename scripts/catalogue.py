"""Shared, deterministic Markdown rendering. Uses only the standard library."""
import re

CATEGORIES = [
    "Rare Books & Manuscripts", "Historical Maps & Atlases",
    "Astronomy & Celestial Charts", "Botanical & Zoological Illustrations",
    "Scientific Discoveries & Publications", "Art, Prints & Illustrations",
    "Historical Photography", "Literature & Poetry", "Music & Musical Scores",
    "Engineering, Inventions & Technical Drawings",
    "Ancient Civilizations & Historical Documents", "Unusual & Forgotten Treasures",
]
RIGHTS = ["CC0", "Public Domain", "Public Domain — United States"]
START = "<!-- BEGIN GENERATED CATALOGUE -->"
END = "<!-- END GENERATED CATALOGUE -->"


def slug(text):
    return re.sub(r"[^\w\- ]", "", text.lower()).replace(" ", "-")


def escape(text):
    return re.sub(r"([\\\[\]*_`<>])", r"\\\1", text)


def render(entries):
    lines = [START]
    for category in CATEGORIES:
        lines += ["", "## " + category, ""]
        for e in entries:
            if e["category"] != category:
                continue
            creator = escape(e["creator"]) if e["creator"] else "Creator unrecorded"
            year = escape(e["year"]) if e["year"] else "Date unrecorded"
            lines += [
                f'<a id="{e["id"]}"></a>',
                f'**[{escape(e["title"])}]({e["item_url"]})** — {creator}; {year}. {escape(e["description"])}  ',
                f'*Collection:* {escape(e["institution"])} · *Rights:* {e["rights_status"]} · [Rights evidence]({e["rights_url"]})  ',
                f'*Access:* {escape(", ".join(e["formats"])) if e["formats"] else "See the institutional record for available formats."}',
                "",
            ]
    lines += [END]
    return "\n".join(lines)

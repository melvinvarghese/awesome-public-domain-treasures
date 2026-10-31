"""Regenerate the marked catalogue in README.md from structured data."""
import json
from pathlib import Path
from catalogue import START, END, render

ROOT = Path(__file__).resolve().parents[1]


def main():
    path = ROOT / "README.md"
    text = path.read_text(encoding="utf-8")
    entries = json.loads((ROOT / "data/treasures.json").read_text(encoding="utf-8"))
    before, remaining = text.split(START, 1)
    _, after = remaining.split(END, 1)
    path.write_text(before + render(entries) + after, encoding="utf-8")


if __name__ == "__main__":
    main()

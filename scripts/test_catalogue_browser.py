import json
import re
import subprocess
import unittest
from html.parser import HTMLParser
from pathlib import Path
from catalogue import START, END, render

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "index.html"
JS = ROOT / "assets" / "catalogue.js"
CSS = ROOT / "assets" / "catalogue.css"
DATA = ROOT / "data" / "treasures.json"


class PageProbe(HTMLParser):
    VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input",
                 "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.elements = []
        self.links = []
        self.text = []
        self.noscript_links = []
        self.error_links = []
        self._stack = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        self.elements.append((tag, attributes))
        if tag == "a":
            href = attributes.get("href", "")
            if any(parent_tag == "noscript" for parent_tag, _ in self._stack):
                self.noscript_links.append(href)
            if any(parent_attrs.get("id") == "catalogue-error" for _, parent_attrs in self._stack):
                self.error_links.append(href)
            self.links.append((href, attributes.get("aria-label", "")))
        if tag not in self.VOID_TAGS:
            self._stack.append((tag, attributes))

    def handle_endtag(self, tag):
        for index in range(len(self._stack) - 1, -1, -1):
            if self._stack[index][0] == tag:
                del self._stack[index:]
                break

    def handle_data(self, data):
        self.text.append(data)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID_TAGS:
            self.handle_endtag(tag)

    def by_id(self, element_id):
        return [attrs for _, attrs in self.elements if attrs.get("id") == element_id]

    def text_content(self):
        return " ".join(" ".join(self.text).split())


class CatalogueBrowserContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parser = PageProbe()
        if HTML.is_file():
            cls.parser.feed(HTML.read_text(encoding="utf-8"))

    def test_homepage_uses_project_relative_assets_and_json(self):
        self.assertTrue(HTML.is_file(), "root homepage must exist")
        html = HTML.read_text(encoding="utf-8")
        css_hrefs = [attrs.get("href") for tag, attrs in self.parser.elements
                     if tag == "link" and attrs.get("rel") == "stylesheet"]
        script_srcs = [attrs.get("src") for tag, attrs in self.parser.elements if tag == "script"]
        self.assertIn("./assets/catalogue.css", css_hrefs)
        self.assertIn("./assets/catalogue.js", script_srcs)
        self.assertIn('fetch("./data/treasures.json")', JS.read_text(encoding="utf-8"))
        self.assertNotRegex(html, r"<script[^>]+src=[\"']https?://")
        self.assertNotRegex(JS.read_text(encoding="utf-8"), r"fetch\([\"']https?://")

    def test_search_and_filter_controls_are_native_and_labeled(self):
        self.assertTrue(HTML.is_file(), "root homepage must exist")
        labels = {attrs.get("for") for tag, attrs in self.parser.elements if tag == "label"}
        controls = [(tag, attrs) for tag, attrs in self.parser.elements
                    if tag in {"input", "select", "button"}]
        search = [attrs for tag, attrs in controls
                  if tag == "input" and attrs.get("type") == "search"]
        selects = [attrs for tag, attrs in controls if tag == "select"]
        self.assertEqual(len(search), 1)
        self.assertEqual(len(selects), 2)
        for attrs in search + selects:
            self.assertTrue(attrs.get("id"), "each control needs an id")
            self.assertIn(attrs["id"], labels, f"{attrs['id']} needs a visible label")
        self.assertTrue(any(tag == "main" for tag, _ in self.parser.elements))
        self.assertTrue(any(tag == "h1" for tag, _ in self.parser.elements))
        self.assertTrue(any(tag == "button" and attrs.get("id") == "clear-filters"
                            for tag, attrs in controls))

    def test_live_result_count_is_polite_and_empty_state_is_present(self):
        self.assertTrue(HTML.is_file(), "root homepage must exist")
        count = self.parser.by_id("results-count")
        empty = self.parser.by_id("empty-state")
        self.assertEqual(len(count), 1)
        self.assertEqual(count[0].get("aria-live"), "polite")
        self.assertEqual(len(empty), 1)
        self.assertIn("hidden", empty[0])

    def test_loading_error_and_noscript_fallback_link_to_readme(self):
        self.assertTrue(HTML.is_file(), "root homepage must exist")
        text = self.parser.text_content()
        self.assertIn("Loading the catalogue", text)
        self.assertTrue(any("README.md" in href for href in self.parser.error_links),
                        "load error should include a rendered README link")
        self.assertTrue(any("README.md" in href for href in self.parser.noscript_links),
                        "noscript fallback should link to README")
        self.assertIn("catalogue-error", {attrs.get("id") for _, attrs in self.parser.elements})

    def test_curator_credit_and_jurisdiction_caution_are_present(self):
        self.assertTrue(HTML.is_file(), "root homepage must exist")
        text = self.parser.text_content()
        self.assertIn("Curated by Melvin Varghese", text)
        for phrase in (
            "Check rights before reuse.",
            "Public-domain assessments differ by jurisdiction and asset.",
            "CC0, an institutional Public Domain Mark and a United States-only copyright statement have different scopes.",
            "Each entry links to evidence; the Met’s eligible images additionally fall under its CC0 policy.",
            "This catalogue is not legal advice.",
        ):
            self.assertIn(phrase, text)
        self.assertTrue(any("Copyright and rights" in aria_label for _, aria_label in self.parser.links)
                        or any("COPYRIGHT_AND_RIGHTS.md" in attrs.get("href", "")
                               for tag, attrs in self.parser.elements if tag == "a"))

    def run_node(self, assertion_script):
        prelude = (
            "global.window = globalThis;\n"
            f"require({json.dumps(str(JS))});\n"
        )
        completed = subprocess.run(["node", "-e", prelude + assertion_script],
                                   check=False, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0,
                         f"Node assertion failed:\n{completed.stdout}\n{completed.stderr}")

    def test_search_fields_cover_all_specified_record_text(self):
        self.assertTrue(JS.is_file(), "catalogue JavaScript must exist")
        self.run_node(
            "const assert = require('node:assert/strict');\n"
            "const api = globalThis.CatalogueBrowser;\n"
            "assert.deepEqual(api.SEARCH_FIELDS, ['title','creator','year','description','institution','region','formats','tags','category','rights_status','rights_evidence']);\n"
            "const text = api.getSearchableText({title:'An open codex',creator:null,year:null,description:'painted leaves',institution:'Archive',region:'North Africa',formats:[],tags:['calligraphy','parchment'],category:'Rare Books & Manuscripts',rights_status:'Public Domain',rights_evidence:'official record'});\n"
            "assert.equal(text, 'An open codex painted leaves Archive North Africa calligraphy parchment Rare Books & Manuscripts Public Domain official record');\n"
        )

    def test_search_and_combined_filters_behavior(self):
        self.assertTrue(JS.is_file(), "catalogue JavaScript must exist")
        self.assertTrue(DATA.is_file(), "catalogue JSON must exist")
        self.run_node(
            "const assert = require('node:assert/strict');\n"
            "const fs = require('node:fs');\n"
            f"const entries = JSON.parse(fs.readFileSync({json.dumps(str(DATA))}, 'utf8'));\n"
            "const ids = (query, category='', rights='') => globalThis.CatalogueBrowser.filterRecords(entries, query, category, rights).map(record => record.id);\n"
            "assert.deepEqual(ids('Harmonia macrocosmica'), ['cellarius-harmonia-1661']);\n"
            "assert.deepEqual(ids('calligraphy'), ['met-451683','met-456074','met-449537']);\n"
            "assert.deepEqual(ids('', 'Historical Maps & Atlases', 'Public Domain — United States'), ['brion-africa-1786','official-war-maps-1898','speed-kingdome-china']);\n"
            "assert.deepEqual(ids('Cuba', 'Historical Maps & Atlases', 'Public Domain — United States'), ['official-war-maps-1898']);\n"
            "assert.deepEqual(ids('a query with no matching record'), []);\n"
        )

    def test_filter_options_are_derived_from_records_and_preserve_exact_values(self):
        self.assertTrue(JS.is_file(), "catalogue JavaScript must exist")
        records = json.loads(DATA.read_text(encoding="utf-8"))
        expected = {
            "category": list(dict.fromkeys(record["category"] for record in records)),
            "rights_status": list(dict.fromkeys(record["rights_status"] for record in records)),
        }
        completed = subprocess.run(
            ["node", "-e", "global.window=globalThis;require(" + json.dumps(str(JS)) + ");"
             "const fs=require('node:fs');const rows=JSON.parse(fs.readFileSync(" + json.dumps(str(DATA)) + ", 'utf8'));"
             "const api=globalThis.CatalogueBrowser;console.log(JSON.stringify({category:api.getFilterValues(rows,'category'),rights_status:api.getFilterValues(rows,'rights_status')}));"],
            check=False, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout), expected)
        self.assertEqual(expected["rights_status"], ["Public Domain", "Public Domain — United States"])

    def test_result_renderer_uses_text_content_and_item_rights_urls(self):
        self.assertTrue(JS.is_file(), "catalogue JavaScript must exist")
        source = JS.read_text(encoding="utf-8")
        self.assertIn("document.createElement", source)
        self.assertIn("textContent", source)
        self.assertIn("record.item_url", source)
        self.assertIn("record.rights_url", source)
        self.assertNotIn("innerHTML", source)

    def test_styles_include_visible_focus_and_mobile_layout(self):
        self.assertTrue(CSS.is_file(), "catalogue stylesheet must exist")
        source = CSS.read_text(encoding="utf-8")
        self.assertRegex(source, r":focus-visible\s*\{")
        self.assertRegex(source, r"@media\s*\(max-width:\s*40rem\)")
        self.assertRegex(source, r"grid-template-columns:\s*1fr")
        self.assertRegex(source, r"min-height:\s*44px")
        self.assertIn("prefers-reduced-motion", source)

    def test_readme_browser_link_and_credit_are_outside_generated_markers(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertEqual(readme.count(START), 1)
        self.assertEqual(readme.count(END), 1)
        begin = readme.index(START)
        end = readme.index(END) + len(END)
        outside = readme[:begin] + readme[end:]
        generated = readme[begin:end]
        self.assertRegex(outside, r"\[Browse the interactive catalogue\]\(index\.html\)")
        self.assertIn("Curated by Melvin Varghese", outside)
        self.assertNotIn("Browse the interactive catalogue", generated)
        self.assertNotIn("Curated by Melvin Varghese", generated)
        entries = json.loads(DATA.read_text(encoding="utf-8"))
        self.assertEqual(generated, render(entries))


if __name__ == "__main__":
    unittest.main()

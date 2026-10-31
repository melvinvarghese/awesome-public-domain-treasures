# Catalogue Browser Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the repository’s GitHub Pages root a responsive, accessible browser for the existing 68-record catalogue while keeping the README complete and all catalogue wording and rights assessments unchanged.

**Architecture:** A root `index.html` loads `./data/treasures.json` in the browser and links local CSS and JavaScript from `assets/`. JavaScript derives native filter options from the loaded records, searches the specified existing text fields, combines the filters in memory, and renders cards from source values; README remains the fallback. No framework, third-party runtime call, server-side component, or new catalogue source is introduced.

**Tech Stack:** Semantic HTML, CSS, dependency-free browser JavaScript, Python standard-library `unittest` checks, and Node’s built-in runtime for testing the real search/filter functions alongside the repository’s existing validator.

**Spec:** `docs/superpowers/specs/2026-10-31-catalogue-browser-design.md`

## Global Constraints

- “The JSON remains the only source of catalogue entries and rights assessments.”
- “The README stays complete and readable as a non-interactive fallback.”
- “Use ordinary HTML, CSS, and browser JavaScript, with no external libraries or third-party runtime calls.”
- “The page reads the JSON but never writes to it.”
- “Use relative asset/data paths so the repository’s Pages project-site prefix is respected.”
- “Do not change `data/treasures.json`, `data/schema.json`, rights assessments, the README’s generated entries, or deployment configuration as part of this scope.”
- Add README browse/credit text only outside `<!-- BEGIN GENERATED CATALOGUE -->` and `<!-- END GENERATED CATALOGUE -->`.
- Preserve exact `rights_status` and `rights_evidence` strings, including `Public Domain — United States`; do not infer or broaden a rights claim.
- The owner-approved repository description is “A curated catalogue of cultural-heritage works and objects, with source and rights-evidence links.” Apply that exact value as a separate GitHub metadata action during the approved release; do not change other repository metadata.

## Review Focus

- `creator` and `year` are `null` in existing records, and four records have empty `formats`; `test_search_fields_cover_all_specified_record_text` plus browser smoke checks must show no literal `null`/`undefined` and tolerate empty arrays.
- Fetch rejection, non-OK HTTP response, malformed JSON, and non-array JSON must leave a visible recovery path; `test_loader_shows_recovery_for_fetch_http_and_json_failures` exercises the actual loader for each failure, while `test_loading_error_and_noscript_fallback_link_to_readme` checks the error and fallback markup.
- Rights labels contain an em dash and category names contain ampersands; `test_filter_options_are_derived_from_records_and_preserve_exact_values` verifies values are sourced verbatim, not normalized or hard-coded.
- Catalogue strings must be rendered as text rather than interpreted as markup; `test_result_renderer_uses_text_content_and_item_rights_urls` requires DOM text nodes and the exact record URLs.
- GitHub Pages may serve this repository below a project-site prefix; `test_homepage_uses_project_relative_assets_and_json` and the local HTTP smoke check require relative asset/data URLs, not root-absolute paths.

---

## File Structure

- Create `index.html`: semantic homepage shell, labeled search and select controls, status/empty/error states, rights caution, curator credit, and JavaScript-disabled fallback.
- Create `assets/catalogue.js`: same-origin JSON loading, filter-option construction, text matching, filter composition, result rendering, status announcements, and visible error handling.
- Create `assets/catalogue.css`: responsive layout, readable contrast, visible keyboard focus, and touch-sized controls/cards.
- Create `assets/favicon.svg`: a small original archive-blue, warm-paper, and brass mark for the browser tab.
- Create `scripts/test_catalogue_browser.py`: focused Python-standard-library contract tests for the static browser; it is included by the existing `test_*.py` unittest discovery command.
- Modify `README.md` only before or after the generated-catalogue markers to add the browser link and curator credit.
- Create this design copy at `docs/superpowers/specs/2026-10-31-catalogue-browser-design.md` and this plan at `docs/superpowers/plans/2026-10-31-catalogue-browser.md`.
- Do not modify `data/treasures.json`, `data/schema.json`, generated README entries, `scripts/build_readme.py`, `scripts/catalogue.py`, `scripts/validate.py`, or `.github/workflows/validate.yml`.

### Task 1: Build and test the static catalogue browser

**Files:**
- Create: `scripts/test_catalogue_browser.py`
- Create: `index.html`
- Create: `assets/catalogue.css`
- Create: `assets/catalogue.js`
- Create: `assets/favicon.svg`

**Interfaces:**
- `assets/catalogue.js` declares `SEARCH_FIELDS` with exactly `title`, `creator`, `year`, `description`, `institution`, `region`, `formats`, `tags`, `category`, `rights_status`, and `rights_evidence`.
- `getSearchableText(record) -> string` joins those values safely, flattening arrays and treating `null` as empty text.
- `populateFilter(select, entries, field) -> void` creates one “All …” option and options from the distinct exact values present for `category` or `rights_status`.
- `matchesRecord(record, query, category, rightsStatus) -> boolean` performs case-insensitive substring search and requires every selected filter to match.
- `filterRecords(entries, query, category, rightsStatus) -> Array<Record>` returns source records matching the query and both selected filters; this pure function is exercised against the real JavaScript by Node’s built-in runtime, with no added dependency.
- `renderRecord(record) -> HTMLElement` creates a semantic card from the existing fields, omits unavailable creator/year rather than printing `null`, preserves the exact rights label/evidence, and assigns the record’s `item_url` and `rights_url` to separately named links.
- `renderResults(entries, query, category, rightsStatus) -> number` updates cards, result count, and the explicit zero-results state, returning the number of visible records.
- `loadCatalogue() -> Promise<void>` fetches only `./data/treasures.json`, checks the response and JSON array, wires controls, and presents a visible error with the README fallback on failure.

- [ ] **Step 1: Write the failing static-browser contract tests**

Add these tests to `scripts/test_catalogue_browser.py`, using `unittest`, `html.parser.HTMLParser`, `json`, `pathlib`, `re`, `subprocess`, the existing `catalogue.render` helper for generated-block parity, and Node’s built-in runtime for the real browser JavaScript. No new package is added:

```python
def test_homepage_uses_project_relative_assets_and_json(self):
    # Assert index.html loads assets/catalogue.css and deferred assets/catalogue.js;
    # assert the loader uses ./data/treasures.json and no external script URL exists.

def test_search_and_filter_controls_are_native_and_labeled(self):
    # Assert type=search, native select controls for category and rights_status,
    # visible label-for/id pairs, semantic main/heading, and a reset/clear button.

def test_live_result_count_is_polite_and_empty_state_is_present(self):
    # Assert a result-count element has aria-live="polite" and an explicit
    # no-results element exists; controls remain native keyboard-operable.

def test_loading_error_and_noscript_fallback_link_to_readme(self):
    # Assert initial loading text, a visible-on-error message containing a
    # readable full-README link, and a <noscript> README link.

def test_curator_credit_and_jurisdiction_caution_are_present(self):
    # Assert the exact text "Curated by Melvin Varghese" and reuse this
    # existing README warning verbatim, including its linked words:
    # "Check rights before reuse. Public-domain assessments differ by
    # jurisdiction and asset. CC0, an institutional Public Domain Mark and a
    # United States-only copyright statement have different scopes. Each entry
    # links to evidence; the Met’s eligible images additionally fall under its
    # CC0 policy. Read Copyright and rights. This catalogue is not legal advice."
    # Assert the linked words target COPYRIGHT_AND_RIGHTS.md.

def test_search_fields_cover_all_specified_record_text(self):
    # Parse SEARCH_FIELDS and compare its ordered values with the 11-field list
    # in Interfaces; assert the search-value code handles arrays and nulls.

def test_search_and_combined_filters_behavior(self):
    # Run the real assets/catalogue.js pure filter API with node and the actual
    # treasures.json: exact title search finds one named ID, calligraphy finds
    # three IDs, the US-rights map filter finds three IDs, and adding query
    # "Cuba" narrows that set to official-war-maps-1898. The three unfiltered
    # IDs are brion-africa-1786, official-war-maps-1898, and speed-kingdome-china.
    # Use one synthetic
    # record with creator=null and formats=[] to check null/empty handling.

def test_filter_options_are_derived_from_records_and_preserve_exact_values(self):
    # Assert populateFilter uses distinct loaded-record values and assigns each
    # option's value/text without rewriting it; assert both category and rights
    # filters are passed into matchesRecord.

def test_result_renderer_uses_text_content_and_item_rights_urls(self):
    # Assert the renderer uses createElement/textContent, record.item_url, and
    # record.rights_url; assert it does not interpolate record values with
    # innerHTML.

def test_styles_include_visible_focus_and_mobile_layout(self):
    # Assert catalogue.css has :focus-visible styling, a narrow-screen media
    # query, a single-column small-screen layout, and touch-sized controls.
```

- [ ] **Step 2: Run the focused tests and confirm the expected red state**

Run: `python3 -m unittest discover -s scripts -p 'test_catalogue_browser.py' -v`

Expected: FAIL because the homepage and browser assets do not exist yet; test discovery itself succeeds, with no missing-module or third-party dependency error.

- [ ] **Step 3: Create `index.html` with the semantic browser shell**

Include a page heading, visible labels tied to the search/category/rights controls, a clear-all button, a polite result-count region, loading and empty states, an error region that links to the rendered GitHub README (`https://github.com/melvinvarghese/awesome-public-domain-treasures/blob/main/README.md`), “Curated by Melvin Varghese,” and a `<noscript>` link to the full README. Reuse the README rights warning verbatim, including the link text “Copyright and rights” to `https://github.com/melvinvarghese/awesome-public-domain-treasures/blob/main/COPYRIGHT_AND_RIGHTS.md` and the sentence that the catalogue is not legal advice. Reference `assets/catalogue.css` and deferred `assets/catalogue.js` with project-relative URLs. Keep status and link purpose in text.

- [ ] **Step 4: Implement data loading, safe rendering, search, and combined filters in `assets/catalogue.js`**

Use the signatures in Interfaces. On successful load, derive both select lists from JSON values, render all records, and respond to search input, select changes, and clear-all. Search case-insensitively across the exact 11 fields; combine the query with both selected values using AND semantics. Construct cards with DOM APIs and `textContent`, not `innerHTML`; use the exact source `item_url` and `rights_url`. Display the record’s exact `rights_status` and, if shown, its unchanged `rights_evidence`. On network, HTTP, JSON-parse, or non-array failure, replace loading with the visible error and README fallback; do not leave a blank page or write to the JSON.

- [ ] **Step 5: Implement responsive and keyboard-visible styling in `assets/catalogue.css`**

Keep controls and cards legible at narrow widths, use a single-column card layout at `max-width: 40rem`, provide a clear `:focus-visible` indicator and readable contrast, and give interactive controls at least 44 CSS pixels of target height. Do not use color or icons as the only signal for rights status or link meaning.

- [ ] **Step 6: Run the focused browser contract suite**

Run: `python3 -m unittest discover -s scripts -p 'test_catalogue_browser.py' -v`

Expected: all 10 tests PASS.

- [ ] **Step 7: Commit the completed browser feature**

```bash
git add index.html assets/catalogue.css assets/catalogue.js scripts/test_catalogue_browser.py
git commit -m "feat: add static catalogue browser"
```

### Task 2: Add the README entry point without changing generated catalogue text

**Files:**
- Modify: `scripts/test_catalogue_browser.py`
- Modify: `README.md` (outside generated-catalogue markers only)

**Interfaces:**
- Add a single README line outside the generated catalogue with a Markdown link labelled “Browse the interactive catalogue” targeting `https://melvinvarghese.github.io/awesome-public-domain-treasures/`, followed by the curator credit “Curated by Melvin Varghese.”
- Preserve exactly one each of `<!-- BEGIN GENERATED CATALOGUE -->` and `<!-- END GENERATED CATALOGUE -->`.

- [ ] **Step 1: Write the failing README boundary test**

Add `test_readme_browser_link_and_credit_are_outside_generated_markers` to `scripts/test_catalogue_browser.py`. Assert each marker occurs exactly once; split the README into before/generated/after portions; require the browse link and curator credit in either outside portion and absent from the generated portion; and assert the README section including both markers equals `catalogue.render(json.loads(data/treasures.json))`.

- [ ] **Step 2: Run the focused suite and confirm this new test fails**

Run: `python3 -m unittest discover -s scripts -p 'test_catalogue_browser.py' -v`

Expected: the 10 browser tests pass and only `test_readme_browser_link_and_credit_are_outside_generated_markers` fails because the new line is not yet present.

- [ ] **Step 3: Add the browse link and credit outside the markers**

Add the browse link and credit near the README introduction, before `<!-- BEGIN GENERATED CATALOGUE -->`. Do not edit, move, or reword any existing README text or any generated entry.

- [ ] **Step 4: Run the README boundary test and the existing generator/validator checks**

Run:

```bash
python3 -m unittest discover -s scripts -p 'test_catalogue_browser.py' -v
python3 scripts/build_readme.py
python3 scripts/validate.py
```

Expected: all 12 browser tests pass; the builder preserves the new line outside the markers; validation prints `PASS: 68 entries; all 12 categories; fields, rights evidence, dates, duplicates, README parity, local links, anchors and SVG XML checked.`

- [ ] **Step 5: Review and commit the README integration**

Run `git diff -- README.md` and confirm the only intentional README diff is the new line before the generated marker and that no generated entry changed. Then run `git diff --check` (expected no output) and commit:

```bash
git add README.md scripts/test_catalogue_browser.py
git commit -m "docs: link README to catalogue browser"
```

### Task 3: Run full regression and Pages-root smoke checks

**Files:**
- No additional source files; verify Tasks 1–2.

**Interfaces:**
- The existing validation workflow already discovers `scripts/test_*.py`; do not add a dependency or modify `.github/workflows/validate.yml`.
- Do not change Pages source/deployment configuration. The approved production route is the repository’s existing Pages root.

- [ ] **Step 1: Regenerate the README and run repository validation**

Run: `python3 scripts/build_readme.py && python3 scripts/validate.py`

Expected: the README’s generated block remains in parity with `data/treasures.json`; validator prints its 68-entry PASS line and the separate note that external reachability/copyright conclusions require separate review.

- [ ] **Step 2: Run every discovered Python test**

Run: `python3 -m unittest discover -s scripts -p 'test_*.py' -v`

Expected: `Ran 23 tests` followed by `OK` (11 existing validator tests plus 12 new browser tests); Node’s built-in runtime and Python’s standard library are used without adding packages.

- [ ] **Step 3: Verify HTTP serving and exercise the browser manually**

From the repository root, run `python3 -m http.server 8000 --bind 127.0.0.1`, then check in another shell:

```bash
curl -fsS http://127.0.0.1:8000/ >/dev/null
curl -fsS http://127.0.0.1:8000/data/treasures.json | python3 -c 'import json,sys; records=json.load(sys.stdin); assert len(records)==68; print("PASS: served 68 catalogue records")'
```

Expected: both HTTP requests succeed and the second command prints `PASS: served 68 catalogue records`. In a browser at `http://127.0.0.1:8000/`, verify: initial count is 68; search `Harmonia macrocosmica` yields `cellarius-harmonia-1661`; search `calligraphy` yields 3 records; category `Historical Maps & Atlases` plus rights `Public Domain — United States` yields 3 records, and adding search `Cuba` yields the single matching record; an impossible query shows the empty state; clear-all restores 68. Confirm the current data produces 12 category options and only the two rights values actually present (50 `Public Domain`, 18 `Public Domain — United States`; do not add a CC0 option just because the schema permits it). Check item/evidence links against their JSON fields, keyboard-only use and focus, polite count announcements, narrow width without horizontal overflow, JavaScript-disabled fallback, and visible recovery when the JSON request fails or returns malformed JSON (use a temporary copied fixture or browser request blocking; do not edit the catalogue source to simulate failures).

- [ ] **Step 4: Review scope, approved metadata, and production route before publishing**

Run `git diff --check` and `git status --short`; confirm only `index.html`, `assets/catalogue.css`, `assets/catalogue.js`, `assets/favicon.svg`, `scripts/test_catalogue_browser.py`, the README line outside generated markers, and the two design/plan documents are changed. Confirm the data/schema, validator, workflow, and deployment configuration are untouched. The repository description is already approved as recorded in the spec; apply that exact value only as the separate approved GitHub metadata release action. After the completed code is pushed through the previously approved release, verify the Pages root displays the browser and its JSON loads from the project-site path; do not force-push.

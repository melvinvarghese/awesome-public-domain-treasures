# Public-Domain Treasures Catalogue Browser — Design

**Status:** Approved for implementation. The owner selected the GitHub Pages root as the browser homepage and approved the proposed repository description.

## Recommendation

Add a small, dependency-free browser to the existing GitHub Pages site. It will load the existing [`data/treasures.json`](https://github.com/melvinvarghese/awesome-public-domain-treasures/blob/main/data/treasures.json) in the visitor’s browser, then provide text search and category and rights-status filters. Each result will retain the catalogue’s existing wording and show clear links to the item record and rights evidence.

The JSON remains the only source of catalogue entries and rights assessments. The README stays complete and readable as a non-interactive fallback. No server, separate host, framework, or new catalogue content is proposed.

## Baseline at design time

- The [live Pages site](https://melvinvarghese.github.io/awesome-public-domain-treasures/) currently renders the README. The public repository metadata says Pages is enabled and names this as its homepage; the public [deployment history](https://api.github.com/repos/melvinvarghese/awesome-public-domain-treasures/deployments) shows GitHub Pages deployments.
- The default-branch [file tree](https://github.com/melvinvarghese/awesome-public-domain-treasures/tree/main) has `data/treasures.json` and [`data/schema.json`](https://github.com/melvinvarghese/awesome-public-domain-treasures/blob/main/data/schema.json), but no HTML/JavaScript catalogue UI. The current JSON is about 66 KB and contains 68 entries across 12 categories.
- Each record already includes `category`, `rights_status`, `rights_evidence`, `item_url`, and `rights_url`, alongside title, description, creator, year, institution, region, formats, and tags. The schema’s rights labels are `CC0`, `Public Domain`, and `Public Domain — United States`.
- [`scripts/build_readme.py`](https://github.com/melvinvarghese/awesome-public-domain-treasures/blob/main/scripts/build_readme.py) renders the JSON into the marked catalogue section of README. [`scripts/validate.py`](https://github.com/melvinvarghese/awesome-public-domain-treasures/blob/main/scripts/validate.py) checks schema/data consistency, rights fields, README parity, and local Markdown links. The existing [validation workflow](https://github.com/melvinvarghese/awesome-public-domain-treasures/blob/main/.github/workflows/validate.yml) runs that validator and its unit tests. No Pages-specific workflow is visible in the default-branch tree.
- The README has no explicit curator credit today. The repository description is currently empty in its [public metadata](https://api.github.com/repos/melvinvarghese/awesome-public-domain-treasures).

## Proposed experience

Visitors can search across the record’s existing text fields, including title, creator, year, description, institution, region, formats, tags, category, rights status, and the existing rights-evidence note. Two native filters can be combined with search: **Category** and **Rights status**. Filter choices come from values present in the JSON, rather than a separately maintained list. A result count updates as filters change; a clear-all control restores the full list, and an explicit empty-results message helps visitors recover.

Each result presents the title, description, available creator/year, category, institution, and the exact existing rights-status label. It provides separately labelled **Item record** and **Rights evidence** links using `item_url` and `rights_url`. The existing `rights_evidence` note may be shown as supporting detail, without rewriting it. A short rights caution links to `COPYRIGHT_AND_RIGHTS.md`; the interface must not imply that one jurisdiction’s status automatically applies elsewhere.

Credit the project as **“Curated by Melvin Varghese.”** Suggested repository description: **“A curated catalogue of cultural-heritage works and objects, with source and rights-evidence links.”**

## Architecture and data flow

Use ordinary HTML, CSS, and browser JavaScript, with no external libraries or third-party runtime calls:

`index.html` → fetch `./data/treasures.json` from the same GitHub Pages site → build filter choices from the loaded records → apply search and selected filters in memory → render result cards and a live result count.

The page reads the JSON but never writes to it. It does not call the institutions’ APIs; source and evidence links remain direct links from each existing record. Use relative asset/data paths so the repository’s Pages project-site prefix is respected. If loading fails, show a clear message and a link to the full README. Include a `<noscript>` fallback link as well.

### Implementation touchpoints

- The browser lives at the root `index.html` and uses `assets/catalogue.css`, `assets/catalogue.js`, and the small archive-themed `assets/favicon.svg`.
- README links to the live Pages homepage and includes the curator credit **outside** `<!-- BEGIN GENERATED CATALOGUE -->` and `<!-- END GENERATED CATALOGUE -->`; the generated catalogue block and its entries remain untouched.
- The concise GitHub repository description is updated as a separate release action, limited to the owner-approved exact value.
- Do not change `data/treasures.json`, `data/schema.json`, rights assessments, the README’s generated entries, or deployment configuration as part of this scope.

## Approved Pages route

**Recommended:** make the Pages root an interactive browser by adding `index.html`, while retaining the full README as the non-interactive fallback linked from the browser and still available in the repository. This makes the existing Pages homepage the catalogue browser without introducing another URL or host.

The owner chose the root browser, replacing the current root’s README rendering while retaining the complete README as a fallback linked from the page and in the repository. The current Pages settings use `main` at `/`, so root static files can be served without changing Pages configuration.

## Accessibility and mobile behavior

Use native, visibly labelled search and select controls; semantic page landmarks and headings; keyboard-operable controls; a clear visible focus indicator; readable contrast; and result-count / no-results announcements through a polite live region. Keep the controls usable at narrow widths with touch-sized targets and a single-column card layout. Rights status and link purpose must be conveyed in text, not by color or icons alone. No interaction should require a mouse or trap keyboard focus.

## Guardrails and risks

- **Rights scope:** preserve status labels and evidence text exactly as authored; do not infer or broaden a rights claim. Keep `Public Domain — United States` intact and the existing jurisdiction warning visible.
- **Pages behavior:** adding `index.html` changes the current root experience by design; the owner approved this route, and Pages currently serves `main` at `/`. Keep the README available as the non-interactive fallback.
- **Static loading:** the browser needs HTTP(S) to fetch JSON; opening the HTML as a local `file://` URL is not a valid test. A fetch or JSON parse error must fail visibly and point to the README fallback.
- **Fallback integrity:** README generation must continue to preserve material outside its markers. Keep all new README text outside the generated block and rerun the existing parity validator.
- **Scope control:** do not add image downloads, user accounts, remote APIs, server-side search, new rights assessments, or dependencies.

## Verification and release checks

1. Run `python3 scripts/build_readme.py`, `python3 scripts/validate.py`, and `python3 -m unittest discover -s scripts -p 'test_*.py'`; confirm the generated README catalogue still matches the JSON and all existing checks pass.
2. Serve the static site locally over HTTP and verify the JSON loads from the same relative path used on Pages. Check all records render, search matches representative titles/tags/rights labels, category and rights filters combine correctly, reset restores all results, and empty results are explained.
3. Check the initial loading state, malformed/unavailable JSON behavior, and JavaScript-disabled fallback. Confirm every card’s item and rights-evidence links use the corresponding JSON values and open successfully as links (without treating reachability as proof of rights).
4. Test keyboard-only operation, focus visibility, screen-reader announcements for changed result counts, narrow mobile widths, and no horizontal overflow.
5. Run existing repository validation, apply only the approved repository description, publish the reviewed changes through a normal fast-forward push, and verify the live GitHub Pages homepage and its project-relative data assets; do not force-push.

## Approval record

The owner approved the design and implementation plan, chose the GitHub Pages root as the interactive browser homepage, approved the repository description “A curated catalogue of cultural-heritage works and objects, with source and rights-evidence links,” requested an independent final review, and authorized publication after verification and review. The full README remains the readable fallback. Do not force-push.

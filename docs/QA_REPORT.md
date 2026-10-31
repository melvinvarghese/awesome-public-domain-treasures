# Quality assurance report

Release: 1.0.0. Research date: 30 October 2026.

## Scope and evidence

This edition contains **68 treasures across all 12 requested categories**, below the aspirational 100–150. It does not use speculative additions to meet a number. Every entry has a primary record, a rights label, a primary rights URL, a paraphrase of the evidence, and a verification date. The linked heritage assets are not included in the ZIP.

Fifty entries report an institutional public-domain determination; eighteen carry an explicitly United States-limited label. Twenty-eight Met object records also support CC0 access to eligible images through their item-level flags and the museum policy. These counts describe reported evidence, not independent legal clearance.

Research notes: [art](research-art.md), [science](research-science.md), [text, photography and music](research-text.md). Supporting checks: [Met item metadata](met-item-checks.json) and [Gutenberg ebook headers](gutenberg-header-checks.json). Both snapshots record observations on the research date; they do not freeze or guarantee current institutional policy.

## Checks executed

- Parsed catalogue and schema as JSON; checked required fields and value types, category and rights enums, dates, URL structure, missing evidence, duplicate IDs and duplicate normalized record URLs.
- Compared every generated README catalogue entry against structured data. The catalogue block must match deterministic rendering, including descriptions and rights links.
- Checked Markdown relative links and fragments, including the table of contents and individual highlight anchors.
- Ran nine regression tests covering the accepted catalogue, missing rights evidence, inappropriate open-license labels, duplicate IDs and URLs, invalid dates and categories, malformed URLs, non-string category values and broken local fragments.
- Parsed the GitHub workflow and issue-form YAML; checked event names and form input structures.
- Parsed SVG XML, rendered the banner to a 1280 × 360 PNG with librsvg/Cairo and inspected that image. It has no external image/font dependencies, with an accessible title, description and README alt text. It is a banner inspection, not a complete assistive-technology audit.
- Reviewed titles, approximate dates, attribution uncertainty, original descriptions and the distinction between format availability and tested download payloads. Formats reflect institutional records; the project did not download every book, scan or image.

## External reachability results

A separate scripted GET audit checked 106 distinct item and rights URLs: 101 returned successful responses and 5 returned HTTP 403. The five blocked URLs are the three Texas A&M maps and the two BHL volumes; their primary record text was available through web research. No 404 or 410 was observed. The JSON report records exact URLs, times and classifications. Successful responses are reachability observations, not a guarantee of complete page content or download access.

## Access limitations

Four Library of Congress scores initially required indexed official record text after HTTP 403 responses. A final direct follow-up with the auditor’s request headers successfully retrieved all four complete HTML pages and confirmed explicit public-domain text. See the [live follow-up results](loc-live-checks.json). The initial access limits remain documented in the research history. Some other hosts may block a scripted audit despite being accessible through web retrieval. The optional audit classifies these outcomes separately from likely missing pages and never removes records automatically.

The machine-readable [link audit](link-audit.json) is a separate reachability check, not a rights review. Results must be interpreted alongside the research notes. A 200 response can be a page shell; a 403 or timeout can be an access restriction. No automatic result proves either legal status or permanent disappearance.

## Diversity and editorial limits

| Category | Entries |
| --- | ---: |
| Rare Books & Manuscripts | 5 |
| Historical Maps & Atlases | 4 |
| Astronomy & Celestial Charts | 6 |
| Botanical & Zoological Illustrations | 4 |
| Scientific Discoveries & Publications | 5 |
| Art, Prints & Illustrations | 12 |
| Historical Photography | 5 |
| Literature & Poetry | 9 |
| Music & Musical Scores | 5 |
| Engineering, Inventions & Technical Drawings | 4 |
| Ancient Civilizations & Historical Documents | 5 |
| Unusual & Forgotten Treasures | 4 |

Cultural origins and subjects span Africa, Asia, Europe and the Americas. Twenty-eight entries are held by the Met, and the science selection is predominantly European in authorship. Several photographs and natural histories reflect colonial production contexts. Oceania is absent; an otherwise relevant navigational chart failed the rights eligibility check. These gaps should guide future contributions. The data does not count a European map of Africa as African authorship.

## Reproduce locally

```bash
python3 scripts/build_readme.py
python3 scripts/validate.py
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 scripts/check_external_links.py
```

The first three commands are offline, standard-library checks for Python 3.11+. The last command uses network access and may take several minutes. GitHub Actions has been supplied but has not run on GitHub because this project was not published.

## Independent review

### Standards

Review against CONTRIBUTING.md and EDITORIAL_GUIDELINES.md identified a malformed-input crash when a category was an array or object. The category-coverage calculation now accepts only strings; a regression test also exercises null and numeric category values. The updated nine-test suite passes.

### Spec

Review against the supplied project brief identified the same validator issue, now corrected. The reviewer confirmed the substantive repository requirements, the explicitly disclosed smaller collection and the documented indexed-record access limit. Final packaging and reachability reporting were checked separately after this review.

One finding on each review axis, both describing the same corrected defect. No unresolved findings from either axis.

## Packaging checks

The final ZIP contains one top-level `awesome-public-domain-treasures/` folder, including `.github` and `.gitignore`. Git history, caches and temporary research files are excluded. The archive was opened, CRC-tested and compared byte-for-byte with its source files. Its extracted copy passed the validator and nine regression tests. README.md is also supplied separately for preview.

## Capability review

The project used the research, implementation, code-review and file-delivery skills; institutional web research and item APIs; Python file generation, validation and ZIP tooling; YAML parsing; and SVG rendering and visual inspection. Independent agents reviewed standards and the supplied spec. No GitHub account access, publication, paid service or account connection was used. Raster image generation, office-document generation and website hosting would not improve this source-only Markdown repository.

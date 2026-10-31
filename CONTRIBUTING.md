# Contributing

Thank you for helping people discover cultural heritage. A good contribution introduces a remarkable work and leaves a traceable explanation of why its linked version qualifies.

## Suggest a treasure

Use the “Suggest a treasure” issue form, or edit [treasures.json](data/treasures.json) in a pull request. Supply an institutional item record, creator and date if recorded, cultural origin, a short original description, and item-specific rights evidence. Say which edition, translation, scan, photograph or recording the evidence covers. A general museum policy is useful only when the object is demonstrably included in that policy.

Eligible: an explicit institutional public-domain designation, CC0 dedication covering the relevant asset, or a carefully supported jurisdiction-specific public-domain determination. Ineligible: CC BY, CC BY-SA, educational permission, personal-use permission, “free download,” and uncertain rights. “No known restrictions” alone is not an affirmative public-domain determination. Collections with mixed rights belong outside the main catalogue unless the included scope is clearly defined.

## Prepare a pull request

1. Add one object to the JSON array, following [schema.json](data/schema.json). Keep unknown creators or dates `null`; never invent them. Use a stable, lowercase hyphenated ID.
2. Follow [EDITORIAL_GUIDELINES.md](EDITORIAL_GUIDELINES.md). Choose the category that best explains the discovery, even if several could fit.
3. Record the source and verification method in a research note under `docs/`; update `date_verified` only after checking the evidence.
4. Run `python3 scripts/build_readme.py`, then `python3 scripts/validate.py` and `python3 -m unittest discover -s scripts -p 'test_*.py'`.
5. Explain your evidence in the pull-request template. Keep unrelated cleanup separate.

No Python dependencies are needed. The JSON Schema also supports independent validation with a Draft 2020-12 validator; the built-in script implements this repository's checks without downloading packages.

## Report a broken link or rights concern

Use the broken-link form for either issue. Include the entry ID, failing URL, observed error and date, and an institutional replacement if known. A 403, CAPTCHA, timeout or 429 does not establish that an item has disappeared. Describe the response rather than assuming the resource is broken. Rights concerns can be reported without proposing a replacement.

## Maintainer review

Read the primary record and rights evidence yourself. Confirm the evidence covers the linked asset; check geographic attribution and edition metadata; compare the README with JSON; run validation. Ask for evidence or leave the item out if uncertain. Recheck the entire submission after redirects or title changes. Record accepted additions, removals and material corrections in [CHANGELOG.md](CHANGELOG.md).

Do not use generated prose as evidence. Contributions must be your original writing or appropriately licensed. By submitting original material, you agree it may be distributed under the repository's [MIT license](LICENSE). Linked third-party material retains its own status.

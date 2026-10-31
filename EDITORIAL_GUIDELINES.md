# Editorial guidelines

## Selection

Choose individual works, objects or clearly bounded historical collections with a useful discovery story. An archive homepage is not a treasure entry. Prefer durable institutional records and stable identifiers over raw image URLs. Include cultural and geographic variety; identify origin separately from the location of the holding museum. One institution should not define what a whole culture looks like.

## Description and metadata

Use the record's title or a transparent shortened title. Preserve uncertainty such as “attributed to,” “ca.” and date ranges. A modern ebook release date is not a historical publication date. Identify translators when their text is the linked version. Do not infer named creators for unattributed objects. Unknown values are `null`, not plausible guesses.

Write one or two original sentences explaining what a reader can inspect or learn. Avoid unsupported “first,” “oldest,” “unique” and “most important” claims. Preserve historical context without endorsing prejudice in a source. Do not copy catalogue descriptions. Name formats only when the record or API demonstrates access; an empty array means format availability has not been established.

## Rights evidence

`rights_status` is one of `CC0`, `Public Domain`, or `Public Domain — United States`. CC0 means the applicable rights holder waived rights to the extent possible; an institutional public-domain statement describes an assessment. Neither resolves every country's law or unrelated rights.

`rights_url` must lead to a primary item record, item API or applicable institutional statement. `rights_evidence` explains the decisive evidence in your own words. When relying on a policy plus an item-level eligibility flag, retain both in the research note. Do not turn “no known restrictions” into “public domain,” or CC BY into CC0. Leave ambiguous candidates out.

## Maintenance and code

Keep JSON as the catalogue source of truth. Regenerate the README rather than editing its marked catalogue manually. Scripts must work on Python 3.11 or later without third-party dependencies; use clear functions and test failures that could admit misleading data. Keep network checking optional and separate from offline validation. The validator checks structure and consistency, never legal correctness.

Review rights and records whenever changing an entry. For an actively maintained fork, aim for a full annual evidence review and a quarterly link review; these are proposed maintainer duties, not services this repository runs automatically. Date the review honestly and log substantive corrections.

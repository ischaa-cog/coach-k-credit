# Citation rules

## The grammar

One form, everywhere. Doc-id, then chapter where one exists, then the page or section.

```
[ck-part1 ch2 p8]                       tier 1, chapter + page
[ck-part1 ch10 p31]                     chapter from the manifest map, NOT the printed
                                        body header, p26 misprints Ch.10 as "CHAPTER 8"
[ck-grant-guide s3]                     synthetic section (Drive text has no real pages)
[t2-credit-millionaire-2024 p41]        tier 2, page
[t2-credit-secrets-mitchell-2019 §12]   tier 2, author suffix MANDATORY
[list-bank-funding p2 · verified 2026-09]   volatile, date-stamped
```

## What the member actually sees

Not the doc-ids. Those are for you and for the verify gate. The member gets **one plain line
at the end of the answer**, no footnotes, no per-sentence attribution.

The line begins with the word `Source:`. It used to begin with an em dash; it no longer does,
because em dashes are banned in member-facing output (see `voice-and-format.md`).

```
Source: Master Blueprint, Ch. 2 & Ch. 19
Source: Grant Writing Guide, Ch. 3; GrantFind Cheat Sheet
Source: Master Blueprint, Ch. 6 & Ch. 17; Access Granted podcast
```

Two or more sources on one line are separated by `;`. Never split them across lines, never
number them, never add a per-sentence citation in the body.

## Linking the source line

**Link every source that has a `drive_url` in `kb/manifest.yaml`.** Standard markdown, on the
title, inside the same single `Source:` line.

```
Source: [GrantFind Grant Proposal Cheat Sheet](https://drive.google.com/file/d/1Kx7f-xR3f6BrAgc0cDu7oZizAOvUWhZr/view)
Source: [Grant Writing Guide, Ch. 3 & Ch. 4](https://drive.google.com/file/d/10Qc3imuOvelbclTyOZmc3EKY6ZADD68h/view); Master Blueprint, Ch. 6
```

Rules that do the work:

- **Read the URL out of the manifest. Never build one from a file id you remember.** Drive
  PDFs are `drive.google.com/file/d/<id>/view`, native Google Docs are
  `docs.google.com/document/d/<id>/edit`, and using the wrong shape produces a link that
  loads for you and 404s for everyone else.
- **No `?usp=drivesdk` and no `ouid=` parameter.** The `ouid` ties the link to one Google
  account. The manifest URLs are already stripped; keep them that way.
- **A source with no `drive_url` stays plain text.** Do not link it, do not substitute a
  neighbouring document's link, and do not send the reader to a Drive search. The Master
  Blueprint is the case that matters: it is the most-cited tier-1 source in the corpus and it
  is **not in this Drive**. `Source: Master Blueprint, Ch. 2 & Ch. 19` is complete and
  correct as it stands.
- **Never link a tier-2 ebook**, even if a URL turns up. Tier 2 is not named by title in
  member-facing output at all, so there is nothing to hang a link on.
- **Never link `staff-cancellation-sop`, any `x-` doc, or `intel-*`.**

### What these links do and do not do

They open for accounts with Drive access to the file, which means you and the team. They are
**not member-safe**: pasted into a community post, a DM, or an email, they are a permission
wall. When an answer is being written to go out to members, either drop to plain titles or
point at where the member actually has the asset.

Two link targets carry a caveat worth knowing before you send anyone to them:

- `ck-fbl-2025-notes` is **page-scoped in the KB to Coach K's page 1**, but the link opens
  the whole bundle, pages 2 to 8 of which are partner-speaker IP.
- `ck-grant-writer-curriculum` lives in a Drive doc titled *"Aug 2024 Coach K's Videos Scripts
  & Course Outline"*. Only the curriculum half was ingested; the rest is marketing copy.

## Tier marking

**Tier 1: Coach K's own material.** The Master Blueprint (95pp, 22 chapters, personal
credit), the Grant Writing Guide, the Masterclass and Bootcamp workbooks, the GrantFind cheat
sheet, the proposal template, the grant-writer curriculum, the SAM.gov checklist, her Funding
Blueprint Live session notes, and the Access Granted transcript. Name it plainly. Quote it
freely, it is hers.

**Tier 2: third-party ebooks.** Copyrighted, mostly 2007 to 2019, stale on specifics.
- **Never reproduce a long passage.** Facts and structure only, rewritten in her voice.
- **Never attribute their claims to Coach K.**
- Cite them as *"general industry practice, not from Coach K's material"* rather than by
  title. Naming a competitor's ebook inside a Coach K answer is off-brand and unnecessary.
- If a tier-2 source is the **only** support for a claim, say so in the answer.

**Volatile.** Anything from `list-*` docs or marked `volatility: volatile` in the manifest
carries "as of \<date\>, verify current terms directly" and never appears as a table of
names, amounts, or thresholds.

## The title-collision rule

`t2-credit-secrets-mitchell-2019` is *"Credit Secrets: The Blueprint on How to Raise Your
Credit Score"* by **Brian Mitchell, 2019**. Coach K's is *"Credit Secrets Master Blueprint"*.

If either is ever referred to as just "Credit Secrets", a 2019 third-party claim gets
attributed to Coach K. That is the failure that destroys trust in this skill fastest. The
author suffix is mandatory; never write a bare "Credit Secrets" citation for tier 2.

## Verify before you cite

The snippet `kbsearch.py` prints is a **locator, not a source**. Read the page file it names
before you use the claim. Two rules that came out of building this:

1. **Chapter numbers come from `kb/manifest.yaml`, never from the page text.** The book
   misprints Ch.10 as "CHAPTER 8" across all 25 pages of dispute letters, and Ch.19's table
   of contents disagrees with its body marker.
2. **Match anchors on normalised text.** Page files preserve the source's line wrapping, so a
   quoted phrase will often span a newline. Collapse whitespace before checking whether your
   quote actually appears.

## Never cite

- Any doc-id beginning `x-`, quarantined, and not present in the corpus or index anyway.
- `staff-cancellation-sop` in any member-facing answer.
- An excluded page range: `ck-fbl-2025-notes` is **Coach K's page 1 only**; pages 2 to 8 are
  partner speakers' IP and were never ingested.
- Partner coaches by name as sources: Marcus Barney, Cassandra Smith, Sevyn Buffins, Tevin
  Walker, Marcus Rosier, Brooklynn Harris, Sire Abram, Mychel Dillard, Kenneth Smith, Sonia
  Lewis, Blake Nathan. The one exception is naming an interviewer of Coach K when quoting her
  own words from that interview.

# Citation rules

## The grammar

One form, everywhere. Doc-id, then chapter where one exists, then the page or section.

```
[ck-part1 ch2 p8]                       tier 1, chapter + page
[ck-part1 ch10 p31]                     chapter from the manifest map, NOT the printed
                                        body header — p26 misprints Ch.10 as "CHAPTER 8"
[ck-grant-guide s3]                     synthetic section (Drive text has no real pages)
[t2-credit-millionaire-2024 p41]        tier 2, page
[t2-credit-secrets-mitchell-2019 §12]   tier 2, author suffix MANDATORY
[list-bank-funding p2 · verified 2026-09]   volatile, date-stamped
```

## What the member actually sees

Not the doc-ids. Those are for you and for the verify gate. The member gets **one plain line
at the end of the answer**, no footnotes, no per-sentence attribution:

```
— Master Blueprint, Ch. 2 & Ch. 19
— Grant Writing Guide, Ch. 3; GrantFind Cheat Sheet
— Master Blueprint, Ch. 6 & Ch. 17; Access Granted podcast
```

## Tier marking

**Tier 1 — Coach K's own material.** The Master Blueprint (95pp, 22 chapters, personal
credit), the Grant Writing Guide, the Masterclass and Bootcamp workbooks, the GrantFind cheat
sheet, the proposal template, the grant-writer curriculum, the SAM.gov checklist, her Funding
Blueprint Live session notes, and the Access Granted transcript. Name it plainly. Quote it
freely — it is hers.

**Tier 2 — third-party ebooks.** Copyrighted, mostly 2007–2019, stale on specifics.
- **Never reproduce a long passage.** Facts and structure only, rewritten in her voice.
- **Never attribute their claims to Coach K.**
- Cite them as *"general industry practice, not from Coach K's material"* rather than by
  title. Naming a competitor's ebook inside a Coach K answer is off-brand and unnecessary.
- If a tier-2 source is the **only** support for a claim, say so in the answer.

**Volatile.** Anything from `list-*` docs or marked `volatility: volatile` in the manifest
carries "as of \<date\> — verify current terms directly" and never appears as a table of
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

- Any doc-id beginning `x-` — quarantined, and not present in the corpus or index anyway.
- `staff-cancellation-sop` in any member-facing answer.
- An excluded page range: `ck-fbl-2025-notes` is **Coach K's page 1 only**; pages 2–8 are
  partner speakers' IP and were never ingested.
- Partner coaches by name as sources: Marcus Barney, Cassandra Smith, Sevyn Buffins, Tevin
  Walker, Marcus Rosier, Brooklynn Harris, Sire Abram, Mychel Dillard, Kenneth Smith, Sonia
  Lewis, Blake Nathan. The one exception is naming an interviewer of Coach K when quoting her
  own words from that interview.

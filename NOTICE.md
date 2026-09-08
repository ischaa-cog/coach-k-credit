# Notice — confidential and proprietary

**This repository is private and must stay private.** It is an internal tool for Coach K
(Jekwenta "Kwenta" Primm) and the Circle of Greatness / Business & Grant Community team.

## What is in here

`kb/corpus/` contains extracted text from two categories of document:

**1. Coach K's own material** — the *Credit Secrets Master Blueprint* (Part 1), *The Grant
Writing Guide for New Business Owners*, the Grant Mastery Masterclass and Grant Writer's
Bootcamp workbooks, the GrantFind Proposal Cheat Sheet, the member proposal template, the
grant-writer curriculum, the SAM.gov checklist, Funding Blueprint Live session notes, and the
Access Granted podcast transcript. These are **paid products**. They are not for
redistribution, and this repository must never be made public or forked outside the team.

**2. Third-party copyrighted ebooks** — approximately 26 documents by other authors, held here
as internal reference only. Notable: *Credit Millionaire* (Bill Harris, ©2024), *The
Billionaire's Business Blueprint* (Reginald Ringgold, ©2008), *The Business Credit Guru*
(2007), *Credit Secrets* (Brian Mitchell, 2019). The skill is instructed never to reproduce
long passages from these and never to attribute their claims to Coach K — see
`references/citation-rules.md`. Making this repository public would constitute redistribution
of that material.

The original PDFs are **not** committed (`.gitignore`). Only extracted text is here.

## What is deliberately absent

Six documents are quarantined and excluded from both the knowledge base and version control:
a CPN registration guide, a credit sweeps cheat sheet, a credit card fraud manual, a tradeline
list that coaches falsified rent verification, the "Section 609 loophole" PDF, and a
CPN-based credit ebook. `kb/manifest.yaml` records the reason for each.

Also excluded: other Circle of Greatness coaches' intellectual property, and a client tracker
containing 14 people's names, emails and phone numbers.

## Staff content

`kb/staff/` holds internal operations documentation naming Stripe and GoHighLevel procedures.
It is indexed into a **separate** database (`staff.sqlite3`) that the member-facing search
never opens, and the skill is instructed never to surface it in an answer written for a
member. Treat it as internal even within the team.

## If this is ever made public

Remove `kb/corpus/`, `kb/canon/`, `kb/staff/` and the content fields of `kb/manifest.yaml`
first. The pipeline (`scripts/`), `SKILL.md`, and `references/` carry no third-party content
and are safe to publish on their own.

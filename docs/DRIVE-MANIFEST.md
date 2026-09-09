# Drive source manifest

Google Drive is reachable only through the Claude Code MCP connector in-session,
not via a local credential — so there is no runnable `05_pull_drive.py`. Files are
pulled with `read_file_content` and written to `kb/sources/_drive/<doc-id>.txt`,
then extracted by `10_extract.py` like any other source, with `pagination: synthetic`.

`read_file_content` is used rather than `download_file_content` deliberately: the
latter returns base64, ~1.4x the bytes for no benefit when we only want text. The
trade-off is that Drive PDFs lose true page boundaries, hence synthetic section
citations (`§7`) for everything in this table.

**Pull by file id only — never by folder crawl.** A crawl is how partner IP and
client PII would drift into the corpus.

## In scope

| doc-id | Drive file id | title | domain |
|---|---|---|---|
| `ck-grant-guide` | `10Qc3imuOvelbclTyOZmc3EKY6ZADD68h` | The Grant Writing Guide for New Business Owners | grants |
| `ck-grant-masterclass-wb` | `1SH9aUOahxAEKYGTODgc2C2aUUBXbYljv` | Grant Mastery Masterclass (Workbook) | grants |
| `ck-grant-cheatsheet` | `1Kx7f-xR3f6BrAgc0cDu7oZizAOvUWhZr` | GrantFind Grant Proposal Cheat Sheet | grants |
| `ck-grant-bootcamp-wb` | `1soCJ1wYj53wmDCwYj7F3D_WnZGwi1EFh` | The Grant Writer's Bootcamp (Workbook) | grants |
| `ck-grant-ai-blueprint-wb` | `1syfiZdacP2hGjS5SymE8pOzRx4TAYim3` | AI and Grants Blueprint (Workbook) | grants |
| `ck-grant-proposal-template` | `1exyCaxU0ghLCAoPkqWU79AuxgYbyhTAC8AiiJ3DxDxo` | Grant Proposal Template ("Grant Tempp 2") | grants |
| `ck-nonprofit-essentials` | `1u1x2C3g0LDYXfRVsNIw27EgSjGzoaS1o` | Non-Profit Essentials: A Beginner's Guide | grants |
| `ck-grant-writer-curriculum` | `1uT9HKQcM1ZRzaqzcpLD0frwYDvfV9Ij5jlwrQBazAqI` | How to Become a Grant Writer — course outline | grants |
| `ck-get-government-ready` | `1D2M9LA3ZmE4iExfwunfwEevN1cSPoX8Y` | Get Government Ready (SAM.gov / DUNS / NAICS) | grants |
| `ck-fbl-2025-notes` | `1K8NSHyGCTX4WytGBTUv6qDZr9pvbyaD77YnqvgTf-j0` | Funding Blueprint Live 2025 Notes Bundle | credit |
| `ck-fbl-2026-notes` | `1SVIqFYo8rKeG4_20VjLr1jqFTSZFPZEL` | Funding Blueprint Live 2026 Session Notes | credit |
| `ck-transcript-access-granted` | `1cWGY3LjhZNW47pgWpjooug1YV-OEQhojlSc4urq0w3A` | Access Granted: Coach K on Funding Strategies | crosscutting |
| `ck-transcript-cog` | `1y7erE_0wqycYhOEzW-GHkHev89IS7fNxUEDLRzhG_9s` | Circle of Greatness: Interview with Coach K | crosscutting |
| `ck-transcript-marvin` | `1gx8CrbpfuYMSd9t5HuIK3s6MPULQtJuP3Be2-ynvXH4` | The Marvin Francois Show: Interview with Coach K | crosscutting |
| `ck-transcript-jt` | `1VkNLm5dOAJ6lrFY9EFZp5el2IT0HBGsnN11Tds3oN3g` | JT Automations Interview with Coach K | crosscutting |

## Link discrepancies, verified 2026-09-09

Every file id above was re-resolved against Drive. All 15 still resolve. Canonical `viewUrl`s
for the 8 ids that are also in `kb/manifest.yaml` are now stored there as `drive_url`, with
`?usp=drivesdk` and `ouid=` stripped. Two notes:

- **`ck-grant-writer-curriculum`** is titled *"Aug 2024 Coach K's Videos Scripts & Course
  Outline"* in Drive, not "How to Become a Grant Writer". Same document, and only the
  curriculum half was ingested; the rest is marketing copy.
- **`ck-grant-cheatsheet`** is titled *"GrantFind  Grant Proposal Cheat Sheet Redesigned
  (1).pdf"* in Drive, double space included.

`ck-part1`, the Master Blueprint, has **no Drive copy**. Searches on both "Credit Secrets" /
"Master Blueprint" and its staged filename return only Funding Blueprint flyers. It is
staged locally and cites without a link.

## Page-scoped

`ck-fbl-2025-notes` — **page 1 only.** Pages 2-8 are partner-speaker IP: Kenneth
Smith (credit card stacking), Sonia Lewis (student loans), Siedah Garrett, Marcus
Y. Rosier, Women in Wealth panel, Blake Nathan (nonprofit tax), Nehemiah Davis.
Blake Nathan's 501(c)(3) material is genuinely good and genuinely his.

## Deferred, with reason

- **`Grant Journal.pdf`** `1N_dpM-a1rjNgToCzF81zLk7GmRgBIYBp` - 226MB print artifact,
  almost certainly image-only, and there is no OCR on this machine.
- **`Grant Workbook.pdf`** `1i1UM9g680ggTT5_ekP3B8hcPyeDWoZLM` - May 2024, superseded
  by the Masterclass and Bootcamp workbooks.
- **`More Money Summit Notes Bundle`** `1u_msZyJOG5Ou3vETT4MaCYtYC0uj2aE597QEIK97w14` -
  the event is Leelah Brown's; notes are COG-produced but the teaching is a partner's.
- **Drive third-party credit ebooks** - `SECRET SAUCE TO A 800 DIY CREDIT REPAIR` x2,
  `the credit journal`, `kid ebook`, `Building Credit for FREEDOM`, Snoop/Mychel
  Dillard's `DHGCRU` + `DIY bonus material`. In scope per the user's decision but
  deferred behind tier-1: the local corpus already carries 26 tier-2 credit documents
  over the same ground, and six of these matched the fraud-term sweep and need
  page-level screening first. Snoop's two are arguably partner IP under rule 5.
- **`Credit_Stacking_Strategy.pdf`** `1K0FxBdZ0msm-MSXUgDCJilrCxDMa9cOy` - quarantined,
  not deferred: advises purchased AU tradelines to support "stated income" credibility.

## Excluded - reported, never ingested

Partner IP: Marcus Barney (incl. `Credit To Cash Challenge (Workbook).pdf`
`1AVQtwzaRnJ-TjQygIzJEu80SxjpDD51o`), Cassandra Smith, Sevyn Buffins, Tevin Walker,
Marcus Rosier, Brooklynn Harris, Sire Abram, Mychel Dillard, Kenneth Smith, Sonia
Lewis, Blake Nathan, Solomon Woods. Anything owned outside `circleofgreatness.com`.

PII: `Coach K HTO Done-For-You Grant Tracker` `16EM7O-33SR7BhgIZ4JFnjYEX3JIwNHWECzUejvFvT5s`
(14 clients with emails and phone numbers), the two `Export_Contacts_*.csv`.

Stale: `Bootcamp Grants` / "Exclusive Grant Vault"
`1Gt51MDKm5UjOuh9H8CtuUhG6llO-mxUF448t7Pnyrh0` - 19 grants, every deadline expired
between 5/8/2025 and 6/9/2025, still linked from the September 2026 VIP page. Never
quoted; flagged to the user as a live business problem.

Marketing/ops: reminder and nurture emails, SMS, offer sheets, sales pages, ad copy,
graphics, PSDs, videos, testimonials, event photos, Skool/HighLevel SOPs, attendance
sheets, post-event surveys. Note that "Credit Call" throughout this Drive is a
**graphics label, not a content label**.

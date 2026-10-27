# Lumen report package

High-profile stakeholder materials for Lumen — written for product, clinical advisors, partners, and demo reviewers. Language stays disclosure-first and deliberately light on engineering detail.

**Prepared:** 27 October 2026

## Start here

| Document | Use when |
|---|---|
| [`Lumen_One_Pager.pdf`](Lumen_One_Pager.pdf) | Handout / leave-behind (1 page) |
| [`Lumen_Executive_Brief.pdf`](Lumen_Executive_Brief.pdf) | Short stakeholder brief (2 pages) |
| [`Lumen_Product_Overview.pdf`](Lumen_Product_Overview.pdf) | Full product narrative with infographics (5 pages) |
| [`Lumen_Project_Presentation.pptx`](Lumen_Project_Presentation.pptx) | Existing talk deck (kept for continuity) |

Editable HTML sources sit beside each PDF. Infographic masters are SVG; presentation-ready exports are PNG @2x.

## Infographics (`diagrams/`)

| File | Story |
|---|---|
| `appointment_value` | Why the moment before an appointment matters |
| `patient_journey` | Intended path from report excerpt to care-team questions |
| `scope_boundary` | What Lumen helps with vs what it will not do |
| `principles_infographic` | Four product commitments in plain language |
| `evidence_gate` | How a statement earns its place on screen |
| `information_flow` | Everyday-language flow + current demo disclosure |
| `trust_snapshot` | Honest status: checked vs not claimed |
| `validation_snapshot` | Compact verification strip for slides / one-pager |

Each diagram ships as `.svg` (edit) and `.png` (share / embed).

## Regenerating exports

```bash
cd report
npm install
npx playwright install chromium
npm run export
```

This refreshes all PNGs from SVG and reprints the three PDFs from HTML.

## Non-negotiable disclosures

- Synthetic-only, English-only software prototype
- Not medical advice, not a diagnostic tool, not clinically validated
- Model provider disabled by default in demos; live path returns no claims
- Polished result screens in demos are labeled synthetic UI fixtures, not live model output
- Fixture integrity numbers are not model accuracy or patient-outcome claims

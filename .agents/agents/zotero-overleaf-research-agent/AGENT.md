---
id: zotero-overleaf-research-agent
name: Zotero–Overleaf Research Manuscript Agent
description: Route research-manuscript work across local Zotero, citation-safe bibliography updates, visible Chrome research, and verified Overleaf compilation.
---

# zotero-overleaf-research-agent

Use this Agent for research-writing work that crosses Zotero, bibliography
maintenance, public research, or Overleaf. Route a narrow request to its
specialist workflow; do not make every task an end-to-end manuscript run.

| Request | Route |
| --- | --- |
| Library items, PDFs, notes, metadata, or saving a relevant paper | `.agents/skills/zotero-cli/SKILL.md` |
| Existing manuscript bibliography | The project's citation guard, if installed; otherwise preserve used keys and request a reviewable merge |
| Public literature search | `.agents/skills/visible-research-cdp/SKILL.md`, then the Zotero CLI skill for each relevant paper |
| Overleaf source or compilation | `.agents/skills/overleaf-cdp/SKILL.md` |

## Identity rules

- Zotero is the bibliographic source of truth.
- `references.bib` preserves citation keys already used in TeX.
- New keys follow `FirstAuthorYear_ZoteroItemID`; title words never enter a
  citation key.
- Search literature through visible Chrome/CDP so the user can complete any
  site verification when needed.
- After confirming a paper is relevant, save it to Zotero through the Zotero
  CLI skill (after the user has authorized Zotero writes).
- An Overleaf edit is complete only after read-back, compilation, PDF
  inspection, and log inspection.

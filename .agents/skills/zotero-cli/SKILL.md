---
name: zotero-cli
description: Save confirmed relevant literature to the user's Zotero library and read or update Zotero metadata with `zotero-cli`. Use for discovered papers, Zotero items, citations, PDFs, notes, or bibliography records.
---

# Zotero CLI

Use `zotero-cli` as the Zotero interface. Run `zotero-cli config` before the
first library operation and pass `--json` whenever parsing output.

For each paper confirmed relevant to the research question:

1. Search Zotero by DOI, URL, title, or author to avoid a duplicate.
2. If it is absent, add the record with its DOI or canonical URL.
3. Read the saved item's metadata and retain its Zotero item key for citation
   and bibliography work.

Before the first write, ensure the user has authorized the local Zotero write
workflow. Confirm only destructive actions, such as deletion, duplicate
merging, or large batch edits.

## Project PDF extraction

When a project PDF must be converted to Markdown, read `WORKSPACE_LAYOUT.md`
and run `.agents/scripts/extract_pdf_to_markdown.py`. It uses the project’s
local Docling dependency; never substitute model-generated extraction.

## Stable BibLaTeX updates

For an existing manuscript, do not overwrite `references.bib` with a raw
export. Use the included guard and inspect its dry-run first:

```bash
python3 .agents/skills/zotero-cli/scripts/sync_zotero_bibliography.py \
  --collection COLLECTION_KEY \
  --current references.bib \
  --lock .zotero/citation-key-lock.json \
  --tex main.tex \
  --dry-run
```

Run it again with `--apply` only after the dry-run is conflict-free, then
compile with Biber and inspect the rendered citations. The lock is local
Zotero state and must remain uncommitted. Read `reference.md` for the complete
CLI contract before using an unlisted command.

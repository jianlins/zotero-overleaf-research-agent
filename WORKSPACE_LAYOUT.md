# Workspace layout

This document is the directory contract for a manuscript project created from
this template. Keep durable, reviewable research decisions in Git; keep
downloaded source files and machine-generated full text as local caches.

| Path | Versioned? | Purpose |
| --- | --- | --- |
| Project root (`*.tex`, `chapters/`, figures, `references.bib`) | Yes | Manuscript source and the bibliography used by the manuscript. Zotero remains the bibliographic source of truth. |
| `references/pdf/` | No | Downloaded source PDFs. Name files with the Zotero item key when possible. |
| `references/markdown/` | No | Text extracted from PDFs for local search or analysis. Use the same base name as its source PDF. |
| `notes/` | Yes | Durable reading notes, argument notes, source summaries, and decision records. Link each source note to its Zotero key. |
| `plans/` | Yes | Bounded execution plans. Use `YYYY-MM-DD-topic.md`; retain completed plans as an audit trail. |
| `handoffs/` | Yes | Continuation briefs for another person or agent: current state, completed work, next actions, verification commands, and open risks. Use `YYYY-MM-DD-topic.md`. |
| `research-log.md` | Yes | Concise chronological record of searches, source checks, material decisions, and claim verification. |
| `.agents/` | Yes | Template-maintenance automation only; never put project research artifacts here. |

## Operating rules

- A PDF or extracted Markdown file is a disposable local artifact. Its durable
  trail is its Zotero item, the citation key in `references.bib`, and any
  related note or research-log entry.
- Convert a text-layer PDF with the deterministic extractor, not an ad-hoc
  model prompt. For example:

  ```bash
  uv run --python 3.12 \
    --with-requirements .agents/requirements-pdf-extraction.txt \
    python .agents/scripts/extract_pdf_to_markdown.py \
    --input references/pdf/ABCD1234.pdf
  ```

  The default output is `references/markdown/ABCD1234.md`. The converter uses
  Docling for layout-aware Markdown (including reading order and tables). Use
  `--output` to choose another local destination and `--force` only to replace
  an existing extraction. OCR is disabled by default; invoke `--ocr` only after
  preparing a supported local Docling OCR engine. Docling requires Python 3.10+
  and its dependency declaration is `.agents/requirements-pdf-extraction.txt`;
  after installing it into a compatible local environment, `python` may be used
  in place of `uv run`. Docling’s code is MIT-licensed; review the licenses of
  any separately selected models before enabling them.
- `references.bib` at the project root is the sole manuscript bibliography.
  The Zotero bibliography guard reads a collection or item selection from the
  local Zotero API, dry-runs a merge into that file, and writes it only when
  invoked with `--apply`:

  ```bash
  python3 .agents/skills/zotero-cli/scripts/sync_zotero_bibliography.py \
    --collection COLLECTION_KEY \
    --current references.bib \
    --lock .zotero/citation-key-lock.json \
    --tex main.tex \
    --dry-run
  ```

  After a conflict-free dry-run, repeat the same command with `--apply`.
  The guard writes `references.bib` and the untracked local key lock; it never
  changes the Zotero library or copies PDFs.
- Put interpretation and quotations needed for the manuscript in `notes/`,
  with a source citation and page number where applicable. Do not rely on an
  extracted Markdown file as the only record of a research decision.
- Create a plan when work has multiple dependent steps or needs a checkpoint;
  create a handoff when a different person or agent must resume the work.
- Keep `research-log.md` factual and short: date, action, source or query,
  result, and consequential decision.

The four working directories (`references/`, `notes/`, `plans/`, and
`handoffs/`) may begin empty. Their `.gitkeep` files preserve the shared
structure; remove a placeholder once real versioned content exists.

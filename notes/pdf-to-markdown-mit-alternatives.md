# MIT-licensed PDF-to-Markdown alternatives

Research date: 2026-10-29

## Recommendation: Docling

[Docling](https://github.com/docling-project/docling) is the strongest
strict-MIT candidate for this template. Its official project documentation
states that the codebase is MIT-licensed, runs locally (including air-gapped
environments), and supports PDF layout, reading order, table structure,
formulas, OCR, and Markdown export. It provides both a CLI and a Python API:

```python
from docling.document_converter import DocumentConverter

result = DocumentConverter().convert("references/pdf/ITEMKEY.pdf")
markdown = result.document.export_to_markdown()
```

Its CLI can also write a structured Markdown file directly:

```bash
docling references/pdf/ITEMKEY.pdf --output references/markdown/
```

Docling requires Python 3.10 or newer; the current host's `python3` is 3.9,
so a controlled converter should use a Python 3.10+ environment (for example,
through `uv`). The Docling code license is MIT, but its README directs users to
review the licenses of individually selected models. Keep the default local
pipeline unless a separately reviewed model is deliberately enabled.

Sources: [Docling README: features, API, CLI, Python requirement, MIT caveat](https://github.com/docling-project/docling/blob/main/README.md), [Docling product page: local/offline and MIT claims](https://docling.ai/).

## Secondary choice: Microsoft MarkItDown

[MarkItDown](https://github.com/microsoft/markitdown) is MIT-licensed and a
lighter-weight local converter. Its README states that it supports PDF input
and aims to preserve headings, lists, tables, and links as Markdown. Its PDF
extra can be installed separately and its CLI has a direct output-file flag:

```bash
markitdown references/pdf/ITEMKEY.pdf -o references/markdown/ITEMKEY.md
```

MarkItDown's own documentation says the output targets text-analysis tools and
may not be the best choice for high-fidelity, human-facing conversion. Use it
when lightweight conversion matters more than research-paper layout recovery.
It requires Python 3.10--3.14.

Sources: [MarkItDown README: MIT, supported structure and PDF support](https://github.com/microsoft/markitdown), [MarkItDown CLI and optional PDF extra](https://github.com/microsoft/markitdown#usage).

## Building blocks, not full converters

| Library | License | What it supplies | Why it is not the default |
| --- | --- | --- | --- |
| [pdfplumber](https://github.com/jsvine/pdfplumber) | MIT | Page text, word coordinates, tables, and visual debugging | No Markdown exporter and no OCR; a project-specific reconstruction layer would be required. |
| [pdfminer.six](https://github.com/pdfminer/pdfminer.six) | MIT | PDF parsing, layout analysis, and text extraction | No table extraction or Markdown exporter. |
| [Camelot](https://github.com/camelot-dev/camelot) | MIT | Table extraction from digital PDFs | Table-only; it cannot form a full paper Markdown document. |

Sources: [pdfplumber license](https://github.com/jsvine/pdfplumber/blob/stable/LICENSE.txt), [pdfplumber capability and limitations](https://github.com/jsvine/pdfplumber/blob/stable/README.md#comparison-to-other-libraries).

## Excluded from a strict-MIT default

- `pymupdf4llm` / PyMuPDF: AGPL or commercial license, so unsuitable for a
  default MIT template without a separate licensing choice. Source:
  [PyMuPDF FAQ](https://pymupdf.readthedocs.io/en/latest/faq/index.html).
- `pypdf`: BSD-3-Clause, not MIT; it extracts page text but is not a
  structured Markdown converter. Source: [official PyPI metadata](https://pypi.org/project/pypdf/), [pdfplumber comparison](https://github.com/jsvine/pdfplumber/blob/stable/README.md#comparison-to-other-libraries).
- Apache-2.0 tools can be permissive and MIT-compatible in many contexts, but
  they do not meet a strict "MIT-only dependency" policy and are not treated
  as candidates here.

## Proposed template policy

Adopt Docling as the controlled PDF-to-Markdown backend. The project converter
should call its local Python API, write only to `references/markdown/`, refuse
to overwrite without `--force`, and keep OCR opt-in. The agent instruction
should direct PDF conversion to that script rather than a model prompt. Record
the selected backend and model setting in the output front matter or research
log so extractions are reproducible.

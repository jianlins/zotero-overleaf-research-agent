#!/usr/bin/env python3
"""Convert a local PDF into structured Markdown with Docling.

The script never delegates text reconstruction to an LLM. OCR is opt-in because
it requires a locally configured Docling OCR engine and can change output.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Source PDF path")
    parser.add_argument(
        "--output",
        type=Path,
        help="Destination Markdown path; defaults beside the PDF or in references/markdown/",
    )
    parser.add_argument(
        "--force", action="store_true", help="Replace an existing output file"
    )
    parser.add_argument(
        "--ocr",
        action="store_true",
        help="Enable Docling OCR; requires a supported local OCR engine",
    )
    return parser.parse_args()


def default_output(pdf: Path) -> Path:
    if pdf.parent.name == "pdf":
        return pdf.parent.parent / "markdown" / (pdf.stem + ".md")
    return pdf.with_suffix(".md")


def extract(pdf: Path, output: Path, force: bool, use_ocr: bool) -> None:
    try:
        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.pipeline_options import PdfPipelineOptions
        from docling.document_converter import DocumentConverter, PdfFormatOption
    except ImportError as error:
        raise RuntimeError(
            "Docling is required. Run this script with Python 3.10+ and install "
            "the dependency declared in "
            ".agents/requirements-pdf-extraction.txt."
        ) from error

    if not pdf.is_file():
        raise RuntimeError("Source PDF does not exist: {}".format(pdf))
    if output.exists() and not force:
        raise RuntimeError("Output already exists: {} (pass --force to replace it)".format(output))

    try:
        pipeline_options = PdfPipelineOptions(
            do_ocr=use_ocr,
            do_table_structure=True,
        )
        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )
        markdown = converter.convert(pdf).document.export_to_markdown()
    except Exception as error:
        raise RuntimeError("Could not convert PDF: {}".format(pdf)) from error

    if not markdown.strip():
        raise RuntimeError(
            "No extractable text was found. Re-run with --ocr after configuring a local Docling OCR engine."
        )

    source_display = pdf.as_posix()
    content = [
        "---",
        "source_pdf: {}".format(source_display),
        "extracted_on: {}".format(date.today().isoformat()),
        "extractor: Docling",
        "ocr: {}".format(str(use_ocr).lower()),
        "---",
        "",
        "# {}".format(pdf.stem),
        "",
    ]
    content.append(markdown.strip())

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(content), encoding="utf-8")
    print("Wrote Markdown to {}".format(output))


def main() -> int:
    args = parse_args()
    pdf = args.input.expanduser()
    output = (args.output or default_output(pdf)).expanduser()
    try:
        extract(pdf, output, args.force, args.ocr)
    except RuntimeError as error:
        print("error: {}".format(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

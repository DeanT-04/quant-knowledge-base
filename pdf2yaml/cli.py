"""Command-line interface for pdf2yaml."""

from __future__ import annotations
import argparse
import sys
import os
from pathlib import Path
from typing import List, Tuple
from .models import Options
from .pipeline import pdf_to_yaml


def _is_relative_to(path: Path, base: Path) -> bool:
    """Check if path is relative to base (Python 3.8+ compatible)."""
    try:
        path.resolve().relative_to(base.resolve())
        return True
    except ValueError:
        return False


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="pdf2yaml",
        description="Convert PDF documents to clean, layout-aware YAML structures.",
    )
    parser.add_argument("inputs", nargs="*", default=["data/pdfs"], help="Input PDF file(s) or directories (default: data/pdfs).")
    parser.add_argument("-o", "--output", default="data/parsed", help="Output YAML file or directory (default: data/parsed).")
    parser.add_argument("--ocr", choices=["off", "auto", "tesseract"], default="auto", help="OCR mode.")
    parser.add_argument("--lang", default="eng", help="OCR language (e.g. eng, deu).")
    parser.add_argument("--no-tables", action="store_true", help="Disable table detection.")
    parser.add_argument("--no-math", action="store_true", help="Disable math/equation detection.")
    parser.add_argument("--preview", action="store_true", help="Preview mode (first 3 pages only).")

    args = parser.parse_args()

    opts = Options(
        ocr_mode=args.ocr,
        ocr_lang=args.lang,
        detect_tables=not args.no_tables,
        detect_math=not args.no_math,
        preview_only=args.preview,
    )

    pdf_tasks: List[Tuple[Path, Path]] = []
    output_arg = Path(args.output) if args.output else Path("data/parsed")
    base_pdfs = Path("data/pdfs")

    for item in args.inputs:
        path = Path(item)
        if path.is_file() and path.suffix.lower() == ".pdf":
            if output_arg.suffix.lower() == ".yaml":
                target_file = output_arg
            else:
                if base_pdfs.exists() and _is_relative_to(path, base_pdfs):
                    rel = path.resolve().relative_to(base_pdfs.resolve())
                    target_file = output_arg / rel.with_suffix(".yaml")
                else:
                    target_file = output_arg / (path.stem + ".yaml")
            pdf_tasks.append((path, target_file))

        elif path.is_dir():
            found_pdfs = sorted(list(path.glob("**/*.pdf")))
            for pdf_path in found_pdfs:
                if base_pdfs.exists() and _is_relative_to(pdf_path, base_pdfs) and path.resolve() != base_pdfs.resolve():
                    rel = pdf_path.resolve().relative_to(base_pdfs.resolve())
                else:
                    rel = pdf_path.resolve().relative_to(path.resolve())
                
                target_file = output_arg / rel.with_suffix(".yaml")
                pdf_tasks.append((pdf_path, target_file))

    if not pdf_tasks:
        print(f"Error: No valid PDF files found in inputs: {args.inputs}", file=sys.stderr)
        sys.exit(1)

    for pdf_path, target_file in pdf_tasks:
        target_file.parent.mkdir(parents=True, exist_ok=True)
        print(f"[pdf2yaml] Converting {pdf_path} -> {target_file}...")
        try:
            pdf_to_yaml(str(pdf_path), str(target_file), options=opts)
            print(f"[pdf2yaml] Saved -> {target_file}")
        except Exception as e:
            print(f"[pdf2yaml] ERROR converting {pdf_path.name}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()

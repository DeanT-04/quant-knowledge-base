"""Docling layout-aware scientific PDF parser with fallback support."""

import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


class PaperParser:
    """Parses scientific PDFs using Docling into Markdown and JSON."""

    def __init__(self, converter: Optional[Any] = None, do_table_structure: bool = False) -> None:
        self._converter = converter
        self.do_table_structure = do_table_structure

    @property
    def converter(self) -> Any:
        if self._converter is None:
            from docling.datamodel.base_models import InputFormat
            from docling.datamodel.pipeline_options import PdfPipelineOptions
            from docling.document_converter import DocumentConverter, PdfFormatOption

            options = PdfPipelineOptions()
            options.do_ocr = False  # Disable OCR to prevent RAM spikes / std::bad_alloc on digital PDFs
            options.do_table_structure = self.do_table_structure

            self._converter = DocumentConverter(
                format_options={
                    InputFormat.PDF: PdfFormatOption(pipeline_options=options)
                }
            )
        return self._converter


    def parse_pdf(self, pdf_path: Path | str) -> Tuple[str, Dict[str, Any]]:
        """Parses a local PDF file and returns (markdown_text, json_dict)."""
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {path}")

        try:
            result = self.converter.convert(str(path))
            markdown_text = result.document.export_to_markdown()
            json_dict = result.document.export_to_dict()
            return markdown_text, json_dict
        except Exception as err:
            # Robust fallback for corrupted or unusual PDF layouts
            return self._fallback_parse(path, error_msg=str(err))

    def _fallback_parse(self, path: Path, error_msg: str) -> Tuple[str, Dict[str, Any]]:
        """Fallback parser using PyPDF / basic text extraction."""
        try:
            import pypdf
            reader = pypdf.PdfReader(str(path))
            pages_text = []
            for idx, page in enumerate(reader.pages):
                txt = page.extract_text() or ""
                pages_text.append(f"## Page {idx + 1}\n\n{txt}")
            full_md = f"# Document: {path.stem}\n\n" + "\n\n".join(pages_text)
            json_dict = {"title": path.stem, "pages_count": len(reader.pages), "parse_mode": "fallback", "error": error_msg}
            return full_md, json_dict
        except Exception:
            fallback_md = f"# Document: {path.stem}\n\n*Unable to parse PDF text layer. Error: {error_msg}*"
            return fallback_md, {"title": path.stem, "parse_mode": "error", "error": error_msg}


def safe_print(msg: str) -> None:
    """Prints a message, falling back to replacing unsupported Unicode characters if encoding fails."""
    try:
        print(msg, flush=True)
    except UnicodeEncodeError:
        try:
            import sys
            encoding = sys.stdout.encoding or "utf-8"
            print(msg.encode(encoding, errors="replace").decode(encoding), flush=True)
        except Exception:
            print(msg.encode("ascii", errors="replace").decode("ascii"), flush=True)


def parse_pdf_directory(
    input_dir: Path | str,
    output_dir: Path | str,
    parser: Optional[PaperParser] = None,
) -> Dict[str, int]:
    """Parses all PDFs in input_dir recursively, replicating directory structure into output_dir."""
    in_path = Path(input_dir)
    out_path = Path(output_dir)
    if not in_path.exists():
        raise FileNotFoundError(f"Input directory not found: {in_path}")

    if parser is None:
        parser = PaperParser()

    stats = {"processed": 0, "skipped": 0, "failed": 0}
    pdf_files = list(in_path.rglob("*.pdf"))
    total = len(pdf_files)
    safe_print(f"Found {total} PDF file(s) in {in_path}")

    for idx, pdf_file in enumerate(pdf_files, 1):
        rel_path = pdf_file.relative_to(in_path)
        dest_dir = out_path / rel_path.parent
        dest_dir.mkdir(parents=True, exist_ok=True)

        md_file = dest_dir / f"{pdf_file.stem}.md"
        json_file = dest_dir / f"{pdf_file.stem}.json"

        if md_file.exists() and json_file.exists() and md_file.stat().st_size > 0 and json_file.stat().st_size > 0:
            stats["skipped"] += 1
            continue

        safe_print(f"[{idx}/{total}] Parsing {rel_path} ...")
        try:
            md_text, json_dict = parser.parse_pdf(pdf_file)
            md_file.write_text(md_text, encoding="utf-8")
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(json_dict, f, indent=2, ensure_ascii=False)
            stats["processed"] += 1
        except Exception as e:
            safe_print(f"Error parsing {pdf_file}: {e}")
            stats["failed"] += 1

    return stats


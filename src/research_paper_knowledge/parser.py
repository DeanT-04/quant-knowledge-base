"""Docling layout-aware scientific PDF parser with fallback support.

Design goals, in priority order:

1. Accuracy: nothing gets silently dropped. Equations are transcribed
   (``do_formula_enrichment``) and tables keep their row/column structure
   (``do_table_structure`` + accurate TableFormer + cell matching against the
   real PDF text layer). Earlier runs of this pipeline had both switched off,
   which left ~94% of parsed papers with "formula-not-decoded" placeholders
   instead of math, and tables collapsed into unstructured text blobs.
2. Throughput: everything that doesn't serve this corpus (OCR on
   born-digital PDFs, picture classification/description, code enrichment,
   page/picture image rendering) stays off, hardware acceleration (CUDA /
   MPS / multi-threaded CPU) is used automatically, and multiple PDFs are
   processed concurrently across worker processes.
3. Idempotency: re-running the pipeline never redoes work. A file is only
   reprocessed if its existing output is missing or was produced by the old,
   lower-fidelity settings (see ``is_output_complete``).
"""

from __future__ import annotations

import os
# Configure CPU thread counts for PyTorch / ONNX to avoid thread thrashing on laptop CPU
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"

import json
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Recognized formula/table quality problems that mark an existing output as
# "needs reprocessing" rather than "already done".
_INCOMPLETE_PARSE_MODES = {"fallback", "error"}


def _subprocess_parse_pdf_worker(
    pdf_path: Path,
    do_table_structure: bool,
    do_formula_enrichment: bool,
    table_mode: str,
    num_threads: int,
    device: str,
    timeout: float,
    queue: Any,
) -> None:
    try:
        from research_paper_knowledge.parser import PaperParser
        # Create an isolated parser instance inside the subprocess
        parser = PaperParser(
            do_table_structure=do_table_structure,
            do_formula_enrichment=do_formula_enrichment,
            table_mode=table_mode,
            num_threads=num_threads,
            device=device,
            timeout=timeout,
            use_watchdog=False  # Prevent infinite subprocess recursion
        )
        result = parser.converter.convert(str(pdf_path))
        if result.errors:
            timeout_errors = [e for e in result.errors if "timeout" in str(e.error_message).lower() or e.category.name == 'TIMEOUT']
            if timeout_errors:
                raise TimeoutError(f"Docling conversion timed out: {timeout_errors[0].error_message}")
        md = result.document.export_to_markdown()
        js = result.document.export_to_dict()
        queue.put((True, md, js))
    except Exception as e:
        queue.put((False, str(e), None))


class PaperParser:
    """Parses scientific PDFs using Docling into Markdown and JSON."""

    def __init__(
        self,
        converter: Optional[Any] = None,
        do_table_structure: bool = True,
        do_formula_enrichment: bool = True,
        table_mode: str = "ACCURATE",
        num_threads: Optional[int] = None,
        device: Optional[str] = None,
        timeout: float = 180.0,
        use_watchdog: bool = False,
    ) -> None:
        """
        Args:
            converter: Inject a pre-built Docling converter (mainly for
                tests). If omitted, one is lazily built from the flags below.
            do_table_structure: Recover real table rows/columns instead of
                collapsing them into one text blob.
            do_formula_enrichment: Transcribe equations instead of leaving
                "formula-not-decoded" placeholders.
            table_mode: "ACCURATE" (default, best quality) or "FAST"
                (quicker, slightly less precise on complex tables).
            num_threads: CPU threads for inference. Defaults to all cores.
            device: "auto" (default; picks CUDA/MPS if available, else CPU),
                "cpu", "cuda", or "mps".
            timeout: Maximum seconds to allow Docling to process a single PDF.
            use_watchdog: Set to True to run parser in a monitored subprocess.
        """
        self._converter = converter
        self.do_table_structure = do_table_structure
        self.do_formula_enrichment = do_formula_enrichment
        self.table_mode = table_mode
        self.num_threads = num_threads or os.cpu_count() or 4
        self.device = device
        self.timeout = timeout
        self.use_watchdog = use_watchdog

    @property
    def converter(self) -> Any:
        if self._converter is None:
            from docling.datamodel.accelerator_options import (
                AcceleratorDevice,
                AcceleratorOptions,
            )
            from docling.datamodel.base_models import InputFormat
            from docling.datamodel.pipeline_options import (
                PdfPipelineOptions,
                TableFormerMode,
                TableStructureOptions,
            )
            from docling.document_converter import DocumentConverter, PdfFormatOption

            device_map = {
                "auto": AcceleratorDevice.AUTO,
                "cpu": AcceleratorDevice.CPU,
                "cuda": AcceleratorDevice.CUDA,
                "mps": AcceleratorDevice.MPS,
            }
            device = device_map.get((self.device or "auto").lower(), AcceleratorDevice.AUTO)

            options = PdfPipelineOptions()

            # Born-digital scientific PDFs already have a text layer, so OCR
            # is both unnecessary and by far the most expensive stage.
            # Keeping it off also avoids the RAM spikes (std::bad_alloc)
            # noted in the README.
            options.do_ocr = False

            # Full table structure recovery. `do_cell_matching=True` maps
            # recognized cells back onto the PDF's real text layer (more
            # accurate than the model's own OCR guess) which is ideal here
            # since we already know these are digital PDFs.
            options.do_table_structure = self.do_table_structure
            options.table_structure_options = TableStructureOptions(
                mode=(
                    TableFormerMode.ACCURATE
                    if self.table_mode.upper() == "ACCURATE"
                    else TableFormerMode.FAST
                ),
                do_cell_matching=True,
            )

            # Transcribe equations instead of leaving them undecoded.
            options.do_formula_enrichment = self.do_formula_enrichment

            # Everything below stays off on purpose: these are the most
            # expensive optional stages in Docling, and none of them adds
            # value for a text/table/formula-focused quant research corpus.
            options.do_code_enrichment = False
            options.do_picture_classification = False
            options.do_picture_description = False
            options.generate_page_images = False
            options.generate_picture_images = False
            options.document_timeout = self.timeout

            options.accelerator_options = AcceleratorOptions(
                num_threads=self.num_threads,
                device=device,
            )

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

        # If a custom converter is injected (e.g., in unit tests with MagicMock)
        # or watchdog is disabled, run the conversion directly in-process.
        if self._converter is not None or not self.use_watchdog:
            try:
                result = self.converter.convert(str(path))
                if result.errors:
                    timeout_errors = [e for e in result.errors if "timeout" in str(e.error_message).lower() or e.category.name == 'TIMEOUT']
                    if timeout_errors:
                        raise TimeoutError(f"Docling conversion timed out: {timeout_errors[0].error_message}")
                markdown_text = result.document.export_to_markdown()
                json_dict = result.document.export_to_dict()
                return markdown_text, json_dict
            except Exception as err:
                return self._fallback_parse(path, error_msg=str(err))

        import multiprocessing
        queue = multiprocessing.Queue()
        p = multiprocessing.Process(
            target=_subprocess_parse_pdf_worker,
            args=(
                path,
                self.do_table_structure,
                self.do_formula_enrichment,
                self.table_mode,
                self.num_threads,
                self.device,
                self.timeout,
                queue
            )
        )
        try:
            p.start()
            p.join(timeout=self.timeout + 5.0)  # Add a small buffer for process startup
            if p.is_alive():
                p.terminate()
                p.join()
                return self._fallback_parse(
                    path,
                    error_msg=f"Docling conversion timed out after {self.timeout} seconds"
                )
            if not queue.empty():
                ok, val1, val2 = queue.get()
                if ok:
                    return val1, val2
                else:
                    return self._fallback_parse(path, error_msg=val1)
            else:
                return self._fallback_parse(path, error_msg="Subprocess exited unexpectedly without returning results")
        except Exception as e:
            if p.is_alive():
                p.terminate()
                p.join()
            return self._fallback_parse(path, error_msg=f"Watchdog exception: {e}")

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


def recommended_worker_count() -> int:
    """A sane default number of worker processes for batch parsing.

    A single GPU is best kept saturated by one process (extra workers would
    just contend for the same VRAM and slow each other down). On CPU-only
    machines, several worker processes running concurrently gives a real
    throughput win since Docling's own internal threading rarely uses every
    core efficiently for a single document.
    """
    try:
        import torch

        if torch.cuda.is_available() or (
            hasattr(torch.backends, "mps") and torch.backends.mps.is_available()
        ):
            return 1
    except ImportError:
        pass

    # Limit workers by available RAM to avoid std::bad_alloc OOM crashes
    # Docling processes are memory-heavy (~3-4 GB per worker on complex PDFs)
    max_workers_by_ram = 8
    try:
        import psutil
        total_ram_gb = psutil.virtual_memory().total / (1024 ** 3)
        available_ram_gb = psutil.virtual_memory().available / (1024 ** 3)
        workers_by_total = int(total_ram_gb / 6.0)
        workers_by_available = int(available_ram_gb / 4.0)
        max_workers_by_ram = max(1, min(workers_by_total, workers_by_available))
    except ImportError:
        pass

    cores = os.cpu_count() or 4
    return max(1, min(cores, max_workers_by_ram, 8))


def is_output_complete(md_path: Path, json_path: Path) -> bool:
    """Returns True only if a previously-parsed output is already full-fidelity.

    This is what makes re-runs idempotent without redoing correct work: a
    file is considered "done" only if it has no undecoded formulas and no
    empty/unstructured tables. Anything produced by the old
    (table-structure-off, formula-enrichment-off) settings, or by the pypdf
    fallback path, is treated as incomplete and will be reprocessed.
    """
    if not (md_path.exists() and json_path.exists()):
        return False
    if md_path.stat().st_size == 0 or json_path.stat().st_size == 0:
        return False

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return False

    if data.get("parse_mode") in _INCOMPLETE_PARSE_MODES:
        return False

    texts = data.get("texts", [])
    if any(t.get("label") == "formula" and not t.get("text") for t in texts):
        return False

    for table in data.get("tables", []):
        table_data = table.get("data", {}) or {}
        if table_data.get("num_rows", 0) == 0 or table_data.get("num_cols", 0) == 0:
            return False

    return True


def _output_paths(pdf_file: Path, in_path: Path, out_path: Path) -> Tuple[Path, Path]:
    rel_path = pdf_file.relative_to(in_path)
    dest_dir = out_path / rel_path.parent
    return dest_dir / f"{pdf_file.stem}.md", dest_dir / f"{pdf_file.stem}.json"


def _plan_tasks(
    input_dir: Path | str, output_dir: Path | str, force: bool
) -> Tuple[Path, Path, List[Path], int]:
    in_path = Path(input_dir)
    out_path = Path(output_dir)
    if not in_path.exists():
        raise FileNotFoundError(f"Input directory not found: {in_path}")

    pdf_files = sorted(in_path.rglob("*.pdf"))
    to_process: List[Path] = []
    skipped = 0
    for pdf_file in pdf_files:
        md_file, json_file = _output_paths(pdf_file, in_path, out_path)
        if not force and is_output_complete(md_file, json_file):
            skipped += 1
            continue
        to_process.append(pdf_file)
    return in_path, out_path, to_process, skipped


_WORKER_PARSER: Optional[PaperParser] = None


def _worker_parse_one(
    args: Tuple[Path, Path, Path, Dict[str, Any]]
) -> Tuple[str, bool, Optional[str]]:
    """Runs in a worker process. Builds/reuses a per-process PaperParser so
    the (expensive) Docling models are only ever loaded once per worker,
    not once per file."""
    global _WORKER_PARSER
    pdf_file, md_file, json_file, parser_kwargs = args
    parser = _WORKER_PARSER
    if parser is None:
        parser = PaperParser(**parser_kwargs)
        _WORKER_PARSER = parser
    try:
        md_text, json_dict = parser.parse_pdf(pdf_file)
        md_file.parent.mkdir(parents=True, exist_ok=True)
        md_file.write_text(md_text, encoding="utf-8")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(json_dict, f, indent=2, ensure_ascii=False)
        return (str(pdf_file), True, None)
    except Exception as e:  # noqa: BLE001
        return (str(pdf_file), False, str(e))


def parse_pdf_directory(
    input_dir: Path | str,
    output_dir: Path | str,
    parser: Optional[PaperParser] = None,
    max_workers: int = 1,
    parser_kwargs: Optional[Dict[str, Any]] = None,
    force: bool = False,
) -> Dict[str, int]:
    """Parses all PDFs in input_dir recursively, replicating directory structure into output_dir.

    Args:
        parser: Pre-built parser to reuse for every file (single-process
            mode only; mainly for tests/dependency injection).
        max_workers: >1 fans work out across worker processes, each with its
            own Docling model instance. Ignored (treated as 1) if `parser`
            is explicitly supplied, since a live object can't be shared
            across processes.
        parser_kwargs: Constructor kwargs used to build the PaperParser in
            each worker process (multi-worker mode) or as the default parser
            (single-worker mode) when `parser` isn't supplied.
        force: Reprocess every PDF even if its output already looks
            complete. Off by default so re-runs stay fast and idempotent.
    """
    in_path, out_path, pdf_files, skipped = _plan_tasks(input_dir, output_dir, force)
    total_found = skipped + len(pdf_files)
    safe_print(
        f"Found {total_found} PDF file(s) in {in_path} "
        f"({skipped} already complete, {len(pdf_files)} to (re)parse)"
    )

    stats = {"processed": 0, "skipped": skipped, "failed": 0}
    if not pdf_files:
        return stats

    if max_workers > 1 and parser is None:
        tasks = []
        for pdf_file in pdf_files:
            md_file, json_file = _output_paths(pdf_file, in_path, out_path)
            tasks.append((pdf_file, md_file, json_file, parser_kwargs or {}))

        total = len(tasks)
        done = 0
        with ProcessPoolExecutor(max_workers=max_workers) as pool:
            futures = {pool.submit(_worker_parse_one, t): t[0] for t in tasks}
            for future in as_completed(futures):
                done += 1
                pdf_path, ok, error = future.result()
                rel = Path(pdf_path).relative_to(in_path)
                if ok:
                    stats["processed"] += 1
                    safe_print(f"[{done}/{total}] Parsed {rel}")
                else:
                    stats["failed"] += 1
                    safe_print(f"[{done}/{total}] Error parsing {rel}: {error}")
        return stats

    # Single-process path (also used for injected `parser`, e.g. in tests).
    active_parser = parser if parser is not None else PaperParser(**(parser_kwargs or {}))
    total = len(pdf_files)
    for idx, pdf_file in enumerate(pdf_files, 1):
        md_file, json_file = _output_paths(pdf_file, in_path, out_path)
        md_file.parent.mkdir(parents=True, exist_ok=True)
        safe_print(f"[{idx}/{total}] Parsing {pdf_file.relative_to(in_path)} ...")
        try:
            md_text, json_dict = active_parser.parse_pdf(pdf_file)
            md_file.write_text(md_text, encoding="utf-8")
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(json_dict, f, indent=2, ensure_ascii=False)
            stats["processed"] += 1
        except Exception as e:  # noqa: BLE001
            safe_print(f"Error parsing {pdf_file}: {e}")
            stats["failed"] += 1

    return stats

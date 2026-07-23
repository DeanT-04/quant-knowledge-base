import argparse
import sys
from pathlib import Path

# Configure console stdout/stderr to be encoding-robust on Windows
if sys.version_info >= (3, 7):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
        sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")
    except Exception:
        pass

from research_paper_knowledge.parser import parse_pdf_directory, recommended_worker_count


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Batch-parse PDFs into Markdown + JSON.")
    p.add_argument("--input", type=Path, default=Path("data/pdfs"), help="Input PDF directory (default: data/pdfs)")
    p.add_argument("--output", type=Path, default=Path("data/parsed"), help="Output directory (default: data/parsed)")
    p.add_argument(
        "--workers",
        type=int,
        default=None,
        help="Number of parallel worker processes. Defaults to an auto-detected value "
        "(1 if a GPU is available, else up to 8 CPU cores).",
    )
    p.add_argument(
        "--table-mode",
        choices=["accurate", "fast"],
        default="accurate",
        help="TableFormer mode: 'accurate' (default) or 'fast' for a speed/quality tradeoff.",
    )
    p.add_argument("--no-formula", action="store_true", help="Disable equation transcription.")
    p.add_argument("--no-tables", action="store_true", help="Disable table structure recovery.")
    p.add_argument(
        "--device",
        choices=["auto", "cpu", "cuda", "mps"],
        default="auto",
        help="Inference device. 'auto' (default) picks CUDA/MPS if available, else CPU.",
    )
    p.add_argument(
        "--timeout",
        type=float,
        default=180.0,
        help="Maximum seconds to allow Docling to process a single PDF before timing out (default: 180.0).",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="Reprocess every PDF even if its output already looks complete "
        "(by default, already-complete outputs are skipped so re-runs are fast).",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    workers = args.workers or recommended_worker_count()

    parser_kwargs = {
        "do_table_structure": not args.no_tables,
        "do_formula_enrichment": not args.no_formula,
        "table_mode": args.table_mode.upper(),
        "device": args.device,
        "timeout": args.timeout,
    }

    print("Starting batch PDF parsing pipeline...")
    print(f"Input Directory:  {args.input.resolve()}")
    print(f"Output Directory: {args.output.resolve()}")
    print(f"Workers:          {workers}")
    print(f"Table structure:  {parser_kwargs['do_table_structure']} (mode={parser_kwargs['table_mode']})")
    print(f"Formula enrich.:  {parser_kwargs['do_formula_enrichment']}")
    print(f"Device:           {parser_kwargs['device']}")
    print(f"Timeout guard:    {parser_kwargs['timeout']}s")
    print(f"Force reprocess:  {args.force}")

    stats = parse_pdf_directory(
        args.input,
        args.output,
        max_workers=workers,
        parser_kwargs=parser_kwargs,
        force=args.force,
    )
    print("\n--- Parsing Complete ---")
    print(f"Processed: {stats['processed']}")
    print(f"Skipped:   {stats['skipped']}")
    print(f"Failed:    {stats['failed']}")


if __name__ == "__main__":
    main()

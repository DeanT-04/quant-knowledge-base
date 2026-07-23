import sys
from pathlib import Path

# Configure console stdout/stderr to be encoding-robust on Windows
if sys.version_info >= (3, 7):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
        sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")
    except Exception:
        pass

from research_paper_knowledge.parser import parse_pdf_directory


def main() -> None:
    input_dir = Path("data/pdfs")
    output_dir = Path("data/parsed")

    print(f"Starting batch PDF parsing pipeline...")
    print(f"Input Directory:  {input_dir.resolve()}")
    print(f"Output Directory: {output_dir.resolve()}")

    stats = parse_pdf_directory(input_dir, output_dir)
    print("\n--- Parsing Complete ---")
    print(f"Processed: {stats['processed']}")
    print(f"Skipped:   {stats['skipped']}")
    print(f"Failed:    {stats['failed']}")



if __name__ == "__main__":
    main()

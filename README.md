# 📈 Quant Knowledge Base

[![Python Version](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://python.org)
[![Coverage](https://img.shields.io/badge/coverage-100%25-success.svg)](https://github.com/DeanT-04/quant-knowledge-base)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Built with uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

A lightweight, high-performance, modular Python pipeline for quantitative research paper discovery, parallel downloading, layout-aware PDF parsing, and structured, AI-readable storage. Built for quantitative researchers, algorithm developers, and RAG (Retrieval-Augmented Generation) applications.

---

## 🚀 Key Features

*   🔎 **ArXiv Discovery**: Automated querying and metadata extraction using the `arxiv` API for targeted research discovery.
*   ⚡ **Asynchronous Downloader**: Concurrent, high-speed multi-file PDF downloading powered by `httpx` and Python's `asyncio` loop.
*   📑 **Layout-Aware Parsing**: Rich structural conversions of scientific PDFs to Markdown and JSON utilizing IBM's advanced `docling` engine, preserving complex tables, formulas, and structural hierarchies.
*   🛡️ **Smart Fallback Engine**: Automatic grace fallbacks to light-weight `pypdf` text extraction in case of memory-intensive OCR or parsing errors, preventing RAM spikes (`std::bad_alloc`).
*   🗂️ **Category-Based Storage**: Unified archiving that maintains hierarchical folder layouts with an automatically updated, indexed `catalog.jsonl` catalog.
*   🧪 **100% Test Coverage**: Full suite of unit and integration tests covering path anomalies, mocks, and fallbacks.

---

## 📁 Repository Structure

```text
quant-knowledge-base/
├── data/
│   ├── metadata/          # Unified metadata catalogs (catalog.json, catalog.jsonl)
│   ├── pdfs/              # Category-classified raw PDF files
│   └── parsed/            # Layout-aware parsed Markdown & JSON outputs
├── src/
│   └── research_paper_knowledge/
│       ├── __init__.py    # Package initialization
│       └── parser.py      # Core parser (Docling & PyPDF fallback logic)
├── tests/
│   └── test_parser.py     # Comprehensive test suite (100% coverage)
├── main.py                # Pipeline execution entry point
├── pyproject.toml         # Modern project metadata & dependency declarations
└── uv.lock                # Deterministic dependency lockfile
```

---

## 🛠️ Installation & Setup

This repository uses [uv](https://github.com/astral-sh/uv), a fast, modern Python package installer and resolver.

### Prerequisites

Ensure you have `uv` installed. If not, install it via:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex
```

### Quickstart

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/DeanT-04/quant-knowledge-base.git
    cd quant-knowledge-base
    ```

2.  **Run the Parsing Pipeline**:
    The pipeline processes PDFs from `data/pdfs/` and outputs parsed files to `data/parsed/`:
    ```bash
    uv run python main.py
    ```

3.  **Run Tests & Coverage**:
    Verify that the test suite runs with 100% test coverage:
    ```bash
    uv run pytest --cov=research_paper_knowledge --cov-report=term-missing
    ```

---

## 💡 Programmatic Usage

You can import and integrate the parser directly into your quantitative research script:

```python
from pathlib import Path
from research_paper_knowledge.parser import PaperParser

# Initialize the parser
parser = PaperParser(do_table_structure=True)

# Parse a single scientific PDF
pdf_path = Path("data/pdfs/algo_trading_general/sample.pdf")
markdown_content, json_metadata = parser.parse_pdf(pdf_path)

print("Parsed Markdown Snippet:")
print(markdown_content[:500])
```

To run the batch parser on an entire folder structured by categories:

```python
from pathlib import Path
from research_paper_knowledge.parser import parse_pdf_directory

# Process folder and replicate its categories structure
stats = parse_pdf_directory(
    input_dir=Path("data/pdfs"),
    output_dir=Path("data/parsed")
)

print(f"Batch completed: {stats}")
```

---

## ⚙️ Configuration & Performance Notes

*   **Memory Safety**: OCR is disabled (`options.do_ocr = False`) by default during Docling conversions. This prevents memory spikes and out-of-memory (`std::bad_alloc`) exceptions when processing dense digital scientific documents.
*   **Table Structure Extraction**: Can be toggled on/off by adjusting `do_table_structure` in the `PaperParser` constructor.
*   **Incremental Processing**: The parser scans for existing parsed `.md` and `.json` outputs, avoiding redundant parses and making it efficient for growing databases.

---

## 📄 License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

"""
Unit tests for scripts/build_quant_db.py SQLite FTS5 database builder.
"""

import sqlite3
import tempfile
import yaml
from pathlib import Path
import pytest

from scripts.build_quant_db import (
    normalize_paper_id,
    init_db,
    parse_yaml_paper,
    extract_paper_records,
    index_parsed_directory,
)


def test_normalize_paper_id():
    # arXiv ID file stem
    p1 = Path("data/parsed/crypto/2501.06032_a_modern_paradigm.yaml")
    assert normalize_paper_id(p1) == "arXiv:2501.06032"

    p2 = Path("data/parsed/algo_trading/0704.2259_wiretap.yaml")
    assert normalize_paper_id(p2) == "arXiv:0704.2259"

    # Non-arXiv stem
    p3 = Path("data/parsed/custom/my_trading_model.yaml")
    assert normalize_paper_id(p3) == "my_trading_model"


def test_init_db(tmp_path):
    db_file = tmp_path / "test_brain.db"
    conn = init_db(db_file)
    assert db_file.exists()

    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = {row[0] for row in cursor.fetchall()}

    assert "papers" in tables
    assert "sections" in tables
    assert "equations" in tables
    assert "citations" in tables
    assert "entities" in tables
    assert "papers_fts" in tables
    conn.close()


def test_extract_paper_records(tmp_path):
    paper_dir = tmp_path / "crypto"
    paper_dir.mkdir(parents=True)
    yaml_file = paper_dir / "2501.06032_sample.yaml"

    sample_data = {
        "metadata": {
            "title": "A Modern Paradigm for Algorithmic Trading",
            "authors": ["J.B. Glattfelder", "T. Houweling"],
            "total_pages": 5,
            "source_file": "data/pdfs/crypto/2501.06032.pdf"
        },
        "pages": [
            {
                "page_number": 1,
                "sections": [
                    {
                        "title": "Abstract",
                        "paragraphs": [
                            "We introduce a novel framework for developing fully-automated trading algorithms.",
                            "See previous work in arXiv:2307.13832."
                        ]
                    },
                    {
                        "title": "Section 1 Formula",
                        "paragraphs": [
                            "The scaling law is given by f(x) = C \\alpha x = 1.0"
                        ]
                    }
                ]
            }
        ]
    }

    with open(yaml_file, "w", encoding="utf-8") as f:
        yaml.dump(sample_data, f)

    parsed = parse_yaml_paper(yaml_file)
    assert parsed is not None

    paper_rec, sections, equations, citations = extract_paper_records(parsed, yaml_file)

    assert paper_rec["paper_id"] == "arXiv:2501.06032"
    assert paper_rec["title"] == "A Modern Paradigm for Algorithmic Trading"
    assert paper_rec["category"] == "crypto"
    assert "Glattfelder" in paper_rec["authors"]

    assert len(sections) == 2
    assert "novel framework" in paper_rec["abstract"]

    assert len(equations) >= 1
    assert any("f(x)" in eq["latex_raw"] for eq in equations)

    assert len(citations) == 1
    assert citations[0]["target_paper_id"] == "arXiv:2307.13832"


def test_index_parsed_directory_and_fts_query(tmp_path):
    data_dir = tmp_path / "parsed_data"
    cat_dir = data_dir / "algo_trading_general"
    cat_dir.mkdir(parents=True)

    yaml_file = cat_dir / "0801.4047_no_arbitrage.yaml"
    sample_data = {
        "metadata": {
            "title": "No Arbitrage Conditions for Simple Trading Strategies",
            "authors": ["Alex Black"],
            "total_pages": 3,
            "source_file": "data/pdfs/0801.4047.pdf"
        },
        "pages": [
            {
                "page_number": 1,
                "sections": [
                    {
                        "title": "Introduction",
                        "paragraphs": [
                            "We prove no-arbitrage bounds for delta-hedged momentum portfolios in intrinsic time."
                        ]
                    }
                ]
            }
        ]
    }

    with open(yaml_file, "w", encoding="utf-8") as f:
        yaml.dump(sample_data, f)

    db_path = tmp_path / "second_brain.db"
    stats = index_parsed_directory(data_dir, db_path)

    assert stats["papers"] == 1
    assert stats["sections"] == 1

    # Test FTS5 full text search query
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute("SELECT paper_id, title FROM papers_fts WHERE papers_fts MATCH 'arbitrage';")
    results = cursor.fetchall()
    assert len(results) == 1
    assert results[0][0] == "arXiv:0801.4047"
    assert "No Arbitrage" in results[0][1]

    cursor.execute("SELECT paper_id, title FROM papers_fts WHERE papers_fts MATCH 'momentum';")
    results_mom = cursor.fetchall()
    assert len(results_mom) == 1

    conn.close()

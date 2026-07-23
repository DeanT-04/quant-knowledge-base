"""
Unit tests for quant_brain_cli.py, create_benchmark.py, and run_benchmark.py
"""

import json
import sqlite3
from pathlib import Path
import pytest

from scripts.quant_brain_cli import hybrid_search, query_fts5, query_graph, query_wiki
from scripts.create_benchmark import generate_benchmark_suite
from scripts.run_benchmark import run_benchmark, write_benchmark_reports
from scripts.build_quant_db import init_db


@pytest.fixture
def test_setup(tmp_path):
    db_path = tmp_path / "test_brain.db"
    conn = init_db(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO papers (paper_id, title, authors, category, source_file, total_pages, abstract)
    VALUES ('arXiv:0809.1949', 'Protocol Channels', 'Steffen Wendzel', 'algo_trading_general', 'data/parsed/algo/paper.yaml', 4, 'Covert data hiding');
    """)

    cursor.execute("""
    INSERT INTO papers_fts (paper_id, title, authors, category, content_text)
    VALUES ('arXiv:0809.1949', 'Protocol Channels', 'Steffen Wendzel', 'algo_trading_general', 'Protocol channel covert data hiding');
    """)

    conn.commit()
    conn.close()

    # Graph json
    graph_path = tmp_path / "graph.json"
    graph_data = {
        "directed": False,
        "multigraph": False,
        "graph": {},
        "nodes": [
            {"id": "arXiv:0809.1949", "label": "Paper: Protocol Channels"},
            {"id": "Category:algo_trading_general", "label": "Category: Algo Trading"}
        ],
        "links": [
            {"source": "arXiv:0809.1949", "target": "Category:algo_trading_general", "relation": "IN_CATEGORY"}
        ]
    }
    graph_path.write_text(json.dumps(graph_data), encoding="utf-8")

    # Wiki dir
    wiki_dir = tmp_path / "wiki"
    wiki_dir.mkdir()
    (wiki_dir / "index.md").write_text("# Wiki Index\n- [Algo Trading](community_0.md)", encoding="utf-8")

    return db_path, graph_path, wiki_dir


def test_quant_brain_cli(test_setup):
    db_path, graph_path, wiki_dir = test_setup

    res = hybrid_search(db_path, graph_path, wiki_dir, "Wendzel")
    assert res["fts_matches"] >= 1
    assert res["token_count"] > 0
    assert res["elapsed_ms"] >= 0


def test_create_and_run_benchmark(tmp_path, test_setup):
    db_path, graph_path, wiki_dir = test_setup
    suite_path = tmp_path / "suite.json"

    suite = generate_benchmark_suite(db_path, suite_path)
    assert len(suite) == 10
    assert suite_path.exists()

    summary = run_benchmark(suite_path, db_path, graph_path, wiki_dir)
    assert "method_a" in summary
    assert "method_b" in summary
    assert "method_c" in summary

    md_path = tmp_path / "results.md"
    txt_path = tmp_path / "results.txt"
    write_benchmark_reports(summary, md_path, txt_path)

    assert md_path.exists()
    assert txt_path.exists()
    assert "BENCHMARK REPORT" in txt_path.read_text(encoding="utf-8")

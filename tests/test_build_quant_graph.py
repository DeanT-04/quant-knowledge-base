"""
Unit tests for scripts/build_quant_graph.py Graphify knowledge graph builder.
"""

import json
import sqlite3
from pathlib import Path
import pytest

from scripts.build_quant_db import init_db, extract_paper_records
from scripts.build_quant_graph import build_extraction_from_db, generate_agent_wiki
from graphify.build import build_from_json
from graphify.cluster import cluster, score_all


@pytest.fixture
def mock_db(tmp_path):
    db_path = tmp_path / "mock_second_brain.db"
    conn = init_db(db_path)
    cursor = conn.cursor()

    # Insert sample paper
    cursor.execute("""
    INSERT INTO papers (paper_id, title, authors, category, source_file, total_pages, abstract)
    VALUES ('arXiv:2501.06032', 'Delta Engine', 'J.B. Glattfelder', 'crypto', 'data/parsed/crypto/paper.yaml', 5, 'Abstract test');
    """)

    # Insert equation
    cursor.execute("""
    INSERT INTO equations (paper_id, page_number, latex_raw, description, section_title)
    VALUES ('arXiv:2501.06032', 1, 'f(x) = C \\alpha x', 'Formula test', 'Section 1');
    """)

    # Insert citation
    cursor.execute("""
    INSERT INTO papers (paper_id, title, authors, category, source_file, total_pages, abstract)
    VALUES ('arXiv:2307.13832', 'MFIN Paper', 'Stefan Zohren', 'crypto', 'data/parsed/crypto/paper2.yaml', 3, 'Ref test');
    """)

    cursor.execute("""
    INSERT INTO citations (source_paper_id, target_paper_id, citation_text)
    VALUES ('arXiv:2501.06032', 'arXiv:2307.13832', 'Cites MFIN');
    """)

    conn.commit()
    conn.close()
    return db_path


def test_build_extraction_from_db(mock_db):
    extraction = build_extraction_from_db(mock_db)
    assert "nodes" in extraction
    assert "edges" in extraction
    assert len(extraction["nodes"]) >= 3  # Category + 2 Papers + Author/Formula
    assert len(extraction["edges"]) >= 3

    node_ids = {n["id"] for n in extraction["nodes"]}
    assert "Category:crypto" in node_ids
    assert "arXiv:2501.06032" in node_ids
    assert "arXiv:2307.13832" in node_ids

    # Check relations
    relations = {e["relation"] for e in extraction["edges"]}
    assert "IN_CATEGORY" in relations
    assert "CITES" in relations


def test_generate_agent_wiki(tmp_path):
    extraction = {
        "nodes": [
            {"id": "arXiv:1", "type": "paper", "label": "Paper 1", "source_file": "paper1.yaml"},
            {"id": "Category:crypto", "type": "concept", "label": "Crypto", "source_file": "crypto.yaml"}
        ],
        "edges": [
            {"source": "arXiv:1", "target": "Category:crypto", "relation": "IN_CATEGORY", "extraction_type": "EXTRACTED", "confidence": "EXTRACTED", "source_location": "paper1.yaml", "source_file": "paper1.yaml"}
        ],
        "hyperedges": []
    }

    G = build_from_json(extraction, root=".", directed=False)
    communities = cluster(G)
    labels = {0: "Crypto Community"}

    wiki_dir = tmp_path / "wiki"
    generate_agent_wiki(G, communities, labels, wiki_dir)

    assert (wiki_dir / "index.md").exists()
    community_files = list(wiki_dir.glob("community_*.md"))
    assert len(community_files) >= 1

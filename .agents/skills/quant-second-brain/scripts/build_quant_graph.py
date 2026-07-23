"""
Quantitative Finance Knowledge Graph Builder for Graphify
Constructs a unified, high-precision Graphify knowledge graph from second_brain.db.
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any

from graphify.build import build_from_json
from graphify.cluster import cluster, score_all
from graphify.analyze import god_nodes, surprising_connections, suggest_questions
from graphify.report import generate
from graphify.export import to_json, to_html
from graphify.diagnostics import diagnose_extraction, format_diagnostic_report


def build_extraction_from_db(db_path: Path) -> Dict[str, Any]:
    """Extract nodes and edges from second_brain.db to construct Graphify extraction JSON."""
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    nodes = []
    edges = []
    seen_nodes = set()

    # 1. Index Category God Nodes
    categories = cursor.execute("SELECT DISTINCT category FROM papers;").fetchall()
    for cat in categories:
        cat_name = cat[0]
        cat_node_id = f"Category:{cat_name}"
        if cat_node_id not in seen_nodes:
            seen_nodes.add(cat_node_id)
            nodes.append({
                "id": cat_node_id,
                "label": f"Category: {cat_name.replace('_', ' ').title()}",
                "type": "concept",
                "source_file": "data/parsed/" + cat_name
            })

    # 2. Index Papers
    papers = cursor.execute("SELECT paper_id, title, authors, category, source_file, abstract FROM papers;").fetchall()
    for p in papers:
        pid, title, authors, category, source_file, abstract = p
        paper_node_id = pid
        if paper_node_id not in seen_nodes:
            seen_nodes.add(paper_node_id)
            nodes.append({
                "id": paper_node_id,
                "label": f"Paper: {title[:60]}",
                "type": "paper",
                "source_file": source_file,
                "authors": authors,
                "category": category,
                "abstract": abstract[:300] if abstract else ""
            })

        # Edge: Paper -> Category
        cat_node_id = f"Category:{category}"
        edges.append({
            "source": paper_node_id,
            "target": cat_node_id,
            "relation": "IN_CATEGORY",
            "extraction_type": "EXTRACTED",
            "confidence": "EXTRACTED",
            "source_file": source_file,
            "source_location": f"{source_file}"
        })

        # Authors
        if authors:
            for author in [a.strip() for a in authors.split(",") if a.strip()][:3]:
                author_node_id = f"Author:{author.replace(' ', '_')}"
                if author_node_id not in seen_nodes:
                    seen_nodes.add(author_node_id)
                    nodes.append({
                        "id": author_node_id,
                        "label": f"Author: {author}",
                        "type": "concept",
                        "source_file": source_file
                    })
                edges.append({
                    "source": paper_node_id,
                    "target": author_node_id,
                    "relation": "AUTHORED_BY",
                    "extraction_type": "EXTRACTED",
                    "confidence": "EXTRACTED",
                    "source_file": source_file,
                    "source_location": f"{source_file}"
                })

    # 3. Index Math Equations / Formulas (group shared formulas)
    equations = cursor.execute("SELECT DISTINCT latex_raw, paper_id, section_title FROM equations WHERE length(latex_raw) > 5 LIMIT 2000;").fetchall()
    formula_map = {}
    for latex, pid, sec_title in equations:
        clean_latex = latex.strip()
        if clean_latex not in formula_map:
            formula_map[clean_latex] = []
        formula_map[clean_latex].append((pid, sec_title))

    formula_idx = 1
    for latex, paper_secs in formula_map.items():
        if len(paper_secs) >= 1:
            formula_node_id = f"Formula:Math_{formula_idx}"
            formula_idx += 1
            if formula_node_id not in seen_nodes:
                seen_nodes.add(formula_node_id)
                nodes.append({
                    "id": formula_node_id,
                    "label": f"Formula: {latex[:40]}...",
                    "type": "concept",
                    "source_file": "data/parsed",
                    "latex": latex
                })
            for pid, sec_title in paper_secs[:5]:
                if pid in seen_nodes:
                    edges.append({
                        "source": pid,
                        "target": formula_node_id,
                        "relation": "USES_FORMULA",
                        "extraction_type": "EXTRACTED",
                        "confidence": "EXTRACTED",
                        "source_file": "data/parsed",
                        "source_location": f"{pid}#{sec_title}"
                    })

    # 4. Index Citations
    citations = cursor.execute("SELECT source_paper_id, target_paper_id, citation_text FROM citations WHERE target_paper_id IS NOT NULL;").fetchall()
    for src_id, tgt_id, text in citations:
        if src_id in seen_nodes and tgt_id in seen_nodes:
            edges.append({
                "source": src_id,
                "target": tgt_id,
                "relation": "CITES",
                "extraction_type": "EXTRACTED",
                "confidence": "EXTRACTED",
                "source_file": "data/parsed",
                "source_location": f"{src_id}"
            })

    conn.close()

    return {
        "nodes": nodes,
        "edges": edges,
        "hyperedges": [],
        "input_tokens": 0,
        "output_tokens": 0
    }


def generate_agent_wiki(G, communities, labels, output_dir: Path):
    """Generate agent-crawlable markdown wiki articles per community cluster."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # index.md
    index_lines = [
        "# Quantitative Finance Knowledge Base - Agent Wiki\n",
        "## Subsystem Communities\n"
    ]
    
    for comm_id, nodes_in_comm in communities.items():
        label = labels.get(comm_id, f"Community {comm_id}")
        filename = f"community_{comm_id}.md"
        index_lines.append(f"- **[{label}]({filename})**: {len(nodes_in_comm)} nodes")
        
        # Write community article
        comm_lines = [
            f"# {label}\n",
            f"**Community ID**: {comm_id} | **Total Nodes**: {len(nodes_in_comm)}\n",
            "## Key Nodes\n"
        ]
        for n in nodes_in_comm[:50]:
            node_data = G.nodes.get(n, {})
            node_type = node_data.get("type", "concept")
            node_label = node_data.get("label", n)
            comm_lines.append(f"- `{n}` ({node_type}): {node_label}")
        
        Path(output_dir / filename).write_text("\n".join(comm_lines), encoding="utf-8")

    Path(output_dir / "index.md").write_text("\n".join(index_lines), encoding="utf-8")


def main():
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    db_path = Path("second_brain.db")
    out_dir = Path("graphify-out")
    out_dir.mkdir(parents=True, exist_ok=True)

    if not db_path.exists():
        print("Error: second_brain.db not found!")
        return

    print("Step 1: Extracting nodes and edges from second_brain.db...")
    extraction = build_extraction_from_db(db_path)
    print(f"Extracted {len(extraction['nodes'])} nodes and {len(extraction['edges'])} edges.")

    # Save extraction json
    Path("graphify-out/.graphify_extract.json").write_text(json.dumps(extraction, indent=2, ensure_ascii=False), encoding="utf-8")

    # Step 2: Build Graphify Graph & Run Health Check
    print("Step 2: Running Graph Health Audit...")
    health_summary = diagnose_extraction(extraction, directed=False, root="data/parsed")
    print(format_diagnostic_report(health_summary))

    print("Step 3: Building graph and clustering communities...")
    G = build_from_json(extraction, root="data/parsed", directed=False)
    communities = cluster(G)
    cohesion = score_all(G, communities)
    gods = god_nodes(G)
    surprises = surprising_connections(G, communities)

    # Assign community labels
    labels = {}
    for cid, nodes_in_c in communities.items():
        cats = [G.nodes[n].get("category", "") for n in nodes_in_c if n in G.nodes and "category" in G.nodes[n]]
        top_cat = max(set(cats), key=cats.count) if cats else f"Cluster {cid}"
        labels[cid] = f"{top_cat.replace('_', ' ').title()} Group ({len(nodes_in_c)} nodes)"

    questions = suggest_questions(G, communities, labels)

    # Step 4: Export Graphify Outputs
    print("Step 4: Exporting graph.json, graph.html, GRAPH_REPORT.md, and Agent Wiki...")
    to_json(G, communities, "graphify-out/graph.json")
    to_html(G, communities, "graphify-out/graph.html", community_labels=labels, node_limit=10000)

    detection = {"total_files": 1640, "total_words": 20000000}
    tokens = {"input": 0, "output": 0}
    report = generate(G, communities, cohesion, labels, gods, surprises, detection, tokens, "data/parsed", suggested_questions=questions)
    Path("graphify-out/GRAPH_REPORT.md").write_text(report, encoding="utf-8")

    # Export Agent Wiki
    wiki_dir = out_dir / "wiki"
    generate_agent_wiki(G, communities, labels, wiki_dir)

    print("\n==========================================")
    print("Graphify Second Brain Build Complete!")
    print(f"  Total Nodes:       {G.number_of_nodes()}")
    print(f"  Total Edges:       {G.number_of_edges()}")
    print(f"  Communities:       {len(communities)}")
    print(f"  God Nodes:         {len(gods)}")
    print(f"  Outputs Generated: graphify-out/graph.json, graphify-out/graph.html, graphify-out/GRAPH_REPORT.md, graphify-out/wiki/")
    print("==========================================")


if __name__ == "__main__":
    main()

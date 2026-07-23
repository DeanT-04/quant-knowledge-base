"""
Unified Custom CLI Query Helper for Quantitative Finance Second Brain
Performs fast hybrid search across SQLite FTS5 (second_brain.db), Graphify (graph.json), and Agent Wiki (graphify-out/wiki/).
"""

import json
import sqlite3
import time
import argparse
from pathlib import Path
from typing import Dict, List, Any
import networkx as nx


def query_fts5(db_path: Path, query_str: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Execute FTS5 keyword search in second_brain.db."""
    if not db_path.exists():
        return []

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Escape quotes
    clean_q = query_str.replace("'", "''").replace('"', '')
    sql = f"SELECT paper_id, title, authors, category, content_text FROM papers_fts WHERE papers_fts MATCH '{clean_q}' LIMIT {limit};"
    
    results = []
    try:
        rows = cursor.execute(sql).fetchall()
        for r in rows:
            results.append({
                "paper_id": r[0],
                "title": r[1],
                "authors": r[2],
                "category": r[3],
                "snippet": r[4][:300] if r[4] else ""
            })
    except Exception as e:
        # Fallback to LIKE
        like_sql = f"SELECT paper_id, title, authors, category, abstract FROM papers WHERE title LIKE '%{clean_q}%' OR abstract LIKE '%{clean_q}%' LIMIT {limit};"
        try:
            rows = cursor.execute(like_sql).fetchall()
            for r in rows:
                results.append({
                    "paper_id": r[0],
                    "title": r[1],
                    "authors": r[2],
                    "category": r[3],
                    "snippet": r[4][:300] if r[4] else ""
                })
        except Exception:
            pass

    conn.close()
    return results


def query_graph(graph_json_path: Path, query_str: str, max_neighbors: int = 5) -> List[Dict[str, Any]]:
    """Traverse Graphify graph.json for 1-hop neighborhoods around matching nodes."""
    if not graph_json_path.exists():
        return []

    try:
        data = json.loads(graph_json_path.read_text(encoding="utf-8"))
        G = nx.node_link_graph(data, edges="links")
    except Exception:
        return []

    query_lower = query_str.lower()
    matching_nodes = [n for n in G.nodes if query_lower in str(n).lower() or query_lower in str(G.nodes[n].get("label", "")).lower()]

    results = []
    for node in matching_nodes[:3]:
        neighbors = list(G.neighbors(node))[:max_neighbors]
        results.append({
            "seed_node": node,
            "label": G.nodes[node].get("label", node),
            "neighbors": [
                {"id": n, "label": G.nodes[n].get("label", n), "relation": G.edges[node, n].get("relation", "")}
                for n in neighbors if G.has_edge(node, n)
            ]
        })

    return results


def query_wiki(wiki_dir: Path, query_str: str) -> List[Dict[str, Any]]:
    """Search Agent Wiki markdown files for relevant community articles."""
    if not wiki_dir.exists():
        return []

    index_path = wiki_dir / "index.md"
    if not index_path.exists():
        return []

    index_text = index_path.read_text(encoding="utf-8")
    query_lower = query_str.lower()
    matches = []
    for line in index_text.splitlines():
        if query_lower in line.lower():
            matches.append(line)

    return [{"matching_line": m} for m in matches[:3]]


def hybrid_search(db_path: Path, graph_json_path: Path, wiki_dir: Path, query_str: str) -> Dict[str, Any]:
    """Execute complete hybrid retrieval pipeline across FTS5, Graphify, and Wiki."""
    t0 = time.time()

    fts_results = query_fts5(db_path, query_str)
    graph_results = query_graph(graph_json_path, query_str)
    wiki_results = query_wiki(wiki_dir, query_str)

    elapsed_ms = round((time.time() - t0) * 1000, 2)
    
    # Estimate token count of result (~4 chars per token)
    result_json = json.dumps({"fts": fts_results, "graph": graph_results, "wiki": wiki_results}, ensure_ascii=False)
    token_count = len(result_json) // 4

    return {
        "query": query_str,
        "elapsed_ms": elapsed_ms,
        "token_count": token_count,
        "fts_matches": len(fts_results),
        "graph_matches": len(graph_results),
        "wiki_matches": len(wiki_results),
        "results": {
            "fts": fts_results,
            "graph": graph_results,
            "wiki": wiki_results
        }
    }


def main():
    parser = argparse.ArgumentParser(description="Unified Custom CLI Query Engine for Second Brain")
    parser.add_argument("--query", type=str, required=True, help="Search query string")
    parser.add_argument("--db-path", type=str, default="second_brain.db", help="Path to SQLite database")
    parser.add_argument("--graph-path", type=str, default="graphify-out/graph.json", help="Path to graph.json")
    parser.add_argument("--wiki-dir", type=str, default="graphify-out/wiki", help="Path to wiki directory")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    res = hybrid_search(Path(args.db_path), Path(args.graph_path), Path(args.wiki_dir), args.query)

    if args.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print(f"=== Hybrid Search Results for '{args.query}' ===")
        print(f"Time: {res['elapsed_ms']} ms | Estimated Tokens: {res['token_count']}")
        print(f"Matches -> FTS5: {res['fts_matches']} | Graph: {res['graph_matches']} | Wiki: {res['wiki_matches']}\n")
        
        if res["results"]["fts"]:
            print("--- Top FTS5 Paper Matches ---")
            for item in res["results"]["fts"]:
                print(f"• [{item['paper_id']}] {item['title']} ({item['category']})")
        
        if res["results"]["graph"]:
            print("\n--- Top Graphify Neighborhoods ---")
            for item in res["results"]["graph"]:
                print(f"• Seed: {item['seed_node']} -> {len(item['neighbors'])} neighbors")


if __name__ == "__main__":
    main()

"""
Unified Custom CLI Query Helper for Quantitative Finance Second Brain
Performs fast hybrid search across SQLite FTS5 (second_brain.db), Graphify (graph.json), and Agent Wiki (graphify-out/wiki/).
"""

import sys
import json
import re
import sqlite3
import time
import argparse
from pathlib import Path
from typing import Dict, List, Any
import networkx as nx


def clean_tokens(query_str: str) -> List[str]:
    """Extract clean alphanumeric search tokens (length >= 2)."""
    return [w for w in re.findall(r'[a-zA-Z0-9]+', query_str) if len(w) >= 2]


def normalize_query_display(query_str: str) -> str:
    """Clean and normalize raw query text to lowercase for single-line display."""
    if not query_str:
        return ""
    return " ".join(query_str.strip().split()).lower()



def query_fts5(db_path: Path, query_str: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Execute multi-tier FTS5 keyword search in second_brain.db with graceful fallbacks."""
    if not db_path.exists():
        return []

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Check for direct arXiv ID in query string
    arxiv_match = re.search(r"(\d{4}\.\d{4,5})", query_str)
    if arxiv_match:
        target_id = f"arXiv:{arxiv_match.group(1)}"
        try:
            rows = cursor.execute("SELECT paper_id, title, authors, category, abstract FROM papers WHERE paper_id LIKE ? LIMIT 1", (f"%{arxiv_match.group(1)}%",)).fetchall()
            if rows:
                conn.close()
                return [{
                    "paper_id": rows[0][0],
                    "title": rows[0][1],
                    "authors": rows[0][2],
                    "category": rows[0][3],
                    "snippet": rows[0][4][:300] if rows[0][4] else ""
                }]
        except Exception:
            pass

    tokens = clean_tokens(query_str)
    if not tokens:
        conn.close()
        return []

    # Build progressive query strategies
    strategies = []
    
    # 1. Exact phrase query (clean alphanumeric)
    strategies.append('"' + " ".join(tokens) + '"')
    
    # 2. All tokens AND query
    if len(tokens) > 1:
        strategies.append(" AND ".join(f'"{t}"' for t in tokens))
        
    # 3. Top longest/distinct terms (up to 5) AND query
    sorted_tokens = sorted(set(tokens), key=lambda x: len(x), reverse=True)[:5]
    if len(sorted_tokens) > 1:
        strategies.append(" AND ".join(f'"{t}"' for t in sorted_tokens))

    # 4. Top 3 tokens AND query
    if len(sorted_tokens) >= 3:
        strategies.append(" AND ".join(f'"{t}"' for t in sorted_tokens[:3]))

    # Execute FTS5 strategies in order
    results = []
    seen_ids = set()

    for fts_q in strategies:
        try:
            sql = """
            SELECT f.paper_id, f.title, f.authors, f.category, f.content_text, p.source_file
            FROM papers_fts f
            LEFT JOIN papers p ON f.paper_id = p.paper_id
            WHERE papers_fts MATCH ? LIMIT ?
            """
            rows = cursor.execute(sql, (fts_q, limit)).fetchall()
            for r in rows:
                pid = r[0]
                if pid not in seen_ids:
                    seen_ids.add(pid)
                    arxiv_num = pid.replace("arXiv:", "").strip()
                    src_file = r[5] or ""
                    abs_path = Path(src_file).resolve() if src_file else None
                    results.append({
                        "paper_id": pid,
                        "title": r[1],
                        "authors": r[2],
                        "category": r[3],
                        "snippet": r[4][:300] if r[4] else "",
                        "source_file": src_file,
                        "web_url": f"https://arxiv.org/abs/{arxiv_num}" if arxiv_num else "",
                        "pdf_url": f"https://arxiv.org/pdf/{arxiv_num}.pdf" if arxiv_num else "",
                        "file_uri": abs_path.as_uri() if abs_path and abs_path.exists() else ""
                    })
            if len(results) >= limit:
                break
        except Exception:
            continue

    # Fallback to SQL LIKE if FTS5 returned 0 matches
    if not results and sorted_tokens:
        like_clauses = " AND ".join(["f.content_text LIKE ?"] * len(sorted_tokens[:3]))
        like_params = [f"%{t}%" for t in sorted_tokens[:3]] + [limit]
        like_sql = f"""
        SELECT f.paper_id, f.title, f.authors, f.category, f.content_text, p.source_file
        FROM papers_fts f
        LEFT JOIN papers p ON f.paper_id = p.paper_id
        WHERE {like_clauses} LIMIT ?
        """
        try:
            rows = cursor.execute(like_sql, like_params).fetchall()
            for r in rows:
                pid = r[0]
                if pid not in seen_ids:
                    seen_ids.add(pid)
                    arxiv_num = pid.replace("arXiv:", "").strip()
                    src_file = r[5] or ""
                    abs_path = Path(src_file).resolve() if src_file else None
                    results.append({
                        "paper_id": pid,
                        "title": r[1],
                        "authors": r[2],
                        "category": r[3],
                        "snippet": r[4][:300] if r[4] else "",
                        "source_file": src_file,
                        "web_url": f"https://arxiv.org/abs/{arxiv_num}" if arxiv_num else "",
                        "pdf_url": f"https://arxiv.org/pdf/{arxiv_num}.pdf" if arxiv_num else "",
                        "file_uri": abs_path.as_uri() if abs_path and abs_path.exists() else ""
                    })
        except Exception:
            pass

    conn.close()
    return results[:limit]


def query_graph(graph_json_path: Path, query_str: str, max_neighbors: int = 5) -> List[Dict[str, Any]]:
    """Traverse Graphify graph.json using scored keyword matching around nodes."""
    if not graph_json_path.exists():
        return []

    try:
        data = json.loads(graph_json_path.read_text(encoding="utf-8"))
        G = nx.node_link_graph(data, edges="links")
    except Exception:
        return []

    tokens = set(clean_tokens(query_str.lower()))
    if not tokens:
        return []

    scored_nodes = []
    for n in G.nodes:
        label = str(G.nodes[n].get("label", n)).lower()
        node_id = str(n).lower()
        
        # Calculate overlap score
        matches = sum(1 for t in tokens if t in label or t in node_id)
        if matches > 0:
            scored_nodes.append((matches, n))

    scored_nodes.sort(key=lambda x: x[0], reverse=True)

    results = []
    for score, node in scored_nodes[:3]:
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
    """Search Agent Wiki markdown files using keyword overlap scoring."""
    if not wiki_dir.exists():
        return []

    index_path = wiki_dir / "index.md"
    if not index_path.exists():
        return []

    tokens = set(clean_tokens(query_str.lower()))
    if not tokens:
        return []

    index_text = index_path.read_text(encoding="utf-8")
    scored_lines = []
    for line in index_text.splitlines():
        line_lower = line.lower()
        matches = sum(1 for t in tokens if t in line_lower)
        if matches > 0:
            scored_lines.append((matches, line))

    scored_lines.sort(key=lambda x: x[0], reverse=True)
    return [{"matching_line": m[1]} for m in scored_lines[:3]]


def hybrid_search(db_path: Path, graph_json_path: Path, wiki_dir: Path, query_str: str, limit: int = 3, snippet_len: int = 200) -> Dict[str, Any]:
    """Execute complete hybrid retrieval pipeline across FTS5, Graphify, and Wiki."""
    t0 = time.time()

    fts_results = query_fts5(db_path, query_str, limit=limit)
    for item in fts_results:
        item["snippet"] = item["snippet"][:snippet_len]

    graph_results = query_graph(graph_json_path, query_str)
    wiki_results = query_wiki(wiki_dir, query_str)

    elapsed_ms = round((time.time() - t0) * 1000, 2)
    
    # Estimate token count of result (~4 chars per token)
    result_json = json.dumps({"fts": fts_results, "graph": graph_results, "wiki": wiki_results}, ensure_ascii=False)
    token_count = len(result_json) // 4

    return {
        "query": query_str,
        "query_clean": normalize_query_display(query_str),
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


def lookup_paper(db_path: Path, paper_id: str, section_filter: str = None, top_sections: int = 3, snippet_len: int = 300) -> Dict[str, Any]:
    """Retrieve details and top/matching sections for a specific paper_id from second_brain.db."""
    if not db_path.exists():
        return {"error": "Database file not found"}

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute("SELECT paper_id, title, authors, category, source_file, total_pages, abstract FROM papers WHERE paper_id = ?", (paper_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return {"error": f"Paper ID '{paper_id}' not found"}

    paper_data = {
        "paper_id": row[0],
        "title": row[1],
        "authors": row[2],
        "category": row[3],
        "source_file": row[4],
        "total_pages": row[5],
        "abstract": row[6][:500] if row[6] else "",
        "sections": []
    }

    try:
        cursor.execute("SELECT section_title, content_text FROM sections WHERE paper_id = ?", (paper_id,))
        sec_rows = cursor.fetchall()
        
        filtered_secs = []
        if section_filter:
            filter_tokens = clean_tokens(section_filter.lower())
            for sec in sec_rows:
                sec_text = (sec[0] + " " + (sec[1] or "")).lower()
                matches = sum(1 for t in filter_tokens if t in sec_text)
                if matches > 0:
                    filtered_secs.append((matches, sec[0], sec[1]))
            filtered_secs.sort(key=lambda x: x[0], reverse=True)
            sec_rows_to_use = [(s[1], s[2]) for s in filtered_secs[:top_sections]]
        else:
            sec_rows_to_use = sec_rows[:top_sections]

        for sec in sec_rows_to_use:
            paper_data["sections"].append({
                "title": sec[0],
                "snippet": sec[1][:snippet_len] if sec[1] else ""
            })
    except Exception:
        pass

    conn.close()
    return paper_data


def format_text_output(res: Dict[str, Any]) -> str:
    """Format search results into an ultra-dense, line-delimited key-value summary (low-token text format)."""
    lines = []
    lines.append(f"[METRICS] query='{res.get('query','')}' elapsed_ms={res.get('elapsed_ms')} est_tokens={res.get('token_count')}")
    
    results = res.get("results", {})
    if results.get("fts"):
        lines.append("--- FTS MATCHES ---")
        for item in results["fts"]:
            lines.append(f"• ID: {item['paper_id']} | Title: {item['title'][:60]} | Snippet: {item['snippet'][:150]}")
            
    if results.get("graph"):
        lines.append("--- GRAPH MATCHES ---")
        for item in results["graph"]:
            nbrs = ", ".join([n['id'] for n in item.get('neighbors', [])[:3]])
            lines.append(f"• Seed: {item['seed_node']} -> [{nbrs}]")
            
    if results.get("wiki"):
        lines.append("--- WIKI MATCHES ---")
        for item in results["wiki"]:
            lines.append(f"• {item['matching_line'][:120]}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Unified Custom CLI Query Engine for Second Brain")
    parser.add_argument("--query", type=str, default=None, help="Search query string")
    parser.add_argument("--paper-id", type=str, default=None, help="Lookup exact paper details by ID (e.g. arXiv:0804.1123)")
    parser.add_argument("--snippet-len", type=int, default=200, help="Snippet character limit")
    parser.add_argument("--db-path", type=str, default="second_brain.db", help="Path to SQLite database")
    parser.add_argument("--graph-path", type=str, default="graphify-out/graph.json", help="Path to graph.json")
    parser.add_argument("--wiki-dir", type=str, default="graphify-out/wiki", help="Path to wiki directory")
    parser.add_argument("--json", action="store_true", help="Output formatted JSON")
    parser.add_argument("--compact", action="store_true", help="Output minified single-line JSON for ultra low tokens")
    parser.add_argument("--text", action="store_true", help="Output dense line-delimited key-value summary")
    parser.add_argument("--limit", type=int, default=3, help="Maximum records to return (default: 3)")
    parser.add_argument("--top-sections", type=int, default=3, help="Max section snippets for paper-id lookup (default: 3)")
    parser.add_argument("--section-filter", type=str, default=None, help="Filter sections by keyword in paper-id lookup")
    args = parser.parse_args()

    if args.paper_id:
        res = lookup_paper(Path(args.db_path), args.paper_id, section_filter=args.section_filter, top_sections=args.top_sections, snippet_len=args.snippet_len)
        if args.json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
        else:
            print(json.dumps(res, separators=(',', ':'), ensure_ascii=False))
        return

    if not args.query:
        parser.error("Either --query or --paper-id must be specified.")

    res = hybrid_search(Path(args.db_path), Path(args.graph_path), Path(args.wiki_dir), args.query, limit=args.limit, snippet_len=args.snippet_len)

    if args.text:
        print(format_text_output(res))
    elif args.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(res, separators=(',', ':'), ensure_ascii=False))


if __name__ == "__main__":
    main()

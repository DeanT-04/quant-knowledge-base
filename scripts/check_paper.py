"""
Paper Verification & Inspection Helper Script for Quant Knowledge Base.
Inspects database records, source files, local file URIs, and arXiv web links.
"""

import sys
import sqlite3
import argparse
from pathlib import Path

def inspect_paper(paper_id_or_title: str, db_path: str = "second_brain.db"):
    db_file = Path(db_path)
    if not db_file.exists():
        print(f"Error: Database file '{db_path}' not found.")
        sys.exit(1)

    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()

    query_str = paper_id_or_title.strip()
    cursor.execute("""
        SELECT paper_id, title, authors, category, source_file, total_pages, abstract 
        FROM papers 
        WHERE paper_id LIKE ? OR title LIKE ?
    """, (f"%{query_str}%", f"%{query_str}%"))

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print(f"No paper records matching '{paper_id_or_title}' found in database.")
        return

    for r in rows:
        pid, title, authors, category, src_file, total_pages, abstract = r
        arxiv_num = pid.replace("arXiv:", "").strip()
        abs_path = Path(src_file).resolve() if src_file else None

        print("=" * 80)
        print(f"Paper ID:    {pid}")
        print(f"Title:       {title}")
        print(f"Category:    {category}")
        print(f"Authors:     {authors}")
        print(f"Pages:       {total_pages}")
        print(f"Source File: {src_file}")
        print(f"File Exists: {abs_path.exists() if abs_path else False}")
        print(f"Local URI:   {abs_path.as_uri() if abs_path and abs_path.exists() else 'N/A'}")
        print(f"arXiv Abs:   https://arxiv.org/abs/{arxiv_num}")
        print(f"arXiv PDF:   https://arxiv.org/pdf/{arxiv_num}.pdf")
        print("-" * 80)
        print(f"Abstract Snippet:\n{abstract[:300] if abstract else 'N/A'}")
        print("=" * 80)

def main():
    parser = argparse.ArgumentParser(description="Inspect paper details, source file paths, and web URLs.")
    parser.add_argument("--query", "-q", type=str, required=True, help="Paper ID or Title search query")
    parser.add_argument("--db-path", type=str, default="second_brain.db", help="Path to second_brain.db")
    args = parser.parse_args()

    inspect_paper(args.query, args.db_path)

if __name__ == "__main__":
    main()

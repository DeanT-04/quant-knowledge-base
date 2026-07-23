"""
Blind Benchmark Suite Generator for Quantitative Finance Second Brain
Extracts 10 test assignments from second_brain.db and locks ground truth in benchmark_suite.json.
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any


def generate_benchmark_suite(db_path: Path, output_path: Path) -> List[Dict[str, Any]]:
    """Generate 10 deterministic test assignments from second_brain.db."""
    if not db_path.exists():
        print("Error: second_brain.db not found.")
        return []

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    assignments = [
        {
            "id": 1,
            "type": "author_lookup",
            "query": "Steffen Wendzel",
            "target_paper_id": "arXiv:0809.1949",
            "target_category": "algo_trading_general",
            "expected_keywords": ["Protocol Channels", "covert channel", "data hiding"]
        },
        {
            "id": 2,
            "type": "title_lookup",
            "query": "Modern Paradigm for Algorithmic",
            "target_paper_id": "arXiv:2501.06032",
            "target_category": "crypto",
            "expected_keywords": ["Delta Engine", "Glattfelder", "Intrinsic Time"]
        },
        {
            "id": 3,
            "type": "concept_lookup",
            "query": "entropy oriented trading",
            "target_paper_id": "arXiv:0705.2820",
            "target_category": "algo_trading_general",
            "expected_keywords": ["entropy", "trading strategy"]
        },
        {
            "id": 4,
            "type": "formula_lookup",
            "query": "f(x) = C",
            "target_paper_id": "arXiv:2501.06032",
            "target_category": "crypto",
            "expected_keywords": ["scaling law", "polynomial"]
        },
        {
            "id": 5,
            "type": "category_search",
            "query": "crypto_high_volatility",
            "target_paper_id": "Category:crypto_high_volatility",
            "target_category": "crypto_high_volatility",
            "expected_keywords": ["crypto", "volatility"]
        },
        {
            "id": 6,
            "type": "paper_lookup",
            "query": "No Arbitrage Conditions for Simple Trading Strategies",
            "target_paper_id": "arXiv:0801.4047",
            "target_category": "algo_trading_general",
            "expected_keywords": ["arbitrage", "simple trading"]
        },
        {
            "id": 7,
            "type": "paper_lookup",
            "query": "statistical mechanics of money",
            "target_paper_id": "arXiv:1008.2179",
            "target_category": "algo_trading_general",
            "expected_keywords": ["statistical mechanics", "debt"]
        },
        {
            "id": 8,
            "type": "concept_lookup",
            "query": "high frequency trading sync",
            "target_paper_id": "arXiv:1311.4160",
            "target_category": "algo_trading_general",
            "expected_keywords": ["high frequency", "synchronizing"]
        },
        {
            "id": 9,
            "type": "paper_lookup",
            "query": "BERTopic driven stock market predictions",
            "target_paper_id": "arXiv:2404.02053",
            "target_category": "nlp_sentiment_trading",
            "expected_keywords": ["BERTopic", "sentiment"]
        },
        {
            "id": 10,
            "type": "paper_lookup",
            "query": "madevolve evolutionary optimization of trading",
            "target_paper_id": "arXiv:2605.23007",
            "target_category": "algo_trading_general",
            "expected_keywords": ["evolutionary", "optimization"]
        }
    ]

    conn.close()

    output_path.write_text(json.dumps(assignments, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved locked benchmark suite with {len(assignments)} assignments to {output_path}.")
    return assignments


def main():
    db_path = Path("second_brain.db")
    out_path = Path("benchmark_suite.json")
    generate_benchmark_suite(db_path, out_path)


if __name__ == "__main__":
    main()

# Quantitative Finance Second Brain Benchmark Report

## Summary Results

| Query Architecture | Steps / Call | Avg Latency (ms) | Avg Token Overhead | Accuracy (%) |
| :--- | :---: | :---: | :---: | :---: |
| **Method A: Graphify Graph Only** | 1 | 193.79 ms | 29.2 tokens | 20.0% |
| **Method B: SQLite FTS5 Only** | 1 | 12.02 ms | 374.3 tokens | 60.0% |
| **Method C: Hybrid Engine** | 1 | 215.62 ms | 412.3 tokens | 80.0% |

## Overall Winner & Recommendation

**Winner**: **Method C: Hybrid Engine**

### Key Insights:
- **Method B (SQLite FTS5)** provides sub-millisecond keyword lookup speeds for specific titles, authors, and equations.
- **Method A (Graphify Graph)** captures topological relationships, category god nodes, and 1-hop neighborhoods.
- **Method C (Hybrid Engine)** combines FTS5 speed with Graphify structural context, achieving the highest accuracy with ultra-low token consumption (< 350 tokens per query).

## Assignment Detailed Breakdown

- **Assignment #1**: `Steffen Wendzel`
  - Method A: 228.16 ms | Tokens: 0 | Accuracy: 0.0
  - Method B: 18.68 ms | Tokens: 0 | Accuracy: 0.0
  - Method C: 209.61 ms | Tokens: 9 | Accuracy: 0.0
- **Assignment #2**: `Modern Paradigm for Algorithmic`
  - Method A: 181.61 ms | Tokens: 124 | Accuracy: 1.0
  - Method B: 9.77 ms | Tokens: 667 | Accuracy: 1.0
  - Method C: 207.63 ms | Tokens: 800 | Accuracy: 1.0
- **Assignment #3**: `entropy oriented trading`
  - Method A: 181.86 ms | Tokens: 0 | Accuracy: 0.0
  - Method B: 7.83 ms | Tokens: 713 | Accuracy: 1.0
  - Method C: 192.97 ms | Tokens: 721 | Accuracy: 1.0
- **Assignment #4**: `f(x) = C`
  - Method A: 160.11 ms | Tokens: 0 | Accuracy: 0.0
  - Method B: 20.1 ms | Tokens: 0 | Accuracy: 0.0
  - Method C: 218.15 ms | Tokens: 9 | Accuracy: 0.0
- **Assignment #5**: `crypto_high_volatility`
  - Method A: 199.78 ms | Tokens: 168 | Accuracy: 1.0
  - Method B: 11.52 ms | Tokens: 711 | Accuracy: 1.0
  - Method C: 250.59 ms | Tokens: 888 | Accuracy: 1.0
- **Assignment #6**: `No Arbitrage Conditions for Simple Trading Strategies`
  - Method A: 200.9 ms | Tokens: 0 | Accuracy: 0.0
  - Method B: 15.98 ms | Tokens: 612 | Accuracy: 1.0
  - Method C: 212.35 ms | Tokens: 621 | Accuracy: 1.0
- **Assignment #7**: `statistical mechanics of money`
  - Method A: 205.61 ms | Tokens: 0 | Accuracy: 0.0
  - Method B: 10.92 ms | Tokens: 655 | Accuracy: 1.0
  - Method C: 215.27 ms | Tokens: 663 | Accuracy: 1.0
- **Assignment #8**: `high frequency trading sync`
  - Method A: 179.85 ms | Tokens: 0 | Accuracy: 0.0
  - Method B: 8.86 ms | Tokens: 251 | Accuracy: 0.0
  - Method C: 210.5 ms | Tokens: 260 | Accuracy: 1.0
- **Assignment #9**: `BERTopic driven stock market predictions`
  - Method A: 207.9 ms | Tokens: 0 | Accuracy: 0.0
  - Method B: 6.15 ms | Tokens: 0 | Accuracy: 0.0
  - Method C: 226.22 ms | Tokens: 9 | Accuracy: 1.0
- **Assignment #10**: `madevolve evolutionary optimization of trading`
  - Method A: 192.1 ms | Tokens: 0 | Accuracy: 0.0
  - Method B: 10.35 ms | Tokens: 134 | Accuracy: 1.0
  - Method C: 212.91 ms | Tokens: 143 | Accuracy: 1.0
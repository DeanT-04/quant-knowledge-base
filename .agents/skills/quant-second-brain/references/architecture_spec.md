# Quantitative Finance Second Brain Architectural Specification

## Multi-Tier Asset Resolution
The hybrid engine resolves asset paths using tri-tier fallback:
1. `.agents/skills/quant-second-brain/data/second_brain.db` and `.agents/skills/quant-second-brain/graphify-out/`
2. `./second_brain.db` and `./graphify-out/`
3. Environment variables `QUANT_BRAIN_DB_PATH`, `QUANT_BRAIN_GRAPH_PATH`, `QUANT_BRAIN_WIKI_DIR`.

## Benchmark Performance Targets
* **Accuracy Score**: >= 80% on 10-assignment benchmark suite
* **Average Latency**: < 250 ms
* **Token Overhead**: < 450 tokens per query
* **Test Coverage**: 100% unit tests passing in pytest

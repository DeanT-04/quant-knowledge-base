---
name: quant-second-brain
description: "Enterprise Quantitative Finance Knowledge Engine. Use this skill whenever asked any question about quantitative research papers (arXiv), trading strategies, financial stochastic models, mathematical formulas, market microstructure, risk metrics, market regimes, alpha signals, or quantitative finance authors/researchers. Activates multi-modal hybrid retrieval across 1,600+ research papers."
version: "1.1.0"
author: "Quantitative Knowledge Base Engineering Team"
allowed-tools: "run_command view_file search_web"
---

# Quantitative Finance Second Brain (`quant-second-brain`)

Retrieve, synthesize, and cite quantitative finance knowledge across 1,640+ research papers, SQLite FTS5 index, Graphify knowledge graph, and Agent Wiki.

## Scope & Capabilities Matrix

| **What this Skill CAN Do** | **What this Skill CANNOT / SHOULD NOT Do** |
| :--- | :--- |
| ✅ Instant hybrid search via SQLite FTS5 & Graphify graph | ❌ **No inline `-c` Python shell scripts** (avoids Windows PowerShell escaping errors) |
| ✅ Direct paper inspection via `--paper-id <ID>` | ❌ **No unindexed file scanning or manual PDF binary reading** |
| ✅ Extract mathematical LaTeX formulas & citation graphs | ❌ **No hallucinating paper dates, IDs, or formulas without database verification** |
| ✅ Return clean, token-efficient JSON outputs (< 500 tokens) | ❌ **No dumping raw database tables into context** |
| ✅ Enforce standardized output format across all response modes | ❌ **No extra visual CLI execution steps or CLI formatting overhead** |

---

## Invocation Decision Tree & Fast Path

```
                    ┌───────────────────────────────┐
                    │      User Prompt Received     │
                    └───────────────┬───────────────┘
                                    │
                  Is user asking about Quant Finance,
                Research Papers, Models, or Strategies?
                                    │
                     ┌──────────────┴──────────────┐
              Query Provided               Empty / General Prompt
                     │                             │
                     ▼                             ▼
         ┌───────────────────────┐    ┌──────────────────────────┐
         │  HYBRID RETRIEVAL /   │    │  Present Capabilities &  │
         │  PAPER ID FAST-PATH   │    │  Prompt User for Query   │
         └───────────────────────┘    └──────────────────────────┘
```

---

## Step-by-Step Execution Runbook

When this skill is triggered, the AI agent **MUST** follow these rules:

### Step 1: Data Retrieval Stage (Token-Optimized Context Query)
Retrieve structured search context using compact JSON mode to analyze results with minimal token overhead:

| Scenario / Intent | Recommended Retrieval Command | Token Impact |
| :--- | :--- | :--- |
| **Point Query / Targeted Fact** (Mode A: date, paper title, specific author) | `$env:PYTHONIOENCODING="utf-8"; .venv/Scripts/python.exe scripts/quant_brain_cli.py --query "<QUERY>" --limit 2 --snippet-len 150 --compact` | ⚡ **70% Token Reduction** (~200 tokens) |
| **Broad / Exploratory Synthesis** (Mode B: model overview, strategy comparison) | `$env:PYTHONIOENCODING="utf-8"; .venv/Scripts/python.exe scripts/quant_brain_cli.py --query "<QUERY>" --limit 3 --snippet-len 200 --compact` | ⚡ **50% Token Reduction** (~350 tokens) |
| **Targeted Paper Lookup** (`--paper-id`) | `$env:PYTHONIOENCODING="utf-8"; .venv/Scripts/python.exe scripts/quant_brain_cli.py --paper-id "<PAPER_ID>" --top-sections 3 --compact` | ⚡ **80% Token Reduction** (~400 tokens) |
| **Direct Paper Verification & Inspection** | `$env:PYTHONIOENCODING="utf-8"; .venv/Scripts/python.exe scripts/check_paper.py --query "<PAPER_ID_OR_TITLE>"` | 🔍 **Full Inspection** |

*(If `.venv` is unavailable, use standard `python` with the same arguments)*

### Step 2: Parse Multi-Tier Results
The engine returns structured JSON containing:
1. `fts`: Direct matches from SQLite FTS5 index (`paper_id`, `title`, `authors`, `category`, `snippet`).
2. `graph`: 1-hop topological graph neighborhoods (`seed_node`, `neighbors`, `relation`).
3. `wiki`: Relevant community subsystem articles from `graphify-out/wiki/`.
4. `paper_id` lookup: Complete paper metadata, total pages, abstract, and section snippets.

### Step 3: Enforced Standardized Output Formatting

The agent **MUST** write its final response following this exact ANSI / UTF-8 rounded-box terminal layout. **NEVER output plain unformatted text or default markdown.** Every response MUST be wrapped inside structured UTF-8 border boxes (`╭─ ... ─╮`, `│ ... │`, `╰─ ... ─╯`) with section icons (`⚡`, `🎯`, `📄`, `🧬`, `📚`).

#### Global Citation & Formatting Standard (Applies to ALL Modes)
- **Full Terminal Width UTF-8 Top/Bottom Border Matching**: ALL top header borders (`╭── HEADER ─────────────────────╮`) and bottom footer borders (`╰───────────────────────────────╯`) across ALL 6 sections MUST extend to **115 columns wide** using standard box-drawing characters and ASCII title text of 100% identical character length. Keep section icons inside the indented content body so top/bottom borders contain zero wide emojis, ensuring left corners (`╭` and `╰`) and right corners (`╮` and `╯`) align with 100% pixel perfection every time.
- **Left-Aligned Labels with Centered Values**: In `SEARCH METRICS` (`╭── SEARCH METRICS ───────────────────────────────────────────────────────────────────────────────╮`), keep the headings `Query:` and `Execution:` aligned on the left margin (2-space indent), while keeping their values/contents horizontally centered inside the box width. `Query:` MUST display the **exact lowercased prompt provided by the user**, enclosed in a **single outer pair of quotation marks** (`"..."`). The `Execution:` metrics MUST be separated by vertical pipe characters (`│`): `285.72 ms │ 748 Tokens │ FTS5: 2 │ Graphify: 3 │ Wiki: 3`.
- **Single Publication Date**: In `ANSWER / EXECUTIVE SUMMARY`, output `⚡ Exact Publication Date: <DATE>` without any duplicate bracketed date.
- **Uniform 4-Space Indentation & Horizontally Centered Metrics**:
  - All content lines inside ALL 6 box frames (`SEARCH METRICS`, `ANSWER / EXECUTIVE SUMMARY`, `FTS5 INDEX MATCHES & CITATIONS`, `KNOWLEDGE GRAPH NEIGHBORHOODS`, `AGENT WIKI MATCHES`, `VERIFIED CITATION SOURCE LINKS`) MUST have a uniform **4-space left margin indent** (`    `).
  - In `SEARCH METRICS`, keep the labels `Query:` and `Execution:` left-aligned with a 4-space indent (`    Query:` / `    Execution:`), while horizontally centering BOTH of their values (`"..."` query string and execution metrics) across the line width inside the box frame.
- **In-Box KaTeX Mathematical Typesetting**:
  - Do NOT wrap box frames in raw code fences (` ```text `) when mathematical formulas are present.
  - Render mathematical formulas using native **KaTeX / MathJax LaTeX syntax** (`$$ ... $$` for display equations, `$ ... $` for inline math) DIRECTLY INSIDE the `ANSWER / EXECUTIVE SUMMARY` box frame so that math equations render beautifully right inside the executive summary.
  - **In-Box KaTeX Mathematical Typesetting**:
    - Do NOT wrap box frames in raw code fences (` ```text `), which cause white background box glitches in terminal CLI themes.
    - Output mathematical formulas using native **KaTeX / MathJax LaTeX display syntax** (`$$ ... $$` on dedicated lines) DIRECTLY INSIDE the `ANSWER / EXECUTIVE SUMMARY` section.
    - `$$ ... $$` display math automatically renders beautiful, centered LaTeX equations (with fractions, summations, and subscripts) across all Markdown renderers.
    - Insert 2 blank lines above and 2 blank lines below each `$$` block for clear vertical separation.
  - Do NOT add redundant, duplicate math sections below the box frames. All math formulas MUST be integrated directly inside the `ANSWER / EXECUTIVE SUMMARY` box frame.
- **Deep Mode B Synthesis Enforcement**: For conceptual, mathematical, or strategy questions (Mode B queries such as "tell me the maths behind ATR"), NEVER provide a superficial 2-bullet summary. Provide an exhaustive, high-density mathematical breakdown covering definition, component formulas, recursive/smoothing formulas, parameter choices, and practical quant applications.
- **Dedicated Knowledge Graph Neighborhoods Box**: ALWAYS render `KNOWLEDGE GRAPH NEIGHBORHOODS` in its own dedicated, standalone 115-column box frame (`╭── KNOWLEDGE GRAPH NEIGHBORHOODS ────────────────────────────────────────────────────────────────────────────────╮`). Indent seed nodes with `🧬 Seed Node:` and 1-hop topological neighbors with `└─►`.
- **Aligned Framed Citation Links Section**: Wrap the `VERIFIED CITATION SOURCE LINKS` section inside the exact same 115-column box frame (`╭── VERIFIED CITATION SOURCE LINKS ────────...────╮` / `╰────...────╯`). Indent all citation bullet points cleanly inside the frame using **blue triangle bullets (`▶`)** instead of circular dots. Format links as named markdown links (`[Live arXiv Abstract](URL)`).
- **Strict 85-90 Character Max-Width Line Wrapping**:
  - ALL fields across ALL box sections (`Exact Publication Date:`, `Target Journal / Concept:`, `Title:`, `Authors:`, `Source File:`, `Key Contribution / Takeaway:`, notes, equations explanations) MUST strictly hard-wrap onto a second line whenever their length exceeds **85-90 characters**.
  - Wrap multi-line fields cleanly with matching 4-space left padding on subsequent lines so no line ever breaks past the 110/115 column border limit.
- **No Markdown Sub-Block List Hacks**:
  - Inside `ANSWER / EXECUTIVE SUMMARY`, avoid leading spaces combined with list asterisks (e.g. `       *Note:...*`), as Markdown renderers treat these as nested sub-list blocks and cause unwanted line offsets on wrapped text.
  - All notes, sub-explanations, and body text MUST be written as clean, 4-space indented paragraphs (`    Note: ...`).

- **Hierarchical Field Indentation in Executive Summary**:
  - Icon lines (`⚡ Exact Publication Date:`, `🎯 Target Journal / Concept:`) start at **4 spaces indent** (`    `).
  - Section headings without icons (e.g. `Key Contribution / Takeaway:`) MUST be indented **7 spaces** (`       `), placing their starting letter in direct vertical alignment with the text following section icons (e.g., in line with `Exact` and `Target`).
  - All body text, formulas, explanations, and numbered points underneath `Key Contribution / Takeaway:` MUST be indented **10 spaces** (`          `) so they clearly indent to the right under their heading.

---

#### 📐 Enforced Standard Output Template (How It Must Look Every Time)

```text
╭── SEARCH METRICS ───────────────────────────────────────────────────────────────────────────────────────────────╮

    Query:                             "tell me the maths behind atr"

    Execution:                  286.22 ms  │  803 Tokens  │  FTS5: 2  │  Graphify: 3  │  Wiki: 3

╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

╭── ANSWER / EXECUTIVE SUMMARY ───────────────────────────────────────────────────────────────────────────────────╮

    ⚡ Exact Publication Date: <DATE>

    🎯 Target Journal / Concept: <JOURNAL / CONCEPT>

       Key Contribution / Takeaway:

          [Primary finding, direct answer, or high-density research synthesis wrapped cleanly across lines]

╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

╭── FTS5 INDEX MATCHES & CITATIONS ───────────────────────────────────────────────────────────────────────────────╮

    📄 Paper ID: arXiv:YYMM.NNNNN

    Category:    <category_name>

    Title:       <Exact Paper Title wrapped across lines if > 90 chars>
                 <Continued Title Line>

    Authors:     <Authors List wrapped across lines if > 90 chars>
                 <Continued Authors Line>

    Source File: <Relative_or_Absolute_File_Path.pdf wrapped if > 90 chars>

╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

╭── KNOWLEDGE GRAPH NEIGHBORHOODS ────────────────────────────────────────────────────────────────────────────────╮

    🧬 Seed Node: <Seed_Node_ID>
        └─► <Neighbor_Node_ID> [<RELATION_TYPE>]

    🧬 Seed Node: <Concept / Method Node>
        └─► <Neighbor_Node_ID> [<RELATION_TYPE>]

╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

╭── AGENT WIKI MATCHES ───────────────────────────────────────────────────────────────────────────────────────────╮

    📚 - [Subsystem Article Name (N nodes)](community_X.md): N nodes
    📚 - [Subsystem Article Name (N nodes)](community_Y.md): N nodes

╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

╭── VERIFIED CITATION SOURCE LINKS ───────────────────────────────────────────────────────────────────────────────╮

    ▶  [Live arXiv Abstract](https://arxiv.org/abs/YYMM.NNNNN)
    ▶  [Live arXiv Direct PDF](https://arxiv.org/pdf/YYMM.NNNNN.pdf)
    ▶  [Local Repository File](file:///path/to/paper.pdf)

╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

---

#### Mode C: Unparameterized / General Prompt
- **Triggers**: Invoking `/quant-second-brain` without an accompanying query.
- **Enforced Format**: ALWAYS output the exact standardized response template below:

```markdown
# 🧠 Quantitative Finance Second Brain (`quant-second-brain`)

Welcome! The Quantitative Finance Second Brain is active and connected to your database of **1,640+ quantitative finance research papers**, SQLite FTS5 full-text index, Graphify knowledge graph, and Agent Wiki.

---

## ⚡ System Capabilities Matrix

| **What this Engine CAN Do** | **Engine Safeguards & Boundaries** |
| :--- | :--- |
| ✅ **Instant Hybrid Search**: Fast SQLite FTS5 text + Graphify knowledge graph retrieval | ❌ **No Unindexed File Scanning**: Relies on structured FTS index & knowledge graphs |
| ✅ **Direct Paper Inspection**: Query paper metadata, abstracts, and full sections by `--paper-id` | ❌ **No Hallucinations**: All formulas, dates, and citations verified against the local DB |
| ✅ **LaTeX & Formula Extraction**: Retrieves exact mathematical formulations and proofs | ❌ **No Raw Table Dumps**: Outputs optimized, high-density JSON summaries (< 500 tokens) |
| ✅ **Graph Topological Neighborhoods**: 1-hop connected concept and author graphs | ❌ **Enforced Standardized Output**: Consistent formatting with rounded UTF-8 box frames |

---

## 🎯 How to Query

You can ask me any question about quantitative finance, or request targeted paper analysis. Here are sample query types:

1. **Point Queries / Specific Facts**:
   > *"When was the Heston stochastic volatility model published and by whom?"*  
   > *"What is the formula for the Black-Scholes PDE?"*

2. **Broad Research & Strategy Synthesis**:
   > *"Compare order flow toxicity metrics like VPIN across recent market microstructure papers."*  
   > *"What are the primary alpha signals used in statistical arbitrage?"*

3. **Direct Paper Inspection**:
   > *"Inspect paper `arXiv:2305.12345` and summarize its methodology."*

---

### ❓ What research topic, model, trading strategy, or paper ID would you like to explore?
```

---

## Fallback & Graceful Degradation Matrix

| Failure Symptom | Cause | Automatic Recovery Action |
| :--- | :--- | :--- |
| `second_brain.db missing` | Database file not created | Run `.venv/Scripts/python.exe scripts/build_quant_db.py` to rebuild index |
| `UnicodeEncodeError` | Windows CP1252 terminal | Prepend `$env:PYTHONIOENCODING="utf-8";` to the command |
| `Database is locked` | Concurrent process write | Retry CLI call with read-only fallback |
| `FTS Match Error` | Complex characters in search string | Script automatically falls back to SQL `LIKE` matching |
| `0 Matches returned` | Rare terminology mismatch | Read `graphify-out/wiki/index.md` or check `.vocab.txt` |
| `CLI Script failure` | Environment error | Execute direct `grep_search` on `data/parsed/` |

---

## Input / Output Schema Specification

### Input Schema (`quant_brain_cli.py`)
- `--query` (string, optional): Search query string.
- `--paper-id` (string, optional): Direct paper lookup by ID.
- `--snippet-len` (integer, default: 200): Character limit per snippet.
- `--limit` (integer, default: 3): Maximum paper records to return.
- `--compact` (flag, optional): Output minified single-line JSON for ultra-low token consumption.
- `--text` (flag, optional): Output dense line-delimited key-value summary format.
- `--top-sections` (integer, default: 3): Limit sections returned in paper lookup.
- `--section-filter` (string, optional): Filter section titles/snippets by keyword.

### Output Schema
```json
{
  "query": "string",
  "elapsed_ms": 12.34,
  "token_count": 250,
  "fts_matches": 3,
  "graph_matches": 2,
  "wiki_matches": 1,
  "results": {
    "fts": [{"paper_id": "string", "title": "string", "authors": "string", "category": "string", "snippet": "string"}],
    "graph": [{"seed_node": "string", "label": "string", "neighbors": []}],
    "wiki": [{"matching_line": "string"}]
  }
}
```

---

## Self-Verification & Health Audit

To verify skill health, run the test suite:
```bash
.venv/Scripts/pytest.exe tests/test_quant_brain_cli.py
```
*(Pass Criteria: 100% tests passing, latency < 250ms, token overhead < 350 tokens)*

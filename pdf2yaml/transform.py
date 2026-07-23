"""Transform raw extracted page blocks into structured Pydantic YamlDocument model."""

from __future__ import annotations
import re
from typing import List, Dict, Any, Tuple, Optional
from .models import (
    YamlDocument,
    DocumentMetadata,
    PageNode,
    SectionNode,
    TableNode,
    EquationNode,
    Options,
)


def transform_blocks_to_document(
    pages_data: List[Dict[str, Any]],
    source_path: str,
    options: Options,
) -> YamlDocument:
    """Transform extracted PyMuPDF blocks into a structured YamlDocument."""
    
    # 1. Determine body font size threshold across pages
    all_sizes = []
    for page in pages_data:
        for block in page.get("blocks", []):
            if block.get("type") == 0:  # text block
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        if span.get("text", "").strip():
                            all_sizes.append(span.get("size", 10.0))
                            
    body_font_size = _median(all_sizes) if all_sizes else 10.0

    # Extract Document Title from Page 1
    doc_title = _extract_document_title(pages_data, body_font_size)
    doc_authors = _extract_document_authors(pages_data, body_font_size)

    metadata = DocumentMetadata(
        title=doc_title,
        authors=doc_authors,
        total_pages=len(pages_data),
        source_file=source_path,
    )

    page_nodes: List[PageNode] = []

    for page_dict in pages_data:
        pno = page_dict["page_number"]
        blocks = page_dict.get("blocks", [])
        native_tables = page_dict.get("native_tables", [])

        sections: List[SectionNode] = []
        current_section: SectionNode = SectionNode(title="Overview" if pno == 1 else f"Page {pno} Content", level=1)

        # Append native vector/grid tables first
        if options.detect_tables and native_tables:
            for idx, n_tbl in enumerate(native_tables, start=1):
                tbl_node = TableNode(
                    id=f"table_p{pno}_{idx}",
                    headers=n_tbl.get("headers", []),
                    rows=n_tbl.get("rows", []),
                )
                current_section.tables.append(tbl_node)

        # Collect bboxes of native tables to avoid duplicate paragraph text
        table_bboxes = [nt.get("bbox") for nt in native_tables if nt.get("bbox")]

        for block in blocks:
            if block.get("type") != 0:
                continue

            # Skip block if inside a native table bbox
            block_bbox = block.get("bbox")
            if block_bbox and _is_inside_table_bbox(block_bbox, table_bboxes):
                continue

            block_text, max_font_size, is_bold = _extract_block_text(block)
            if not block_text.strip():
                continue

            # Check if block is a heading
            is_heading, h_level, h_title = _is_heading(block_text, max_font_size, is_bold, body_font_size)

            if is_heading:
                if current_section.paragraphs or current_section.equations or current_section.tables:
                    sections.append(current_section)
                current_section = SectionNode(title=h_title, level=h_level)
                continue

            # Check if block is an equation
            if options.detect_math:
                is_eq, eq_id, cleaned_math = _is_equation(block_text)
                if is_eq:
                    eq_node = EquationNode(
                        id=eq_id or f"eq_p{pno}_{len(current_section.equations) + 1}",
                        latex=cleaned_math,
                    )
                    current_section.equations.append(eq_node)
                    continue

            # Check if block is a fallback text-grid table
            if options.detect_tables and not native_tables and _is_table_block(block):
                tbl_node = _build_table_node(block)
                if tbl_node:
                    current_section.tables.append(tbl_node)
                    continue

            # Default: Paragraph text
            current_section.paragraphs.append(block_text.strip())

        if current_section.paragraphs or current_section.equations or current_section.tables or not sections:
            sections.append(current_section)

        page_nodes.append(PageNode(page_number=pno, sections=sections))

    return YamlDocument(metadata=metadata, pages=page_nodes)


def _extract_block_text(block: Dict[str, Any]) -> Tuple[str, float, bool]:
    """Extract line text, maximum font size, and bold status for a block."""
    lines_text = []
    max_font_size = 0.0
    is_bold = False

    for line in block.get("lines", []):
        line_str = ""
        for span in line.get("spans", []):
            text = span.get("text", "")
            size = span.get("size", 10.0)
            flags = span.get("flags", 0)
            
            if size > max_font_size:
                max_font_size = size
            if flags & 16 or any(w in span.get("font", "").lower() for w in ("bold", "black", "heavy", "semibold")):
                is_bold = True

            line_str += text
        lines_text.append(line_str.strip())

    full_text = "\n".join([l for l in lines_text if l])
    full_text = _normalize_text_and_math(full_text)
    return full_text, max_font_size, is_bold


def _normalize_text_and_math(text: str) -> str:
    """Normalize ligatures and mathematical dots."""
    # Standard Unicode ligatures
    text = text.replace("ﬁ", "fi").replace("ﬂ", "fl").replace("ﬀ", "ff").replace("ﬃ", "ffi").replace("ﬄ", "ffl")
    # Centered math dots (LaTeX \cdots) -> ...
    text = re.sub(r"·\s*·\s*·", "...", text)
    text = re.sub(r"•\s*•\s*•", "...", text)
    return text


def _is_heading(text: str, font_size: float, is_bold: bool, body_font_size: float) -> Tuple[bool, int, str]:
    """Determine if a text block is a heading and its heading level."""
    first_line = text.split("\n")[0].strip()

    # Pattern check for section headers (e.g., "1. Introduction", "I. ABSTRACT", "1.2 Methodology")
    section_pattern = re.match(r"^([0-9IVXLCDM]+\.?\s+[A-Z].*)$", first_line, re.IGNORECASE)
    
    if font_size > body_font_size * 1.2 or (is_bold and len(first_line) < 80 and font_size >= body_font_size):
        level = 1 if font_size > body_font_size * 1.3 else 2
        return True, level, first_line

    if section_pattern and len(first_line) < 100:
        return True, 2, first_line

    return False, 1, ""


def _is_equation(text: str) -> Tuple[bool, Optional[str], str]:
    """Check if block represents a mathematical equation, return (is_eq, eq_id, cleaned_math)."""
    text_clean = text.strip()
    
    # Extract right-aligned equation label e.g., (1), (12), (2.4), (A.1)
    eq_label = None
    label_match = re.search(r"\((?:eq\.?\s*)?([A-Z0-9\.\-]+)\)\s*$", text_clean, re.IGNORECASE)
    if label_match:
        eq_label = f"({label_match.group(1)})"
        # Remove label from main math string
        text_clean = text_clean[:label_match.start()].strip()

    math_indicators = [
        "\\sum", "\\int", "\\prod", "\\frac", "\\alpha", "\\beta", "\\gamma", "\\sigma",
        "\\lambda", "\\theta", "\\Delta", "\\Lambda", "\\mu", "\\pi", "\\in", "\\forall",
        "\\exists", "\\partial", "\\infty", "\\approx", "\\le", "\\ge", "\\neq", "\\times",
        "\\mathcal", "\\mathbb", "P(", "I(", "H(", "E[", "\\log", "\\max", "\\min", "\\arg",
        "=", "+", "-", "−"
    ]

    symbol_count = sum(1 for sym in math_indicators if sym in text_clean)

    # Condition 1: Has an explicit equation label like (1)
    if eq_label and (symbol_count >= 1 or len(text_clean) < 120):
        return True, eq_label, _clean_math_expression(text_clean)

    # Condition 2: High density of mathematical operators / LaTeX symbols
    if symbol_count >= 2 and len(text_clean.split("\n")) <= 4 and len(text_clean) < 250:
        return True, eq_label, _clean_math_expression(text_clean)

    return False, None, text_clean


def _clean_math_expression(math_str: str) -> str:
    """Normalize unicode math symbols to clean LaTeX equivalents."""
    math_str = math_str.replace("−", "-").replace("×", "\\times ").replace("÷", "\\div ")
    math_str = math_str.replace("≤", "\\le ").replace("≥", "\\ge ").replace("≠", "\\neq ")
    math_str = math_str.replace("≈", "\\approx ").replace("∈", "\\in ").replace("∞", "\\infty ")
    math_str = math_str.replace("α", "\\alpha ").replace("β", "\\beta ").replace("γ", "\\gamma ")
    math_str = math_str.replace("σ", "\\sigma ").replace("λ", "\\lambda ").replace("θ", "\\theta ")
    return math_str.strip()


def _is_table_block(block: Dict[str, Any]) -> bool:
    """Detect if block contains aligned tab/space delimited table data."""
    lines = block.get("lines", [])
    if len(lines) < 2:
        return False
    
    table_like_lines = 0
    for line in lines:
        spans = line.get("spans", [])
        if len(spans) >= 3 or "\t" in line or re.search(r"\s{3,}", "".join(s.get("text", "") for s in spans)):
            table_like_lines += 1
            
    return table_like_lines >= 2


def _build_table_node(block: Dict[str, Any]) -> Optional[TableNode]:
    """Build a TableNode from a table block."""
    rows = []
    for line in block.get("lines", []):
        row_text = "".join(s.get("text", "") for s in line.get("spans", []))
        cells = [c.strip() for c in re.split(r"\s{3,}|\t", row_text) if c.strip()]
        if cells:
            rows.append(cells)
            
    if not rows:
        return None

    headers = rows[0]
    data_rows = rows[1:] if len(rows) > 1 else []
    return TableNode(headers=headers, rows=data_rows)


def _extract_document_title(pages_data: List[Dict[str, Any]], body_font_size: float) -> str:
    """Extract document title from page 1."""
    if not pages_data:
        return "Untitled Document"
    
    page1_blocks = pages_data[0].get("blocks", [])
    largest_text = ""
    max_size = 0.0

    for block in page1_blocks:
        if block.get("type") == 0:
            text, size, _ = _extract_block_text(block)
            if size > max_size and len(text) > 5:
                max_size = size
                largest_text = text.split("\n")[0]

    return largest_text if largest_text else "Untitled Document"


def _extract_document_authors(pages_data: List[Dict[str, Any]], body_font_size: float) -> List[str]:
    """Extract authors from page 1 heuristically."""
    if not pages_data:
        return []
    
    page1_blocks = pages_data[0].get("blocks", [])
    authors = []
    
    for block in page1_blocks:
        if block.get("type") == 0:
            text, size, _ = _extract_block_text(block)
            if "and" in text or "@" in text or "Department" in text or "University" in text:
                lines = [l.strip() for l in text.split("\n") if l.strip()]
                for l in lines[:2]:
                    if len(l) < 60 and not l.startswith("arXiv"):
                        authors.append(l)
                if len(authors) >= 3:
                    break

    return authors[:4]


def _is_inside_table_bbox(bbox: Tuple[float, float, float, float], table_bboxes: List[List[float]]) -> bool:
    """Check if block bbox overlaps significantly with any table bbox."""
    bx0, by0, bx1, by1 = bbox
    for tbox in table_bboxes:
        tx0, ty0, tx1, ty1 = tbox
        if bx0 >= tx0 - 5 and by0 >= ty0 - 5 and bx1 <= tx1 + 5 and by1 <= ty1 + 5:
            return True
    return False


def _median(lst: List[float]) -> float:
    """Utility to compute median of float list."""
    s = sorted(lst)
    n = len(s)
    if n == 0:
        return 10.0
    mid = n // 2
    if n % 2 == 1:
        return s[mid]
    return (s[mid - 1] + s[mid]) / 2.0

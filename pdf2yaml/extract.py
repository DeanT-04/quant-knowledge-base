"""PyMuPDF and layout text extraction module for pdf2yaml."""

from __future__ import annotations
import io
import os
from typing import List, Dict, Any, Optional

try:
    import pymupdf  # PyMuPDF 1.28.0+
except Exception:
    pymupdf = None

try:
    import pytesseract
    from PIL import Image
    _HAS_OCR = True
    if "TESSERACT_CMD" in os.environ:
        pytesseract.pytesseract.tesseract_cmd = os.environ["TESSERACT_CMD"]
except Exception:
    _HAS_OCR = False


def extract_raw_page_blocks(pdf_path: str, options: Any) -> List[Dict[str, Any]]:
    """Extract raw structured blocks from each page using PyMuPDF.

    Returns a list of page dicts containing page number, dimensions, and blocks.
    """
    if pymupdf is None:
        raise RuntimeError("PyMuPDF is not installed. Install with `uv pip install pymupdf`.")

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found at: {pdf_path}")

    doc = pymupdf.open(pdf_path)
    try:
        total_pages = len(doc)
        limit = total_pages if not getattr(options, "preview_only", False) else min(3, total_pages)
        pages_data = []

        for pno in range(limit):
            page = doc.load_page(pno)
            text_dict = page.get_text("dict")
            
            # Extract basic metadata
            rect = page.rect
            width, height = rect.width, rect.height

            # Check if page is scanned/empty and needs OCR fallback
            blocks = text_dict.get("blocks", [])
            text_content = "".join([span["text"] for b in blocks if "lines" in b for l in b["lines"] for span in l.get("spans", [])]).strip()

            if len(text_content) < 50 and getattr(options, "ocr_mode", "auto") != "off" and _HAS_OCR:
                # Perform Tesseract OCR on page image
                pix = page.get_pixmap(dpi=300)
                img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("L")
                try:
                    ocr_data = pytesseract.image_to_data(
                        img,
                        lang=getattr(options, "ocr_lang", "eng"),
                        config=r"--oem 3 --psm 3",
                        output_type=pytesseract.Output.DICT,
                    )
                    blocks = _convert_tesseract_to_blocks(ocr_data)
                except Exception:
                    pass

            # Extract native vector/grid tables using PyMuPDF find_tables()
            native_tables = []
            if getattr(options, "detect_tables", True):
                try:
                    table_finder = page.find_tables()
                    if hasattr(table_finder, "tables"):
                        for tbl in table_finder.tables:
                            extracted = tbl.extract()
                            if extracted and len(extracted) > 0:
                                # Clean cells
                                clean_rows = []
                                for row in extracted:
                                    clean_row = [c.replace("\n", " ").strip() if c else "" for c in row]
                                    if any(clean_row):
                                        clean_rows.append(clean_row)
                                if clean_rows:
                                    native_tables.append({
                                        "bbox": list(tbl.bbox),
                                        "headers": clean_rows[0],
                                        "rows": clean_rows[1:] if len(clean_rows) > 1 else [],
                                    })
                except Exception:
                    pass

            pages_data.append({
                "page_number": pno + 1,
                "width": width,
                "height": height,
                "blocks": blocks,
                "native_tables": native_tables,
            })

        return pages_data
    finally:
        doc.close()


def _convert_tesseract_to_blocks(ocr_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Convert pytesseract dictionary output to PyMuPDF block format."""
    blocks: List[Dict[str, Any]] = []
    texts = ocr_data.get("text", [])
    n_boxes = len(texts)
    current_block: Dict[str, Any] = {"type": 0, "lines": []}
    current_line: Dict[str, Any] = {"spans": []}
    last_block_num = -1
    last_line_num = -1

    for i in range(n_boxes):
        text = str(texts[i]).strip()
        if not text:
            continue
        
        block_num = ocr_data.get("block_num", [])[i] if i < len(ocr_data.get("block_num", [])) else -1
        line_num = ocr_data.get("line_num", [])[i] if i < len(ocr_data.get("line_num", [])) else -1

        span = {
            "text": text,
            "size": 11.0,
            "flags": 0,
            "font": "Tesseract",
            "bbox": (
                ocr_data.get("left", [0])[i] if i < len(ocr_data.get("left", [])) else 0,
                ocr_data.get("top", [0])[i] if i < len(ocr_data.get("top", [])) else 0,
                (ocr_data.get("left", [0])[i] + ocr_data.get("width", [0])[i]) if i < len(ocr_data.get("left", [])) and i < len(ocr_data.get("width", [])) else 0,
                (ocr_data.get("top", [0])[i] + ocr_data.get("height", [0])[i]) if i < len(ocr_data.get("top", [])) and i < len(ocr_data.get("height", [])) else 0,
            )
        }

        if block_num != last_block_num:
            if current_line["spans"]:
                current_block["lines"].append(current_line)
                current_line = {"spans": []}
            if current_block["lines"]:
                blocks.append(current_block)
                current_block = {"type": 0, "lines": []}

        if line_num != last_line_num and current_line["spans"]:
            current_block["lines"].append(current_line)
            current_line = {"spans": []}

        spans_list: List[Any] = current_line["spans"]
        spans_list.append(span)
        last_block_num = block_num
        last_line_num = line_num

    if current_line["spans"]:
        lines_list2: List[Any] = current_block["lines"]
        lines_list2.append(current_line)
    if current_block["lines"]:
        blocks.append(current_block)

    return blocks

"""Main orchestrator pipeline for PDF to YAML conversion."""

from __future__ import annotations
import os
from typing import Optional
from .models import Options, YamlDocument
from .extract import extract_raw_page_blocks
from .transform import transform_blocks_to_document
from .render import render_document_to_yaml


def pdf_to_yaml(
    input_pdf: str,
    output_yaml: Optional[str] = None,
    options: Optional[Options] = None,
) -> YamlDocument:
    """Convert a PDF file to a structured YAML output file or YamlDocument object.

    Args:
        input_pdf: Path to the input PDF file.
        output_yaml: Path where the YAML output file should be saved.
        options: Conversion options.

    Returns:
        The generated YamlDocument object.
    """
    if options is None:
        options = Options()

    if not os.path.exists(input_pdf):
        raise FileNotFoundError(f"Input PDF file not found: {input_pdf}")

    # Stage 1: Extract layout blocks
    pages_data = extract_raw_page_blocks(input_pdf, options)

    # Stage 2: Transform blocks into structured YamlDocument model
    yaml_doc = transform_blocks_to_document(pages_data, input_pdf, options)

    # Stage 3: Render to clean YAML string and save if output_yaml path provided
    yaml_str = render_document_to_yaml(yaml_doc)

    if output_yaml:
        output_dir = os.path.dirname(os.path.abspath(output_yaml))
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        with open(output_yaml, "w", encoding="utf-8") as f:
            f.write(yaml_str)

    return yaml_doc

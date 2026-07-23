"""Unit tests for pdf2yaml pipeline."""

import os
import pytest
from pdf2yaml import pdf_to_yaml, Options

SAMPLE_PDF = os.path.join(
    os.path.dirname(__file__),
    "..",
    "data",
    "pdfs",
    "algo_trading_general",
    "0704.2259_the_wiretap_channel_with_feedback_encryption_over_.pdf",
)


def test_pdf_to_yaml_pipeline(tmp_path):
    assert os.path.exists(SAMPLE_PDF), f"Sample PDF missing at {SAMPLE_PDF}"
    
    out_yaml = tmp_path / "output.yaml"
    opts = Options(ocr_mode="off", preview_only=True)
    
    doc = pdf_to_yaml(SAMPLE_PDF, str(out_yaml), options=opts)
    
    assert doc is not None
    assert doc.metadata.total_pages > 0
    assert len(doc.pages) > 0
    assert os.path.exists(out_yaml)
    
    yaml_content = out_yaml.read_text(encoding="utf-8")
    assert "metadata:" in yaml_content
    assert "pages:" in yaml_content

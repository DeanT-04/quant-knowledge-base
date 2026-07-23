import pytest
from pdf2yaml.models import (
    YamlDocument,
    DocumentMetadata,
    PageNode,
    SectionNode,
    EquationNode,
    TableNode,
    Options,
)

def test_models_creation():
    opts = Options(ocr_mode="off", export_images=False)
    assert opts.ocr_mode == "off"

    eq = EquationNode(id="eq_1", latex="E=mc^2")
    assert eq.id == "eq_1"

    tbl = TableNode(headers=["A", "B"], rows=[["1", "2"]])
    assert tbl.headers == ["A", "B"]

    sec = SectionNode(title="Intro", level=1, paragraphs=["Hello world"], equations=[eq], tables=[tbl])
    assert sec.title == "Intro"

    page = PageNode(page_number=1, sections=[sec])
    meta = DocumentMetadata(title="Test", total_pages=1)
    
    doc = YamlDocument(metadata=meta, pages=[page])
    assert doc.metadata.title == "Test"
    assert len(doc.pages) == 1

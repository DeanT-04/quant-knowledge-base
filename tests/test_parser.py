"""Unit tests for paper parser module."""

from pathlib import Path
from unittest.mock import MagicMock
import pytest

from research_paper_knowledge.parser import PaperParser


def test_paper_parser_file_not_found(tmp_path):
    parser = PaperParser()
    missing_file = tmp_path / "nonexistent.pdf"
    with pytest.raises(FileNotFoundError):
        parser.parse_pdf(missing_file)


def test_paper_parser_convert(tmp_path):
    pdf_file = tmp_path / "paper.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 dummy content")

    mock_doc = MagicMock()
    mock_doc.export_to_markdown.return_value = "# Abstract\nPaper text"
    mock_doc.export_to_dict.return_value = {"title": "Paper Title"}

    mock_result = MagicMock()
    mock_result.document = mock_doc

    mock_converter = MagicMock()
    mock_converter.convert.return_value = mock_result

    parser = PaperParser(converter=mock_converter)
    md_text, json_dict = parser.parse_pdf(pdf_file)

    assert md_text == "# Abstract\nPaper text"
    assert json_dict == {"title": "Paper Title"}
    mock_converter.convert.assert_called_once_with(str(pdf_file))


def test_paper_parser_fallback(tmp_path, monkeypatch):
    pdf_file = tmp_path / "failing.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 dummy failing content")

    mock_converter = MagicMock()
    mock_converter.convert.side_effect = RuntimeError("Docling memory error")

    parser = PaperParser(converter=mock_converter)
    md_text, json_dict = parser.parse_pdf(pdf_file)

    assert "Unable to parse PDF text layer" in md_text or "Document: failing" in md_text
    assert json_dict["title"] == "failing"


def test_paper_parser_fallback_with_pypdf(tmp_path, monkeypatch):
    pdf_file = tmp_path / "sample.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 content")

    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Page content"
    mock_reader = MagicMock()
    mock_reader.pages = [mock_page]

    mock_pypdf = MagicMock()
    mock_pypdf.PdfReader.return_value = mock_reader
    monkeypatch.setitem(__import__("sys").modules, "pypdf", mock_pypdf)

    parser = PaperParser()
    md_text, json_dict = parser._fallback_parse(pdf_file, error_msg="Test Error")
    assert "Document: sample" in md_text
    assert json_dict["title"] == "sample"
    assert json_dict["parse_mode"] == "fallback"


def test_paper_parser_fallback_exception(tmp_path, monkeypatch):
    pdf_file = tmp_path / "sample_err.pdf"
    pdf_file.write_bytes(b"corrupted")

    mock_pypdf = MagicMock()
    mock_pypdf.PdfReader.side_effect = Exception("PyPDF failure")
    monkeypatch.setitem(__import__("sys").modules, "pypdf", mock_pypdf)

    parser = PaperParser()
    md_text, json_dict = parser._fallback_parse(pdf_file, error_msg="Test Error")
    assert "Unable to parse PDF text layer" in md_text
    assert json_dict["parse_mode"] == "error"



def test_paper_parser_lazy_converter(monkeypatch):
    mock_docling = MagicMock()
    mock_converter_class = MagicMock()
    mock_docling.DocumentConverter = mock_converter_class

    monkeypatch.setitem(__import__("sys").modules, "docling.document_converter", mock_docling)
    monkeypatch.setitem(__import__("sys").modules, "docling.datamodel.base_models", MagicMock())
    monkeypatch.setitem(__import__("sys").modules, "docling.datamodel.pipeline_options", MagicMock())

    parser = PaperParser()
    conv = parser.converter
    assert conv is not None


def test_parse_pdf_directory_not_found(tmp_path):
    from research_paper_knowledge.parser import parse_pdf_directory

    missing_dir = tmp_path / "missing"
    with pytest.raises(FileNotFoundError):
        parse_pdf_directory(missing_dir, tmp_path / "out")


def test_parse_pdf_directory_process_skip_fail(tmp_path):
    from research_paper_knowledge.parser import parse_pdf_directory

    input_dir = tmp_path / "in"
    sub_dir = input_dir / "cat1"
    sub_dir.mkdir(parents=True)

    pdf1 = sub_dir / "paper1.pdf"
    pdf1.write_bytes(b"%PDF content 1")
    pdf2 = sub_dir / "paper2.pdf"
    pdf2.write_bytes(b"%PDF content 2")
    pdf3 = sub_dir / "paper3.pdf"
    pdf3.write_bytes(b"%PDF content 3")

    output_dir = tmp_path / "out"
    out_cat = output_dir / "cat1"
    out_cat.mkdir(parents=True)

    # Pre-create paper1 md and json so it gets skipped
    (out_cat / "paper1.md").write_text("existing md")
    (out_cat / "paper1.json").write_text("{}")

    mock_parser = MagicMock()
    mock_parser.parse_pdf.side_effect = [
        ("# Paper 2", {"title": "paper2"}),  # for paper2
        RuntimeError("parse failed"),          # for paper3
    ]

    stats = parse_pdf_directory(input_dir, output_dir, parser=mock_parser)

    assert stats["skipped"] == 1
    assert stats["processed"] == 1
    assert stats["failed"] == 1
    assert (out_cat / "paper2.md").read_text() == "# Paper 2"
    assert (out_cat / "paper2.json").exists()


def test_parse_pdf_directory_default_parser(tmp_path, monkeypatch):
    from research_paper_knowledge.parser import parse_pdf_directory

    input_dir = tmp_path / "in_def"
    input_dir.mkdir()

    mock_parser_instance = MagicMock()
    mock_parser_instance.parse_pdf.return_value = ("# Default", {"title": "def"})
    monkeypatch.setattr("research_paper_knowledge.parser.PaperParser", lambda: mock_parser_instance)

    pdf = input_dir / "doc.pdf"
    pdf.write_bytes(b"%PDF content")

    output_dir = tmp_path / "out_def"
    stats = parse_pdf_directory(input_dir, output_dir)
    assert stats["processed"] == 1
    assert (output_dir / "doc.md").exists()


def test_safe_print_normal(capsys):
    from research_paper_knowledge.parser import safe_print
    safe_print("hello world")
    captured = capsys.readouterr()
    assert "hello world" in captured.out


def test_safe_print_unicode_error(capsys, monkeypatch):
    from research_paper_knowledge.parser import safe_print

    # Mock print to raise UnicodeEncodeError only once to test fallback
    failed = False
    orig_print = print
    def mock_print(msg, *args, **kwargs):
        nonlocal failed
        if msg == "bad_char" and not failed:
            failed = True
            raise UnicodeEncodeError("charmap", msg, 0, 1, "unsupported")
        orig_print(msg, *args, **kwargs)

    monkeypatch.setitem(__import__("builtins").__dict__, "print", mock_print)
    safe_print("bad_char")
    captured = capsys.readouterr()
    assert "bad_char" in captured.out or "???" in captured.out or "bad_char" in captured.err


def test_safe_print_exception_fallback(capsys, monkeypatch):
    from research_paper_knowledge.parser import safe_print

    failed = False
    orig_print = print
    def mock_print(msg, *args, **kwargs):
        nonlocal failed
        if msg == "bad_char" and not failed:
            failed = True
            raise UnicodeEncodeError("charmap", msg, 0, 1, "unsupported")
        orig_print(msg, *args, **kwargs)

    monkeypatch.setitem(__import__("builtins").__dict__, "print", mock_print)

    import sys
    orig_stdout = sys.stdout
    class BadStdout:
        @property
        def encoding(self):
            raise RuntimeError("mock encoding error")
        def write(self, s):
            orig_stdout.write(s)
        def flush(self):
            orig_stdout.flush()

    monkeypatch.setattr(sys, "stdout", BadStdout())

    safe_print("bad_char")
    captured = capsys.readouterr()
    assert "bad_char" in captured.out or "???" in captured.out








"""Unit tests for paper parser module."""

import json
from pathlib import Path
from unittest.mock import MagicMock
import pytest

from research_paper_knowledge.parser import (
    PaperParser,
    is_output_complete,
    parse_pdf_directory,
    recommended_worker_count,
)


# ---------------------------------------------------------------------------
# PaperParser.parse_pdf / fallback behavior (unchanged core logic)
# ---------------------------------------------------------------------------


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


def test_paper_parser_fallback(tmp_path):
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


# ---------------------------------------------------------------------------
# Lazy converter construction / optimized pipeline options
# ---------------------------------------------------------------------------


def test_paper_parser_lazy_converter_builds_optimized_pipeline(monkeypatch):
    captured = {}

    mock_docling_dc = MagicMock()

    def fake_document_converter(format_options):
        captured["format_options"] = format_options
        return MagicMock()

    mock_docling_dc.DocumentConverter.side_effect = fake_document_converter
    mock_docling_dc.PdfFormatOption.side_effect = lambda pipeline_options: MagicMock(
        pipeline_options=pipeline_options
    )

    mock_base_models = MagicMock()
    mock_base_models.InputFormat.PDF = "PDF"

    mock_pipeline_options_mod = MagicMock()
    captured_options = {}

    class FakePdfPipelineOptions:
        def __init__(self):
            self.do_ocr = None
            self.do_table_structure = None
            self.table_structure_options = None
            self.do_formula_enrichment = None
            self.do_code_enrichment = None
            self.do_picture_classification = None
            self.do_picture_description = None
            self.generate_page_images = None
            self.generate_picture_images = None
            self.accelerator_options = None
            captured_options["instance"] = self

    class FakeTableStructureOptions:
        def __init__(self, mode, do_cell_matching):
            self.mode = mode
            self.do_cell_matching = do_cell_matching

    mock_pipeline_options_mod.PdfPipelineOptions = FakePdfPipelineOptions
    mock_pipeline_options_mod.TableStructureOptions = FakeTableStructureOptions
    mock_pipeline_options_mod.TableFormerMode = MagicMock(ACCURATE="ACCURATE", FAST="FAST")

    mock_accel_mod = MagicMock()
    mock_accel_mod.AcceleratorDevice = MagicMock(AUTO="AUTO", CPU="CPU", CUDA="CUDA", MPS="MPS")
    mock_accel_mod.AcceleratorOptions.side_effect = lambda num_threads, device: MagicMock(
        num_threads=num_threads, device=device
    )

    sys_modules = __import__("sys").modules
    monkeypatch.setitem(sys_modules, "docling.document_converter", mock_docling_dc)
    monkeypatch.setitem(sys_modules, "docling.datamodel.base_models", mock_base_models)
    monkeypatch.setitem(sys_modules, "docling.datamodel.pipeline_options", mock_pipeline_options_mod)
    monkeypatch.setitem(sys_modules, "docling.datamodel.accelerator_options", mock_accel_mod)

    parser = PaperParser(num_threads=4, device="cpu")
    conv = parser.converter
    assert conv is not None

    opts = captured_options["instance"]
    # The whole point of the optimization: formulas and tables are on,
    # accuracy mode is used, and irrelevant/expensive stages are off.
    assert opts.do_ocr is False
    assert opts.do_table_structure is True
    assert opts.do_formula_enrichment is True
    assert opts.table_structure_options.do_cell_matching is True
    assert opts.do_code_enrichment is False
    assert opts.do_picture_classification is False
    assert opts.do_picture_description is False
    assert opts.generate_page_images is False
    assert opts.generate_picture_images is False
    assert opts.accelerator_options.num_threads == 4
    assert opts.accelerator_options.device == "CPU"


def test_recommended_worker_count_returns_positive_int():
    assert recommended_worker_count() >= 1


# ---------------------------------------------------------------------------
# is_output_complete
# ---------------------------------------------------------------------------


def test_is_output_complete_missing_files(tmp_path):
    assert is_output_complete(tmp_path / "a.md", tmp_path / "a.json") is False


def test_is_output_complete_empty_files(tmp_path):
    md = tmp_path / "a.md"
    js = tmp_path / "a.json"
    md.write_text("")
    js.write_text("")
    assert is_output_complete(md, js) is False


def test_is_output_complete_corrupt_json(tmp_path):
    md = tmp_path / "a.md"
    js = tmp_path / "a.json"
    md.write_text("some text")
    js.write_text("{not valid json")
    assert is_output_complete(md, js) is False


def test_is_output_complete_fallback_mode(tmp_path):
    md = tmp_path / "a.md"
    js = tmp_path / "a.json"
    md.write_text("some text")
    js.write_text(json.dumps({"parse_mode": "fallback"}))
    assert is_output_complete(md, js) is False


def test_is_output_complete_undecoded_formula(tmp_path):
    md = tmp_path / "a.md"
    js = tmp_path / "a.json"
    md.write_text("some text")
    js.write_text(json.dumps({"texts": [{"label": "formula", "text": ""}]}))
    assert is_output_complete(md, js) is False


def test_is_output_complete_empty_table(tmp_path):
    md = tmp_path / "a.md"
    js = tmp_path / "a.json"
    md.write_text("some text")
    js.write_text(json.dumps({"tables": [{"data": {"num_rows": 0, "num_cols": 0}}]}))
    assert is_output_complete(md, js) is False


def test_is_output_complete_true(tmp_path):
    md = tmp_path / "a.md"
    js = tmp_path / "a.json"
    md.write_text("some text")
    js.write_text(
        json.dumps(
            {
                "texts": [{"label": "formula", "text": "x = y"}],
                "tables": [{"data": {"num_rows": 3, "num_cols": 2}}],
            }
        )
    )
    assert is_output_complete(md, js) is True


# ---------------------------------------------------------------------------
# parse_pdf_directory
# ---------------------------------------------------------------------------


def test_parse_pdf_directory_not_found(tmp_path):
    missing_dir = tmp_path / "missing"
    with pytest.raises(FileNotFoundError):
        parse_pdf_directory(missing_dir, tmp_path / "out")


def test_parse_pdf_directory_process_skip_fail(tmp_path):
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

    # Pre-create a genuinely complete paper1 output so it gets skipped.
    (out_cat / "paper1.md").write_text("existing md")
    (out_cat / "paper1.json").write_text(json.dumps({"texts": [], "tables": []}))

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


def test_parse_pdf_directory_force_reprocesses_complete_output(tmp_path):
    input_dir = tmp_path / "in"
    input_dir.mkdir()
    pdf = input_dir / "doc.pdf"
    pdf.write_bytes(b"%PDF content")

    output_dir = tmp_path / "out"
    output_dir.mkdir()
    (output_dir / "doc.md").write_text("old md")
    (output_dir / "doc.json").write_text(json.dumps({"texts": [], "tables": []}))

    mock_parser = MagicMock()
    mock_parser.parse_pdf.return_value = ("# New", {"title": "doc"})

    stats = parse_pdf_directory(input_dir, output_dir, parser=mock_parser, force=True)
    assert stats["processed"] == 1
    assert stats["skipped"] == 0
    assert (output_dir / "doc.md").read_text() == "# New"


def test_parse_pdf_directory_default_parser(tmp_path, monkeypatch):
    input_dir = tmp_path / "in_def"
    input_dir.mkdir()

    mock_parser_instance = MagicMock()
    mock_parser_instance.parse_pdf.return_value = ("# Default", {"title": "def"})
    monkeypatch.setattr(
        "research_paper_knowledge.parser.PaperParser", lambda **kwargs: mock_parser_instance
    )

    pdf = input_dir / "doc.pdf"
    pdf.write_bytes(b"%PDF content")

    output_dir = tmp_path / "out_def"
    stats = parse_pdf_directory(input_dir, output_dir)
    assert stats["processed"] == 1
    assert (output_dir / "doc.md").exists()


def test_parse_pdf_directory_no_files_to_process(tmp_path):
    input_dir = tmp_path / "empty_in"
    input_dir.mkdir()
    output_dir = tmp_path / "empty_out"
    stats = parse_pdf_directory(input_dir, output_dir)
    assert stats == {"processed": 0, "skipped": 0, "failed": 0}


def test_parse_pdf_directory_injected_parser_ignores_max_workers(tmp_path):
    """An explicitly injected parser always runs single-process, even if
    max_workers > 1, since a live object/mock can't cross process boundaries."""
    input_dir = tmp_path / "in"
    input_dir.mkdir()
    pdf = input_dir / "doc.pdf"
    pdf.write_bytes(b"%PDF content")

    output_dir = tmp_path / "out"
    mock_parser = MagicMock()
    mock_parser.parse_pdf.return_value = ("# Doc", {"title": "doc"})

    stats = parse_pdf_directory(input_dir, output_dir, parser=mock_parser, max_workers=4)
    assert stats["processed"] == 1
    mock_parser.parse_pdf.assert_called_once()


# ---------------------------------------------------------------------------
# Multi-worker dispatch internals
# ---------------------------------------------------------------------------


def test_worker_parse_one_success(tmp_path, monkeypatch):
    import research_paper_knowledge.parser as parser_mod

    monkeypatch.setattr(parser_mod, "_WORKER_PARSER", None)

    pdf = tmp_path / "doc.pdf"
    pdf.write_bytes(b"%PDF")
    md_file = tmp_path / "out" / "doc.md"
    json_file = tmp_path / "out" / "doc.json"

    mock_doc = MagicMock()
    mock_doc.export_to_markdown.return_value = "# X"
    mock_doc.export_to_dict.return_value = {"a": 1}
    mock_result = MagicMock(document=mock_doc)
    mock_converter = MagicMock()
    mock_converter.convert.return_value = mock_result

    path, ok, err = parser_mod._worker_parse_one(
        (pdf, md_file, json_file, {"converter": mock_converter})
    )
    assert ok is True
    assert err is None
    assert md_file.read_text() == "# X"
    assert json.loads(json_file.read_text()) == {"a": 1}
    # The parser built for this worker process is cached for subsequent files.
    assert parser_mod._WORKER_PARSER is not None


def test_worker_parse_one_failure(tmp_path, monkeypatch):
    import research_paper_knowledge.parser as parser_mod

    monkeypatch.setattr(parser_mod, "_WORKER_PARSER", None)

    pdf = tmp_path / "doc.pdf"
    pdf.write_bytes(b"%PDF")
    md_file = tmp_path / "out" / "doc.md"
    json_file = tmp_path / "out" / "doc.json"

    mock_converter = MagicMock()
    mock_converter.convert.side_effect = RuntimeError("boom")

    # parse_pdf falls back to pypdf on error rather than raising, so force a
    # hard failure by making the fallback path blow up too.
    monkeypatch.setattr(
        parser_mod.PaperParser,
        "_fallback_parse",
        lambda self, path, error_msg: (_ for _ in ()).throw(RuntimeError("fallback boom")),
    )

    path, ok, err = parser_mod._worker_parse_one(
        (pdf, md_file, json_file, {"converter": mock_converter})
    )
    assert ok is False
    assert "fallback boom" in err


def test_parse_pdf_directory_multi_worker_dispatch(tmp_path, monkeypatch):
    """Exercises the ProcessPoolExecutor dispatch path without paying the
    cost of a real process pool / real Docling models."""
    import research_paper_knowledge.parser as parser_mod

    input_dir = tmp_path / "in"
    input_dir.mkdir()
    (input_dir / "a.pdf").write_bytes(b"%PDF")
    (input_dir / "b.pdf").write_bytes(b"%PDF")
    output_dir = tmp_path / "out"

    class FakeFuture:
        def __init__(self, result):
            self._result = result

        def result(self):
            return self._result

    class FakePool:
        def __init__(self, max_workers):
            self.max_workers = max_workers

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def submit(self, fn, task):
            pdf_file, md_file, json_file, kwargs = task
            md_file.parent.mkdir(parents=True, exist_ok=True)
            md_file.write_text(f"# {pdf_file.name}")
            json_file.write_text(json.dumps({"texts": [], "tables": []}))
            return FakeFuture((str(pdf_file), True, None))

    monkeypatch.setattr(parser_mod, "ProcessPoolExecutor", FakePool)
    monkeypatch.setattr(
        parser_mod,
        "as_completed",
        lambda futures: list(futures.keys()),
    )

    stats = parse_pdf_directory(input_dir, output_dir, max_workers=2, parser_kwargs={})
    assert stats["processed"] == 2
    assert stats["failed"] == 0
    assert (output_dir / "a.md").exists()
    assert (output_dir / "b.md").exists()


# ---------------------------------------------------------------------------
# safe_print (unchanged)
# ---------------------------------------------------------------------------


def test_safe_print_normal(capsys):
    from research_paper_knowledge.parser import safe_print
    safe_print("hello world")
    captured = capsys.readouterr()
    assert "hello world" in captured.out


def test_safe_print_unicode_error(capsys, monkeypatch):
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


# ---------------------------------------------------------------------------
# Watchdog timeout tests
# ---------------------------------------------------------------------------


def _mock_hanging_worker(pdf_path, do_table_structure, do_formula_enrichment, table_mode, num_threads, device, queue):
    import time
    time.sleep(5)
    queue.put((True, "# Late markdown", {"title": "late"}))


def test_paper_parser_watchdog_timeout(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "research_paper_knowledge.parser._subprocess_parse_pdf_worker",
        _mock_hanging_worker
    )
    
    mock_reader = MagicMock()
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Fallback Page Text"
    mock_reader.pages = [mock_page]
    
    mock_pypdf = MagicMock()
    mock_pypdf.PdfReader.return_value = mock_reader
    monkeypatch.setitem(__import__("sys").modules, "pypdf", mock_pypdf)
    
    pdf_file = tmp_path / "timeout.pdf"
    pdf_file.write_bytes(b"%PDF")
    
    parser = PaperParser(timeout=0.2, use_watchdog=True)
    md_text, json_dict = parser.parse_pdf(pdf_file)
    
    assert "Document: timeout" in md_text
    assert json_dict["parse_mode"] == "fallback"
    assert "timed out after 0.2 seconds" in json_dict["error"]



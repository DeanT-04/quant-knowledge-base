import os
import pytest
import sys
from pdf2yaml.cli import main

def test_cli_help(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main_args = ["pdf2yaml", "--help"]
        sys.argv = main_args
        main()
    assert exc_info.value.code == 0


def test_cli_conversion(tmp_path):
    pdf_path = os.path.join("data", "pdfs", "algo_trading_general", "0704.2259_the_wiretap_channel_with_feedback_encryption_over_.pdf")
    assert os.path.exists(pdf_path), f"Sample PDF not found at {pdf_path}"

    output_yaml = tmp_path / "cli_output.yaml"
    sys.argv = ["pdf2yaml", pdf_path, "-o", str(output_yaml), "--preview"]
    main()
    
    assert output_yaml.exists()
    content = output_yaml.read_text(encoding="utf-8")
    assert len(content) > 0
    assert "metadata:" in content

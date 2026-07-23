"""Dedicated test suite for math equation and table extraction in pdf2yaml."""

import pytest
from pdf2yaml.transform import _is_equation, _clean_math_expression, _is_table_block, _build_table_node


def test_equation_detection_and_label_extraction():
    # Test equation with explicit label (1)
    text = "C_s = \\max_{P_X} [I(X; Y) - I(X; Z)]   (1)"
    is_eq, eq_id, math_clean = _is_equation(text)
    assert is_eq is True
    assert eq_id == "(1)"
    assert "C_s = \\max_{P_X}" in math_clean

    # Test equation with equation number (12a)
    text2 = "H(K) \\ge H(M)   (12a)"
    is_eq2, eq_id2, math_clean2 = _is_equation(text2)
    assert is_eq2 is True
    assert eq_id2 == "(12a)"

    # Test math symbol normalization (unicode to LaTeX)
    raw_math = "α + β ≤ γ × σ"
    cleaned = _clean_math_expression(raw_math)
    assert "\\alpha" in cleaned
    assert "\\beta" in cleaned
    assert "\\le" in cleaned
    assert "\\times" in cleaned
    assert "\\sigma" in cleaned


def test_table_grid_detection():
    block = {
        "lines": [
            {"spans": [{"text": "Symbol   Description   Value"}]},
            {"spans": [{"text": "M        Message       100"}]},
            {"spans": [{"text": "Z        Noise         50"}]},
        ]
    }
    assert _is_table_block(block) is True
    tbl_node = _build_table_node(block)
    assert tbl_node is not None
    assert tbl_node.headers == ["Symbol", "Description", "Value"]
    assert len(tbl_node.rows) == 2
    assert tbl_node.rows[0] == ["M", "Message", "100"]

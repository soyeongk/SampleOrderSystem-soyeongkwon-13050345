from views.table import compute_column_widths, display_width, pad, render_row


def test_display_width_counts_ascii_as_one_per_character():
    assert display_width("S-001") == 5


def test_display_width_counts_korean_as_two_per_character():
    assert display_width("웨이퍼") == 6


def test_pad_fills_based_on_display_width_for_ascii():
    result = pad("S-001", 10)

    assert result == "S-001     "


def test_pad_fills_based_on_display_width_for_korean():
    result = pad("웨이퍼", 10)

    assert display_width(result) == 10
    assert result.startswith("웨이퍼")


def test_pad_does_not_truncate_when_text_exceeds_width():
    result = pad("실리콘 웨이퍼-12인치", 5)

    assert result == "실리콘 웨이퍼-12인치"


def test_compute_column_widths_uses_max_of_header_and_cells():
    widths = compute_column_widths(
        ["이름", "재고"],
        [["실리콘 웨이퍼-12인치", 10], ["A", 5]],
    )

    assert widths[0] == display_width("실리콘 웨이퍼-12인치")
    assert widths[1] == display_width("재고")


def test_render_row_pads_each_cell_to_column_width_plus_gap():
    widths = [10, 5]

    row = render_row(["AB", "C"], widths, gap=2)

    assert row == pad("AB", 12) + pad("C", 7)


def test_render_row_produces_equal_width_lines_for_different_content():
    widths = compute_column_widths(["이름"], [["짧음"], ["아주긴이름텍스트입니다"]])

    short_line = render_row(["짧음"], widths)
    long_line = render_row(["아주긴이름텍스트입니다"], widths)

    assert display_width(short_line) == display_width(long_line)

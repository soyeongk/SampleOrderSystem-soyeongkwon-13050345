from views.table import display_width, pad


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

    assert result.startswith("실리콘 웨이퍼-12인치")


def test_pad_keeps_minimum_gap_when_text_reaches_or_exceeds_width():
    exact_fit = pad("게르마늄 웨이퍼-4인치", 20)  # display width exactly 20
    overflow = pad("실리콘 웨이퍼-12인치", 5)

    assert exact_fit.endswith("  ")
    assert overflow.endswith("  ")

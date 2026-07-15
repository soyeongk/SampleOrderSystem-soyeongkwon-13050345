from controllers.pagination import paginate, resolve_page_selection


def test_paginate_returns_first_page_with_up_to_page_size_items():
    items = list(range(1, 26))  # 25 items

    page = paginate(items, page_number=1, page_size=10)

    assert page.items == list(range(1, 11))
    assert page.page_number == 1
    assert page.total_pages == 3


def test_paginate_returns_remaining_items_on_last_page():
    items = list(range(1, 26))  # 25 items

    page = paginate(items, page_number=3, page_size=10)

    assert page.items == [21, 22, 23, 24, 25]
    assert page.page_number == 3


def test_paginate_clamps_page_below_1_to_1():
    items = list(range(1, 26))

    page = paginate(items, page_number=0, page_size=10)

    assert page.page_number == 1
    assert page.items == list(range(1, 11))


def test_paginate_clamps_page_above_total_to_last():
    items = list(range(1, 26))

    page = paginate(items, page_number=99, page_size=10)

    assert page.page_number == 3
    assert page.items == [21, 22, 23, 24, 25]


def test_paginate_returns_empty_page_when_no_items():
    page = paginate([], page_number=1, page_size=10)

    assert page.items == []
    assert page.total_pages == 0
    assert page.page_number == 1


def test_resolve_page_selection_returns_item_for_valid_number():
    items = ["a", "b", "c"]
    page = paginate(items, page_number=1, page_size=10)

    assert resolve_page_selection(page, "2") == "b"


def test_resolve_page_selection_returns_none_for_out_of_range_number():
    items = ["a", "b", "c"]
    page = paginate(items, page_number=1, page_size=10)

    assert resolve_page_selection(page, "4") is None


def test_resolve_page_selection_returns_none_for_non_numeric_command():
    items = ["a", "b", "c"]
    page = paginate(items, page_number=1, page_size=10)

    assert resolve_page_selection(page, "n") is None

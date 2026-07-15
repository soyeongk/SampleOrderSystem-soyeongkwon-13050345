import unicodedata


def display_width(text) -> int:
    text = str(text)
    return sum(2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1 for ch in text)


def pad(text, width: int) -> str:
    text = str(text)
    gap = max(0, width - display_width(text))
    return text + " " * gap


def compute_column_widths(headers, rows) -> list:
    widths = [display_width(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], display_width(cell))
    return widths


def render_row(cells, widths, gap: int = 2) -> str:
    return "".join(pad(cell, width + gap) for cell, width in zip(cells, widths))

import math
from dataclasses import dataclass


@dataclass
class Page:
    items: list
    page_number: int
    total_pages: int


def paginate(items: list, page_number: int, page_size: int = 10) -> Page:
    total_pages = math.ceil(len(items) / page_size) if items else 0

    if total_pages == 0:
        return Page(items=[], page_number=1, total_pages=0)

    clamped_page_number = max(1, min(page_number, total_pages))
    start = (clamped_page_number - 1) * page_size
    end = start + page_size

    return Page(items=items[start:end], page_number=clamped_page_number, total_pages=total_pages)


def resolve_page_selection(page: Page, command: str):
    if not command.isdigit():
        return None
    index = int(command) - 1
    if 0 <= index < len(page.items):
        return page.items[index]
    return None

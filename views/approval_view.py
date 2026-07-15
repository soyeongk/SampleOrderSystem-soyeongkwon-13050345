from views.screen import clear_screen
from views.table import compute_column_widths, render_row


class ApprovalView:
    def show_pending_page(self, page) -> None:
        clear_screen()
        print("--- 주문 승인/거절 (RESERVED) ---")
        print()
        if not page.items:
            print("승인 대기 중인 주문이 없습니다.")
        else:
            headers = ["번호", "주문번호", "시료ID", "고객명", "수량"]
            rows = [
                [i, o.order_id, o.sample_id, o.customer_name, o.quantity]
                for i, o in enumerate(page.items, start=1)
            ]
            widths = compute_column_widths(headers, rows)
            print(render_row(headers, widths))
            for row in rows:
                print(render_row(row, widths))
        print()
        print(f"[페이지 {page.page_number}/{page.total_pages}] n: 다음, p: 이전, b: 이전 메뉴로, 번호: 선택")

    def read_page_command(self) -> str:
        return input("선택: ").strip()

    def read_decision(self) -> str:
        return input("[1] 승인  [2] 거절: ").strip()

    def show_result(self, order_id: str, new_status: str) -> None:
        print(f"처리 완료: {order_id} -> {new_status}")

    def show_error(self, message: str) -> None:
        print(f"처리 실패: {message}")

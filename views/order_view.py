from views.screen import clear_screen
from views.table import compute_column_widths, render_row


class OrderView:
    def show_sample_page(self, page) -> None:
        clear_screen()
        print("--- 시료 주문(예약) : 시료 선택 ---")
        print()
        if not page.items:
            print("등록된 시료가 없습니다.")
        else:
            headers = ["번호", "시료ID", "이름", "재고", "수율"]
            rows = [
                [i, s.sample_id, s.name, s.stock_quantity, s.yield_rate]
                for i, s in enumerate(page.items, start=1)
            ]
            widths = compute_column_widths(headers, rows)
            print(render_row(headers, widths))
            for row in rows:
                print(render_row(row, widths))
        print()
        print(f"[페이지 {page.page_number}/{page.total_pages}] n: 다음, p: 이전, b: 이전 메뉴로, 번호: 선택")

    def read_sample_page_command(self) -> str:
        return input("선택: ").strip()

    def read_customer_name(self) -> str:
        return input("고객명: ").strip()

    def read_quantity(self) -> str:
        return input("주문 수량: ").strip()

    def show_order_summary(self, sample, customer_name: str, quantity: int) -> None:
        print()
        print("--- 입력 내용 확인 ---")
        print(f"시료: {sample.name} ({sample.sample_id})")
        print(f"고객: {customer_name}")
        print(f"수량: {quantity} ea")
        print("[Y] 예약 접수  [N] 취소")

    def read_confirmation(self) -> str:
        return input("선택: ").strip()

    def show_reservation_cancelled(self) -> None:
        print("예약이 취소되었습니다.")

    def show_order_success(self, order) -> None:
        print(
            f"주문 예약 완료: {order.order_id} | 시료 {order.sample_id} | "
            f"고객 {order.customer_name} | 수량 {order.quantity} | 상태 {order.status}"
        )

    def show_order_error(self, message: str) -> None:
        print(f"주문 실패: {message}")

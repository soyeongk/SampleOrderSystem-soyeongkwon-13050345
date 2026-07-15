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

    def show_approval_summary(self, summary) -> None:
        print()
        print("--- 승인 내용 확인 ---")
        print(f"시료: {summary.sample_name}")
        print(f"현재 재고: {summary.current_stock} ea")
        print(f"주문 수량: {summary.order_quantity} ea")
        print(f"부족분: {summary.shortfall} ea")
        if summary.is_insufficient:
            print("* 재고 부족")
            print(f"실 생산량: {summary.actual_quantity} ea")
            print(f"생산 시간: {summary.total_production_minutes}분")

    def read_decision(self) -> str:
        return input("[1] 승인  [2] 거절: ").strip()

    def show_result(self, order_id: str, new_status: str) -> None:
        print(f"처리 완료: {order_id} -> {new_status}")

    def show_error(self, message: str) -> None:
        print(f"처리 실패: {message}")

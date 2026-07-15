from views.screen import clear_screen


class ApprovalView:
    def show_pending_page(self, page) -> None:
        clear_screen()
        print("--- 주문 승인/거절 (RESERVED) ---")
        if not page.items:
            print("승인 대기 중인 주문이 없습니다.")
            return
        for i, order in enumerate(page.items, start=1):
            print(
                f"{i}. {order.order_id} | 시료 {order.sample_id} | "
                f"고객 {order.customer_name} | 수량 {order.quantity}"
            )
        print(f"[페이지 {page.page_number}/{page.total_pages}] n: 다음, p: 이전, 번호: 선택")

    def read_page_command(self) -> str:
        return input("선택: ").strip()

    def read_decision(self) -> str:
        return input("[1] 승인  [2] 거절: ").strip()

    def show_result(self, order_id: str, new_status: str) -> None:
        print(f"처리 완료: {order_id} -> {new_status}")

    def show_error(self, message: str) -> None:
        print(f"처리 실패: {message}")

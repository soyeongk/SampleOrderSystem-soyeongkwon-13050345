from views.screen import clear_screen


class OrderView:
    def show_sample_page(self, page) -> None:
        clear_screen()
        print("--- 시료 주문(예약) : 시료 선택 ---")
        if not page.items:
            print("등록된 시료가 없습니다.")
            return
        for i, sample in enumerate(page.items, start=1):
            print(
                f"{i}. {sample.name} ({sample.sample_id}) | "
                f"재고 {sample.stock_quantity} | 수율 {sample.yield_rate}"
            )
        print(f"[페이지 {page.page_number}/{page.total_pages}] n: 다음, p: 이전, b: 이전 메뉴로, 번호: 선택")

    def read_sample_page_command(self) -> str:
        return input("선택: ").strip()

    def read_customer_name(self) -> str:
        return input("고객명: ").strip()

    def read_quantity(self) -> str:
        return input("주문 수량: ").strip()

    def show_order_success(self, order) -> None:
        print(
            f"주문 예약 완료: {order.order_id} | 시료 {order.sample_id} | "
            f"고객 {order.customer_name} | 수량 {order.quantity} | 상태 {order.status}"
        )

    def show_order_error(self, message: str) -> None:
        print(f"주문 실패: {message}")

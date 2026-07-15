class OrderView:
    def show_order_menu(self) -> None:
        print()
        print("--- 시료 주문(예약) ---")

    def read_new_order_input(self) -> dict:
        sample_id = input("시료 ID: ").strip()
        customer_name = input("고객명: ").strip()
        quantity = input("주문 수량: ").strip()
        return {
            "sample_id": sample_id,
            "customer_name": customer_name,
            "quantity": quantity,
        }

    def show_order_success(self, order) -> None:
        print(
            f"주문 예약 완료: {order.order_id} | 시료 {order.sample_id} | "
            f"고객 {order.customer_name} | 수량 {order.quantity} | 상태 {order.status}"
        )

    def show_order_error(self, message: str) -> None:
        print(f"주문 실패: {message}")

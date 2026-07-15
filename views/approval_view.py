class ApprovalView:
    def show_pending_orders(self, orders) -> None:
        print()
        print("--- 주문 승인/거절 (RESERVED) ---")
        if not orders:
            print("승인 대기 중인 주문이 없습니다.")
            return
        for order in orders:
            print(
                f"{order.order_id} | 시료 {order.sample_id} | "
                f"고객 {order.customer_name} | 수량 {order.quantity}"
            )

    def read_target_order_id(self) -> str:
        return input("승인/거절할 주문번호: ").strip()

    def read_decision(self) -> str:
        return input("[1] 승인  [2] 거절: ").strip()

    def show_result(self, order_id: str, new_status: str) -> None:
        print(f"처리 완료: {order_id} -> {new_status}")

    def show_error(self, message: str) -> None:
        print(f"처리 실패: {message}")

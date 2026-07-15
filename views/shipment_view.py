class ShipmentView:
    def show_shippable_orders(self, orders) -> None:
        print()
        print("--- 출고 처리 (CONFIRMED) ---")
        if not orders:
            print("출고 가능한 주문이 없습니다.")
            return
        for order in orders:
            print(
                f"{order.order_id} | 시료 {order.sample_id} | "
                f"고객 {order.customer_name} | 수량 {order.quantity}"
            )

    def read_target_order_id(self) -> str:
        return input("출고할 주문번호: ").strip()

    def show_result(self, order_id: str, new_status: str) -> None:
        print(f"출고 처리 완료: {order_id} -> {new_status}")

    def show_error(self, message: str) -> None:
        print(f"출고 실패: {message}")

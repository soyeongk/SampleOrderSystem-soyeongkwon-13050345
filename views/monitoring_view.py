class MonitoringView:
    def show_order_status_counts(self, counts: dict) -> None:
        print()
        print("--- 주문량 확인 (REJECTED 제외) ---")
        for status, count in counts.items():
            print(f"{status}: {count}건")

    def show_inventory_status(self, rows: list) -> None:
        print()
        print("--- 재고량 확인 ---")
        if not rows:
            print("등록된 시료가 없습니다.")
            return
        for row in rows:
            print(
                f"{row.sample_id} | {row.name} | 재고 {row.stock_quantity} | "
                f"대기수요 {row.pending_demand} | 상태 {row.status}"
            )
        print()
        print(
            "* 재고는 승인(CONFIRMED) 시점에 이미 차감된 수량입니다. "
            "출고 처리 전이라도 승인된 주문만큼은 재고에서 미리 빠져 있습니다."
        )

class ProductionView:
    def show_current_status(self, status_entry) -> None:
        print()
        print("--- 생산 현황 ---")
        if status_entry is None:
            print("현재 생산 중인 항목이 없습니다.")
            return
        print(
            f"주문번호 {status_entry.order_id} | 시료 {status_entry.sample_id} | "
            f"실 생산량 {status_entry.actual_quantity} | "
            f"총 생산 시간 {status_entry.total_production_minutes}분 | "
            f"시작 {status_entry.started_at}"
        )

    def show_waiting_queue(self, waiting_entries) -> None:
        print()
        print("--- 대기 주문 (FIFO) ---")
        if not waiting_entries:
            print("대기 중인 주문이 없습니다.")
            return
        for order_no, entry in enumerate(waiting_entries, start=1):
            print(f"{order_no}. 주문번호 {entry.order_id} | 시료 {entry.sample_id} | 수량 {entry.quantity}")

    def show_force_complete_result(self) -> None:
        print()
        print("[Test용] 생산 시간을 강제로 경과시켰습니다.")

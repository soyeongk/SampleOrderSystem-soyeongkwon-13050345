class DummyDataView:
    def read_sample_count(self) -> str:
        return input("생성할 시료 개수: ").strip()

    def show_result(self, created_samples: list) -> None:
        print(f"더미 시료 {len(created_samples)}건 생성 완료:")
        for sample in created_samples:
            print(f"{sample.sample_id} | {sample.name} | 재고 {sample.stock_quantity}")

    def show_error(self, message: str) -> None:
        print(f"생성 실패: {message}")

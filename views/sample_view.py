class SampleView:
    def show_registration_menu(self) -> None:
        print()
        print("--- 시료 등록 ---")

    def read_new_sample_input(self) -> dict:
        name = input("시료 이름: ").strip()
        average_production_minutes = input("평균 생산시간(분): ").strip()
        yield_rate = input("수율(0~1): ").strip()
        stock_quantity = input("재고 수량: ").strip()
        return {
            "name": name,
            "average_production_minutes": average_production_minutes,
            "yield_rate": yield_rate,
            "stock_quantity": stock_quantity,
        }

    def show_registration_success(self, sample) -> None:
        print(f"등록 완료: {sample.sample_id} - {sample.name}")

    def show_registration_error(self, message: str) -> None:
        print(f"등록 실패: {message}")

    def show_lookup_menu(self) -> None:
        print()
        print("--- 시료 조회 ---")
        print("1. 전체 목록")
        print("2. 이름으로 검색")

    def read_lookup_choice(self) -> str:
        return input("조회 방식을 선택하세요: ").strip()

    def read_search_keyword(self) -> str:
        return input("검색할 이름 키워드: ").strip()

    def show_sample_list(self, samples: list) -> None:
        if not samples:
            print("등록된 시료가 없습니다.")
            return
        for sample in samples:
            print(
                f"{sample.sample_id} | {sample.name} | "
                f"평균생산시간 {sample.average_production_minutes}분 | "
                f"수율 {sample.yield_rate} | 재고 {sample.stock_quantity}"
            )

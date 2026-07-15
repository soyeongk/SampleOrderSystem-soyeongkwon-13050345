from views.screen import clear_screen
from views.table import compute_column_widths, render_row


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

    def show_sample_page(self, page) -> None:
        clear_screen()
        print("--- 시료 조회 결과 ---")
        print()
        if not page.items:
            print("등록된 시료가 없습니다.")
        else:
            headers = ["번호", "시료ID", "이름", "평균생산시간", "수율", "재고"]
            rows = [
                [i, s.sample_id, s.name, s.average_production_minutes, s.yield_rate, s.stock_quantity]
                for i, s in enumerate(page.items, start=1)
            ]
            widths = compute_column_widths(headers, rows)
            print(render_row(headers, widths))
            for row in rows:
                print(render_row(row, widths))
        print()
        print(f"[페이지 {page.page_number}/{page.total_pages}] n: 다음, p: 이전, b: 이전 메뉴로")

    def read_sample_browse_command(self) -> str:
        return input("선택: ").strip()

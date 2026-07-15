class MainView:
    def show_menu(self) -> None:
        print()
        print("===== S-Semi 시료 생산주문관리 시스템 =====")
        print("1. 시료 등록")
        print("2. 시료 조회")
        print("3. 시료 주문(예약)")
        print("4. 주문 승인/거절")
        print("5. 생산 라인 조회")
        print("6. 종료")

    def read_menu_choice(self) -> str:
        return input("메뉴를 선택하세요: ").strip()

    def show_unknown_choice(self) -> None:
        print("올바른 메뉴 번호를 입력하세요.")

    def show_goodbye(self) -> None:
        print("시스템을 종료합니다.")

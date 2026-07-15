from views.screen import clear_screen


class MainView:
    def show_screen_header(self, title: str) -> None:
        clear_screen()
        print("===== S-Semi 시료 생산주문관리 시스템 =====")
        print(f"[ 현재 메뉴: {title} ]")

    def show_menu(self) -> None:
        clear_screen()
        print()
        print("===== S-Semi 시료 생산주문관리 시스템 =====")
        print("1. 시료 등록")
        print("2. 시료 조회")
        print("3. 시료 주문(예약)")
        print("4. 주문 승인/거절")
        print("5. 생산 라인 조회")
        print("6. 모니터링")
        print("7. 출고 처리")
        print("8. [Test용] 생산 시간 강제 경과")
        print("9. 종료")

    def read_menu_choice(self) -> str:
        return input("메뉴를 선택하세요: ").strip()

    def wait_for_continue(self) -> None:
        input("\n계속하려면 Enter를 누르세요...")

    def show_unknown_choice(self) -> None:
        print("올바른 메뉴 번호를 입력하세요.")

    def show_goodbye(self) -> None:
        print("시스템을 종료합니다.")

from datetime import datetime

from controllers.approval_controller import ApprovalController
from controllers.monitoring_controller import MonitoringController
from controllers.order_controller import OrderController
from controllers.production_line_controller import ProductionLineController
from controllers.sample_controller import SampleController
from controllers.shipment_controller import ShipmentController
from repository.order_repository import OrderRepository
from repository.production_queue_repository import ProductionQueueRepository
from repository.sample_repository import SampleRepository
from views.approval_view import ApprovalView
from views.main_view import MainView
from views.monitoring_view import MonitoringView
from views.order_view import OrderView
from views.production_view import ProductionView
from views.sample_view import SampleView
from views.shipment_view import ShipmentView


class MainController:
    def __init__(self, samples_file_path, orders_file_path, production_queue_file_path):
        self.main_view = MainView()
        self.production_view = ProductionView()
        self.monitoring_view = MonitoringView()
        sample_repository = SampleRepository(samples_file_path)
        order_repository = OrderRepository(orders_file_path)
        production_queue_repository = ProductionQueueRepository(production_queue_file_path)
        self.sample_controller = SampleController(sample_repository, SampleView())
        self.order_controller = OrderController(order_repository, sample_repository, OrderView())
        self.approval_controller = ApprovalController(
            order_repository, sample_repository, production_queue_repository, ApprovalView()
        )
        self.production_line_controller = ProductionLineController(
            order_repository, sample_repository, production_queue_repository
        )
        self.monitoring_controller = MonitoringController(order_repository, sample_repository)
        self.shipment_controller = ShipmentController(order_repository, ShipmentView())
        self.menu_titles = {
            "1": "시료 등록",
            "2": "시료 조회",
            "3": "시료 주문(예약)",
            "4": "주문 승인/거절",
            "5": "생산 라인 조회",
            "6": "모니터링",
            "7": "출고 처리",
        }

    def run(self) -> None:
        is_running = True
        while is_running:
            self.main_view.show_menu()
            choice = self.main_view.read_menu_choice()

            if choice in self.menu_titles:
                self.main_view.show_screen_header(self.menu_titles[choice])

            if choice == "1":
                self.sample_controller.register_sample()
            elif choice == "2":
                self.sample_controller.browse_samples()
            elif choice == "3":
                self.order_controller.reserve_order()
            elif choice == "4":
                self.approval_controller.handle_menu()
            elif choice == "5":
                now = datetime.now()
                self.production_view.show_current_status(
                    self.production_line_controller.get_current_status(now)
                )
                self.production_view.show_waiting_queue(
                    self.production_line_controller.get_waiting_queue()
                )
            elif choice == "6":
                self.monitoring_view.show_order_status_counts(
                    self.monitoring_controller.get_order_status_counts()
                )
                self.monitoring_view.show_inventory_status(
                    self.monitoring_controller.get_inventory_status()
                )
            elif choice == "7":
                self.shipment_controller.handle_menu()
            elif choice == "8":
                self.main_view.show_goodbye()
                is_running = False
            else:
                self.main_view.show_unknown_choice()

            if is_running:
                self.main_view.wait_for_continue()

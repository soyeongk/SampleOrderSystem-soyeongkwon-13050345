from datetime import datetime

from controllers.approval_controller import ApprovalController
from controllers.order_controller import OrderController
from controllers.production_line_controller import ProductionLineController
from controllers.sample_controller import SampleController
from repository.order_repository import OrderRepository
from repository.production_queue_repository import ProductionQueueRepository
from repository.sample_repository import SampleRepository
from views.approval_view import ApprovalView
from views.main_view import MainView
from views.order_view import OrderView
from views.production_view import ProductionView
from views.sample_view import SampleView


class MainController:
    def __init__(self, samples_file_path, orders_file_path, production_queue_file_path):
        self.main_view = MainView()
        self.production_view = ProductionView()
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

    def run(self) -> None:
        is_running = True
        while is_running:
            self.main_view.show_menu()
            choice = self.main_view.read_menu_choice()

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
                self.main_view.show_goodbye()
                is_running = False
            else:
                self.main_view.show_unknown_choice()

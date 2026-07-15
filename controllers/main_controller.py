from controllers.order_controller import OrderController
from controllers.sample_controller import SampleController
from repository.order_repository import OrderRepository
from repository.sample_repository import SampleRepository
from views.main_view import MainView
from views.order_view import OrderView
from views.sample_view import SampleView


class MainController:
    def __init__(self, samples_file_path, orders_file_path):
        self.main_view = MainView()
        sample_repository = SampleRepository(samples_file_path)
        order_repository = OrderRepository(orders_file_path)
        self.sample_controller = SampleController(sample_repository, SampleView())
        self.order_controller = OrderController(order_repository, sample_repository, OrderView())

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
                self.main_view.show_goodbye()
                is_running = False
            else:
                self.main_view.show_unknown_choice()

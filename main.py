import os

from controllers.main_controller import MainController

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
SAMPLES_FILE_PATH = os.path.join(DATA_DIR, "samples.json")
ORDERS_FILE_PATH = os.path.join(DATA_DIR, "orders.json")
PRODUCTION_QUEUE_FILE_PATH = os.path.join(DATA_DIR, "production_queue.json")


def main() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    MainController(SAMPLES_FILE_PATH, ORDERS_FILE_PATH, PRODUCTION_QUEUE_FILE_PATH).run()


if __name__ == "__main__":
    main()

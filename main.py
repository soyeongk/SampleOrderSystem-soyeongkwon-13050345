import os

from controllers.main_controller import MainController

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
SAMPLES_FILE_PATH = os.path.join(DATA_DIR, "samples.json")


def main() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    MainController(SAMPLES_FILE_PATH).run()


if __name__ == "__main__":
    main()

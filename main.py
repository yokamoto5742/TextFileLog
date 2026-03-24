import sys

from app.main_window import MainApp
from service.file_processor import FileProcessor
from utils.config_manager import ConfigManager


def run_auto() -> None:
    """--auto モード: GUIなしで処理して終了"""
    config = ConfigManager()
    operations = config.load()
    if not operations:
        return
    FileProcessor().process_all(operations)


def main() -> None:
    if "--auto" in sys.argv:
        run_auto()
    else:
        MainApp().mainloop()


if __name__ == "__main__":
    main()

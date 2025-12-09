from PyQt6.QtWidgets import QApplication
import sys
from src.view.home_ui import AutomationApp


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AutomationApp()
    window.show()
    sys.exit(app.exec())
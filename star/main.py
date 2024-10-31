from PySide6.QtWidgets import *
from justGui import GuiForm


def main():
    app = QApplication()

    window = GuiForm()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()

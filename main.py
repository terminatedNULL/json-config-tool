import sys
import application_window as app_wind
from PyQt5.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)

    window = app_wind.ApplicationWindow()
    window.show()

    app.exec()

if __name__ == "__main__":
    main()
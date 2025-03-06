from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon
from enum import Enum

class Severity(Enum):
    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'
    SUCCESS = 'success'

def show_popup(severity: Severity, message: str, icon: str = None):
    msg_box = QMessageBox()
    msg_box.setMinimumWidth(400)

    if icon:
        msg_box.setWindowIcon(QIcon(icon))
    
    if severity == Severity.INFO:
        if not icon:
            msg_box.setWindowIcon(QIcon("assets/icons/info.png"))
        msg_box.setWindowTitle("Information")
    elif severity == Severity.WARNING:
        if not icon:
            msg_box.setWindowIcon(QIcon("assets/icons/warning.png"))
        msg_box.setWindowTitle("Warning")
    elif severity == Severity.SUCCESS:
        if not icon:
            msg_box.setWindowIcon(QIcon("assets/icons/success.png"))
        msg_box.setWindowTitle("Success")
    elif severity == Severity.ERROR:
        if not icon:
            msg_box.setWindowIcon(QIcon("assets/icons/error.png"))
        msg_box.setWindowTitle("Error")

        
    msg_box.setText(message)
    msg_box.exec_()
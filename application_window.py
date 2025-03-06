import json, os, shutil
import stylesheet as style
from popups import show_popup, Severity

from enum import Enum
from datetime import date
from extra_gui import QHLine, QVLine

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QFontMetrics
from PyQt5.QtWidgets import (
    QMainWindow,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
    QLineEdit,
    QFileDialog,
    QFormLayout,
    QSizePolicy,
    QListWidget,
    QListWidgetItem,
    QScrollArea
)

class Options(Enum):
    CREATE: int = 0
    EDIT: int = 1

class SelectType(Enum):
    DIRECTORY = 0
    FILE = 1

class ApplicationWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.loaded_file = None
        self.loaded_data = None
        self.edit_fields = {}

        # Window setup
        self.setWindowTitle("LIMS Parser Configuration Tool")
        self.setWindowIcon(QIcon("assets/icons/signature.png"))
        self.setFixedSize(QSize(1000, 600))
        central_widget = QWidget(self)

        # Layout setup
        main_column_layout = QVBoxLayout(central_widget)

        # Top button row
        button_layout = QHBoxLayout()

        self.create_button = QPushButton("Create")
        self.edit_button = QPushButton("Edit / View")
        self.save_button = QPushButton()
        self.save_button.setIcon(QIcon("assets/icons/file_open.png"))

        self.create_button.setFixedHeight(30)
        self.edit_button.setFixedHeight(30)
        self.save_button.setFixedSize(30, 30)
        self.save_mode = False

        self.create_button.clicked.connect(self.create_config)
        self.edit_button.clicked.connect(self.edit_config)
        self.save_button.clicked.connect(self.save_load_button)

        button_layout.addWidget(self.create_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.save_button)

        # Create group
        self.create_group = QWidget()
        create_form = QFormLayout(self.create_group)

        self.create_name = QLineEdit("config_%s" % date.today().strftime("%d_%m_%y"))
        self.create_name.setFont(QFont("Arial", pointSize=10))

        create_label = QLabel("Configuration File Name : ")
        create_label.setFont(QFont("Arial", weight=QFont.Bold, pointSize=10))
        create_form.addRow(create_label, self.create_name)

        self.create_save_path = QLineEdit(os.getcwd())
        self.create_save_path.setFont(QFont("Arial", pointSize=10))

        self.create_save_button = QPushButton(" Select Folder")
        self.create_save_button.setFont(QFont("Arial", weight=QFont.Bold, pointSize=10))
        self.create_save_button.setIcon(QIcon("assets/icons/file_open.png"))
        self.create_save_button.setFixedWidth(165)
        self.create_save_button.clicked.connect(lambda: self.select_file_for(self.create_save_path, SelectType.DIRECTORY))
        create_form.addRow(self.create_save_button, self.create_save_path)

        self.create_file_button = QPushButton("Create File")
        self.create_file_button.clicked.connect(self.create_file)
        create_form.addRow(self.create_file_button)

        # Edit group
        self.edit_group = QWidget()
        self.edit_scroll = QScrollArea(self)
        self.edit_scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.edit_layout = QVBoxLayout(scroll_content)
        self.edit_scroll.setWidget(scroll_content)
        self.edit_scroll.setFixedHeight(460)
        self.edit_group.setLayout(QVBoxLayout())
        self.edit_group.layout().addWidget(self.edit_scroll)

        temp_text = QLabel("No File Loaded!")
        temp_text.setFont(QFont("Arial", pointSize=10, weight=QFont.Bold))
        temp_text.setAlignment(Qt.AlignCenter)
        self.edit_layout.addWidget(temp_text)

        self.create_group.setVisible(False)
        self.edit_group.setVisible(False)

        # Build main layout
        main_column_layout.addLayout(button_layout)
        main_column_layout.addWidget(QHLine())
        main_column_layout.addWidget(self.create_group)
        main_column_layout.addWidget(self.edit_group)
        main_column_layout.addStretch()

        # Loaded file text
        self.bottom_widget = QWidget()
        self.bottom_widget.setFixedHeight(40)
        bottom_layout = QHBoxLayout(self.bottom_widget)

        bottom_label = QLabel("Current Configuration : ")
        bottom_label.setFont(QFont("Arial", weight=QFont.Bold, pointSize=10))
        self.current_configuration = QLabel("No File Loaded!")
        self.current_configuration.setFont(QFont("Arial", pointSize=10))
        self.current_configuration.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        bottom_layout.addWidget(bottom_label)
        bottom_layout.addWidget(self.current_configuration)
        bottom_layout.setAlignment(Qt.AlignLeft)
        main_column_layout.addWidget(self.bottom_widget)

        self.select_button(Options.CREATE)
        self.setCentralWidget(central_widget)

    def create_config(self):
        self.select_button(Options.CREATE)

    def edit_config(self):
        self.select_button(Options.EDIT)

        if self.edit_group.layout().count() == 1 and self.loaded_data is not None:
            self.clear_widgets(self.edit_layout)
            layout = self.edit_layout
            
            for name, value in self.loaded_data.items():
                label = QLabel(name.replace("_", " ").title())
                label.setFont(QFont("Arial", weight=QFont.Bold, pointSize=10))

                list = QListWidget()
                for entry in value:
                    list.addItem(QListWidgetItem(entry))
                
                controls = QWidget()
                controls_layout = QHBoxLayout(controls)

                entry_field = QLineEdit()
                entry_field.setPlaceholderText("...")

                open_button = QPushButton()
                open_button.setIcon(QIcon("assets/icons/file_open.png"))
                open_button.clicked.connect(lambda checked, target=name: self.select_item(target))

                add_button = QPushButton("+")
                add_button.clicked.connect(lambda checked, target=name: self.add_item(target))

                remove_button = QPushButton("-")
                remove_button.clicked.connect(lambda checked, target=name: self.remove_item(target))

                self.edit_fields[name] = {
                    "list": list,
                    "entry": entry_field,
                    "select": open_button,
                }

                controls_layout.addWidget(open_button)
                controls_layout.addWidget(entry_field)
                controls_layout.addWidget(add_button)
                controls_layout.addWidget(remove_button)

                layout.addWidget(label)
                layout.addWidget(list)
                layout.addWidget(controls)

    def add_item(self, target):
        text = self.edit_fields[target]["entry"].text()
        if text != "":
            self.edit_fields[target]["list"].addItem(QListWidgetItem(text))
            QListWidgetItem(self.edit_fields[target]["entry"].setText(""))

    def remove_item(self, target):
        self.edit_fields[target]["list"].takeItem(self.edit_fields[target]["list"].currentRow())

    def select_item(self, target):
        self.select_file_for(self.edit_fields[target]["entry"])

    def select_button(self, button):
        self.edit_button.setStyleSheet(style.button_selected if button == Options.EDIT else style.button_normal)
        self.create_button.setStyleSheet(style.button_selected if button == Options.CREATE else style.button_normal)

        self.edit_group.setVisible(True if button == Options.EDIT else False)
        self.create_group.setVisible(True if button == Options.CREATE else False)

    def select_file_for(self, widget, select_type=SelectType.FILE):
        dialog = QFileDialog(self)
        dialog.setWindowTitle("Select Save Folder")
        dialog.setViewMode(QFileDialog.ViewMode.Detail)

        if select_type == SelectType.FILE:
            dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        else:
            dialog.setFileMode(QFileDialog.FileMode.DirectoryOnly)

        if dialog.exec():
            files = dialog.selectedFiles()
            widget.setText(files[0])

    def select_file(self, select_type=SelectType.FILE):
        dialog = QFileDialog(self)
        dialog.setWindowTitle("Select Save Folder")
        dialog.setViewMode(QFileDialog.ViewMode.Detail)

        if select_type == SelectType.FILE:
            dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        else:
            dialog.setFileMode(QFileDialog.FileMode.DirectoryOnly)

        if dialog.exec():
            files = dialog.selectedFiles()
            return files[0]

    def save_load_button(self):
        if self.save_mode:
            self.save_file()
            return

        self.load_file(self.select_file())
        self.save_button.setIcon(QIcon("assets/icons/save.png"))

    def clear_widgets(self, group):
        if group.layout() is not None:
            old_layout = group.layout()
            while old_layout.count():
                item = old_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

    def create_file(self):
        name = self.create_save_path.text() + "\\" + self.create_name.text() + ".json"
        if os.path.exists(name):
            show_popup(Severity.ERROR, "File '%s.json' already exists at the specified path!" % self.create_name.text())
            return

        shutil.copyfile("assets\\template.json", name)
        self.load_file(name)

    def save_file(self):
        if not self.loaded_file or not self.loaded_data:
            return

        if not os.path.exists(self.loaded_file):
            show_popup(Severity.ERROR, "Invalid file save path!")
            return

        for name, value in self.edit_fields.items():
            try:
                new_data = []
                for i in range(value["list"].count()):
                    entry = value["list"].item(i)
                    new_data.append(entry.text())

                self.loaded_data[name] = new_data
            except Exception as e:
                show_popup(Severity.ERROR, "Failed to save, invalid entry name! %s" % e)
                return

        with open(self.loaded_file, "w") as file:
            file.write(json.dumps(self.loaded_data))

        show_popup(Severity.SUCCESS, "Configuration saved successfully!")

    def load_file(self, file_name):
        obj = json.loads(open(file_name, "r").read())

        self.loaded_data = obj
        self.loaded_file = file_name

        font_metrics = QFontMetrics(self.current_configuration.font())
        elided_text = font_metrics.elidedText(file_name, Qt.ElideLeft, self.current_configuration.width())
        name_start = elided_text.rfind("\\") + 1
        elided_text = elided_text[:name_start] + "<b>" + elided_text[name_start:] + "<\\b>"
        self.current_configuration.setText(elided_text)
        self.edit_config()
        self.save_button.setIcon(QIcon("assets/icons/save.png"))
        self.save_mode = True
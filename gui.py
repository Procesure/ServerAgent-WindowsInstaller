from typing import Callable
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QTextEdit, QStackedWidget
)
from PyQt5.QtCore import pyqtSignal, QThread, Qt

from installers.models import *


class InstallationWorker(QThread):
    finished = pyqtSignal()

    def __init__(
        self,
        config: InstallationConfig,
        install_function: Callable[[InstallationConfig], None]
    ) -> None:

        super().__init__()
        self.config = config
        self.install_function = install_function

    def run(self) -> None:

        try:
            self.install_function(self.config)
            self.finished.emit()
        except Exception as e:
            print(f"Installation error: {e}")


class MultiStepInstaller(QMainWindow):

    def __init__(
        self,
        install_function: Callable[[InstallationConfig], None]
    ) -> None:

        super().__init__()

        self.worker = None
        self.steps: QStackedWidget = None
        self.config: InstallationConfig = InstallationConfig()
        self.log_output: QTextEdit = None
        self.installation_root_dir: QLineEdit = None
        self.tcp_token: QLineEdit = None
        self.tcp_address: QLineEdit = None
        self.ssh_public_key: QLineEdit = None
        self.rdp_username: QLineEdit = None
        self.rdp_password: QLineEdit = None

        self.steps = QStackedWidget()
        self.step1 = self.create_step1()
        self.step2 = self.create_step2()
        self.step3 = self.create_step3()

        self.init_ui()
        self.install_function = install_function

    def init_ui(self) -> None:

        self.setWindowTitle("Procesure Server Agent Installer")
        self.setMinimumSize(600, 400)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #f7f9fb;
            }
            QLabel {
                color: #34495e;
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 10px;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                font-size: 14px;
                margin-bottom: 10px;
            }
            QLineEdit::placeholder {
                color: #95a5a6;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #2471a3;
            }
            QTextEdit {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 8px;
                font-family: Consolas, monospace;
                font-size: 12px;
                color: #2c3e50;
                background-color: white;
            }
        """)

        self.steps.addWidget(self.step1)
        self.steps.addWidget(self.step2)
        self.steps.addWidget(self.step3)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        layout.addWidget(self.steps)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def show_step(self, step_index: int) -> None:
        self.steps.setCurrentIndex(step_index)
        self.clear_error_messages()

    def validate_and_next(self) -> None:
        current_step = self.steps.currentIndex()
        try:
            self.validate_current_step(current_step)
            self.show_step(current_step + 1)
        except ValueError as e:
            self.log_output.append(f"Error: {e}")

    def validate_current_step(self, step_index: int) -> None:

        if step_index == 0:

            path = self.installation_root_dir.text().strip()
            if not path:
                raise ValueError("Installation path is required.")

            self.config.installation_root_dir = Path(path)

        elif step_index == 1:

            token = self.tcp_token.text().strip()
            address = self.tcp_address.text().strip()
            public_key = self.ssh_public_key.text().strip()

            if not token or not address:
                raise ValueError("Authentication token and TCP address are required.")

            self.config.tcp.token = token
            self.config.tcp.address = address
            self.config.ssh.public_key = public_key

        elif step_index == 2:
            username = self.rdp_username.text().strip()
            password = self.rdp_password.text().strip()
            if not username or not password:
                raise ValueError("Username and password are required.")
            self.config.rdp.username = username
            self.config.rdp.password = password

    def clear_error_messages(self) -> None:
        if self.log_output:
            self.log_output.clear()

    def create_step1(self) -> QWidget:

        step = QWidget()
        layout = QVBoxLayout()

        title = QLabel("Step 1: Select the installation path")
        layout.addWidget(title)

        self.installation_root_dir = QLineEdit()
        self.installation_root_dir.setPlaceholderText("Enter installation path or browse")
        self.installation_root_dir.setText(str(self.config.installation_root_dir))
        layout.addWidget(self.installation_root_dir)

        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.handle_browse_install_path)
        layout.addWidget(browse_btn)

        next_btn = QPushButton("Next")
        next_btn.clicked.connect(self.validate_and_next)
        layout.addWidget(next_btn)

        step.setLayout(layout)
        return step

    def create_step2(self) -> QWidget:

        step = QWidget()
        layout = QVBoxLayout()

        title = QLabel("Step 2: Enter TCP Address Information")
        layout.addWidget(title)

        self.tcp_address = QLineEdit()
        self.tcp_address.setPlaceholderText("Enter TCP address")
        layout.addWidget(self.tcp_address)

        self.tcp_token = QLineEdit()
        self.tcp_token.setPlaceholderText("Enter authentication token")
        layout.addWidget(self.tcp_token)

        self.ssh_public_key = QLineEdit()
        self.ssh_public_key.setPlaceholderText("Paste public key")
        layout.addWidget(self.ssh_public_key)

        next_btn = QPushButton("Next")
        next_btn.clicked.connect(self.validate_and_next)
        layout.addWidget(next_btn)

        step.setLayout(layout)
        return step

    def create_step3(self) -> QWidget:

        step = QWidget()
        layout = QVBoxLayout()

        title = QLabel("Step 5: Enter Client Credentials")
        layout.addWidget(title)

        description = QLabel(
            "Note: The credentials entered here are stored securely as Windows credentials on this machine and are not transmitted externally.")
        description.setWordWrap(True)  # Enable word wrapping for longer text
        layout.addWidget(description)

        self.rdp_username = QLineEdit()
        self.rdp_username.setPlaceholderText("Enter username")
        layout.addWidget(self.rdp_username)

        self.rdp_password = QLineEdit()
        self.rdp_password.setPlaceholderText("Enter password")
        self.rdp_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.rdp_password)

        next_btn = QPushButton("Next")
        next_btn.clicked.connect(self.validate_and_next)
        layout.addWidget(next_btn)

        step.setLayout(layout)
        return step

    def handle_browse_install_path(self) -> None:

        folder = QFileDialog.getExistingDirectory(self, "Select Installation Path")
        if folder:
            self.installation_root_dir.setText(folder)

    def start_installation(self) -> None:

        self.log_output.append("Starting installation...")
        self.worker = InstallationWorker(config=self.config, install_function=self.install_function)
        self.worker.finished.connect(self.on_installation_finished)
        self.worker.start()

    def on_installation_finished(self) -> None:
        self.log_output.append("Installation complete.")

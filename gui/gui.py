from typing import Callable
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QStackedWidget
)
from PyQt5.QtCore import pyqtSignal, QThread, Qt

from .logger import GUILogger

from installers.models import InstallationConfig


class InstallationWorker(QThread):

    finished = pyqtSignal(str)  # Signal to emit completion message

    def __init__(
        self,
        config: InstallationConfig,
        install_function: Callable[[InstallationConfig, GUILogger], None],
        logger: GUILogger
    ) -> None:

        super().__init__()
        self.config = config
        self.install_function = install_function
        self.logger = logger

    def run(self) -> None:
        try:
            self.install_function(
                self.config,
                self.logger
            )
            self.finished.emit("Installation complete.")
        except Exception as e:
            self.finished.emit(f"Installation error: {e}")


class MultiStepInstaller(QMainWindow):

    def __init__(
        self,
        install_function: Callable[[InstallationConfig, GUILogger], None]
    ) -> None:

        super().__init__()

        self.worker = None

        self.steps: QStackedWidget = QStackedWidget()
        self.config: InstallationConfig = InstallationConfig()

        self.log_output: QTextEdit = QTextEdit()

        self.tcp_token: QLineEdit = QLineEdit()
        self.tcp_address: QLineEdit = QLineEdit()
        self.ssh_public_key: QLineEdit = QLineEdit()
        self.rdp_username: QLineEdit = QLineEdit()
        self.rdp_password: QLineEdit = QLineEdit()

        self.step1 = self.create_step1()
        self.step2 = self.create_step2()
        self.step3 = self.create_step3()

        self.logger = GUILogger(self.log_output)

        self.init_ui()
        self.install_function = install_function

    def init_ui(self) -> None:

        self.setWindowTitle("Procesure Server Agent Installer")
        self.setMinimumSize(600, 400)
        self.setup_stylesheet()

        self.log_output.setReadOnly(True)
        self.steps.addWidget(self.step1)
        self.steps.addWidget(self.step2)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        layout.addWidget(self.steps)
        layout.addWidget(self.log_output)  # Add the log output to the layout

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def setup_stylesheet(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f7f9fb;
            }
            QLabel, QLineEdit, QPushButton, QTextEdit {
                margin-bottom: 10px;
            }
            QLabel {
                color: #34495e;
                font-size: 16px;
                font-weight: bold;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                font-size: 14px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
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

    def validate_and_next(self) -> None:
        current_step = self.steps.currentIndex()
        try:
            self.validate_current_step(current_step)
            if current_step + 1 < self.steps.count():
                self.show_step(current_step + 1)
            else:
                self.start_installation()
        except ValueError as e:
            self.log_output.append(f"Error: {e}")

    def validate_current_step(self, step_index: int) -> None:

        if step_index == 0:
            token = self.tcp_token.text().strip()
            address = self.tcp_address.text().strip()
            public_key = self.ssh_public_key.text().strip()

            if not token or not address:
                raise ValueError("Authentication token and TCP address are required.")

            self.config.agent.token = token
            self.config.agent.address = address
            self.config.server.public_key = public_key

        elif step_index == 1:

            username = self.rdp_username.text().strip()
            password = self.rdp_password.text().strip()

            if not username or not password:
                raise ValueError("Username and password are required.")

            self.config.server.username = username
            self.config.rdp.username = username
            self.config.rdp.password = password

    def show_step(self, step_index: int) -> None:
        self.steps.setCurrentIndex(step_index)
        if step_index == 2:
            self.start_installation()

    def create_step1(self) -> QWidget:

        step = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Step 1: Enter TCP Address Information"))
        layout.addWidget(self.tcp_address)
        self.tcp_address.setPlaceholderText("Enter TCP address")
        layout.addWidget(self.tcp_token)
        self.tcp_token.setPlaceholderText("Enter authentication token")
        layout.addWidget(self.ssh_public_key)
        self.ssh_public_key.setPlaceholderText("Paste public key")
        layout.addWidget(QPushButton("Next", clicked=self.validate_and_next))
        step.setLayout(layout)
        return step

    def create_step2(self) -> QWidget:

        step = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Step 2: Enter Client Credentials"))
        layout.addWidget(QLabel("Note: The credentials entered here are stored securely as Windows credentials on this machine and are not transmitted externally.", wordWrap=True))

        layout.addWidget(self.rdp_username)
        self.rdp_username.setPlaceholderText("Enter username")

        layout.addWidget(self.rdp_password)
        self.rdp_password.setPlaceholderText("Enter password")
        self.rdp_password.setEchoMode(QLineEdit.Password)

        layout.addWidget(QPushButton("Install", clicked=self.validate_and_next))
        step.setLayout(layout)

        return step

    def create_step3(self):

        step = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Installation Progress"))

        self.finish_button = QPushButton("Finish Installation", clicked=self.finish_installation)
        self.finish_button.setEnabled(False)  # Disable until installation is complete

        layout.addWidget(self.finish_button)
        step.setLayout(layout)

        return step

    def start_installation(self) -> None:

        self.log_output.append("Starting installation...")

        self.worker = InstallationWorker(
            config=self.config,
            logger=self.logger,
            install_function=self.install_function
        )

        self.worker.finished.connect(self.on_installation_finished)
        self.worker.start()

    def on_installation_finished(self, message: str, success: bool):

        self.logger.log(message)

        if success:
            self.finish_button.setEnabled(True)

    def finish_installation(self):
        self.close()

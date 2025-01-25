import sys
from gui.gui import QApplication, MultiStepInstaller, GUILogger
from .models import InstallationConfig
from typing import Callable


class BaseInstaller:

    def __init__(self):
        pass

    @staticmethod
    def start(
        install_function: Callable[[
            InstallationConfig,
            GUILogger
        ], None]
    ):

        app = QApplication(sys.argv)
        installer = MultiStepInstaller(install_function=install_function)

        installer.show()
        sys.exit(app.exec())

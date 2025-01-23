import sys
from gui.gui import QApplication, MultiStepInstaller
from .models import InstallationConfig
from typing import Callable


class BaseInstaller:

    def __init__(self):
        pass

    @staticmethod
    def start(install_function: Callable[[InstallationConfig], None]):

        app = QApplication(sys.argv)
        installer = MultiStepInstaller(install_function=install_function)

        installer.show()
        sys.exit(app.exec())

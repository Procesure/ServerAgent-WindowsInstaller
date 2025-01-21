import sys
from typing import Union
from gui import QApplication, MultiStepInstaller

from managers.open_ssh.manager import WinServer2016OpenSSHManager
from managers.procesure.manager import ProcesureManager
from managers.rdp.manager import RDPManager
from .models import InstallationConfig
from typing import Callable


class BaseInstaller:

    def __init__(self):

        self.config: Union[InstallationConfig, None] = None
        self.ssh_manager: Union[WinServer2016OpenSSHManager, None] = None
        self.procesure_manager: Union[ProcesureManager, None] = None
        self.rdp_manager: Union[RDPManager, None] = None

    @staticmethod
    def start(install_function: Callable[[InstallationConfig], None]):

        app = QApplication(sys.argv)
        installer = MultiStepInstaller(install_function=install_function)

        installer.show()
        sys.exit(app.exec())

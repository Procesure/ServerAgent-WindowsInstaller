from typing import Union, Callable
from managers.open_ssh.manager import WinServer2016OpenSSHManager
from managers.procesure.manager import ProcesureManager
from managers.rdp.manager import RDPManager
from .base_installer import BaseInstaller
from .models import *


class WinServer2016Installer(BaseInstaller):


    def __init__(self):
        super().__init__()

    @staticmethod
    def handle_installations(config: InstallationConfig):

        installation_classes = [
            WinServer2016OpenSSHManager(config=config.ssh),
            ProcesureManager(config=config.tcp),
            RDPManager(config=config.rdp)
        ]

        for installation_class in installation_classes:
            installation_class.handle_installation()
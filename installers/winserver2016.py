from managers.server.manager import WinServer2016ServerManager
from managers.agent.manager import AgentManager
from managers.rdp.manager import RDPManager
from installers.base_installer import BaseInstaller
from .models import *
from gui.logger import GUILogger
from managers.service.manager import ServiceManager


class WinServer2016Installer(BaseInstaller):

    def __init__(self):
        super().__init__()

    @staticmethod
    def handle_installations(
        config: InstallationConfig,
        logger: GUILogger
    ):

        installation_classes = [
            WinServer2016ServerManager(config.server, logger),
            AgentManager(config.agent, logger),
            RDPManager(config.rdp, logger)
        ]

        for installation_class in installation_classes:
            installation_class.handle_installation()

        svc_manager = ServiceManager(logger)
        svc_manager.to_exe()
        svc_manager.install_service()
        svc_manager.start_service()


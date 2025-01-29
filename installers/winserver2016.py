from managers.server.manager import WinServer2016ServerManager
from managers.agent.manager import AgentManager
from managers.rdp.manager import RDPManager
from installers.base_installer import BaseInstaller
from .models import *
from managers.service.manager import ServiceManager
from gui.logger import gui_logger


class WinServer2016Installer(BaseInstaller):

    def __init__(self):
        super().__init__()

    @staticmethod
    def handle_installations(
        config: InstallationConfig
    ):

        installation_classes = [
            WinServer2016ServerManager(config.server),
            AgentManager(config.agent),
            RDPManager(config.rdp)
        ]

        for installation_class in installation_classes:

            gui_logger.log(message="\n\n\n\n")
            gui_logger.log(message=f"{installation_class.class_name_intro}")
            gui_logger.log(message="\n\n\n\n")
            installation_class.handle_installation()

        svc_manager = ServiceManager()
        svc_manager.to_exe()
        svc_manager.uninstall_service()
        svc_manager.install_service()
        svc_manager.start_service()


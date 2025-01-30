from managers.server.manager import WinServer2016ServerManager, gui_logger
from managers.service.manager import ServiceManager
from managers.agent.manager import AgentManager
from managers.rdp.manager import RDPManager
from managers.task.manager import TaskManager
from installers.base_installer import BaseInstaller
from .models import *


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
            RDPManager(config.rdp),
            TaskManager()
        ]

        for installation_class in installation_classes:

            gui_logger.log(message="\n\n\n\n")
            gui_logger.log(message=f"{installation_class.class_name_intro}")
            gui_logger.log(message="\n\n\n\n")
            installation_class.handle_installation()

        svc_manager = ServiceManager()
        svc_manager.to_exe()

        try:
            svc_manager.uninstall_service()
        except BaseException as e:
            gui_logger.log(str(e))

        try:
            svc_manager.install_service()
        except BaseException as e:
            gui_logger.log(str(e))

        svc_manager.start_service()


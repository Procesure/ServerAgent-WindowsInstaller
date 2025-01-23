import os

from dotenv import load_dotenv

from installers.winserver2016 import WinServer2016Installer
from managers.server.manager import WinServer2016ServerManager, ServerConfig
from managers.service.manager import ServiceManager
from managers.agent.manager import AgentManager, AgentConfig
from managers.rdp.manager import RDPManager, RDPConfig

load_dotenv()

if __name__ == "__main__":

    # installer = WinServer2016Installer()
    # installer.start(installer.handle_installations)

    # server_config = ServerConfig(
    #     username=os.getenv("SERVER_USERNAME"),
    #     public_key=os.getenv("SERVER_PUBLIC_KEY")
    # )
    #
    # ssh_manager = WinServer2016ServerManager(server_config)
    # ssh_manager.handle_installation()

    server_agent_config = AgentConfig(
        address=os.getenv("AGENT_ADDRESS"),
        token=os.getenv("AGENT_TOKEN")
    )
    #
    # agent_manager = AgentManager(server_agent_config)
    # agent_manager.handle_installation()

    # ServiceManager.to_exe()

    rdp_config = RDPConfig(
        username=os.getenv("RDP_USERNAME"),
        password=os.getenv("RDP_PASSWORD")
    )

    rdp_manager = RDPManager(rdp_config)
    rdp_manager.handle_installation()
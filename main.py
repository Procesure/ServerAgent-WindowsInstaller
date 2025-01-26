import os

from dotenv import load_dotenv

from installers.winserver2016 import WinServer2016Installer
from managers.server.manager import WinServer2016ServerManager, ServerConfig
from managers.service.manager import ServiceManager
from managers.agent.manager import AgentManager, AgentConfig
from managers.rdp.manager import RDPManager, RDPConfig

load_dotenv()

if __name__ == "__main__":

    installer = WinServer2016Installer()
    installer.start(installer.handle_installations)

    # server_config = ServerConfig(
    #     username=os.getenv("SERVER_USERNAME"),
    #     public_key=os.getenv("SERVER_PUBLIC_KEY")
    # )
    #
    # agent_config = AgentConfig(
    #     address=os.getenv("AGENT_ADDRESS"),
    #     token=os.getenv("AGENT_TOKEN")
    # )
    #
    # rdp_config = RDPConfig(
    #     username=os.getenv("RDP_USERNAME"),
    #     password=os.getenv("RDP_PASSWORD")
    # )

    #server_manager = WinServer2016ServerManager(server_config)
    #agent_manager = AgentManager(agent_config)
    # rdp_manager = RDPManager(rdp_config)

    #server_manager.handle_installation()
    # rdp_manager.handle_installation()
    #agent_manager.handle_installation()


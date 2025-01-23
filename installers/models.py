from pathlib import Path
from pydantic import BaseModel, Field
from managers.server.models import ServerConfig
from managers.agent.models import AgentConfig
from managers.rdp.models import RDPConfig


class InstallationConfig(BaseModel):

    installation_root_dir: Path = Field(default=Path("C:/Program Files/Procesure"), description="Path to install the program")
    server: ServerConfig = Field(default=ServerConfig(public_key="", username=""))
    agent: AgentConfig = Field(default=AgentConfig(address="", token=""))
    rdp: RDPConfig = Field(default=RDPConfig(username="", password=""))
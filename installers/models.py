from pathlib import Path
from pydantic import BaseModel, StrictStr, Field, field_validator
from managers.open_ssh.models import SSHConfig
from managers.procesure.models import TCPConfig
from managers.rdp.models import RDPConfig


class InstallationConfig(BaseModel):

    installation_root_dir: Path = Field(default=Path("C:/Program Files/Procesure"), description="Path to install the program")
    tcp: TCPConfig = Field(default=TCPConfig(address="", token=""))
    ssh: SSHConfig = Field(default=SSHConfig())
    rdp: RDPConfig = Field(default=RDPConfig(username="", password=""))
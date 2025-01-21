from pathlib import Path
from pydantic import BaseModel, StrictStr, Field
from typing import Union


class SSHConfig(BaseModel):

    open_ssh_installation_path: Path = Field(default=Path("C:\Program Files"), description="Path to install OpenSSH binaries")
    public_key: Union[StrictStr, None] = Field(default=None, description="Public key to add for SSH authentication")
    username: Union[StrictStr, None] = Field(default=None, description="The username associated with the public key and login")
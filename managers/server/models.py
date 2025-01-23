from pydantic import BaseModel, StrictStr, Field
from typing import Union


class ServerConfig(BaseModel):

    public_key: Union[StrictStr, None] = Field(default=None, description="Public key to add for SSH authentication")
    username: Union[StrictStr, None] = Field(default=None, description="The username associated with the public key and login")
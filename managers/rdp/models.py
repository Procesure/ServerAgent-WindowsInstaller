from pydantic import BaseModel, StrictStr, Field


class RDPConfig(BaseModel):

    username: StrictStr = Field(description="Username for client credentials")
    password: StrictStr = Field(description="Password for client credentials")

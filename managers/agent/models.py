import re
from pydantic import BaseModel, StrictStr, Field, field_validator


class AgentConfig(BaseModel):

    address: StrictStr = Field(description="The TCP address in the format 'hostname:port', e.g., '123.io.agent:23090'")
    token: StrictStr = Field(description="The token that allows connection to the address.")

    @classmethod
    @field_validator('address')
    def validate_address(cls, value: str) -> str:
        pattern = r'^(?P<host>[\w.-]+):(?P<port>\d+)$'
        match = re.match(pattern, value)
        if not match:
            raise ValueError("Address must be in the format 'hostname:port', e.g., '123.io.agent:23090'")

        port = int(match.group('port'))
        if not (1 <= port <= 65535):
            raise ValueError("Port must be between 1 and 65535")

        return value

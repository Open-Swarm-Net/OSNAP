from pydantic import BaseModel
from typing import Union, UUID


class AgentInfo(BaseModel):
    """
    The response from an agent's info method.
    """

    name: str
    description: str
    id: Union[int, str, UUID, None] = None
    tools: list = []
    url: str = None

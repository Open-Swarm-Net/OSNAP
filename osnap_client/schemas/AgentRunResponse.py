from enum import Enum
from pydantic import BaseModel

class AgentRunResponseStatus(str, Enum):
    STARTING = "starting"
    WORKING = "working"
    ERROR = "error"

class AgentRunResponse(BaseModel):
    """
    The response from an agent's run method.
    """

    status: AgentRunResponseStatus
    message: str
    payload: dict
import enum
from pydantic import BaseModel

class Scope(int, enum.Enum):
    PUBLIC = 0
    PRIVATE = 1

class SwarmAgentInfo(BaseModel):
    """
    Information about a swarm agent.
    """
    id: int
    name: str
    description: str
    endpoints: list = []
    scope: Scope = Scope.PUBLIC
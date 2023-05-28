from pydantic import BaseModel

class SwarmJoinResponse(BaseModel):
    """
    The response to a join request.
    """
    accepted: bool
    swarm_manager_id: str
    message: str
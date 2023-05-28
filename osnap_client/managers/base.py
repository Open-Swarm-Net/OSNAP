from pydantic import BaseModel
from abc import abstractmethod, ABC

class SwarmConnection: 
    pass

class SwarmJoinResponse(BaseModel):
    """
    The response to a join request.
    """
    accepted: bool
    swarm_manager_id: str
    message: str

class SwarmManagerBase(ABC): 
    """
    The base class for all swarm managers.
    """

    @abstractmethod
    def info(self):
        """
        Return information about the swarm manager
        """

    @abstractmethod
    def join_swarm() -> SwarmJoinResponse:
        """
        Make a request to join with an upstream or peer
        swarm mangager.

        The upstream swarm sends a response accepting
        or rejecting the join request
        """
        

    # @abstractmethod
    # def leave_swarm_manager(self, swarm_manager_id: str):
    #     pass

    # @abstractmethod
    # def send_message(self, recipient_id: str, message: dict):
    #     pass

    # @abstractmethod
    # def receive_message(self, sender_id: str, message: dict):
    #     pass
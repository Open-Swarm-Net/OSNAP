from abc import ABC, abstractmethod
from osnap_client.agents import SwarmAgentBase

class SwarmAdapterBase(ABC):
    """In the current implementation the adapter is basically a request factory and response handler.    
    """
    @abstractmethod
    def join_swarm(self, agent: SwarmAgentBase):
        raise NotImplementedError

    @abstractmethod
    def leave_swarm(self, agent: SwarmAgentBase):
        raise NotImplementedError

    @abstractmethod
    def get_info(self):
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} swarm_host={self.swarm_host}>"

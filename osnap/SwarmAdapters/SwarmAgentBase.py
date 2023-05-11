# SwarmAgentBase.py
from abc import ABC, abstractmethod

class SwarmAgentBase(ABC):
    """
    This is a base class that the user needs to implement to define the logic of the bot
    for request handling and sending.
    """
    @property
    @abstractmethod
    def name(self):
        raise NotImplementedError

    @abstractmethod
    async def on_receive(self, message: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def on_ready(self):
        raise NotImplementedError

    @staticmethod
    def command(func):
        func.is_command = True
        return func

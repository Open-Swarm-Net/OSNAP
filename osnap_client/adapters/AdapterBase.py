from abc import ABC, abstractmethod
import asyncio
import functools
from osnap.SwarmAdapters.QueueTaskStruct import QueueTaskStruct

class AdapterBase(ABC):
    """This class stores some basic properties that every adapter should implement.
    """

    def __init__(self) -> None:
        self.event_queue = asyncio.Queue()

    # @staticmethod
    # def add_to_queue(func):
    #     @functools.wraps(func)
    #     async def wrapper(self, *args, **kwargs):
    #         result = await func(self, *args, **kwargs)
    #         if not isinstance(result, QueueTaskStruct):
    #             raise TypeError(f"Expected a QueueTaskStruct to add to the event_queue, got {type(result)}")
    #         await self.event_queue.put(result)
    #     return wrapper

    async def add_to_queue(self, task):
        if not isinstance(task, QueueTaskStruct):
            raise TypeError(f"Expected a QueueTaskStruct to add to the event_queue, got {type(task)}")
        await self.event_queue.put(task)
        print(f"Added {task} to the event_queue")

    @abstractmethod
    async def on_ready(self) -> QueueTaskStruct:
        """This method is called when the apter is loaded.
        The output is forwarded to the agent through the event queue.
        """
        raise NotImplementedError
    
    @abstractmethod
    async def on_message(self, message: str) -> QueueTaskStruct:
        """This method is called when the apter is loaded
        """
        raise NotImplementedError

    @abstractmethod
    async def get_users(self):
        """Returns the information about the users on the server
        """
        raise NotImplementedError
    
    @abstractmethod
    async def send_message(self, message: str, target_channel: str):
        """This method is called to send a message to a specific channel
        """
        raise NotImplementedError
    
    @abstractmethod
    async def send_dm(self, message: str, target_user: str):
        """This method is called to send a message to a specific user
        """
        raise NotImplementedError
    
    @abstractmethod
    async def start():
        """This method is called to start the adapter
        """
        raise NotImplementedError
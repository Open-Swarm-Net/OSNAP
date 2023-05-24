from abc import ABC, abstractmethod
import asyncio
import logging
from osnap_client.protocol import AgentCommand

# Create a handler that puts messages into the queue
class QueueHandler(logging.Handler):
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        log_entry = self.format(record)
        self.log_queue.put_nowait(log_entry)

class AdapterBase(ABC):
    """This class stores some basic properties that every adapter should implement.
    """

    def __init__(self) -> None:
        self.event_queue = asyncio.Queue()
        
        self.log_queue = asyncio.Queue()
        self.log_queue_handler = QueueHandler(self.log_queue)
        self.log_queue_handler.setLevel(logging.INFO)

    async def add_to_queue(self, task):
        if not isinstance(task, AgentCommand):
            raise TypeError(f"Expected a AgentCommand to add to the event_queue, got {type(task)}")
        await self.event_queue.put(task)
        print(f"Added {task} to the event_queue")

    @abstractmethod
    async def on_ready(self) -> AgentCommand:
        """This method is called when the apter is loaded.
        The output is forwarded to the agent through the event queue.
        """
        raise NotImplementedError
    
    @abstractmethod
    async def on_message(self, message: str) -> AgentCommand:
        """This method is called when the adapter receives a message
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
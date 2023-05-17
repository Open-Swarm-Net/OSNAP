from abc import ABC, abstractmethod
import asyncio
import time
import threading

from osnap.SwarmAdapters.AdapterBase import AdapterBase
from osnap.SwarmAdapters.QueueTaskStruct import QueueTaskStruct

class SwarmAgentBase(ABC):
    """
    This is a base class that the user needs to implement to define the logic of the bot
    for request handling and sending.
    """
    def __init__(self, name: str, description: str, swarm_adapter: AdapterBase) -> None:
        super().__init__()
        self.name = name
        self.description = description
        self.swarm_adapter = swarm_adapter
        self.event_queue = swarm_adapter.event_queue
        self.command_map = {}

        # Register "ready" command
        self.command_map["on_ready"] = self.on_ready
    
    def command(self, name: str):
        def decorator(func):
            self.command_map[name] = func
            return func
        return decorator
    
    async def on_callback_event_listener(self):
        while True:
            task = None
            try:
                task = self.event_queue.get_nowait()
            except asyncio.QueueEmpty:
                time.sleep(0.5)
                continue
            if not isinstance(task, QueueTaskStruct):
                raise TypeError(f"Expected a QueueTaskStruct, got {type(task)}")
            
            command = task.command_type
            data = task.data

            if command in self.command_map:
                # check if the adapter loop is running
                if not self.swarm_adapter.adapter_loop.is_running():
                    print("Adapter loop is not running, starting it now")
                    try:
                        self.start_adapter()
                    except Exception as e:
                        print(f"Error starting adapter: {e}")
                    if not self.swarm_adapter.adapter_loop.is_running():
                        raise Exception("Adapter loop is still not running after starting it")
                
                try:
                    asyncio.run_coroutine_threadsafe(self.command_map[command](data), self.swarm_adapter.adapter_loop)
                except Exception as e:
                    print(f"Error in {command} command: {e}")
            else:
                print(f"Unknown command: {command}")

    def start_adapter(self):
        adapter_thread = threading.Thread(target=self.swarm_adapter.start)
        adapter_thread.start()

    async def on_ready(self, data: str):
        """This method is called when the apter is loaded."""
        self_description = f"Hi everyone!\nName: {self.name}\nDescription: {self.description}"
        await self.swarm_adapter.send_message(self_description, "intros")

    def run(self):
        """This method is called to start the bot
        
        Clarification on the event loops. Bear with me here =)
        Ideally we'd like the adapter and the agent to run in the same event loop,
        but both the discord process and the adent process are blocking the event loop.

        So we need to split the process into two event loops, one for the agent and one for the adapter.

        However, now we cannot await the adapter methods from the agent, because they are running in different event loops.
        Therefore in the agent we need to use the run_coroutine_threadsafe method to run the adapter methods in the adapter event loop.
        """       
        # run the adapter in a separate thread
        self.start_adapter()

        # run the event listener in the main thread
        agent_loop = asyncio.get_event_loop()
        agent_loop.run_until_complete(self.on_callback_event_listener())

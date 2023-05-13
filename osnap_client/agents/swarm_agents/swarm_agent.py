from abc import ABC, abstractmethod
import asyncio
import time
import threading

from osnap_client.SwarmAdapters.AdapterBase import AdapterBase
from osnap_client.SwarmAdapters.QueueTaskStruct import QueueTaskStruct


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
                try:
                    await self.command_map[command](data)
                except Exception as e:
                    print(f"Error in {command} command: {e}")
            else:
                print(f"Unknown command: {command}")

    async def on_ready(self, data: str):
        """This method is called when the apter is loaded."""
        self_description = (
            f"Hi everyone!\nName: {self.name}\nDescription: {self.description}"
        )
        await self.swarm_adapter.send_message(self_description, "intros")

    async def run(self):
        """This method is called to start the bot"""
        # # order matters!
        # # TODO: figure out why order matters
        # await asyncio.gather(
        #     self.swarm_adapter.start(),
        #     self.on_callback_event_listener()
        # )

        # run the adapter in a separate thread
        adapter_thread = threading.Thread(target=self.swarm_adapter.start)
        adapter_thread.start()

        # run the event listener in the main thread
        await self.on_callback_event_listener()

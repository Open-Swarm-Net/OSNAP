from abc import ABC, abstractmethod
import asyncio
import time
import threading

from osnap_client.adapters.AdapterBase import AdapterBase
from osnap_client.protocol import AgentCommand, AgentCommandType, TaskMap, Task

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
        self.task_map = TaskMap()

        # Register "ready" command
        self.command_map["on_ready"] = self.on_ready
    
    def command(self, name: str):
        def decorator(func):
            self.command_map[name] = func
            return func
        return decorator
    
    async def on_callback_event_listener(self):
        while True:
            
            try:
                message = self.swarm_adapter.log_queue.get_nowait()
                print(message)
            except asyncio.QueueEmpty:
                pass
            command_obj = None
            try:
                command_obj = self.event_queue.get_nowait()
            except asyncio.QueueEmpty:
                time.sleep(0.5)
                continue
            if not isinstance(command_obj, AgentCommand):
                raise TypeError(f"Expected a AgentCommand, got {type(command_obj)}")
            
            task_name = command_obj.task_type

            if task_name in self.command_map:
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
                    asyncio.run_coroutine_threadsafe(self.command_map[task_name](command_obj), self.swarm_adapter.adapter_loop)
                except Exception as e:
                    print(f"Error in {task_name} command: {e}")
                    response = AgentCommand(
                        sender=self.name,
                        receiver="agent",
                        command_type=AgentCommandType.ERROR,
                        task_type=task_name,
                        payload_type = 'str',
                        payload=f"505: Internal Server Error: {e}",
                    )
                    await self.swarm_adapter.send_dm(response, message.sender)
            else:
                pass

    def start_adapter(self):
        adapter_thread = threading.Thread(target=self.swarm_adapter.start)
        adapter_thread.start()

    async def on_ready(self, data: str):
        """This method is called when the apter is loaded."""
        available_commands = [command for command in self.command_map.keys() if command != "on_ready"]
        self_description = AgentCommand(
            sender=self.name,
            receiver="swarm",
            command_type=AgentCommandType.REGISTER,
            task_type="register",
            payload_type = 'dict',
            payload={
                "description": self.description,
                "available_commands": available_commands
            }
        )
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
        try:
            agent_loop.run_until_complete(self.on_callback_event_listener())
        except KeyboardInterrupt:
            print("Exiting...")
            agent_loop.close()
            self.swarm_adapter.stop()
            exit(0)

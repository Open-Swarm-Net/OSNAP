from abc import ABC, abstractmethod

class BaseSwarmAdapter(ABC):
    """This is a base class for the Swarm Adapters.
    The responsibilities of the swarm adapters are to handle networking part of the swarm communication:
    * discover agents and tools
    * catch incoming requests
    * route requests to the appropriate request handler
    * send responses

    Swarm architectures can vary, but the main functionalities are:
    * one to one communication
    * one to many communication
    * many to one communication

    Configurations of the adapters can vary a lot, so the class is very abstract.

    Theoretically, if you are brave, you can run multiple adapters simultaneously like this:
    async def main():
        TOKEN_bot2 = "abc"
        server_name = 'swarm1_test'
        channel_name = 'general'
        matrix_server_token = "xyz"

        discord_adapter = DiscordAdapter(TOKEN_bot2, server_name, channel_name)
        matrix_adapter = MatrixAdapter(matrix_server_token, server_name, channel_name)

        # Create tasks for both servers
        discord_task = asyncio.create_task(discord_adapter.run())
        matrix_task = asyncio.create_task(matrix_adapter.run())

        # Run both tasks concurrently
        await asyncio.gather(discord_task, matrix_task)
    """

    def __init__(self, adapter_config):
        self.adapter_config = adapter_config
        self.client_process = None
        self.is_running = False

    @abstractmethod
    def run(self):
        """This method is responsible for running the adapter.
        The actual run method is adapter specific, can be client.run, server.run, client.start, etc.
        This method is responsible for launching this specific method implementation in a separate process.
        """
        raise NotImplementedError

    @abstractmethod
    async def on_message(self, message):
        """Called when a new message is received."""
        raise NotImplementedError
    
    @abstractmethod
    async def on_ready(self):
        """Called when the server is ready."""
        raise NotImplementedError

    # @abstractmethod
    # def discover_agents(self):
    #     raise NotImplementedError
    
    # @abstractmethod
    # async def on_error(self, error):
    #     """Called when an error occurs."""
    #     raise NotImplementedError
    
    # @abstractmethod
    # async def send_message(self, message):
    #     """Send a message to the server."""
    #     raise NotImplementedError
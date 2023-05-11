# user_logic.py
from osnap.SwarmAdapters.SwarmAgentBase import SwarmAgentBase
from osnap.SwarmAdapters.AdapterBase import AdapterBase

class ExampleSwarmAgent(SwarmAgentBase):
    def __init__(self, command_prefix='$'):
        self.command_prefix = command_prefix

    @property
    def name(self):
        return 'Example Swarm Agent'

    async def on_ready(self):
        print(f'We have logged in as {self.name}')

    async def on_receive(self, adapter: AdapterBase, message: str) -> str:
        if message.startswith(f'{self.command_prefix}hello'):
            return self.introduce_yourself()

        if message.startswith(f'{self.command_prefix}list'):
            response = await self.find_users_on_server(adapter)
            return response

    def introduce_yourself(self):
        return f'Hello!, my name is {self.name}'

    async def find_users_on_server(self, adapter: AdapterBase) -> str:
        users = await adapter.users
        return f'Users on server:\n{users}'

    # TODO: examine if commands.Bot is better
    # @SwarmAgentBase.command
    # async def list(self, ctx, message):
    #     await ctx.send(f"List command received with argument: {message}")

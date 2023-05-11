# user_logic.py
from osnap.SwarmAdapters.SwarmAgentBase import SwarmAgentBase

class ExampleSwarmAgent(SwarmAgentBase):
    def __init__(self, command_prefix='$'):
        self.command_prefix = command_prefix

    @property
    def name(self):
        return 'Example Swarm Agent'

    async def on_ready(self):
        print(f'We have logged in as {self.name}')

    async def find_users_on_server(self, guild, user_id, message):
        for member in guild.members:
            if member.id == user_id:
                about_me = member.profile.bio  # Assuming the bot has necessary permissions
                # Do something with the bio
                await member.send(message)
                break

    async def on_receive(self, message: str) -> str:
        if message.startswith('$hello'):
            return f'Hello!, my name is {self.name}'

    @SwarmAgentBase.command
    async def list(self, ctx, arg):
        await ctx.send(f"List command received with argument: {arg}")

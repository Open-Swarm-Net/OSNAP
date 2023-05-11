# discord_adapter.py
import discord
import inspect
from osnap.SwarmAdapters.SwarmAgentBase import SwarmAgentBase

class DiscordAdapter(discord.Client):
    """This is an adapter that allows the agent to communicate with Discord and receive/send messages.

    Args:
    - agent_logic (SwarmAgentBase): The logic of the bot that the user needs to implement.
    - intents_list (list[str]): A list of intents that the bot will listen to.
    - token (str): The token of the bot that is used to connect to Discord.
    """
    
    def __init__(self, agent_logic: SwarmAgentBase, start_server: str, intents_list: list, token: str):

        if not isinstance(agent_logic, SwarmAgentBase):
            raise TypeError(f'Expected type {SwarmAgentBase}, got {type(agent_logic)}')
        intents = self._unpack_intents(intents_list)

        super().__init__(intents=intents)
        self.agent_logic = agent_logic
        self.token = token
        self.start_server = start_server

    def _unpack_intents(self, intents_list: list) -> discord.Intents:
        intents_obj = discord.Intents.default()
        for intent in intents_list:
            # check if the intent is a vaild attribute of discord.Intents
            if hasattr(intents_obj, intent):
                setattr(intents_obj, intent, True)
            else:
                raise ValueError(f"Invalid intent: {intent}")
        return intents_obj

    async def on_ready(self):
        reponse = await self.agent_logic.on_ready()

        target_guild_name = self.start_server
        target_channel_name = 'intros' 

        # Find the guild by its name
        target_guild = None
        for guild in self.guilds:
            if guild.name == target_guild_name:
                target_guild = guild
                break

        if target_guild is None:
            print(f"Guild '{target_guild_name}' not found.")
            raise ValueError(f"Guild '{target_guild_name}' not found.")
            
        # Find the channel by its name
        target_channel = None
        for channel in target_guild.channels:
            if channel.name == target_channel_name and isinstance(channel, discord.TextChannel):
                target_channel = channel
                break
        
        if target_channel is None:
            print(f"Channel '{target_channel_name}' not found. Setting to 'general'.")
            target_channel = target_guild.text_channels[0]

        if reponse is None:
            reponse = f"Hi, my name is {self.agent_logic.name}."
            
        await target_channel.send(reponse)


    async def on_message(self, message):
        if message.author == self.user:
            return
        response = await self.agent_logic.on_receive(message.content)

        if response:
            await message.reply(response)

    def format_response(self, response: str) -> str:
        # Enforce the desired output format, e.g., add a prefix to the message
        formatted_response = f"[Your Bot] {response}"
        return formatted_response

    def run(self):
        super().run(self.token)

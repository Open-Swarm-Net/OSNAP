# discord_adapter.py
import discord
from abc import ABCMeta
from osnap.SwarmAdapters import AdapterBase
from osnap.SwarmAdapters.QueueTaskStruct import QueueTaskStruct

class DiscordAdapter(AdapterBase, discord.Client):
    """This is an adapter that allows the agent to communicate with Discord and receive/send messages.

    Args:
    - intents_list (list[str]): A list of intents that the bot will listen to.
    - token (str): The token of the bot that is used to connect to Discord.
    """
    
    def __init__(self, start_server: str, intents_list: list, token: str):
        intents = self._unpack_intents(intents_list)

        super().__init__(intents=intents)
        self.token = token
        self.start_server = start_server
        self.guild = self._get_start_guild()

    async def on_ready(self):
        """This method is called automatically by the discord library when the bot is ready to start working.
        the QueueTaskStruct is added to the queue automatically on return.
        """
        reponse = QueueTaskStruct(command_type='on_ready', data='')
        return reponse

    async def on_message(self, message):
        """This method is called automatically by the discord library when a message is received.
        the QueueTaskStruct is added to the queue automatically on return.
        """
        if message.author == self.user:
            return
        
        message_content = message.content
        
        if message.content.startswith('$'):
            command_name = message_content.split(' ')[0][1:]
            command_data = ' '.join(message_content.split(' ')[1:])
            response = QueueTaskStruct(command_type=command_name, data=command_data)
            return response

    async def get_users(self):
        """Returns the information about the users on the server
        # About me is not available in the API: https://stackoverflow.com/questions/68654914/discord-py-get-user-about-me-section
        """
        users = []
        users_iterator = self.guilds[0].fetch_members()
        async for user in users_iterator:
            users.append(user.name)
        return users

    async def send_message(self, message: str, target_channel="general"):
        """Sends a message to the specified channel"""

        # Find the channel by its name
        for channel in self.guild.channels:
            if channel.name == target_channel and isinstance(channel, discord.TextChannel):
                await channel.send(message)

        raise ValueError(f"Could not find the channel {target_channel} in the list of channels: {self.guild.channels}.")
    
    async def send_dm(self, message: str, target_user: str):
        """Sends a direct message to the specified user"""
        for user in self.guild.members:
            if user.name == target_user:
                await user.send(message)
        
        raise ValueError(f"Could not find the user {target_user} in the list of users: {self.guild.members}.")

    def run(self):
        super().run(self.token)


    def _unpack_intents(self, intents_list: list) -> discord.Intents:
        intents_obj = discord.Intents.default()
        for intent in intents_list:
            # check if the intent is a vaild attribute of discord.Intents
            if hasattr(intents_obj, intent):
                setattr(intents_obj, intent, True)
            else:
                raise ValueError(f"Invalid intent: {intent}")
        return intents_obj

    def _get_start_guild(self):
        """In discord api the servers are called guilds.
        """
        target_guild_name = self.start_server

        # Find the guild by its name
        target_guild = None
        for guild in self.guilds:
            if guild.name == target_guild_name:
                target_guild = guild
                return target_guild
        
        raise ValueError(f"Could not find the guild {target_guild_name} in the list of guilds: {self.guilds}. Make sure the bot is added to the server: https://discordpy.readthedocs.io/en/stable/discord.html")
        
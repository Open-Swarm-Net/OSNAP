# discord_adapter.py
import logging
import discord
from io import BytesIO
from osnap_client.adapters.AdapterBase import AdapterBase
from osnap_client.protocol import AgentCommand, AgentCommandType
import asyncio

class DiscordAdapter(AdapterBase):
    """This is an adapter that allows the agent to communicate with Discord and receive/send messages.

    Args:
    - intents_list (list[str]): A list of intents that the bot will listen to.
    - token (str): The token of the bot that is used to connect to Discord.
    """
    
    def __init__(self, start_server: str, intents_list: list, token: str):
        super().__init__()
        intents = self._unpack_intents(intents_list)

        self.adapter_loop = asyncio.new_event_loop()
        self.client = discord.Client(loop=self.adapter_loop, intents=intents)
        self.token = token
        self.start_server_name = start_server
        self.guild = None

        # Set up an event handler for the log queue
        self.logger  = logging.getLogger('discord')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(self.log_queue_handler)

        # file handler
        log_file_name = "discord.log"
        open(log_file_name, 'w').close()
        file_handler = logging.FileHandler(filename=log_file_name, encoding='utf-8', mode='w')
        file_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)

    async def on_ready(self):
        """This method is called automatically by the discord library when the bot is ready to start working.
        """
        response = AgentCommand(
            sender='discord_adapter',
            receiver='agent',
            command_type=AgentCommandType.ON_READY,
            task_type = 'on_ready',
            payload="",
            payload_type = 'str'
        )
        await self.add_to_queue(response)

    async def on_message(self, message: discord.Message):
        """This method is called automatically by the discord library when a message is received.

        Args:
        - message (str): The message can be a normal message like "$hello xxx" or a jsonified AgentCommand object like {"sender": "agent", "receiver": "discord_adapter", "command": "request", "task_name": "hello", "data": "xxx"}
        """
        if message.author == self.client.user:
            return
        
        message_content = message.content
        sender = message.author.name
        
        if message.content.startswith('$'):
            command_name = message_content.split(' ')[0][1:]
            command_data = ' '.join(message_content.split(' ')[1:])
            message_obj = AgentCommand(
                sender=sender,
                receiver='agent',
                command_type=AgentCommandType.REQUEST,
                task_type = command_name,
                payload_type = 'str',
                payload=command_data
            )
            await self.add_to_queue(message_obj)
        elif message.content.startswith('{'):
            try:
                message_json = message_content
                message_obj = AgentCommand.parse_raw(message_json)
                message_obj.sender = sender
                await self.add_to_queue(message_obj)
            except Exception as e:
                print(f"Error parsing message: {e}")
                message = AgentCommand(
                    sender='discord_adapter',
                    receiver='agent',
                    command_type=AgentCommandType.ERROR,
                    task_type = 'fix',
                    payload_type = 'str',
                    payload=f"Failed to parse message {message.id}:\n {e}"
                )
                await message.reply(message.json())

    async def get_users(self):
        """Returns the information about the users on the server
        # About me is not available in the API: https://stackoverflow.com/questions/68654914/discord-py-get-user-about-me-section
        """
        users = []
        users_iterator = self.client.guilds[0].fetch_members()
        async for user in users_iterator:
            users.append(user.name)
        return users

    async def send_message(self, message: AgentCommand, target_channel="general", file: bytes = None):
        """Sends a message to the specified channel"""
        if self.guild is None:
            self.guild = self._get_start_guild()

        message_json = message.json()
        if file is not None:
            with BytesIO() as image_binary:
                image_binary.write(file)
                image_binary.seek(0)
                file = discord.File(image_binary, filename='image.png')

        # Find the channel by its name
        for channel in self.guild.channels:
            if channel.name == target_channel and isinstance(channel, discord.TextChannel):
                await channel.send(message_json)
                print(f"Sent message {message_json} to channel {target_channel}")
                return

        raise ValueError(f"Could not find the channel {target_channel} in the list of channels: {self.guild.channels}.")

    async def send_dm(self, message: AgentCommand, target_user: str, file: bytes = None):
        """Sends a direct message to the specified user"""
        if self.guild is None:
            self.guild = self._get_start_guild()

        message_json = message.json()
        if file is not None:
            with BytesIO() as image_binary:
                image_binary.write(file)
                image_binary.seek(0)
                file = discord.File(image_binary, filename='image.png')

        for user in self.guild.members:
            if user.name == target_user:
                await user.send(message_json, file=file)
        
        raise ValueError(f"Could not find the user {target_user} in the list of users: {self.guild.members}.")

    def start(self):
        # adding the methods to the adapter
        self.client.event(self.on_ready)
        self.client.event(self.on_message)
        # need to launch the adapter loop
        self.adapter_loop.run_until_complete(self.client.start(self.token))

    def stop(self):
        #self.adapter_loop.create_task(self.client.close())
        tasks = asyncio.all_tasks(loop=self.adapter_loop)
        for task in tasks:
            task.cancel()
        self.adapter_loop.close()

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
        # Find the guild by its name
        target_guild = None
        for guild in self.client.guilds:
            if guild.name == self.start_server_name:
                target_guild = guild
                return target_guild
        
        raise ValueError(f"Could not find the guild {self.start_server_name} in the list of guilds: {self.client.guilds}. Make sure the bot is added to the server: https://discordpy.readthedocs.io/en/stable/discord.html")
        
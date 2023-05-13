import sys, os

sys.path.append(os.path.abspath(os.path.join("../..")))

import discord
import asyncio
import json
import time
from jsonschema import validate

from osnap_client.SwarmAdapters.BaseSwarmAdapter import BaseSwarmAdapter


class DiscordSwarmAdapter(BaseSwarmAdapter):
    """And implementation of the Swarm Adapter for Discord.

    Args:
        - config (dict): The configuration of the adapter.
    """

    def __init__(self, config: dict):
        super().__init__(config)
        self.configure(config)

    def configure(self, config: dict):
        """Configure the adapter.

        Args:
            - config (dict): The configuration of the adapter.
            {
                "bot_token": "your_token",
                "server": "your_prefix",
                "entry_channel": "your_entry_channel"
                "intents": []
            }
        """
        config_schema = {
            "type": "object",
            "properties": {
                "bot_token": {"type": "string"},
                "server": {"type": "string"},
                "entry_channel": {"type": "string"},
                "intents": {"type": "array"},
            },
            "required": ["bot_token", "server", "entry_channel"],
        }
        validate(instance=config, schema=config_schema)

        self.config = config
        self.bot_token = config["bot_token"]

        # intents: https://discordpy.readthedocs.io/en/stable/intents.html
        self.intents = discord.Intents.default()
        for intent in config["intents"]:
            # check if the intent is a vaild attribute of discord.Intents
            if hasattr(self.intents, intent):
                setattr(self.intents, intent, True)
            else:
                raise ValueError(f"Invalid intent: {intent}")

        self.client = discord.Client(intents=self.intents)

        # events and commands: https://dev.to/mikeywastaken/events-in-discord-py-mk0
        self.client.event(self.on_ready)
        self.client.event(self.on_message)

    def run(self):
        # TODO: can add logger directly here as a kwarg
        self.client.run(self.bot_token)

    async def on_ready(self):
        print(f"{self.client.user} is connected to Discord!")

    async def on_message(self, message):
        if message.author == self.client.user:
            return

        if message.content.startswith("!discover"):
            response = f"Hi, I'm test_bot1"
            await message.channel.send(response)

        if message.content.startswith("!produce_icecream"):
            icecreams = self.handle_who_can(message)
            await message.channel.send(response)

    def handle_who_can(self, message):
        time.sleep(1)
        return [{"body": "icecream"} for _ in range(1)]

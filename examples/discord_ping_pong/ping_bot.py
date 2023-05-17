import sys, os, time
from dotenv import load_dotenv

<<<<<<< HEAD
import asyncio

from pathlib import Path
file_path = Path(__file__).absolute()
sys.path.append(str(file_path.parent.parent.parent))

from osnap.SwarmAdapters.DiscordAdapter import DiscordAdapter
from osnap.SwarmAgents import SwarmAgentBase

class ExampleSwarmAgent(SwarmAgentBase):

=======
from osnap_client.adapters.DiscordAdapter import DiscordAdapter
from osnap_client.agents import SwarmAgentBase


class ExampleSwarmAgent(SwarmAgentBase):
>>>>>>> 687d44eefefe8d1224508ed9f3f15a51e4d85b88
    def __init__(self, name, description, swarm_adapter):
        super().__init__(name, description, swarm_adapter)
        self.num_pings = 0
        self.max_pings = 5

        @self.command(name="hello")
        async def hello(message):
            await self.swarm_adapter.send_message("Hello!", "general")
<<<<<<< HEAD
            #await self.send_message("Hello!", "general")
=======
            # await self.send_message("Hello!", "general")
>>>>>>> 687d44eefefe8d1224508ed9f3f15a51e4d85b88

        @self.command(name="ping")
        async def ping(message):
            if self.num_pings >= self.max_pings:
                await self.swarm_adapter.send_message("I'm done pinging!", "general")
                return
<<<<<<< HEAD
            
=======

>>>>>>> 687d44eefefe8d1224508ed9f3f15a51e4d85b88
            time.sleep(2)
            self.num_pings += 1
            await self.swarm_adapter.send_message("$pong", "general")

        @self.command(name="reset")
        async def reset(message):
            self.num_pings = 0
            await self.swarm_adapter.send_message("I'm reset!", "general")


def main():
    """
    On a mac, go to Macintosh HD > Applications > Python3.x folder (x being your python3 version) > double click on "Install Certificates.command" file
    """
    load_dotenv()

    intents_list = ["message_content", "members", "guilds"]
    adapter = DiscordAdapter(
<<<<<<< HEAD
        start_server="swarm1_test",
        intents_list=intents_list,
        token = os.getenv("BOT1_TOKEN")
    )

    agent = ExampleSwarmAgent(
        name="Agent Smith",
        description="I am a bot that pings",
        swarm_adapter=adapter
    )
    agent.run()

    
if __name__ == "__main__":
    main()
=======
        start_server="fdog's server",
        intents_list=intents_list,
        token=os.getenv("PING_BOT_TOKEN"),
    )

    agent = ExampleSwarmAgent(
        name="Agent Smith", description="I am a bot that pings", swarm_adapter=adapter
    )
    agent.run()


if __name__ == "__main__":
    main()
>>>>>>> 687d44eefefe8d1224508ed9f3f15a51e4d85b88

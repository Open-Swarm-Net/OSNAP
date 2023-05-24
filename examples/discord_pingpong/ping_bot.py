import sys, os, time
from dotenv import load_dotenv

# adding the lates version of the osnap_client to the path
from pathlib import Path
file_path = Path(__file__).absolute()
sys.path.append(str(file_path.parent.parent.parent))

from osnap_client.adapters import DiscordAdapter
from osnap_client.agents import SwarmAgentBase
from osnap_client.protocol import AgentCommand

class ExampleSwarmAgent(SwarmAgentBase):
    def __init__(self, name, description, swarm_adapter):
        super().__init__(name, description, swarm_adapter)
        self.num_pings = 0
        self.max_pings = 5

        @self.command(name="hello")
        async def hello(message: AgentCommand):
            await self.swarm_adapter.send_message("Hello!", "general")

        @self.command(name="ping")
        async def ping(message: AgentCommand):
            if self.num_pings >= self.max_pings:
                await self.swarm_adapter.send_message("I'm done pinging!", "general")
                return
            time.sleep(2)
            self.num_pings += 1
            await self.swarm_adapter.send_message("$pong", "general")

        @self.command(name="reset")
        async def reset(message: AgentCommand):
            self.num_pings = 0
            await self.swarm_adapter.send_message("I'm reset!", "general")


def main():
    """
    On a mac, go to Macintosh HD > Applications > Python3.x folder (x being your python3 version) > double click on "Install Certificates.command" file
    """
    load_dotenv()

    intents_list = ["message_content", "members", "guilds"]
    adapter = DiscordAdapter(
        start_server=os.getenv("START_SERVER_NAME"),
        intents_list=intents_list,
        token=os.getenv("PING_BOT_TOKEN"),
    )

    agent = ExampleSwarmAgent(
        name="Agent Freeman", description="I am a bot who pings", swarm_adapter=adapter
    )
    agent.run()


if __name__ == "__main__":
    main()

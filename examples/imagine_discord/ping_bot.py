import sys, os, time
from dotenv import load_dotenv

# adding the lates version of the osnap_client to the path
from pathlib import Path
file_path = Path(__file__).absolute()
sys.path.append(str(file_path.parent.parent.parent))

from osnap_client.adapters import DiscordAdapter
from osnap_client.agents import SwarmAgentBase
from osnap_client.protocol import AgentCommand, AgentCommandType
from osnap_client.utils.ai_engines import DalleEngine

class PingBot(SwarmAgentBase):
    def __init__(self, name, description, swarm_adapter):
        super().__init__(name, description, swarm_adapter)

        @self.command(name="ping")
        async def ping(command_obj: AgentCommand):
            print(f"Got a ping from {command_obj.sender}")
            await self.swarm_adapter.send_message(
                channel_id=command_obj.channel_id,
                message=f"pong from {self.name}"
            )

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

    agent = PingBot(
        name="PingBot",
        description="When someone says 'ping', I say post a job to the swarm!",
        swarm_adapter=adapter
    )
    agent.run()


if __name__ == "__main__":
    main()

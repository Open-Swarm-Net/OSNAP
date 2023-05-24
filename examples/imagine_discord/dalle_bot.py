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

class DalleAgent(SwarmAgentBase):
    def __init__(self, name, description, swarm_adapter):
        super().__init__(name, description, swarm_adapter)

        self.dalle_engine = DalleEngine()

        @self.command(name="imagine")
        async def imagine(message: AgentCommand):
            try:
                prompt = message.payload
                image = self.dalle_engine.imagine(prompt)

                response = AgentCommand(
                    sender=self.name,
                    receiver="agent",
                    command_type=AgentCommandType.SUBMIT,
                    task_name="imagine",
                    payload_type = 'attachment',
                    payload='' # cannot send bytes over discord because of the 4000 character limit
                )
                await self.swarm_adapter.send_dm(response, message.sender, file=image)
            except Exception as e:
                print(f"Error in imagine command: {e}")
                response = AgentCommand(
                    sender=self.name,
                    receiver="agent",
                    command_type=AgentCommandType.ERROR,
                    task_name="imagine",
                    payload_type = 'str',
                    payload=f"505: Internal Server Error",
                )
                await self.swarm_adapter.send_dm(response, message.sender)

def main():
    """
    On a mac, go to Macintosh HD > Applications > Python3.x folder (x being your python3 version) > double click on "Install Certificates.command" file
    """
    load_dotenv()

    intents_list = ["message_content", "members", "guilds"]
    adapter = DiscordAdapter(
        start_server=os.getenv("START_SERVER_NAME"),
        intents_list=intents_list,
        token=os.getenv("DALLE_BOT_TOKEN"),
    )

    agent = DalleAgent(
        name="DalleBot",
        description="I am a bot who can generate images",
        swarm_adapter=adapter
    )
    agent.run()


if __name__ == "__main__":
    main()

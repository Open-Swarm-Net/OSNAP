import sys, os, time
from dotenv import load_dotenv
import base64

# adding the lates version of the osnap_client to the path
from pathlib import Path
file_path = Path(__file__).absolute()
sys.path.append(str(file_path.parent.parent.parent))

from osnap_client.adapters import DiscordAdapter
from osnap_client.agents import SwarmAgentBase
from osnap_client.protocol import AgentCommand, AgentCommandType, Task, TaskMedia
from osnap_client.utils.ai_engines import DalleEngine

class DalleAgent(SwarmAgentBase):
    def __init__(self, name, description, swarm_adapter):
        super().__init__(name, description, swarm_adapter)

        self.dalle_engine = DalleEngine()

        @self.command(name="imagine")
        async def imagine(message: AgentCommand):
            try:
                if message.payload_type == "task":
                    task = Task.from_json(message.payload)
                    prompt = task.task_description
                    task_id = task.task_id
                elif message.payload_type == "str":
                    prompt = message.payload
                    task_id = None
                    task = Task(task_name="imagine", task_description=prompt)

                image = self.dalle_engine.imagine(prompt)

                task.result = prompt
                task.related_media = [TaskMedia(media_type="Pil.Image", media=base64.b64encode(image).decode('utf-8'))]
                task.status = "submitted"

                response = AgentCommand(
                    sender=self.name,
                    receiver="agent",
                    command_type=AgentCommandType.SUBMIT,
                    task_type="imagine",
                    payload_type='task',
                    payload=task.json(),
                )
                await self.swarm_adapter.send_dm(response, message.sender, file=image)
            except Exception as e:
                print(f"Error in imagine command: {e}")
                response = AgentCommand(
                    sender=self.name,
                    receiver="agent",
                    command_type=AgentCommandType.ERROR,
                    task_type="imagine",
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

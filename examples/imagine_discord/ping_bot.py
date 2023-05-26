import sys, os, time
from dotenv import load_dotenv
import json

# adding the lates version of the osnap_client to the path
from pathlib import Path
file_path = Path(__file__).absolute()
sys.path.append(str(file_path.parent.parent.parent))

from osnap_client.adapters import DiscordAdapter
from osnap_client.agents import SwarmAgentBase
from osnap_client.protocol import AgentCommand, AgentCommandType

class PingBot(SwarmAgentBase):
    def __init__(self, name, description, swarm_adapter):
        super().__init__(name, description, swarm_adapter)

        @self.command(name="smart_imagine")
        async def smart_imagine(command_obj: AgentCommand):
            prompt = command_obj.payload

            # creating the main task
            main_task_id, main_task = self.task_map.create_task(prompt)
            main_task_json = main_task.json()

            # the next in the hierarchy is the image generation task
            image_generation_task_id, image_generation_task = self.task_map.add_subtask(main_task_id, "{{generated_prompt}}")
            image_generation_task_json = image_generation_task.json()

            # first, research the image generation and find the best prompt
            prompt_research = f"Generate the best prompt for dall-e 2 to generate an image of {prompt}"
            research_task_id, research_task = self.task_map.add_subtask(image_generation_task_id, prompt_research)
            research_task_json = research_task.json()

            # first, send the research task to the swarm
            request = AgentCommand(
                sender=self.name,
                receiver="swarm",
                command_type=AgentCommandType.TASK,
                task_type="research",
                payload_type = 'task',
                payload=research_task_json
            )
            await self.swarm_adapter.send_message(request)

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
        description="I optimize the image generation prompt and generate an image for you.",
        swarm_adapter=adapter
    )
    agent.run()


if __name__ == "__main__":
    main()

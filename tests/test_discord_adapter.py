import sys, os, time
from pathlib import Path
file_path = Path(__file__).absolute()
sys.path.append(str(file_path.parent.parent))

from dotenv import load_dotenv
import discord

from osnap.SwarmAdapters import DiscordAdapter
from osnap.SwarmAdapters import ExampleSwarmAgent

if __name__ == "__main__":
    """
    On a mac, go to Macintosh HD > Applications > Python3.x folder (x being your python3 version) > double click on "Install Certificates.command" file
    """
    load_dotenv()
    intents_list = ["message_content"]
    mybot_logic = ExampleSwarmAgent(command_prefix='$')
    adapter = DiscordAdapter(
        agent_logic = mybot_logic,
        start_server = "swarm1_test",
        intents_list = intents_list,
        token = os.getenv("DISCORD_BOT_TOKEN")
    )
    adapter.run()
    # config = {
    #     "bot_token": os.getenv("DISCORD_BOT_TOKEN"),
    #     "server": 'swarm1_test',
    #     "entry_channel": 'general',
    #     "intents": ['message_content']
    # }
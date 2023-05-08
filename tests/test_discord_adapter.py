import sys, os, time
from pathlib import Path
file_path = Path(__file__).absolute()
sys.path.append(str(file_path.parent.parent))

import pytest
from dotenv import load_dotenv

from osnap.SwarmAdapters import DiscordSwarmAdapter

def test_discord_adapter(config):
    adapter = DiscordSwarmAdapter(config)
    adapter.run()
    time.wait(20)
    adapter.stop()

if __name__ == "__main__":
    load_dotenv()
    config = {
        "bot_token": os.getenv("DISCORD_BOT_TOKEN"),
        "server": 'swarm1_test',
        "entry_channel": 'general',
        "intents": ['message_content']
    }
    test_discord_adapter(config)
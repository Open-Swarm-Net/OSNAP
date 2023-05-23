import sys, os, time
from dotenv import load_dotenv
from pytest import fixture

from osnap_client.adapters import DiscordAdapter 


@fixture
def config():
    load_dotenv()
    config = {
        "bot_token": os.getenv("DISCORD_BOT_TOKEN"),
        "server": "swarm1_test",
        "entry_channel": "general",
        "intents": ["message_content"],
    }
    return config


# def test_discord_adapter(config):
#     adapter = DiscordSwarmAdapter(config)
#     adapter.run()
#     time.wait(20)
#     adapter.stop()


if __name__ == "__main__":
    load_dotenv()

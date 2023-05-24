import sys, os, time
from dotenv import load_dotenv
from pathlib import Path
file_path = Path(__file__).absolute()
sys.path.append(str(file_path.parent.parent.parent))

from osnap_client.adapters import DiscordAdapter
from .ping_bot import PingBot

load_dotenv()

intents_list = ["message_content", "members", "guilds"]
swarm = DiscordAdapter(
    start_server=os.getenv("START_SERVER_NAME"),
    intents_list=intents_list,
    token=os.getenv("SWARM_TOKEN"),
)

# how does an agent join the swarm? 
ping_agent = PingBot(swarm_adapter=swarm)

# The swarm needs to should be responsible for issuing the UUID to the agent
# otherwise, guaranteeing uniqueness is cumbersome for users
# 
# Probably 

# swarm.join(ping_agent)



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
        name="Agent Smith", description="I am a bot that pings", swarm_adapter=adapter
    )
    agent.run()


if __name__ == "__main__":
    main()

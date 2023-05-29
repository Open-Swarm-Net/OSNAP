# testing central controller architecture
import sys
from pathlib import Path

# adding the lates version of the osnap_client to the path
file_path = Path(__file__).absolute()
sys.path.append(str(file_path.parent.parent))

from osnap_client.agents import SwarmAgentBase
from osnap_client.adapters import CentralControllerAdapter
from osnap_client.schemas import AgentTask, AgentRunResponse

class TestAgent(SwarmAgentBase):
    def start(self, objective: str, agent_url=None):
        print("starting objective")

    def run(self, task: AgentTask) -> AgentRunResponse:
        print("running task")
        return AgentRunResponse(status="success", payload="test payload")

    def terminate(self):
        print("terminating objective")


def main():
    adapter = CentralControllerAdapter("http://localhost:3000", "dummy")
    agent = TestAgent(
        name="test agent",
        description="test agent description",
        adapter=adapter
    )

    agent.join_swarm()

    print(agent.swarm_agents)

    agent.stop()




if __name__ == '__main__':
    main()
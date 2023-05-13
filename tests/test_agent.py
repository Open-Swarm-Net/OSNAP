from osnap_client import OSNAPAgent, AgentInfo
from uuid import uuid4

from osnap_client.core.agent import OSNAPAgentTaskResult


class TestAgent(OSNAPAgent):
    name = "test_agent"
    description = "test agent"
    tools = ["test_tool"]
    id = "1234"
    url = "foobar"

    def run(self, task):
        pass

    def listen(self, result: OSNAPAgentTaskResult):
        return super().listen(result)

    def start(self, objective: str, agent_url=None):
        return super().start(objective, agent_url)


def test_agent_creation():
    agent = TestAgent()
    assert agent.name == "test_agent"
    assert agent.description == "test agent"
    assert agent.tools == ["test_tool"]

    # validate arguments
    try:

        class BadAgent(OSNAPAgent):
            name = 1
            description = 2
            tools = 3

        agent = BadAgent(name="test_agent")
    except Exception as e:
        assert e.__class__.__name__ == "TypeError"


# Agents should have a /info endpoint that returns the agent's name, description, and scope.
def test_agent_info():
    agent = TestAgent()

    assert agent.info() == AgentInfo(
        **{
            "name": "test_agent",
            "description": "test agent",
            "id": "1234",
            "tools": ["test_tool"],
            "url": "foobar",
        }
    )

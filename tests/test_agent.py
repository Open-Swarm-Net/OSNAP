from osnap_client.agents import OSNAPBaseAgent, AgentInfo, AgentTaskResult
from uuid import uuid4


class FakeAgent(OSNAPBaseAgent):
    name = "test_agent"
    description = "test agent"
    tools = ["test_tool"]
    id = "1234"
    url = "foobar"

    def run(self, task):
        pass

    def listen(self, result: AgentTaskResult):
        return super().listen(result)

    def start(self, objective: str, agent_url=None):
        return super().start(objective, agent_url)


def test_agent_creation():
    agent = FakeAgent()
    assert agent.name == "test_agent"
    assert agent.description == "test agent"
    assert agent.tools == ["test_tool"]

    # validate arguments
    try:

        class BadAgent(OSNAPBaseAgent):
            name = 1
            description = 2
            tools = 3

        agent = BadAgent(name="test_agent")
    except Exception as e:
        assert e.__class__.__name__ == "TypeError"


def test_agent_required_methods():
    class FakeAgentWithoutMethods(OSNAPBaseAgent):
        name = "test_agent"
        description = "test agent"
        tools = ["test_tool"]
        id = "1234"
        url = "foobar"

    try:
        agent = FakeAgentWithoutMethods()
    except Exception as e:
        assert e.__class__.__name__ == "TypeError"


# Agents should have a /info endpoint that returns the agent's name, description, and scope.
def test_agent_info():
    agent = FakeAgent()

    assert agent.info() == AgentInfo(
        **{
            "name": "test_agent",
            "description": "test agent",
            "id": "1234",
            "tools": ["test_tool"],
            "url": "foobar",
        }
    )

from unittest.mock import patch


def test_register_command_called():
    with patch.object(OSNAPBaseAgent, "_register_command") as mock_register:

        agent = FakeAgent()

        mock_register.assert_called_once()
import sys, os
sys.path.append(os.path.abspath(os.path.join("..")))

from osnap import OSNAPApp, OSNAPAgent, OSNAPTool, OSNAPRegistry, Scope

import uuid


class MockAgentRegistry(OSNAPRegistry):
    agents = []

    def register(self, agent: OSNAPAgent):
        agent.id = str(uuid.uuid4())
        self.agents.append(agent)
        return agent

    def unregister(self):
        pass


class MockToolRegistry(OSNAPRegistry):
    tools = []

    def register(self, tool: OSNAPTool):
        tool.id = str(uuid.uuid4())
        self.tools.append(tool)
        return tool

    def unregister():
        pass


def test_osnap_app_init():
    tools = [
        OSNAPTool(
            name="test_tool",
            description="test tool",
            scope=Scope.PUBLIC,
            invoke_endpoint="foobar",
        ),
        OSNAPTool(
            name="test_tool2",
            description="test tool2",
            scope=Scope.PUBLIC,
            invoke_endpoint="foobar2",
        ),
    ]
    agents = [
        OSNAPAgent(
            name="test_agent", description="test agent", scope="public", tools=tools
        ),
        OSNAPAgent(
            name="test_agent2", description="test agent2", scope="public", tools=tools
        ),
    ]

    agent_registry = MockAgentRegistry()
    tool_registry = MockToolRegistry()

    app = OSNAPApp(
        agents=agents,
        tools=tools,
        agent_registry=agent_registry,
        tool_registry=tool_registry,
    )

    assert len(agent_registry.agents) == 2
    assert len(tool_registry.tools) == 2
    assert len(agent_registry.agents[0].tools) == 2


if __name__ == "__main__":
    test_osnap_app_init()
    print("Everything passed")
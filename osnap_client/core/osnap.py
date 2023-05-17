import json
import enum
import time
import uuid
from typing import Callable, Dict, Union, List, Any
from functools import wraps

from pydantic import BaseModel
from abc import ABC, abstractmethod

import networkx as nx

from .crypt import SignatureUtil

from osnap_client.pubsub import PubSub


class OSNAPRegistry(BaseModel):
    """Base Class for an Agent or Tool Registry"""

    @abstractmethod
    def register(self):
        raise NotImplementedError

    @abstractmethod
    def unregister(self):
        raise NotImplementedError


class OSNAPApp:
    required_handler_types = set(
        [
            "agents",
            # "tools",
            # "run"
        ]
    )

    graph: nx.DiGraph
    agent_registry: OSNAPRegistry
    tool_registry: OSNAPRegistry

    def __init__(
        self,
        agents: list,
        tools: list,
        agent_registry: OSNAPRegistry,
        tool_registry: OSNAPRegistry,
    ):
        ## iterate over all the methods of the API class
        # TODO: Figure out the best time to check the API
        # self.check_api()
        self.handler_registry = set()
        self.agent_registry = agent_registry
        self.tool_registry = tool_registry
        self.pubsub = None
        self.register_agents(agents)

    async def create_pubsub(self):
        self.pubsub = PubSub()
        await self.pubsub.connect()
        await self.pubsub.subscribe()

    async def call_pubsub(self, message):
        if self.pubsub is None:
            return None
        else:
            await self.pubsub.publish(message)

    def agents(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # OSNAPRequest = *args["request"]
            await self.call_pubsub("agents")
            return await func(*args, **kwargs)

        self.handler_registry.add(("agents", wrapper))
        return wrapper

    def _build_agent_tool_graph(self, agents: list, external=False):
        app_graph = nx.DiGraph()
        for agent in agents:
            if external:
                agent.scope = Scope.EXTERNAL
            app_graph.add_node(agent.name, agent=agent)
            for tool in agent.tools:
                if external:
                    tool.scope = Scope.EXTERNAL
                app_graph.add_node(tool.name, tool=tool)
                app_graph.add_edge(agent.name, tool.name, type="agent->tool")
        return app_graph

    def _register_app_graph(self, app_graph: nx.DiGraph):
        # TODO: put this in RedisGraph

        sorted = list(reversed(list(nx.topological_sort(app_graph))))
        for node in sorted:
            if "agent" in app_graph.nodes[node]:
                tool_deps = list(app_graph.successors(node))
                agent = app_graph.nodes[node]["agent"]
                agent.tools = [
                    app_graph.nodes[tool]["tool"].toJson() for tool in tool_deps
                ]
                self.agent_registry.register(app_graph.nodes[node]["agent"])
            elif "tool" in app_graph.nodes[node]:
                assigned = self.tool_registry.register(app_graph.nodes[node]["tool"])
                # Write the assigned id back to the graph
                app_graph.nodes[node]["tool"].id = assigned.id

    def register_agents(self, agents: list, external=False):
        self.graph = self._build_agent_tool_graph(agents, external=external)

        # register the graph with the app using topo sort
        self._register_app_graph(self.graph)

    def check_api(self):
        handler_types = set(
            [handler_type for (handler_type, handler) in self.handler_registry]
        )
        missing_handler_types = self.required_handler_types - handler_types
        if len(missing_handler_types):
            raise Exception("Missing required handlers: " + str(missing_handler_types))


class Scope(str, enum.Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    EXTERNAL = "external"


class OSNAPResponse(BaseModel):
    def __init__(self, payload: Dict):
        self.payload = json.dumps(payload)
        self.signature = None


class OSNAPError:
    def __init__(self, message: str):
        self.payload = json.dumps({"error": message})
        self.signature = None


class OSNAPRequest(BaseModel):
    def __init__(
        self,
        caller_agent_id: str,
        request_type: str,
        task_name: str = None,
        priority: int = 0,
        request_metadata: Dict = None,
        instructions=None,
    ):
        self.caller_agent_id = caller_agent_id
        self.request_type = request_type
        self.task_name = task_name
        self.priority = priority
        self.request_metadata = request_metadata or {}
        self.timestamp = time.time()
        self.payload = json.dumps(
            {
                "caller_agent_id": self.caller_agent_id,
                "request_type": self.request_type,
                "task_name": self.task_name,
                "priority": self.priority,
                "request_metadata": self.request_metadata,
                "timestamp": self.timestamp,
            }
        )
        self.signature = None
        self.instructions = instructions


class OSNAPTool:
    def __init__(
        self,
        name: str,
        description: str,
        invoke_endpoint: str,
        scope: Scope,
        invoke_required_params: Dict[str, Any] = {},
        invoke_optional_params: List[str] = [],
        id: str = None,
    ):
        self.name = name
        self.description = description
        self.scope = scope
        self.invoke_endpoint = invoke_endpoint
        self.invoke_required_params = invoke_required_params
        self.invoke_optional_params = invoke_optional_params
        self.id = id

    def __str__(self) -> str:
        return f"Tool: {self.name} id: ({self.id}) description: {self.description} scope: {self.scope} invoke_endpoint: {self.invoke_endpoint} invoke_required_params: {self.invoke_required_params} invoke_optional_params: {self.invoke_optional_params}"

    def __repr__(self) -> str:
        return self.__str__()

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)


# Usage Example

# @OSNAP.agents()
# def my_apps_agent_handler():
#  return my_apps_agent_registry.get_agents(request)
#
# myapp = OSnapApp()

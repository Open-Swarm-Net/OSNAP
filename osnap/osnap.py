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

from pubsub import PubSub


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


class OSNAPAgent:
    """
    Agents are the core of the OSNAP system. They are the entities that interact with one another,
    or themselves to perform tasks.

    Agents are registered with the OSNAP system, and can be public or private. Public agents are available
    to all other agents, while private agents are only available to agents that are in the same environment.

    They will get an ID after being registered, and will be able to use that ID to interact with other agents.
    """

    def __init__(
        self,
        name: str,
        description: str,
        scope: Scope = Scope.PRIVATE,
        id: str = None,
        using_rsa: bool = False,
        tools: List = [],
    ):
        self.id = id
        self.name = name
        self.description = description
        self.scope = scope
        self.using_rsa = using_rsa
        self.tools = tools or []

        if isinstance(tools, str):
            tool_list_json = json.loads(tools)
            self.tools = [OSNAPTool(**json.loads(tool)) for tool in tool_list_json]

        if using_rsa:
            # Generate a key pair
            (
                self.private_key_pem,
                self.public_key_pem,
            ) = SignatureUtil.generate_key_pair()

        # Call the register method with required arguments

    def __str__(self):
        return f"Agent: {self.name} id: ({self.id}) description: {self.description} tools: {self.tools}"

    def send_request_to_agent(
        self, destination_agent: "OSNAPAgent", request: OSNAPRequest
    ) -> Union[OSNAPResponse, OSNAPError]:
        if self.handlers["request_validation"](
            request
        ) and SignatureUtil.verify_signature(
            destination_agent.public_key_p_key_pem, request.payload, request.signature
        ):
            response = destination_agent.process_request(request)
            if self.handlers["response_validation"](
                response
            ) and SignatureUtil.verify_signature(
                destination_agent.public_key_pem, response.payload, response.signature
            ):
                return response
            else:
                return OSNAPError("Invalid response signature")
        else:
            return OSNAPError("Invalid request signature")

    def process_request(
        self, request: OSNAPRequest
    ) -> Union[OSNAPResponse, OSNAPError]:
        if request.request_type == "info":
            handler = self.handlers.get("info")
            if handler:
                return handler(request)
            else:
                return OSNAPError("Info handler not found")
        elif request.request_type == "task":
            handler = self.handlers.get(request.task_name)
            if handler:
                return handler(request)
            else:
                return OSNAPError("Task handler not found")
        else:
            return OSNAPError("Invalid request type")

    def create_osnap_request(
        self,
        request_type: str,
        task_name: str = None,
        priority: int = 0,
        request_metadata: Dict = None,
    ) -> OSNAPRequest:
        request = OSNAPRequest(
            caller_agent_id=self.id,
            request_type=request_type,
            task_name=task_name,
            priority=priority,
            request_metadata=request_metadata,
        )
        signature = SignatureUtil.sign_data(self.private_key_pem, request.payload)
        request.signature = signature
        return request

    def create_osnap_response(self, payload: Dict) -> OSNAPResponse:
        response = OSNAPResponse(payload=payload)
        signature = SignatureUtil.sign_data(self.private_key_pem, response.payload)
        response.signature = signature
        return response

    def create_osnap_error(self, message: str) -> OSNAPError:
        error = OSNAPError(message)
        signature = SignatureUtil.sign_data(self.private_key_pem, error.payload)
        error.signature = signature
        return error


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
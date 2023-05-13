from pydantic import BaseModel, validate_arguments, ValidationError
from typing import List, Union
from uuid import UUID
from enum import Enum
from abc import ABC, abstractmethod

from .osnap import Scope


class OSNAPTask(BaseModel):
    objective: str
    task_name: str
    task_description: str
    task_tool: str = ""


class OSNAPAgentRunResponseStatus(str, Enum):
    STARTING = "starting"
    WORKING = "working"
    ERROR = "error"


class OSNAPAgentRunResponse(BaseModel):
    """
    The response from an agent's run method.
    """

    status: OSNAPAgentRunResponseStatus
    message: str
    payload: dict


class OSNAPAgentTaskResultStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"


class OSNAPAgentTaskResult(BaseModel):
    """
    The result of an agent's task.
    Payload might contain metadata like the time it took to run the task
    """

    status: OSNAPAgentRunResponseStatus
    message: str
    payload: dict


class AgentInfo(BaseModel):
    """
    The response from an agent's info method.
    """

    name: str
    description: str
    id: Union[int, str, UUID, None] = None
    tools: list = []
    url: str = None


class OSNAPAgent(BaseModel, ABC):
    """
    Agents are the core of the OSNAP system. They are the entities that interact with one another,
    or themselves to perform tasks.

    Agents implement the protocol of starting objectives, running tasks, listening for task results, and completing or terminating tasks.
    """

    name: str
    description: str
    id: Union[int, str, UUID] = None
    tools: list = []
    url: str = None

    def info(self) -> AgentInfo:
        """
        Returns the agent's name, description, and public tools.
        """
        return AgentInfo(**self.__dict__)

    @abstractmethod
    def start(self, objective: str, agent_url=None):
        """
        Begins work on a new objective.
        If agent_url is provided, it communicates directly with that agent. Otherwise, it searches the registry.
        """
        raise NotImplementedError

    @abstractmethod
    def run(self, task: OSNAPTask) -> OSNAPAgentRunResponse:
        """
        Receives a request from another agent.
        Returns a run response with a status and optionally, a payload
        """
        raise NotImplementedError

    @abstractmethod
    def listen(self, result: OSNAPAgentTaskResult):
        """
        Receives a task result from another agent.
        """
        raise NotImplementedError

    def complete(self):
        """
        Completes the current objective.
        Can use this to stop listening for particular task results or stop running a task.
        """
        raise NotImplementedError

    def terminate(self):
        """
        Terminates the current objective.
        Can use this to cancel a task or stop listening for particular task results.
        """
        raise NotImplementedError

    #     if isinstance(tools, str):
    #         tool_list_json = json.loads(tools)
    #         self.tools = [OSNAPTool(**json.loads(tool)) for tool in tool_list_json]

    #     if using_rsa:
    #         # Generate a key pair
    #         (
    #             self.private_key_pem,
    #             self.public_key_pem,
    #         ) = SignatureUtil.generate_key_pair()

    #     # Call the register method with required arguments

    # def __str__(self):
    #     return f"Agent: {self.name} id: ({self.id}) description: {self.description} tools: {self.tools}"

    # def send_request_to_agent(
    #     self, destination_agent: "OSNAPAgent", request: OSNAPRequest
    # ) -> Union[OSNAPResponse, OSNAPError]:
    #     if self.handlers["request_validation"](
    #         request
    #     ) and SignatureUtil.verify_signature(
    #         destination_agent.public_key_p_key_pem, request.payload, request.signature
    #     ):
    #         response = destination_agent.process_request(request)
    #         if self.handlers["response_validation"](
    #             response
    #         ) and SignatureUtil.verify_signature(
    #             destination_agent.public_key_pem, response.payload, response.signature
    #         ):
    #             return response
    #         else:
    #             return OSNAPError("Invalid response signature")
    #     else:
    #         return OSNAPError("Invalid request signature")

    # def process_request(
    #     self, request: OSNAPRequest
    # ) -> Union[OSNAPResponse, OSNAPError]:
    #     if request.request_type == "info":
    #         handler = self.handlers.get("info")
    #         if handler:
    #             return handler(request)
    #         else:
    #             return OSNAPError("Info handler not found")
    #     elif request.request_type == "task":
    #         handler = self.handlers.get(request.task_name)
    #         if handler:
    #             return handler(request)
    #         else:
    #             return OSNAPError("Task handler not found")
    #     else:
    #         return OSNAPError("Invalid request type")

    # def create_osnap_request(
    #     self,
    #     request_type: str,
    #     task_name: str = None,
    #     priority: int = 0,
    #     request_metadata: Dict = None,
    # ) -> OSNAPRequest:
    #     request = OSNAPRequest(
    #         caller_agent_id=self.id,
    #         request_type=request_type,
    #         task_name=task_name,
    #         priority=priority,
    #         request_metadata=request_metadata,
    #     )
    #     signature = SignatureUtil.sign_data(self.private_key_pem, request.payload)
    #     request.signature = signature
    #     return request

    # def create_osnap_response(self, payload: Dict) -> OSNAPResponse:
    #     response = OSNAPResponse(payload=payload)
    #     return response

    # def create_osnap_error(self, message: str) -> OSNAPError:
    #     error = OSNAPError(message)
    #     return error

from pydantic import BaseModel, validate_arguments, ValidationError
from typing import List, Union
from uuid import UUID
from enum import Enum
from abc import ABC, abstractmethod


class OSNAPTask(BaseModel):
    objective: str
    task_id: Union[int, str, UUID]
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


class OSNAPBaseAgent(BaseModel, ABC):
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

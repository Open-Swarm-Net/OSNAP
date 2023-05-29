from enum import Enum
from pydantic import BaseModel, validate_arguments, ValidationError

class AgentTaskResultStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"

class AgentTask(BaseModel):
    objective: str
    task_id: str
    task_name: str
    task_description: str
    task_tool: str = ""

class AgentTaskResult(BaseModel):
    """
    The result of an agent's task.
    Payload might contain metadata like the time it took to run the task
    """
    task_id: str
    task_name: str
    status: AgentTaskResultStatus
    message: str
    payload: dict
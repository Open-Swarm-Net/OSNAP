from enum import Enum
from pydantic import BaseModel
from typing import Any, Dict

class AgentCommandType(Enum):
    REQUEST = "request"
    RESPONSE = "response"
    ERROR = "error"
    ON_READY = "on_ready"
    TASK = "task"
    SUBMIT = "submit"
    REGISTER = "register"
    INFO = "info"
    # add more command types as needed

class AgentCommand(BaseModel):
    # TODO: substitute with the OSNAP protocol
    """This is an adapter-independent command object that is exchanged between the agnet and the adapter.
    Adapter -> Agent: This data structure is added to the task queue and is consumed by the agent.
    Agent -> Adapter: This data structure is sent to the adapter via the agent's callback function.

    Attributes:
        sender (str): Can be the adapter (on_ready), can be another agent on the swarm, can be the agent itself
        receiver (str): Can be another agent on swarm, can be a channel. CanNOT be the adapter.
        command (AgentCommandType): The type of command. Purely technical, not used by the agent directly.
        task_name (str): The name of the task to be executed by the agent
        status (int): The status. Same as HTTP status codes. 200 = OK, 400 = Bad Request, 500 = Internal Server Error
        data_type (str): The type of the data to be sent
        data (Any): The data to be sent
    """
    sender: str
    receiver: str
    command_type: AgentCommandType
    task_name: str
    payload_type: str
    payload: Any

    # def from_dict(self, data: Dict[str, Any]):
    #     return self.parse_obj(data)
    
    # def to_dict(self) -> Dict[str, Any]:
    #     return self.dict()
    
    # def from_json(self, json_str: str):
    #     return self.parse_raw(json_str)
    
    # def to_json(self) -> str:
    #     return self.json()
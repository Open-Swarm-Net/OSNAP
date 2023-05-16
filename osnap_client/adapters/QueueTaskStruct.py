from pydantic import BaseModel

class QueueTaskStruct(BaseModel):
    """ QueueTaskStruct holds the callback function and the arguments to pass to it. """
    command_type: str
    data: str
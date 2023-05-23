# Creating an Agent

## Use the OSNAPBaseAgent class

```python
from osnap_client import (
  OSNAPBaseAgent,
  AgentInfo,
  OSNAPTask,
  OSNAPAgentRunResponse
)

class MyAgent(OSNAPBaseAgent): 
  name = "My Agent"
  description = "My agent does cool things"
  tools = ["tool1", "tool2"]
  id = "1234"
  endpoint = "https://myagent.com/1234"

  def info(self) -> AgentInfo: 
    """
    Info is the only method with a concrete implementation in OSNAPBaseAgent. The default
    behavior returns an AgentInfo object constructed
    from the __dict__ of the class. 

    You can override this behavior if you want to do something more complex.
    """
    pass

  def run(self, task: OSNAPTask) -> OSNAPAgentRunResponse:
    """
    This is the method that will be called when your agent is invoked with some incoming task.

    You can implement it's behavior however you want, but it must return an OSNAPAgentRunResponse. 

    Because the predominant use case of Agents is to do somthing that takes a long time, run returns an 
    OSNAPAgentRunResponse object that contains a way for another agent to keep track of it's progress without blocking. 
    """

```
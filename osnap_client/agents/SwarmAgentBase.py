from abc import ABC, abstractmethod
from osnap_client.schemas import AgentTask, AgentRunResponse, SwarmAgentInfo
from osnap_client.adapters import SwarmAdapterBase

class SwarmAgentBase(ABC):
    """
    Agents are the core of the OSNAP system. They are the entities that interact with one another,
    or themselves to perform tasks.

    Agents implement the protocol of starting objectives, running tasks, listening for task results, and completing or terminating tasks.

    Args:
    - name: The name of the agent
    - description: A description of the agent
    - id: The id of the agent
    - command_map: A map of commands to functions
    """
    def __init__(self, name: str, description: str, adapter: SwarmAdapterBase):
        self.name = name
        self.description = description
        self.adapter = adapter

        self.command_map = {}
        self.swarm_agents = []

        self.info = SwarmAgentInfo(
            id=0,
            name=self.name,
            description=self.description,
            endpoints=list(self.command_map.keys())
        )

    def command(self, name: str):
        def decorator(func):
            self.command_map[name] = func
            return func
        return decorator

    def join_swarm(self):
        """
        Joins a swarm.
        """
        self.swarm_agents = self.adapter.join_swarm(self)
        
        for agent in self.swarm_agents:
            if agent.name == self.name:
                self.info = agent
                break
        
        print(f"Joined swarm: {self.swarm_agents}")
        print(f"Unique id: {self.info.id}")
    
    def stop(self):
        # first leave the swarm
        self.adapter.leave_swarm(self)

        # check that the agent is not in the swarm anymore
        agents = self.adapter.get_info()
        for agent in agents:
            if agent.name == self.name:
                raise Exception("Agent not removed from swarm")
        
        print("Agent removed from swarm")

    @abstractmethod
    def start(self, objective: str, agent_url=None):
        raise NotImplementedError

    @abstractmethod
    def run(self, task: AgentTask) -> AgentRunResponse:
        """
        Receives a request from another agent.
        Returns a run response with a status and optionally, a payload
        """
        raise NotImplementedError


    def __repr__(self):
        return self.info.dict()

    def __str__(self):
        return self.info.json()

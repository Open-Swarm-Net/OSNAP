import requests

from .SwarmAdapterBase import SwarmAdapterBase
from osnap_client.agents import SwarmAgentBase
from osnap_client.schemas import SwarmAgentInfo

class CentralControllerAdapter(SwarmAdapterBase):

    def __init__(self, swarm_host: str, token: str):
        self.swarm_host = swarm_host
        self.token = token

    def join_swarm(self, agent: SwarmAgentBase) -> list[SwarmAgentInfo]:
        """
        Joins a swarm.
        """

        # create the request
        url = f"{self.swarm_host}/api/join"
        headers = {
            "Authorization": self.token,
            "Content-Type": "application/json"
        }
        data = agent.info.json()

        # send the request
        response = requests.post(url, headers=headers, data=data)

        # handle the response
        if response.status_code == 200:
            # response includes a list of agent objects in the swarm
            # so we need to parse the list
            agents = response.json()
            agent_list = [SwarmAgentInfo(**agent) for agent in agents]
            return agent_list
        else:
            raise Exception(f"Failed to join swarm: {response.status_code} {response.text}")

    def leave_swarm(self, agent: SwarmAgentBase) -> list[SwarmAgentInfo]:
        """
        Leaves a swarm.
        """

        # create the request
        url = f"{self.swarm_host}/api/leave"
        headers = {
            "Authorization": self.token,
            "Content-Type": "application/json"
        }
        data = agent.info.json()

        # send the request
        response = requests.post(url, headers=headers, data=data)

        # handle the response
        if response.status_code == 200:
            other_user_agents = response.json()
            other_user_agents = [SwarmAgentInfo(**agent) for agent in other_user_agents]
            return other_user_agents
        else:
            raise Exception(f"Failed to leave swarm: {response.status_code} {response.text}")
    
    def get_info(self) -> dict:
        """
        Returns the information about the swarm.
        """

        url = f"{self.swarm_host}/api/agents"
        response = requests.get(url)
        if response.status_code == 200:
            agents = response.json()
            agents = [SwarmAgentInfo(**agent) for agent in agents]
            return agents
        else:
            raise Exception(f"Failed to get swarm info: {response.status_code} {response.text}")
        
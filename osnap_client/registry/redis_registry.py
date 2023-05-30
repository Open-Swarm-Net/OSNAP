import redis
import networkx as nx
from typing import List, Dict
from dataclasses import asdict

from osnap_client.managers import SwarmManager
from osnap_client.agents import SwarmAgent
from .base import SwarmRegistryBase

class RedisSwarmRegistry(SwarmRegistryBase):
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis = redis.StrictRedis(host=host, port=port, db=db, decode_responses=True)
        self.graph = nx.DiGraph()

    def add_swarm_entry(self, swarm: SwarmManager):
        self.graph.add_node(swarm.swarm_id)
        self._persist_swarm_entry(swarm)

    def add_agent_entry(self, agent: SwarmAgent):
        self.graph.add_node(agent.id)
        self._persist_agent_entry(agent)

    def join_swarm(self, swarm_id: str, joined_swarm_id: str):
        # self.graph.add_edge(swarm_id, joined_swarm_id)
        # self._persist_swarm_relationship(swarm_id, joined_swarm_id)
        pass

    def _persist_swarm_entry(self, swarm: SwarmManager):
        swarm_key = f'swarm:{swarm.swarm_id}'
        self.redis.hmset(swarm_key, mapping=asdict(swarm))

    def _persist_agent_entry(self, agent: SwarmAgent):
        agent_key = f'agent:{agent.id}'
        self.redis.hmset(agent_key, mapping=asdict(agent))

    # def _persist_swarm_relationship(self, swarm_id: str, joined_swarm_id: str):
    #     relationship_key = f'swarm_relationship:{swarm_id}:{joined_swarm_id}'
    #     self.redis.set(relationship_key, '')

    def retrieve_swarm_information(self, swarm_id: str) -> SwarmManager:
        swarm_key = f'swarm:{swarm_id}'
        swarm_data = self.redis.hgetall(swarm_key)
        if swarm_data:
            # Parse the swarm_data and return an instance of SwarmManagerBase
            # You can use the retrieved data to populate the SwarmManagerBase attributes

            return SwarmManager(**swarm_data)
        return None

    def retrieve_agent_information(self, agent_id: str) -> SwarmAgent:
        agent_key = f'agent:{agent_id}'
        agent_data = self.redis.hgetall(agent_key)
        if agent_data:
            # Parse the agent_data and return an instance of SwarmAgentBase
            # You can use the retrieved data to populate the SwarmAgentBase attributes
            return SwarmAgent(**agent_data) 
        return None

    # def perform_graph_query(self, query: str) -> List[Dict]:
    #     # Perform the graph query using networkx and return the results
    #     results = nx.query.ancestors(self.graph, query)  # Example query, customize as per your requirements
    #     return list(results)

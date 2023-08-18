import redis
from redis.commands.graph import Graph, Node, Edge
import networkx as nx
from typing import List, Dict
from enum import Enum
from dataclasses import asdict

from osnap_client.managers import SwarmManager
from osnap_client.agents import SwarmAgent
from .base import SwarmRegistryBase

class SwarmRelationship:
    JOINED = "joined"

class RedisSwarmRegistry(SwarmRegistryBase):
    def __init__(self, host='localhost', port=6379, db=0, graph_name='swarm_registry'):
        self.redis = redis.StrictRedis(host=host, port=port, db=db, decode_responses=True)
        self.redis_graph = Graph(self.redis, graph_name)
        self.graph = nx.DiGraph()

    def _entity_to_node(self, entity: SwarmManager | SwarmAgent) -> Node:
        return Node(node_id=entity.id, alias=entity.name, label=entity.type, properties=asdict(entity))


    def _add_node(self, node: SwarmManager | SwarmAgent):
        self.graph.add_node(node.id)
        if isinstance(node, SwarmManager):
            self.add_swarm_entry(node)
        elif isinstance(node, SwarmAgent):
            self.add_agent_entry(node)

    def _add_edge(self, from_node: Node, to_node: Node, relationship):
        match_query = f"MATCH (a:{from_node.label}),(b:{to_node.label}) WHERE a.id = {from_node.id} AND b.id = {to_node.id}"

        query = f"""
        {match_query}
        CREATE (a)-[r:joined]->(b) RETURN r
        """.replace("\n", "")

        self.redis_graph.query(query)

    def add_swarm_entry(self, swarm: SwarmManager):
        node = self._entity_to_node(swarm)
        self._persist_node(node)

    def add_agent_entry(self, agent: SwarmAgent):
        node = self._entity_to_node(agent)
        self._persist_node(node)

    def join_swarm(self, from_entity: SwarmAgent | SwarmManager, to_entity: SwarmManager):
        """
        Adds an edge between two nodes in the graph
        """
        from_node = self._entity_to_node(from_entity)
        to_node = self._entity_to_node(to_entity)

        return self._add_edge(from_node, to_node, SwarmRelationship.JOINED)

    def _persist_node(self, node: Node):
        query = f"CREATE {node}"
        self.redis_graph.query(query)

    def retrieve_swarm_information(self, swarm_id: int) -> SwarmManager:
        swarm_key = f'swarm:{swarm_id}'
        swarm_data = self.redis.hgetall(swarm_key)
        if swarm_data:
            # Parse the swarm_data and return an instance of SwarmManagerBase
            # You can use the retrieved data to populate the SwarmManagerBase attributes

            return SwarmManager(**swarm_data)
        return None

    def retrieve_joined_agents(self) -> List[SwarmAgent]:
        agent_data = self.redis_graph.query("MATCH (a:agent)-[:joined]->(b:manager) RETURN a")
        if agent_data:
            # Parse the agent_data and return an instance of SwarmAgentBase
            # You can use the retrieved data to populate the SwarmAgentBase attributes
            return [SwarmAgent(**agent_data) for agent_data in agent_data]
        return None

    # def perform_graph_query(self, query: str) -> List[Dict]:
    #     # Perform the graph query using networkx and return the results
    #     results = nx.query.ancestors(self.graph, query)  # Example query, customize as per your requirements
    #     return list(results)

from osnap_client.managers import SwarmManager
from osnap_client.agents import SwarmAgent
from osnap_client.registry import RedisSwarmRegistry
import pytest


class TestRegistry: 

    def setup_class(self): 
        print("setting up test registry using redis, make sure redis is running locally")
        self.registry = RedisSwarmRegistry(db=1)
       

    def teardown_class(self):
        print("tearing down test registry")
        self.registry.redis.flushdb()


    def test_add_swarm_manager_to_registry(self): 

        mgr = SwarmManager(
            id=12341,
            name="alice"
        )

        self.registry.add_swarm_entry(mgr)
        retrieved_mgr = self.registry.retrieve_swarm_information(mgr.id)
        assert retrieved_mgr.id == mgr.id

    def test_add_agent_entry(self): 
        agent = SwarmAgent(
            name="alice",
            id=12342,
            description="test agent"
        )

        self.registry.add_agent_entry(agent)
        retrieved_agent = self.registry.retrieve_agent_information(agent.id)
        assert retrieved_agent.id == agent.id

    def test_agent_join_swarm(self):

        mgr = SwarmManager(
            id=12343,
            name="alice"
        ) 

        agent = SwarmAgent(
            name="alice_agent",
            id=12344,
            description="test agent"
        )

        self.registry.add_swarm_entry(mgr)
        self.registry.add_agent_entry(agent)
        self.registry.join_swarm(mgr.id, agent.id)
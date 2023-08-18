import redis
import json
import uuid

from osnap_client.agents import SwarmAgentBase

import logging

LOGGER = logging.getLogger(__name__)


class AgentRegistry:
    def __init__(self, host, port, username, password):
        self.redis_client = redis.Redis(
            host=host,
            port=port,
            username=username,
            password=password,
            decode_responses=True,
        )

    def register(self, agent: SwarmAgentBase):
        return self.get_or_create_agent(agent)

    def get_agents(self, scope):
        return self._get_agents_by_scope(scope)

    def _get_agents_by_scope(self, scope):
        agent_ids = self.redis_client.smembers(f"scope:{scope}:agents")
        agents = []
        for agent_id in agent_ids:
            agent_data = self.redis_client.hgetall(f"agent:{agent_id}")
            agent = {k: v for k, v in agent_data.items()}
            agents.append(agent)
        return agents

    def get_or_create_agent(self, agent: SwarmAgentBase):
        if self.redis_client.hexists(f"agent:{agent.name}", agent.name):
            return self.get_agent(agent.name)
        else:
            agent.id = str(uuid.uuid4())
            self.add_agent(agent)

    def get_agent(self, name):
        agent_data = self.redis_client.hget(f"agent:{name}", name)
        if agent_data:
            agent_data["tools"] = json.loads(agent_data["tools"])
            return agent_data
        return None

    def add_agent(self, agent: SwarmAgentBase) -> SwarmAgentBase | None:
        agent_data = {
            "id": agent.id,
            "name": agent.name,
            "description": agent.description,
            "tools": json.dumps(agent.tools),
            "scope": agent.scope,
        }
        name = agent.name
        if not self.redis_client.hexists(f"agent:{name}", name):
            self.redis_client.hset(f"agent:{name}", mapping=agent_data)
            self.redis_client.sadd(f"scope:{agent.scope}:agents", name)
            LOGGER.info("Agent {agent_id} created with name '{name}'.")
            return agent

    def update_tools(self, agent_id, tools):
        agent_key = f"agent:{agent_id}"
        self.redis_client.hset(agent_key, "tools", json.dumps(tools))

    def remove_agent(self, agent_id):
        agent_key = f"agent:{agent_id}"
        self.redis_client.delete(agent_key)

    def get_agent_by_id(self, agent_id):
        agent_key = f"agent:{agent_id}"
        agent_data = self.redis_client.hgetall(agent_key)
        if agent_data:
            agent_data["tools"] = json.loads(agent_data["tools"])
            return agent_data
        return None

    def search_agents_by_tool_description(self, search_query):
        matching_agents = []
        for key in self.redis_client.scan_iter(match="agent:*"):
            agent_data = self.redis_client.hgetall(key)
            tools = json.loads(agent_data["tools"])
            for tool in tools:
                if search_query.lower() in tool["description"].lower():
                    agent_data["tools"] = tools
                    matching_agents.append(agent_data)
                    break
        return matching_agents

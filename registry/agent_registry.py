import redis
import json


class AgentRegistry:
    def __init__(self, host, port, username, password):
        self.redis_client = redis.Redis(
            host=host,
            port=port,
            username=username,
            password=password,
            decode_responses=True,
        )

    def get_agents(self, scope):
        return self._get_agents_by_scope(scope)

    def _get_agents_by_scope(self, scope):
        agent_ids = self.redis_client.smembers(f"scope:{scope}:agents")
        agents = []
        for agent_id in agent_ids:
            agent_data = self.redis_client.hgetall(f"agent:{agent_id}")
            print("agent_data by scope", agent_data)
            agent = {k: v for k, v in agent_data.items()}
            agents.append(agent)
        return agents

    def get_or_create_agent(
        self, agent_id, name, description, invoke_endpoint, tools, scope
    ):
        if self.redis_client.hexists(f"agent:{name}", name):
            return self.get_agent(name)
        else:
            self.add_agent(agent_id, name, description, invoke_endpoint, tools, scope)

    def get_agent(self, name):
        agent_data = self.redis_client.hget(f"agent:{name}", name)
        print("agent_data")
        if agent_data:
            agent_data["tools"] = json.loads(agent_data["tools"])
            return agent_data
        return None

    def add_agent(self, agent_id, name, description, invoke_endpoint, tools, scope):
        agent_data = {
            "agent_id": agent_id,
            "agent_name": name,
            "description": description,
            "invoke_endpoint": invoke_endpoint,
            "tools": json.dumps(tools),
            "scope": scope,
        }

        if not self.redis_client.hexists(f"agent:{name}", name):
            self.redis_client.hset(f"agent:{name}", mapping=agent_data)
            print(f"Agent {agent_id} created with name '{name}'.")
            self.redis_client.sadd(f"scope:{scope}:agents", agent_id)
            return name

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

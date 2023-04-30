import redis
import json

class AgentRegistry:

    def __init__(self, host, port, username, password):
        self.redis_client = redis.Redis(
            host=host,
            port=port,
            username=username,
            password=password,
            decode_responses=True
        )

    def get_agents(self, scope):
        return self._get_agents_by_scope(scope)
    
    def _get_agents_by_scope(self, scope):
        agent_ids = self.redis_client.smembers(f"scope:{scope}:agents")
        agents = []
        for agent_id in agent_ids:
            agent_data = self.hgetall(f"agent:{agent_id.decode('utf-8')}")
            agent = {k.decode('utf-8'): v.decode('utf-8') for k, v in agent_data.items()}
            agents.append(agent)
        return agents

    def add_agent(self, agent_id, name, description, endpoint, tools, scope):
        agent_key = f'agent:{agent_id}'
        agent_data = {
            'name': name,
            'description': description,
            'endpoint': endpoint,
            'tools': json.dumps(tools),
            'scope': scope
        }
        self.redis_client.hmset(agent_key, agent_data)
        self.redis_client.sadd(f"scope:{scope}:agents", agent_id)
        return agent_key

    def update_tools(self, agent_id, tools):
        agent_key = f'agent:{agent_id}'
        self.redis_client.hset(agent_key, 'tools', json.dumps(tools))

    def remove_agent(self, agent_id):
        agent_key = f'agent:{agent_id}'
        self.redis_client.delete(agent_key)

    def get_agent_by_id(self, agent_id):
        agent_key = f'agent:{agent_id}'
        agent_data = self.redis_client.hgetall(agent_key)
        if agent_data:
            agent_data['tools'] = json.loads(agent_data['tools'])
            return agent_data
        return None

    def search_agents_by_tool_description(self, search_query):
        matching_agents = []
        for key in self.redis_client.scan_iter(match='agent:*'):
            agent_data = self.redis_client.hgetall(key)
            tools = json.loads(agent_data['tools'])
            for tool in tools:
                if search_query.lower() in tool['description'].lower():
                    agent_data['tools'] = tools
                    matching_agents.append(agent_data)
                    break
        return matching_agents

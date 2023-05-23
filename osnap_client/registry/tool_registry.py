import redis
import uuid

from osnap_client.core import OSNAPTool


class ToolRegistry:
    def __init__(self, host, port, username, password):
        self.redis_client = redis.Redis(
            host=host,
            port=port,
            username=username,
            password=password,
            decode_responses=True,
        )

    def register(self, tool: OSNAPTool) -> OSNAPTool:
        return self.get_or_create_tool(tool)

    def get_tool(self, name):
        tool_data = self.redis_client.hget(f"tool:{name}", name)
        if tool_data:
            return tool_data
        return None

    def get_tools(self, scope):
        return self._get_tools_by_scope(scope)

    def _get_tools_by_scope(self, scope):
        tool_ids = self.redis_client.smembers(f"scope:{scope}:tools")
        tools = []
        for tool_id in tool_ids:
            tool_data = self.redis_client.hgetall(f"tool:{tool_id}")
            tool = {k: v for k, v in tool_data.items()}
            tools.append(tool)
        return tools

    def get_or_create_tool(self, tool: OSNAPTool) -> OSNAPTool:
        name = tool.name
        if self.redis_client.hexists(f"tool:{name}", name):
            return self.get_tool(tool)
        else:
            return self.add_tool(tool)

    def add_tool(self, tool: OSNAPTool) -> OSNAPTool:
        name = tool.name

        if not self.redis_client.hexists(f"tool:{name}", name):
            id = uuid.uuid4()
            tool.id = str(id)
            tool_data = {
                "id": tool.id,
                "name": name,
                "description": tool.description,
                "scope": tool.scope,
            }
            self.redis_client.hset(f"tool:{name}", mapping=tool_data)
            self.redis_client.sadd(f"scope:{tool.scope}:tools", name)
            return tool

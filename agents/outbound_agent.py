import uuid
import json
import time
import redis
import pickle
from threading import Thread
from queue import Queue

class RedisRegistry:
    def __init__(self, host='cognihack-redis', port=6379, db=0):
        self.redis = redis.Redis(host=host, port=port, db=db)

    def register_agent(self, agent_info):
        serialized_agent_info = pickle.dumps(agent_info)
        self.redis.set(agent_info["agent_id"], serialized_agent_info)
        print("Agent registered:", agent_info)

    def send_message(self, message):
        print("Message sent:", message)

class OutBoundAgent:
    def __init__(self, agent_id=None):
        self.agent_id = agent_id or str(uuid.uuid4())
        self.capabilities = {}
        self.registry = RedisRegistry()
        self.message_queue = Queue()

    def register_capability(self, name, description, plugin):
        self.capabilities[name] = {
            "description": description,
            "plugin": plugin
        }

    def register_agent(self):
        agent_info = {
            "agent_id": self.agent_id,
            "capabilities": list(self.capabilities.keys())
        }
        self.registry.register_agent(agent_info)

    def listen_for_messages(self):
        while True:
            if not self.message_queue.empty():
                message = self.message_queue.get()
                self.process_message(message)
            time.sleep(1)

    def process_message(self, message):
        message_type = message.get("message_type")
        
        if message_type == "capabilities_query":
            self.handle_capabilities_query(message)

    def handle_capabilities_query(self, message):
        sender_agent_id = message["sender_agent_id"]
        capabilities_response = {
            "sender_agent_id": self.agent_id,
            "receiver_agent_id": sender_agent_id,
            "message_type": "capabilities_response",
            "capabilities": self.capabilities
        }
        self.registry.send_message(capabilities_response)

def main():
    agent = OutBoundAgent()

    # Example capability plugin
    def example_plugin():
        return "This is an example plugin."

    agent.register_capability("example_capability", "An example capability.", example_plugin)
    agent.register_agent()

    # Start listening for messages
    message_listener_thread = Thread(target=agent.listen_for_messages)
    message_listener_thread.start()
    message_listener_thread.join()

if __name__ == "__main__":
    main()
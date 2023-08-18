from osnap_client.managers import SwarmManagerBase
from osnap_client.adapters import FastAPISwarmAdapter



class AliceSwarmManager(SwarmManagerBase):
    swarm_manager_id = "alice"
    swarm_manager_url = "http://localhost:8000"

    def __init__(self):
        self.swarm_adapter = FastAPISwarmAdapter(self)

    def info(self):
        return {
            "swarm_manager_id": self.swarm_manager_id,
            "swarm_manager_url": self.swarm_manager_url
        }

    def join_swarm(self, swarm_manager_url: str):
        self.swarm_adapter.join_swarm_manager(swarm_manager_url, self.swarm_manager_id)



alice = AliceSwarmManager()

if __name__ == "__main__":
    alice.swarm_adapter.start()
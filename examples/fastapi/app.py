from alice import AliceSwarmManager
from bob import BobSwarmManager

alice = AliceSwarmManager()
bob = BobSwarmManager()

alice.join_swarm(bob.swarm_manager_url)
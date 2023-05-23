import redis
import json
import uuid

class RedisRegistry: 
    def __init__(self, host, port, username, password):
        self.redis_client = redis.Redis(
            host=host,
            port=port,
            username=username,
            password=password,
            decode_responses=True,
        )
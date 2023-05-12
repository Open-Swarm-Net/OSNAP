import asyncio
import os
import redis.asyncio as redis
from fastapi import WebSocket

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_USERNAME = os.getenv("REDIS_USERNAME")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

STOPWORD = "STOP"


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


class PubSub:
    def __init__(self, redis_url: str = None, channel_name: str = "osnap"):
        self.redis_url = redis_url
        self.channel_name = channel_name
        self.redis = None
        self.pubsub = None
        self.manager = ConnectionManager()

    async def connect(self):
        self.redis = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            username=REDIS_USERNAME,
            password=REDIS_PASSWORD,
            db=0,
        )
        self.pubsub = self.redis.pubsub()

    async def close(self):
        if self.redis:
            self.redis.close()
            await self.redis.wait_closed()

    async def subscribe(self):
        self.sub = await self.pubsub.subscribe(self.channel_name)
        future = asyncio.create_task(self.reader(self.pubsub))
        return future

    async def reader(self, channel: redis.client.PubSub):
        while True:
            message = await channel.get_message(ignore_subscribe_messages=True)
            if message is not None:
                print(f"(Reader) Message Received: {message}")
                if message["data"].decode() == STOPWORD:
                    print("(Reader) STOP")
                    break

    async def publish(self, message: str):
        await self.redis.publish(self.channel_name, message)
        await self.manager.broadcast(message)

    def on_message(self, message):
        print(f"Received message: {message}")

    async def add_conn_manager(self, websocket: WebSocket):
        await self.manager.connect(websocket)

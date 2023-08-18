# from httpx import Client
from fastapi import FastAPI, HTTPException
import httpx
from pydantic import BaseModel
import uvicorn 
from urllib.parse import urlparse

from .base import SwarmAdapterBase
from osnap_client.managers.base import SwarmJoinResponse

class FastAPISwarmAdapter(SwarmAdapterBase):

    def __init__(self, mgr):
        self.swarm_manager = mgr
        self.swarm_manager_url = mgr.swarm_manager_url
        self.swarm_manager_id = mgr.swarm_manager_id
        self.app = FastAPI()
        self.register_routes()
        # self.connection.headers.update({'Authorization': 'Bearer <token>'})  # Example authorization header
        # Additional connection setup code specific to REST

    def start(self): 
        o = urlparse(self.swarm_manager_url)
        uvicorn.run(self.app, host=o.hostname, port=o.port)

    def join_swarm_manager(self, to_swarm_url: str, from_swarm_id: str) -> SwarmJoinResponse:
        """
        Outgoing request to join a swarm manager
        """
        url = f"{to_swarm_url}/join"
        
        response = httpx.post(url, json={"swarm_manager_id": self.swarm_manager_id})

        print(f"Response from {url}: {response.json()}")
        
        joined_id = response.json().get("swarm_manager_id")

        # Handle the response as needed
        if response.status_code == 200:
            r = response.json()
            print(f"Successfully joined swarm manager {joined_id}")
            return SwarmJoinResponse(accepted=True, swarm_manager_id=joined_id, message=r.get("message"))
        else:
            print(f"Failed to join swarm manager {joined_id}. Error: {response.text}")
            return SwarmJoinResponse(accepted=False, swarm_manager_id=joined_id, message=response.text)

    def leave_swarm_manager(self, swarm_manager_id: str):
        pass

    def send_message(self, recipient_id: str, message: dict):
        pass

    def receive_message(self, sender_id: str, message: dict):
        pass

    def handle_incoming_messages(self):
        pass

    def register_routes(self):

        @self.app.get("/info")
        async def info():
            return self.swarm_manager.info()

        """
        Allows incoming join requests from other swarm managers
        """
        class JoinRequest(BaseModel):
            swarm_manager_id: str

        @self.app.post("/join")
        async def join_swarm_manager_endpoint(join_request: JoinRequest, response_model=SwarmJoinResponse):
            print(join_request)
            try:
                # self.join_swarm_manager(swarm_manager_id)
                return SwarmJoinResponse(**{
                    "message": f"Successfully joined swarm manager {self.swarm_manager_id}",
                    "swarm_manager_id": self.swarm_manager_id, 
                    "accepted": "true"
                })
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/leave/{swarm_manager_id}")
        async def leave_swarm_manager_endpoint(swarm_manager_id: str):
            try:
                self.leave_swarm_manager(swarm_manager_id)
                return {"message": f"Successfully left swarm manager {swarm_manager_id}"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # Define other route handlers for sending/receiving messages and other operations

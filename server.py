from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


# Describes the agent's role
@app.get("/info")
async def root():
    return {"message": "Hello World"}

# Describe the agent's available tools
@app.get("/tools")
async def root():
    return {"message": "Hello World"}

@app.get("/agents")
async def root(request):
    pass
    # TODO: Make me run
    # return agent_registry.get_agents(request)

# Run a certain task
@app.post("/run")
async def root():
    return {"message": "Hello World"}

class OSnapRunRequest(BaseModel):
    agent_id: str
    task_id: str
    task_payload: str

@app.post("/run/{agent_id}")
async def root(request: OSnapRunRequest):
    # TODO: Implement me
    pass

# Listen for task results distributed to other agents
@app.get("/listen")
async def root():
    return {"message": "Hello World"}

# Agents try and agree they are done
@app.get("/finish")
async def root():
    return {"message": "Hello World"}
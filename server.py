from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.openapi.utils import get_openapi
from starlette.responses import RedirectResponse

def osnap_schema():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="OSNAP - Open Swarm Network Agent Protocol",
        version="1.0.0",
        description="An agent-based workflow orchestration system.",
        routes=app.routes,
    )
    # openapi_schema["info"]["x-logo"] = {
    #     "url": "https://raw.githubusercontent.com/OSnapDev/OSnap/master/docs/logo.png"
    # }
    app.openapi_schema = openapi_schema
    return app.openapi_schema
  
app = FastAPI()
app.openapi = osnap_schema

@app.get("/")
async def root():
    response = RedirectResponse(url='/docs')
    return response

class OSnapEnvironment(BaseModel):
    """Describes the environment, including it's endpoints, OSNAP version, etc."""

    osnap_schema_version: str = "1.0.0"    
    docs_url: str = "/docs"
    api_types = ["REST", "GraphQL"]

    environment_id: str
    environment_name: str
    environment_description: str
    environment_url: str

    def __str__(self):
        return f'{self.environment_name} ({self.environment_id})'


@app.get("/info")
async def root():
    """Describes the environment, including it's endpoints, OSNAP version, etc."""
    return {
        "info": OSnapEnvironment(environment_id="1", environment_name="OSnap", environment_description="An agent-based workflow orchestration system.", environment_url="")
    }

@app.get("/agents")
async def root(request):
    return agent_registry.get_agents(request)
    # TODO: Make me run
    # return agent_registry.get_agents(request)


# Describe the agent's available tools
@app.get("/tools")
async def root():
    return {"message": "Hello World"}

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

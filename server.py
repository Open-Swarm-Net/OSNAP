import os
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.openapi.utils import get_openapi
from starlette.responses import RedirectResponse
from uuid import uuid4

from lib.osnap import OSNAP, OSNAPApp, OSNAPAgent, OSNAPTool, OSNAPRequest, OSNAPResponse, Scope
from registry import AgentRegistry

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


REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_USERNAME = os.getenv("REDIS_USERNAME")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
WEAVIATE_HOST = os.getenv("WEAVIATE_HOST")
WEAVIATE_VECTORIZER = os.getenv("WEAVIATE_VECTORIZER")

agent_registry = AgentRegistry(REDIS_HOST, REDIS_PORT, REDIS_USERNAME, REDIS_PASSWORD)

app = FastAPI()
app.openapi = osnap_schema


# {
#       "id": "01GZ9EDJRAHHV015YT9PMBE4E3",
#       "operation_id": "google_calendar_update_event_bf4a22a",
#       "description": "Google Calendar: Update Event",
#       "params": {
#         "instructions": "str",
#         "Calendar": "str",
#         "Event": "str"
#       }
#     },
my_tools = [
    OSNAPTool(
        name="Google Calendar: Update Event",
        description="",
        invoke_endpoint="http://localhost:8000/{agent_id}/tools/google_calendar_update_event",
        tool_id="google_calendar_update_event",
        invoke_required_params={
            "instructions": "str",
            "Calendar": "str",
            "Event": "str"
        }
    )
]

my_agents = [
    OSNAPAgent(
        name="agent1",
        description="can do stuff",
        scope=Scope.PUBLIC,
        info_endpoint="http://localhost:8000/info",
        registry_url="http://localhost:8000/agents",
        invoke_endpoint="http://localhost:8000/run", 
        tools=my_tools,
        register=agent_registry.add_agent,
    ),
]

osnap_app = OSNAPApp(agents=my_agents)


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

@OSNAP.agents()
@app.get("/agents")
async def root():
    return agent_registry.get_agents()
    # TODO: Make me run
    # return agent_registry.get_agents(request)

# Decorator checks at runtime if the agent conforms to the OSNAP spec
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

@app.post("/run/{agent_id}/tool/{tool_id}")
async def invoke_tool(request: OSNAPRequest) -> OSNAPResponse:
    # make a POST request to the Internal API
    tool_response = update_gcal_event(request.task_payload) 
    res = OSNAPResponse(tool_response)
    return res

# Listen for task results distributed to other agents
@app.get("/listen")
async def root():
    return {"message": "Hello World"}

# Agents try and agree they are done
@app.get("/finish")
async def root():
    return {"message": "Hello World"}

@OSNAP.tool_invoke()
@app.get("/tools/{tool_id}")
async def tool_invoke(request: OSNAPRequest):
    return {"message": "Hello World"}


# Internal API
@app.get("/tools/google_calendar_update_event")
async def update_gcal_event():
    return { "message": "I updated the event" }


# from alice (planner agent)
# requests.get('bob.com/run/agent2/tool/google_calendar_update_event')
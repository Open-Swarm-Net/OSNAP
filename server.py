import os
from fastapi import FastAPI
from langchain.agents import AgentExecutor
from langchain.vectorstores.redis import Dict, List
from pydantic import BaseModel
from fastapi.openapi.utils import get_openapi
from starlette.responses import RedirectResponse
from uuid import uuid4

from langchain.agents import ZeroShotAgent, Tool, AgentExecutor
from langchain.agents.agent_toolkits import ZapierToolkit
from langchain import LLMChain, PromptTemplate
from langchain.llms import OpenAI
from langchain.agents import initialize_agent
from langchain.agents.agent_toolkits import ZapierToolkit
from langchain.agents import AgentType
from langchain.utilities.zapier import ZapierNLAWrapper
from langchain.chat_models import ChatOpenAI

from lib import OSNAP
from lib.osnap import OSNAPApp, OSNAPAgent, OSNAPTool, OSNAPRequest, OSNAPResponse, Scope
from registry import AgentRegistry

import httpx

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

class OSNAPAdapter():
    def x(agent_executor: AgentExecutor)-> OSNAPAgent:

        OSNAP_tools = []

        for tool in agent_executor.tools:
            OSNAP_tools.append(
                OSNAPTool(
                    name = tool.name,
                    description = tool.description,
                    invoke_endpoint = "http://localhost:8000/{agent_id}/tools/google_calendar_update_event",
                    tool_id = "google_calendar_update_event",
                    invoke_required_params = {
                        "instructions": "str",
                        "Calendar": "str",
                        "Event": "str"
                    }
                )
                
            )

my_tools = [
    
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
        add_agent_function=agent_registry.add_agent,
    ),
]

osnap_app = OSNAPApp(agents=my_agents)

class SnapTask(BaseModel):
   task_description: str

@app.get("/")
async def root():
    response = RedirectResponse(url='/docs')
    return response

@app.post("/kickoff")
async def kickOff(task: SnapTask):

    res = await httpx.AsyncClient().get('http://cognihack-app:8000/agents',)
    external_agents = res
    
    prompt = PromptTemplate(template="""
            You are an AI who performs one task based on the following objective: {objective}.
            You are going to work together with another agent to complete the job.
            Given the following agents, which one would you like to work with?
            {external_agents}
        """, 
        input_variables=["objective", "external_agents"]
    )

    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0,
        #max_tokens=1500,
        #streaming=True
        verbose=True,
    )
    chain = LLMChain(llm=llm, prompt=prompt)

    response = chain.arun(objective=task.task_description, external_agents=external_agents)

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
    return agent_registry.get_agents('public')
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

    # TODO: Wrap this whole thing in an OSNAPAdapter class
    def update_gcal_event(): 
        verbose = True

        tools += ZapierToolkit.from_zapier_nla_wrapper(ZapierNLAWrapper()).get_tools()

        prefix = """You are an AI who performs one task based on the following objective: {objective}."""
        suffix = """Question: {objective}
        {agent_scratchpad}"""
        prompt = ZeroShotAgent.create_prompt(
            tools=tools,
            prefix=prefix,
            suffix=suffix,
            input_variables=["objective", "agent_scratchpad"],
        )

        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            #max_tokens=1500,
            #streaming=True
            verbose=True,
        )

        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=ZeroShotAgent(
                llm_chain=LLMChain(
                    llm=llm,
                    prompt=prompt,
                    verbose=verbose,
                ),
                allowed_tools=[tool.name for tool in tools],
                verbose=verbose,
            ),
            tools=tools,
            verbose=verbose,
            #return_intermediate_steps=True,
            max_iterations=3,
            max_execution_time=60,
            early_stopping_method="generate"
        )

        # OBJECTIVE = "Plan a meeting for today at 4pm"

        agent_executor({"objective": request.instructions})


    tool_actions = {
        "google_calendar_update_event": update_gcal_event
    }

    tool_response = tool_actions[request.tool_id](request.task_payload)

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
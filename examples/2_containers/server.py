import os
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

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
from fastapi.middleware.cors import CORSMiddleware

from osnap import (
    OSNAP,
    OSNAPApp,
    OSNAPAgent,
    OSNAPTool,
    OSNAPRequest,
    OSNAPResponse,
    Scope,
)
from registry import AgentRegistry, ToolRegistry
from osnap_client.pubsub import PubSub, ConnectionManager

import httpx
import logging
import redis
import redis.asyncio as raio

logging.basicConfig(
    level=logging.INFO, format="%(levelname)-9s %(asctime)s - %(name)s - %(message)s"
)
LOGGER = logging.getLogger(__name__)

import asyncio


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


# REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_USERNAME = os.getenv("REDIS_USERNAME")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
WEAVIATE_HOST = os.getenv("WEAVIATE_HOST")
WEAVIATE_VECTORIZER = os.getenv("WEAVIATE_VECTORIZER")


app = FastAPI()
app.openapi = osnap_schema

pubsub = PubSub()


class OSNAPAdapter:
    def x(agent_executor: AgentExecutor) -> OSNAPAgent:
        OSNAP_tools = []

        for tool in agent_executor.tools:
            OSNAP_tools.append(
                OSNAPTool(
                    name=tool.name,
                    description=tool.description,
                    invoke_endpoint="http://localhost:8000/{agent_id}/tools/google_calendar_update_event",
                    invoke_required_params={
                        "instructions": "str",
                        "Calendar": "str",
                        "Event": "str",
                    },
                )
            )


agent_registry = AgentRegistry(REDIS_HOST, REDIS_PORT, REDIS_USERNAME, REDIS_PASSWORD)
tool_registry = ToolRegistry(REDIS_HOST, REDIS_PORT, REDIS_USERNAME, REDIS_PASSWORD)

my_tools = [
    OSNAPTool(
        name="google_calendar_update_event",
        description="updates a google calendar event",
        scope=Scope.PUBLIC,
        invoke_endpoint="http://localhost:8000/{agent_id}/tools/google_calendar_update_event",
        invoke_optional_params=None,
        invoke_required_params=None,
    )
]

my_agents = [
    OSNAPAgent(
        name="agent1",
        description="can do stuff",
        scope=Scope.PUBLIC,
        tools=my_tools,
    ),
    OSNAPAgent(
        name="agent2",
        description="can schedule stuff",
        scope=Scope.PUBLIC,
        tools=my_tools,
    ),
]

osnap_app = OSNAPApp(
    agents=my_agents,
    tools=my_tools,
    agent_registry=agent_registry,
    tool_registry=tool_registry,
)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    await osnap_app.create_pubsub()


@app.get("/")
async def root():
    response = RedirectResponse(url="/docs")
    return response


class OSNAPTask(BaseModel):
    task_description: str
    environment_url: str


@app.post("/start")
async def start(task: OSNAPTask):
    async_client = httpx.AsyncClient()
    res = await async_client.get(f"{task.environment_url}/agents")

    # Instantiate agents from the response and register them as external agents
    agents_res = res.json()
    external_agents = [OSNAPAgent(**agent) for agent in agents_res]

    external_agents_strings = [str(a) for a in external_agents]

    # TODO: Make a decorator for this and add expose a method to register external agents
    osnap_app.register_agents(external_agents, external=True)

    prompt = PromptTemplate(
        template="""
            You are an AI who performs one task based on the following objective: {objective}.
            You are going to work together with another agent to complete the job.
            Given the following agents, which one would you like to work with?
            {external_agents}
        """,
        input_variables=["objective", "external_agents"],
    )

    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0,
        # max_tokens=1500,
        # streaming=True
        verbose=True,
    )
    chain = LLMChain(llm=llm, prompt=prompt)

    def async_generate(chain):
        return chain.arun(
            objective=task.task_description, external_agents=external_agents_strings
        )

    tasks = [async_generate(chain)]
    response = await asyncio.gather(*tasks)
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
        return f"{self.environment_name} ({self.environment_id})"


@app.get("/info")
async def root():
    """Describes the environment, including it's endpoints, OSNAP version, etc."""
    return {
        "info": OSnapEnvironment(
            environment_id="1",
            environment_name="OSnap",
            environment_description="An agent-based workflow orchestration system.",
            environment_url="",
        )
    }


@app.get("/agents")
@osnap_app.agents
async def root():
    return agent_registry.get_agents("public")
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
    await pubsub.publish("Run endpoint hit")
    return {"message": "Hello World"}


class OSnapRunRequest(BaseModel):
    agent_id: str
    task_id: str
    task_payload: str


@app.post("/run/{agent_id}")
async def root(request: OSnapRunRequest):
    await pubsub.publish(
        f"Run endpoint hit by: {request.agent_id} Requesting Task: {request.task_payload}, Task ID: {request.task_id}"
    )
    return {"message": "Hello World"}
    # TODO: Implement me
    pass


@app.post("/run/{agent_id}/tool/{tool_id}")
async def invoke_tool(request: OSNAPRequest) -> OSNAPResponse:
    await pubsub.publish(
        f"Run endpoint hit by: {request.agent_id} Requesting Tool: {request.tool_id}, Tool Payload: {request.tool_payload}"
    )

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
            # max_tokens=1500,
            # streaming=True
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
            # return_intermediate_steps=True,
            max_iterations=3,
            max_execution_time=60,
            early_stopping_method="generate",
        )

        # OBJECTIVE = "Plan a meeting for today at 4pm"

        agent_executor({"objective": request.instructions})

    tool_actions = {"google_calendar_update_event": update_gcal_event}

    tool_response = tool_actions[request.tool_id](request.task_payload)

    res = OSNAPResponse(tool_response)
    return res


# Listen for task results distributed to other agents


@app.get("/listen")
async def root():
    await pubsub.publish("Hello World")
    return {"message": "Hello World"}


html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = Date.now()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://localhost:8000/ws/${client_id}`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@app.get("/chat")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    pubsub = PubSub()
    await pubsub.connect()
    await pubsub.manager.connect(websocket)

    async def ws_receive():
        while True:
            data = await websocket.receive_text()
            await pubsub.manager.send_personal_message(f"You wrote: {data}", websocket)
            await pubsub.manager.broadcast(f"Client #{client_id} says: {data}")
            await pubsub.publish(data)

    ws_receive_task = asyncio.create_task(ws_receive())
    ws_pubsub_reader_task = asyncio.create_task(pubsub.subscribe())

    try:
        await asyncio.gather(ws_receive_task, ws_pubsub_reader_task)
    except WebSocketDisconnect:
        pubsub.manager.disconnect(websocket)
        await pubsub.manager.broadcast(f"Client #{client_id} left the chat")
        ws_receive_task.cancel()
        ws_pubsub_reader_task.cancel()


# Agents try and agree they are done


@app.get("/finish")
async def root():
    return {"message": "Hello World"}


@OSNAP.tool_invoke()
@app.get("/tools/{tool_id}")
async def tool_invoke(request: OSNAPRequest):
    return {"message": "Hello World"}

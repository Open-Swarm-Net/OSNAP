import os
import math
from redis.exceptions import ResponseError
from langchain import LLMChain, PromptTemplate
from langchain.agents import ZeroShotAgent, Tool, AgentExecutor
from registry.agent_registry import AgentRegistry
from langchain.agents.agent_toolkits import FileManagementToolkit
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.experimental import BabyAGI
from langchain.retrievers import TimeWeightedVectorStoreRetriever
from langchain.tools import ShellTool
from langchain.vectorstores.redis import Redis

from langchain.agents.agent_toolkits import (
    create_vectorstore_agent,
    VectorStoreToolkit,
    VectorStoreInfo,
)
from tempfile import TemporaryDirectory


REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_USERNAME = os.getenv("REDIS_USERNAME")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

agent_registry = AgentRegistry(REDIS_HOST, REDIS_PORT, REDIS_USERNAME, REDIS_PASSWORD)

embeddings_model = OpenAIEmbeddings(model="text-embedding-ada-002")

def relevance_score_fn(score: float) -> float:
    return 1.0 - score / math.sqrt(2)

vectorstore = Redis(
    embedding_function=embeddings_model.embed_query,
    redis_url=f"redis://{REDIS_USERNAME}:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}",
    index_name='link',
    relevance_score_fn=relevance_score_fn
)

try:
    vectorstore._create_index()
except ResponseError:
    print('no')

llm = ChatOpenAI(
    model="gpt-3.5-turbo-0301",
    temperature=0,
    #max_tokens=1500,
    #streaming=True
 )

memory_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=TimeWeightedVectorStoreRetriever(
        vectorstore=vectorstore,
        other_score_keys=["importance"],
        k=15,
        decay_rate=0.01
    )
)

fileManagementToolkit = FileManagementToolkit()

shellTool = ShellTool()
shellTool.description = shellTool.description + f"args {shellTool.args}".replace("{", "{{").replace("}", "}}")

tools = fileManagementToolkit.get_tools()
#tools.append(shellTool)

# Option 1: Complete vectorstore
#tools.append(
#    VectorStoreToolkit(
#        vectorstore_info=VectorStoreInfo(
#            name="Memory",
#            description="Useful for when you need to quickly access memory of events and people and things that happened recently or longer ago. Always do this first whenever you need external information.",
#            vectorstore=vectorstore
#        )
#    ).get_tools()
#)
# Option 2: Time weigh
tools.append(
    Tool(
        name="Memory",
        func=memory_chain,
        description="Always do this first. Useful for when you need to access memory of events or people or things that happened recently or longer ago.",
    )
)

agent_registry.add_agent(1, 'name', 'description', '/end/1/point', [tool.name for tool in tools])

tools.append(
    Tool(
        name="TODO",
        func=LLMChain(
            llm=llm,
            prompt=PromptTemplate.from_template(
                "You are a planner who is an expert at coming up with a todo list for a given objective. Come up with a todo list for this objective: {objective}"
            )
        ),
        description="useful for when you need to come up with todo lists. Input: an objective to create a todo list for. Output: a todo list for that objective. Please be very clear what the objective is!",
    ),
)

prefix = """You are an AI who performs one task based on the following objective: {objective}. Take into account these previously completed tasks: {context}."""
suffix = """Question: {task}
{agent_scratchpad}"""
prompt = ZeroShotAgent.create_prompt(
    tools,
    prefix=prefix,
    suffix=suffix,
    input_variables=["objective", "task", "context", "agent_scratchpad"],
)

agent_executor = AgentExecutor.from_agent_and_tools(
    agent=ZeroShotAgent(
        llm_chain=LLMChain(
            llm=llm,
            prompt=prompt
        ),
        allowed_tools=[tool.name for tool in tools]
    ),
    tools=tools,
    verbose=True,
    #return_intermediate_steps=True,
    max_iterations=3,
    max_execution_time=60,
    early_stopping_method="generate"
)

OBJECTIVE = "Analyze the repository you're in"

baby_agi = BabyAGI.from_llm(
    llm=llm, 
    vectorstore=vectorstore, 
    task_execution_chain=agent_executor, 
    verbose=False, 
    max_iterations=3
)

baby_agi({"objective": OBJECTIVE})
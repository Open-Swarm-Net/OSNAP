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

from langchain.llms import OpenAI
from langchain.agents import initialize_agent
from langchain.agents.agent_toolkits import ZapierToolkit
from langchain.agents import AgentType
from langchain.utilities.zapier import ZapierNLAWrapper

# Change to your liking
verbose = True

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_USERNAME = os.getenv("REDIS_USERNAME")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

ZAPIER_API_KEY = os.environ["ZAPIER_NLA_API_KEY"] = os.getenv("ZAPIER_API_KEY")

agent_registry = AgentRegistry(REDIS_HOST, REDIS_PORT, REDIS_USERNAME, REDIS_PASSWORD)

embeddings_model = OpenAIEmbeddings(model="text-embedding-ada-002")

def relevance_score_fn(score: float) -> float:
    return 1.0 - score / math.sqrt(2)

vectorstore = Redis(
    embedding_function=embeddings_model.embed_query,
    redis_url=f"redis://{REDIS_USERNAME}:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}",
    index_name='link',
    relevance_score_fn=relevance_score_fn,
)

try:
    vectorstore._create_index()
except ResponseError:
    print('no')

llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0,
    #max_tokens=1500,
    #streaming=True
    verbose=verbose,
 )

memory_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=TimeWeightedVectorStoreRetriever(
        vectorstore=vectorstore,
        other_score_keys=["importance"],
        k=15,
        decay_rate=0.01,
        verbose=verbose,
    ),
    verbose=verbose,
)

# Option 1: Complete vectorstore
tools = VectorStoreToolkit(
    vectorstore_info=VectorStoreInfo(
        name="Memory",
        description="Useful for when you need to quickly access memory of events and people and things that happened recently or longer ago. Always do this first whenever you need external information.",
        vectorstore=vectorstore,
        verbose=verbose,
    ),
    verbose=verbose,
).get_tools()
# Option 2: Time weigh
#tools.append(
#    Tool(
#        name="Memory",
#        func=memory_chain,
#        description="Always do this first. Useful for when you need to access memory of events or people or things that happened recently or longer ago.",
#    )
#)

tools += FileManagementToolkit().get_tools()

tools += ZapierToolkit.from_zapier_nla_wrapper(ZapierNLAWrapper()).get_tools()

shellTool = ShellTool()
#shellTool.description = shellTool.description + f"args {shellTool.args}".replace("{", "{{").replace("}", "}}")
tools.append(shellTool)

tools.append(
    Tool(
        name="TODO",
        func=LLMChain(
            llm=llm,
            prompt=PromptTemplate.from_template(
                "You are a planner who is an expert at coming up with a todo list for a given objective. Come up with a todo list for this objective: {objective}"
            ),
            verbose=verbose,
        ),
        description="useful for when you need to come up with todo lists. Input: an objective to create a todo list for. Output: a todo list for that objective. Please be very clear what the objective is!",
        verbose=verbose,
    ),
)

agent_registry.add_agent(1, 'name', 'description', '/end/1/point', [tool.name for tool in tools], )

prefix = """You are an AI who performs one task based on the following objective: {objective}."""
suffix = """Question: {objective}
{agent_scratchpad}"""
prompt = ZeroShotAgent.create_prompt(
    tools=tools,
    prefix=prefix,
    suffix=suffix,
    input_variables=["objective", "agent_scratchpad"],
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

OBJECTIVE = "Plan a meeting for today at 4pm"

agent_executor({"objective": OBJECTIVE})

#baby_agi = BabyAGI.from_llm(
#    llm=llm, 
#    vectorstore=vectorstore, 
#    task_execution_chain=agent_executor,
#    max_iterations=3,
#    verbose=verbose,
#)

#baby_agi({"objective": OBJECTIVE})
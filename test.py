from audioop import add
import os
from redis.exceptions import ResponseError
from langchain import LLMChain, PromptTemplate
from langchain.agents import ZeroShotAgent, Tool, AgentExecutor
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.experimental import BabyAGI
from langchain.retrievers import TimeWeightedVectorStoreRetriever
from langchain.vectorstores.redis import Redis

from langchain.agents.agent_toolkits import (
    create_vectorstore_agent,
    VectorStoreToolkit,
    VectorStoreInfo,
)

from registry.agent_registry import AgentRegistry

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_USERNAME = os.getenv("REDIS_USERNAME")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
WEAVIATE_HOST = os.getenv("WEAVIATE_HOST")
WEAVIATE_VECTORIZER = os.getenv("WEAVIATE_VECTORIZER")

agent_registry = AgentRegistry(REDIS_HOST, REDIS_PORT, REDIS_USERNAME, REDIS_PASSWORD)

embeddings_model = OpenAIEmbeddings(model="text-embedding-ada-002")

vectorstore = Redis(
    embedding_function=embeddings_model.embed_query,
    redis_url=f"redis://default:redis-stack@{REDIS_HOST}:{REDIS_PORT}",
    index_name='link'
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
        k=15
    )
)

tools = []

## These are 2 different kinds of memory, I wonder which works better.


# Option 1: Toolkit

#tools = VectorStoreToolkit(
#    vectorstore_info=VectorStoreInfo(
#        name="Memory",
#        description="Useful for when you need to quickly access memory of events and people and things that happened recently or longer ago. Always do this first whenever you need external information.",
#        vectorstore=vectorstore
#    )
#).get_tools()

# Option 2: Time weighted memory retriever

tools.append(
    Tool(
        name="Memory",
        func=memory_chain,
        description="Always do this first. Useful for when you need to access memory of events or people or things that happened recently or longer ago.",
    )
)



todo_chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate.from_template(
        "You are a planner who is an expert at coming up with a todo list for a given objective. Come up with a todo list for this objective: {objective}"
    )
)

tools.append(
    Tool(
        name="TODO",
        func=todo_chain,
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

OBJECTIVE = "Write a weather report for SF today"


baby_agi = BabyAGI.from_llm(
    llm=llm, 
    vectorstore=vectorstore, 
    task_execution_chain=agent_executor, 
    verbose=False, 
    max_iterations=3
)

baby_agi({"objective": OBJECTIVE})
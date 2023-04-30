import os
from collections import deque
from typing import Dict, List, Optional, Any

from langchain import LLMChain, OpenAI, PromptTemplate
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import BaseLLM
from langchain.vectorstores.base import VectorStore
from pydantic import BaseModel, Field
from langchain.chains.base import Chain
from langchain.experimental import BabyAGI

from langchain.vectorstores import FAISS
from langchain.docstore import InMemoryDocstore
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.redis import Redis
from langchain.retrievers import TimeWeightedVectorStoreRetriever
from langchain.agents import ZeroShotAgent, Tool, AgentExecutor
from langchain import OpenAI, SerpAPIWrapper, LLMChain
from langchain.agents.agent_toolkits import (
    create_vectorstore_agent,
    VectorStoreToolkit,
    VectorStoreInfo,
)
from langchain.experimental.generative_agents import GenerativeAgent, GenerativeAgentMemory
from langchain.chains import RetrievalQA


REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
WEAVIATE_HOST = os.getenv("WEAVIATE_HOST")
WEAVIATE_VECTORIZER = os.getenv("WEAVIATE_VECTORIZER")

embeddings_model = OpenAIEmbeddings(model="text-embedding-ada-002")

vectorstore = Redis.from_existing_index(
    embeddings_model,
    redis_url=f"redis://{REDIS_HOST}:{REDIS_PORT}",
    index_name='link'
)

llm = OpenAI(
    model="gpt3.5-turbo",
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
        func=memory_chain.run,
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
        func=todo_chain.run,
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
    return_intermediate_steps=True,
    max_iterations=3,
    max_execution_time=60,
    early_stopping_method="generate"
)

OBJECTIVE = "Write a weather report for SF today"

agent_executor.run(OBJECTIVE)

#baby_agi = BabyAGI.from_llm(
#    llm=llm, 
#    vectorstore=vectorstore, 
#    task_execution_chain=agent_executor, 
#    verbose=False, 
#    max_iterations=3
#)

#baby_agi({"objective": OBJECTIVE})
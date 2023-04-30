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
from langchain.retrievers import TimeWeightedVectorStoreRetriever

# Define your embedding model
embeddings_model = OpenAIEmbeddings(model="text-embedding-ada-002")
# Initialize the vectorstore as empty
import faiss

embedding_size = 1536
index = faiss.IndexFlatL2(embedding_size)
vectorstore = FAISS(embeddings_model.embed_query, index, InMemoryDocstore({}))


def relevance_score_fn(score: float) -> float:
    return 1.0 - score / math.sqrt(2)

retriever = TimeWeightedVectorStoreRetriever(
    vectorstore=vectorstore,
    other_score_keys=["importance"],
    k=15
)





from langchain.agents import ZeroShotAgent, Tool, AgentExecutor
from langchain import OpenAI, SerpAPIWrapper, LLMChain


llm = OpenAI(
    model="gpt3.5-turbo",
    temperature=0,
    #max_tokens=1500,
    #streaming=True
 )

todo_prompt = PromptTemplate.from_template(
    "You are a planner who is an expert at coming up with a todo list for a given objective. Come up with a todo list for this objective: {objective}"
)
todo_chain = LLMChain(llm=llm, prompt=todo_prompt)
search = SerpAPIWrapper()


from langchain.agents.agent_toolkits import (
    create_vectorstore_agent,
    VectorStoreToolkit,
    VectorStoreInfo,
)
from langchain.experimental.generative_agents import GenerativeAgent, GenerativeAgentMemory

vectorstore_info = VectorStoreInfo(
    name="Memory",
    description="Useful for when you need to quickly access memory of events and people and things that happened recently or longer ago. Always do this first whenever you need external information.",
    vectorstore=vectorstore
)

toolkit = VectorStoreToolkit(vectorstore_info=vectorstore_info)

tools = toolkit.get_tools()

tools.append(
    Tool(
        name="Search",
        func=search.run,
        description="useful for when you need to answer questions about current events",
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

llm = OpenAI(
    model="gpt3.5-turbo",
    temperature=0,
    #max_tokens=1500,
    #streaming=True
 )

llm_chain = LLMChain(llm=llm, prompt=prompt)
tool_names = [tool.name for tool in tools]
agent = ZeroShotAgent(llm_chain=llm_chain, allowed_tools=tool_names)
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent, tools=tools, verbose=True
)

OBJECTIVE = "Write a weather report for SF today"

verbose = False
max_iterations: Optional[int] = 3

baby_agi = BabyAGI.from_llm(
    llm=llm, 
    vectorstore=vectorstore, 
    task_execution_chain=agent_executor, 
    verbose=verbose, 
    max_iterations=max_iterations
)

baby_agi({"objective": OBJECTIVE})
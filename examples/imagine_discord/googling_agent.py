import sys, os, time
from dotenv import load_dotenv
import re

# adding the lates version of the osnap_client to the path
from pathlib import Path
file_path = Path(__file__).absolute()
sys.path.append(str(file_path.parent.parent.parent))

from osnap_client.adapters import DiscordAdapter
from osnap_client.agents import SwarmAgentBase
from osnap_client.protocol import AgentCommand, AgentCommandType, Task
from osnap_client.utils.ai_engines import LanchainGoogleEngine, GPTConversEngine

class GooglingAgent(SwarmAgentBase):
    def __init__(self, name, description, swarm_adapter):
        super().__init__(name, description, swarm_adapter)

        self.search_engine = LanchainGoogleEngine("gpt-3.5-turbo", 0.5, 1000)
        self.thinking_engine = GPTConversEngine("gpt-3.5-turbo", 0.5, 1000)

        @self.command(name="research")
        async def research(message: AgentCommand):
            try:
                if message.payload_type == "task":
                    task = Task.from_json(message.payload)
                    payload = task.task_description
                    task_id = task.task_id
                elif message.payload_type == "str":
                    payload = message.payload
                    task_id = None
                    task = Task(task_name="research", task_description=payload)
                
                if message.payload_type != "str":
                    raise ValueError(f"Expected payload_type to be 'str' but got {message.payload_type}")
                
                if payload == "":
                    raise ValueError("Payload cannot be empty")
                
                if not isinstance(payload, str):
                    raise ValueError(f"Expected payload to be of type str but got {type(payload)}")

                research_results = self._research(payload)
                task.result = research_results
                task.status = "submitted"
                
                response = AgentCommand(
                    sender=self.name,
                    receiver="agent",
                    command_type=AgentCommandType.SUBMIT,
                    task_type="research",
                    payload_type='task',
                    payload=task.json(),
                )
                await self.swarm_adapter.send_dm(response, message.sender)
            except Exception as e:
                print(f"Error in research command: {e}")
                response = AgentCommand(
                    sender=self.name,
                    receiver="agent",
                    command_type=AgentCommandType.ERROR,
                    task_type="research",
                    payload_type = 'str',
                    payload=f"505: Internal Server Error: {e}",
                )
                await self.swarm_adapter.send_dm(response, message.sender)
    
    def _research(self, topic: str) -> str:
        """Does google search on a given topic and returns the results
        """
        print(f"Researching '{topic}'")
        queries = self._gen_querries(topic)
        results = []
        for query in queries:
            results.append(self._google_search(query))
        response = self._summarize(topic, results)
        return response

    def _google_search(self, query: str)-> str:
        """Does the search itself but provides very short answers!
        """
        query = query.strip().replace("'", "").replace('"', "")
        response = self.search_engine.call_model(query)
        print(f"For query: '{query}', got response: '{response[:100]}'")
        return response
    
    def _summarize(self, topic: str, results: list) -> str:
        """Summarizes the results into a single paragraph
        """
        results_summarisation_prompt = (
            "----Results Summarisation Prompt----\n"
            "You will be presented with a global topic and a list of research results related to this topic. Your task is to distill this information into a single, concise paragraph. "
            "The summarisation should capture the essence of the results and their relevance to the global topic. "
            "Focus on highlighting key findings, unique insights, and essential takeaways that are relevant only to the global topic. "
            "The summarisation should be comprehensive yet succinct, enabling anyone to grasp the major points quickly. \n\n"
            "For example, if the global topic is 'Climate Change Impact on Agriculture' and the results include various studies, statistics, and expert opinions, weave them into a coherent, compact summary.\n"
            "--------\n"
        )

        results = "\n".join(results)

        conversation = [
            {"role": "system", "content": results_summarisation_prompt},
            {"role": "user", "content": f"Topic: {topic}.\n\nResults:\n{results}"},
        ]

        response = self.thinking_engine.call_model(conversation)

        print(f"Summarized results: '{response[:100]}'")
        return response
    
    def _gen_querries(self, topic: str) -> list:
        """Breaks down the topic into a list of google search querries
        """
        search_query_breakdown = (
            "----Search Query Breakdown----\n"
            "You're given a topic. Your task is to break this topic down into 2 distinct Google search queries that would help answer the posed question."
            "The search queries should be unique, focused, and specific. "
            "You MUST include only the search queries in your output formatted as a list that is parsable by re.findall(r'\[(.*?)\]', response)!!\n\n"
            "Example: \n"
            "Topic: 'Self-driving cars'\n"
            "Response: ['History of self-driving cars', 'Technology used in self-driving cars', 'Legal issues surrounding self-driving cars', 'Safety records of self-driving cars', 'Future prospects of self-driving cars']\n"
            "--------\n"
        )
        conversation = [
            {"role": "system", "content": search_query_breakdown},
            {"role": "user", "content": f"Topic: {topic}"},
        ]

        attempts = 0
        while attempts < 3:
            try:
                response = self.thinking_engine.call_model(conversation)
                # parse the response into a list of querries
                querries = re.findall(r"\[(.*?)\]", response)
                querries = querries[0].split(",")
                querries = [q.strip() for q in querries]
                print(f"Generated querries: {querries[:100]}")
                return querries[:5]
            except Exception as e:
                attempts += 1
                print(f"Error in _gen_querries: {e}")
                time.sleep(1)
        
        raise Exception("Failed to generate querries")
        
        

def main():
    """
    On a mac, go to Macintosh HD > Applications > Python3.x folder (x being your python3 version) > double click on "Install Certificates.command" file
    """
    load_dotenv()

    intents_list = ["message_content", "members", "guilds"]
    adapter = DiscordAdapter(
        start_server=os.getenv("START_SERVER_NAME"),
        intents_list=intents_list,
        token=os.getenv("GOOGLE_BOT_TOKEN"),
    )

    agent = GooglingAgent(
        name="GooglingBOT",
        description="I am a bot who can research a topic on google",
        swarm_adapter=adapter
    )
    agent.run()


if __name__ == "__main__":
    main()

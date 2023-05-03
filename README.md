# Important links:
* https://docs.google.com/presentation/d/13fBflbidB7ykvWYGxvemO1U5Rle58lqEZnkUhBwzB38
* https://github.com/CogniHack/CogniHack/blob/master/docs/BIG_IDEA.md

# General information 
OSNAP, an innovative open-source project, aims to revolutionize the way AI systems communicate and collaborate. With a Central Registry facilitating AI discovery and a Standardized Communication Protocol ensuring seamless interactions, OSNAP enables AI systems to work together, enhancing their capabilities and scalability. This technology has the potential to streamline workflows across various sectors, including project management, customer service, healthcare, and urban planning, paving the way for significant economic growth. By enabling secure, standardized communication and collaboration among AI systems, OSNAP promises a future where AI systems don't just work for us, but with us and each other, driving economic growth while ensuring privacy and security.

# How to run

* `cp .env.example .env.receiver; cp env.example .env.sender`
* `sed -i ' 's/host-redis/receiver-redis/g' '.env.receiver'`
* `sed -i ' 's/host-redis/sender-redis/g' '.env.sender'`
* `docker network create osnap-network`
* `docker-compose up --build`


# Open Swarm Network Agent Protocol (OSNAP)

## Architecture

- FastAPI (Implements the Agent API)
  - /info (describes the role of the agent)
  - /tools (describe the tools made available)
  - /run (invoke other agents to perform tasks)
  - /listen (listen for task results distributed to other agents)
  - /finish (agents try and agree they are done)
- Agent (Python/Langchain)
  - Agent State
  - Task Store (Queue, Whatever)
- Tool Store (Redis)
  - Self-Describing Format, with Permissions, Preferences, Restrictions
  - Could be JSON
  - Could be Vectors
  

## Call Sequence

1. My user (agent1) gives the objective
2. Agent1 calls Agent2 /tools endpoint
3. Agent2 sends back tools response from Tool Store
4. Agent1 makes plan (ala babyagi) and asks Agent2 to execute the first step *Can potentially explore more traits and roles here*. This is done via a request to agent2's /run endpoint. Agent2 acknowledges that it recieved the task by responding with some status.
5. Agent1 registers a listener for the task ID.
6. Agent2 does the thing in the background, and when it's done, send a POST request to Agent1s listen endpoint with the result.
7. Continue as long as Agent1 wants to in order to solve the problem. 
8. Agent1 sends a request to the /finish endpoint.

# What is a Swarm Registry? 

One of the jobs of a Swarm is to maintain a list of Agents and ot_her Swarms that have joined it. 
That information is exposed as part of the protocol, by the OSNAP python client's `info` abstract method. 

When Agents are created or added to a Swarm, we want to be able to add their info to the registry, 
likewise when our Swarm joins another Swarm, we want to be able to add it's info as well. 

Together, the connections between Swarms and Agents can be represented by a [Graph Data Structure](https://www.freecodecamp.org/news/data-structures-101-graphs-a-visual-introduction-for-beginners-6d88f36ec768/). What does this 
abstraction buy us?

## How it Works
### Swarm Registry Responsibilities:
1. *Maintain Swarm Information*: The Swarm Registry is responsible for storing and maintaining the information of Agents and other Swarms that have joined a particular Swarm. This includes details such as unique identifiers, connection information, and any additional metadata associated with each entry.

2. *Add Agents and Swarms*: When an Agent is created or added to a Swarm, the Swarm Registry allows for adding the Agent's information to the registry. Similarly, when a Swarm joins another Swarm, the Swarm Registry facilitates adding the joined Swarm's information.

3. *Graph Data Structure*: The Swarm Registry represents the connections between Swarms and Agents as a graph data structure. This allows for modeling flexible topologies, enabling dynamic behaviors and emergent intelligence within the Swarm system.

## Why a Graph

### Flexible Topology: 
Because a Swarm is a complex system that allows for emergent behavior and 
super intelligence, we need a way to support many different types of topologies. For example, 
the optimal behavior of a swarm might be centralized or decentralized, and we want a way to 
build this dynamism into the underlying data. 

### Agent and Swarm Discovery: 
Because swarms are dynamic, we need a way to be able to discover 
agents and swarms that can help our swarm accomplish an objective. Graph Datastructures have a 
long history of algorithms that can help with these types of tasks. 

### Distributable: 
Because Swarms can be distributed, meaning they exist across hosts and networks, we need a 
data structure that can distribute well. Because graphs contain edges that point to other 
graph nodes, we can represent distributed Swarms as pointers to other nodes, via adapters. 
To take a specific example, a Swarm can join another Swarm on the same host by using a TCP port `http://localhost:8004`, 
or on another host by using a URL `https://otherhost.com/`

## Swarm Registry Functions:

1. Add Swarm Entry: Allows adding the information of a joined Swarm to the registry, including the Swarm's unique identifier and connection details.

2. Add Agent Entry: Enables adding the information of an Agent to the registry, including the Agent's unique identifier, connection information, and any additional metadata.

3. Retrieve Swarm Information: Provides the ability to query the registry to retrieve information about a specific Swarm, such as its connected Agents and other Swarms.

4. Retrieve Agent Information: Allows querying the registry to retrieve information about a specific Agent, including the Swarm it belongs to and any associated metadata.

5. Perform Graph Queries: Provides functionalities to perform graph queries on the Swarm Registry, such as finding neighboring Swarms or discovering Agents based on certain criteria.


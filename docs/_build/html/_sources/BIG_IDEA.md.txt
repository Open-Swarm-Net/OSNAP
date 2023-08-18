# The Big Idea

Agent models have been one of the most useful ideas to fall out of the recent LLM explosion. Projects like [AutoGPT](https://github.com/Significant-Gravitas/Auto-GPT), [BabyAGI](https://github.com/yoheinakajima/babyagi), [Generative Agents](https://arxiv.org/pdf/2304.03442.pdf), [CAMEL](https://www.camel-ai.org/) have all demonstrated the power of this abstraction. Currently, these Agent implementations are all fundamentally "virtualized", that is running on the same host machine with the same environment permissions, etc.

We propose a new protocol and architecture for Agents communicating over the network. Users can expose Agents to the internet by following the Open-Swarm Network Agent Protocol (O-SNAP).

## Architectures

O-SNAP endeavors to support flexible "Swarm Network" configurations.

### Basic Two Agent

Let's imagine a use case -- Alice wants to schedule a coffee date with Bob. Both Alice and Bob have Personal Agents running in an environment which has access to a set of tools, defined in a Tool Registry.

In this case, Alice will tell her agent1 that she wants to schedule coffee with Bob. Sometime in the next two weeks.

```mermaid
---
title: Basic Two Agent
---
graph TD
    subgraph Alice's Environment
      agent1 --> t1(Tool Registry)
    end

    t1 <== O-SNAP protocol ==> t2

    subgraph Bob's Environment
        agent2 --> t2(Tool Registry)
    end
```

### Three Agent

What happens if Alice requests a coffee date sometime this week, but Bob is booked solid. Bob can configure his Calendar tool in the registry to support reaching out to Olesia's agent to ask if she would be okay with rescheduling. Olesia's agent might text her asking if she's okay with re-scheduling. Note that Alice's agent and Olesia's agent don't have to know about each other!

```mermaid
---
title: Three Agent
---
graph TD
    subgraph Alice's Environment
      agent1 --> t1(Tool Registry)
    end

    t1 <== O-SNAP ==> t2

    agent2 <=== O-SNAP ===> agent3

    subgraph Bob's Environment
        agent2 --> t2(Tool Registry)
    end

    subgraph Olesia's Environment
        agent3 --> t3(Tool Registry)
    end
```

### Team-Team

We are not limited to a single agent. For example, BabyAGI uses multiple agents each with different roles to serve user requests.

Let's imagine two companies, Bob's Big Burgers and Acme Beer Co. They want to work together to plan a big event to celebrate the Summer Solstice. Each team has it's own internal task loop, and O-SNAP lets them communicate team to team so they can consult each other to figure out what each other are doing and how they can help one another

```mermaid
---
title: Team-Team
---
graph TD
    subgraph Bob's Big Burgers Environment
      CashierAgent --> t1(Task Store)
      ChefAgent --> t1
      HostessAgent --> t1
    end

    t1 <== O-SNAP protocol ==> t2

    subgraph Acme Beer Co.'s Environment
        Brewmeister --> t2(Task Store)
        DeliveryDriver --> t2
    end
```

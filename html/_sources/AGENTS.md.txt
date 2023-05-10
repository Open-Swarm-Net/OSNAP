# Agents

## What is an Agent exactly?

First some dime-store philosophy. Using an LLM is inherently a stateless endeavor. Agents are essentially a [gestalt](https://en.wikipedia.org/wiki/Gestalt_psychology) composed of some "role", "memory", and "tools", which are all synthesized into a text prompt. We then program agents to continue prompting, responding, using tools, however we want them to behave.

## Exposing Agents

O-SNAP specifies that we expose agents via an API. It could be a RESTful API or a GraphQL API. There are two parts to this:

Expose an endpoint `/agents` that will return a list of all the available agents
Can also expose a list in a searchable way e.g. `/agents?task="<task description"`
Each agent returned will have a Invocable URL, like `/run/<agentId>`

### REST
### GraphQL

## Agent Registry

For your Environment and Agents to support O-SNAP, you need to be able to return a properly formatted response for the `/agents` endpoint.

Response Format:

```json 
{}
```

### Registry Reference Architecture

Use REDIS!
# Tools

Users of [LangChain](https://docs.langchain.com/docs/) or [ReAct](https://react-lm.github.io/) might already be familiar with tools (actions). These describe the atomic units of LLM based planning. O-SNAP facilitiates Agent interaction by providing a standard for exposing tools.

## Tool Registry

Agents have access to a registry of tools that are stored in the tool registry. These define what exactly what an agent can do on behalf of a user or organizaton.

## Tool Anatomy

- Name: Says what it is
- Description: Describes what it can do
- Uses: Describes what uses the tool has

*example-tool.json:*
```json
{
  "Name": "Calendar",
}
```

### Public vs. Private